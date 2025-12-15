"""
Admin-Endpunkte für Lehrer
Raum- und Rätsel-Verwaltung
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import json
import sys

sys.path.append('..')

from ..database import get_db
from ..auth import get_current_teacher
from .. import models
from shared.models import Room, RoomCreate, Puzzle, PuzzleCreate, User
from shared.models import User  # ← Das ist schon weiter oben importiert

router = APIRouter(prefix="/api/admin", tags=["admin"])

from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime


# Eigenes Response-Model für Puzzle, um den Fehler beim Erstellen eines Fehler zu verhindern
class PuzzleResponse(BaseModel):
    id: int
    room_id: int
    title: str
    h5p_content_id: Optional[str] = None
    h5p_json: Optional[str] = None  # ← Als String!
    puzzle_type: str
    order_index: int
    points: int
    time_limit_seconds: int
    created_at: datetime

    class Config:
        from_attributes = True


@router.get("/rooms", response_model=List[Room])
async def get_rooms(
        current_user: models.User = Depends(get_current_teacher),
        db: Session = Depends(get_db)
):
    """Alle Räume des Lehrers abrufen"""
    rooms = db.query(models.Room).filter(
        models.Room.teacher_id == current_user.id
    ).all()
    return rooms


@router.post("/rooms", response_model=Room)
async def create_room(
        room: RoomCreate,
        current_user: models.User = Depends(get_current_teacher),
        db: Session = Depends(get_db)
):
    """Neuen Raum erstellen"""
    db_room = models.Room(
        **room.dict(),
        teacher_id=current_user.id
    )
    db.add(db_room)
    db.commit()
    db.refresh(db_room)
    return db_room


@router.put("/rooms/{room_id}", response_model=Room)
async def update_room(
        room_id: int,
        room: RoomCreate,
        current_user: models.User = Depends(get_current_teacher),
        db: Session = Depends(get_db)
):
    """Raum aktualisieren"""
    db_room = db.query(models.Room).filter(
        models.Room.id == room_id,
        models.Room.teacher_id == current_user.id
    ).first()

    if not db_room:
        raise HTTPException(status_code=404, detail="Raum nicht gefunden")

    for key, value in room.dict().items():
        setattr(db_room, key, value)

    db.commit()
    db.refresh(db_room)
    return db_room


@router.delete("/rooms/{room_id}")
async def delete_room(
        room_id: int,
        current_user: models.User = Depends(get_current_teacher),
        db: Session = Depends(get_db)
):
    """Raum löschen"""
    db_room = db.query(models.Room).filter(
        models.Room.id == room_id,
        models.Room.teacher_id == current_user.id
    ).first()

    if not db_room:
        raise HTTPException(status_code=404, detail="Raum nicht gefunden")

    db.delete(db_room)
    db.commit()
    return {"message": "Raum gelöscht"}


@router.post("/rooms/{room_id}/activate")
async def activate_room(
        room_id: int,
        current_user: models.User = Depends(get_current_teacher),
        db: Session = Depends(get_db)
):
    """Raum aktivieren/deaktivieren"""
    db_room = db.query(models.Room).filter(
        models.Room.id == room_id,
        models.Room.teacher_id == current_user.id
    ).first()

    if not db_room:
        raise HTTPException(status_code=404, detail="Raum nicht gefunden")

    db_room.is_active = not db_room.is_active
    db.commit()
    return {"is_active": db_room.is_active}


@router.get("/rooms/{room_id}/puzzles", response_model=List[PuzzleResponse])  # Verweist auf Modell oben
async def get_puzzles(
    room_id: int,
    current_user: models.User = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    """Rätsel eines Raums abrufen"""
    # Prüfen ob Raum dem Lehrer gehört
    db_room = db.query(models.Room).filter(
        models.Room.id == room_id,
        models.Room.teacher_id == current_user.id
    ).first()

    if not db_room:
        raise HTTPException(status_code=404, detail="Raum nicht gefunden")

    puzzles = db.query(models.Puzzle).filter(
        models.Puzzle.room_id == room_id
    ).order_by(models.Puzzle.order_index).all()

    return puzzles


@router.post("/puzzles", response_model=PuzzleResponse)  #Verweist auf Modell oben
async def create_puzzle(
    puzzle: PuzzleCreate,
    current_user: models.User = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    """Neues Rätsel erstellen"""
    # Prüfen ob Raum dem Lehrer gehört
    db_room = db.query(models.Room).filter(
        models.Room.id == puzzle.room_id,
        models.Room.teacher_id == current_user.id
    ).first()

    if not db_room:
        raise HTTPException(status_code=404, detail="Raum nicht gefunden")

    # WICHTIG: h5p_json muss als STRING gespeichert werden
    import json
    h5p_json_str = json.dumps(puzzle.h5p_json) if puzzle.h5p_json else None

    db_puzzle = models.Puzzle(
        room_id=puzzle.room_id,
        title=puzzle.title,
        h5p_content_id=puzzle.h5p_content_id,
        h5p_json=h5p_json_str,  # ← Als String!
        puzzle_type=puzzle.puzzle_type,
        order_index=puzzle.order_index,
        points=puzzle.points,
        time_limit_seconds=puzzle.time_limit_seconds
    )

    db.add(db_puzzle)
    db.commit()
    db.refresh(db_puzzle)

    return db_puzzle


@router.put("/puzzles/{puzzle_id}", response_model=Puzzle)
async def update_puzzle(
        puzzle_id: int,
        puzzle: PuzzleCreate,
        current_user: models.User = Depends(get_current_teacher),
        db: Session = Depends(get_db)
):
    """Rätsel aktualisieren"""
    db_puzzle = db.query(models.Puzzle).join(models.Room).filter(
        models.Puzzle.id == puzzle_id,
        models.Room.teacher_id == current_user.id
    ).first()

    if not db_puzzle:
        raise HTTPException(status_code=404, detail="Rätsel nicht gefunden")

    for key, value in puzzle.dict().items():
        setattr(db_puzzle, key, value)

    db.commit()
    db.refresh(db_puzzle)
    return db_puzzle


@router.delete("/puzzles/{puzzle_id}")
async def delete_puzzle(
        puzzle_id: int,
        current_user: models.User = Depends(get_current_teacher),
        db: Session = Depends(get_db)
):
    """Rätsel löschen"""
    db_puzzle = db.query(models.Puzzle).join(models.Room).filter(
        models.Puzzle.id == puzzle_id,
        models.Room.teacher_id == current_user.id
    ).first()

    if not db_puzzle:
        raise HTTPException(status_code=404, detail="Rätsel nicht gefunden")

    db.delete(db_puzzle)
    db.commit()
    return {"message": "Rätsel gelöscht"}


@router.post("/rooms/{room_id}/assign-student")
async def assign_student_to_room(
        room_id: int,
        student_id: int,
        current_user: models.User = Depends(get_current_teacher),
        db: Session = Depends(get_db)
):
    """Schüler einem Raum zuweisen"""
    # Prüfen ob Raum dem Lehrer gehört
    db_room = db.query(models.Room).filter(
        models.Room.id == room_id,
        models.Room.teacher_id == current_user.id
    ).first()

    if not db_room:
        raise HTTPException(status_code=404, detail="Raum nicht gefunden")

    # Prüfen ob Schüler existiert
    student = db.query(models.User).filter(
        models.User.id == student_id,
        models.User.role == "student"
    ).first()

    if not student:
        raise HTTPException(status_code=404, detail="Schüler nicht gefunden")

    # Zuweisung erstellen (falls nicht vorhanden)
    existing = db.query(models.RoomAssignment).filter(
        models.RoomAssignment.room_id == room_id,
        models.RoomAssignment.student_id == student_id
    ).first()

    if existing:
        return {"message": "Schüler bereits zugewiesen"}

    assignment = models.RoomAssignment(room_id=room_id, student_id=student_id)
    db.add(assignment)
    db.commit()
    return {"message": "Schüler zugewiesen"}


@router.get("/students", response_model=List[User])
async def get_students(
        current_user: models.User = Depends(get_current_teacher),
        db: Session = Depends(get_db)
):
    """Alle Schüler abrufen"""
    students = db.query(models.User).filter(
        models.User.role == "student"
    ).all()
    return students

@router.get("/teachers", response_model=List[User])
async def get_teachers(
    current_user: models.User = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    """Alle Lehrer abrufen (nur für Lehrer)"""
    teachers = db.query(models.User).filter(
        models.User.role == "teacher"
    ).all()
    return teachers


@router.get("/pending-teachers", response_model=List[User])
async def get_pending_teachers(
        current_user: models.User = Depends(get_current_teacher),
        db: Session = Depends(get_db)
):
    """Wartende Lehrer-Registrierungen"""
    # Nur freigeschaltete Lehrer dürfen das
    if not current_user.is_approved:
        raise HTTPException(403, "Keine Berechtigung")

    pending = db.query(models.User).filter(
        models.User.role == 'teacher',
        models.User.is_approved == False
    ).all()

    return pending


@router.post("/approve-teacher/{teacher_id}")
async def approve_teacher(
        teacher_id: int,
        approve: bool = True,
        current_user: models.User = Depends(get_current_teacher),
        db: Session = Depends(get_db)
):
    """Lehrer freischalten oder ablehnen"""
    if not current_user.is_approved:
        raise HTTPException(403, "Keine Berechtigung")

    teacher = db.query(models.User).filter(
        models.User.id == teacher_id,
        models.User.role == 'teacher'
    ).first()

    if not teacher:
        raise HTTPException(404, "Lehrer nicht gefunden")

    if approve:
        teacher.is_active = True
        teacher.is_approved = True
        message = f"✅ Lehrer '{teacher.full_name}' wurde freigeschaltet"
    else:
        db.delete(teacher)
        message = f"❌ Registrierung von '{teacher.full_name}' wurde abgelehnt"

    db.commit()

    return {"message": message, "approved": approve}