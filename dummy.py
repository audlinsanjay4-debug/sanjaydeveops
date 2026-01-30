import sqlite3
import hashlib

# ---------------- PASSWORD HASHING ----------------
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


# ---------------- DB CONNECTION ----------------
conn = sqlite3.connect("database.db")
cursor = conn.cursor()

# ---------------- STUDENT TABLE ----------------
cursor.execute("""
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id TEXT UNIQUE NOT NULL,
    year INTEGER NOT NULL,
    password TEXT NOT NULL,
    name TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

# ---------------- TEACHER TABLE ----------------
cursor.execute("""
CREATE TABLE IF NOT EXISTS teachers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    teacher_id TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    name TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

# ---------------- DUMMY DATA ----------------
students = [
    ("STU001", 1, hash_password("student123"), "Alice"),
    ("STU002", 2, hash_password("student123"), "Bob"),
    ("STU003", 3, hash_password("student123"), "Charlie"),
]

teachers = [
    ("TEA001", hash_password("teacher123"), "Mr. Smith"),
    ("TEA002", hash_password("teacher123"), "Ms. Johnson"),
]

cursor.executemany("""
INSERT OR IGNORE INTO students (student_id, year, password, name)
VALUES (?, ?, ?, ?)
""", students)

cursor.executemany("""
INSERT OR IGNORE INTO teachers (teacher_id, password, name)
VALUES (?, ?, ?)
""", teachers)

conn.commit()
conn.close()

print("Database initialized with dummy data successfully.")
