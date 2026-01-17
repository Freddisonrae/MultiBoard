# ═══════════════════════════════════════════════════════════════
# 🎨 FARBPALETTE
# ═══════════════════════════════════════════════════════════════

COLORS = {
    # Primärfarben (Blau)
    "primary": "#3B82F6",
    "primary_hover": "#2563EB",
    "primary_dark": "#1D4ED8",
    "primary_light": "#60A5FA",

    # Akzentfarben (Amber/Gold)
    "accent": "#F59E0B",
    "accent_hover": "#D97706",
    "accent_light": "#FCD34D",

    # Hintergründe (Dunkles Theme)
    "bg_main": "#0F172A",  # Haupthintergrund
    "bg_card": "#1E293B",  # Karten/Dialoge
    "bg_card_hover": "#334155",  # Karten hover
    "bg_input": "#334155",  # Eingabefelder
    "bg_header": "#1E293B",  # Header

    # Text
    "text_primary": "#F8FAFC",  # Haupttext (weiß)
    "text_secondary": "#94A3B8",  # Sekundärtext (grau)
    "text_muted": "#64748B",  # Gedämpfter Text
    "text_dark": "#0F172A",  # Dunkler Text (für helle Buttons)

    # Status
    "success": "#22C55E",
    "success_hover": "#16A34A",
    "warning": "#EAB308",
    "error": "#EF4444",
    "error_hover": "#DC2626",

    # Rahmen
    "border": "#334155",
    "border_hover": "#475569",
    "border_focus": "#3B82F6",
}

# ═══════════════════════════════════════════════════════════════
# 📝 SCHRIFTARTEN
# ═══════════════════════════════════════════════════════════════

FONTS = {
    "family": "Segoe UI, Inter, -apple-system, sans-serif",
    "size_xs": "11px",
    "size_sm": "13px",
    "size_base": "14px",
    "size_lg": "16px",
    "size_xl": "18px",
    "size_2xl": "22px",
    "size_3xl": "28px",
    "size_4xl": "36px",
}


# ═══════════════════════════════════════════════════════════════
# 🎯 WIEDERVERWENDBARE STYLES
# ═══════════════════════════════════════════════════════════════

def get_global_style():
    """Globaler Style für alle Fenster"""
    return f"""
        * {{
            font-family: {FONTS['family']};
        }}

        QMainWindow, QDialog {{
            background-color: {COLORS['bg_main']};
            color: {COLORS['text_primary']};
        }}

        QWidget {{
            color: {COLORS['text_primary']};
        }}

        QLabel {{
            color: {COLORS['text_primary']};
        }}

        QMessageBox {{
            background-color: {COLORS['bg_card']};
            color: {COLORS['text_primary']};
        }}

        QMessageBox QLabel {{
            color: {COLORS['text_primary']};
        }}

        QScrollArea {{
            border: none;
            background-color: transparent;
        }}

        QScrollBar:vertical {{
            background-color: {COLORS['bg_card']};
            width: 10px;
            border-radius: 5px;
            margin: 2px;
        }}

        QScrollBar::handle:vertical {{
            background-color: {COLORS['border_hover']};
            border-radius: 5px;
            min-height: 30px;
        }}

        QScrollBar::handle:vertical:hover {{
            background-color: {COLORS['primary']};
        }}

        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0px;
        }}
    """


def get_input_style():
    """Style für Eingabefelder"""
    return f"""
        QLineEdit, QTextEdit {{
            background-color: {COLORS['bg_input']};
            border: 2px solid {COLORS['border']};
            border-radius: 10px;
            padding: 12px 16px;
            color: {COLORS['text_primary']};
            font-size: {FONTS['size_base']};
            selection-background-color: {COLORS['primary']};
        }}

        QLineEdit:hover, QTextEdit:hover {{
            border-color: {COLORS['border_hover']};
        }}

        QLineEdit:focus, QTextEdit:focus {{
            border-color: {COLORS['primary']};
            background-color: {COLORS['bg_card']};
        }}

        QLineEdit::placeholder {{
            color: {COLORS['text_muted']};
        }}
    """


