"""Sign-in hardening: login throttling, session expiry, security headers.

Throttling is stored in the database (login_attempts), so it holds across
gunicorn workers and restarts. Failed attempts are counted per email and per
client IP in a sliding window.
"""
from flask import request

from .db import get_db

WINDOW_MIN = 15
MAX_FAILS_PER_EMAIL = 5
MAX_FAILS_PER_IP = 20
MAX_SIGNUPS_PER_IP_HOUR = 20
USER_SESSION_MIN = 30 * 24 * 60
ADMIN_SESSION_MIN = 12 * 60


def client_ip():
    return (request.remote_addr or "unknown")[:64]


def _count(kind, key, minutes):
    row = get_db().execute(
        f"SELECT COUNT(*) AS n FROM login_attempts WHERE kind = ? AND key = ? "
        f"AND created_at > datetime('now', '-{int(minutes)} minutes')",
        (kind, key),
    ).fetchone()
    return row["n"] if row else 0


def record(kind, key):
    db = get_db()
    db.execute("INSERT INTO login_attempts (kind, key) VALUES (?, ?)", (kind, key))
    db.commit()


def clear(kind, key):
    db = get_db()
    db.execute("DELETE FROM login_attempts WHERE kind = ? AND key = ?", (kind, key))
    db.commit()


def login_blocked(email):
    return (
        _count("fail_email", email, WINDOW_MIN) >= MAX_FAILS_PER_EMAIL
        or _count("fail_ip", client_ip(), WINDOW_MIN) >= MAX_FAILS_PER_IP
    )


def record_login_failure(email):
    record("fail_email", email)
    record("fail_ip", client_ip())


def admin_blocked():
    return _count("fail_admin", client_ip(), WINDOW_MIN) >= 5


def record_admin_failure():
    record("fail_admin", client_ip())


def signup_blocked():
    return _count("signup_ip", client_ip(), 60) >= MAX_SIGNUPS_PER_IP_HOUR


def record_signup():
    record("signup_ip", client_ip())


def purge_old():
    db = get_db()
    db.execute("DELETE FROM login_attempts WHERE created_at < datetime('now', '-1440 minutes')")
    db.execute(f"DELETE FROM sessions WHERE created_at < datetime('now', '-{USER_SESSION_MIN} minutes')")
    db.execute(f"DELETE FROM admin_sessions WHERE created_at < datetime('now', '-{ADMIN_SESSION_MIN} minutes')")
    db.commit()


def add_headers(resp):
    h = resp.headers
    h.setdefault("X-Content-Type-Options", "nosniff")
    h.setdefault("X-Frame-Options", "DENY")
    h.setdefault("Referrer-Policy", "no-referrer")
    h.setdefault("Strict-Transport-Security", "max-age=31536000; includeSubDomains")
    h.setdefault("Permissions-Policy", "camera=(), microphone=(), geolocation=()")
    if request.path.startswith("/api/") or request.path == "/admin":
        h["Cache-Control"] = "no-store"
    elif request.path == "/" or request.path.endswith((".js", ".css", ".html")):
        h["Cache-Control"] = "no-cache"
    return resp
