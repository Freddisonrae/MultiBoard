// Admin-Panel JavaScript - MultiRoom
const API_BASE = window.location.origin;
let authToken = null;
let currentUser = null;

// Initialisierung
document.addEventListener('DOMContentLoaded', () => {
    initApp();
});

function initApp() {
    // Tab-Umschalter für Login/Register
    document.querySelectorAll('.auth-tab').forEach(tab => {
        tab.addEventListener('click', () => switchAuthMode(tab.dataset.mode));
    });

    // Event Listeners für Formulare
    document.getElementById('login-form').addEventListener('submit', handleLogin);
    document.getElementById('register-form').addEventListener('submit', handleRegister);

    // Dashboard-Event-Listeners (werden später aktiviert)
    const logoutBtn = document.getElementById('logout-btn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', handleLogout);
    }

    const createRoomBtn = document.getElementById('create-room-btn');
    if (createRoomBtn) {
        createRoomBtn.addEventListener('click', showCreateRoomModal);
    }

    const createPuzzleBtn = document.getElementById('create-puzzle-btn');
    if (createPuzzleBtn) {
        createPuzzleBtn.addEventListener('click', showCreatePuzzleModal);
    }

    const modalClose = document.getElementById('modal-close');
    if (modalClose) {
        modalClose.addEventListener('click', closeModal);
    }

    // Tab-Switching im Dashboard
    document.querySelectorAll('.tab').forEach(tab => {
        tab.addEventListener('click', () => switchTab(tab.dataset.tab));
    });

    // Token aus localStorage laden
    const savedToken = localStorage.getItem('authToken');
    const savedUser = localStorage.getItem('currentUser');

    if (savedToken && savedUser) {
        authToken = savedToken;
        currentUser = JSON.parse(savedUser);
        showDashboard();
        loadRooms();
    }
}

// Tab-Umschalter für Login/Register
function switchAuthMode(mode) {
    // Tabs umschalten
    document.querySelectorAll('.auth-tab').forEach(t => t.classList.remove('active'));
    document.querySelector(`[data-mode="${mode}"]`).classList.add('active');

    // Forms umschalten
    document.querySelectorAll('.auth-form').forEach(f => f.classList.remove('active'));
    document.getElementById(`${mode}-form`).classList.add('active');

    // Nachricht ausblenden
    hideMessage();
}

// Login
async function handleLogin(e) {
    e.preventDefault();

    const username = document.getElementById('login-username').value.trim();
    const password = document.getElementById('login-password').value.trim();

    if (!username || !password) {
        showMessage('Bitte alle Felder ausfüllen', 'error');
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/api/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });

        const data = await response.json();

        if (!response.ok) {
            showMessage(data.detail || 'Anmeldung fehlgeschlagen', 'error');
            return;
        }

        if (data.user.role !== 'teacher') {
            showMessage('Nur Lehrer können sich hier anmelden', 'error');
            return;
        }

        // WICHTIG: Token global speichern
        authToken = data.access_token;
        currentUser = data.user;

        console.log('✅ Login erfolgreich!'); // DEBUG
        console.log('🔑 Token gespeichert:', authToken); // DEBUG
        console.log('👤 User:', currentUser); // DEBUG

        // In localStorage speichern
        localStorage.setItem('authToken', authToken);
        localStorage.setItem('currentUser', JSON.stringify(currentUser));

        showMessage('Anmeldung erfolgreich! Lade Dashboard...', 'success');

        // Dashboard anzeigen
        setTimeout(() => {
            showDashboard();
            loadRooms();
        }, 500);

    } catch (error) {
        console.error('Login error:', error);
        showMessage('Verbindungsfehler. Bitte prüfen Sie Ihre Internetverbindung.', 'error');
    }
}

