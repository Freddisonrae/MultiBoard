import mariadb


def get_connection():
    try:
        conn = mariadb.connect(
            user="game_user",
            password="1234",
            host="192.168.0.50",
            port=3306,
            database="multiroom_db"
        )
        return conn
    except mariadb.Error as e:
        print(f"Fehler bei der Datenbankverbindung: {e}")
        return None