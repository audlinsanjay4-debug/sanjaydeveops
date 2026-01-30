import sqlite3
import hashlib

# ================= PASSWORD HASH (STANDARD LIB ONLY) =================
def generate_password_hash(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


conn = sqlite3.connect("database.db")
cursor = conn.cursor()

# ================= DROP OLD TABLES (DEV ONLY) =================
cursor.execute("DROP TABLE IF EXISTS students")
cursor.execute("DROP TABLE IF EXISTS teachers")

# ================= STUDENTS TABLE =================
cursor.execute("""
CREATE TABLE students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id TEXT UNIQUE NOT NULL,
    year INTEGER NOT NULL CHECK(year BETWEEN 1 AND 4),
    password TEXT NOT NULL,
    name TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

# ================= TEACHERS TABLE =================
cursor.execute("""
CREATE TABLE teachers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    teacher_id TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    name TEXT NOT NULL,
    department TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    phone TEXT,
    joining_year INTEGER,
    mentor_id TEXT,
    profile_photo TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

# ================= DUMMY STUDENTS =================
students = [
    ("STU001", 1, generate_password_hash("student123"), "Alice"),
    ("STU002", 2, generate_password_hash("student123"), "Bob"),
    ("STU003", 3, generate_password_hash("student123"), "Charlie"),
]

cursor.executemany("""
INSERT INTO students (student_id, year, password, name)
VALUES (?, ?, ?, ?)
""", students)

# ================= DUMMY TEACHERS =================
teachers = [
    (
        "TEA001",
        generate_password_hash("teacher123"),
        "Ms. Johnson",
        "Computer Science",
        "johnson@college.edu",
        "+91 9876543210",
        2018,
        "TEA000",
        "https://cdn-icons-png.flaticon.com/512/194/194935.png"
    ),
    (
        "TEA002",
        generate_password_hash("teacher123"),
        "Mr. Smith",
        "Information Technology",
        "smith@college.edu",
        "+91 9123456780",
        2016,
        None,
        "https://cdn-icons-png.flaticon.com/512/194/194937.png"
    )
]

cursor.executemany("""
INSERT INTO teachers (
    teacher_id, password, name, department,
    email, phone, joining_year, mentor_id, profile_photo
)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
""", teachers)

conn.commit()
conn.close()

print("✅ Database recreated and initialized successfully (no external libraries).")
