"""Registration, login, token sessions."""
import re
import secrets
from functools import wraps

from flask import g, jsonify, request
from werkzeug.security import check_password_hash, generate_password_hash

from .db import get_db

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def register_user(email, password, name):
    db = get_db()
    cur = db.execute(
        "INSERT INTO users (email, password_hash, name) VALUES (?, ?, ?)",
        (email, generate_password_hash(password), name),
    )
    uid = cur.lastrowid
    db.execute("INSERT INTO profiles (user_id) VALUES (?)", (uid,))
    db.commit()
    return uid


def create_session(user_id):
    db = get_db()
    token = secrets.token_urlsafe(32)
    db.execute("INSERT INTO sessions (token, user_id) VALUES (?, ?)", (token, user_id))
    db.commit()
    return token


def current_user():
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return None
    token = auth[7:].strip()
    db = get_db()
    row = db.execute(
        """SELECT u.id, u.email, u.name FROM sessions s
           JOIN users u ON u.id = s.user_id WHERE s.token = ?""",
        (token,),
    ).fetchone()
    return dict(row) if row else None


def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        user = current_user()
        if user is None:
            return jsonify({"error": "يجب تسجيل الدخول أولاً"}), 401
        g.user = user
        return fn(*args, **kwargs)

    return wrapper


def validate_credentials(email, password, name=None):
    if not EMAIL_RE.match(email or ""):
        return "البريد الإلكتروني غير صالح"
    if not password or len(password) < 6:
        return "كلمة المرور لازم تكون 6 أحرف على الأقل"
    if name is not None and not name.strip():
        return "الاسم مطلوب"
    return None
