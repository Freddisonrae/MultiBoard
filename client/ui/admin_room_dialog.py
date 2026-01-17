from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, QSpinBox,
    QPushButton, QHBoxLayout, QMessageBox, QComboBox, QFrame,
    QGraphicsOpacityEffect
)
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve

# Farben
COLORS = {
    "bg_main": "#0F172A", "bg_card": "#1E293B",
    "primary": "#3B82F6", "primary_hover": "#2563EB",
    "text_primary": "#F8FAFC", "text_secondary": "#94A3B8", "text_muted": "#64748B",
    "border": "#334155", "accent": "#F59E0B", "success": "#22C55E"
}


class AdminRoomDialog(QDialog):
    """Admin-Dialog zum Erstellen eines Raums"""

    def __init__(self, api_client, parent=None):
        super().__init__(parent)
        self.api_client = api_client

        self.setWindowTitle("Neuen Raum erstellen")
        self.setFixedSize(420, 500)

        self.init_ui()
        self.animate_entrance()

    def init_ui(self):
        """UI initialisieren"""
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {COLORS['bg_main']};
            }}
        """)

        layout = QVBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        # ═══════════════════════════════════════════════════════
        # Header
        # ═══════════════════════════════════════════════════════
        header = QFrame()
        header.setFixedHeight(70)
        header.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 {COLORS['accent']}, 
                    stop:1 #D97706
                );
            }}
        """)

        header_layout = QVBoxLayout()
        header_layout.setContentsMargins(0, 12, 0, 12)
        header_layout.setAlignment(Qt.AlignCenter)

        title = QLabel("🚪 Neuen Raum erstellen")
        title.setStyleSheet(f"""
            color: {COLORS['bg_main']};
            font-size: 18px;
            font-weight: bold;
            background: transparent;
        """)
        title.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(title)

        header.setLayout(header_layout)
        layout.addWidget(header)

        # ═══════════════════════════════════════════════════════
        # Formular
        # ═══════════════════════════════════════════════════════
        form_container = QFrame()
        form_container.setStyleSheet(f"QFrame {{ background-color: {COLORS['bg_card']}; }}")

        form_layout = QVBoxLayout()
        form_layout.setSpacing(8)
        form_layout.setContentsMargins(28, 20, 28, 20)

        # Input-Style
        input_style = f"""
            QLineEdit {{
                background-color: {COLORS['bg_main']};
                border: 2px solid {COLORS['border']};
                border-radius: 8px;
                padding: 10px 14px;
                color: {COLORS['text_primary']};
                font-size: 14px;
            }}
            QLineEdit:hover {{
                border-color: #475569;
            }}
            QLineEdit:focus {{
                border-color: {COLORS['accent']};
            }}
            QLineEdit::placeholder {{
                color: {COLORS['text_muted']};
            }}
        """

        # Raumname
        name_label = QLabel("Raumname")
        name_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 12px; font-weight: 500;")
        form_layout.addWidget(name_label)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("z.B. Mathe-Quiz Klasse 7a")
        self.name_input.setFixedHeight(40)
        self.name_input.setStyleSheet(input_style)
        form_layout.addWidget(self.name_input)
        form_layout.addSpacing(4)

        # Beschreibung
        desc_label = QLabel("Beschreibung (optional)")
        desc_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 12px; font-weight: 500;")
        form_layout.addWidget(desc_label)

        self.desc_input = QLineEdit()
        self.desc_input.setPlaceholderText("Kurze Beschreibung des Raums")
        self.desc_input.setFixedHeight(40)
        self.desc_input.setStyleSheet(input_style)
        form_layout.addWidget(self.desc_input)
        form_layout.addSpacing(4)

        # Zeitlimit
        time_label = QLabel("Zeitlimit")
        time_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 12px; font-weight: 500;")
        form_layout.addWidget(time_label)

        self.time_input = QSpinBox()
        self.time_input.setRange(1, 300)
        self.time_input.setValue(15)
        self.time_input.setSuffix(" Minuten")
        self.time_input.setFixedHeight(40)
        self.time_input.setStyleSheet(f"""
            QSpinBox {{
                background-color: {COLORS['bg_main']};
                border: 2px solid {COLORS['border']};
                border-radius: 8px;
                padding: 10px 14px;
                color: {COLORS['text_primary']};
                font-size: 14px;
            }}
            QSpinBox:hover {{
                border-color: #475569;
            }}
            QSpinBox:focus {{
                border-color: {COLORS['accent']};
            }}
            QSpinBox::up-button, QSpinBox::down-button {{
                width: 20px;
                background-color: {COLORS['bg_card']};
                border: none;
            }}
        """)
        form_layout.addWidget(self.time_input)
        form_layout.addSpacing(4)

        # Speichermodus
        mode_label = QLabel("Speichermodus")
        mode_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 12px; font-weight: 500;")
        form_layout.addWidget(mode_label)

        self.mode_select = QComboBox()
        self.mode_select.addItems(["Offline", "Online"])
        self.mode_select.setFixedHeight(40)
        self.mode_select.setStyleSheet(f"""
            QComboBox {{
                background-color: {COLORS['bg_main']};
                border: 2px solid {COLORS['border']};
                border-radius: 8px;
                padding: 10px 14px;
                color: {COLORS['text_primary']};
                font-size: 14px;
            }}
            QComboBox:hover {{
                border-color: #475569;
            }}
            QComboBox::drop-down {{
                border: none;
                width: 24px;
            }}
            QComboBox QAbstractItemView {{
                background-color: {COLORS['bg_card']};
                border: 2px solid {COLORS['border']};
                border-radius: 6px;
                color: {COLORS['text_primary']};
                selection-background-color: {COLORS['accent']};
            }}
        """)
        form_layout.addWidget(self.mode_select)

        form_layout.addSpacing(16)

        # ═══════════════════════════════════════════════════════
        # Buttons
        # ═══════════════════════════════════════════════════════
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)

        cancel_btn = QPushButton("Abbrechen")
        cancel_btn.setCursor(Qt.PointingHandCursor)
        cancel_btn.setFixedHeight(42)
        cancel_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {COLORS['text_secondary']};
                font-size: 14px;
                border: 2px solid {COLORS['border']};
                border-radius: 8px;
                padding: 10px 20px;
            }}
            QPushButton:hover {{
                border-color: {COLORS['text_secondary']};
                color: {COLORS['text_primary']};
            }}
        """)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        save_btn = QPushButton("✓ Raum erstellen")
        save_btn.setCursor(Qt.PointingHandCursor)
        save_btn.setFixedHeight(42)
        save_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['accent']};
                color: {COLORS['bg_main']};
                font-size: 14px;
                font-weight: bold;
                border-radius: 8px;
                border: none;
                padding: 10px 20px;
            }}
            QPushButton:hover {{
                background-color: #D97706;
            }}
        """)
        save_btn.clicked.connect(self.handle_create)
        btn_layout.addWidget(save_btn)

        form_layout.addLayout(btn_layout)

        form_container.setLayout(form_layout)
        layout.addWidget(form_container, stretch=1)

        self.setLayout(layout)

    def animate_entrance(self):
        """Einblend-Animation"""
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)

        self.fade_animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_animation.setDuration(200)
        self.fade_animation.setStartValue(0.0)
        self.fade_animation.setEndValue(1.0)
        self.fade_animation.setEasingCurve(QEasingCurve.OutCubic)
        self.fade_animation.start()

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

        # OFFLINE SPEICHERN
        if mode == "Offline":
            if not hasattr(self.api_client, "offline_rooms"):
                self.api_client.offline_rooms = []

            room_data["id"] = len(self.api_client.offline_rooms) + 1000
            self.api_client.offline_rooms.append(room_data)

            QMessageBox.information(self, "Erfolg ✓", f"Raum '{name}' wurde offline erstellt.")
            self.accept()
            return

        # ONLINE SPEICHERN
        if mode == "Online":
            result = self.api_client.start_session(room_data)
            if result:
                QMessageBox.information(self, "Erfolg ✓", f"Raum '{name}' wurde online gespeichert.")
                self.accept()
            else:
                QMessageBox.critical(self, "Fehler", "Raum konnte nicht online gespeichert werden.")

