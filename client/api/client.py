"""
API-Client für Desktop-App
Kommuniziert mit FastAPI-Server
"""
import requests
import json
from typing import Optional, List, Dict, Any


class APIClient:
    """Client für API-Kommunikation"""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.token: Optional[str] = None
        self.user: Optional[Dict] = None

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
        """Holt verfügbare Räume"""
        try:
            response = requests.get(
                f"{self.base_url}/api/game/available-rooms",
                headers=self._get_headers(),
                timeout=10
            )

            if response.status_code == 200:
                return response.json()

            return []

        except Exception as e:
            print(f"Fehler beim Laden der Räume: {e}")
            return []

    def start_session(self, room_id: int) -> Optional[Dict]:
        """Startet neue Spiel-Session"""
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

    def get_session_puzzles(self, session_id: int) -> List[Dict]:
        """Holt Rätsel für Session"""
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

    def submit_answer(
            self,
            session_id: int,
            puzzle_id: int,
            answer: Dict[str, Any],
            time_taken: int
    ) -> Optional[Dict]:
        """Sendet Antwort an Server"""
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