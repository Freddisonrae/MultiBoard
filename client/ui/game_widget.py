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

    puzzle_completed = Signal(dict)
    session_completed = Signal()
    exit_requested = Signal()  # NEU: Signal für Exit

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

        # NEU: Exit-Button links
        self.exit_btn = QPushButton("← Zurück")
        self.exit_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                font-size: 14px;
                font-weight: bold;
                border-radius: 8px;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        self.exit_btn.clicked.connect(self.confirm_exit)
        header_layout.addWidget(self.exit_btn)

        header_layout.addSpacing(20)

        self.progress_label = QLabel()
        self.progress_label.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            color: #667eea;
        """)
        header_layout.addWidget(self.progress_label)

        header_layout.addStretch()

        self.score_label = QLabel("Punkte: 0")
        self.score_label.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            color: #27ae60;
        """)
        header_layout.addWidget(self.score_label)

        self.timer_label = QLabel("Zeit: 0s")
        self.timer_label.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            color: #e74c3c;
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
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #667eea, stop:1 #764ba2
                );
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
                border: 2px solid #667eea;
                border-radius: 10px;
                padding: 20px;
                font-size: 18px;
                font-weight: bold;
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
                    border-color: #667eea;
                }
                QRadioButton:checked {
                    background-color: #e8eaff;
                    border-color: #667eea;
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
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #667eea, stop:1 #764ba2
                );
                color: white;
                font-size: 16px;
                font-weight: bold;
                border-radius: 10px;
                padding: 15px;
                min-height: 50px;
            }
            QPushButton:hover {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #5568d3, stop:1 #6941a1
                );
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
        self.timer.start(1000)

    def confirm_exit(self):
        """Bestätigung vor dem Verlassen"""
        reply = QMessageBox.question(
            self,
            "Rätsel verlassen?",
            "Möchtest du wirklich zurück zur Raumliste?\nDein Fortschritt geht verloren.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.timer.stop()
            self.exit_requested.emit()

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
                    "Richtig! ✅",
                    f"Sehr gut! Du hast {result['points_earned']} Punkte erhalten."
                )
            else:
                QMessageBox.warning(
                    self,
                    "Leider falsch ❌",
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
            "Geschafft! 🎉",
            f"Du hast alle Rätsel gelöst!\n\nGesamtpunktzahl: {self.score}"
        )

        self.session_completed.emit()