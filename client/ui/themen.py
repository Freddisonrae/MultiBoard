"""
Modernes, eckiges Theme für die Desktop-App
Passend zum Admin-Panel Design
"""

APP_QSS = """
/* ========== CSS Variables via Palette ========== */
/* Farben: Indigo-basiertes modernes Theme */

/* ========== Global Reset ========== */
* {
    font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, system-ui, sans-serif;
    font-size: 14px;
}

/* ========== Base Widgets ========== */
QWidget {
    background: #F9FAFB;
    color: #111827;
}

QLabel {
    color: #111827;
    background: transparent;
}

QLabel#Title {
    font-size: 20px;
    font-weight: 700;
    color: #111827;
    padding: 8px 0;
}

QLabel#Subtitle {
    font-size: 16px;
    font-weight: 600;
    color: #374151;
    padding: 4px 0;
}

QLabel#Muted {
    color: #6B7280;
    font-size: 13px;
}

/* ========== Frames & Cards ========== */
QFrame {
    background: #FFFFFF;
    border: 1px solid #E5E7EB;
    border-radius: 4px;
}

QFrame#Card {
    background: #FFFFFF;
    border: 1px solid #E5E7EB;
    border-radius: 8px;
    padding: 16px;
}

QFrame#HeaderBar {
    background: #FFFFFF;
    border: none;
    border-bottom: 1px solid #E5E7EB;
    border-radius: 0px;
    padding: 16px 24px;
}

/* ========== Input Fields ========== */
QLineEdit, QTextEdit, QPlainTextEdit {
    background: #FFFFFF;
    color: #111827;
    border: 1px solid #D1D5DB;
    border-radius: 4px;
    padding: 10px 12px;
    selection-background-color: #6366F1;
    selection-color: #FFFFFF;
}

QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {
    border: 1px solid #4F46E5;
    background: #FFFFFF;
}

QLineEdit:hover, QTextEdit:hover, QPlainTextEdit:hover {
    border-color: #9CA3AF;
}

QLineEdit::placeholder {
    color: #9CA3AF;
}

/* ========== Spin Boxes & Combo Boxes ========== */
QSpinBox, QComboBox {
    background: #FFFFFF;
    color: #111827;
    border: 1px solid #D1D5DB;
    border-radius: 4px;
    padding: 10px 12px;
}

QSpinBox:focus, QComboBox:focus {
    border: 1px solid #4F46E5;
}

QSpinBox:hover, QComboBox:hover {
    border-color: #9CA3AF;
}

QSpinBox::up-button, QSpinBox::down-button {
    background: transparent;
    border: none;
    width: 20px;
}

QSpinBox::up-button:hover, QSpinBox::down-button:hover {
    background: #F3F4F6;
}

QComboBox::drop-down {
    border: none;
    width: 30px;
}

QComboBox::down-arrow {
    image: none;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 6px solid #6B7280;
    margin-right: 8px;
}

QComboBox QAbstractItemView {
    background: #FFFFFF;
    border: 1px solid #E5E7EB;
    border-radius: 4px;
    selection-background-color: #EEF2FF;
    selection-color: #111827;
    padding: 4px;
}

/* ========== Buttons ========== */
QPushButton {
    background: #FFFFFF;
    color: #111827;
    border: 1px solid #D1D5DB;
    border-radius: 4px;
    padding: 10px 20px;
    font-weight: 600;
    font-size: 14px;
}

QPushButton:hover {
    background: #F9FAFB;
    border-color: #9CA3AF;
}

QPushButton:pressed {
    background: #F3F4F6;
}

QPushButton:disabled {
    background: #F3F4F6;
    color: #9CA3AF;
    border-color: #E5E7EB;
}

/* Primary Button */
QPushButton#PrimaryButton {
    background: #4F46E5;
    color: #FFFFFF;
    border: none;
}

QPushButton#PrimaryButton:hover {
    background: #4338CA;
}

QPushButton#PrimaryButton:pressed {
    background: #3730A3;
}

QPushButton#PrimaryButton:disabled {
    background: #D1D5DB;
    color: #9CA3AF;
}

/* Success Button */
QPushButton#SuccessButton {
    background: #10B981;
    color: #FFFFFF;
    border: none;
}

QPushButton#SuccessButton:hover {
    background: #059669;
}

QPushButton#SuccessButton:pressed {
    background: #047857;
}

/* Danger Button */
QPushButton#DangerButton {
    background: #EF4444;
    color: #FFFFFF;
    border: none;
}

QPushButton#DangerButton:hover {
    background: #DC2626;
}

QPushButton#DangerButton:pressed {
    background: #B91C1C;
}

/* Ghost Button (transparent) */
QPushButton#GhostBtn {
    background: transparent;
    color: #4F46E5;
    border: 1px solid #4F46E5;
}

QPushButton#GhostBtn:hover {
    background: #EEF2FF;
}

QPushButton#GhostBtn:pressed {
    background: #E0E7FF;
}

/* ========== Scroll Areas ========== */
QScrollArea {
    border: none;
    background: transparent;
}

QScrollBar:vertical {
    width: 10px;
    background: #F3F4F6;
    margin: 0px;
    border-radius: 5px;
}

QScrollBar::handle:vertical {
    background: #D1D5DB;
    border-radius: 5px;
    min-height: 30px;
}

QScrollBar::handle:vertical:hover {
    background: #9CA3AF;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar:horizontal {
    height: 10px;
    background: #F3F4F6;
    margin: 0px;
    border-radius: 5px;
}

QScrollBar::handle:horizontal {
    background: #D1D5DB;
    border-radius: 5px;
    min-width: 30px;
}

QScrollBar::handle:horizontal:hover {
    background: #9CA3AF;
}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0px;
}

/* ========== Lists & Tables ========== */
QListWidget, QTableWidget, QTreeWidget {
    background: #FFFFFF;
    color: #111827;
    border: 1px solid #E5E7EB;
    border-radius: 8px;
    selection-background-color: #EEF2FF;
    selection-color: #111827;
    outline: none;
}

QListWidget::item, QTableWidget::item, QTreeWidget::item {
    padding: 8px;
    border-bottom: 1px solid #F3F4F6;
}

QListWidget::item:hover, QTableWidget::item:hover, QTreeWidget::item:hover {
    background: #F9FAFB;
}

QListWidget::item:selected, QTableWidget::item:selected, QTreeWidget::item:selected {
    background: #EEF2FF;
    color: #111827;
    border-left: 3px solid #4F46E5;
}

QHeaderView::section {
    background: #F9FAFB;
    color: #374151;
    padding: 8px 12px;
    border: none;
    border-bottom: 1px solid #E5E7EB;
    font-weight: 600;
}

/* ========== Tabs ========== */
QTabWidget::pane {
    border: 1px solid #E5E7EB;
    border-radius: 8px;
    background: #FFFFFF;
    top: -1px;
}

QTabBar {
    background: transparent;
}

QTabBar::tab {
    background: transparent;
    color: #6B7280;
    padding: 10px 20px;
    margin: 0px 4px;
    border-radius: 4px;
    font-weight: 600;
}

QTabBar::tab:hover {
    background: #F3F4F6;
    color: #111827;
}

QTabBar::tab:selected {
    background: #4F46E5;
    color: #FFFFFF;
}

/* ========== Group Boxes ========== */
QGroupBox {
    background: #FFFFFF;
    border: 1px solid #E5E7EB;
    border-radius: 8px;
    margin-top: 12px;
    padding: 16px;
    font-weight: 600;
    color: #111827;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 4px 8px;
    background: #FFFFFF;
    color: #4F46E5;
}

/* ========== Progress Bars ========== */
QProgressBar {
    border: 1px solid #E5E7EB;
    border-radius: 4px;
    text-align: center;
    background: #F3F4F6;
    color: #111827;
    font-weight: 600;
    height: 24px;
}

QProgressBar::chunk {
    background: #4F46E5;
    border-radius: 3px;
}

/* ========== Check Boxes & Radio Buttons ========== */
QCheckBox, QRadioButton {
    color: #111827;
    spacing: 8px;
}

QCheckBox:hover, QRadioButton:hover {
    color: #4F46E5;
}

QCheckBox::indicator, QRadioButton::indicator {
    width: 18px;
    height: 18px;
    border: 2px solid #D1D5DB;
    background: #FFFFFF;
}

QCheckBox::indicator {
    border-radius: 4px;
}

QRadioButton::indicator {
    border-radius: 9px;
}

QCheckBox::indicator:hover, QRadioButton::indicator:hover {
    border-color: #4F46E5;
}

QCheckBox::indicator:checked, QRadioButton::indicator:checked {
    background: #4F46E5;
    border-color: #4F46E5;
}

QCheckBox::indicator:checked {
    image: none;
}

/* ========== Sliders ========== */
QSlider::groove:horizontal {
    height: 6px;
    background: #E5E7EB;
    border-radius: 3px;
}

QSlider::handle:horizontal {
    background: #4F46E5;
    width: 18px;
    height: 18px;
    margin: -6px 0;
    border-radius: 9px;
}

QSlider::handle:horizontal:hover {
    background: #4338CA;
}

/* ========== Message Boxes ========== */
QMessageBox {
    background: #FFFFFF;
}

QMessageBox QLabel {
    color: #111827;
    background: transparent;
    min-width: 300px;
    font-size: 14px;
}

QMessageBox QPushButton {
    min-width: 80px;
    padding: 8px 16px;
}

/* ========== Dialogs ========== */
QDialog {
    background: #F9FAFB;
}

/* ========== Status Bar ========== */
QStatusBar {
    background: #FFFFFF;
    color: #6B7280;
    border-top: 1px solid #E5E7EB;
}

/* ========== Menu Bar ========== */
QMenuBar {
    background: #FFFFFF;
    color: #111827;
    border-bottom: 1px solid #E5E7EB;
    padding: 4px;
}

QMenuBar::item {
    background: transparent;
    padding: 6px 12px;
    border-radius: 4px;
}

QMenuBar::item:selected {
    background: #F3F4F6;
}

QMenuBar::item:pressed {
    background: #E5E7EB;
}

QMenu {
    background: #FFFFFF;
    border: 1px solid #E5E7EB;
    border-radius: 8px;
    padding: 4px;
}

QMenu::item {
    padding: 8px 24px 8px 12px;
    border-radius: 4px;
}

QMenu::item:selected {
    background: #F3F4F6;
}

/* ========== Tool Tips ========== */
QToolTip {
    background: #1F2937;
    color: #FFFFFF;
    border: none;
    border-radius: 4px;
    padding: 6px 10px;
    font-size: 12px;
}

/* ========== Specific App Components ========== */

/* Login Dialog - Einfarbig grau */
QDialog#LoginDialog {
    background: #F9FAFB;
}

/* Main Window Header - Schöner Indigo-Header wie Admin-Panel! */
QWidget#HeaderWidget {
    background: #4F46E5;
    border: none;
    border-bottom: 1px solid #4338CA;
}

QWidget#HeaderWidget QLabel {
    color: #FFFFFF;
    background: transparent;
}

QWidget#HeaderWidget QPushButton {
    background: rgba(255, 255, 255, 0.15);
    color: #FFFFFF;
    border: 1px solid rgba(255, 255, 255, 0.2);
}

QWidget#HeaderWidget QPushButton:hover {
    background: rgba(255, 255, 255, 0.25);
}

QWidget#HeaderWidget QPushButton:pressed {
    background: rgba(255, 255, 255, 0.1);
}

/* Room Card Hover Effect */
QFrame#RoomCard:hover {
    border: 1px solid #4F46E5;
}

/* Game Widget */
QWidget#GameWidget {
    background: #FFFFFF;
    border-radius: 8px;
}

/* Score Label */
QLabel#ScoreLabel {
    color: #10B981;
    font-weight: 700;
    font-size: 16px;
}

/* Timer Label */
QLabel#TimerLabel {
    color: #EF4444;
    font-weight: 700;
    font-size: 16px;
}

/* Progress Label */
QLabel#ProgressLabel {
    color: #4F46E5;
    font-weight: 700;
    font-size: 16px;
}

/* Question Label */
QLabel#QuestionLabel {
    background: #F9FAFB;
    border: 2px solid #4F46E5;
    border-radius: 8px;
    padding: 20px;
    font-size: 16px;
    font-weight: 600;
    color: #111827;
}

/* Answer Buttons */
QRadioButton#AnswerButton {
    background: #FFFFFF;
    border: 2px solid #E5E7EB;
    border-radius: 4px;
    padding: 16px;
    font-size: 15px;
    margin: 4px 0;
}

QRadioButton#AnswerButton:hover {
    background: #F9FAFB;
    border-color: #4F46E5;
}

QRadioButton#AnswerButton:checked {
    background: #EEF2FF;
    border-color: #4F46E5;
    font-weight: 600;
}

QRadioButton#AnswerButton::indicator {
    width: 20px;
    height: 20px;
}
"""