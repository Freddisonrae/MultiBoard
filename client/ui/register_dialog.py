from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox, QCheckBox
)
from PySide6.QtCore import Qt


class RegisterDialog(QDialog):
    def __init__(self, api_client, parent=None):
        super().__init__(parent)
        self.api_client = api_client
        self.setWindowTitle("Registrieren")
        self.setMinimumSize(380, 320)

        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        title = QLabel("Account erstellen")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size:18px; font-weight:bold;")
        layout.addWidget(title)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Benutzername")
        layout.addWidget(self.username_input)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Passwort")
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_input)

        self.password_confirm_input = QLineEdit()
        self.password_confirm_input.setPlaceholderText("Passwort bestätigen")
        self.password_confirm_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_confirm_input)

        self.admin_checkbox = QCheckBox("Admin-Rechte (nur wenn erlaubt)")
        layout.addWidget(self.admin_checkbox)

        self.register_btn = QPushButton("Registrieren")
        self.register_btn.clicked.connect(self.handle_register)
        layout.addWidget(self.register_btn)

    def handle_register(self):
        username = self.username_input.text().strip()
        pw = self.password_input.text()
        pw2 = self.password_confirm_input.text()
        is_admin = self.admin_checkbox.isChecked()

        if not username or not pw:
            QMessageBox.warning(self, "Fehler", "Bitte Benutzername und Passwort eingeben.")
            return
        if pw != pw2:
            QMessageBox.warning(self, "Fehler", "Passwörter stimmen nicht überein.")
            return

        ok = self.api_client.register(username=username, password=pw, is_admin=is_admin)
        if ok:
            QMessageBox.information(self, "Erfolg", "Account erstellt. Du kannst dich jetzt anmelden.")
            self.accept()
        else:
            QMessageBox.critical(self, "Fehler", "Registrierung fehlgeschlagen (User existiert evtl. schon).")