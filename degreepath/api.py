"""REST API blueprint."""
import json
import sqlite3

from flask import Blueprint, g, jsonify, request
from werkzeug.security import check_password_hash

from . import matching, nlp
from .auth import (
    create_session,
    current_user,
    login_required,
    register_user,
    validate_credentials,
)
from .db import get_db

bp = Blueprint("api", __name__, url_prefix="/api")


@bp.post("/register")
def register():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    name = (data.get("name") or "").strip()
    err = validate_credentials(email, password, name)
    if err:
        return jsonify({"error": err}), 400
    try:
        uid = register_user(email, password, name)
    except sqlite3.IntegrityError:
        return jsonify({"error": "البريد ده مسجل قبل كده، جرّب تسجيل الدخول"}), 409
    return jsonify({"token": create_session(uid), "user": {"id": uid, "email": email, "name": name}}), 201


@bp.post("/login")
def login():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    db = get_db()
    row = db.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
    if row is None or not check_password_hash(row["password_hash"], password):
        return jsonify({"error": "البريد أو كلمة المرور غير صحيحة"}), 401
    token = create_session(row["id"])
    return jsonify({"token": token, "user": {"id": row["id"], "email": row["email"], "name": row["name"]}})


@bp.post("/logout")
@login_required
def logout():
    auth = request.headers.get("Authorization", "")
    get_db().execute("DELETE FROM sessions WHERE token = ?", (auth[7:].strip(),))
    get_db().commit()
    return jsonify({"ok": True})


@bp.get("/me")
def me():
    user = current_user()
    if user is None:
        return jsonify({"error": "يجب تسجيل الدخول أولاً"}), 401
    return jsonify({"user": user})


@bp.get("/profile")
@login_required
def get_profile():
    db = get_db()
    row = db.execute(
        """SELECT p.*, j.title AS target_job_title, j.title_ar AS target_job_title_ar
           FROM profiles p LEFT JOIN jobs j ON j.id = p.target_job_id
           WHERE p.user_id = ?""",
        (g.user["id"],),
    ).fetchone()
    return jsonify({"profile": dict(row) if row else {}})


@bp.put("/profile")
@login_required
def put_profile():
    data = request.get_json(silent=True) or {}
    db = get_db()
    target = data.get("target_job_id")
    if target is not None:
        exists = db.execute("SELECT 1 FROM jobs WHERE id = ?", (target,)).fetchone()
        if not exists:
            return jsonify({"error": "الوظيفة المستهدفة غير موجودة"}), 400
    db.execute(
        """INSERT INTO profiles (user_id, university, major, study_year, target_job_id)
           VALUES (?, ?, ?, ?, ?)
           ON CONFLICT(user_id) DO UPDATE SET
             university=excluded.university, major=excluded.major,
             study_year=excluded.study_year, target_job_id=excluded.target_job_id""",
        (
            g.user["id"],
            (data.get("university") or "").strip(),
            (data.get("major") or "").strip(),
            (data.get("study_year") or "").strip(),
            target,
        ),
    )
    db.commit()
    return get_profile()


@bp.get("/courses")
@login_required
def list_courses():
    db = get_db()
    courses = db.execute(
        "SELECT * FROM courses WHERE user_id = ? ORDER BY id DESC", (g.user["id"],)
    ).fetchall()
    out = []
    for c in courses:
        skills = db.execute(
            """SELECT s.id, s.name, s.name_ar, s.category FROM course_skills cs
               JOIN skills s ON s.id = cs.skill_id WHERE cs.course_id = ?""",
            (c["id"],),
        ).fetchall()
        d = dict(c)
        d["skills"] = [dict(s) for s in skills]
        out.append(d)
    return jsonify({"courses": out})


@bp.post("/courses")
@login_required
def add_course():
    data = request.get_json(silent=True) or {}
    title = (data.get("title") or "").strip()
    description = (data.get("description") or "").strip()
    kind = data.get("kind") if data.get("kind") in ("course", "certification") else "course"
    if not title:
        return jsonify({"error": "اسم المادة مطلوب"}), 400
    db = get_db()
    cur = db.execute(
        "INSERT INTO courses (user_id, title, description, kind) VALUES (?, ?, ?, ?)",
        (g.user["id"], title, description, kind),
    )
    cid = cur.lastrowid
    skills = nlp.extract_skills_named(f"{title}. {description}", db)
    for s in skills:
        db.execute(
            "INSERT OR IGNORE INTO course_skills (course_id, skill_id) VALUES (?, ?)",
            (cid, s["id"]),
        )
    db.commit()
    return jsonify({"id": cid, "extracted_skills": skills}), 201


@bp.get("/catalog")
@login_required
def catalog():
    db = get_db()
    rows = db.execute(
        "SELECT id, title, level, semester, description FROM course_catalog ORDER BY level, semester, id"
    ).fetchall()
    return jsonify({"catalog": [dict(r) for r in rows]})


