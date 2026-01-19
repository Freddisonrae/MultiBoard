// Admin-Panel JavaScript - MultiBoard mit H5P Support
const API_BASE = window.location.origin;
let authToken = null;
let currentUser = null;
let currentRoomId = null;

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

    // Dashboard-Event-Listeners
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

    // H5P Upload Button
    const uploadH5pBtn = document.getElementById('upload-h5p-btn');
    if (uploadH5pBtn) {
        uploadH5pBtn.addEventListener('click', showH5PUploadModal);
    }

    // Schüler erstellen Button - FIXED
    const createStudentBtn = document.getElementById('create-student-btn');
    if (createStudentBtn) {
        createStudentBtn.addEventListener('click', showCreateStudentModal);
    }

    const modalClose = document.getElementById('modal-close');
    if (modalClose) {
        modalClose.addEventListener('click', closeModal);
    }

    // H5P Preview Modal schließen
    const h5pPreviewClose = document.getElementById('h5p-preview-close');
    if (h5pPreviewClose) {
        h5pPreviewClose.addEventListener('click', closeH5PPreview);
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
    document.querySelectorAll('.auth-tab').forEach(t => t.classList.remove('active'));
    document.querySelector(`[data-mode="${mode}"]`).classList.add('active');
    document.querySelectorAll('.auth-form').forEach(f => f.classList.remove('active'));
    document.getElementById(`${mode}-form`).classList.add('active');
    hideMessage();
}

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

        authToken = data.access_token;
        currentUser = data.user;

        localStorage.setItem('authToken', authToken);
        localStorage.setItem('currentUser', JSON.stringify(currentUser));

        showMessage('Anmeldung erfolgreich! Lade Dashboard...', 'success');

        setTimeout(() => {
            showDashboard();
            loadRooms();
        }, 500);

    } catch (error) {
        console.error('Login error:', error);
        showMessage('Verbindungsfehler. Bitte prüfen Sie Ihre Internetverbindung.', 'error');
    }
}

async function handleRegister(e) {
    e.preventDefault();
    const username = document.getElementById('reg-username').value.trim();
    const fullname = document.getElementById('reg-fullname').value.trim();
    const password = document.getElementById('reg-password').value;
    const password2 = document.getElementById('reg-password2').value;

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

        showMessage(
            '✅ Registrierung erfolgreich! Sie können sich jetzt anmelden.',
            'success'
        );

        document.getElementById('register-form').reset();

        setTimeout(() => {
            switchAuthMode('login');
        }, 3000);

    } catch (error) {
        console.error('Register error:', error);
        showMessage('Verbindungsfehler. Bitte prüfen Sie Ihre Internetverbindung.', 'error');
    }
}

function showMessage(text, type) {
    const msg = document.getElementById('auth-message');
    msg.textContent = text;
    msg.className = `message ${type} visible`;
}

function hideMessage() {
    const msg = document.getElementById('auth-message');
    msg.className = 'message';
}

function handleLogout() {
    authToken = null;
    currentUser = null;
    localStorage.removeItem('authToken');
    localStorage.removeItem('currentUser');

    document.getElementById('auth-container').style.display = 'block';
    document.getElementById('dashboard-container').style.display = 'none';

    document.getElementById('login-form').reset();
    document.getElementById('register-form').reset();
    switchAuthMode('login');
}

function showDashboard() {
    document.getElementById('auth-container').style.display = 'none';
    document.getElementById('dashboard-container').style.display = 'block';
    document.getElementById('user-name').textContent = currentUser.full_name || currentUser.username;
}

async function apiRequest(endpoint, options = {}) {
    const headers = {
        ...options.headers
    };

    // Content-Type NUR wenn kein FormData
    if (!(options.body instanceof FormData)) {
        headers['Content-Type'] = 'application/json';
    }

    if (authToken) {
        headers['Authorization'] = `Bearer ${authToken}`;
    }

    const response = await fetch(`${API_BASE}${endpoint}`, {
        ...options,
        headers
    });

    if (!response.ok) {
        const error = await response.text();
        throw new Error(`API Error: ${response.status}`);
    }

    return response.json();
}

function switchTab(tabName) {
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(tc => tc.classList.remove('active'));

    document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');
    document.getElementById(`${tabName}-tab`).classList.add('active');

    if (tabName === 'rooms') loadRooms();
    else if (tabName === 'puzzles') loadPuzzles();
    else if (tabName === 'students') loadStudents();
}

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

// H5P Upload Modal
function showH5PUploadModal() {
    const roomId = document.getElementById('room-select').value;
    if (!roomId) {
        alert('Bitte wählen Sie zuerst einen Raum aus');
        return;
    }

    currentRoomId = roomId;

    showModal('H5P-Datei hochladen', `
        <div class="h5p-upload-info">
            <p>📤 Laden Sie eine .h5p Datei hoch</p>
            <p style="font-size: 14px; color: #666;">
                H5P-Dateien können Sie von <a href="https://h5p.org" target="_blank">h5p.org</a> herunterladen
                oder mit dem H5P-Editor erstellen.
            </p>
        </div>

        <form id="h5p-upload-form" enctype="multipart/form-data">
            <div class="form-group">
                <label>H5P-Datei auswählen (.h5p)</label>
                <input type="file" id="h5p-file" accept=".h5p" required>
            </div>

            <div id="upload-progress" style="display: none;">
                <div class="progress-bar">
                    <div class="progress-fill" id="progress-fill"></div>
                </div>
                <p id="upload-status">Hochladen...</p>
            </div>

            <button type="submit" class="btn-primary" id="upload-submit-btn">Hochladen & Vorschau</button>
        </form>
    `);

    document.getElementById('h5p-upload-form').addEventListener('submit', handleH5PUpload);
}

