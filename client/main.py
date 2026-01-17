"""
Haupt-Einstiegspunkt der Desktop-App
"""
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
    app.setAttribute(Qt.AA_EnableHighDpiScaling)

    # API-Client erstellen
    # Server-URL anpassen falls nötig
    api_client = APIClient(base_url="http://127.0.0.1:8000")

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