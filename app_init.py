from flask import Flask
from flask_cors import CORS
import os
import sqlite3

app = Flask(__name__)

# Allow Next.js dev servers
CORS(
    app,
    resources={r"/api/*": {"origins": ["http://localhost:3000", "http://127.0.0.1:3000"]}},
    supports_credentials=False,
)


def init_database():
    os.makedirs('images', exist_ok=True)
    con = sqlite3.connect('attendance_app.db', check_same_thread=False)
    cur = con.cursor()
    # Enable foreign keys
    cur.execute("PRAGMA foreign_keys = ON;")

    # Teachers
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS teachers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT UNIQUE,
            password TEXT
        );
        """
    )

    # Students
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT UNIQUE,
            password TEXT,
            encoding BLOB
        );
        """
    )

    # Sessions
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            numberofstudent INTEGER DEFAULT 0,
            startdate TEXT,
            enddate TEXT,
            teacher_id INTEGER,
            FOREIGN KEY (teacher_id) REFERENCES teachers(id) ON DELETE SET NULL
        );
        """
    )

    # Attendance (many-to-many: session x student)
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS attendance (
            session_id INTEGER,
            student_id INTEGER,
            status TEXT,
            checkin_time TEXT,
            PRIMARY KEY (session_id, student_id),
            FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE,
            FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
        );
        """
    )

    con.commit()
    con.close()


# Initialize DB on app import
init_database()