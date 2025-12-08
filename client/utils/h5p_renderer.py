"""
H5P-Content-Renderer für Desktop-App
Rendert verschiedene H5P-Content-Typen als Qt-Widgets
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QRadioButton, QButtonGroup, QCheckBox, QLineEdit,
    QTextEdit, QPushButton, QGroupBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from typing import Dict, Any, Optional
import json


class H5PRenderer:
    """
    Factory-Klasse für H5P-Content-Rendering
    Erstellt Qt-Widgets basierend auf H5P-Content-Type
    """

    @staticmethod
    def render(h5p_data: Dict[str, Any], puzzle_type: str, parent=None) -> Optional[QWidget]:
        """
        Rendert H5P-Content basierend auf Typ

        Args:
            h5p_data: H5P-JSON-Daten
            puzzle_type: Typ des Rätsels (z.B. 'multiple_choice')
            parent: Parent-Widget

        Returns:
            QWidget mit gerendertem Content oder None
        """
        if puzzle_type == "multiple_choice":
            return MultipleChoiceWidget(h5p_data, parent)
        elif puzzle_type == "true_false":
            return TrueFalseWidget(h5p_data, parent)
        elif puzzle_type == "fill_in_blank":
            return FillInBlankWidget(h5p_data, parent)
        elif puzzle_type == "essay":
            return EssayWidget(h5p_data, parent)
        else:
            # Fallback für unbekannte Typen
            return DefaultWidget(h5p_data, parent)


class BaseH5PWidget(QWidget):
    """Basis-Widget für alle H5P-Content-Typen"""

    answer_changed = Signal()

    def __init__(self, h5p_data: Dict[str, Any], parent=None):
        super().__init__(parent)
        self.h5p_data = h5p_data
        self.init_ui()

    def init_ui(self):
        """Muss von Subklassen implementiert werden"""
        raise NotImplementedError

    def get_answer(self) -> Dict[str, Any]:
        """
        Gibt die Antwort als Dictionary zurück
        Muss von Subklassen implementiert werden
        """
        raise NotImplementedError

    def is_valid(self) -> bool:
        """Prüft ob Antwort gültig ist"""
        return True


class MultipleChoiceWidget(BaseH5PWidget):
    """Widget für Multiple-Choice-Fragen"""

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)

        # Frage
        question = self.h5p_data.get("question", "")
        question_label = QLabel(question)
        question_label.setWordWrap(True)
        question_label.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            padding: 20px;
            background-color: #f5f5f5;
            border: 2px solid #667eea;
            border-radius: 10px;
        """)
        layout.addWidget(question_label)

        # Antwort-Optionen
        self.button_group = QButtonGroup(self)
        options = self.h5p_data.get("options", [])

        for i, option in enumerate(options):
            radio = QRadioButton(option)
            radio.setStyleSheet("""
                QRadioButton {
                    font-size: 16px;
                    padding: 15px;
                    background-color: white;
                    border: 2px solid #e0e0e0;
                    border-radius: 8px;
                    margin: 5px;
                }
                QRadioButton:hover {
                    background-color: #f0f0f0;
                    border-color: #667eea;
                }
                QRadioButton:checked {
                    background-color: #e8eaff;
                    border-color: #667eea;
                    font-weight: bold;
                }
                QRadioButton::indicator {
                    width: 20px;
                    height: 20px;
                }
            """)
            self.button_group.addButton(radio, i)
            layout.addWidget(radio)
            radio.toggled.connect(self.answer_changed.emit)

        self.setLayout(layout)

    def get_answer(self) -> Dict[str, Any]:
        """Gibt ausgewählte Antwort zurück"""
        selected = self.button_group.checkedId()
        return {"selected": selected, "type": "multiple_choice"}

    def is_valid(self) -> bool:
        """Prüft ob eine Option ausgewählt wurde"""
        return self.button_group.checkedId() != -1


