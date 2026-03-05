import sqlite3
import hashlib
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "data" / "study_companion.db"

def _get_connection():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn

def _hash_password(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

def initialize_database():
    conn = _get_connection()
    c = conn.cursor()
    c.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            role TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            keywords TEXT,
            upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS roadmaps (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic TEXT NOT NULL,
            roadmap TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            roadmap_id INTEGER NOT NULL,
            rating INTEGER NOT NULL,
            comment TEXT
        );
    """)
    if c.execute("SELECT COUNT(*) FROM users").fetchone()[0] == 0:
        c.executemany("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", [
            ("admin", _hash_password("admin123"), "admin"),
            ("student", _hash_password("student123"), "student")
        ])
    conn.commit()
    conn.close()

def save_document(filename, keywords=None):
    conn = _get_connection()
    c = conn.cursor()
    c.execute("INSERT INTO documents (filename, keywords) VALUES (?, ?)", (filename, keywords))
    conn.commit()
    conn.close()

def save_roadmap(topic, roadmap):
    conn = _get_connection()
    c = conn.cursor()
    c.execute("INSERT INTO roadmaps (topic, roadmap) VALUES (?, ?)", (topic, roadmap))
    conn.commit()
    res = c.lastrowid
    conn.close()
    return res

def save_feedback(roadmap_id, rating, comment):
    conn = _get_connection()
    c = conn.cursor()
    c.execute("INSERT INTO feedback (roadmap_id, rating, comment) VALUES (?, ?, ?)", (roadmap_id, rating, comment))
    conn.commit()
    conn.close()

def get_roadmaps():
    conn = _get_connection()
    rows = conn.execute("SELECT * FROM roadmaps ORDER BY created_at DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_feedback():
    conn = _get_connection()
    rows = conn.execute("""
        SELECT f.*, r.topic 
        FROM feedback f 
        JOIN roadmaps r ON f.roadmap_id = r.id 
        ORDER BY f.id DESC
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_documents():
    conn = _get_connection()
    rows = conn.execute("SELECT * FROM documents ORDER BY upload_time DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_user_count():
    conn = _get_connection()
    count = conn.execute("SELECT COUNT(*) FROM users WHERE role = 'student'").fetchone()[0]
    conn.close()
    return count

def update_document_keywords(filename, keywords):
    conn = _get_connection()
    conn.execute("UPDATE documents SET keywords = ? WHERE filename = ?", (keywords, filename))
    conn.commit()
    conn.close()

def register_user(u, p, r="student"):
    """Register a new user with hashed password."""
    try:
        conn = _get_connection()
        c = conn.cursor()
        c.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", (u, _hash_password(p), r))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False

def validate_user(u, p):
    conn = _get_connection()
    row = conn.execute("SELECT id, username, role FROM users WHERE username = ? AND password = ?", (u, _hash_password(p))).fetchone()
    conn.close()
    return dict(row) if row else None
