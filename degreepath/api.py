"""REST API blueprint."""
import json

from flask import Blueprint, current_app, g, jsonify, request
from werkzeug.security import check_password_hash, generate_password_hash

from . import feed, matching, nlp, security
from .auth import (
    create_session,
    current_user,
    login_required,
    register_user,
    validate_credentials,
)
from .db import get_db, is_unique_violation

bp = Blueprint("api", __name__, url_prefix="/api")
_DUMMY_HASH = generate_password_hash("dummy-password-for-timing")


@bp.post("/register")
def register():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    name = (data.get("name") or "").strip()
    err = validate_credentials(email, password, name)
    if err:
        return jsonify({"error": err}), 400
    if security.signup_blocked():
        return jsonify({"error": "محاولات تسجيل كتير، جرّب بعد شوية"}), 429
    security.record_signup()
    try:
        uid = register_user(email, password, name)
    except Exception as exc:
        if not is_unique_violation(exc):
            raise
        return jsonify({"error": "البريد ده مسجل قبل كده، جرّب تسجيل الدخول"}), 409
    return jsonify({"token": create_session(uid), "user": {"id": uid, "email": email, "name": name}}), 201


@bp.post("/login")
def login():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    if len(email) > 254 or len(password) > 128:
        return jsonify({"error": "البريد أو كلمة المرور غير صحيحة"}), 401
    if security.login_blocked(email):
        return jsonify({"error": "محاولات كتير غلط. استنى 15 دقيقة وجرّب تاني"}), 429
    db = get_db()
    row = db.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
    if row is None:
        check_password_hash(_DUMMY_HASH, password)  # same timing as a real check
    if row is None or not check_password_hash(row["password_hash"], password):
        security.record_login_failure(email)
        return jsonify({"error": "البريد أو كلمة المرور غير صحيحة"}), 401
    security.clear("fail_email", email)
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
    skills = nlp.extract_skills_hybrid(f"{title}. {description}", db)
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
    skills = nlp.extract_skills_hybrid(f"{row['title']}. {row['description']}", db)
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
            "skills": nlp.extract_skills_hybrid(text, db),
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


# ---------------------------------------------------------------- live feed

def _feed_job_row(db, j, user_skills):
    reqs = db.execute(
        """SELECT s.id, s.name, s.name_ar, js.importance FROM live_job_skills js
           JOIN skills s ON s.id = js.skill_id WHERE js.job_id = ?
           ORDER BY js.importance DESC, s.name""",
        (j["id"],),
    ).fetchall()
    total = sum(r["importance"] for r in reqs) or 1
    got = sum(r["importance"] for r in reqs if r["id"] in user_skills)
    info = feed.SOURCE_INFO.get(j["source"], {})
    return {
        "id": j["id"], "title": j["title"], "company": j["company"],
        "location": j["location"], "remote": bool(j["remote"]),
        "posted_at": j["posted_at"], "source": j["source"],
        "field": j["field"] or "other", "field_label": feed.FIELD_LABELS.get(j["field"] or "other", ""),
        "egypt": (j["country"] or "") == "EG",
        "source_name": info.get("name", j["source"]), "source_site": info.get("site", ""),
        "apply_url": j["url"],
        "match_pct": round(100.0 * got / total, 1),
        "n_skills": len(reqs),
        "matched": [dict(r) for r in reqs if r["id"] in user_skills],
        "missing": [dict(r) for r in reqs if r["id"] not in user_skills],
    }


@bp.get("/feed/status")
def feed_status():
    db = get_db()
    feed.maybe_refresh(current_app, db)
    jobs = db.execute("SELECT source, COUNT(*) AS c FROM live_jobs GROUP BY source").fetchall()
    courses = db.execute("SELECT source, COUNT(*) AS c FROM live_courses GROUP BY source").fetchall()
    last = feed.last_run(db)
    return jsonify({
        "refreshing": feed.is_running(db),
        "stale_after_hours": feed.STALE_HOURS,
        "last_refresh_utc": last["finished_at"] if last else None,
        "job_sources": [
            {"source": r["source"], "name": feed.SOURCE_INFO[r["source"]]["name"],
             "site": feed.SOURCE_INFO[r["source"]]["site"], "count": r["c"]}
            for r in jobs if r["source"] in feed.SOURCE_INFO
        ],
        "course_sources": [
            {"source": r["source"], "name": feed.SOURCE_INFO[r["source"]]["name"],
             "site": feed.SOURCE_INFO[r["source"]]["site"],
             "note": feed.SOURCE_INFO[r["source"]]["note"], "count": r["c"]}
            for r in courses if r["source"] in feed.SOURCE_INFO
        ],
        "total_jobs": sum(r["c"] for r in jobs),
        "egypt_jobs": db.execute("SELECT COUNT(*) AS n FROM live_jobs WHERE country='EG'").fetchone()["n"],
        "job_fields": [
            {"field": r["f"], "label": feed.FIELD_LABELS.get(r["f"], r["f"]), "count": r["c"]}
            for r in db.execute(
                "SELECT COALESCE(field,'other') AS f, COUNT(*) AS c FROM live_jobs GROUP BY f ORDER BY c DESC")
        ],
        "course_fields": [
            {"field": r["f"], "label": feed.FIELD_LABELS.get(r["f"], r["f"]), "count": r["c"]}
            for r in db.execute(
                "SELECT COALESCE(field,'other') AS f, COUNT(*) AS c FROM live_courses GROUP BY f ORDER BY c DESC")
        ],
        "total_courses": sum(r["c"] for r in courses),
        "last_report": last,
    })