// Registrierung
async function handleRegister(e) {
    e.preventDefault();

    const username = document.getElementById('reg-username').value.trim();
    const fullname = document.getElementById('reg-fullname').value.trim();
    const password = document.getElementById('reg-password').value;
    const password2 = document.getElementById('reg-password2').value;

    // Validierung
    if (!username || !fullname || !password || !password2) {
        showMessage('Bitte alle Felder ausfüllen', 'error');
        return;
    }

    if (username.length < 3) {
        showMessage('Benutzername muss mindestens 3 Zeichen haben', 'error');
        return;
    }

    if (password.length < 8) {
        showMessage('Passwort muss mindestens 8 Zeichen haben', 'error');
        return;
    }

    if (password !== password2) {
        showMessage('Passwörter stimmen nicht überein', 'error');
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/api/auth/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                username: username,
                password: password,
                role: 'teacher',
                full_name: fullname
            })
        });

        const data = await response.json();

        if (!response.ok) {
            showMessage(data.detail || 'Registrierung fehlgeschlagen', 'error');
            return;
        }

        // Erfolg
        showMessage(
            '✅ Registrierung erfolgreich! Ihr Account muss von einem Administrator freigeschaltet werden. ' +
            'Sie werden benachrichtigt, sobald Sie sich anmelden können.',
            'success'
        );

        // Formular zurücksetzen
        document.getElementById('register-form').reset();

        // Nach 3 Sekunden zum Login wechseln
        setTimeout(() => {
            switchAuthMode('login');
        }, 3000);

    } catch (error) {
        console.error('Register error:', error);
        showMessage('Verbindungsfehler. Bitte prüfen Sie Ihre Internetverbindung.', 'error');
    }
}

// Nachrichten anzeigen
function showMessage(text, type) {
    const msg = document.getElementById('auth-message');
    msg.textContent = text;
    msg.className = `message ${type} visible`;
}

function hideMessage() {
    const msg = document.getElementById('auth-message');
    msg.className = 'message';
}

function showError(message) {
    showMessage(message, 'error');
}

function handleLogout() {
    authToken = null;
    currentUser = null;
    localStorage.removeItem('authToken');
    localStorage.removeItem('currentUser');

    document.getElementById('auth-container').style.display = 'block';
    document.getElementById('dashboard-container').style.display = 'none';

    // Formulare zurücksetzen
    document.getElementById('login-form').reset();
    document.getElementById('register-form').reset();
    switchAuthMode('login');
}

function showDashboard() {
    document.getElementById('auth-container').style.display = 'none';
    document.getElementById('dashboard-container').style.display = 'block';
    document.getElementById('user-name').textContent = currentUser.full_name || currentUser.username;
}

// API-Helfer
async function apiRequest(endpoint, options = {}) {
    const headers = {
        'Content-Type': 'application/json',
        ...options.headers
    };

    if (authToken) {
        headers['Authorization'] = `Bearer ${authToken}`;
    }

    console.log('🌐 API Request:', endpoint, headers); // DEBUG

    const response = await fetch(`${API_BASE}${endpoint}`, {
        ...options,
        headers
    });

    if (!response.ok) {
        const error = await response.text();
        console.error('❌ API Error:', response.status, error);
        throw new Error(`API Error: ${response.status}`);
    }

    return response.json();
}

// Tab-Switching
function switchTab(tabName) {
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(tc => tc.classList.remove('active'));

    document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');
    document.getElementById(`${tabName}-tab`).classList.add('active');

    // Daten laden
    if (tabName === 'rooms') loadRooms();
    else if (tabName === 'puzzles') loadPuzzles();
    else if (tabName === 'students') loadStudents();
}

// Räume laden
async function loadRooms() {
    try {
        const rooms = await apiRequest('/api/admin/rooms');
        displayRooms(rooms);
    } catch (error) {
        console.error('Fehler beim Laden der Räume:', error);
    }
}

