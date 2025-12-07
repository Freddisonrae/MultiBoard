"""
Datenbank-Konfiguration und Session-Management
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
load_dotenv()

# Datenbank-URL - anpassen für deine MariaDB-Installation
DATABASE_URL = os.getenv("DATABASE_URL")

# Engine erstellen
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # Prüft Verbindung vor Verwendung
    pool_recycle=3600,   # Recycelt Verbindungen nach 1 Stunde
    echo=False           # SQL-Logging (True für Debugging)
)

# Session-Factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base-Klasse für Models
Base = declarative_base()


def get_db():
    """
    Dependency für FastAPI - liefert DB-Session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Initialisiert Datenbank-Tabellen
    Wird beim Server-Start aufgerufen
    """
    Base.metadata.create_all(bind=engine)