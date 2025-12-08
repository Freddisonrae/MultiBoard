"""
Admin-Endpunkte für Lehrer
Raum- und Rätsel-Verwaltung
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
import json
import sys

sys.path.append('..')

from ..database import get_db
from ..auth import get_current_teacher
from .. import models
from shared.models import Room, RoomCreate, Puzzle, PuzzleCreate, User

router = APIRouter(prefix="/api/admin", tags=["admin"])


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


@router.get("/rooms/{room_id}/puzzles", response_model=List[Puzzle])
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


@router.post("/puzzles", response_model=Puzzle)
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

    db_puzzle = models.Puzzle(**puzzle.dict())
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