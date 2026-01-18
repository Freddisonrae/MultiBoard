"""
Login-Dialog für Desktop-App - Updated mit modernem Theme
"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QMessageBox, QFrame
)
from .register_dialog import RegisterDialog
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont


class LoginDialog(QDialog):
    """Login-Dialog"""

    login_successful = Signal(object)  # Sendet API-Client

    def __init__(self, api_client, parent=None):
        super().__init__(parent)
        self.api_client = api_client
        self.setObjectName("LoginDialog")
        self.init_ui()

    def init_ui(self):
        """UI initialisieren"""
        self.setWindowTitle("School Puzzle Game - Login")
        self.setMinimumSize(520, 560)
        self.resize(520, 560)

        # Haupt-Layout
        main_layout = QVBoxLayout()
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Content Card
        content_card = QFrame()
        content_card.setObjectName("Card")
        card_layout = QVBoxLayout(content_card)
        card_layout.setSpacing(20)
        card_layout.setContentsMargins(40, 50, 40, 50)

        # Logo/Titel
        title = QLabel("🎓 School Puzzle Game")
        title.setObjectName("Title")
        title.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(title)

        subtitle = QLabel("Schüler-Anmeldung")
        subtitle.setObjectName("Subtitle")
        subtitle.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(subtitle)

        card_layout.addSpacing(10)

        # Benutzername
        username_label = QLabel("Benutzername")
        card_layout.addWidget(username_label)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Benutzername eingeben")
        self.username_input.setMinimumHeight(40)
        card_layout.addWidget(self.username_input)

        # Passwort
        password_label = QLabel("Passwort")
        card_layout.addWidget(password_label)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Passwort eingeben")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setMinimumHeight(40)
        card_layout.addWidget(self.password_input)

        card_layout.addSpacing(10)

        # Login-Button
        self.login_btn = QPushButton("Anmelden")
        self.login_btn.setObjectName("PrimaryButton")
        self.login_btn.setMinimumHeight(44)
        self.login_btn.clicked.connect(self.handle_login)
        card_layout.addWidget(self.login_btn)

        # Registrieren-Button
        self.register_btn = QPushButton("Neuen Account erstellen")
        self.register_btn.setObjectName("GhostBtn")
        self.register_btn.setMinimumHeight(40)
        self.register_btn.clicked.connect(self.open_register)
        card_layout.addWidget(self.register_btn)

        # Enter-Taste aktivieren
        self.password_input.returnPressed.connect(self.handle_login)

        card_layout.addStretch()

        main_layout.addWidget(content_card)
        self.setLayout(main_layout)

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

    def open_register(self):
        dialog = RegisterDialog(self.api_client, self)
        dialog.exec()