"""
Gemeinsame Datenmodelle für Client und Server
Pydantic-Schemas für API-Kommunikation
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class UserBase(BaseModel):
    username: str
    role: str  # 'teacher' oder 'student'
    full_name: Optional[str] = None


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class RoomBase(BaseModel):
    name: str
    description: Optional[str] = None
    time_limit_minutes: int = 60


class RoomCreate(RoomBase):
    pass


class Room(RoomBase):
    id: int
    teacher_id: int
    is_active: bool = False
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PuzzleBase(BaseModel):
    title: str
    h5p_content_id: Optional[str] = None
    h5p_json: Optional[Dict[str, Any]] = None
    puzzle_type: str = "multiple_choice"
    order_index: int = 0
    points: int = 10
    time_limit_seconds: int = 300


class PuzzleCreate(PuzzleBase):
    room_id: int


class Puzzle(PuzzleBase):
    id: int
    room_id: int
    created_at: datetime


    class Config:
        from_attributes = True


class GameSessionBase(BaseModel):
    room_id: int
    student_id: int


class GameSession(GameSessionBase):
    id: int
    started_at: datetime
    completed_at: Optional[datetime] = None
    total_score: int = 0
    status: str = "in_progress"

    class Config:
        from_attributes = True


class PuzzleResultCreate(BaseModel):
    session_id: int
    puzzle_id: int
    answer_json: Dict[str, Any]
    time_taken_seconds: int


class PuzzleResult(PuzzleResultCreate):
    id: int
    is_correct: bool
    points_earned: int
    answered_at: datetime

    class Config:
        from_attributes = True


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: User


class RoomProgress(BaseModel):
    """Fortschritt eines Schülers in einem Raum"""
    room_id: int
    student_id: int
    completed_puzzles: int
    total_puzzles: int
    current_score: int
    status: str