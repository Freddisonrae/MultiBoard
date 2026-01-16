"""
H5P Upload und Verwaltung - FastAPI Routes
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session
from pathlib import Path
import json
import zipfile
import shutil
import uuid
from typing import Optional

from server.database import get_db
from server import models
from server.auth import get_current_user

router = APIRouter(prefix="/api/admin/h5p", tags=["h5p"])

# Basis-Verzeichnis für H5P-Content
H5P_CONTENT_DIR = Path("server/static/h5p-content")
H5P_CONTENT_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/upload")
async def upload_h5p(
        room_id: int,
        file: UploadFile = File(...),
        db: Session = Depends(get_db),
        current_user: models.User = Depends(get_current_user)
):
    """
    H5P-Datei hochladen und entpacken

    Returns:
        puzzle_id: ID des erstellten Rätsels
        content_path: Pfad zum entpackten Content
    """

    # Nur Lehrer dürfen hochladen
    if current_user.role != "teacher":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Nur Lehrer können H5P-Dateien hochladen"
        )

    # Raum existiert und gehört dem Lehrer?
    room = db.query(models.Room).filter(
        models.Room.id == room_id,
        models.Room.teacher_id == current_user.id
    ).first()

    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Raum nicht gefunden oder keine Berechtigung"
        )

    # Datei muss .h5p sein
    if not file.filename.endswith('.h5p'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nur .h5p Dateien sind erlaubt"
        )

    try:
        # Eindeutige ID für diesen Content generieren
        content_id = str(uuid.uuid4())
        content_path = H5P_CONTENT_DIR / content_id
        content_path.mkdir(parents=True, exist_ok=True)

        # Temporäre .h5p Datei speichern
        temp_h5p = content_path / "temp.h5p"
        with open(temp_h5p, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # .h5p entpacken (ist ein ZIP)
        with zipfile.ZipFile(temp_h5p, 'r') as zip_ref:
            zip_ref.extractall(content_path)

        # Temp-Datei löschen
        temp_h5p.unlink()

        # h5p.json lesen für Metadaten
        h5p_json_path = content_path / "h5p.json"
        if not h5p_json_path.exists():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ungültige H5P-Datei (h5p.json fehlt)"
            )

        with open(h5p_json_path, 'r', encoding='utf-8') as f:
            h5p_metadata = json.load(f)

        # content.json lesen für die eigentlichen Inhalte
        content_json_path = content_path / "content" / "content.json"
        if not content_json_path.exists():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ungültige H5P-Datei (content/content.json fehlt)"
            )

        with open(content_json_path, 'r', encoding='utf-8') as f:
            content_data = json.load(f)

        # Titel extrahieren
        title = h5p_metadata.get("title", "H5P Rätsel")

        # Puzzle-Typ bestimmen
        main_library = h5p_metadata.get("mainLibrary", "")
        puzzle_type = "h5p_interactive"

        if "MultiChoice" in main_library:
            puzzle_type = "h5p_multichoice"
        elif "QuestionSet" in main_library:
            puzzle_type = "h5p_questionset"
        elif "DragQuestion" in main_library:
            puzzle_type = "h5p_drag"

        # Puzzle in Datenbank erstellen
        puzzle = models.Puzzle(
            room_id=room_id,
            title=title,
            h5p_content_id=content_id,
            h5p_json=json.dumps(content_data, ensure_ascii=False),
            puzzle_type=puzzle_type,
            points=10,
            time_limit_seconds=300,
            order_index=len(room.puzzles)
        )

        db.add(puzzle)
        db.commit()
        db.refresh(puzzle)

        return {
            "success": True,
            "puzzle_id": puzzle.id,
            "content_id": content_id,
            "content_path": f"/static/h5p-content/{content_id}",
            "title": title,
            "type": puzzle_type
        }

    except zipfile.BadZipFile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Datei ist kein gültiges ZIP-Archiv"
        )
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="H5P-JSON konnte nicht gelesen werden"
        )
    except Exception as e:
        # Cleanup bei Fehler
        if content_path.exists():
            shutil.rmtree(content_path)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Fehler beim Verarbeiten der H5P-Datei: {str(e)}"
        )


@router.get("/content/{content_id}")
async def get_h5p_content(
        content_id: str,
        db: Session = Depends(get_db)
):
    """
    H5P-Content-Metadaten abrufen
    """

    # Prüfen ob Content existiert
    puzzle = db.query(models.Puzzle).filter(
        models.Puzzle.h5p_content_id == content_id
    ).first()

    if not puzzle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="H5P-Content nicht gefunden"
        )

    content_path = H5P_CONTENT_DIR / content_id

    if not content_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="H5P-Content-Dateien nicht gefunden"
        )

    # h5p.json lesen
    h5p_json_path = content_path / "h5p.json"
    with open(h5p_json_path, 'r', encoding='utf-8') as f:
        h5p_metadata = json.load(f)

    return {
        "content_id": content_id,
        "metadata": h5p_metadata,
        "content_path": f"/static/h5p-content/{content_id}",
        "puzzle_id": puzzle.id
    }


@router.delete("/content/{puzzle_id}")
async def delete_h5p_content(
        puzzle_id: int,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(get_current_user)
):
    """
    H5P-Content und Puzzle löschen
    """

    # Puzzle holen
    puzzle = db.query(models.Puzzle).filter(
        models.Puzzle.id == puzzle_id
    ).first()

    if not puzzle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Puzzle nicht gefunden"
        )

    # Berechtigung prüfen
    if puzzle.room.teacher_id != current_user.id and current_user.role != "teacher":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Keine Berechtigung"
        )

    # Content-Verzeichnis löschen
    if puzzle.h5p_content_id:
        content_path = H5P_CONTENT_DIR / puzzle.h5p_content_id
        if content_path.exists():
            shutil.rmtree(content_path)

    # Puzzle aus DB löschen
    db.delete(puzzle)
    db.commit()

    return {"success": True, "message": "H5P-Content gelöscht"}