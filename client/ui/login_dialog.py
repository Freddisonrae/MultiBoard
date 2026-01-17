"""
Login-Dialog für Desktop-App
"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QMessageBox
)
from .register_dialog import RegisterDialog
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QMessageBox, QGraphicsOpacityEffect,
    QFrame
)
from PySide6.QtCore import Qt, Signal, QPropertyAnimation, QEasingCurve, QTimer
from PySide6.QtGui import QFont

# Import der gemeinsamen Styles
try:
    from .styles import (
        COLORS, FONTS, get_global_style, get_input_style,
        get_primary_button_style, get_ghost_button_style,
        ANIMATION_DURATION_NORMAL
    )
except ImportError:
    # Fallback falls styles.py nicht existiert
    COLORS = {
        "bg_main": "#0F172A", "bg_card": "#1E293B", "primary": "#3B82F6",
        "primary_hover": "#2563EB", "text_primary": "#F8FAFC",
        "text_secondary": "#94A3B8", "text_muted": "#64748B",
        "border": "#334155", "accent": "#F59E0B"
    }

# Import RegisterDialog
from .register_dialog import RegisterDialog


class LoginDialog(QDialog):
    """Login-Dialog mit modernem Design"""

    login_successful = Signal(object)

    def __init__(self, api_client, parent=None):
        super().__init__(parent)
        self.api_client = api_client
        self.init_ui()
        self.animate_entrance()

    def init_ui(self):
        """UI initialisieren"""
        self.setWindowTitle("MultiBoard - Anmeldung")
        self.setMinimumSize(450, 520)
        self.setMaximumSize(450, 520)

        # Globaler Style
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {COLORS['bg_main']};
            }}
        """)

        layout = QVBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        # ═══════════════════════════════════════════════════════
        # Header mit Gradient
        # ═══════════════════════════════════════════════════════
        header = QFrame()
        header.setFixedHeight(140)
        header.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 {COLORS['primary']}, 
                    stop:1 #8B5CF6
                );
                border-top-left-radius: 0px;
                border-top-right-radius: 0px;
            }}
        """)

        header_layout = QVBoxLayout()
        header_layout.setAlignment(Qt.AlignCenter)

        # Logo/Icon
        logo = QLabel("🎓")
        logo.setStyleSheet("font-size: 48px; background: transparent;")
        logo.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(logo)

        # Titel
        title = QLabel("MultiBoard")
        title.setStyleSheet(f"""
            color: {COLORS['text_primary']};
            font-size: 28px;
            font-weight: bold;
            background: transparent;
        """)
        title.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(title)

        header.setLayout(header_layout)
        layout.addWidget(header)

        # ═══════════════════════════════════════════════════════
        # Formular-Bereich
        # ═══════════════════════════════════════════════════════
        form_container = QFrame()
        form_container.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['bg_card']};
                border-bottom-left-radius: 0px;
                border-bottom-right-radius: 0px;
            }}
        """)

        form_layout = QVBoxLayout()
        form_layout.setSpacing(20)
        form_layout.setContentsMargins(40, 40, 40, 40)

        # Untertitel
        subtitle = QLabel("Willkommen zurück!")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet(f"""
            color: {COLORS['text_secondary']};
            font-size: 16px;
            margin-bottom: 10px;
        """)
        form_layout.addWidget(subtitle)

        # ═══════════════════════════════════════════════════════
        # Benutzername
        # ═══════════════════════════════════════════════════════
        username_label = QLabel("Benutzername")
        username_label.setStyleSheet(f"""
            color: {COLORS['text_secondary']};
            font-size: 13px;
            font-weight: 500;
            margin-bottom: 4px;
        """)
        form_layout.addWidget(username_label)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Gib deinen Benutzernamen ein")
        self.username_input.setMinimumHeight(50)
        self.username_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {COLORS['bg_main']};
                border: 2px solid {COLORS['border']};
                border-radius: 12px;
                padding: 14px 18px;
                color: {COLORS['text_primary']};
                font-size: 15px;
            }}
            QLineEdit:hover {{
                border-color: #475569;
            }}
            QLineEdit:focus {{
                border-color: {COLORS['primary']};
            }}
            QLineEdit::placeholder {{
                color: {COLORS['text_muted']};
            }}
        """)
        form_layout.addWidget(self.username_input)

        # ═══════════════════════════════════════════════════════
        # Passwort
        # ═══════════════════════════════════════════════════════
        password_label = QLabel("Passwort")
        password_label.setStyleSheet(f"""
            color: {COLORS['text_secondary']};
            font-size: 13px;
            font-weight: 500;
            margin-bottom: 4px;
        """)
        form_layout.addWidget(password_label)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Gib dein Passwort ein")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setMinimumHeight(50)
        self.password_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {COLORS['bg_main']};
                border: 2px solid {COLORS['border']};
                border-radius: 12px;
                padding: 14px 18px;
                color: {COLORS['text_primary']};
                font-size: 15px;
            }}
            QLineEdit:hover {{
                border-color: #475569;
            }}
            QLineEdit:focus {{
                border-color: {COLORS['primary']};
            }}
            QLineEdit::placeholder {{
                color: {COLORS['text_muted']};
            }}
        """)
        self.password_input.returnPressed.connect(self.handle_login)
        form_layout.addWidget(self.password_input)

        form_layout.addSpacing(10)

        # ═══════════════════════════════════════════════════════
        # Login-Button
        # ═══════════════════════════════════════════════════════
        self.login_btn = QPushButton("Anmelden")
        self.login_btn.setMinimumHeight(54)
        self.login_btn.setCursor(Qt.PointingHandCursor)
        self.login_btn.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 {COLORS['primary']}, 
                    stop:1 #8B5CF6
                );
                color: {COLORS['text_primary']};
                font-size: 16px;
                font-weight: bold;
                border-radius: 12px;
                border: none;
            }}
            QPushButton:hover {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 {COLORS['primary_hover']}, 
                    stop:1 #7C3AED
                );
            }}
            QPushButton:pressed {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #1D4ED8, 
                    stop:1 #6D28D9
                );
            }}
            QPushButton:disabled {{
                background-color: {COLORS['border']};
                color: {COLORS['text_muted']};
            }}
        """)
        self.login_btn.clicked.connect(self.handle_login)
        form_layout.addWidget(self.login_btn)

        # ═══════════════════════════════════════════════════════
        # Registrieren-Link
        # ═══════════════════════════════════════════════════════
        register_layout = QHBoxLayout()
        register_layout.setAlignment(Qt.AlignCenter)

        register_text = QLabel("Noch kein Konto?")
        register_text.setStyleSheet(f"color: {COLORS['text_muted']}; font-size: 14px;")
        register_layout.addWidget(register_text)

        self.register_btn = QPushButton("Registrieren")
        self.register_btn.setCursor(Qt.PointingHandCursor)
        self.register_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {COLORS['primary']};
                font-size: 14px;
                font-weight: 600;
                border: none;
                padding: 0px 4px;
            }}
            QPushButton:hover {{
                color: {COLORS['accent']};
                text-decoration: underline;
            }}
        """)
        self.register_btn.clicked.connect(self.open_register)
        register_layout.addWidget(self.register_btn)

        form_layout.addLayout(register_layout)
        form_layout.addStretch()

        form_container.setLayout(form_layout)
        layout.addWidget(form_container, stretch=1)

        self.setLayout(layout)

    def animate_entrance(self):
        """Einblend-Animation"""
        # Opacity-Animation für sanftes Einblenden
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)

        self.fade_animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_animation.setDuration(300)
        self.fade_animation.setStartValue(0.0)
        self.fade_animation.setEndValue(1.0)
        self.fade_animation.setEasingCurve(QEasingCurve.OutCubic)
        self.fade_animation.start()

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

        # Button deaktivieren mit Animation
        self.login_btn.setEnabled(False)
        self.login_btn.setText("⏳ Anmeldung läuft...")

        # Kurze Verzögerung für visuelles Feedback
        QTimer.singleShot(100, lambda: self._do_login(username, password))

    def _do_login(self, username, password):
        """Führt den eigentlichen Login durch"""
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
                "Benutzername oder Passwort falsch.\nBitte versuche es erneut."
            )

    def open_register(self):
        """Öffnet den Registrierungs-Dialog"""
        dialog = RegisterDialog(self.api_client, self)
        dialog.exec()