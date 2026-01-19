"""
Hauptfenster der Desktop-App - MIT modernem Indigo-Design
"""
from PySide6.QtWidgets import QFileDialog
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QScrollArea, QMessageBox
)
from PySide6.QtCore import Qt, QTimer, Signal, QObject
from PySide6.QtGui import QFont

# 🔥 WICHTIG: Beide Widgets importieren
from .game_widget import GameWidget
from .h5p_game_widget import H5PGameWidget


class WebSocketSignalBridge(QObject):
    rooms_updated = Signal(list)


class MainWindow(QMainWindow):
    """Hauptfenster"""

    def __init__(self, api_client):
        super().__init__()
        self.api_client = api_client
        self.current_session = None

        self.setWindowTitle("MultiBoard")
        self.setMinimumSize(1024, 768)

        self.ws_bridge = WebSocketSignalBridge()
        self.ws_bridge.rooms_updated.connect(self.on_rooms_updated_from_websocket)

        self.init_ui()
        self.load_rooms()
        self.connect_websocket()

    def connect_websocket(self):
        """WebSocket-Verbindung für Live-Updates starten"""
        try:
            def on_ws_rooms_updated(rooms):
                self.ws_bridge.rooms_updated.emit(rooms)

            self.api_client.connect_websocket(on_ws_rooms_updated)
            print("✅ WebSocket-Verbindung wird aufgebaut...")

        except Exception as e:
            print(f"WebSocket-Fehler: {e}")

    def on_rooms_updated_from_websocket(self, rooms):
        """Wird aufgerufen wenn WebSocket meldet: Räume haben sich geändert"""
        print(f"🔄 WebSocket-Update empfangen: {len(rooms)} Räume")

        if hasattr(self, 'refresh_button'):
            original_text = self.refresh_button.text()
            self.refresh_button.setText("✨")
            QTimer.singleShot(500, lambda: self.refresh_button.setText(original_text))

        self.load_rooms()

    def init_ui(self):
        """UI initialisieren"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout()
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Header - UPDATED mit Indigo-Hintergrund
        header = QWidget()
        header.setObjectName("HeaderWidget")
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(30, 20, 30, 20)

        title = QLabel("MultiBoard")
        title.setObjectName("Title")
        header_layout.addWidget(title)

        header_layout.addStretch()

        user_name = self.api_client.user.get("full_name") or self.api_client.user.get("username")
        user_label = QLabel(f"Angemeldet als: {user_name}")
        user_label.setObjectName("Muted")
        header_layout.addWidget(user_label)

        # WebSocket Status
        self.ws_status_label = QLabel("●")
        self.ws_status_label.setStyleSheet("""
            QLabel {
                color: rgba(255, 255, 255, 0.6);
                font-size: 20px;
                background: transparent;
            }
        """)
        self.ws_status_label.setToolTip("WebSocket: Verbindung wird aufgebaut...")
        header_layout.addWidget(self.ws_status_label)

        self.ws_status_timer = QTimer(self)
        self.ws_status_timer.timeout.connect(self.update_ws_status)
        self.ws_status_timer.start(2000)

        # Refresh Button
        self.refresh_button = QPushButton("🔄")
        self.refresh_button.setMinimumSize(40, 36)
        self.refresh_button.setMaximumSize(40, 36)
        self.refresh_button.clicked.connect(self.manual_refresh)
        self.refresh_button.setToolTip("Raumliste aktualisieren")
        header_layout.addWidget(self.refresh_button)

        # Admin Button (falls Admin)
        if self.api_client.user.get("username") == "admin":
            admin_btn = QPushButton("Admin Bereich")
            admin_btn.setMinimumHeight(36)
            admin_btn.setStyleSheet("""
                QPushButton {
                    background: #10B981;
                    color: #FFFFFF;
                    border: none;
                    font-weight: 600;
                    padding: 8px 16px;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    background: #059669;
                }
            """)
            admin_btn.clicked.connect(self.open_admin_panel)
            header_layout.addWidget(admin_btn)

        # Logout Button
        logout_btn = QPushButton("Abmelden")
        logout_btn.setMinimumHeight(36)
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

    def update_ws_status(self):
        """WebSocket-Status visuell anzeigen"""
        if hasattr(self.api_client, '_ws_connected') and self.api_client._ws_connected:
            self.ws_status_label.setStyleSheet("""
                QLabel {
                    color: #10B981;
                    font-size: 20px;
                    background: transparent;
                }
            """)
            self.ws_status_label.setToolTip("WebSocket: Verbunden ✓ (Live-Updates aktiv)")
        else:
            self.ws_status_label.setStyleSheet("""
                QLabel {
                    color: #EF4444;
                    font-size: 20px;
                    background: transparent;
                }
            """)
            self.ws_status_label.setToolTip("WebSocket: Nicht verbunden")

    def manual_refresh(self):
        """Manuelles Aktualisieren mit visuellem Feedback"""
        self.refresh_button.setEnabled(False)
        self.refresh_button.setText("⏳")

        self.load_rooms()

        QTimer.singleShot(1000, lambda: (
            self.refresh_button.setEnabled(True),
            self.refresh_button.setText("🔄")
        ))

    def load_rooms(self):
        """Lädt Räume"""
        layout = self.content_container.layout()

        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        title = QLabel("Verfügbare Räume")
        title.setObjectName("Title")
        title.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: 700;
                color: #111827;
                margin-bottom: 20px;
                background: transparent;
            }
        """)
        layout.addWidget(title)

        load_btn = QPushButton("Quiz-JSON laden")
        load_btn.setObjectName("GhostBtn")
        load_btn.setMinimumHeight(40)
        load_btn.clicked.connect(self.load_quiz_json)
        layout.addWidget(load_btn)

        rooms = self.api_client.get_available_rooms()

        if not rooms:
            no_rooms = QLabel("Keine Räume verfügbar.\nBitte wende dich an deinen Lehrer.")
            no_rooms.setAlignment(Qt.AlignCenter)
            no_rooms.setObjectName("Muted")
            no_rooms.setStyleSheet("""
                QLabel {
                    font-size: 16px;
                    color: #9CA3AF;
                    padding: 50px;
                    background: transparent;
                }
            """)
            layout.addWidget(no_rooms)
            layout.addStretch()
            return

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

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
        from PySide6.QtWidgets import QFrame

        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background: #FFFFFF;
                border: 1px solid #E5E7EB;
                border-radius: 4px;
                padding: 20px;
            }
            QFrame:hover {
                border-color: #4F46E5;
            }
        """)

        layout = QHBoxLayout()

        info_layout = QVBoxLayout()

        name_label = QLabel(room["name"])
        name_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: 700;
                color: #111827;
                background: transparent;
            }
        """)
        info_layout.addWidget(name_label)

        if room.get("description"):
            desc_label = QLabel(room["description"])
            desc_label.setWordWrap(True)
            desc_label.setStyleSheet("""
                QLabel {
                    font-size: 14px;
                    color: #6B7280;
                    margin-top: 5px;
                    background: transparent;
                }
            """)
            info_layout.addWidget(desc_label)

        time_label = QLabel(f" Zeitlimit: {room['time_limit_minutes']} Minuten")
        time_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #6B7280;
                margin-top: 10px;
                background: transparent;
            }
        """)
        info_layout.addWidget(time_label)

        layout.addLayout(info_layout, stretch=1)

        start_btn = QPushButton("Raum betreten")
        start_btn.setStyleSheet("""
            QPushButton {
                background: #4F46E5;
                color: #FFFFFF;
                border: none;
                border-radius: 4px;
                padding: 12px 24px;
                font-size: 14px;
                font-weight: 600;
                min-width: 150px;
                min-height: 44px;
            }
            QPushButton:hover {
                background: #4338CA;
            }
        """)
        start_btn.clicked.connect(lambda: self.start_room(room))
        layout.addWidget(start_btn)

        if self.api_client.user.get("username") == "admin":
            edit_btn = QPushButton("Rätsel bearbeiten")
            edit_btn.setStyleSheet("""
                QPushButton {
                    background: #10B981;
                    color: #FFFFFF;
                    border: none;
                    border-radius: 4px;
                    padding: 10px 20px;
                    font-size: 14px;
                    font-weight: 600;
                    min-width: 140px;
                    min-height: 40px;
                }
                QPushButton:hover {
                    background: #059669;
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
        """Spiel anzeigen - wählt automatisch richtiges Widget"""
        layout = self.content_container.layout()
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        #
        has_h5p = any(p.get("h5p_content_id") for p in puzzles)

        if has_h5p:
            print("Nutze H5P Game Widget")
            game_widget = H5PGameWidget(self.api_client, session, puzzles, self)
        else:
            print("Nutze Standard Game Widget")
            game_widget = GameWidget(self.api_client, session, puzzles, self)

        # Verbinde beide Signals
        game_widget.session_completed.connect(self.load_rooms)

        #  exit_requested Signal verbinden (nur H5P Widget hat das)
        if hasattr(game_widget, 'exit_requested'):
            game_widget.exit_requested.connect(self.load_rooms)

        layout.addWidget(game_widget)

    def handle_logout(self):
        reply = QMessageBox.question(self, "Abmelden", "Möchten Sie sich wirklich abmelden?",
                                     QMessageBox.Yes | QMessageBox.No)

        if reply == QMessageBox.Yes:
            self.api_client.disconnect_websocket()
            self.close()

    def closeEvent(self, event):
        """Beim Schließen des Fensters aufräumen"""
        self.api_client.disconnect_websocket()
        event.accept()

    def open_admin_panel(self):
        from .admin_room_dialog import AdminRoomDialog
        dialog = AdminRoomDialog(self.api_client, self)

        if dialog.exec():
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
            self.load_rooms()
        except Exception as e:
            QMessageBox.critical(self, "Fehler", f"JSON konnte nicht geladen werden:\n{e}")