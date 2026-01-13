"""
Hauptfenster der Desktop-App
"""
from PySide6.QtWidgets import QFileDialog
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QScrollArea, QMessageBox
)
from PySide6.QtCore import Qt, QtTimer
from PySide6.QtGui import QFont
from .game_widget import GameWidget


class MainWindow(QMainWindow):
    """Hauptfenster"""

    def __init__(self, api_client):
        super().__init__()
        self.api_client = api_client
        self.current_session = None
        self.auto_refresh_enabled = True

        self.refresh_button = QPushButton("🔄 Aktualisieren")
        self.refresh_button.clicked.connect(self.refresh_rooms)

        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.auto_refresh)
        self.refresh_timer.start(10000)

        self.refresh_rooms()

        self.setWindowTitle("School Puzzle Game")
        self.setMinimumSize(1024, 768)


        self.init_ui()
        self.load_rooms()

    def init_ui(self):
        """UI initialisieren"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout()
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Header
        header = QWidget()
        header.setStyleSheet("""
            background: qlineargradient(
                x1:0, y1:0, x2:1, y2:0,
                stop:0 #667eea, stop:1 #764ba2
            );
        """)
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(30, 20, 30, 20)

        title = QLabel("🎓 School Puzzle Game")
        title.setStyleSheet("""
            color: white;
            font-size: 28px;
            font-weight: bold;
        """)
        header_layout.addWidget(title)

        header_layout.addStretch()

        # Benutzer-Info
        user_name = self.api_client.user.get("full_name") or self.api_client.user.get("username")
        user_label = QLabel(f"Angemeldet als: {user_name}")
        user_label.setStyleSheet("""
            color: white;
            font-size: 16px;
        """)
        header_layout.addWidget(user_label)

        # Admin-Button nur für Admin
        if self.api_client.user.get("username") == "admin":
            admin_btn = QPushButton("Admin Bereich")
            admin_btn.setStyleSheet("""
                QPushButton {
                    background-color: white;
                    color: #27ae60;
                    font-weight: bold;
                    border-radius: 8px;
                    padding: 10px 20px;
                }
            """)
            admin_btn.clicked.connect(self.open_admin_panel)
            header_layout.addWidget(admin_btn)

        logout_btn = QPushButton("Abmelden")
        logout_btn.setStyleSheet("""
            QPushButton {
                background-color: white;
                color: #667eea;
                font-weight: bold;
                border-radius: 8px;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #f0f0f0;
            }
        """)
        logout_btn.clicked.connect(self.handle_logout)
        header_layout.addWidget(logout_btn)

        header.setLayout(header_layout)
        main_layout.addWidget(header)

        # Content
        self.content_container = QWidget()
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(30, 30, 30, 30)
        self.content_container.setLayout(content_layout)
        main_layout.addWidget(self.content_container)

        central_widget.setLayout(main_layout)

    def load_rooms(self):
        """Lädt Räume"""
        layout = self.content_container.layout()

        # UI leeren
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        # Titel
        title = QLabel("Verfügbare Räume")
        title.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #333;
            margin-bottom: 20px;
        """)
        layout.addWidget(title)

        # JSON-Upload-Button
        load_btn = QPushButton("📄 Quiz-JSON laden")
        load_btn.clicked.connect(self.load_quiz_json)
        layout.addWidget(load_btn)

        # Räume laden (online + offline kommen bereits aus dem Client)
        rooms = self.api_client.get_available_rooms()

        if not rooms:
            no_rooms = QLabel("Keine Räume verfügbar.\nBitte wende dich an deinen Lehrer.")
            no_rooms.setAlignment(Qt.AlignCenter)
            no_rooms.setStyleSheet("""
                font-size: 16px;
                color: #999;
                padding: 50px;
            """)
            layout.addWidget(no_rooms)
            layout.addStretch()
            return

        # Scroll-Bereich für Räume
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; }")

        rooms_widget = QWidget()
        rooms_layout = QVBoxLayout()
        rooms_layout.setSpacing(15)

        for room in rooms:
            card = self.create_room_card(room)
            rooms_layout.addWidget(card)

        rooms_layout.addStretch()
        rooms_widget.setLayout(rooms_layout)
        scroll.setWidget(rooms_widget)

        layout.addWidget(scroll)

    def create_room_card(self, room):
        """Raumkarte erstellen"""
        card = QWidget()
        card.setStyleSheet("""
            QWidget {
                background-color: white;
                border: 2px solid #e0e0e0;
                border-radius: 10px;
                padding: 20px;
            }
            QWidget:hover {
                border-color: #667eea;
            }
        """)

        layout = QHBoxLayout()

        # Info
        info_layout = QVBoxLayout()

        name_label = QLabel(room["name"])
        name_label.setStyleSheet("""
            font-size: 20px;
            font-weight: bold;
            color: #333;
        """)
        info_layout.addWidget(name_label)

        if room.get("description"):
            desc_label = QLabel(room["description"])
            desc_label.setWordWrap(True)
            desc_label.setStyleSheet("""
                font-size: 14px;
                color: #666;
                margin-top: 5px;
            """)
            info_layout.addWidget(desc_label)

        time_label = QLabel(f"⏱️ Zeitlimit: {room['time_limit_minutes']} Minuten")
        time_label.setStyleSheet("""
            font-size: 14px;
            color: #888;
            margin-top: 10px;
        """)
        info_layout.addWidget(time_label)

        layout.addLayout(info_layout, stretch=1)

        # Start-Button
        start_btn = QPushButton("Raum betreten")
        start_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #667eea, stop:1 #764ba2
                );
                color: white;
                font-size: 16px;
                font-weight: bold;
                border-radius: 8px;
                padding: 15px 30px;
                min-width: 150px;
            }
        """)
        start_btn.clicked.connect(lambda: self.start_room(room))
        layout.addWidget(start_btn)

        # ✨ **NEU: Rätsel bearbeiten Button**
        if self.api_client.user.get("username") == "admin":
            edit_btn = QPushButton("Rätsel bearbeiten")
            edit_btn.setStyleSheet("""
                QPushButton {
                    background-color: #27ae60;
                    color: white;
                    font-weight: bold;
                    padding: 10px 20px;
                    border-radius: 8px;
                }
            """)
            edit_btn.clicked.connect(lambda _, r=room: self.open_puzzle_editor(r))
            layout.addWidget(edit_btn)

        card.setLayout(layout)
        return card

    def start_room(self, room):
        """Raum starten"""
        session = self.api_client.start_session(room["id"])

        if not session:
            QMessageBox.critical(self, "Fehler", "Raum konnte nicht gestartet werden.")
            return

        self.current_session = session
        puzzles = self.api_client.get_session_puzzles(session["id"])

        if not puzzles:
            QMessageBox.warning(self, "Keine Rätsel", "Dieser Raum enthält noch keine Rätsel.")
            return

        self.show_game(session, puzzles)

    def show_game(self, session, puzzles):
        """Spiel anzeigen"""
        layout = self.content_container.layout()
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        game_widget = GameWidget(self.api_client, session, puzzles, self)
        game_widget.session_completed.connect(self.load_rooms)
        layout.addWidget(game_widget)

    def handle_logout(self):
        reply = QMessageBox.question(self, "Abmelden", "Möchten Sie sich wirklich abmelden?",
                                     QMessageBox.Yes | QMessageBox.No)

        if reply == QMessageBox.Yes:
            self.close()

    def open_admin_panel(self):
        from .admin_room_dialog import AdminRoomDialog
        dialog = AdminRoomDialog(self.api_client, self)

        if dialog.exec():
            QMessageBox.information(self, "Info", "Admin-Daten aktualisiert.")
            self.load_rooms()

    def open_puzzle_editor(self, room):
        from .admin_puzzle_dialog import AdminPuzzleDialog
        dialog = AdminPuzzleDialog(self.api_client, room["id"], self)
        dialog.exec()

    def load_quiz_json(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Quiz JSON auswählen",
            "",
            "JSON Dateien (*.json)"
        )
        if not path:
            return

        try:
            self.api_client.load_quiz_json_file(path)
            self.load_rooms()  # refresh
        except Exception as e:
            QMessageBox.critical(self, "Fehler", f"JSON konnte nicht geladen werden:\n{e}")

    def refresh_rooms(self):
        """Lädt Raumliste neu"""
        try:
            rooms = self.api_client.get_available_rooms()
            self.update_room_list(rooms)
        except Exception as e:
            print(f"Fehler beim Aktualisieren: {e}")

    def update_room_list(self, rooms):
        """Aktualisiert die Raumliste in der UI"""
        # Beispiel mit QListWidget:
        current_selection = self.room_list.currentRow()

        self.room_list.clear()

        for room in rooms:
            mode_icon = "📄" if room.get("mode") == "offline" else "🌐"
            self.room_list.addItem(f"{mode_icon} {room['name']}")

        # Auswahl wiederherstellen
        if current_selection >= 0 and current_selection < self.room_list.count():
            self.room_list.setCurrentRow(current_selection)

    def on_room_created(self, room: dict):
        """Wird aufgerufen wenn ein neuer Raum erstellt wurde"""
        print(f"Neuer Raum erstellt: {room['name']}")
        # Sofort aktualisieren (ohne auf Timer zu warten)
        self.refresh_rooms()

