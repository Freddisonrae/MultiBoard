"""
Haupt-Einstiegspunkt der Desktop-App - Modernes Theme
"""
import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

from api.client import APIClient
from ui.login_dialog import LoginDialog
from ui.main_window import MainWindow
from ui.themen import APP_QSS


def main():
    """Hauptfunktion"""
    # Qt-Anwendung erstellen
    app = QApplication(sys.argv)
    app.setApplicationName("MultiBoard")

    # ✅ Modernes Theme anwenden
    app.setStyleSheet(APP_QSS)

    # High-DPI-Support für moderne Displays
    app.setAttribute(Qt.AA_EnableHighDpiScaling)

    # API-Client erstellen
    api_client = APIClient(base_url="http://127.0.0.1:8000")

    # Login-Dialog anzeigen
    login_dialog = LoginDialog(api_client)

    if login_dialog.exec() == LoginDialog.Accepted:
        main_window = MainWindow(api_client)
        main_window.show()
        sys.exit(app.exec())
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()