async function handleH5PUpload(e) {
    e.preventDefault();

    const fileInput = document.getElementById('h5p-file');
    const file = fileInput.files[0];

    if (!file) {
        alert('Bitte wählen Sie eine Datei aus');
        return;
    }

    if (!file.name.endsWith('.h5p')) {
        alert('Bitte wählen Sie eine .h5p Datei');
        return;
    }

    // Upload UI zeigen
    document.getElementById('upload-progress').style.display = 'block';
    document.getElementById('upload-submit-btn').disabled = true;

    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await fetch(
            `${API_BASE}/api/admin/h5p/upload?room_id=${currentRoomId}`,
            {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${authToken}`
                },
                body: formData
            }
        );

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Upload fehlgeschlagen');
        }

        const result = await response.json();

        document.getElementById('upload-status').textContent = 'Upload erfolgreich!';

        // Modal schließen und Puzzle-Liste neu laden
        setTimeout(() => {
            closeModal();
            loadPuzzles();

            // H5P-Vorschau zeigen
            showH5PPreview(result.content_id);
        }, 1000);

    } catch (error) {
        console.error('Upload error:', error);
        document.getElementById('upload-status').textContent = '❌ ' + error.message;
        document.getElementById('upload-submit-btn').disabled = false;
    }
}

// H5P Vorschau anzeigen
function showH5PPreview(contentId) {
    const overlay = document.getElementById('h5p-preview-overlay');
    const container = document.getElementById('h5p-preview-container');

    overlay.classList.add('active');

    // H5P Standalone initialisieren
    container.innerHTML = ''; // Clear previous content

    const h5pContainer = document.createElement('div');
    h5pContainer.className = 'h5p-standalone';
    container.appendChild(h5pContainer);

    new H5PStandalone.H5P(h5pContainer, {
        h5pJsonPath: `/static/h5p-content/${contentId}`,
        frameJs: '/static/h5p-standalone/dist/frame.bundle.js',
        frameCss: '/static/h5p-standalone/dist/styles/h5p.css',
    });
}

function closeH5PPreview() {
    const overlay = document.getElementById('h5p-preview-overlay');
    overlay.classList.remove('active');

    // Container leeren
    document.getElementById('h5p-preview-container').innerHTML = '';
}

async function loadPuzzles() {
    try {
        const rooms = await apiRequest('/api/admin/rooms');

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
                <p>
                    Typ: ${puzzle.puzzle_type} |
                    Punkte: ${puzzle.points} |
                    Zeit: ${puzzle.time_limit_seconds}s
                    ${puzzle.h5p_content_id ? ' |  H5P-Interaktiv' : ''}
                </p>
            </div>
            <div class="item-actions">
                ${puzzle.h5p_content_id ?
                    `<button class="btn-secondary" onclick="showH5PPreview('${puzzle.h5p_content_id}')">👁️ Vorschau</button>`
                    : ''}
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

    showModal('Neues Rätsel (Manuell)', `
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
            <div class="item-actions">
                <button class="btn-danger" onclick="deleteStudent(${student.id})">Löschen</button>
            </div>
        </div>
    `).join('');
}

// NEUE FUNKTION: Schüler erstellen Modal
function showCreateStudentModal() {
    showModal('Neuer Schüler', `
        <form id="student-form">
            <div class="form-group">
                <label>Benutzername</label>
                <input type="text" id="student-username" required minlength="3">
                <small>Mindestens 3 Zeichen</small>
            </div>
            <div class="form-group">
                <label>Vollständiger Name</label>
                <input type="text" id="student-fullname" required>
            </div>
            <div class="form-group">
                <label>Passwort</label>
                <input type="password" id="student-password" required minlength="8">
                <small>Mindestens 8 Zeichen</small>
            </div>
            <button type="submit" class="btn-primary">Schüler erstellen</button>
        </form>
    `);

    document.getElementById('student-form').addEventListener('submit', async (e) => {
        e.preventDefault();

        const studentData = {
            username: document.getElementById('student-username').value.trim(),
            password: document.getElementById('student-password').value,
            role: 'student',
            full_name: document.getElementById('student-fullname').value.trim()
        };

        try {
            await apiRequest('/api/auth/register', {
                method: 'POST',
                body: JSON.stringify(studentData)
            });

            closeModal();
            loadStudents();
            alert('Schüler erfolgreich erstellt!');
        } catch (error) {
            alert('Fehler beim Erstellen des Schülers');
        }
    });
}

// NEUE FUNKTION: Schüler löschen
async function deleteStudent(studentId) {
    if (!confirm('Schüler wirklich löschen?')) return;

    try {
        await apiRequest(`/api/admin/students/${studentId}`, { method: 'DELETE' });
        loadStudents();
    } catch (error) {
        alert('Fehler beim Löschen');
    }
}

function showModal(title, content) {
    document.getElementById('modal-title').textContent = title;
    document.getElementById('modal-body').innerHTML = content;
    document.getElementById('modal-overlay').classList.add('active');
}

function closeModal() {
    document.getElementById('modal-overlay').classList.remove('active');
}