@bp.get("/feed/jobs")
@login_required
def feed_jobs():
    db = get_db()
    feed.maybe_refresh(current_app, db)
    user_skills = matching.student_skill_ids(db, g.user["id"])
    q = (request.args.get("q") or "").strip().lower()
    source = request.args.get("source") or ""
    sort = request.args.get("sort") or "match"
    try:
        limit = max(1, min(int(request.args.get("limit", 40)), 100))
        offset = max(0, int(request.args.get("offset", 0)))
    except ValueError:
        limit, offset = 40, 0
    sql = "SELECT * FROM live_jobs"
    args, where = [], []
    if source:
        where.append("source = ?")
        args.append(source)
    if q:
        where.append("(lower(title) LIKE ? OR lower(company) LIKE ?)")
        args += [f"%{q}%", f"%{q}%"]
    field = request.args.get("field") or ""
    if field:
        where.append("field = ?")
        args.append(field)
    where_country = request.args.get("country") or ""
    if where_country == "eg":
        where.append("country = 'EG'")
    elif where_country == "world":
        where.append("COALESCE(country,'') <> 'EG'")
    if where:
        sql += " WHERE " + " AND ".join(where)
    rows = [_feed_job_row(db, j, user_skills) for j in db.execute(sql, args).fetchall()]
    if sort == "new":
        rows.sort(key=lambda r: r["posted_at"] or "", reverse=True)
    else:
        rows.sort(key=lambda r: (r["match_pct"] * min(1.0, r["n_skills"] / 4), r["posted_at"] or ""), reverse=True)
    # mix sources: when sorted by match, no source may take every top slot
    total = len(rows)
    if not source and not where_country:
        rows = _interleave(rows)
    return jsonify({"total": total, "jobs": rows[offset: offset + limit]})


def _interleave(rows):
    """Egypt jobs lead: three Egypt jobs for every one from abroad, keeping the chosen order."""
    eg = [r for r in rows if r["egypt"]]
    world = [r for r in rows if not r["egypt"]]
    out = []
    while eg or world:
        for _ in range(3):
            if eg:
                out.append(eg.pop(0))
        if world:
            out.append(world.pop(0))
    return out


@bp.get("/feed/courses")
@login_required
def feed_courses():
    db = get_db()
    q = (request.args.get("q") or "").strip().lower()
    field = request.args.get("field") or ""
    source = request.args.get("source") or ""
    try:
        limit = max(1, min(int(request.args.get("limit", 30)), 100))
        offset = max(0, int(request.args.get("offset", 0)))
    except ValueError:
        limit, offset = 30, 0
    where, args = [], []
    if q:
        where.append("(lower(title) LIKE ? OR lower(summary) LIKE ?)")
        args += [f"%{q}%", f"%{q}%"]
    if field:
        where.append("field = ?")
        args.append(field)
    if source:
        where.append("source = ?")
        args.append(source)
    w = (" WHERE " + " AND ".join(where)) if where else ""
    total = db.execute("SELECT COUNT(*) AS n FROM live_courses" + w, args).fetchone()["n"]
    rows = db.execute(
        "SELECT id, source, title, summary, url, level, duration_min, field FROM live_courses" + w
        + " ORDER BY (source='coursera') DESC, id LIMIT ? OFFSET ?", args + [limit, offset]).fetchall()
    out = []
    for r in rows:
        info = feed.SOURCE_INFO.get(r["source"], {})
        out.append({
            "id": r["id"], "title": r["title"], "summary": r["summary"], "url": r["url"],
            "level": r["level"], "duration_min": r["duration_min"],
            "provider": info.get("name", r["source"]),
            "free": "audit" if r["source"] == "coursera" else "free",
            "field_label": feed.FIELD_LABELS.get(r["field"] or "other", ""),
        })
    return jsonify({"total": total, "courses": out})


@bp.get("/feed/jobs/<int:job_id>")
@login_required
def feed_job_detail(job_id):
    db = get_db()
    j = db.execute("SELECT * FROM live_jobs WHERE id = ?", (job_id,)).fetchone()
    if j is None:
        return jsonify({"error": "الوظيفة غير موجودة أو انتهت (الوظائف بتتحدث يوميًا)"}), 404
    user_skills = matching.student_skill_ids(db, g.user["id"])
    row = _feed_job_row(db, j, user_skills)
    row["description"] = j["description"]
    steps = []
    for i, m in enumerate(row["missing"], 1):
        steps.append({
            "step": i, "skill": m["name"], "skill_ar": m["name_ar"], "importance": m["importance"],
            "courses": feed.courses_for_skill(db, m["id"]),
        })
    row["roadmap"] = steps
    return jsonify({"job": row})


@bp.post("/feed/refresh")
@login_required
def feed_refresh():
    db = get_db()
    last = feed.last_run(db)
    if feed.is_running(db):
        return jsonify({"started": False, "message": "التحديث شغال دلوقتي"}), 202
    if last:
        try:
            from datetime import datetime, timezone
            t = datetime.strptime(last["finished_at"], "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
            if (datetime.now(timezone.utc) - t).total_seconds() < 1800:
                return jsonify({"started": False,
                                "message": "اتحدّث من أقل من 30 دقيقة، جرب بعدين"}), 429
        except Exception:
            pass
    return jsonify({"started": feed.refresh_in_background(current_app)})
