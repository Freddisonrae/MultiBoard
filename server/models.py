"""
SQLAlchemy Database Models
"""
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum('teacher', 'student'), nullable=False, default='student', index=True)
    full_name = Column(String(200))
    created_at = Column(DateTime, default=datetime.utcnow)


    # Relationships
    rooms = relationship("Room", back_populates="teacher")
    game_sessions = relationship("GameSession", back_populates="student")
    room_assignments = relationship("RoomAssignment", back_populates="student")


class Room(Base):
    __tablename__ = "rooms"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    teacher_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    time_limit_minutes = Column(Integer, default=60)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=False, nullable=False)
    # Relationships
    teacher = relationship("User", back_populates="rooms")
    puzzles = relationship("Puzzle", back_populates="room", cascade="all, delete-orphan")
    game_sessions = relationship("GameSession", back_populates="room")
    room_assignments = relationship("RoomAssignment", back_populates="room")


class Puzzle(Base):
    __tablename__ = "puzzles"

    id = Column(Integer, primary_key=True, index=True)
    room_id = Column(Integer, ForeignKey("rooms.id"), nullable=False, index=True)
    title = Column(String(300), nullable=False)
    h5p_content_id = Column(String(100))
    h5p_json = Column(Text)
    puzzle_type = Column(String(50), default='multiple_choice')
    order_index = Column(Integer, default=0, index=True)
    points = Column(Integer, default=10)
    time_limit_seconds = Column(Integer, default=300)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    room = relationship("Room", back_populates="puzzles")
    results = relationship("PuzzleResult", back_populates="puzzle")


class RoomAssignment(Base):
    __tablename__ = "room_assignments"

    id = Column(Integer, primary_key=True, index=True)
    room_id = Column(Integer, ForeignKey("rooms.id"), nullable=False, index=True)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    assigned_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    room = relationship("Room", back_populates="room_assignments")
    student = relationship("User", back_populates="room_assignments")


class GameSession(Base):
    __tablename__ = "game_sessions"

    id = Column(Integer, primary_key=True, index=True)
    room_id = Column(Integer, ForeignKey("rooms.id"), nullable=False, index=True)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    total_score = Column(Integer, default=0)
    status = Column(Enum('in_progress', 'completed', 'abandoned'), default='in_progress', index=True)

    # Relationships
    room = relationship("Room", back_populates="game_sessions")
    student = relationship("User", back_populates="game_sessions")
    results = relationship("PuzzleResult", back_populates="session", cascade="all, delete-orphan")


class PuzzleResult(Base):
    __tablename__ = "puzzle_results"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("game_sessions.id"), nullable=False, index=True)
    puzzle_id = Column(Integer, ForeignKey("puzzles.id"), nullable=False, index=True)
    answer_json = Column(Text)
    is_correct = Column(Boolean, default=False)
    points_earned = Column(Integer, default=0)
    time_taken_seconds = Column(Integer)
    answered_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    session = relationship("GameSession", back_populates="results")
    puzzle = relationship("Puzzle", back_populates="results")