function displayRooms(rooms) {
    const container = document.getElementById('rooms-list');

    if (rooms.length === 0) {
        container.innerHTML = '<p style="text-align: center; color: #999;">Keine Räume vorhanden. Erstellen Sie Ihren ersten Raum!</p>';
        return;
    }

    container.innerHTML = rooms.map(room => `
        <div class="room-card">
            <h3>${room.name}</h3>
            <span class="status ${room.is_active ? 'active' : 'inactive'}">
                ${room.is_active ? 'Aktiv' : 'Inaktiv'}
            </span>
            <p>${room.description || 'Keine Beschreibung'}</p>
            <p style="color: #666; font-size: 14px; margin-top: 10px;">
                ⏱️ ${room.time_limit_minutes} Minuten
            </p>
            <div class="actions">
                <button class="btn-success" onclick="toggleRoomStatus(${room.id})">
                    ${room.is_active ? 'Deaktivieren' : 'Aktivieren'}
                </button>
                <button class="btn-secondary" onclick="editRoom(${room.id})">Bearbeiten</button>
                <button class="btn-danger" onclick="deleteRoom(${room.id})">Löschen</button>
            </div>
        </div>
    `).join('');
}

async function toggleRoomStatus(roomId) {
    try {
        await apiRequest(`/api/admin/rooms/${roomId}/activate`, { method: 'POST' });
        loadRooms();
    } catch (error) {
        alert('Fehler beim Ändern des Status');
    }
}

async function deleteRoom(roomId) {
    if (!confirm('Raum wirklich löschen?')) return;

    try {
        await apiRequest(`/api/admin/rooms/${roomId}`, { method: 'DELETE' });
        loadRooms();
    } catch (error) {
        alert('Fehler beim Löschen');
    }
}

// Raum erstellen/bearbeiten
function showCreateRoomModal() {
    showModal('Neuer Raum', `
        <form id="room-form">
            <div class="form-group">
                <label>Raumname</label>
                <input type="text" id="room-name" required>
            </div>
            <div class="form-group">
                <label>Beschreibung</label>
                <textarea id="room-description"></textarea>
            </div>
            <div class="form-group">
                <label>Zeitlimit (Minuten)</label>
                <input type="number" id="room-time" value="60" required>
            </div>
            <button type="submit" class="btn-primary">Raum erstellen</button>
        </form>
    `);

    document.getElementById('room-form').addEventListener('submit', async (e) => {
        e.preventDefault();

        const roomData = {
            name: document.getElementById('room-name').value,
            description: document.getElementById('room-description').value,
            time_limit_minutes: parseInt(document.getElementById('room-time').value)
        };

        try {
            await apiRequest('/api/admin/rooms', {
                method: 'POST',
                body: JSON.stringify(roomData)
            });

            closeModal();
            loadRooms();
        } catch (error) {
            alert('Fehler beim Erstellen des Raums');
        }
    });
}

// Rätsel laden
async function loadPuzzles() {
    try {
        const rooms = await apiRequest('/api/admin/rooms');

        // Room-Select füllen
        const select = document.getElementById('room-select');
        select.innerHTML = '<option value="">Raum auswählen...</option>' +
            rooms.map(r => `<option value="${r.id}">${r.name}</option>`).join('');

        select.addEventListener('change', async (e) => {
            if (e.target.value) {
                const puzzles = await apiRequest(`/api/admin/rooms/${e.target.value}/puzzles`);
                displayPuzzles(puzzles);
            }
        });

    } catch (error) {
        console.error('Fehler:', error);
    }
}

function displayPuzzles(puzzles) {
    const container = document.getElementById('puzzles-list');

    if (puzzles.length === 0) {
        container.innerHTML = '<p style="text-align: center; color: #999;">Keine Rätsel vorhanden.</p>';
        return;
    }

    container.innerHTML = puzzles.map(puzzle => `
        <div class="item-card">
            <div class="item-info">
                <h4>${puzzle.title}</h4>
                <p>Typ: ${puzzle.puzzle_type} | Punkte: ${puzzle.points} | Zeit: ${puzzle.time_limit_seconds}s</p>
            </div>
            <div class="item-actions">
                <button class="btn-secondary" onclick="editPuzzle(${puzzle.id})">Bearbeiten</button>
                <button class="btn-danger" onclick="deletePuzzle(${puzzle.id})">Löschen</button>
            </div>
        </div>
    `).join('');
}

