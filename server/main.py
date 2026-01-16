"""
FastAPI Server - Hauptdatei
Startet den Server und registriert alle Routen
"""
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import timedelta
import sys

sys.path.append('..')

import sys
import os

# Parent-Verzeichnis zum Path hinzufügen für absolute Imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from server.database import get_db, init_db
from server.auth import authenticate_user, create_access_token, get_password_hash, ACCESS_TOKEN_EXPIRE_MINUTES
from server import models
from shared.models import LoginRequest, TokenResponse, User, UserCreate
from server.routes import admin, game, websocket, h5p

# FastAPI App erstellen
app = FastAPI(
    title="School Puzzle Game API",
    description="MultiRoom",
    version="1.0.0"
)

# CORS aktivieren (für Web-Admin-Panel und Desktop-Client)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In Produktion spezifischer konfigurieren
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Statische Dateien für Admin-Panel (absoluter Pfad)
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static", "admin")
if os.path.exists(STATIC_DIR):
    app.mount("/admin", StaticFiles(directory=STATIC_DIR, html=True), name="admin")
else:
    print("⚠️  Admin-Panel nicht gefunden (static/admin fehlt)")

# H5P Content verfügbar machen
H5P_CONTENT_DIR = os.path.join(os.path.dirname(__file__), "static", "h5p-content")
if os.path.exists(H5P_CONTENT_DIR):
    app.mount("/static/h5p-content", StaticFiles(directory=H5P_CONTENT_DIR), name="h5p_content")

#H5P Standalone Player verfügbar machen
H5P_STANDALONE_DIR = os.path.join(os.path.dirname(__file__), "static", "h5p-standalone")
if os.path.exists(H5P_STANDALONE_DIR):
    app.mount("/static/h5p-standalone", StaticFiles(directory=H5P_STANDALONE_DIR), name="h5p_standalone")

# Routen registrieren
app.include_router(admin.router)
app.include_router(game.router)
app.include_router(websocket.router)
app.include_router(h5p.router)


@app.on_event("startup")
async def startup_event():
    """Wird beim Server-Start ausgeführt"""
    print("🚀 Server startet...")
    init_db()
    print("✅ Datenbank initialisiert")


@app.get("/")
async def root():
    """Root-Endpunkt"""
    return {
        "message": "MultiRoom - Multi-Room Puzzle Game API",
        "version": "1.0.0",
        "admin_panel": "/admin",
        "docs": "/docs"
    }


# In main.py - Login anpassen:
@app.post("/api/auth/login", response_model=TokenResponse)
async def login(
        credentials: LoginRequest,
        db: Session = Depends(get_db)
):
    """Login-Endpunkt"""
    user = authenticate_user(db, credentials.username, credentials.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Falscher Benutzername oder Passwort",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Token erstellen
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=access_token_expires
    )

    return TokenResponse(
        access_token=access_token,
        user=User.from_orm(user)
    )

@app.post("/api/auth/register", response_model=User)
async def register(
        user_data: UserCreate,
        db: Session = Depends(get_db)
):
    """Registrierungs-Endpunkt"""
    # Username bereits vergeben?
    existing_user = db.query(models.User).filter(
        models.User.username == user_data.username
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Benutzername bereits vergeben"
        )

    # Passwort hashen
    hashed_password = get_password_hash(user_data.password)

    # User erstellen - OHNE is_active/is_approved
    db_user = models.User(
        username=user_data.username,
        password_hash=hashed_password,
        role=user_data.role,
        full_name=user_data.full_name
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return User.from_orm(db_user)



@app.get("/api/health")
async def health_check():
    """Health-Check-Endpunkt"""
    return {"status": "healthy", "service": "school-puzzle-game"}

#Erstellen von Lehrern

from pydantic import BaseModel, Field


class TeacherRegistration(BaseModel):
    username: str = Field(..., min_length=3, max_length=100)
    password: str = Field(..., min_length=8)
    full_name: str = Field(..., min_length=3)
    email: str = Field(...)  # Für Kontakt
    school_name: str  # Optionaler Kontext



if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="192.168.2.162",
        port=8000,
        reload=True,
        log_level="info"
    )
