from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, QSpinBox,
    QPushButton, QHBoxLayout, QMessageBox, QFileDialog, QTextEdit
)
from PySide6.QtCore import Qt
import json
import os


class AdminPuzzleDialog(QDialog):
    """Admin-Dialog zum Erstellen oder Importieren von H5P-Rätseln"""

    def __init__(self, api_client, room_id, parent=None):
        super().__init__(parent)
        self.api_client = api_client
        self.room_id = room_id

        self.setWindowTitle("Rätsel hinzufügen (H5P / Manuell)")
        self.setMinimumSize(500, 550)

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(12)

        # Titel
        title = QLabel("Manuell ein Rätsel erstellen")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title)

        # Frage
        self.question_input = QLineEdit()
        self.question_input.setPlaceholderText("Frage eingeben…")
        layout.addWidget(self.question_input)

        # Antworten (4 Felder)
        self.answer_inputs = []
        for i in range(4):
            input_field = QLineEdit()
            input_field.setPlaceholderText(f"Antwort {i + 1}")
            self.answer_inputs.append(input_field)
            layout.addWidget(input_field)

        # Richtige Antwort
        self.correct_input = QSpinBox()
        self.correct_input.setRange(0, 3)
        self.correct_input.setPrefix("Richtige Antwort: Index ")
        layout.addWidget(self.correct_input)

        # Speichern Button
        save_btn = QPushButton("Manuell speichern")
        save_btn.clicked.connect(self.save_manual)
        layout.addWidget(save_btn)

        layout.addSpacing(20)

        # Import Bereich
        import_title = QLabel("H5P-JSON importieren")
        import_title.setStyleSheet("font-size: 18px; font-weight: bold; margin-top: 15px;")
        layout.addWidget(import_title)

        import_btn = QPushButton("JSON Datei importieren")
        import_btn.clicked.connect(self.import_h5p)
        layout.addWidget(import_btn)

        self.setLayout(layout)


    # 1. MANUELLES ERSTELLEN

    def save_manual(self):
        question = self.question_input.text().strip()
        answers = [a.text().strip() for a in self.answer_inputs]
        correct = self.correct_input.value()

        if not question or any(a == "" for a in answers):
            QMessageBox.warning(self, "Fehler", "Bitte Frage und alle 4 Antworten eingeben.")
            return

        self.save_puzzle(question, answers, correct)
        QMessageBox.information(self, "Gespeichert", "Rätsel manuell gespeichert!")
        self.accept()


    # 2. H5P IMPORT

    def import_h5p(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "H5P JSON auswählen", "", "JSON Dateien (*.json)")

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
            QMessageBox.information(self, "Import erfolgreich", "MCQ H5P erfolgreich importiert!")
            self.accept()
            return

        # Format B – Single Choice Set
        if "questions" in data:
            self.import_single_choice_set(data)
            QMessageBox.information(self, "Import erfolgreich", "Single Choice Set erfolgreich importiert!")
            self.accept()
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

    # --------------------------------------------------
    # 3. SPEICHERN IM OFFLINE PUZZLE-SYSTEM
    # --------------------------------------------------
    def save_puzzle(self, question, options, correct):
        """Speichert ein Puzzle in den offline_puzzles"""

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