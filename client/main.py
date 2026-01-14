"""
Haupt-Einstiegspunkt der Desktop-App
"""
from pathlib import Path
import os
import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

from api.client import APIClient
from ui.login_dialog import LoginDialog
from ui.main_window import MainWindow


def main():
    """Hauptfunktion"""
    # Qt-Anwendung erstellen
    app = QApplication(sys.argv)
    app.setApplicationName("MultiBoard")

    # High-DPI-Support für moderne Displays
    ## app.setAttribute(Qt.AA_EnableHighDpiScaling)

    # API-Client erstellen
    # Server-URL anpassen falls nötig
    api_client = APIClient(base_url="http://192.168.2.115:8000")

    DEV_BYPASS_LOGIN = os.getenv("DEV_BYPASS_LOGIN", "0") == "1"
    if DEV_BYPASS_LOGIN:
        api_client.user = {
    "username": "admin",
    "full_name": "Dev Admin",
    "role": "admin",      # <- Admin-Rechte
    "is_admin": True}
        api_client.token = "DEV_TOKEN"
        main_window = MainWindow(api_client)
        main_window.show()
        sys.exit(app.exec())
    # Login-Dialog anzeigen
    login_dialog = LoginDialog(api_client)

    if login_dialog.exec() == LoginDialog.Accepted:
        # Login erfolgreich -> Hauptfenster anzeigen
        main_window = MainWindow(api_client)
        main_window.show()

        # Event-Loop starten
        sys.exit(app.exec())
    else:
        # Login abgebrochen
        sys.exit(0)


if __name__ == "__main__":
    main()