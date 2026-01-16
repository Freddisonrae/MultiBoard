"""
Spiel-Endpunkte für Schüler
Räume betreten, Rätsel lösen, Fortschritt speichern
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import json
import sys
sys.path.append('..')

from ..database import get_db
from ..auth import get_current_user
from .. import models
from shared.models import Room, Puzzle, GameSession, PuzzleResult, PuzzleResultCreate, RoomProgress

router = APIRouter(prefix="/api/game", tags=["game"])


@router.get("/available-rooms", response_model=List[Room])
async def get_available_rooms(
        current_user: models.User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """Verfügbare Räume für Schüler abrufen"""

    # 🔍 DEBUG: Alle Räume in DB anzeigen
    all_rooms = db.query(models.Room).all()
    print(f"🔍 DEBUG: Insgesamt {len(all_rooms)} Räume in Datenbank")
    for room in all_rooms:
        print(f"  - ID: {room.id}, Name: {room.name}, Teacher: {room.teacher_id}")

    print(f"🔍 DEBUG: Current User: {current_user.username}, Role: {current_user.role}, ID: {current_user.id}")

    # Admin sieht ALLE Räume
    if current_user.role == "admin":
        rooms = db.query(models.Room).all()
        print(f"📋 Admin sieht alle Räume: {len(rooms)} gefunden")
        return rooms

    # Lehrer sehen alle ihre Räume
    elif current_user.role == "teacher":
        rooms = db.query(models.Room).filter(
            models.Room.teacher_id == current_user.id
        ).all()
        print(f"📋 Lehrer (ID:{current_user.id}) sieht eigene Räume: {len(rooms)} gefunden")
        return rooms

    # Schüler sehen nur zugewiesene, aktive Räume
    elif current_user.role == "student":
        rooms = db.query(models.Room).filter(
            models.Room.is_active == True
        ).all()
        print(f"📋 Schüler sieht zugewiesene Räume: {len(rooms)} gefunden")
        return rooms


@router.post("/start-session/{room_id}", response_model=GameSession)
async def start_game_session(
    room_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Neue Spiel-Session starten"""
    # Prüfen ob Raum existiert und zugänglich ist
    room = db.query(models.Room).filter(models.Room.id == room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Raum nicht gefunden")

    # Für Schüler: Prüfen ob zugewiesen
    if current_user.role == "student":
        assignment = db.query(models.RoomAssignment).filter(
            models.RoomAssignment.room_id == room_id,
            models.RoomAssignment.student_id == current_user.id
        ).first()

        if not assignment:
            raise HTTPException(status_code=403, detail="Zugriff verweigert")

    # Prüfen ob bereits aktive Session existiert
    existing_session = db.query(models.GameSession).filter(
        models.GameSession.room_id == room_id,
        models.GameSession.student_id == current_user.id,
        models.GameSession.status == "in_progress"
    ).first()

    if existing_session:
        return existing_session

    # Neue Session erstellen
    session = models.GameSession(
        room_id=room_id,
        student_id=current_user.id
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


@router.get("/session/{session_id}/puzzles", response_model=List[Puzzle])
async def get_session_puzzles(
    session_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Rätsel für eine Session abrufen"""
    # Session prüfen
    session = db.query(models.GameSession).filter(
        models.GameSession.id == session_id,
        models.GameSession.student_id == current_user.id
    ).first()

    if not session:
        raise HTTPException(status_code=404, detail="Session nicht gefunden")

    # Rätsel laden
    puzzles = db.query(models.Puzzle).filter(
        models.Puzzle.room_id == session.room_id
    ).order_by(models.Puzzle.order_index).all()

    return puzzles


@router.post("/submit-answer", response_model=PuzzleResult)
async def submit_answer(
    result: PuzzleResultCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Antwort einreichen und bewerten"""
    # Session prüfen
    session = db.query(models.GameSession).filter(
        models.GameSession.id == result.session_id,
        models.GameSession.student_id == current_user.id
    ).first()

    if not session:
        raise HTTPException(status_code=404, detail="Session nicht gefunden")

    # Rätsel laden
    puzzle = db.query(models.Puzzle).filter(
        models.Puzzle.id == result.puzzle_id
    ).first()

    if not puzzle:
        raise HTTPException(status_code=404, detail="Rätsel nicht gefunden")

    # Antwort bewerten
    is_correct = False
    points_earned = 0

    # H5P-JSON parsen
    h5p_data = json.loads(puzzle.h5p_json) if puzzle.h5p_json else {}

    # Einfache Multiple-Choice-Bewertung
    if puzzle.puzzle_type == "multiple_choice":
        correct_index = h5p_data.get("correct", -1)
        user_answer = result.answer_json.get("selected", -1)
        is_correct = (correct_index == user_answer)

        if is_correct:
            points_earned = puzzle.points

    # Ergebnis speichern
    db_result = models.PuzzleResult(
        session_id=result.session_id,
        puzzle_id=result.puzzle_id,
        answer_json=json.dumps(result.answer_json),
        is_correct=is_correct,
        points_earned=points_earned,
        time_taken_seconds=result.time_taken_seconds
    )

    db.add(db_result)

    # Session-Score aktualisieren
    session.total_score += points_earned

    db.commit()
    db.refresh(db_result)

    return db_result


@router.get("/session/{session_id}/progress", response_model=RoomProgress)
async def get_session_progress(
    session_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Fortschritt einer Session abrufen"""
    # Session prüfen
    session = db.query(models.GameSession).filter(
        models.GameSession.id == session_id,
        models.GameSession.student_id == current_user.id
    ).first()

    if not session:
        raise HTTPException(status_code=404, detail="Session nicht gefunden")

    # Anzahl gelöster Rätsel
    completed_count = db.query(models.PuzzleResult).filter(
        models.PuzzleResult.session_id == session_id
    ).count()

    # Gesamt-Rätsel im Raum
    total_count = db.query(models.Puzzle).filter(
        models.Puzzle.room_id == session.room_id
    ).count()

    return RoomProgress(
        room_id=session.room_id,
        student_id=session.student_id,
        completed_puzzles=completed_count,
        total_puzzles=total_count,
        current_score=session.total_score,
        status=session.status
    )


@router.post("/session/{session_id}/complete")
async def complete_session(
    session_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Session als abgeschlossen markieren"""
    from datetime import datetime

    session = db.query(models.GameSession).filter(
        models.GameSession.id == session_id,
        models.GameSession.student_id == current_user.id
    ).first()

    if not session:
        raise HTTPException(status_code=404, detail="Session nicht gefunden")

    session.status = "completed"
    session.completed_at = datetime.utcnow()

    db.commit()
    return {"message": "Session abgeschlossen", "total_score": session.total_score}