"""Database layer for DegreePath AI.

SQLite locally (file path in config["DATABASE"]), Postgres (Neon) when the
config holds a postgres:// DSN (env DATABASE_URL). The rest of the app keeps
writing sqlite-style SQL with "?" placeholders; the Postgres wrapper below
translates the small dialect differences.
"""
import re
import sqlite3

from flask import current_app, g

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    name TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS sessions (
    token TEXT PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS admin_sessions (
    token TEXT PRIMARY KEY,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS skills (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    name_ar TEXT DEFAULT '',
    category TEXT DEFAULT 'general'
);

CREATE TABLE IF NOT EXISTS skill_aliases (
    alias TEXT NOT NULL,
    skill_id INTEGER NOT NULL REFERENCES skills(id) ON DELETE CASCADE,
    PRIMARY KEY (alias, skill_id)
);

CREATE TABLE IF NOT EXISTS jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL UNIQUE,
    title_ar TEXT DEFAULT '',
    description TEXT DEFAULT '',
    category TEXT DEFAULT ''
);

CREATE TABLE IF NOT EXISTS job_skills (
    job_id INTEGER NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
    skill_id INTEGER NOT NULL REFERENCES skills(id),
    importance INTEGER NOT NULL DEFAULT 2,
    PRIMARY KEY (job_id, skill_id)
);

CREATE TABLE IF NOT EXISTS profiles (
    user_id INTEGER PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    university TEXT DEFAULT '',
    major TEXT DEFAULT '',
    study_year TEXT DEFAULT '',
    target_job_id INTEGER REFERENCES jobs(id)
);

CREATE TABLE IF NOT EXISTS courses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    kind TEXT NOT NULL DEFAULT 'course',
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS course_skills (
    course_id INTEGER NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
    skill_id INTEGER NOT NULL REFERENCES skills(id),
    PRIMARY KEY (course_id, skill_id)
);

CREATE TABLE IF NOT EXISTS resources (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    skill_id INTEGER NOT NULL REFERENCES skills(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    url TEXT NOT NULL,
    kind TEXT DEFAULT 'course'
);

CREATE TABLE IF NOT EXISTS course_catalog (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    level INTEGER NOT NULL,
    semester INTEGER NOT NULL,
    description TEXT DEFAULT ''
);

CREATE TABLE IF NOT EXISTS analyses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    job_id INTEGER NOT NULL REFERENCES jobs(id),
    match_pct REAL NOT NULL,
    matched TEXT NOT NULL DEFAULT '[]',
    missing TEXT NOT NULL DEFAULT '[]',
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS live_jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source TEXT NOT NULL,
    ext_id TEXT NOT NULL,
    title TEXT NOT NULL,
    company TEXT DEFAULT '',
    location TEXT DEFAULT '',
    remote INTEGER NOT NULL DEFAULT 0,
    url TEXT NOT NULL,
    description TEXT DEFAULT '',
    posted_at TEXT DEFAULT '',
    fetched_at TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE (source, ext_id)
);

CREATE TABLE IF NOT EXISTS live_job_skills (
    job_id INTEGER NOT NULL REFERENCES live_jobs(id) ON DELETE CASCADE,
    skill_id INTEGER NOT NULL REFERENCES skills(id),
    importance INTEGER NOT NULL DEFAULT 2,
    PRIMARY KEY (job_id, skill_id)
);

CREATE TABLE IF NOT EXISTS live_courses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source TEXT NOT NULL,
    ext_id TEXT NOT NULL,
    title TEXT NOT NULL,
    summary TEXT DEFAULT '',
    url TEXT NOT NULL,
    level TEXT DEFAULT '',
    duration_min INTEGER DEFAULT 0,
    fetched_at TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE (source, ext_id)
);

CREATE TABLE IF NOT EXISTS live_course_skills (
    course_id INTEGER NOT NULL REFERENCES live_courses(id) ON DELETE CASCADE,
    skill_id INTEGER NOT NULL REFERENCES skills(id),
    PRIMARY KEY (course_id, skill_id)
);