def get_primary_button_style():
    """Style für primäre Buttons"""
    return f"""
        QPushButton {{
            background-color: {COLORS['primary']};
            color: {COLORS['text_primary']};
            border: none;
            border-radius: 10px;
            padding: 14px 28px;
            font-size: {FONTS['size_base']};
            font-weight: 600;
            min-height: 20px;
        }}

        QPushButton:hover {{
            background-color: {COLORS['primary_hover']};
        }}

        QPushButton:pressed {{
            background-color: {COLORS['primary_dark']};
        }}

        QPushButton:disabled {{
            background-color: {COLORS['border']};
            color: {COLORS['text_muted']};
        }}
    """


def get_secondary_button_style():
    """Style für sekundäre Buttons"""
    return f"""
        QPushButton {{
            background-color: transparent;
            color: {COLORS['text_secondary']};
            border: 2px solid {COLORS['border']};
            border-radius: 10px;
            padding: 12px 24px;
            font-size: {FONTS['size_base']};
            font-weight: 500;
        }}

        QPushButton:hover {{
            border-color: {COLORS['primary']};
            color: {COLORS['primary']};
            background-color: rgba(59, 130, 246, 0.1);
        }}

        QPushButton:pressed {{
            background-color: rgba(59, 130, 246, 0.2);
        }}
    """


def get_success_button_style():
    """Style für Erfolgs-Buttons"""
    return f"""
        QPushButton {{
            background-color: {COLORS['success']};
            color: {COLORS['text_primary']};
            border: none;
            border-radius: 10px;
            padding: 12px 24px;
            font-size: {FONTS['size_base']};
            font-weight: 600;
        }}

        QPushButton:hover {{
            background-color: {COLORS['success_hover']};
        }}
    """


def get_danger_button_style():
    """Style für Gefahr-Buttons"""
    return f"""
        QPushButton {{
            background-color: {COLORS['error']};
            color: {COLORS['text_primary']};
            border: none;
            border-radius: 10px;
            padding: 12px 24px;
            font-size: {FONTS['size_base']};
            font-weight: 600;
        }}

        QPushButton:hover {{
            background-color: {COLORS['error_hover']};
        }}
    """


def get_ghost_button_style():
    """Style für transparente/Ghost Buttons"""
    return f"""
        QPushButton {{
            background-color: transparent;
            color: {COLORS['text_secondary']};
            border: none;
            padding: 8px 16px;
            font-size: {FONTS['size_sm']};
            text-decoration: underline;
        }}

        QPushButton:hover {{
            color: {COLORS['primary_light']};
        }}
    """


def get_card_style():
    """Style für Karten"""
    return f"""
        QWidget {{
            background-color: {COLORS['bg_card']};
            border: 1px solid {COLORS['border']};
            border-radius: 16px;
        }}
    """


def get_card_hover_style():
    """Style für Karten mit Hover-Effekt"""
    return f"""
        QWidget {{
            background-color: {COLORS['bg_card']};
            border: 2px solid {COLORS['border']};
            border-radius: 16px;
        }}

        QWidget:hover {{
            border-color: {COLORS['primary']};
            background-color: {COLORS['bg_card_hover']};
        }}
    """


def get_spinbox_style():
    """Style für SpinBox"""
    return f"""
        QSpinBox {{
            background-color: {COLORS['bg_input']};
            border: 2px solid {COLORS['border']};
            border-radius: 10px;
            padding: 12px 16px;
            color: {COLORS['text_primary']};
            font-size: {FONTS['size_base']};
        }}

        QSpinBox:hover {{
            border-color: {COLORS['border_hover']};
        }}

        QSpinBox:focus {{
            border-color: {COLORS['primary']};
        }}

        QSpinBox::up-button, QSpinBox::down-button {{
            background-color: {COLORS['bg_card']};
            border: none;
            width: 24px;
        }}

        QSpinBox::up-button:hover, QSpinBox::down-button:hover {{
            background-color: {COLORS['primary']};
        }}
    """