class TrueFalseWidget(BaseH5PWidget):
    """Widget für Wahr/Falsch-Fragen"""

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)

        # Frage
        question = self.h5p_data.get("question", "")
        question_label = QLabel(question)
        question_label.setWordWrap(True)
        question_label.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            padding: 20px;
            background-color: #f5f5f5;
            border: 2px solid #667eea;
            border-radius: 10px;
        """)
        layout.addWidget(question_label)

        # Wahr/Falsch Buttons
        self.button_group = QButtonGroup(self)

        true_button = QRadioButton("✓ Wahr")
        true_button.setStyleSheet(self._button_style())
        self.button_group.addButton(true_button, 1)
        layout.addWidget(true_button)

        false_button = QRadioButton("✗ Falsch")
        false_button.setStyleSheet(self._button_style())
        self.button_group.addButton(false_button, 0)
        layout.addWidget(false_button)

        true_button.toggled.connect(self.answer_changed.emit)
        false_button.toggled.connect(self.answer_changed.emit)

        self.setLayout(layout)

    def _button_style(self):
        return """
            QRadioButton {
                font-size: 18px;
                padding: 20px;
                background-color: white;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                margin: 5px;
            }
            QRadioButton:hover {
                background-color: #f0f0f0;
                border-color: #667eea;
            }
            QRadioButton:checked {
                background-color: #e8eaff;
                border-color: #667eea;
                font-weight: bold;
            }
        """

    def get_answer(self) -> Dict[str, Any]:
        """Gibt Wahr/Falsch-Antwort zurück"""
        selected = self.button_group.checkedId()
        return {"value": bool(selected), "type": "true_false"}

    def is_valid(self) -> bool:
        return self.button_group.checkedId() != -1


class FillInBlankWidget(BaseH5PWidget):
    """Widget für Lückentext-Aufgaben"""

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)

        # Frage/Text
        question = self.h5p_data.get("question", "")
        question_label = QLabel(question)
        question_label.setWordWrap(True)
        question_label.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            padding: 20px;
            background-color: #f5f5f5;
            border: 2px solid #667eea;
            border-radius: 10px;
        """)
        layout.addWidget(question_label)

        # Lücken (Blanks)
        self.blank_inputs = []
        blanks = self.h5p_data.get("blanks", [])

        for i, blank in enumerate(blanks):
            group = QGroupBox(f"Lücke {i + 1}")
            group.setStyleSheet("""
                QGroupBox {
                    font-size: 16px;
                    font-weight: bold;
                    border: 2px solid #e0e0e0;
                    border-radius: 8px;
                    margin-top: 10px;
                    padding-top: 15px;
                }
                QGroupBox::title {
                    color: #667eea;
                }
            """)

            group_layout = QVBoxLayout()

            # Hinweis falls vorhanden
            hint = blank.get("hint", "")
            if hint:
                hint_label = QLabel(f"💡 Hinweis: {hint}")
                hint_label.setStyleSheet("color: #666; font-size: 14px; font-style: italic;")
                group_layout.addWidget(hint_label)

            # Eingabefeld
            input_field = QLineEdit()
            input_field.setPlaceholderText("Antwort eingeben...")
            input_field.setStyleSheet("""
                QLineEdit {
                    font-size: 16px;
                    padding: 12px;
                    border: 2px solid #e0e0e0;
                    border-radius: 8px;
                    background-color: white;
                }
                QLineEdit:focus {
                    border-color: #667eea;
                }
            """)
            input_field.textChanged.connect(self.answer_changed.emit)
            self.blank_inputs.append(input_field)
            group_layout.addWidget(input_field)

            group.setLayout(group_layout)
            layout.addWidget(group)

        self.setLayout(layout)

    def get_answer(self) -> Dict[str, Any]:
        """Gibt Lückentext-Antworten zurück"""
        answers = [input_field.text().strip() for input_field in self.blank_inputs]
        return {"blanks": answers, "type": "fill_in_blank"}

    def is_valid(self) -> bool:
        """Prüft ob alle Lücken ausgefüllt sind"""
        return all(input_field.text().strip() for input_field in self.blank_inputs)


