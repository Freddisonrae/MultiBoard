"""
Hauptfenster der Desktop-App
"""
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QScrollArea, QMessageBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from .game_widget import GameWidget

from PySide6.QtWidgets import QFileDialog
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QScrollArea, QMessageBox, QFrame,
    QGraphicsDropShadowEffect, QGraphicsOpacityEffect
)
from PySide6.QtCore import Qt, QTimer, Signal, QObject, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QFont, QColor
from .game_widget import GameWidget

# Farben
COLORS = {
    "bg_main": "#0F172A", "bg_card": "#1E293B", "bg_card_hover": "#334155",
    "primary": "#3B82F6", "primary_hover": "#2563EB",
    "text_primary": "#F8FAFC", "text_secondary": "#94A3B8", "text_muted": "#64748B",
    "border": "#334155", "accent": "#F59E0B", "success": "#22C55E", "error": "#EF4444"
}


class WebSocketSignalBridge(QObject):
    """Bridge zwischen WebSocket-Thread und Qt Main-Thread"""
    rooms_updated = Signal(list)


class MainWindow(QMainWindow):
    """Hauptfenster mit modernem Design"""

    def __init__(self, api_client):
        super().__init__()
        self.api_client = api_client
        self.current_session = None
        self.auto_refresh_enabled = True

        self.setWindowTitle("MultiBoard - School Puzzle Game")
        self.setMinimumSize(1100, 750)

        # Globaler Style
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {COLORS['bg_main']};
            }}
            QScrollArea {{
                border: none;
                background-color: transparent;
            }}
            QScrollBar:vertical {{
                background-color: {COLORS['bg_card']};
                width: 10px;
                border-radius: 5px;
            }}
            QScrollBar::handle:vertical {{
                background-color: {COLORS['border']};
                border-radius: 5px;
                min-height: 30px;
            }}
            QScrollBar::handle:vertical:hover {{
                background-color: {COLORS['primary']};
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
            QMessageBox {{
                background-color: {COLORS['bg_card']};
            }}
            QMessageBox QLabel {{
                color: {COLORS['text_primary']};
            }}
        """)

        # WebSocket Signal-Bridge
        self.ws_bridge = WebSocketSignalBridge()
        self.ws_bridge.rooms_updated.connect(self.on_rooms_updated_from_websocket)

        self.init_ui()
        self.load_rooms()
        self.connect_websocket()

        # Auto-Refresh Timer (Fallback)
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.auto_refresh)
        self.refresh_timer.start(30000)

    def connect_websocket(self):
        """WebSocket-Verbindung starten"""
        try:
            def on_ws_rooms_updated(rooms):
                self.ws_bridge.rooms_updated.emit(rooms)

            self.api_client.connect_websocket(on_ws_rooms_updated)
            print("✅ WebSocket-Verbindung wird aufgebaut...")
        except Exception as e:
            print(f"⚠️ WebSocket-Fehler: {e}")

    def on_rooms_updated_from_websocket(self, rooms):
        """WebSocket-Update empfangen"""
        print(f"🔄 WebSocket-Update: {len(rooms)} Räume")
        if hasattr(self, 'refresh_button'):
            original_text = self.refresh_button.text()
            self.refresh_button.setText("✨")
            QTimer.singleShot(500, lambda: self.refresh_button.setText(original_text))
        self.load_rooms()

    def auto_refresh(self):
        """Automatisches Aktualisieren"""
        if self.auto_refresh_enabled:
            self.load_rooms()

    def init_ui(self):
        """UI initialisieren"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout()
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # ═══════════════════════════════════════════════════════
        # HEADER
        # ═══════════════════════════════════════════════════════
        header = QFrame()
        header.setFixedHeight(80)
        header.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['bg_card']};
                border-bottom: 1px solid {COLORS['border']};
            }}
        """)

        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(30, 0, 30, 0)

        # Logo & Titel
        logo_layout = QHBoxLayout()
        logo_layout.setSpacing(12)

        logo = QLabel("🎓")
        logo.setStyleSheet("font-size: 32px;")
        logo_layout.addWidget(logo)

        title = QLabel("MultiBoard")
        title.setStyleSheet(f"""
            color: {COLORS['text_primary']};
            font-size: 24px;
            font-weight: bold;
        """)
        logo_layout.addWidget(title)

        header_layout.addLayout(logo_layout)
        header_layout.addStretch()

        # Benutzer-Info
        user_name = self.api_client.user.get("full_name") or self.api_client.user.get("username")
        user_container = QFrame()
        user_container.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['bg_main']};
                border-radius: 20px;
                padding: 4px 12px;
            }}
        """)
        user_layout = QHBoxLayout()
        user_layout.setContentsMargins(12, 6, 12, 6)
        user_layout.setSpacing(8)

        user_icon = QLabel("👤")
        user_icon.setStyleSheet("font-size: 16px;")
        user_layout.addWidget(user_icon)

        user_label = QLabel(user_name)
        user_label.setStyleSheet(f"""
            color: {COLORS['text_primary']};
            font-size: 14px;
            font-weight: 500;
        """)
        user_layout.addWidget(user_label)
        user_container.setLayout(user_layout)
        header_layout.addWidget(user_container)

        header_layout.addSpacing(16)

        # WebSocket-Status
        self.ws_status_label = QLabel("●")
        self.ws_status_label.setStyleSheet(f"color: {COLORS['text_muted']}; font-size: 20px;")
        self.ws_status_label.setToolTip("WebSocket: Verbindung wird aufgebaut...")
        header_layout.addWidget(self.ws_status_label)

        self.ws_status_timer = QTimer(self)
        self.ws_status_timer.timeout.connect(self.update_ws_status)
        self.ws_status_timer.start(2000)

        # Refresh-Button
        self.refresh_button = QPushButton("🔄")
        self.refresh_button.setCursor(Qt.PointingHandCursor)
        self.refresh_button.setFixedSize(44, 44)
        self.refresh_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['bg_main']};
                color: {COLORS['text_primary']};
                font-size: 18px;
                border-radius: 22px;
                border: 1px solid {COLORS['border']};
            }}
            QPushButton:hover {{
                background-color: {COLORS['primary']};
                border-color: {COLORS['primary']};
            }}
        """)
        self.refresh_button.clicked.connect(self.manual_refresh)
        self.refresh_button.setToolTip("Raumliste aktualisieren")
        header_layout.addWidget(self.refresh_button)

        # Admin-Button
        if self.api_client.user.get("username") == "admin" or self.api_client.user.get("is_admin"):
            admin_btn = QPushButton("⚙️ Admin")
            admin_btn.setCursor(Qt.PointingHandCursor)
            admin_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {COLORS['accent']};
                    color: {COLORS['bg_main']};
                    font-size: 14px;
                    font-weight: bold;
                    border-radius: 8px;
                    padding: 10px 20px;
                    border: none;
                }}
                QPushButton:hover {{
                    background-color: #D97706;
                }}
            """)
            admin_btn.clicked.connect(self.open_admin_panel)
            header_layout.addWidget(admin_btn)

        # Logout-Button
        logout_btn = QPushButton("Abmelden")
        logout_btn.setCursor(Qt.PointingHandCursor)
        logout_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {COLORS['text_secondary']};
                font-size: 14px;
                border: 2px solid {COLORS['border']};
                border-radius: 8px;
                padding: 10px 20px;
            }}
            QPushButton:hover {{
                border-color: {COLORS['error']};
                color: {COLORS['error']};
            }}
        """)
        logout_btn.clicked.connect(self.handle_logout)
        header_layout.addWidget(logout_btn)

        header.setLayout(header_layout)
        main_layout.addWidget(header)

        # ═══════════════════════════════════════════════════════
        # CONTENT
        # ═══════════════════════════════════════════════════════
        self.content_container = QWidget()
        self.content_container.setStyleSheet(f"background-color: {COLORS['bg_main']};")
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(40, 30, 40, 30)
        self.content_container.setLayout(content_layout)
        main_layout.addWidget(self.content_container)

        central_widget.setLayout(main_layout)

    def update_ws_status(self):
        """WebSocket-Status anzeigen"""
        if hasattr(self.api_client, '_ws_connected') and self.api_client._ws_connected:
            self.ws_status_label.setStyleSheet(f"color: {COLORS['success']}; font-size: 20px;")
            self.ws_status_label.setToolTip("WebSocket: Verbunden ✓")
        else:
            self.ws_status_label.setStyleSheet(f"color: {COLORS['error']}; font-size: 20px;")
            self.ws_status_label.setToolTip("WebSocket: Nicht verbunden")

    def manual_refresh(self):
        """Manuelles Aktualisieren"""
        self.refresh_button.setEnabled(False)
        self.refresh_button.setText("⏳")
        self.load_rooms()
        QTimer.singleShot(1000, lambda: (
            self.refresh_button.setEnabled(True),
            self.refresh_button.setText("🔄")
        ))

    def load_rooms(self):
        """Räume laden"""
        layout = self.content_container.layout()

        # UI leeren
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        # Titel-Bereich
        title_layout = QHBoxLayout()

        title = QLabel("🚪 Verfügbare Räume")
        title.setStyleSheet(f"""
            font-size: 28px;
            font-weight: bold;
            color: {COLORS['text_primary']};
        """)
        title_layout.addWidget(title)

        title_layout.addStretch()

        # JSON-Upload-Button
        load_btn = QPushButton("📄 Quiz-JSON laden")
        load_btn.setCursor(Qt.PointingHandCursor)
        load_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['bg_card']};
                color: {COLORS['text_secondary']};
                font-size: 14px;
                border: 2px solid {COLORS['border']};
                border-radius: 8px;
                padding: 10px 20px;
            }}
            QPushButton:hover {{
                border-color: {COLORS['primary']};
                color: {COLORS['primary']};
            }}
        """)
        load_btn.clicked.connect(self.load_quiz_json)
        title_layout.addWidget(load_btn)

        layout.addLayout(title_layout)
        layout.addSpacing(20)

        # Räume laden
        rooms = self.api_client.get_available_rooms()

        if not rooms:
            no_rooms_container = QFrame()
            no_rooms_container.setStyleSheet(f"""
                QFrame {{
                    background-color: {COLORS['bg_card']};
                    border: 2px dashed {COLORS['border']};
                    border-radius: 16px;
                    padding: 60px;
                }}
            """)
            no_rooms_layout = QVBoxLayout()
            no_rooms_layout.setAlignment(Qt.AlignCenter)

            icon = QLabel("📭")
            icon.setStyleSheet("font-size: 48px;")
            icon.setAlignment(Qt.AlignCenter)
            no_rooms_layout.addWidget(icon)

            text = QLabel("Keine Räume verfügbar")
            text.setStyleSheet(f"""
                font-size: 18px;
                font-weight: bold;
                color: {COLORS['text_primary']};
            """)
            text.setAlignment(Qt.AlignCenter)
            no_rooms_layout.addWidget(text)

            subtext = QLabel("Bitte wende dich an deinen Lehrer.")
            subtext.setStyleSheet(f"font-size: 14px; color: {COLORS['text_muted']};")
            subtext.setAlignment(Qt.AlignCenter)
            no_rooms_layout.addWidget(subtext)

            no_rooms_container.setLayout(no_rooms_layout)
            layout.addWidget(no_rooms_container)
            layout.addStretch()
            return

        # Scroll-Bereich
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        rooms_widget = QWidget()
        rooms_widget.setStyleSheet("background: transparent;")
        rooms_layout = QVBoxLayout()
        rooms_layout.setSpacing(16)

        for room in rooms:
            card = self.create_room_card(room)
            rooms_layout.addWidget(card)

        rooms_layout.addStretch()
        rooms_widget.setLayout(rooms_layout)
        scroll.setWidget(rooms_widget)
        layout.addWidget(scroll)

    def create_room_card(self, room):
        """Moderne Raumkarte erstellen"""
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['bg_card']};
                border: 2px solid {COLORS['border']};
                border-radius: 16px;
            }}
            QFrame:hover {{
                border-color: {COLORS['primary']};
                background-color: {COLORS['bg_card_hover']};
            }}
        """)

        # Schatten-Effekt
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setXOffset(0)
        shadow.setYOffset(4)
        shadow.setColor(QColor(0, 0, 0, 40))
        card.setGraphicsEffect(shadow)

        layout = QHBoxLayout()
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(20)

        # Info-Bereich
        info_layout = QVBoxLayout()
        info_layout.setSpacing(8)

        name_label = QLabel(room["name"])
        name_label.setStyleSheet(f"""
            font-size: 20px;
            font-weight: bold;
            color: {COLORS['text_primary']};
        """)
        info_layout.addWidget(name_label)

        if room.get("description"):
            desc_label = QLabel(room["description"])
            desc_label.setWordWrap(True)
            desc_label.setStyleSheet(f"""
                font-size: 14px;
                color: {COLORS['text_secondary']};
            """)
            info_layout.addWidget(desc_label)

        # Meta-Info
        meta_layout = QHBoxLayout()
        meta_layout.setSpacing(16)

        time_badge = QLabel(f"⏱️ {room['time_limit_minutes']} Min")
        time_badge.setStyleSheet(f"""
            background-color: {COLORS['bg_main']};
            color: {COLORS['accent']};
            font-size: 13px;
            font-weight: 500;
            padding: 6px 12px;
            border-radius: 6px;
        """)
        meta_layout.addWidget(time_badge)
        meta_layout.addStretch()

        info_layout.addLayout(meta_layout)
        layout.addLayout(info_layout, stretch=1)

        # Buttons
        button_layout = QVBoxLayout()
        button_layout.setSpacing(8)

        start_btn = QPushButton("▶️ Starten")
        start_btn.setCursor(Qt.PointingHandCursor)
        start_btn.setMinimumWidth(140)
        start_btn.setMinimumHeight(44)
        start_btn.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 {COLORS['primary']}, 
                    stop:1 #8B5CF6
                );
                color: {COLORS['text_primary']};
                font-size: 15px;
                font-weight: bold;
                border-radius: 10px;
                border: none;
            }}
            QPushButton:hover {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 {COLORS['primary_hover']}, 
                    stop:1 #7C3AED
                );
            }}
        """)
        start_btn.clicked.connect(lambda: self.start_room(room))
        button_layout.addWidget(start_btn)

        # Admin: Rätsel bearbeiten
        if self.api_client.user.get("username") == "admin" or self.api_client.user.get("is_admin"):
            edit_btn = QPushButton("✏️ Bearbeiten")
            edit_btn.setCursor(Qt.PointingHandCursor)
            edit_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: transparent;
                    color: {COLORS['text_secondary']};
                    font-size: 13px;
                    border: 1px solid {COLORS['border']};
                    border-radius: 8px;
                    padding: 8px 16px;
                }}
                QPushButton:hover {{
                    border-color: {COLORS['accent']};
                    color: {COLORS['accent']};
                }}
            """)
            edit_btn.clicked.connect(lambda _, r=room: self.open_puzzle_editor(r))
            button_layout.addWidget(edit_btn)

        layout.addLayout(button_layout)
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
        """Logout"""
        reply = QMessageBox.question(
            self, "Abmelden",
            "Möchtest du dich wirklich abmelden?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.api_client.disconnect_websocket()
            self.close()

    def closeEvent(self, event):
        """Aufräumen beim Schließen"""
        self.api_client.disconnect_websocket()
        event.accept()

    def open_admin_panel(self):
        """Admin-Panel öffnen"""
        from .admin_room_dialog import AdminRoomDialog
        dialog = AdminRoomDialog(self.api_client, self)
        if dialog.exec():
            self.load_rooms()

    def open_puzzle_editor(self, room):
        """Rätsel-Editor öffnen"""
        from .admin_puzzle_dialog import AdminPuzzleDialog
        dialog = AdminPuzzleDialog(self.api_client, room["id"], self)
        dialog.exec()

    def load_quiz_json(self):
        """Quiz-JSON laden"""
        path, _ = QFileDialog.getOpenFileName(
            self, "Quiz JSON auswählen", "", "JSON Dateien (*.json)"
        )
        if not path:
            return

        try:
            self.api_client.load_quiz_json_file(path)
            self.load_rooms()
        except Exception as e:
            QMessageBox.critical(self, "Fehler", f"Datei konnte nicht geladen werden:\n{e}")