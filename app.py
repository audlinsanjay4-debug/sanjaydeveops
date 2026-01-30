from flask import Flask, render_template, request, jsonify
import sqlite3
import hashlib
from typing import Optional

app = Flask(__name__)


# ===================== DATABASE (SINGLETON) =====================
class Database:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
            cls._instance.connection = sqlite3.connect(
                "database.db", check_same_thread=False
            )
        return cls._instance

    def get_cursor(self):
        return self.connection.cursor()

    def commit(self):
        self.connection.commit()


# ===================== PASSWORD UTILS =====================
class PasswordUtils:
    @staticmethod
    def hash_password(password: str) -> str:
        return hashlib.sha256(password.encode("utf-8")).hexdigest()

    @staticmethod
    def verify_password(input_password: str, stored_hash: str) -> bool:
        return PasswordUtils.hash_password(input_password) == stored_hash


# ===================== USER BASE CLASS =====================
class User:
    def __init__(self, user_id: str, password: str):
        self.user_id = user_id
        self.password = password

    def login(self) -> bool:
        raise NotImplementedError


# ===================== STUDENT CLASS =====================
class Student(User):
    def __init__(self, student_id: str, year: int, password: str):
        super().__init__(student_id, password)
        self.year = year

    def login(self) -> bool:
        db = Database()
        cursor = db.get_cursor()

        cursor.execute("""
            SELECT password FROM students
            WHERE student_id = ? AND year = ?
        """, (self.user_id, self.year))

        result = cursor.fetchone()
        return bool(result and PasswordUtils.verify_password(self.password, result[0]))


# ===================== TEACHER CLASS =====================
class Teacher(User):
    def __init__(self, teacher_id: str, password: str):
        super().__init__(teacher_id, password)

    def login(self) -> bool:
        db = Database()
        cursor = db.get_cursor()

        cursor.execute("""
            SELECT password FROM teachers
            WHERE teacher_id = ?
        """, (self.user_id,))

        result = cursor.fetchone()
        return bool(result and PasswordUtils.verify_password(self.password, result[0]))


# ===================== AUTH SERVICE =====================
class AuthService:
    @staticmethod
    def authenticate(
        role: str,
        user_id: str,
        password: str,
        year: Optional[int] = None
    ) -> bool:

        if role == "student":
            user = Student(user_id, int(year), password)
        elif role == "teacher":
            user = Teacher(user_id, password)
        else:
            return False

        return user.login()


# ===================== ROUTES =====================
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    role = data.get("role")
    user_id = data.get("user_id")
    password = data.get("password")
    year = data.get("year")

    success = AuthService.authenticate(role, user_id, password, year)

    if success:
        return jsonify({"success": True, "message": "Login successful"})
    else:
        return jsonify({"success": False, "message": "Invalid credentials"}), 401


# ===================== ENTRY POINT =====================
if __name__ == "__main__":
    app.run(debug=True)
