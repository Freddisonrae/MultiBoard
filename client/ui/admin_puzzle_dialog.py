from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, QSpinBox,
    QPushButton, QHBoxLayout, QMessageBox, QFileDialog, QTextEdit
)
from PySide6.QtCore import Qt
import json
import os

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, QSpinBox,
    QPushButton, QHBoxLayout, QMessageBox, QFileDialog, QTextEdit,
    QFrame, QGraphicsOpacityEffect
)
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve
import json
import os

# Farben
COLORS = {
    "bg_main": "#0F172A", "bg_card": "#1E293B",
    "primary": "#3B82F6", "primary_hover": "#2563EB",
    "text_primary": "#F8FAFC", "text_secondary": "#94A3B8", "text_muted": "#64748B",
    "border": "#334155", "accent": "#F59E0B", "success": "#22C55E"
}


class AdminPuzzleDialog(QDialog):
    """Admin-Dialog zum Erstellen oder Importieren von Rätseln"""

    def __init__(self, api_client, room_id, parent=None):
        super().__init__(parent)
        self.api_client = api_client
        self.room_id = room_id

        self.setWindowTitle("Rätsel hinzufügen")
        self.setFixedSize(480, 580)

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
        header.setFixedHeight(60)
        header.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 {COLORS['primary']}, 
                    stop:1 #8B5CF6
                );
            }}
        """)

        header_layout = QVBoxLayout()
        header_layout.setContentsMargins(0, 10, 0, 10)
        header_layout.setAlignment(Qt.AlignCenter)

        title = QLabel("🧩 Rätsel hinzufügen")
        title.setStyleSheet(f"""
            color: {COLORS['text_primary']};
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
        form_layout.setSpacing(6)
        form_layout.setContentsMargins(24, 16, 24, 16)

        # Input-Style
        input_style = f"""
            QLineEdit {{
                background-color: {COLORS['bg_main']};
                border: 2px solid {COLORS['border']};
                border-radius: 6px;
                padding: 8px 12px;
                color: {COLORS['text_primary']};
                font-size: 13px;
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
        """

        # ───────────────────────────────────────────────────────
        # Manuelles Erstellen
        # ───────────────────────────────────────────────────────
        manual_title = QLabel("📝 Manuell erstellen")
        manual_title.setStyleSheet(f"""
            color: {COLORS['text_primary']};
            font-size: 14px;
            font-weight: bold;
        """)
        form_layout.addWidget(manual_title)

        # Frage
        self.question_input = QLineEdit()
        self.question_input.setPlaceholderText("Frage eingeben...")
        self.question_input.setFixedHeight(36)
        self.question_input.setStyleSheet(input_style)
        form_layout.addWidget(self.question_input)

        # Antworten
        self.answer_inputs = []
        for i in range(4):
            input_field = QLineEdit()
            input_field.setPlaceholderText(f"Antwort {i + 1}")
            input_field.setFixedHeight(34)
            input_field.setStyleSheet(input_style)
            self.answer_inputs.append(input_field)
            form_layout.addWidget(input_field)

        # Richtige Antwort
        correct_layout = QHBoxLayout()
        correct_layout.setSpacing(10)
        correct_label = QLabel("Richtige Antwort:")
        correct_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 13px;")
        correct_layout.addWidget(correct_label)

        self.correct_input = QSpinBox()
        self.correct_input.setRange(1, 4)
        self.correct_input.setValue(1)
        self.correct_input.setFixedHeight(34)
        self.correct_input.setFixedWidth(70)
        self.correct_input.setStyleSheet(f"""
            QSpinBox {{
                background-color: {COLORS['bg_main']};
                border: 2px solid {COLORS['border']};
                border-radius: 6px;
                padding: 6px 10px;
                color: {COLORS['text_primary']};
                font-size: 13px;
            }}
            QSpinBox::up-button, QSpinBox::down-button {{
                width: 18px;
                background-color: {COLORS['bg_card']};
                border: none;
            }}
        """)
        correct_layout.addWidget(self.correct_input)
        correct_layout.addStretch()
        form_layout.addLayout(correct_layout)
        form_layout.addSpacing(4)

        # Speichern Button
        save_btn = QPushButton("💾 Manuell speichern")
        save_btn.setCursor(Qt.PointingHandCursor)
        save_btn.setFixedHeight(38)
        save_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['success']};
                color: {COLORS['text_primary']};
                font-size: 13px;
                font-weight: bold;
                border-radius: 8px;
                border: none;
            }}
            QPushButton:hover {{
                background-color: #16A34A;
            }}
        """)
        save_btn.clicked.connect(self.save_manual)
        form_layout.addWidget(save_btn)

        # ───────────────────────────────────────────────────────
        # Trennlinie
        # ───────────────────────────────────────────────────────
        separator = QFrame()
        separator.setFixedHeight(1)
        separator.setStyleSheet(f"background-color: {COLORS['border']};")
        form_layout.addSpacing(10)
        form_layout.addWidget(separator)
        form_layout.addSpacing(10)

        # ───────────────────────────────────────────────────────
        # H5P Import
        # ───────────────────────────────────────────────────────
        import_title = QLabel("📦 H5P-JSON importieren")
        import_title.setStyleSheet(f"""
            color: {COLORS['text_primary']};
            font-size: 14px;
            font-weight: bold;
        """)
        form_layout.addWidget(import_title)

        import_desc = QLabel("Multiple-Choice oder Single-Choice-Set Dateien")
        import_desc.setStyleSheet(f"color: {COLORS['text_muted']}; font-size: 12px;")
        form_layout.addWidget(import_desc)
        form_layout.addSpacing(4)

        import_btn = QPushButton("📂 JSON-Datei auswählen")
        import_btn.setCursor(Qt.PointingHandCursor)
        import_btn.setFixedHeight(38)
        import_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['primary']};
                color: {COLORS['text_primary']};
                font-size: 13px;
                font-weight: bold;
                border-radius: 8px;
                border: none;
            }}
            QPushButton:hover {{
                background-color: {COLORS['primary_hover']};
            }}
        """)
        import_btn.clicked.connect(self.import_h5p)
        form_layout.addWidget(import_btn)

        form_layout.addStretch()

        form_layout.addStretch()

        # Schließen Button
        close_btn = QPushButton("Schließen")
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.setFixedHeight(36)
        close_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {COLORS['text_muted']};
                font-size: 13px;
                border: none;
            }}
            QPushButton:hover {{
                color: {COLORS['text_primary']};
            }}
        """)
        close_btn.clicked.connect(self.accept)
        form_layout.addWidget(close_btn)

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

    def save_manual(self):
        """Manuell erstelltes Rätsel speichern"""
        question = self.question_input.text().strip()
        answers = [a.text().strip() for a in self.answer_inputs]
        correct = self.correct_input.value() - 1  # Index 0-3

        if not question or any(a == "" for a in answers):
            QMessageBox.warning(self, "Fehler", "Bitte Frage und alle 4 Antworten eingeben.")
            return

        self.save_puzzle(question, answers, correct)
        QMessageBox.information(self, "Erfolg ✓", "Rätsel erfolgreich gespeichert!")

        # Felder leeren für nächstes Rätsel
        self.question_input.clear()
        for a in self.answer_inputs:
            a.clear()
        self.correct_input.setValue(1)

    def import_h5p(self):
        """H5P-JSON importieren"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "H5P JSON auswählen", "", "JSON Dateien (*.json)"
        )

        if not file_path:
            return

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except:
            QMessageBox.critical(self, "Fehler", "Die Datei konnte nicht gelesen werden.")
            return

        # Format A – Multiple Choice (MCQ)
        if "choices" in data and "question" in data:
            self.import_mcq(data)
            QMessageBox.information(self, "Erfolg ✓", "MCQ H5P erfolgreich importiert!")
            return

        # Format B – Single Choice Set
        if "questions" in data:
            self.import_single_choice_set(data)
            QMessageBox.information(self, "Erfolg ✓", "Single Choice Set erfolgreich importiert!")
            return

        QMessageBox.critical(self, "Fehler", "Unbekanntes H5P Format.")

    def import_mcq(self, data):
        """H5P Multiple Choice (eine Frage)"""
        question = data["question"]
        options = [c["text"] for c in data["choices"]]
        correct = next(i for i, c in enumerate(data["choices"]) if c.get("correct"))
        self.save_puzzle(question, options, correct)

    def import_single_choice_set(self, data):
        """H5P Single Choice Set (mehrere Fragen)"""
        for q in data["questions"]:
            question = q["question"]
            options = q["answers"]
            correct = q["correctAnswer"]
            self.save_puzzle(question, options, correct)

    def save_puzzle(self, question, options, correct):
        """Puzzle in offline_puzzles speichern"""
        if not hasattr(self.api_client, "offline_puzzles"):
            self.api_client.offline_puzzles = {}

        if self.room_id not in self.api_client.offline_puzzles:
            self.api_client.offline_puzzles[self.room_id] = []

        new_id = len(self.api_client.offline_puzzles[self.room_id]) + 1

        puzzle = {
            "id": new_id,
            "title": question,
            "h5p_json": json.dumps({
                "question": question,
                "options": options,
                "correct": correct
            })
        }

        self.api_client.offline_puzzles[self.room_id].append(puzzle)