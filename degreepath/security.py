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
    # one-off cleanup of QA test accounts created during v1.6.1 testing
    db.execute("DELETE FROM users WHERE email = 'qa1x@example.com' OR email LIKE 'q1%@ex.com' OR email LIKE 'qa1%@example.com'")
    db.commit()


_GZ = {}


def _gzip(resp):
    """Compress text responses (the 1.3 MB-free JSON/JS/CSS go over slow mobile links)."""
    import gzip
    if resp.status_code != 200 or "gzip" not in request.headers.get("Accept-Encoding", ""):
        return
    if resp.headers.get("Content-Encoding") or resp.mimetype not in (
            "application/json", "text/html", "text/css", "text/javascript",
            "application/javascript"):
        return
    if resp.direct_passthrough:
        key = (request.path, resp.headers.get("ETag"))
        gz = _GZ.get(key)
        if gz is None:
            resp.direct_passthrough = False
            raw = resp.get_data()
            gz = gzip.compress(raw, 6)
            _GZ[key] = gz
        resp.set_data(gz)
    else:
        raw = resp.get_data()
        if len(raw) < 700:
            return
        resp.set_data(gzip.compress(raw, 5))
    resp.headers["Content-Encoding"] = "gzip"
    resp.headers.add("Vary", "Accept-Encoding")


def add_headers(resp):
    h = resp.headers
    h.setdefault("X-Content-Type-Options", "nosniff")
    h.setdefault("X-Frame-Options", "DENY")
    h.setdefault("Referrer-Policy", "no-referrer")
    h.setdefault("Strict-Transport-Security", "max-age=31536000; includeSubDomains")
    h.setdefault("Permissions-Policy", "camera=(), microphone=(), geolocation=()")
    if request.path.startswith("/api/") or request.path == "/admin":
        h["Cache-Control"] = "no-store"
    elif request.path.endswith((".js", ".css")) and request.args.get("v"):
        # versioned URL (?v=x.y.z): safe to keep for a year, index.html changes the version
        h["Cache-Control"] = "public, max-age=31536000, immutable"
    elif request.path == "/" or request.path.endswith((".js", ".css", ".html")):
        h["Cache-Control"] = "no-cache"
    try:
        _gzip(resp)
    except Exception:
        pass
    return resp
