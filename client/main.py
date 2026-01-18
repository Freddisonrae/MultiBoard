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

    # ✅ Globales Styling: schwarzer Text auf hellem Hintergrund
    app.setStyleSheet("""
        /* ✅ Nur Text standardmäßig schwarz machen — KEIN globales Background! */
        QWidget {
            color: #000000;
            font-size: 14px;
        }

        QPushButton {
            background-color: #f3f4f6;
            color: #000000;
            border: 1px solid #d1d5db;
            padding: 8px 10px;
            border-radius: 8px;
        }
        QPushButton:hover { background-color: #e5e7eb; }
        QPushButton:pressed { background-color: #d1d5db; }

        QLineEdit, QTextEdit, QPlainTextEdit, QComboBox, QSpinBox {
            background-color: #ffffff;
            color: #000000;
            border: 1px solid #d1d5db;
            padding: 8px;
            border-radius: 8px;
            selection-background-color: #93c5fd;
            selection-color: #000000;
        }

        QScrollArea { border: none; background: transparent; }

        QListWidget, QTableWidget {
            background-color: #ffffff;
            color: #000000;
            border: 1px solid #e5e7eb;
            border-radius: 10px;
            selection-background-color: #dbeafe;
            selection-color: #000000;
        }

        QMessageBox QLabel { color: #000000; }
    """)

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