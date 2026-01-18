"""
H5P Game Widget - FIXED für lokalen Server
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QProgressBar, QMessageBox
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
            print(f"📩 Antwort von H5P empfangen: {answer_data}")
            self.answer_submitted.emit(answer_data)
        except Exception as e:
            print(f"❌ Fehler beim Parsen der H5P-Antwort: {e}")


class H5PGameWidget(QWidget):
    """Widget für H5P-Rätsel mit WebView"""

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

        # WebChannel für JavaScript-Bridge
        self.bridge = H5PBridge()
        self.bridge.answer_submitted.connect(self.handle_h5p_answer)

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

        # WebView für H5P
        self.webview = QWebEngineView()
        self.webview.setMinimumHeight(500)

        # 🔥 WICHTIG: Settings konfigurieren
        settings = self.webview.settings()
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalStorageEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.AllowRunningInsecureContent, True)

        # 🔥 NEU: JavaScript Console Logging aktivieren
        self.webview.page().javaScriptConsoleMessage = self.handle_js_console

        # WebChannel einrichten
        self.channel = QWebChannel()
        self.channel.registerObject("bridge", self.bridge)
        self.webview.page().setWebChannel(self.channel)

        layout.addWidget(self.webview)

        layout.addSpacing(20)

        # Weiter-Button
        self.next_btn = QPushButton("Weiter zum nächsten Rätsel")
        self.next_btn.setStyleSheet("""
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
        """)
        self.next_btn.clicked.connect(self.next_puzzle)
        self.next_btn.setVisible(False)
        layout.addWidget(self.next_btn)

        self.setLayout(layout)

        # Timer für Zeitmessung
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_timer)
        self.timer.start(1000)

    def handle_js_console(self, level, message, line, source):
        """JavaScript Console Nachrichten loggen (nur Errors)"""
        if level == 2:  # Nur Errors loggen
            print(f"🌐 JS Error: {message}")

    def load_puzzle(self, index):
        """Lädt H5P-Rätsel"""
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

        # H5P laden
        if puzzle.get("h5p_content_id"):
            self.load_h5p_content(puzzle)
        else:
            self.load_simple_quiz(puzzle)

    def load_h5p_content(self, puzzle):
        """Lädt H5P-Content vom Server"""
        content_id = puzzle["h5p_content_id"]
        server_url = self.api_client.base_url.rstrip('/')

        print(f"🎨 Lade H5P Content: {content_id}")

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
        // WebChannel-Bridge zu Python
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
                // Event-Listener für H5P-Events
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

        // Starte Laden
        loadH5PFromServer();
    </script>
</body>
</html>
"""

        # 🔥 FIX: Verwende setHtml mit baseUrl statt nur setHtml
        # Das löst das localStorage Problem!
        from PySide6.QtCore import QUrl
        self.webview.setHtml(html, QUrl(server_url + "/"))
        self.next_btn.setVisible(False)

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
        """Verarbeitet Antwort von H5P"""
        print(f"✅ Antwort verarbeitet: {answer_data}")

        # Zeit berechnen
        time_taken = int(time.time() - self.start_time)

        # Antwort an Server senden
        puzzle = self.puzzles[self.current_puzzle_index]

        result = self.api_client.submit_answer(
            session_id=self.session["id"],
            puzzle_id=puzzle["id"],
            answer=answer_data,
            time_taken=time_taken
        )

        if result:
            # Punkte aktualisieren
            self.score += result.get("points_earned", 0)
            self.score_label.setText(f"Punkte: {self.score}")

            # Feedback anzeigen
            if result.get("is_correct") or answer_data.get("success"):
                QMessageBox.information(
                    self,
                    "Richtig! ✅",
                    f"Sehr gut! Du hast {result.get('points_earned', 10)} Punkte erhalten."
                )
            else:
                QMessageBox.warning(
                    self,
                    "Leider falsch ❌",
                    "Das war nicht die richtige Antwort. Beim nächsten Mal klappt's!"
                )

            # Weiter-Button anzeigen
            self.next_btn.setVisible(True)

    def next_puzzle(self):
        """Nächstes Rätsel laden"""
        self.next_btn.setVisible(False)
        self.load_puzzle(self.current_puzzle_index + 1)

    def update_timer(self):
        """Timer aktualisieren"""
        if self.start_time > 0:
            elapsed = int(time.time() - self.start_time)
            self.timer_label.setText(f"Zeit: {elapsed}s")

    def complete_session(self):
        """Session abschließen"""
        self.timer.stop()

        self.api_client.complete_session(self.session["id"])

        QMessageBox.information(
            self,
            "Geschafft! 🎉",
            f"Du hast alle Rätsel gelöst!\n\nGesamtpunktzahl: {self.score}"
        )

        self.session_completed.emit()