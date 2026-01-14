# server/routes/websocket.py
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import List, Dict
import json

router = APIRouter()


class ConnectionManager:
    """Verwaltet alle WebSocket-Verbindungen"""

    def __init__(self):
        # Liste aller aktiven WebSocket-Verbindungen
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        """Neue Verbindung hinzufügen"""
        await websocket.accept()  # Verbindung akzeptieren
        self.active_connections.append(websocket)
        print(f"✅ Neuer Client verbunden. Gesamt: {len(self.active_connections)}")

    async def disconnect(self, websocket: WebSocket):
        """Verbindung entfernen"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        print(f"❌ Client getrennt. Noch: {len(self.active_connections)}")

    async def broadcast(self, message: Dict):
        """Nachricht an ALLE verbundenen Clients senden"""
        dead_connections = []

        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                print(f"Fehler beim Senden: {e}")
                dead_connections.append(connection)

        # Tote Verbindungen aufräumen
        for dead in dead_connections:
            if dead in self.active_connections:
                self.active_connections.remove(dead)


# Globale Instanz (wird in main.py importiert!)
manager = ConnectionManager()


@router.websocket("/ws/rooms")
async def websocket_rooms_endpoint(websocket: WebSocket):
    """WebSocket-Endpunkt für Raum-Updates"""
    await manager.connect(websocket)

    try:
        # Endlos-Schleife: warte auf Nachrichten vom Client
        while True:
            # Client kann "ping" senden als Keep-Alive
            data = await websocket.receive_text()

            # Optional: auf bestimmte Nachrichten reagieren
            if data == "get_rooms":
                await websocket.send_json({
                    "type": "rooms_update_request",
                    "message": "Bitte Räume neu laden"
                })

    except WebSocketDisconnect:
        # Client hat Verbindung geschlossen
        await manager.disconnect(websocket)
    except Exception as e:
        print(f"WebSocket Fehler: {e}")
        await manager.disconnect(websocket)