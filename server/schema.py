"""
Pydantic Schemas für FastAPI
Server-spezifische Schema-Definitionen
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, validator


# ============================================================================
# User Schemas
# ============================================================================

class UserBase(BaseModel):
    """Basis-Schema für User"""
    username: str = Field(..., min_length=3, max_length=100)
    role: str = Field(..., pattern="^(teacher|student)$")
    full_name: Optional[str] = Field(None, max_length=200)


class UserCreate(UserBase):
    """Schema für User-Erstellung"""
    password: str = Field(..., min_length=6)


class UserUpdate(BaseModel):
    """Schema für User-Update"""
    full_name: Optional[str] = None
    password: Optional[str] = None


class UserResponse(UserBase):
    """Schema für User-Response"""
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
        orm_mode = True


# ============================================================================
# Room Schemas
# ============================================================================

class RoomBase(BaseModel):
    """Basis-Schema für Room"""
    name: str = Field(..., min_length=3, max_length=200)
    description: Optional[str] = None
    time_limit_minutes: int = Field(default=60, ge=1, le=480)


class RoomCreate(RoomBase):
    """Schema für Room-Erstellung"""
    pass


class RoomUpdate(BaseModel):
    """Schema für Room-Update"""
    name: Optional[str] = Field(None, min_length=3, max_length=200)
    description: Optional[str] = None
    time_limit_minutes: Optional[int] = Field(None, ge=1, le=480)
    is_active: Optional[bool] = None


class RoomResponse(RoomBase):
    """Schema für Room-Response"""
    id: int
    teacher_id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        orm_mode = True


class RoomWithStats(RoomResponse):
    """Room mit Statistiken"""
    puzzle_count: int = 0
    student_count: int = 0
    active_sessions: int = 0


# ============================================================================
# Puzzle Schemas
# ============================================================================

class PuzzleBase(BaseModel):
    """Basis-Schema für Puzzle"""
    title: str = Field(..., min_length=3, max_length=300)
    h5p_content_id: Optional[str] = Field(None, max_length=100)
    h5p_json: Optional[Dict[str, Any]] = None
    puzzle_type: str = Field(default="multiple_choice", max_length=50)
    order_index: int = Field(default=0, ge=0)
    points: int = Field(default=10, ge=0, le=1000)
    time_limit_seconds: int = Field(default=300, ge=10, le=3600)

    @validator('puzzle_type')
    def validate_puzzle_type(cls, v):
        """Validiert Puzzle-Typ"""
        allowed_types = [
            'multiple_choice',
            'true_false',
            'fill_in_blank',
            'drag_drop',
            'essay'
        ]
        if v not in allowed_types:
            raise ValueError(f'puzzle_type must be one of: {", ".join(allowed_types)}')
        return v


class PuzzleCreate(PuzzleBase):
    """Schema für Puzzle-Erstellung"""
    room_id: int = Field(..., gt=0)


class PuzzleUpdate(BaseModel):
    """Schema für Puzzle-Update"""
    title: Optional[str] = Field(None, min_length=3, max_length=300)
    h5p_content_id: Optional[str] = None
    h5p_json: Optional[Dict[str, Any]] = None
    puzzle_type: Optional[str] = None
    order_index: Optional[int] = Field(None, ge=0)
    points: Optional[int] = Field(None, ge=0, le=1000)
    time_limit_seconds: Optional[int] = Field(None, ge=10, le=3600)


class PuzzleResponse(PuzzleBase):
    """Schema für Puzzle-Response"""
    id: int
    room_id: int
    created_at: datetime

    class Config:
        from_attributes = True
        orm_mode = True


# ============================================================================
# Assignment Schemas
# ============================================================================

class RoomAssignmentCreate(BaseModel):
    """Schema für Raum-Zuweisung"""
    room_id: int = Field(..., gt=0)
    student_id: int = Field(..., gt=0)


class RoomAssignmentResponse(BaseModel):
    """Schema für Assignment-Response"""
    id: int
    room_id: int
    student_id: int
    assigned_at: datetime

    class Config:
        from_attributes = True
        orm_mode = True


# ============================================================================
# Game Session Schemas
# ============================================================================

class GameSessionCreate(BaseModel):
    """Schema für Session-Erstellung"""
    room_id: int = Field(..., gt=0)


class GameSessionResponse(BaseModel):
    """Schema für Session-Response"""
    id: int
    room_id: int
    student_id: int
    started_at: datetime
    completed_at: Optional[datetime] = None
    total_score: int
    status: str

    class Config:
        from_attributes = True
        orm_mode = True


# ============================================================================
# Puzzle Result Schemas
# ============================================================================

class PuzzleResultCreate(BaseModel):
    """Schema für Antwort-Einreichung"""
    session_id: int = Field(..., gt=0)
    puzzle_id: int = Field(..., gt=0)
    answer_json: Dict[str, Any]
    time_taken_seconds: int = Field(..., ge=0)


class PuzzleResultResponse(BaseModel):
    """Schema für Result-Response"""
    id: int
    session_id: int
    puzzle_id: int
    answer_json: str
    is_correct: bool
    points_earned: int
    time_taken_seconds: int
    answered_at: datetime

    class Config:
        from_attributes = True
        orm_mode = True


# ============================================================================
# Progress & Statistics Schemas
# ============================================================================

class RoomProgress(BaseModel):
    """Fortschritt eines Schülers in einem Raum"""
    room_id: int
    student_id: int
    completed_puzzles: int
    total_puzzles: int
    current_score: int
    status: str


class StudentStats(BaseModel):
    """Statistiken für einen Schüler"""
    student_id: int
    student_name: str
    total_sessions: int
    completed_sessions: int
    total_score: int
    average_score: float
    total_time_spent: int


class RoomStats(BaseModel):
    """Statistiken für einen Raum"""
    room_id: int
    room_name: str
    total_students: int
    active_sessions: int
    completed_sessions: int
    average_score: float
    average_completion_time: int


# ============================================================================
# Authentication Schemas
# ============================================================================

class LoginRequest(BaseModel):
    """Schema für Login-Request"""
    username: str = Field(..., min_length=3)
    password: str = Field(..., min_length=6)


class TokenResponse(BaseModel):
    """Schema für Token-Response"""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class PasswordChange(BaseModel):
    """Schema für Passwort-Änderung"""
    old_password: str
    new_password: str = Field(..., min_length=6)


# ============================================================================
# Bulk Operations
# ============================================================================

class BulkStudentAssign(BaseModel):
    """Schema für Massen-Zuweisung"""
    room_id: int = Field(..., gt=0)
    student_ids: List[int] = Field(..., min_items=1)


class BulkPuzzleReorder(BaseModel):
    """Schema für Puzzle-Neuordnung"""
    puzzle_orders: Dict[int, int]  # puzzle_id -> new_order_index


# ============================================================================
# Response Wrappers
# ============================================================================

class MessageResponse(BaseModel):
    """Einfache Message-Response"""
    message: str
    success: bool = True


class ErrorResponse(BaseModel):
    """Error-Response"""
    detail: str
    error_code: Optional[str] = None


class PaginatedResponse(BaseModel):
    """Paginierte Response"""
    items: List[Any]
    total: int
    page: int
    page_size: int
    total_pages: int


# ============================================================================
# File Upload Schemas
# ============================================================================

class H5PUploadResponse(BaseModel):
    """Response für H5P-Upload"""
    content_id: str
    title: str
    puzzle_type: str
    file_size: int
    uploaded_at: datetime


# ============================================================================
# WebSocket Message Schemas
# ============================================================================

class WSMessage(BaseModel):
    """WebSocket-Nachricht"""
    type: str
    data: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class WSProgressUpdate(BaseModel):
    """WebSocket Progress-Update"""
    type: str = "progress_update"
    student_id: int
    room_id: int
    completed_puzzles: int
    score: int


class WSRoomStatus(BaseModel):
    """WebSocket Room-Status"""
    type: str = "room_status"
    room_id: int
    is_active: bool
    name: str