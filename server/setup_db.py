#!/usr/bin/env python3
import os
import sys
import pymysql
from pymysql import OperationalError
from dotenv import load_dotenv

load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_NAME = os.getenv("DB_NAME")  # erwartet z. B. "abiprj25"
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), '..', 'database', 'schema.sql')

if not DB_NAME:
    print("❌ Fehler: DB_NAME ist nicht in der .env gesetzt. Bitte DB_NAME=dein_db_name hinzufügen.")
    sys.exit(1)

try:
    # Verbindung direkt zur ZIEL-Datenbank (wir erstellen die DB hier NICHT)
    connection = pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=False
    )
except OperationalError as e:
    errno = e.args[0] if e.args else None
    msg = e.args[1] if len(e.args) > 1 else str(e)
    if errno == 1049:  # Unknown database
        print(f"❌ Datenbank '{DB_NAME}' existiert nicht. Bitte erstelle die Datenbank manuell (siehe unten).")
    elif errno == 1044:  # Access denied to database
        print(f"❌ Zugriff verweigert für Benutzer '{DB_USER}' auf Datenbank '{DB_NAME}'. Prüfe Berechtigungen.")
    elif errno == 1045:  # Access denied (auth)
        print(f"❌ Authentifizierungsfehler: Benutzername/Passwort vermutlich falsch.")
    else:
        print(f"❌ Verbindung fehlgeschlagen: {msg} (Errno {errno})")
    sys.exit(1)

try:
    with connection:
        with connection.cursor() as cursor:
            # Lade schema.sql
            if not os.path.exists(SCHEMA_PATH):
                print(f"❌ Schema-Datei nicht gefunden: {SCHEMA_PATH}")
                sys.exit(1)

            with open(SCHEMA_PATH, 'r', encoding='utf-8') as f:
                sql = f.read()

            # Einfache Aufteilung der Statements; für sehr komplexe SQL-Skripte ggf. parser verwenden
            statements = [s.strip() for s in sql.split(';') if s.strip()]

            for stmt in statements:
                try:
                    cursor.execute(stmt)
                except OperationalError as e:
                    # Falls ein einzelnes Statement fehlschlägt, werfen wir es nach Rollback
                    print(f"❌ Fehler beim Ausführen eines Statements:\n{e}\nStatement:\n{stmt[:200]}...")
                    connection.rollback()
                    raise

        connection.commit()
        print("✅ Tabellen/Schema erfolgreich angewendet.")
except Exception as e:
    print("❌ Vorgang abgebrochen wegen eines Fehlers.")
    print("Details:", str(e))
    sys.exit(1)

