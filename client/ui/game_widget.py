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
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QRadioButton, QButtonGroup, QProgressBar,
    QMessageBox, QFrame, QGraphicsOpacityEffect
)
from PySide6.QtCore import Qt, QTimer, Signal, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QFont
import json
import time

# Farben
COLORS = {
    "bg_main": "#0F172A", "bg_card": "#1E293B", "bg_card_hover": "#334155",
    "primary": "#3B82F6", "primary_hover": "#2563EB",
    "text_primary": "#F8FAFC", "text_secondary": "#94A3B8", "text_muted": "#64748B",
    "border": "#334155", "accent": "#F59E0B", "success": "#22C55E", "error": "#EF4444"
}


class GameWidget(QWidget):
    """Widget für Rätsel-Anzeige mit modernem Design"""

    puzzle_completed = Signal(dict)
    session_completed = Signal()

    def __init__(self, api_client, session, puzzles, parent=None):
        super().__init__(parent)
        self.api_client = api_client
        self.session = session
        self.puzzles = puzzles
        self.current_puzzle_index = 0
        self.start_time = 0
        self.score = 0

        self.setStyleSheet(f"background-color: {COLORS['bg_main']};")
        self.init_ui()
        self.load_puzzle(0)

    def init_ui(self):
        """UI initialisieren"""
        layout = QVBoxLayout()
        layout.setSpacing(24)
        layout.setContentsMargins(40, 30, 40, 30)

        # ═══════════════════════════════════════════════════════
        # HEADER mit Statistiken
        # ═══════════════════════════════════════════════════════
        header_frame = QFrame()
        header_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['bg_card']};
                border: 1px solid {COLORS['border']};
                border-radius: 16px;
                padding: 16px;
            }}
        """)
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(20, 16, 20, 16)

        # Fortschritt
        progress_container = QVBoxLayout()
        progress_label_title = QLabel("Fortschritt")
        progress_label_title.setStyleSheet(f"color: {COLORS['text_muted']}; font-size: 12px;")
        progress_container.addWidget(progress_label_title)

        self.progress_label = QLabel()
        self.progress_label.setStyleSheet(f"""
            font-size: 20px;
            font-weight: bold;
            color: {COLORS['primary']};
        """)
        progress_container.addWidget(self.progress_label)
        header_layout.addLayout(progress_container)

        header_layout.addStretch()

        # Punkte
        score_container = QVBoxLayout()
        score_label_title = QLabel("Punkte")
        score_label_title.setStyleSheet(f"color: {COLORS['text_muted']}; font-size: 12px;")
        score_label_title.setAlignment(Qt.AlignCenter)
        score_container.addWidget(score_label_title)

        self.score_label = QLabel("0")
        self.score_label.setStyleSheet(f"""
            font-size: 28px;
            font-weight: bold;
            color: {COLORS['success']};
        """)
        self.score_label.setAlignment(Qt.AlignCenter)
        score_container.addWidget(self.score_label)
        header_layout.addLayout(score_container)

        header_layout.addStretch()

        # Timer
        timer_container = QVBoxLayout()
        timer_label_title = QLabel("Zeit")
        timer_label_title.setStyleSheet(f"color: {COLORS['text_muted']}; font-size: 12px;")
        timer_label_title.setAlignment(Qt.AlignRight)
        timer_container.addWidget(timer_label_title)

        self.timer_label = QLabel("0s")
        self.timer_label.setStyleSheet(f"""
            font-size: 20px;
            font-weight: bold;
            color: {COLORS['accent']};
        """)
        self.timer_label.setAlignment(Qt.AlignRight)
        timer_container.addWidget(self.timer_label)
        header_layout.addLayout(timer_container)

        header_frame.setLayout(header_layout)
        layout.addWidget(header_frame)

        # ═══════════════════════════════════════════════════════
        # FORTSCHRITTSBALKEN
        # ═══════════════════════════════════════════════════════
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedHeight(8)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                background-color: {COLORS['bg_card']};
                border: none;
                border-radius: 4px;
            }}
            QProgressBar::chunk {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 {COLORS['primary']}, 
                    stop:1 {COLORS['accent']}
                );
                border-radius: 4px;
            }}
        """)
        layout.addWidget(self.progress_bar)

        # ═══════════════════════════════════════════════════════
        # FRAGE
        # ═══════════════════════════════════════════════════════
        question_frame = QFrame()
        question_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['bg_card']};
                border: 2px solid {COLORS['primary']};
                border-radius: 16px;
            }}
        """)
        question_layout = QVBoxLayout()
        question_layout.setContentsMargins(28, 24, 28, 24)

        question_icon = QLabel("❓")
        question_icon.setStyleSheet("font-size: 32px;")
        question_layout.addWidget(question_icon)

        self.question_label = QLabel()
        self.question_label.setWordWrap(True)
        self.question_label.setStyleSheet(f"""
            font-size: 22px;
            font-weight: 600;
            color: {COLORS['text_primary']};
            line-height: 1.5;
        """)
        question_layout.addWidget(self.question_label)

        question_frame.setLayout(question_layout)
        layout.addWidget(question_frame)

        # ═══════════════════════════════════════════════════════
        # ANTWORT-OPTIONEN
        # ═══════════════════════════════════════════════════════
        self.answer_group = QButtonGroup(self)
        self.answer_buttons = []
        self.answer_frames = []

        answers_container = QWidget()
        answers_layout = QVBoxLayout()
        answers_layout.setSpacing(12)
        answers_layout.setContentsMargins(0, 0, 0, 0)

        option_letters = ["A", "B", "C", "D"]

        for i in range(4):
            # Container für jede Antwort
            answer_frame = QFrame()
            answer_frame.setStyleSheet(f"""
                QFrame {{
                    background-color: {COLORS['bg_card']};
                    border: 2px solid {COLORS['border']};
                    border-radius: 12px;
                }}
                QFrame:hover {{
                    border-color: {COLORS['primary']};
                    background-color: {COLORS['bg_card_hover']};
                }}
            """)

            frame_layout = QHBoxLayout()
            frame_layout.setContentsMargins(16, 14, 16, 14)
            frame_layout.setSpacing(16)

            # Buchstaben-Badge
            letter_label = QLabel(option_letters[i])
            letter_label.setFixedSize(36, 36)
            letter_label.setAlignment(Qt.AlignCenter)
            letter_label.setStyleSheet(f"""
                background-color: {COLORS['bg_main']};
                color: {COLORS['primary']};
                font-size: 16px;
                font-weight: bold;
                border-radius: 18px;
            """)
            frame_layout.addWidget(letter_label)

            # Radio Button
            btn = QRadioButton()
            btn.setStyleSheet(f"""
                QRadioButton {{
                    color: {COLORS['text_primary']};
                    font-size: 16px;
                    spacing: 0px;
                }}
                QRadioButton::indicator {{
                    width: 0px;
                    height: 0px;
                }}
            """)
            self.answer_group.addButton(btn, i)
            self.answer_buttons.append(btn)
            frame_layout.addWidget(btn, stretch=1)

            answer_frame.setLayout(frame_layout)
            self.answer_frames.append(answer_frame)

            # Klick auf Frame aktiviert Radio Button
            answer_frame.mousePressEvent = lambda e, b=btn, f=answer_frame: self._select_answer(b, f)

            answers_layout.addWidget(answer_frame)

        answers_container.setLayout(answers_layout)
        layout.addWidget(answers_container)

        layout.addSpacing(8)

        # ═══════════════════════════════════════════════════════
        # SUBMIT-BUTTON
        # ═══════════════════════════════════════════════════════
        self.submit_btn = QPushButton("✓ Antwort absenden")
        self.submit_btn.setCursor(Qt.PointingHandCursor)
        self.submit_btn.setMinimumHeight(56)
        self.submit_btn.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 {COLORS['success']}, 
                    stop:1 #10B981
                );
                color: {COLORS['text_primary']};
                font-size: 18px;
                font-weight: bold;
                border-radius: 14px;
                border: none;
            }}
            QPushButton:hover {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #16A34A, 
                    stop:1 #059669
                );
            }}
            QPushButton:disabled {{
                background-color: {COLORS['border']};
                color: {COLORS['text_muted']};
            }}
        """)
        self.submit_btn.clicked.connect(self.submit_answer)
        layout.addWidget(self.submit_btn)

        layout.addStretch()
        self.setLayout(layout)

        # Timer für Zeitmessung
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_timer)
        self.timer.start(1000)

    def _select_answer(self, button, frame):
        """Antwort auswählen und visuell hervorheben"""
        button.setChecked(True)

        # Alle Frames zurücksetzen
        for f in self.answer_frames:
            f.setStyleSheet(f"""
                QFrame {{
                    background-color: {COLORS['bg_card']};
                    border: 2px solid {COLORS['border']};
                    border-radius: 12px;
                }}
            """)

        # Ausgewählten Frame hervorheben
        frame.setStyleSheet(f"""
            QFrame {{
                background-color: rgba(59, 130, 246, 0.15);
                border: 2px solid {COLORS['primary']};
                border-radius: 12px;
            }}
        """)

    def load_puzzle(self, index):
        """Rätsel laden"""
        if index >= len(self.puzzles):
            self.complete_session()
            return

        puzzle = self.puzzles[index]
        self.current_puzzle_index = index
        self.start_time = time.time()

        # Fortschritt aktualisieren
        self.progress_label.setText(f"{index + 1} / {len(self.puzzles)}")
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
                self.answer_frames[i].setVisible(True)
                # Frame-Style zurücksetzen
                self.answer_frames[i].setStyleSheet(f"""
                    QFrame {{
                        background-color: {COLORS['bg_card']};
                        border: 2px solid {COLORS['border']};
                        border-radius: 12px;
                    }}
                    QFrame:hover {{
                        border-color: {COLORS['primary']};
                        background-color: {COLORS['bg_card_hover']};
                    }}
                """)
            else:
                btn.setVisible(False)
                self.answer_frames[i].setVisible(False)

        self.submit_btn.setEnabled(True)
        self.submit_btn.setText("✓ Antwort absenden")

    def update_timer(self):
        """Timer aktualisieren"""
        if self.start_time > 0:
            elapsed = int(time.time() - self.start_time)
            self.timer_label.setText(f"{elapsed}s")

            # Farbe ändern bei langer Zeit
            if elapsed > 30:
                self.timer_label.setStyleSheet(f"""
                    font-size: 20px;
                    font-weight: bold;
                    color: {COLORS['error']};
                """)
            elif elapsed > 15:
                self.timer_label.setStyleSheet(f"""
                    font-size: 20px;
                    font-weight: bold;
                    color: {COLORS['accent']};
                """)

    def submit_answer(self):
        """Antwort absenden"""
        selected_id = self.answer_group.checkedId()

        if selected_id == -1:
            QMessageBox.warning(
                self,
                "Keine Auswahl",
                "Bitte wähle eine Antwort aus."
            )
            return

        self.submit_btn.setEnabled(False)
        self.submit_btn.setText("⏳ Wird geprüft...")

        time_taken = int(time.time() - self.start_time)

        puzzle = self.puzzles[self.current_puzzle_index]
        result = self.api_client.submit_answer(
            session_id=self.session["id"],
            puzzle_id=puzzle["id"],
            answer={"selected": selected_id},
            time_taken=time_taken
        )

        if result:
            self.score += result.get("points_earned", 0)
            self.score_label.setText(str(self.score))

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
                    "Das war nicht die richtige Antwort.\nBeim nächsten Mal klappt's!"
                )

            # Timer-Farbe zurücksetzen
            self.timer_label.setStyleSheet(f"""
                font-size: 20px;
                font-weight: bold;
                color: {COLORS['accent']};
            """)

            self.load_puzzle(self.current_puzzle_index + 1)
        else:
            QMessageBox.critical(
                self,
                "Fehler",
                "Antwort konnte nicht gesendet werden."
            )
            self.submit_btn.setEnabled(True)
            self.submit_btn.setText("✓ Antwort absenden")

    def complete_session(self):
        """Session abschließen"""
        self.timer.stop()
        self.api_client.complete_session(self.session["id"])

        QMessageBox.information(
            self,
            "Geschafft! 🎉",
            f"Du hast alle Rätsel gelöst!\n\n🏆 Gesamtpunktzahl: {self.score}"
        )

        self.session_completed.emit()
