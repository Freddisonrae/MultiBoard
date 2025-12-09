"""
Login-Dialog für Desktop-App
"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QMessageBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont


class LoginDialog(QDialog):
    """Login-Dialog"""

    login_successful = Signal(object)  # Sendet API-Client

    def __init__(self, api_client, parent=None):
        super().__init__(parent)
        self.api_client = api_client
        self.init_ui()

    def init_ui(self):
        """UI initialisieren"""
        self.setWindowTitle("School Puzzle Game - Login")
        self.setMinimumSize(400, 300)
        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 #667eea, stop:1 #764ba2
                );
            }
        """)

        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(40, 40, 40, 40)

        # Logo/Titel
        title = QLabel("🎓 School Puzzle Game")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            color: white;
            font-size: 28px;
            font-weight: bold;
        """)
        layout.addWidget(title)

        subtitle = QLabel("Schüler-Anmeldung")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("""
            color: rgba(255, 255, 255, 0.9);
            font-size: 16px;
        """)
        layout.addWidget(subtitle)

        layout.addSpacing(20)

        # Eingabefelder
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Benutzername")
        self.username_input.setStyleSheet(self._input_style())
        self.username_input.setMinimumHeight(45)
        layout.addWidget(self.username_input)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Passwort")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setStyleSheet(self._input_style())
        self.password_input.setMinimumHeight(45)
        layout.addWidget(self.password_input)

        # Login-Button
        self.login_btn = QPushButton("Anmelden")
        self.login_btn.setStyleSheet("""
            QPushButton {
                background-color: white;
                color: #667eea;
                font-size: 16px;
                font-weight: bold;
                border-radius: 8px;
                padding: 12px;
                min-height: 45px;
            }
            QPushButton:hover {
                background-color: #f0f0f0;
            }
            QPushButton:pressed {
                background-color: #e0e0e0;
            }
        """)
        self.login_btn.clicked.connect(self.handle_login)
        layout.addWidget(self.login_btn)

        # Enter-Taste aktivieren
        self.password_input.returnPressed.connect(self.handle_login)

        layout.addStretch()

        self.setLayout(layout)

    def _input_style(self):
        """Style für Input-Felder"""
        return """
            QLineEdit {
                background-color: white;
                color: black;              
                border: none;
                border-radius: 8px;
                padding: 12px;
                font-size: 14px;
            }
            QLineEdit:focus {
                background-color: #ffffff;
            }
        """

    def handle_login(self):
        """Login durchführen"""
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()

        if not username or not password:
            QMessageBox.warning(
                self,
                "Eingabe fehlt",
                "Bitte Benutzername und Passwort eingeben."
            )
            return

        # Login-Button deaktivieren
        self.login_btn.setEnabled(False)
        self.login_btn.setText("Anmeldung läuft...")

        # Login versuchen
        success = self.api_client.login(username, password)

        if success:
            self.login_successful.emit(self.api_client)
            self.accept()
        else:
            self.login_btn.setEnabled(True)
            self.login_btn.setText("Anmelden")
            QMessageBox.critical(
                self,
                "Login fehlgeschlagen",
                "Benutzername oder Passwort falsch.\nBitte versuchen Sie es erneut."
            )