class EssayWidget(BaseH5PWidget):
    """Widget für Essay/Freitext-Aufgaben"""

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)

        # Frage
        question = self.h5p_data.get("question", "")
        question_label = QLabel(question)
        question_label.setWordWrap(True)
        question_label.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            padding: 20px;
            background-color: #f5f5f5;
            border: 2px solid #667eea;
            border-radius: 10px;
        """)
        layout.addWidget(question_label)

        # Anforderungen
        min_words = self.h5p_data.get("min_words", 50)
        info_label = QLabel(f"📝 Mindestens {min_words} Wörter erforderlich")
        info_label.setStyleSheet("""
            font-size: 14px;
            color: #666;
            padding: 10px;
        """)
        layout.addWidget(info_label)

        # Textfeld
        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText("Deine Antwort hier eingeben...")
        self.text_edit.setStyleSheet("""
            QTextEdit {
                font-size: 16px;
                padding: 15px;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                background-color: white;
                min-height: 200px;
            }
            QTextEdit:focus {
                border-color: #667eea;
            }
        """)
        self.text_edit.textChanged.connect(self._update_word_count)
        layout.addWidget(self.text_edit)

        # Wörter-Zähler
        self.word_count_label = QLabel("Wörter: 0")
        self.word_count_label.setStyleSheet("""
            font-size: 14px;
            color: #888;
        """)
        layout.addWidget(self.word_count_label)

        self.setLayout(layout)

    def _update_word_count(self):
        """Aktualisiert Wörter-Zähler"""
        text = self.text_edit.toPlainText()
        words = len(text.split()) if text.strip() else 0
        self.word_count_label.setText(f"Wörter: {words}")
        self.answer_changed.emit()

    def get_answer(self) -> Dict[str, Any]:
        """Gibt Essay-Text zurück"""
        text = self.text_edit.toPlainText()
        word_count = len(text.split()) if text.strip() else 0
        return {
            "text": text,
            "word_count": word_count,
            "type": "essay"
        }

    def is_valid(self) -> bool:
        """Prüft ob Mindest-Wortzahl erreicht ist"""
        text = self.text_edit.toPlainText()
        word_count = len(text.split()) if text.strip() else 0
        min_words = self.h5p_data.get("min_words", 50)
        return word_count >= min_words


class DefaultWidget(BaseH5PWidget):
    """Fallback-Widget für unbekannte Content-Typen"""

    def init_ui(self):
        layout = QVBoxLayout()

        message = QLabel("⚠️ Dieser Content-Typ wird noch nicht unterstützt.")
        message.setAlignment(Qt.AlignCenter)
        message.setStyleSheet("""
            font-size: 16px;
            color: #e74c3c;
            padding: 40px;
        """)
        layout.addWidget(message)

        # Debug-Info (JSON anzeigen)
        debug = QLabel(f"Content-Daten: {json.dumps(self.h5p_data, indent=2)}")
        debug.setWordWrap(True)
        debug.setStyleSheet("""
            font-size: 12px;
            color: #666;
            padding: 20px;
            background-color: #f5f5f5;
            border-radius: 8px;
        """)
        layout.addWidget(debug)

        self.setLayout(layout)

    def get_answer(self) -> Dict[str, Any]:
        return {"type": "unknown"}

    def is_valid(self) -> bool:
        return False


# ============================================================================
# Utility-Funktionen
# ============================================================================

def parse_h5p_json(h5p_string: str) -> Dict[str, Any]:
    """
    Parst H5P-JSON-String sicher

    Args:
        h5p_string: JSON-String

    Returns:
        Dictionary oder leeres Dict bei Fehler
    """
    try:
        return json.loads(h5p_string)
    except (json.JSONDecodeError, TypeError):
        return {}


def validate_h5p_data(h5p_data: Dict[str, Any], puzzle_type: str) -> bool:
    """
    Validiert H5P-Daten für bestimmten Typ

    Args:
        h5p_data: H5P-Daten
        puzzle_type: Content-Typ

    Returns:
        True wenn gültig, False sonst
    """
    if puzzle_type == "multiple_choice":
        return "question" in h5p_data and "options" in h5p_data
    elif puzzle_type == "true_false":
        return "question" in h5p_data
    elif puzzle_type == "fill_in_blank":
        return "question" in h5p_data and "blanks" in h5p_data
    elif puzzle_type == "essay":
        return "question" in h5p_data

    return False