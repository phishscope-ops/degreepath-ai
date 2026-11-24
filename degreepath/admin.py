"""Owner-only admin dashboard API.

Enabled only when ADMIN_PASSWORD is set (env var). Login returns a token
stored in admin_sessions; the dashboard page (static/admin.html) sends it as
a Bearer token. Read-only: the owner can follow registered accounts, nothing
here mutates user data.
"""
import os
import secrets
import time
from datetime import datetime, timezone
from functools import wraps

from flask import Blueprint, current_app, jsonify, request

from . import security
from .db import get_db

bp = Blueprint("admin", __name__, url_prefix="/api/admin")


def _password():
    return current_app.config.get("ADMIN_PASSWORD") or os.environ.get("ADMIN_PASSWORD") or ""


def _is_admin():
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return False
    token = auth[7:].strip()
    if not token:
        return False
    row = get_db().execute(
        "SELECT token FROM admin_sessions WHERE token = ? "
        "AND created_at > datetime('now', '-720 minutes')", (token,)
    ).fetchone()
    return row is not None


def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not _password():
            return jsonify({"error": "لوحة المالك غير مفعّلة"}), 403
        if not _is_admin():
            return jsonify({"error": "غير مصرّح — دي لوحة المالك بس"}), 401
        return fn(*args, **kwargs)

    return wrapper


@bp.post("/login")
def login():
    if not _password():
        return jsonify({"error": "لوحة المالك غير مفعّلة"}), 403
    data = request.get_json(silent=True) or {}
    password = data.get("password") or ""
    if security.admin_blocked():
        return jsonify({"error": "محاولات كتير غلط. استنى 15 دقيقة"}), 429
    if not isinstance(password, str) or not secrets.compare_digest(
        password.encode(), _password().encode()
    ):
        security.record_admin_failure()
        time.sleep(1)  # blunt password guessing
        return jsonify({"error": "كلمة المرور غير صحيحة"}), 401
    token = secrets.token_urlsafe(32)
    db = get_db()
    db.execute("INSERT INTO admin_sessions (token) VALUES (?)", (token,))
    db.commit()
    return jsonify({"token": token})


@bp.post("/logout")
@admin_required
def logout():
    auth = request.headers.get("Authorization", "")
    db = get_db()
    db.execute("DELETE FROM admin_sessions WHERE token = ?", (auth[7:].strip(),))
    db.commit()
    return jsonify({"ok": True})


@bp.get("/overview")
@admin_required
def overview():
    db = get_db()
    users = db.execute(
        """SELECT u.id, u.name, u.email, u.created_at,
                  p.university, p.major, p.study_year,
                  j.title_ar AS target_job, j.title AS target_job_en,
                  (SELECT COUNT(*) FROM courses c WHERE c.user_id = u.id) AS n_courses,
                  (SELECT COUNT(DISTINCT cs.skill_id) FROM course_skills cs
                     JOIN courses c2 ON c2.id = cs.course_id
                    WHERE c2.user_id = u.id) AS n_skills,
                  (SELECT COUNT(*) FROM analyses a WHERE a.user_id = u.id) AS n_analyses
           FROM users u
           LEFT JOIN profiles p ON p.user_id = u.id
           LEFT JOIN jobs j ON j.id = p.target_job_id
           ORDER BY u.id DESC LIMIT 500"""
    ).fetchall()
    by_day = db.execute(
        """SELECT substr(created_at, 1, 10) AS d, COUNT(*) AS c
           FROM users GROUP BY d ORDER BY d DESC LIMIT 30"""
    ).fetchall()
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    stats = {
        "total_users": db.execute("SELECT COUNT(*) AS n FROM users").fetchone()["n"],
        "total_courses": db.execute("SELECT COUNT(*) AS n FROM courses").fetchone()["n"],
        "total_analyses": db.execute("SELECT COUNT(*) AS n FROM analyses").fetchone()["n"],
        "catalog_jobs": db.execute("SELECT COUNT(*) AS n FROM jobs").fetchone()["n"],
        "live_jobs": db.execute("SELECT COUNT(*) AS n FROM live_jobs").fetchone()["n"],
        "signups_today": db.execute(
            "SELECT COUNT(*) AS n FROM users WHERE substr(created_at, 1, 10) = ?", (today,)
        ).fetchone()["n"],
    }
    return jsonify(
        {
            "stats": stats,
            "signups_by_day": [dict(r) for r in by_day],
            "users": [dict(r) for r in users],
        }
    )
