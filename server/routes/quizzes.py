from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from fastapi import Query
from pathlib import Path
from typing import Dict, Any, List
import json
import os
from datetime import datetime
import hashlib
import time

from server.auth import get_current_teacher
from server import models
from server.routes.websocket import manager  # ✅ Broadcast


router = APIRouter(prefix="/api/quizzes", tags=["quizzes"])

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads", "quizzes")
os.makedirs(UPLOAD_DIR, exist_ok=True)
UPLOAD_PATH = Path(UPLOAD_DIR)

# -----------------------------
# Server-"Offline" Räume (ohne DB)
# -----------------------------
OFFLINE_ROOMS: Dict[int, Dict[str, Any]] = {}


def _parse_quiz_to_puzzles(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Unterstützt:
    - H5P Question Set:
      { "questions": [ { "params": { "question": "...", "answers":[{"text":"", "correct":true}, ...] } } ] }
    - Simple Format:
      { "questions": [ { "question":"...", "answers":[{"text":"", "correct":true}, ...] } ] }
    """
    qlist = data.get("questions", [])
    puzzles: List[Dict[str, Any]] = []
    pid = 1

    for q in qlist:
        if not isinstance(q, dict):
            continue

        params = q.get("params")
        if isinstance(params, dict):
            question = params.get("question", f"Frage {pid}")
            answers = params.get("answers", [])
        else:
            question = q.get("question", f"Frage {pid}")
            answers = q.get("answers", [])

        if not isinstance(answers, list):
            answers = []

        options = [a.get("text", "") for a in answers if isinstance(a, dict)]
        correct_index = next(
            (i for i, a in enumerate(answers) if isinstance(a, dict) and a.get("correct") is True),
            0
        )

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

    return puzzles


def _room_id_for_path(p: Path) -> int:
    # stabile ID pro Datei (Pfad)
    return int(hashlib.md5(str(p).encode("utf-8")).hexdigest()[:8], 16)


def create_room_from_file(path: Path) -> int:
    """Erzeugt/aktualisiert OFFLINE_ROOMS aus einer JSON-Datei."""
    data = json.loads(path.read_text(encoding="utf-8"))
    puzzles = _parse_quiz_to_puzzles(data)
    room_id = _room_id_for_path(path)

    OFFLINE_ROOMS[room_id] = {
        "id": room_id,
        "name": f"📄 {path.stem}",
        "description": "Server-Quiz (JSON) – ohne Datenbank",
        "time_limit_minutes": 10,
        "mode": "server_offline",
        "_quiz_id": path.name,
        "_puzzles": puzzles,
        "_created_at": time.time()
    }
    return room_id


def load_rooms_from_disk() -> None:
    """Beim Server-Start: alle vorhandenen Quiz-Dateien als Rooms laden."""
    if not UPLOAD_PATH.exists():
        return

    for p in UPLOAD_PATH.glob("*.json"):
        try:
            create_room_from_file(p)
        except Exception:
            continue


@router.post("/upload", status_code=201)
async def upload_quiz_json(
    file: UploadFile = File(...),
    current_user: models.User = Depends(get_current_teacher),
):
    # Nur .json akzeptieren
    if not file.filename.lower().endswith(".json"):
        raise HTTPException(status_code=400, detail="Nur .json Dateien erlaubt")

    raw = await file.read()

    # JSON validieren
    try:
        json.loads(raw.decode("utf-8"))
    except Exception:
        raise HTTPException(status_code=400, detail="Ungültiges JSON")

    # eindeutiger Dateiname (timestamp + original)
    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    safe_name = file.filename.replace("/", "_").replace("\\", "_")
    out_name = f"{ts}_{safe_name}"
    out_path = UPLOAD_PATH / out_name
    out_path.write_bytes(raw)

    # ✅ Room sofort erstellen
    room_id = create_room_from_file(out_path)

    # ✅ Live-Update an alle Clients
    await manager.broadcast({
        "type": "rooms_updated",
        "action": "quiz_uploaded",
        "room_id": room_id,
        "quiz_id": out_name
    })

    return {"ok": True, "filename": out_name, "room_id": room_id}


@router.get("", status_code=200)
async def list_quizzes(limit: int = Query(50, ge=1, le=200)):
    """Liste der hochgeladenen Quiz-Dateien inkl. Mini-Vorschau."""
    if not UPLOAD_PATH.exists():
        return []

    files = sorted(UPLOAD_PATH.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)[:limit]
    result = []

    for p in files:
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
            puzzles = _parse_quiz_to_puzzles(data)

            preview = None
            if puzzles:
                h = json.loads(puzzles[0]["h5p_json"])
                preview = {
                    "question": h.get("question"),
                    "answers_count": len(h.get("options", []))
                }

            result.append({
                "id": p.name,
                "filename": p.name,
                "title": p.stem,
                "questions_count": len(puzzles),
                "preview": preview
            })
        except Exception:
            continue

    return result


@router.get("/rooms", status_code=200)
async def list_server_offline_rooms():
    """Gibt alle serverseitigen Offline-Räume zurück (ohne DB)."""
    return list(OFFLINE_ROOMS.values())