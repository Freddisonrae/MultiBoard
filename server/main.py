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
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

sys.path.append('..')

from .database import get_db, init_db
from .auth import authenticate_user, create_access_token, get_password_hash, ACCESS_TOKEN_EXPIRE_MINUTES
from . import models
from shared.models import LoginRequest, TokenResponse, User, UserCreate
from .routes import admin, game, websocket

# FastAPI App erstellen
app = FastAPI(
    title="School Puzzle Game API",
    description="Multi-Room-Rätselspiel für Schulen",
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

# Statische Dateien für Admin-Panel
app.mount(
    "/admin",
    StaticFiles(directory=os.path.join(BASE_DIR, "static", "admin"), html=True),
    name="admin"
)

# Routen registrieren
app.include_router(admin.router)
app.include_router(game.router)
app.include_router(websocket.router)


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
        "message": "School Puzzle Game API",
        "version": "1.0.0",
        "admin_panel": "/admin",
        "docs": "/docs"
    }


@app.post("/api/auth/login", response_model=TokenResponse)
async def login(
        credentials: LoginRequest,
        db: Session = Depends(get_db)
):
    """
    Login-Endpunkt für Lehrer und Schüler
    Gibt JWT-Token zurück
    """
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
    """
    Registrierungs-Endpunkt
    Erstellt neuen Benutzer (Schüler oder Lehrer)
    """
    # Prüfen ob Username bereits existiert
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

    # Benutzer erstellen
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


if __name__ == "__main__":
    import uvicorn

    # Server starten
    # Development: mit Reload
    # Production: ohne Reload, mit mehreren Workern
    uvicorn.run(
        "server.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )



