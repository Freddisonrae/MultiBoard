"""
H5P Game Widget - Mit Puzzle-Auswahl vor dem Start
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QProgressBar, QMessageBox, QScrollArea, QFrame
)
from PySide6.QtCore import Qt, QTimer, Signal, QUrl, Slot, QObject
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebEngineCore import QWebEngineSettings
from PySide6.QtWebChannel import QWebChannel
import json
import time


class H5PBridge(QObject):
    """Bridge zwischen JavaScript (H5P) und Python (Qt)"""
    answer_submitted = Signal(dict)

    @Slot(str)
    def submitAnswer(self, answer_json: str):
        """Wird von JavaScript aufgerufen wenn H5P fertig ist"""
        try:
            answer_data = json.loads(answer_json)
            print(f"Antwort von H5P empfangen: {answer_data}")
            self.answer_submitted.emit(answer_data)
        except Exception as e:
            print(f"Fehler beim Parsen der H5P-Antwort: {e}")


class H5PGameWidget(QWidget):
    """Widget für H5P-Rätsel mit Auswahlmenü"""

    puzzle_completed = Signal(dict)
    session_completed = Signal()
    exit_requested = Signal()

    def __init__(self, api_client, session, puzzles, parent=None):
        super().__init__(parent)
        self.api_client = api_client
        self.session = session
        self.puzzles = puzzles
        self.current_puzzle_index = -1  # -1 = Auswahlmenü
        self.start_time = 0
        self.completed_puzzles = set()  # Speichert welche Rätsel gelöst wurden

        # WebChannel für JavaScript-Bridge
        self.bridge = H5PBridge()
        self.bridge.answer_submitted.connect(self.handle_h5p_answer)

        self.init_ui()
        self.show_puzzle_selection()

    def init_ui(self):
        """UI initialisieren"""
        self.main_layout = QVBoxLayout()
        self.main_layout.setSpacing(20)
        self.main_layout.setContentsMargins(30, 30, 30, 30)

        # Container für wechselnden Content (Auswahl oder Rätsel)
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout()
        self.content_widget.setLayout(self.content_layout)

        self.main_layout.addWidget(self.content_widget)
        self.setLayout(self.main_layout)

    def show_puzzle_selection(self):
        """Zeigt Puzzle-Auswahlmenü"""
        # Content leeren
        while self.content_layout.count():
            child = self.content_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        # Header
        header_layout = QHBoxLayout()

        # NUR Zurück zur Raumliste Button (wenn im Auswahlmenü)
        exit_btn = QPushButton("← Zurück zur Raumliste")
        exit_btn.setStyleSheet("""
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
        exit_btn.clicked.connect(self.confirm_exit)
        header_layout.addWidget(exit_btn)

        header_layout.addStretch()

        # Fortschrittsanzeige
        completed_count = len(self.completed_puzzles)
        total_count = len(self.puzzles)
        progress_label = QLabel(f"Gelöst: {completed_count}/{total_count} Rätsel")
        progress_label.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: #27ae60;
        """)
        header_layout.addWidget(progress_label)

        self.content_layout.addLayout(header_layout)

        # Titel
        title = QLabel("Wähle ein Rätsel aus")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            font-size: 28px;
            font-weight: bold;
            color: #667eea;
            margin: 20px 0;
        """)
        self.content_layout.addWidget(title)

        # Fortschrittsbalken
        progress_bar = QProgressBar()
        progress_bar.setMaximum(total_count)
        progress_bar.setValue(completed_count)
        progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                text-align: center;
                height: 30px;
                font-size: 14px;
                font-weight: bold;
            }
            QProgressBar::chunk {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #27ae60, stop:1 #2ecc71
                );
            }
        """)
        progress_bar.setFormat(f"{completed_count}/{total_count} Rätsel gelöst")
        self.content_layout.addWidget(progress_bar)

        self.content_layout.addSpacing(20)

        # Scroll-Bereich für Rätsel-Karten
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; }")

        puzzles_widget = QWidget()
        puzzles_layout = QVBoxLayout()
        puzzles_layout.setSpacing(15)

        for i, puzzle in enumerate(self.puzzles):
            card = self.create_puzzle_card(puzzle, i)
            puzzles_layout.addWidget(card)

        puzzles_layout.addStretch()
        puzzles_widget.setLayout(puzzles_layout)
        scroll.setWidget(puzzles_widget)

        self.content_layout.addWidget(scroll)

        # Prüfe ob alle Rätsel gelöst sind
        if completed_count == total_count:
            self.show_completion_message()

    def create_puzzle_card(self, puzzle, index):
        """Erstellt eine Rätsel-Karte"""
        card = QFrame()
        is_completed = index in self.completed_puzzles

        if is_completed:
            card.setStyleSheet("""
                QFrame {
                    background-color: #d4edda;
                    border: 2px solid #28a745;
                    border-radius: 10px;
                    padding: 20px;
                }
            """)
        else:
            card.setStyleSheet("""
                QFrame {
                    background-color: white;
                    border: 2px solid #e0e0e0;
                    border-radius: 10px;
                    padding: 20px;
                }
                QFrame:hover {
                    border-color: #667eea;
                    background-color: #f8f9ff;
                }
            """)

        layout = QHBoxLayout()

        # Info-Bereich
        info_layout = QVBoxLayout()

        title_layout = QHBoxLayout()

        # Nummer
        number_label = QLabel(f"#{index + 1}")
        number_label.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #667eea;
            min-width: 50px;
        """)
        title_layout.addWidget(number_label)

        # Titel
        title_label = QLabel(puzzle.get("title", f"Rätsel {index + 1}"))
        title_label.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: #333;
        """)
        title_label.setWordWrap(True)
        title_layout.addWidget(title_label, stretch=1)

        info_layout.addLayout(title_layout)

        # Beschreibung falls vorhanden
        if puzzle.get("description"):
            desc_label = QLabel(puzzle["description"])
            desc_label.setWordWrap(True)
            desc_label.setStyleSheet("""
                font-size: 14px;
                color: #666;
                margin-top: 5px;
            """)
            info_layout.addWidget(desc_label)

        # Typ-Info
        puzzle_type = "H5P Interaktiv" if puzzle.get("h5p_content_id") else "Multiple Choice"
        type_label = QLabel(f"📝 {puzzle_type}")
        type_label.setStyleSheet("""
            font-size: 12px;
            color: #888;
            margin-top: 10px;
        """)
        info_layout.addWidget(type_label)

        layout.addLayout(info_layout, stretch=1)

        # Button-Bereich
        button_layout = QVBoxLayout()
        button_layout.setAlignment(Qt.AlignCenter)

        if is_completed:
            status_label = QLabel("✅ Gelöst")
            status_label.setStyleSheet("""
                font-size: 16px;
                font-weight: bold;
                color: #28a745;
            """)
            button_layout.addWidget(status_label)

            retry_btn = QPushButton("Nochmal spielen")
            retry_btn.setStyleSheet("""
                QPushButton {
                    background-color: #17a2b8;
                    color: white;
                    font-size: 14px;
                    font-weight: bold;
                    border-radius: 8px;
                    padding: 10px 20px;
                }
                QPushButton:hover {
                    background-color: #138496;
                }
            """)
            retry_btn.clicked.connect(lambda checked, idx=index: self.start_puzzle(idx))
            button_layout.addWidget(retry_btn)
        else:
            start_btn = QPushButton("▶ Starten")
            start_btn.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(
                        x1:0, y1:0, x2:1, y2:0,
                        stop:0 #667eea, stop:1 #764ba2
                    );
                    color: white;
                    font-size: 16px;
                    font-weight: bold;
                    border-radius: 8px;
                    padding: 15px 30px;
                    min-width: 120px;
                }
                QPushButton:hover {
                    background: qlineargradient(
                        x1:0, y1:0, x2:1, y2:0,
                        stop:0 #5568d3, stop:1 #6941a1
                    );
                }
            """)
            start_btn.clicked.connect(lambda checked, idx=index: self.start_puzzle(idx))
            button_layout.addWidget(start_btn)

        layout.addLayout(button_layout)

        card.setLayout(layout)
        return card

    def start_puzzle(self, index):
        """Startet ein bestimmtes Rätsel"""
        self.current_puzzle_index = index
        self.show_puzzle_view()

    def show_puzzle_view(self):
        """Zeigt die Rätsel-Ansicht"""
        # Content leeren
        while self.content_layout.count():
            child = self.content_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        puzzle = self.puzzles[self.current_puzzle_index]
        self.start_time = time.time()

        # Header
        header_layout = QHBoxLayout()

        # NUR Zurück zur Auswahl Button (wenn im Rätsel)
        back_btn = QPushButton("← Zurück zur Auswahl")
        back_btn.setStyleSheet("""
            QPushButton {
                background-color: #f39c12;
                color: white;
                font-size: 14px;
                font-weight: bold;
                border-radius: 8px;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #e67e22;
            }
        """)
        back_btn.clicked.connect(self.show_puzzle_selection)
        header_layout.addWidget(back_btn)

        header_layout.addSpacing(20)

        # Rätsel-Titel
        title_label = QLabel(f" {puzzle.get('title', f'Rätsel #{self.current_puzzle_index + 1}')}")
        title_label.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: #667eea;
        """)
        header_layout.addWidget(title_label)

        header_layout.addStretch()

        # Timer
        self.timer_label = QLabel("Zeit: 0s")
        self.timer_label.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            color: #e74c3c;
        """)
        header_layout.addWidget(self.timer_label)

        self.content_layout.addLayout(header_layout)
        self.content_layout.addSpacing(20)

        # WebView für H5P
        self.webview = QWebEngineView()
        self.webview.setMinimumHeight(500)

        # Settings konfigurieren
        settings = self.webview.settings()
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalStorageEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.AllowRunningInsecureContent, True)

        # JavaScript Console Logging
        self.webview.page().javaScriptConsoleMessage = self.handle_js_console

        # WebChannel einrichten
        self.channel = QWebChannel()
        self.channel.registerObject("bridge", self.bridge)
        self.webview.page().setWebChannel(self.channel)

        self.content_layout.addWidget(self.webview)

        # H5P laden
        if puzzle.get("h5p_content_id"):
            self.load_h5p_content(puzzle)
        else:
            self.load_simple_quiz(puzzle)

        # Timer starten
        if hasattr(self, 'timer'):
            self.timer.stop()
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_timer)
        self.timer.start(1000)

    def confirm_exit(self):
        """Bestätigung vor dem Verlassen"""
        reply = QMessageBox.question(
            self,
            "Raum verlassen?",
            "Möchtest du wirklich zurück zur Raumliste?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            if hasattr(self, 'timer'):
                self.timer.stop()
            self.exit_requested.emit()

    def handle_js_console(self, level, message, line, source):
        """JavaScript Console Nachrichten loggen (nur Errors)"""
        if level == 2:
            print(f"🌐 JS Error: {message}")

    def load_h5p_content(self, puzzle):
        """Lädt H5P-Content vom Server"""
        content_id = puzzle["h5p_content_id"]
        server_url = self.api_client.base_url.rstrip('/')

        print(f"Lade H5P Content: {content_id}")

        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>H5P Content</title>
    <script src="qrc:///qtwebchannel/qwebchannel.js"></script>
    <style>
        body {{
            margin: 0;
            padding: 20px;
            font-family: Arial, sans-serif;
            background: #f5f5f5;
        }}
        .h5p-container {{
            background: white;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .loading {{
            text-align: center;
            padding: 50px;
            font-size: 18px;
            color: #667eea;
        }}
        .error {{
            background: #fff3cd;
            border: 2px solid #ffc107;
            border-radius: 10px;
            padding: 20px;
            color: #856404;
            margin: 20px;
            text-align: center;
        }}
    </style>
</head>
<body>
    <div class="h5p-container">
        <div id="h5p-content">
            <div class="loading">H5P wird geladen...</div>
        </div>
    </div>

    <script>
        var bridge = null;
        new QWebChannel(qt.webChannelTransport, function(channel) {{
            bridge = channel.objects.bridge;
        }});

        var h5pLoaded = false;

        function loadH5PFromServer() {{
            const script = document.createElement('script');
            script.src = '{server_url}/static/h5p-standalone/dist/main.bundle.js';

            const timeout = setTimeout(function() {{
                if (!h5pLoaded) loadH5PFromCDN();
            }}, 3000);

            script.onload = function() {{
                clearTimeout(timeout);
                h5pLoaded = true;
                initH5P('{server_url}/static/h5p-standalone/dist');
            }};

            script.onerror = function() {{
                clearTimeout(timeout);
                loadH5PFromCDN();
            }};

            document.head.appendChild(script);
        }}

        function loadH5PFromCDN() {{
            if (h5pLoaded) return;

            const script = document.createElement('script');
            script.src = 'https://unpkg.com/h5p-standalone@3.7.3/dist/main.bundle.js';

            script.onload = function() {{
                h5pLoaded = true;
                initH5P('https://unpkg.com/h5p-standalone@3.7.3/dist');
            }};

            script.onerror = function() {{
                document.getElementById('h5p-content').innerHTML = 
                    '<div class="error">H5P konnte nicht geladen werden.<br>Bitte prüfe die Internetverbindung.</div>';
            }};

            document.head.appendChild(script);
        }}

        function initH5P(basePath) {{
            const el = document.getElementById('h5p-content');

            if (typeof H5PStandalone === 'undefined') {{
                el.innerHTML = '<div class="error">H5PStandalone nicht verfügbar.</div>';
                return;
            }}

            const h5pConfig = {{
                h5pJsonPath: '{server_url}/static/h5p-content/{content_id}',
                frameJs: basePath + '/frame.bundle.js',
                frameCss: basePath + '/styles/h5p.css',
            }};

            new H5PStandalone.H5P(el, h5pConfig).then(function(instance) {{
                window.H5P = window.H5P || {{}};
                H5P.externalDispatcher = H5P.externalDispatcher || new H5P.EventDispatcher();

                H5P.externalDispatcher.on('xAPI', function(event) {{
                    const verb = event.getVerb();

                    if (verb === 'answered' || verb === 'completed') {{
                        const score = event.getScore();
                        const maxScore = event.getMaxScore();
                        const success = score === maxScore;

                        const answer = {{
                            score: score,
                            maxScore: maxScore,
                            success: success,
                            raw: event.data
                        }};

                        if (bridge) {{
                            bridge.submitAnswer(JSON.stringify(answer));
                        }}
                    }}
                }});
            }}).catch(function(error) {{
                el.innerHTML = '<div class="error">Fehler beim Laden:<br>' + error + '</div>';
            }});
        }}

        loadH5PFromServer();
    </script>
</body>
</html>
"""

        from PySide6.QtCore import QUrl
        self.webview.setHtml(html, QUrl(server_url + "/"))

    def load_simple_quiz(self, puzzle):
        """Fallback: Einfaches Multiple-Choice ohne H5P"""
        h5p_data = json.loads(puzzle["h5p_json"]) if puzzle.get("h5p_json") else {}

        question = h5p_data.get("question", puzzle["title"])
        options = h5p_data.get("options", [])
        correct = h5p_data.get("correct", 0)

        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{
            font-family: Arial, sans-serif;
            padding: 20px;
            background: white;
        }}
        .question {{
            font-size: 20px;
            font-weight: bold;
            margin-bottom: 20px;
            color: #333;
        }}
        .option {{
            padding: 15px;
            margin: 10px 0;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.3s;
        }}
        .option:hover {{
            background: #f0f0f0;
            border-color: #667eea;
        }}
        .option.selected {{
            background: #e8eaff;
            border-color: #667eea;
        }}
        .submit-btn {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px 30px;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
            margin-top: 20px;
        }}
        .submit-btn:hover {{
            opacity: 0.9;
        }}
    </style>
    <script src="qrc:///qtwebchannel/qwebchannel.js"></script>
</head>
<body>
    <div class="question">{question}</div>
    <div id="options">
        {''.join([f'<div class="option" data-index="{i}" onclick="selectOption({i})">{opt}</div>'
                  for i, opt in enumerate(options)])}
    </div>
    <button class="submit-btn" onclick="submitAnswer()">Antwort absenden</button>

    <script>
        var bridge = null;
        var selectedIndex = -1;
        var correctIndex = {correct};

        new QWebChannel(qt.webChannelTransport, function(channel) {{
            bridge = channel.objects.bridge;
        }});

        function selectOption(index) {{
            document.querySelectorAll('.option').forEach(opt => {{
                opt.classList.remove('selected');
            }});
            document.querySelector('[data-index="' + index + '"]').classList.add('selected');
            selectedIndex = index;
        }}

        function submitAnswer() {{
            if (selectedIndex === -1) {{
                alert('Bitte wähle eine Antwort aus');
                return;
            }}

            const isCorrect = selectedIndex === correctIndex;
            const answer = {{
                selected: selectedIndex,
                correct: correctIndex,
                success: isCorrect,
                score: isCorrect ? 1 : 0,
                maxScore: 1
            }};

            if (bridge) {{
                bridge.submitAnswer(JSON.stringify(answer));
            }}
        }}
    </script>
</body>
</html>
"""

        self.webview.setHtml(html)

    @Slot(dict)
    def handle_h5p_answer(self, answer_data):
        """Verarbeitet Antwort von H5P - OHNE MessageBox"""
        print(f"Antwort verarbeitet: {answer_data}")

        if hasattr(self, 'timer'):
            self.timer.stop()

        time_taken = int(time.time() - self.start_time)
        puzzle = self.puzzles[self.current_puzzle_index]

        result = self.api_client.submit_answer(
            session_id=self.session["id"],
            puzzle_id=puzzle["id"],
            answer=answer_data,
            time_taken=time_taken
        )

        if result:
            # Rätsel als gelöst markieren
            self.completed_puzzles.add(self.current_puzzle_index)

            # Zurück zur Auswahl
            QTimer.singleShot(1000, self.show_puzzle_selection)

    def update_timer(self):
        """Timer aktualisieren"""
        if self.start_time > 0 and hasattr(self, 'timer_label'):
            elapsed = int(time.time() - self.start_time)
            self.timer_label.setText(f"Zeit: {elapsed}s")

    def show_completion_message(self):
        """Zeigt Glückwunsch-Nachricht wenn alle Rätsel gelöst sind"""
        QMessageBox.information(
            self,
            "Alle Rätsel gelöst!",
            f"Gratuliere! Du hast alle {len(self.puzzles)} Rätsel erfolgreich gelöst!\n\n"
            "Du kannst jetzt zur Raumliste zurückkehren oder einzelne Rätsel nochmal spielen."
        )