CREATE TABLE IF NOT EXISTS feed_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    started_at TEXT NOT NULL,
    finished_at TEXT,
    report TEXT NOT NULL DEFAULT '{}'
);
"""

# Tables with an integer "id" primary key. INSERTs into these get a RETURNING
# clause on Postgres so cursor.lastrowid keeps working like sqlite3.
_ID_TABLES = {
    "users", "courses", "jobs", "skills", "resources", "course_catalog",
    "analyses", "live_jobs", "live_courses", "feed_runs",
}

_DT_NOW = "to_char(now(), 'YYYY-MM-DD HH24:MI:SS')"


def is_pg_dsn(dsn):
    return isinstance(dsn, str) and dsn.startswith(("postgres://", "postgresql://"))


def is_unique_violation(exc):
    """True for sqlite3.IntegrityError and psycopg2 UniqueViolation."""
    if isinstance(exc, sqlite3.IntegrityError):
        return True
    return exc.__class__.__name__ == "UniqueViolation"


def _pg_sql(sql):
    """Translate our sqlite-dialect SQL to Postgres. Returns None to skip."""
    s = sql.strip()
    if not s:
        return None
    if s.upper().startswith("PRAGMA"):
        return None
    s = re.sub(
        r"datetime\('now',\s*'-(\d+)\s*minutes'\)",
        r"to_char(now() - interval '\1 minutes', 'YYYY-MM-DD HH24:MI:SS')",
        s,
    )
    s = s.replace("datetime('now')", _DT_NOW)
    s = s.replace(
        "INTEGER PRIMARY KEY AUTOINCREMENT",
        "INTEGER GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY",
    )
    if s.upper().startswith("INSERT OR IGNORE INTO"):
        s = "INSERT INTO" + s[len("INSERT OR IGNORE INTO"):]
        s = s.rstrip().rstrip(";") + " ON CONFLICT DO NOTHING"
    if s.upper() == "BEGIN IMMEDIATE":
        s = "BEGIN"
    m = re.match(r"(?is)^INSERT\s+INTO\s+(\w+)", s)
    if m and m.group(1).lower() in _ID_TABLES and "RETURNING" not in s.upper():
        s = s.rstrip().rstrip(";") + " RETURNING id"
    s = s.replace("?", "%s")
    return s


class _NullCursor:
    lastrowid = None
    rowcount = 0

    def __iter__(self):
        return iter([])

    def fetchone(self):
        return None

    def fetchall(self):
        return []


class _PgCursor:
    def __init__(self, cur, lastrowid=None):
        self._cur = cur
        self.lastrowid = lastrowid

    def __iter__(self):
        return iter(self._cur)

    @property
    def rowcount(self):
        return self._cur.rowcount

    def fetchone(self):
        return self._cur.fetchone()

    def fetchall(self):
        return self._cur.fetchall()


class _PgConn:
    """Minimal psycopg2 connection wrapper matching the sqlite3 API we use."""

    def __init__(self, raw):
        self._raw = raw

    def execute(self, sql, params=()):
        translated = _pg_sql(sql)
        if translated is None:
            return _NullCursor()
        cur = self._raw.cursor()
        cur.execute(translated, params)
        lastrowid = None
        if "RETURNING id" in translated:
            row = cur.fetchone()
            lastrowid = row["id"] if row else None
        return _PgCursor(cur, lastrowid)

    def executescript(self, script):
        for stmt in script.split(";"):
            self.execute(stmt)

    def commit(self):
        self._raw.commit()

    def rollback(self):
        self._raw.rollback()

    def close(self):
        self._raw.close()


def _with_ssl(dsn):
    if "sslmode=" in dsn:
        return dsn
    return dsn + ("&" if "?" in dsn else "?") + "sslmode=require"


def connect_dsn(dsn):
    """Open a standalone connection (used by the feed's background thread)."""
    if is_pg_dsn(dsn):
        import psycopg2
        import psycopg2.extras

        return _PgConn(
            psycopg2.connect(_with_ssl(dsn), cursor_factory=psycopg2.extras.RealDictCursor)
        )
    db = sqlite3.connect(dsn, timeout=60)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA journal_mode=WAL")
    db.execute("PRAGMA busy_timeout=60000")
    db.execute("PRAGMA foreign_keys = ON")
    return db


def get_db():
    """One connection per request. On Postgres a fresh connect per request is
    deliberate: Neon scales to zero when idle, which drops pooled connections."""
    if "db" not in g:
        dsn = current_app.config["DATABASE"]
        if is_pg_dsn(dsn):
            g.db = connect_dsn(dsn)
        else:
            g.db = sqlite3.connect(dsn, timeout=60)
            g.db.row_factory = sqlite3.Row
            g.db.execute("PRAGMA busy_timeout = 60000")
            g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def close_db(_exc=None):
    db = g.pop("db", None)
    if db is None:
        return
    if isinstance(db, _PgConn):
        try:
            db.rollback()
        except Exception:
            pass
    db.close()


def _table_columns(db, table):
    if isinstance(db, _PgConn):
        rows = db.execute(
            "SELECT column_name AS name FROM information_schema.columns WHERE table_name = %s",
            (table,),
        ).fetchall()
    else:
        rows = db.execute(f"PRAGMA table_info({table})").fetchall()
    return {r["name"] for r in rows}


def init_db(app):
    with app.app_context():
        db = get_db()
        if isinstance(db, _PgConn):
            db.executescript(SCHEMA)
        else:
            db.execute("PRAGMA journal_mode=WAL")
            db.executescript(SCHEMA)
        for table, col, ddl in (("live_jobs", "field", "TEXT DEFAULT 'other'"),
                                ("live_jobs", "country", "TEXT DEFAULT ''"),
                                ("live_courses", "field", "TEXT DEFAULT 'other'")):
            if col not in _table_columns(db, table):
                db.execute(f"ALTER TABLE {table} ADD COLUMN {col} {ddl}")
        db.commit()
        from .seed import seed_if_empty

        seed_if_empty(db)


def init_app(app):
    app.teardown_appcontext(close_db)
