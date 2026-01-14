import json
import threading
from typing import Callable, Optional, Dict, List, Any  # ← Dict hier importieren!
import requests
from pathlib import Path
import hashlib

# ⚠️ WICHTIG: Richtiges Modul!
import websocket  # ← NICHT websockets (mit 's')!


class APIClient:
    """Client für API-Kommunikation"""

    def __init__(self, base_url: str = "http://192.168.2.162:8000"):
        self.base_url = base_url
        self.token: Optional[str] = None
        self.user: Optional[Dict] = None

        # Offline-Quiz Support
        self.offline_rooms: List[Dict] = []
        self._offline_sessions: Dict[int, Dict] = {}
        self._offline_next_session_id = 100000

        # WebSocket-Variablen
        self._ws: Optional[websocket.WebSocketApp] = None  # ← websocket (ohne 's')
        self._ws_thread: Optional[threading.Thread] = None
        self._on_rooms_updated: Optional[Callable] = None
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

    def connect_websocket(self, on_rooms_updated: Callable):
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

    # ... Rest deiner Methoden (get_available_rooms, start_session, etc.)