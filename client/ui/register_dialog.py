from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QFrame, QMessageBox
)
from PySide6.QtCore import Qt


class RegisterDialog(QDialog):
    def __init__(self, api_client, parent=None):
        super().__init__(parent)
        self.api_client = api_client

        self.setWindowTitle("Schüler registrieren")
        self.setFixedSize(560, 520)
        self.setModal(True)

        root = QVBoxLayout(self)
        root.setContentsMargins(18, 18, 18, 18)
        root.setSpacing(14)

        header = QFrame()
        header.setObjectName("Card")
        h = QVBoxLayout(header)
        h.setContentsMargins(18, 16, 18, 16)
        h.setSpacing(6)

        title = QLabel("Schüler-Account erstellen")
        title.setObjectName("Title")
        subtitle = QLabel("Registriere dich als Schüler und starte anschließend ein Spiel.")
        subtitle.setObjectName("Muted")

        h.addWidget(title)
        h.addWidget(subtitle)
        root.addWidget(header)

        card = QFrame()
        card.setObjectName("Card")
        c = QVBoxLayout(card)
        c.setContentsMargins(18, 18, 18, 18)
        c.setSpacing(10)

        self.username = QLineEdit()
        self.username.setPlaceholderText("Benutzername")

        self.full_name = QLineEdit()
        self.full_name.setPlaceholderText("Vorname Nachname")

        self.password = QLineEdit()
        self.password.setPlaceholderText("Passwort (max. 72 Zeichen)")
        self.password.setEchoMode(QLineEdit.Password)

        self.password2 = QLineEdit()
        self.password2.setPlaceholderText("Passwort wiederholen")
        self.password2.setEchoMode(QLineEdit.Password)

        c.addWidget(QLabel("Benutzername"))
        c.addWidget(self.username)
        c.addWidget(QLabel("Name"))
        c.addWidget(self.full_name)
        c.addWidget(QLabel("Passwort"))
        c.addWidget(self.password)
        c.addWidget(QLabel("Passwort wiederholen"))
        c.addWidget(self.password2)

        btn_row = QHBoxLayout()
        cancel = QPushButton("Abbrechen")
        cancel.setObjectName("GhostBtn")
        cancel.clicked.connect(self.reject)

        create = QPushButton("Registrieren")
        create.clicked.connect(self.on_register)

        btn_row.addWidget(cancel)
        btn_row.addStretch()
        btn_row.addWidget(create)

        c.addLayout(btn_row)
        root.addWidget(card)

        note = QLabel("Hinweis: Diese Registrierung erstellt immer einen Schüler-Account.")
        note.setObjectName("Muted")
        note.setAlignment(Qt.AlignCenter)
        root.addWidget(note)

    def on_register(self):
        username = self.username.text().strip()
        full_name = self.full_name.text().strip()
        password = self.password.text()
        password2 = self.password2.text()

        if not username or not password:
            QMessageBox.warning(self, "Fehler", "Bitte Benutzername und Passwort eingeben.")
            return

        if password != password2:
            QMessageBox.warning(self, "Fehler", "Die Passwörter stimmen nicht überein.")
            return

        # bcrypt limitation: 72 bytes
        if len(password.encode("utf-8")) > 72:
            QMessageBox.warning(self, "Fehler", "Passwort ist zu lang (max. 72 Bytes).")
            return

        try:
            ok = self.api_client.register_student(
                username=username,
                password=password,
                full_name=full_name
            )
        except Exception as e:
            QMessageBox.critical(self, "Fehler", str(e))
            return

        if ok:
            QMessageBox.information(self, "Erfolg", "Schüler registriert. Du kannst dich jetzt anmelden.")
            self.accept()
        else:
            QMessageBox.critical(self, "Fehler", "Registrierung fehlgeschlagen (Username evtl. vergeben).")