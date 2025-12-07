import os

import pymysql

from dotenv import load_dotenv

load_dotenv()

# Verbindung OHNE Datenbank
connection = pymysql.connect(
    user = os.getenv("DB_USER"),
    password = os.getenv("DB_PASSWORD"),
    host = os.getenv("DB_HOST"),
)

with connection.cursor() as cursor:
    # Datenbank erstellen falls nicht existiert
    cursor.execute("CREATE DATABASE IF NOT EXISTS abiprj25")
    print("✅ Datenbank erstellt")

    # Zur Datenbank wechseln
    cursor.execute("abiprj25")

    # SQL-Script einlesen
    with open('../database/schema.sql', 'r', encoding='utf-8') as f:
        sql = f.read()

    # Statements ausführen
    for statement in sql.split(';'):
        if statement.strip():
            cursor.execute(statement)

    connection.commit()
    print("✅ Tabellen erstellt")

connection.close()