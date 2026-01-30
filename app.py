from flask import Flask, render_template, request, jsonify
import sqlite3
import hashlib
from typing import Optional

app = Flask(__name__)

# ===================== DATABASE (SINGLETON) =====================
class Database:
    _instance = None

    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance.connection = sqlite3.connect(
                "database.db", check_same_thread=False
            )
            cls._instance.connection.row_factory = sqlite3.Row
        return cls._instance

    def cursor(self):
        return self.connection.cursor()

    def commit(self):
        self.connection.commit()


# ===================== PASSWORD UTILS =====================
class PasswordUtils:
    @staticmethod
    def hash_password(password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()

    @staticmethod
    def verify(input_password: str, stored_hash: str) -> bool:
        return PasswordUtils.hash_password(input_password) == stored_hash


# ===================== USER BASE =====================
class User:
    def __init__(self, user_id: str, password: str):
        self.user_id = user_id
        self.password = password

    def login(self):
        raise NotImplementedError


# ===================== STUDENT =====================
class Student(User):
    def __init__(self, student_id: str, year: int, password: str):
        super().__init__(student_id, password)
        self.year = year

    def login(self) -> bool:
        db = Database()
        cur = db.cursor()

        cur.execute("""
            SELECT password FROM students
            WHERE student_id = ? AND year = ?
        """, (self.user_id, self.year))

        row = cur.fetchone()
        return bool(row and PasswordUtils.verify(self.password, row["password"]))


# ===================== TEACHER =====================
class Teacher(User):
    def login(self) -> Optional[dict]:
        db = Database()
        cur = db.cursor()

        cur.execute("""
            SELECT * FROM teachers WHERE teacher_id = ?
        """, (self.user_id,))

        row = cur.fetchone()

        if row and PasswordUtils.verify(self.password, row["password"]):
            return dict(row)

        return None


# ===================== FACTORY =====================
class UserFactory:
    @staticmethod
    def create(role: str, user_id: str, password: str, year: Optional[int] = None):
        if role == "student":
            return Student(user_id, int(year), password)
        elif role == "teacher":
            return Teacher(user_id, password)
        return None


# ===================== AUTH SERVICE =====================
class AuthService:
    @staticmethod
    def authenticate(role, user_id, password, year=None):
        user = UserFactory.create(role, user_id, password, year)
        if not user:
            return None

        return user.login()


# ===================== ROUTES =====================
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    result = AuthService.authenticate(
        role=data.get("role"),
        user_id=data.get("user_id"),
        password=data.get("password"),
        year=data.get("year")
    )

    if not result:
        return jsonify({"success": False}), 401

    # TEACHER LOGIN
    if data.get("role") == "teacher":
        return jsonify({
            "success": True,
            "redirect": "/teacher",
            "teacher": result
        })

    return jsonify({"success": True})


@app.route("/teacher")
def teacher_dashboard():
    # for demo purpose: fetch TEA001
    db = Database()
    cur = db.cursor()
    cur.execute("SELECT * FROM teachers WHERE teacher_id = 'TEA001'")
    teacher = dict(cur.fetchone())

    return render_template(
        "teacher.html",
        teacher_name=teacher["name"],
        department=teacher["department"],
        email=teacher["email"],
        phone=teacher["phone"],
        joining_year=teacher["joining_year"],
        mentor_id=teacher["mentor_id"],
        designation=teacher["designation"]
    )


# ===================== ENTRY =====================
if __name__ == "__main__":
    app.run(debug=True)
