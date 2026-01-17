"""
API-Client für Desktop-App
Kommuniziert mit FastAPI-Server
"""
import requests
import json
from typing import Optional, List, Dict, Any
from pathlib import Path
import hashlib
import threading
import websocket


class APIClient:
    """Client für API-Kommunikation"""

    def __init__(self, base_url: str = "http://127.0.0.1:8000"):
        self.base_url = base_url
        self.token: Optional[str] = None
        self.user: Optional[Dict] = None

        # Offline-Quiz Support
        self.offline_rooms: List[Dict] = []
        self._offline_sessions: Dict[int, Dict] = {}
        self._offline_next_session_id = 100000

        # WebSocket-Variablen
        self._ws: Optional[websocket.WebSocketApp] = None
        self._ws_thread: Optional[threading.Thread] = None
        self._on_rooms_updated: Optional[callable] = None
        self._ws_connected = False

    def _get_headers(self) -> Dict[str, str]:
        """Erstellt Headers mit Auth-Token"""
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def login(self, username: str, password: str) -> bool:
        """
        Login-Funktion
        Returns: True bei Erfolg, False bei Fehler
        """
        try:
            response = requests.post(
                f"{self.base_url}/api/auth/login",
                json={"username": username, "password": password},
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                self.token = data["access_token"]
                self.user = data["user"]
                return True

            return False

        except Exception as e:
            print(f"Login-Fehler: {e}")
            return False

    def get_available_rooms(self) -> List[Dict]:
        """Holt verfügbare Räume (online + offline)"""
        try:
            response = requests.get(
                f"{self.base_url}/api/game/available-rooms",
                headers=self._get_headers(),
                timeout=10
            )
            if response.status_code == 200:
                online = response.json()
                return self.offline_rooms + online
            return self.offline_rooms
        except Exception as e:
            print(f"Fehler beim Laden der Räume: {e}")
            return self.offline_rooms

    def start_session(self, room_id: int):
        """Startet eine neue Session"""
        room = next((r for r in self.offline_rooms if r["id"] == room_id), None)
        if room and room.get("mode") == "offline":
            session_id = self._offline_next_session_id
            self._offline_next_session_id += 1

            self._offline_sessions[session_id] = {
                "room_id": room_id,
                "puzzles": room.get("_puzzles", [])
            }
            return {"id": session_id, "mode": "offline"}

        # ONLINE
        try:
            response = requests.post(
                f"{self.base_url}/api/game/start-session/{room_id}",
                headers=self._get_headers(),
                timeout=10
            )
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            print(f"Fehler beim Starten der Session: {e}")
            return None

    def submit_answer(self, session_id: int, puzzle_id: int, answer: Dict[str, Any], time_taken: int) -> Optional[Dict]:
        """Sendet Antwort"""
        # OFFLINE
        if session_id in self._offline_sessions:
            puzzles = self._offline_sessions[session_id]["puzzles"]
            puzzle = next((p for p in puzzles if p["id"] == puzzle_id), None)
            if not puzzle:
                return None

            h5p = json.loads(puzzle.get("h5p_json", "{}"))
            correct_index = int(h5p.get("correct_index", 0))
            selected = int(answer.get("selected", -1))
            is_correct = (selected == correct_index)

            return {
                "is_correct": is_correct,
                "points_earned": 10 if is_correct else 0
            }

        # ONLINE
        try:
            data = {
                "session_id": session_id,
                "puzzle_id": puzzle_id,
                "answer_json": answer,
                "time_taken_seconds": time_taken
            }
            response = requests.post(
                f"{self.base_url}/api/game/submit-answer",
                headers=self._get_headers(),
                json=data,
                timeout=10
            )
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            print(f"Fehler beim Senden der Antwort: {e}")
            return None

    def get_progress(self, session_id: int) -> Optional[Dict]:
        """Holt Fortschritt"""
        try:
            response = requests.get(
                f"{self.base_url}/api/game/session/{session_id}/progress",
                headers=self._get_headers(),
                timeout=10
            )

            if response.status_code == 200:
                return response.json()

            return None

        except Exception as e:
            print(f"Fehler beim Laden des Fortschritts: {e}")
            return None

    def complete_session(self, session_id: int) -> bool:
        """Markiert Session als abgeschlossen"""
        try:
            response = requests.post(
                f"{self.base_url}/api/game/session/{session_id}/complete",
                headers=self._get_headers(),
                timeout=10
            )

            return response.status_code == 200

        except Exception as e:
            print(f"Fehler beim Abschließen: {e}")
            return False

    def register(self, username: str, password: str, is_admin: bool = False) -> bool:
        """Registriert neuen User"""
        try:
            response = requests.post(
                f"{self.base_url}/api/auth/register",
                json={"username": username, "password": password, "is_admin": is_admin},
                timeout=10
            )
            return response.status_code in (200, 201)
        except Exception as e:
            print(f"Registrierung fehlgeschlagen: {e}")
            return False

    def load_quiz_json_file(self, filepath: str) -> Dict:
        """Lädt Quiz aus JSON-Datei"""
        p = Path(filepath).resolve()
        data = json.loads(p.read_text(encoding="utf-8"))

        qlist = data.get("questions", [])
        puzzles = []
        pid = 1

        for q in qlist:
            # H5P-Format?
            params = q.get("params") if isinstance(q, dict) else None
            if isinstance(params, dict):
                question = params.get("question", f"Frage {pid}")
                answers = params.get("answers", [])
            else:
                # Simple-Format
                question = q.get("question", f"Frage {pid}") if isinstance(q, dict) else f"Frage {pid}"
                answers = q.get("answers", []) if isinstance(q, dict) else []

            options = [a.get("text", "") for a in answers if isinstance(a, dict)]
            correct_index = next((i for i, a in enumerate(answers) if isinstance(a, dict) and a.get("correct") is True),
                                 0)

            puzzles.append({
                "id": pid,
                "title": question,
                "h5p_json": json.dumps({
                    "question": question,
                    "options": options,
                    "correct_index": correct_index
                }, ensure_ascii=False)
            })
            pid += 1

        # stabile Room-ID + keine Duplikate
        room_id = int(hashlib.md5(str(p).encode("utf-8")).hexdigest()[:8], 16)
        room = {
            "id": room_id,
            "name": f"📄 {p.stem}",
            "description": "Lokales Quiz (JSON)",
            "time_limit_minutes": 10,
            "mode": "offline",
            "_source": str(p),
            "_puzzles": puzzles
        }

        # dedupe: gleiche Datei => ersetzen
        self.offline_rooms = [r for r in self.offline_rooms if r.get("_source") != room["_source"]]
        self.offline_rooms.insert(0, room)

        return room

    def get_session_puzzles(self, session_id: int) -> List[Dict]:
        """Holt Rätsel für Session"""
        # OFFLINE
        if session_id in self._offline_sessions:
            return self._offline_sessions[session_id]["puzzles"]

        # ONLINE
        try:
            response = requests.get(
                f"{self.base_url}/api/game/session/{session_id}/puzzles",
                headers=self._get_headers(),
                timeout=10
            )
            if response.status_code == 200:
                return response.json()
            return []
        except Exception as e:
            print(f"Fehler beim Laden der Rätsel: {e}")
            return []

    # 🔥 WEBSOCKET-METHODEN
    def connect_websocket(self, on_rooms_updated: callable):
        """
        Startet WebSocket-Verbindung für Live-Updates

        Args:
            on_rooms_updated: Callback-Funktion die aufgerufen wird,
                             wenn sich Räume ändern
        """
        self._on_rooms_updated = on_rooms_updated

        # HTTP -> WebSocket URL
        ws_url = self.base_url.replace("http://", "ws://").replace("https://", "wss://")
        ws_url += "/ws/rooms"

        def on_message(ws, message):
            """Wird aufgerufen wenn Nachricht vom Server kommt"""
            try:
                data = json.loads(message)
                print(f"📨 WebSocket Nachricht: {data}")

                if data.get("type") == "rooms_updated":
                    # Räume neu laden
                    rooms = self.get_available_rooms()

                    # Callback aufrufen (= GUI updaten)
                    if self._on_rooms_updated:
                        self._on_rooms_updated(rooms)

            except Exception as e:
                print(f"Fehler beim Verarbeiten der Nachricht: {e}")

        def on_error(ws, error):
            """Bei Fehlern"""
            print(f"❌ WebSocket Fehler: {error}")
            self._ws_connected = False

        def on_close(ws, close_status_code, close_msg):
            """Verbindung geschlossen"""
            print("🔌 WebSocket geschlossen")
            self._ws_connected = False

        def on_open(ws):
            """Verbindung hergestellt"""
            print("✅ WebSocket verbunden!")
            self._ws_connected = True

            # Optional: Keep-Alive senden
            def send_ping():
                import time
                while self._ws_connected:
                    try:
                        ws.send("ping")
                        time.sleep(30)  # Alle 30 Sekunden
                    except:
                        break

            ping_thread = threading.Thread(target=send_ping, daemon=True)
            ping_thread.start()

        # WebSocket erstellen
        self._ws = websocket.WebSocketApp(
            ws_url,
            on_message=on_message,
            on_error=on_error,
            on_close=on_close,
            on_open=on_open
        )

        # In eigenem Thread starten (blockiert nicht!)
        def run_websocket():
            self._ws.run_forever()

        self._ws_thread = threading.Thread(target=run_websocket, daemon=True)
        self._ws_thread.start()

    def disconnect_websocket(self):
        """WebSocket-Verbindung schließen"""
        if self._ws:
            self._ws.close()
            self._ws_connected = False