function showCreatePuzzleModal() {
    const roomId = document.getElementById('room-select').value;
    if (!roomId) {
        alert('Bitte wählen Sie zuerst einen Raum aus');
        return;
    }

    showModal('Neues Rätsel', `
        <form id="puzzle-form">
            <div class="form-group">
                <label>Titel</label>
                <input type="text" id="puzzle-title" required>
            </div>
            <div class="form-group">
                <label>Frage</label>
                <textarea id="puzzle-question" required></textarea>
            </div>
            <div class="form-group">
                <label>Antwort 1</label>
                <input type="text" id="answer-0" required>
            </div>
            <div class="form-group">
                <label>Antwort 2</label>
                <input type="text" id="answer-1" required>
            </div>
            <div class="form-group">
                <label>Antwort 3</label>
                <input type="text" id="answer-2" required>
            </div>
            <div class="form-group">
                <label>Antwort 4</label>
                <input type="text" id="answer-3" required>
            </div>
            <div class="form-group">
                <label>Richtige Antwort (0-3)</label>
                <input type="number" id="correct-answer" min="0" max="3" required>
            </div>
            <div class="form-group">
                <label>Punkte</label>
                <input type="number" id="puzzle-points" value="10" required>
            </div>
            <button type="submit" class="btn-primary">Rätsel erstellen</button>
        </form>
    `);

    document.getElementById('puzzle-form').addEventListener('submit', async (e) => {
        e.preventDefault();

        const h5pJson = {
            question: document.getElementById('puzzle-question').value,
            options: [
                document.getElementById('answer-0').value,
                document.getElementById('answer-1').value,
                document.getElementById('answer-2').value,
                document.getElementById('answer-3').value
            ],
            correct: parseInt(document.getElementById('correct-answer').value)
        };

        const puzzleData = {
            room_id: parseInt(roomId),
            title: document.getElementById('puzzle-title').value,
            h5p_json: h5pJson,
            puzzle_type: 'multiple_choice',
            points: parseInt(document.getElementById('puzzle-points').value),
            time_limit_seconds: 300,
            order_index: 0
        };

        try {
            await apiRequest('/api/admin/puzzles', {
                method: 'POST',
                body: JSON.stringify(puzzleData)
            });

            closeModal();
            loadPuzzles();
        } catch (error) {
            alert('Fehler beim Erstellen des Rätsels');
            console.log("Gesendete Daten:", puzzleData)
        }
    });
}

async function deletePuzzle(puzzleId) {
    if (!confirm('Rätsel wirklich löschen?')) return;

    try {
        await apiRequest(`/api/admin/puzzles/${puzzleId}`, { method: 'DELETE' });
        loadPuzzles();
    } catch (error) {
        alert('Fehler beim Löschen');
    }
}

// Schüler laden
async function loadStudents() {
    try {
        const students = await apiRequest('/api/admin/students');
        displayStudents(students);
    } catch (error) {
        console.error('Fehler:', error);
    }
}

function displayStudents(students) {
    const container = document.getElementById('students-list');

    if (students.length === 0) {
        container.innerHTML = '<p style="text-align: center; color: #999;">Keine Schüler vorhanden.</p>';
        return;
    }

    container.innerHTML = students.map(student => `
        <div class="item-card">
            <div class="item-info">
                <h4>${student.full_name || student.username}</h4>
                <p>Benutzername: ${student.username}</p>
            </div>
        </div>
    `).join('');
}

// Modal-Funktionen
function showModal(title, content) {
    document.getElementById('modal-title').textContent = title;
    document.getElementById('modal-body').innerHTML = content;
    document.getElementById('modal-overlay').classList.add('active');
}

function closeModal() {
    document.getElementById('modal-overlay').classList.remove('active');
}