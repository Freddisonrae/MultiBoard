from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox, QCheckBox
)
from PySide6.QtCore import Qt

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox, QCheckBox, QFrame, QGraphicsOpacityEffect
)
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve

# Fallback-Farben falls styles.py nicht existiert
COLORS = {
    "bg_main": "#0F172A", "bg_card": "#1E293B", "primary": "#3B82F6",
    "primary_hover": "#2563EB", "text_primary": "#F8FAFC",
    "text_secondary": "#94A3B8", "text_muted": "#64748B",
    "border": "#334155", "accent": "#F59E0B", "success": "#22C55E"
}


class RegisterDialog(QDialog):
    """Registrierungs-Dialog mit modernem Design"""

    def __init__(self, api_client, parent=None):
        super().__init__(parent)
        self.api_client = api_client
        self.setWindowTitle("MultiBoard - Registrieren")
        self.setFixedSize(400, 520)

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
        header.setFixedHeight(80)
        header.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 {COLORS['success']}, 
                    stop:1 #10B981
                );
            }}
        """)

        header_layout = QVBoxLayout()
        header_layout.setContentsMargins(0, 16, 0, 16)
        header_layout.setAlignment(Qt.AlignCenter)

        title = QLabel("✨ Account erstellen")
        title.setStyleSheet(f"""
            color: {COLORS['text_primary']};
            font-size: 20px;
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
        form_container.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['bg_card']};
            }}
        """)

        form_layout = QVBoxLayout()
        form_layout.setSpacing(10)
        form_layout.setContentsMargins(32, 20, 32, 20)

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
                border-color: {COLORS['success']};
            }}
            QLineEdit::placeholder {{
                color: {COLORS['text_muted']};
            }}
        """

        # Benutzername
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("👤 Benutzername")
        self.username_input.setFixedHeight(42)
        self.username_input.setStyleSheet(input_style)
        form_layout.addWidget(self.username_input)

        # Passwort
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("🔒 Passwort")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setFixedHeight(42)
        self.password_input.setStyleSheet(input_style)
        form_layout.addWidget(self.password_input)

        # Passwort bestätigen
        self.password_confirm_input = QLineEdit()
        self.password_confirm_input.setPlaceholderText("🔒 Passwort bestätigen")
        self.password_confirm_input.setEchoMode(QLineEdit.Password)
        self.password_confirm_input.setFixedHeight(42)
        self.password_confirm_input.setStyleSheet(input_style)
        form_layout.addWidget(self.password_confirm_input)

        # Admin-Checkbox
        self.admin_checkbox = QCheckBox("Als Administrator registrieren")
        self.admin_checkbox.setStyleSheet(f"""
            QCheckBox {{
                color: {COLORS['text_secondary']};
                font-size: 13px;
                spacing: 8px;
                padding: 4px 0;
            }}
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
                border: 2px solid {COLORS['border']};
                border-radius: 5px;
                background-color: {COLORS['bg_main']};
            }}
            QCheckBox::indicator:checked {{
                background-color: {COLORS['success']};
                border-color: {COLORS['success']};
            }}
        """)
        form_layout.addWidget(self.admin_checkbox)

        form_layout.addSpacing(12)

        # Registrieren-Button
        self.register_btn = QPushButton("Account erstellen")
        self.register_btn.setFixedHeight(44)
        self.register_btn.setCursor(Qt.PointingHandCursor)
        self.register_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['success']};
                color: {COLORS['text_primary']};
                font-size: 14px;
                font-weight: bold;
                border-radius: 8px;
                border: none;
            }}
            QPushButton:hover {{
                background-color: #16A34A;
            }}
            QPushButton:pressed {{
                background-color: #15803D;
            }}
        """)
        self.register_btn.clicked.connect(self.handle_register)
        form_layout.addWidget(self.register_btn)

        # Abbrechen-Button
        cancel_btn = QPushButton("Zurück zum Login")
        cancel_btn.setCursor(Qt.PointingHandCursor)
        cancel_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {COLORS['text_muted']};
                font-size: 14px;
                border: none;
                padding: 10px;
            }}
            QPushButton:hover {{
                color: {COLORS['text_primary']};
            }}
        """)
        cancel_btn.clicked.connect(self.reject)
        form_layout.addWidget(cancel_btn)

        form_layout.addStretch()
        form_container.setLayout(form_layout)
        layout.addWidget(form_container, stretch=1)

        self.setLayout(layout)

    def animate_entrance(self):
        """Einblend-Animation"""
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)

        self.fade_animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_animation.setDuration(250)
        self.fade_animation.setStartValue(0.0)
        self.fade_animation.setEndValue(1.0)
        self.fade_animation.setEasingCurve(QEasingCurve.OutCubic)
        self.fade_animation.start()

    def handle_register(self):
        """Registrierung durchführen"""
        username = self.username_input.text().strip()
        pw = self.password_input.text()
        pw2 = self.password_confirm_input.text()
        is_admin = self.admin_checkbox.isChecked()

        if not username or not pw:
            QMessageBox.warning(self, "Fehler", "Bitte Benutzername und Passwort eingeben.")
            return

        if pw != pw2:
            QMessageBox.warning(self, "Fehler", "Die Passwörter stimmen nicht überein.")
            return

        ok = self.api_client.register(username=username, password=pw, is_admin=is_admin)

        if ok:
            QMessageBox.information(
                self,
                "Erfolg ✓",
                "Account erfolgreich erstellt!\nDu kannst dich jetzt anmelden."
            )
            self.accept()
        else:
            QMessageBox.critical(
                self,
                "Fehler",
                "Registrierung fehlgeschlagen.\nBitte versuche es erneut."
            )