"""
WebSocket-Endpunkte für Echtzeit-Updates
Live-Fortschritt und Raum-Synchronisation
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session
from typing import Dict, List
import json
import asyncio

from ..database import get_db
from .. import models

router = APIRouter()


class ConnectionManager:
    """Verwaltet WebSocket-Verbindungen pro Raum"""

    def __init__(self):
        # room_id -> Liste von WebSocket-Verbindungen
        self.active_connections: Dict[int, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, room_id: int):
        """Neue Verbindung hinzufügen"""
        await websocket.accept()
        if room_id not in self.active_connections:
            self.active_connections[room_id] = []
        self.active_connections[room_id].append(websocket)

    def disconnect(self, websocket: WebSocket, room_id: int):
        """Verbindung entfernen"""
        if room_id in self.active_connections:
            self.active_connections[room_id].remove(websocket)
            if not self.active_connections[room_id]:
                del self.active_connections[room_id]

    async def broadcast_to_room(self, room_id: int, message: dict):
        """Nachricht an alle Verbindungen eines Raums senden"""
        if room_id in self.active_connections:
            disconnected = []
            for connection in self.active_connections[room_id]:
                try:
                    await connection.send_json(message)
                except:
                    disconnected.append(connection)

            # Tote Verbindungen entfernen
            for conn in disconnected:
                self.disconnect(conn, room_id)


manager = ConnectionManager()


@router.websocket("/ws/room/{room_id}")
async def websocket_room_endpoint(
        websocket: WebSocket,
        room_id: int,
        db: Session = Depends(get_db)
):
    """
    WebSocket für Raum-Updates
    Sendet Fortschritt-Updates an alle verbundenen Clients
    """
    await manager.connect(websocket, room_id)

    try:
        while True:
            # Auf Nachrichten vom Client warten
            data = await websocket.receive_text()
            message = json.loads(data)

            # Je nach Nachrichtentyp handeln
            if message.get("type") == "progress_update":
                # Fortschritt an alle Clients broadcasten
                await manager.broadcast_to_room(room_id, {
                    "type": "progress_update",
                    "student_id": message.get("student_id"),
                    "completed_puzzles": message.get("completed_puzzles"),
                    "score": message.get("score")
                })

            elif message.get("type") == "room_status":
                # Raum-Status ändern
                room = db.query(models.Room).filter(
                    models.Room.id == room_id
                ).first()

                if room:
                    await manager.broadcast_to_room(room_id, {
                        "type": "room_status",
                        "is_active": room.is_active,
                        "name": room.name
                    })

    except WebSocketDisconnect:
        manager.disconnect(websocket, room_id)
        # Optional: Anderen mitteilen, dass jemand disconnected ist
        await manager.broadcast_to_room(room_id, {
            "type": "user_disconnected",
            "message": "Ein Teilnehmer hat den Raum verlassen"
        })


@router.websocket("/ws/admin")
async def websocket_admin_endpoint(websocket: WebSocket):
    """
    WebSocket für Admin-Dashboard
    Sendet globale Updates an Lehrer
    """
    await websocket.accept()

    try:
        while True:
            data = await websocket.receive_text()
            # Admin-spezifische Logik hier
            await websocket.send_json({
                "type": "admin_update",
                "message": "Admin-Panel verbunden"
            })
            await asyncio.sleep(5)  # Heartbeat

    except WebSocketDisconnect:
        pass