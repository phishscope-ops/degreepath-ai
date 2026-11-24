"""Registration, login, token sessions."""
import re
import secrets
from functools import wraps

import time

from flask import current_app, g, jsonify, request
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


_SESS = {}
_SESS_TTL = 20  # seconds a verified session is trusted without asking the database


def forget_token(token):
    _SESS.pop(token, None)


def current_user():
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return None
    token = auth[7:].strip()
    use_cache = not current_app.config.get("TESTING")
    if use_cache:
        hit = _SESS.get(token)
        if hit and hit[0] > time.time():
            return dict(hit[1])
    db = get_db()
    row = db.execute(
        """SELECT u.id, u.email, u.name FROM sessions s
           JOIN users u ON u.id = s.user_id WHERE s.token = ?
           AND s.created_at > datetime('now', '-43200 minutes')""",
        (token,),
    ).fetchone()
    if row and use_cache:
        if len(_SESS) > 5000:
            _SESS.clear()
        _SESS[token] = (time.time() + _SESS_TTL, dict(row))
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
    if len(email or "") > 254:
        return "البريد الإلكتروني غير صالح"
    if not password or len(password) < 8:
        return "كلمة المرور لازم تكون 8 أحرف على الأقل"
    if len(password) > 128:
        return "كلمة المرور طويلة جداً"
    if name is not None and not name.strip():
        return "الاسم مطلوب"
    if name is not None and len(name) > 100:
        return "الاسم طويل جداً"
    return None