@bp.post("/courses/from-catalog")
@login_required
def add_from_catalog():
    data = request.get_json(silent=True) or {}
    db = get_db()
    row = db.execute(
        "SELECT * FROM course_catalog WHERE id = ?", (data.get("catalog_id"),)
    ).fetchone()
    if row is None:
        return jsonify({"error": "المادة غير موجودة في القائمة"}), 404
    dup = db.execute(
        "SELECT 1 FROM courses WHERE user_id = ? AND title = ?", (g.user["id"], row["title"])
    ).fetchone()
    if dup:
        return jsonify({"error": "المادة دي مضافة عندك قبل كده"}), 409
    cur = db.execute(
        "INSERT INTO courses (user_id, title, description, kind) VALUES (?, ?, ?, 'course')",
        (g.user["id"], row["title"], row["description"]),
    )
    cid = cur.lastrowid
    skills = nlp.extract_skills_named(f"{row['title']}. {row['description']}", db)
    for s in skills:
        db.execute(
            "INSERT OR IGNORE INTO course_skills (course_id, skill_id) VALUES (?, ?)",
            (cid, s["id"]),
        )
    db.commit()
    return jsonify({"id": cid, "extracted_skills": skills}), 201


@bp.delete("/courses/<int:course_id>")
@login_required
def delete_course(course_id):
    db = get_db()
    cur = db.execute(
        "DELETE FROM courses WHERE id = ? AND user_id = ?", (course_id, g.user["id"])
    )
    db.commit()
    if cur.rowcount == 0:
        return jsonify({"error": "المادة غير موجودة"}), 404
    return jsonify({"ok": True})


@bp.get("/skills")
@login_required
def my_skills():
    db = get_db()
    rows = db.execute(
        """SELECT DISTINCT s.id, s.name, s.name_ar, s.category FROM course_skills cs
           JOIN courses c ON c.id = cs.course_id
           JOIN skills s ON s.id = cs.skill_id
           WHERE c.user_id = ? ORDER BY s.category, s.name""",
        (g.user["id"],),
    ).fetchall()
    return jsonify({"skills": [dict(r) for r in rows]})


@bp.post("/extract")
@login_required
def extract_preview():
    data = request.get_json(silent=True) or {}
    text = (data.get("text") or "").strip()
    if not text:
        return jsonify({"error": "النص فارغ"}), 400
    db = get_db()
    return jsonify(
        {
            "tokens": nlp.preprocess(text)[:60],
            "skills": nlp.extract_skills_named(text, db),
        }
    )


@bp.get("/jobs")
@login_required
def list_jobs():
    db = get_db()
    jobs = db.execute("SELECT id, title, title_ar, category, description FROM jobs").fetchall()
    out = []
    for j in jobs:
        reqs = db.execute(
            """SELECT s.id, s.name, s.name_ar, js.importance FROM job_skills js
               JOIN skills s ON s.id = js.skill_id
               WHERE js.job_id = ? ORDER BY js.importance DESC, s.name""",
            (j["id"],),
        ).fetchall()
        d = dict(j)
        d["required_skills"] = [dict(r) for r in reqs]
        out.append(d)
    return jsonify({"jobs": out})


@bp.get("/jobs/<int:job_id>")
@login_required
def job_detail(job_id):
    db = get_db()
    j = db.execute("SELECT * FROM jobs WHERE id = ?", (job_id,)).fetchone()
    if j is None:
        return jsonify({"error": "الوظيفة غير موجودة"}), 404
    reqs = db.execute(
        """SELECT s.id, s.name, s.name_ar, js.importance FROM job_skills js
           JOIN skills s ON s.id = js.skill_id
           WHERE js.job_id = ? ORDER BY js.importance DESC, s.name""",
        (job_id,),
    ).fetchall()
    d = dict(j)
    d["required_skills"] = [dict(r) for r in reqs]
    return jsonify({"job": d})


@bp.get("/matches")
@login_required
def matches():
    db = get_db()
    return jsonify({"matches": matching.rank_jobs(db, g.user["id"])})


@bp.get("/analysis/<int:job_id>")
@login_required
def analysis(job_id):
    db = get_db()
    j = db.execute("SELECT * FROM jobs WHERE id = ?", (job_id,)).fetchone()
    if j is None:
        return jsonify({"error": "الوظيفة غير موجودة"}), 404
    user_skills = matching.student_skill_ids(db, g.user["id"])
    m = matching.match_job(db, user_skills, job_id)
    roadmap = matching.build_roadmap(db, user_skills, job_id)
    db.execute(
        "INSERT INTO analyses (user_id, job_id, match_pct, matched, missing) VALUES (?, ?, ?, ?, ?)",
        (
            g.user["id"],
            job_id,
            m["match_pct"],
            json.dumps([e["skill_id"] for e in m["matched"]]),
            json.dumps([e["skill_id"] for e in m["missing"]]),
        ),
    )
    db.commit()
    return jsonify(
        {
            "job": {"id": j["id"], "title": j["title"], "title_ar": j["title_ar"]},
            "match_pct": m["match_pct"],
            "matched": m["matched"],
            "missing": m["missing"],
            "roadmap": roadmap["steps"],
        }
    )