def get_combobox_style():
    """Style für ComboBox"""
    return f"""
        QComboBox {{
            background-color: {COLORS['bg_input']};
            border: 2px solid {COLORS['border']};
            border-radius: 10px;
            padding: 12px 16px;
            color: {COLORS['text_primary']};
            font-size: {FONTS['size_base']};
        }}

        QComboBox:hover {{
            border-color: {COLORS['border_hover']};
        }}

        QComboBox:focus {{
            border-color: {COLORS['primary']};
        }}

        QComboBox::drop-down {{
            border: none;
            width: 30px;
        }}

        QComboBox QAbstractItemView {{
            background-color: {COLORS['bg_card']};
            border: 2px solid {COLORS['border']};
            border-radius: 8px;
            color: {COLORS['text_primary']};
            selection-background-color: {COLORS['primary']};
        }}
    """


def get_checkbox_style():
    """Style für Checkboxen"""
    return f"""
        QCheckBox {{
            color: {COLORS['text_primary']};
            font-size: {FONTS['size_base']};
            spacing: 10px;
        }}

        QCheckBox::indicator {{
            width: 22px;
            height: 22px;
            border: 2px solid {COLORS['border']};
            border-radius: 6px;
            background-color: {COLORS['bg_input']};
        }}

        QCheckBox::indicator:hover {{
            border-color: {COLORS['primary']};
        }}

        QCheckBox::indicator:checked {{
            background-color: {COLORS['primary']};
            border-color: {COLORS['primary']};
        }}
    """


def get_radio_button_style():
    """Style für Radio Buttons"""
    return f"""
        QRadioButton {{
            color: {COLORS['text_primary']};
            font-size: {FONTS['size_lg']};
            padding: 16px 20px;
            background-color: {COLORS['bg_card']};
            border: 2px solid {COLORS['border']};
            border-radius: 12px;
            spacing: 12px;
        }}

        QRadioButton:hover {{
            background-color: {COLORS['bg_card_hover']};
            border-color: {COLORS['primary']};
        }}

        QRadioButton:checked {{
            background-color: rgba(59, 130, 246, 0.15);
            border-color: {COLORS['primary']};
        }}

        QRadioButton::indicator {{
            width: 22px;
            height: 22px;
            border: 2px solid {COLORS['border']};
            border-radius: 11px;
            background-color: {COLORS['bg_input']};
        }}

        QRadioButton::indicator:checked {{
            background-color: {COLORS['primary']};
            border-color: {COLORS['primary']};
        }}
    """


def get_progress_bar_style():
    """Style für Fortschrittsbalken"""
    return f"""
        QProgressBar {{
            background-color: {COLORS['bg_input']};
            border: none;
            border-radius: 8px;
            text-align: center;
            height: 16px;
            color: {COLORS['text_primary']};
            font-size: {FONTS['size_sm']};
            font-weight: 600;
        }}

        QProgressBar::chunk {{
            background: qlineargradient(
                x1:0, y1:0, x2:1, y2:0,
                stop:0 {COLORS['primary']}, 
                stop:1 {COLORS['accent']}
            );
            border-radius: 8px;
        }}
    """


def get_header_style():
    """Style für Header"""
    return f"""
        QWidget {{
            background-color: {COLORS['bg_header']};
            border-bottom: 1px solid {COLORS['border']};
        }}
    """


# ═══════════════════════════════════════════════════════════════
# 🎬 ANIMATION HELPERS (für QPropertyAnimation)
# ═══════════════════════════════════════════════════════════════

ANIMATION_DURATION_FAST = 150
ANIMATION_DURATION_NORMAL = 250
ANIMATION_DURATION_SLOW = 400
