"""
Game-Widget - Zeigt Rätsel an und verarbeitet Antworten
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QRadioButton, QButtonGroup, QProgressBar, QMessageBox
)
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QFont
import json
import time


class GameWidget(QWidget):
    """Widget für Rätsel-Anzeige"""

    puzzle_completed = Signal(dict)  # Sendet Ergebnis
    session_completed = Signal()

    def __init__(self, api_client, session, puzzles, parent=None):
        super().__init__(parent)
        self.api_client = api_client
        self.session = session
        self.puzzles = puzzles
        self.current_puzzle_index = 0
        self.start_time = 0
        self.score = 0

        self.init_ui()
        self.load_puzzle(0)

    def init_ui(self):
        """UI initialisieren"""
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)

        # Header mit Fortschritt
        header_layout = QHBoxLayout()

        self.progress_label = QLabel()
        self.progress_label.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            color: #4F46E5;
        """)
        header_layout.addWidget(self.progress_label)

        header_layout.addStretch()

        self.score_label = QLabel("Punkte: 0")
        self.score_label.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            color: #10B981;
        """)
        header_layout.addWidget(self.score_label)

        self.timer_label = QLabel("Zeit: 0s")
        self.timer_label.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            color: #EF4444;
        """)
        header_layout.addWidget(self.timer_label)

        layout.addLayout(header_layout)

        # Fortschrittsbalken
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                text-align: center;
                height: 25px;
            }
            QProgressBar::chunk {
                background: #4F46E5;
            }
        """)
        layout.addWidget(self.progress_bar)

        layout.addSpacing(20)

        # Frage
        self.question_label = QLabel()
        self.question_label.setWordWrap(True)
        self.question_label.setStyleSheet("""
            QLabel {
                background-color: #f5f5f5;
                border: 2px solid #4F46E5;
                border-radius: 10px;
                padding: 18px;
                font-size: 18px;
                font-weight: bold;
                min-height: 50px;
            }
        """)
        layout.addWidget(self.question_label)

        layout.addSpacing(20)

        # Antwort-Optionen
        self.answer_group = QButtonGroup(self)
        self.answer_buttons = []

        for i in range(4):
            btn = QRadioButton()
            btn.setStyleSheet("""
                QRadioButton {
                    font-size: 16px;
                    padding: 15px;
                    background-color: white;
                    border: 2px solid #e0e0e0;
                    border-radius: 8px;
                }
                QRadioButton:hover {
                    background-color: #f0f0f0;
                    border-color: #4F46E5;
                }
                QRadioButton:checked {
                    background-color: #EEF2FF;
                    border-color: #4F46E5;
                    font-weight: bold;
                }
                QRadioButton::indicator {
                    width: 20px;
                    height: 20px;
                }
            """)
            self.answer_group.addButton(btn, i)
            self.answer_buttons.append(btn)
            layout.addWidget(btn)

        layout.addSpacing(20)

        # Submit-Button
        self.submit_btn = QPushButton("Antwort absenden")
        self.submit_btn.setStyleSheet("""
            QPushButton {
                background: #4F46E5;
                color: white;
                font-size: 16px;
                font-weight: bold;
                border-radius: 10px;
                padding: 15px;
                min-height: 50px;
            }
            QPushButton:hover {
                background: #4338CA;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)
        self.submit_btn.clicked.connect(self.submit_answer)
        layout.addWidget(self.submit_btn)

        layout.addStretch()

        self.setLayout(layout)

        # Timer für Zeitmessung
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_timer)
        self.timer.start(1000)  # Jede Sekunde

    def load_puzzle(self, index):
        """Lädt Rätsel"""
        if index >= len(self.puzzles):
            self.complete_session()
            return

        puzzle = self.puzzles[index]
        self.current_puzzle_index = index
        self.start_time = time.time()

        # Fortschritt aktualisieren
        self.progress_label.setText(f"Frage {index + 1} von {len(self.puzzles)}")
        self.progress_bar.setMaximum(len(self.puzzles))
        self.progress_bar.setValue(index)

        # H5P-Daten parsen
        h5p_data = json.loads(puzzle["h5p_json"]) if puzzle.get("h5p_json") else {}

        # Frage anzeigen
        question = h5p_data.get("question", puzzle["title"])
        self.question_label.setText(question)

        # Antwort-Optionen
        options = h5p_data.get("options", [])
        for i, btn in enumerate(self.answer_buttons):
            if i < len(options):
                btn.setText(options[i])
                btn.setVisible(True)
                btn.setChecked(False)
            else:
                btn.setVisible(False)

        self.submit_btn.setEnabled(True)

    def update_timer(self):
        """Aktualisiert Timer"""
        if self.start_time > 0:
            elapsed = int(time.time() - self.start_time)
            self.timer_label.setText(f"Zeit: {elapsed}s")

    def submit_answer(self):
        """Antwort absenden"""
        selected_id = self.answer_group.checkedId()

        if selected_id == -1:
            QMessageBox.warning(
                self,
                "Keine Auswahl",
                "Bitte wählen Sie eine Antwort aus."
            )
            return

        self.submit_btn.setEnabled(False)

        # Zeit berechnen
        time_taken = int(time.time() - self.start_time)

        # Antwort senden
        puzzle = self.puzzles[self.current_puzzle_index]
        result = self.api_client.submit_answer(
            session_id=self.session["id"],
            puzzle_id=puzzle["id"],
            answer={"selected": selected_id},
            time_taken=time_taken
        )

        if result:
            # Punkte aktualisieren
            self.score += result.get("points_earned", 0)
            self.score_label.setText(f"Punkte: {self.score}")

            # Feedback anzeigen
            if result.get("is_correct"):
                QMessageBox.information(
                    self,
                    "Richtig!",
                    f"Sehr gut! Du hast {result['points_earned']} Punkte erhalten."
                )
            else:
                QMessageBox.warning(
                    self,
                    "Leider falsch",
                    "Das war nicht die richtige Antwort. Beim nächsten Mal klappt's!"
                )

            # Nächstes Rätsel laden
            self.load_puzzle(self.current_puzzle_index + 1)
        else:
            QMessageBox.critical(
                self,
                "Fehler",
                "Antwort konnte nicht gesendet werden."
            )
            self.submit_btn.setEnabled(True)

    def complete_session(self):
        """Session abschließen"""
        self.timer.stop()

        # Session als abgeschlossen markieren
        self.api_client.complete_session(self.session["id"])

        QMessageBox.information(
            self,
            "Geschafft!",
            f"Du hast alle Rätsel gelöst!\n\nGesamtpunktzahl: {self.score}"
        )

        self.session_completed.emit()