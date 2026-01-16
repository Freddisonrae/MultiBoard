from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, QSpinBox,
    QPushButton, QHBoxLayout, QMessageBox, QComboBox
)
from PySide6.QtCore import Qt


class AdminRoomDialog(QDialog):
    """Admin-Dialog zum Erstellen eines Raums"""

    def __init__(self, api_client, parent=None):
        super().__init__(parent)
        self.api_client = api_client

        self.setWindowTitle("Admin – Raum erstellen")
        self.setMinimumSize(400, 350)

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)

        # Titel
        title = QLabel("Neuen Raum erstellen")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 22px; font-weight: bold;")
        layout.addWidget(title)

        # Name
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Raumname")
        layout.addWidget(self.name_input)

        # Beschreibung
        self.desc_input = QLineEdit()
        self.desc_input.setPlaceholderText("Beschreibung")
        layout.addWidget(self.desc_input)

        # Zeitlimit
        self.time_input = QSpinBox()
        self.time_input.setRange(1, 300)
        self.time_input.setValue(15)
        self.time_input.setPrefix("Zeitlimit: ")
        self.time_input.setSuffix(" Minuten")
        layout.addWidget(self.time_input)

        # Modus: Offline oder Online
        mode_label = QLabel("Speichermodus:")
        layout.addWidget(mode_label)

        self.mode_select = QComboBox()
        self.mode_select.addItems(["Offline", "Online"])
        layout.addWidget(self.mode_select)

        # Buttons
        btn_layout = QHBoxLayout()

        save_btn = QPushButton("Erstellen")
        save_btn.clicked.connect(self.handle_create)

        cancel_btn = QPushButton("Abbrechen")
        cancel_btn.clicked.connect(self.reject)

        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)

        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def handle_create(self):
        """Raum erstellen"""
        name = self.name_input.text().strip()
        desc = self.desc_input.text().strip()
        minutes = self.time_input.value()
        mode = self.mode_select.currentText()

        if not name:
            QMessageBox.warning(self, "Fehler", "Bitte einen Raumname eingeben.")
            return

        room_data = {
            "name": name,
            "description": desc,
            "time_limit_minutes": minutes
        }

        # --- OFFLINE SPEICHERN ---
        if mode == "Offline":
            if not hasattr(self.api_client, "offline_rooms"):
                self.api_client.offline_rooms = []

            room_data["id"] = len(self.api_client.offline_rooms) + 1000
            self.api_client.offline_rooms.append(room_data)

            QMessageBox.information(self, "Gespeichert", "Raum wurde offline erstellt.")
            self.accept()
            return

        # --- ONLINE SPEICHERN ---
        if mode == "Online":
            result = self.api_client.start_session(room_data)
            if result:
                QMessageBox.information(self, "Erfolg", "Raum wurde online gespeichert.")
                self.accept()
            else:
                QMessageBox.critical(self, "Fehler", "Raum konnte nicht auf dem Server gespeichert werden.")