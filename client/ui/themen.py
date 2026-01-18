

APP_QSS = """
/* ---------- Base ---------- */
QWidget {
    background: #F6F8FB;
    color: #0F172A;              /* dunkle Schrift */
    font-size: 14px;
}

QLabel {
    color: #0F172A;
}

QFrame#Card {
    background: #FFFFFF;
    border: 1px solid #E7ECF3;
    border-radius: 16px;
}

QFrame#HeaderBar {
    background: #FFFFFF;
    border-bottom: 1px solid #E7ECF3;
}

/* ---------- Inputs ---------- */
QLineEdit, QTextEdit, QPlainTextEdit, QSpinBox, QComboBox {
    background: #FFFFFF;
    color: #0F172A;
    border: 1px solid #D7DEE9;
    border-radius: 12px;
    padding: 10px 12px;
}

QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus, QSpinBox:focus, QComboBox:focus {
    border: 1px solid #2F6BFF;
}

QLineEdit::placeholder {
    color: #64748B;
}

/* ---------- Buttons ---------- */
QPushButton {
    background: #EEF2FF;
    color: #0F172A;
    border: 1px solid #D7DEE9;
    border-radius: 12px;
    padding: 10px 14px;
}

QPushButton:hover {
    background: #E6ECFF;
}

QPushButton:pressed {
    background: #DDE6FF;
}

QPushButton#PrimaryButton {
    background: #2F6BFF;
    color: #FFFFFF;
    border: none;
    border-radius: 12px;
    padding: 10px 14px;
}

QPushButton#PrimaryButton:hover {
    background: #245BFF;
}

QPushButton#DangerButton {
    background: #FEF2F2;
    color: #991B1B;
    border: 1px solid #FECACA;
}

/* ---------- Scroll ---------- */
QScrollArea {
    border: none;
    background: transparent;
}

QScrollBar:vertical {
    width: 10px;
    background: transparent;
    margin: 0px;
}
QScrollBar::handle:vertical {
    background: #D7DEE9;
    border-radius: 5px;
    min-height: 30px;
}
QScrollBar::handle:vertical:hover {
    background: #C7D0DD;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

/* ---------- Tabs / Group ---------- */
QTabWidget::pane {
    border: 1px solid #E7ECF3;
    border-radius: 14px;
    background: #FFFFFF;
}
QTabBar::tab {
    background: transparent;
    padding: 10px 14px;
    margin: 4px;
    border-radius: 12px;
    color: #334155;
}
QTabBar::tab:selected {
    background: #E9F0FF;
    color: #0F172A;
}

/* ---------- MessageBox ---------- */
QMessageBox QLabel {
    color: #0F172A;
    background: transparent;
}
"""