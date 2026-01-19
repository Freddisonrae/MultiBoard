"""
Authentifizierung und Autorisierung
JWT-Token-basiert - Unterstützt HTTPBearer UND Header-basiert
"""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from .database import get_db
from . import models

# Sicherheits-Konfiguration
SECRET_KEY = "dein-geheimer-schluessel-hier-aendern-in-produktion"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 480  # 8 Stunden

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifiziert Passwort gegen Hash"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Erstellt Passwort-Hash"""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Erstellt JWT Access Token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def authenticate_user(db: Session, username: str, password: str):
    """Authentifiziert Benutzer"""
    user = db.query(models.User).filter(models.User.username == username).first()

    if not user:
        return None

    if not verify_password(password, user.password_hash):
        return None

    return user


async def get_current_user(
        authorization: Optional[str] = Header(None),
        db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Ungültige Authentifizierung",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if not authorization:
        raise credentials_exception

    # Token extrahieren
    token = authorization
    if authorization.startswith("Bearer "):
        token = authorization.replace("Bearer ", "")

    print(f"Auth-Token empfangen: {token[:20]}...")  # DEBUG

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception

        user_id = int(user_id)
        print(f"Token dekodiert: User-ID={user_id}")  # DEBUG

    except JWTError as e:
        print(f"JWT-Fehler: {e}")  # DEBUG
        raise credentials_exception

    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is None:
        print(f"User mit ID {user_id} nicht gefunden")  # DEBUG
        raise credentials_exception

    print(f"User authentifiziert: {user.username} (Role: {user.role})")  # DEBUG
    return user


async def get_current_teacher(current_user: models.User = Depends(get_current_user)):
    """Stellt sicher, dass aktueller Benutzer ein Lehrer ist"""
    if current_user.role != "teacher":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Nur für Lehrer zugänglich"
        )
    return current_user


async def get_current_student(current_user: models.User = Depends(get_current_user)):
    """Stellt sicher, dass aktueller Benutzer ein Schüler ist"""
    if current_user.role != "student":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Nur für Schüler zugänglich"
        )
    return current_user