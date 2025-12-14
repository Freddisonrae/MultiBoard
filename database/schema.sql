-- Datenbank-Schema für Multi-Room-Schul-Rätselspiel
-- MariaDB/MySQL

-- Benutzer-Tabelle (Lehrer und Schüler)
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('teacher', 'student') NOT NULL DEFAULT 'student',
    full_name VARCHAR(200),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_username (username),
    INDEX idx_role (role)
) ENGINE=InnoDB;

-- Räume-Tabelle
CREATE TABLE rooms (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    teacher_id INT NOT NULL,
    is_active BOOLEAN DEFAULT FALSE,
    time_limit_minutes INT DEFAULT 60,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (teacher_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_teacher (teacher_id),
    INDEX idx_active (is_active)
) ENGINE=InnoDB;

-- Rätsel/Fragen-Tabelle (H5P-Content)
CREATE TABLE puzzles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    room_id INT NOT NULL,
    title VARCHAR(300) NOT NULL,
    h5p_content_id VARCHAR(100),
    h5p_json TEXT,
    puzzle_type VARCHAR(50) DEFAULT 'multiple_choice',
    order_index INT DEFAULT 0,
    points INT DEFAULT 10,
    time_limit_seconds INT DEFAULT 300,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (room_id) REFERENCES rooms(id) ON DELETE CASCADE,
    INDEX idx_room (room_id),
    INDEX idx_order (room_id, order_index)
) ENGINE=InnoDB;

-- Raum-Zuweisungen (welcher Schüler darf welchen Raum betreten)
CREATE TABLE room_assignments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    room_id INT NOT NULL,
    student_id INT NOT NULL,
    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (room_id) REFERENCES rooms(id) ON DELETE CASCADE,
    FOREIGN KEY (student_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE KEY unique_assignment (room_id, student_id),
    INDEX idx_room (room_id),
    INDEX idx_student (student_id)
) ENGINE=InnoDB;

-- Spiel-Sessions
CREATE TABLE game_sessions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    room_id INT NOT NULL,
    student_id INT NOT NULL,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP NULL,
    total_score INT DEFAULT 0,
    status ENUM('in_progress', 'completed', 'abandoned') DEFAULT 'in_progress',
    FOREIGN KEY (room_id) REFERENCES rooms(id) ON DELETE CASCADE,
    FOREIGN KEY (student_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_room_student (room_id, student_id),
    INDEX idx_status (status)
) ENGINE=InnoDB;

-- Antworten/Ergebnisse
CREATE TABLE puzzle_results (
    id INT AUTO_INCREMENT PRIMARY KEY,
    session_id INT NOT NULL,
    puzzle_id INT NOT NULL,
    answer_json TEXT,
    is_correct BOOLEAN DEFAULT FALSE,
    points_earned INT DEFAULT 0,
    time_taken_seconds INT,
    answered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES game_sessions(id) ON DELETE CASCADE,
    FOREIGN KEY (puzzle_id) REFERENCES puzzles(id) ON DELETE CASCADE,
    INDEX idx_session (session_id),
    INDEX idx_puzzle (puzzle_id)
) ENGINE=InnoDB;

-- Standard-Admin-Benutzer erstellen (Passwort: admin123)
-- Hash für 'admin123' mit bcrypt
INSERT INTO users (username, password_hash, role, full_name) VALUES
('admin', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5UpYqFqYMlEG2', 'teacher', 'Administrator'),
('lehrer1', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5UpYqFqYMlEG2', 'teacher', 'Max Mustermann'),
('schueler1', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5UpYqFqYMlEG2', 'student', 'Anna Schmidt');

-- Beispiel-Raum erstellen
INSERT INTO rooms (name, description, teacher_id, is_active) VALUES
('Mathe-Rätsel Raum 1', 'Grundlegende Mathematik-Rätsel für Klasse 5', 1, TRUE);


-- Beispiel-Rätsel (Multiple Choice)
INSERT INTO puzzles (room_id, title, h5p_json, puzzle_type, order_index, points) VALUES
(1, 'Was ist 5 + 3?', '{"question": "Was ist 5 + 3?", "options": ["6", "7", "8", "9"], "correct": 2}', 'multiple_choice', 1, 10),
(1, 'Was ist 12 - 4?', '{"question": "Was ist 12 - 4?", "options": ["6", "7", "8", "9"], "correct": 2}', 'multiple_choice', 2, 10);

-- Schüler dem Raum zuweisen
INSERT INTO room_assignments (room_id, student_id) VALUES (1, 3);