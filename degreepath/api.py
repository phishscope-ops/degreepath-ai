"""REST API blueprint."""
import json

from flask import Blueprint, current_app, g, jsonify, request
from werkzeug.security import check_password_hash, generate_password_hash

from . import arsearch, feed, matching, nlp, security
from .auth import (
    create_session,
    current_user,
    login_required,
    register_user,
    validate_credentials,
)
from .db import get_db, is_unique_violation, log_analysis_later

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
    from .auth import forget_token
    forget_token(auth[7:].strip())
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
    by_course = {}
    for r in db.execute(
        """SELECT cs.course_id AS course_id, s.id AS id, s.name AS name, s.name_ar AS name_ar,
                  s.category AS category FROM course_skills cs
           JOIN skills s ON s.id = cs.skill_id JOIN courses c ON c.id = cs.course_id
           WHERE c.user_id = ?""",
        (g.user["id"],),
    ).fetchall():
        by_course.setdefault(r["course_id"], []).append(
            {"id": r["id"], "name": r["name"], "name_ar": r["name_ar"], "category": r["category"]})
    out = []
    for c in courses:
        d = dict(c)
        d["skills"] = by_course.get(c["id"], [])
        out.append(d)
    return jsonify({"courses": out})


@bp.post("/courses")
@login_required
def add_course():
    data = request.get_json(silent=True) or {}
    title = (data.get("title") or "").strip()
    description = (data.get("description") or "").strip()
    kind = data.get("kind") if data.get("kind") in ("course", "certification", "skill") else "course"
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
    rows = _cached_rows(
        db, "SELECT id, title, level, semester, description FROM course_catalog ORDER BY level, semester, id")
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


@bp.get("/skills/search")
@login_required
def skills_search():
    """Find skills to add by name, in Arabic or English (empty query = the most wanted skills)."""
    db = get_db()
    q = (request.args.get("q") or "").strip()
    cat = matching.catalog(db)
    mine = matching.student_skill_ids(db, g.user["id"])
    aliases = {}
    for r in _cached_rows(db, "SELECT skill_id, alias FROM skill_aliases"):
        aliases.setdefault(r["skill_id"], []).append(r["alias"])
    groups = arsearch.parse(q)
    out = []
    for sid, sk in cat["smap"].items():
        if groups:
            hay = [sk["name"], sk["name_ar"] or ""] + aliases.get(sid, [])
            if not arsearch.matches(groups, " ".join(hay)):
                continue
        out.append({"id": sid, "name": sk["name"], "name_ar": sk["name_ar"], "category": sk["category"],
                    "have": sid in mine, "demand": cat["demand"].get(sid, 0)})
    out.sort(key=lambda x: (-x["demand"], x["name"]))
    return jsonify({"skills": out[:24]})


@bp.post("/skills/add")
@login_required
def skills_add():
    """Add one skill (not a subject or course) to the student's profile."""
    data = request.get_json(silent=True) or {}
    db = get_db()
    try:
        sid = int(data.get("skill_id"))
    except (TypeError, ValueError):
        return jsonify({"error": "اختار مهارة من القائمة"}), 400
    sk = db.execute("SELECT id, name, name_ar, category FROM skills WHERE id = ?", (sid,)).fetchone()
    if sk is None:
        return jsonify({"error": "المهارة دي مش موجودة"}), 404
    if sid in matching.student_skill_ids(db, g.user["id"]):
        return jsonify({"skill": dict(sk), "already": True}), 200
    cur = db.execute("INSERT INTO courses (user_id, title, description, kind) VALUES (?, ?, ?, 'skill')",
                     (g.user["id"], sk["name"], sk["name"]))
    db.execute("INSERT OR IGNORE INTO course_skills (course_id, skill_id) VALUES (?, ?)", (cur.lastrowid, sid))
    db.commit()
    return jsonify({"skill": dict(sk), "already": False}), 201


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


CATEGORY_LABELS = {
    "web": "تطوير الويب", "software": "هندسة البرمجيات", "mobile": "تطبيقات الموبايل",
    "data": "البيانات", "ai": "الذكاء الاصطناعي", "security": "الأمن السيبراني",
    "cloud": "السحابة و DevOps", "it": "الدعم الفني والشبكات", "business": "الأعمال والتحليل",
    "design": "التصميم", "databases": "قواعد البيانات", "games": "الألعاب", "web3": "بلوك تشين",
}


def _job_skill_list(cat, job_id):
    out = []
    for r in cat["reqs"].get(job_id, []):
        sk = cat["smap"].get(r["skill_id"])
        if sk:
            out.append({"id": r["skill_id"], "name": sk["name"], "name_ar": sk["name_ar"],
                        "importance": r["importance"]})
    return out


@bp.get("/jobs")
@login_required
def list_jobs():
    cat = matching.catalog(get_db())
    out = []
    for j in cat["jobs"]:
        d = dict(j)
        d["required_skills"] = _job_skill_list(cat, j["id"])
        out.append(d)
    return jsonify({"jobs": out})


@bp.get("/careers")
@login_required
def list_careers():
    """Every career track in the system (no personalization), grouped by category."""
    cat = matching.catalog(get_db())
    careers = []
    for j in cat["jobs"]:
        sk = _job_skill_list(cat, j["id"])
        careers.append({
            "id": j["id"], "title": j["title"], "title_ar": j["title_ar"],
            "category": j["category"], "description": j["description"],
            "n_skills": len(sk), "top_skills": [s["name"] for s in sk[:4]],
        })
    seen = []
    for c in careers:
        if c["category"] not in seen:
            seen.append(c["category"])
    cats = [{"key": k, "label": CATEGORY_LABELS.get(k, k),
             "count": sum(1 for c in careers if c["category"] == k)} for k in seen]
    return jsonify({"careers": careers, "categories": cats})


@bp.get("/careers/<int:job_id>")
@login_required
def career_detail(job_id):
    db = get_db()
    r = matching.full_roadmap(db, job_id, matching.student_skill_ids(db, g.user["id"]))
    if r is None:
        return jsonify({"error": "الوظيفة غير موجودة"}), 404
    r["job"]["category_label"] = CATEGORY_LABELS.get(r["job"]["category"], r["job"]["category"])
    return jsonify(r)


@bp.get("/jobs/<int:job_id>")
@login_required
def job_detail(job_id):
    db = get_db()
    cat = matching.catalog(db)
    j = cat["jobs_by_id"].get(job_id)
    if j is None:
        return jsonify({"error": "الوظيفة غير موجودة"}), 404
    d = dict(j)
    d["required_skills"] = _job_skill_list(cat, job_id)
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
    cat = matching.catalog(db)
    j = cat["jobs_by_id"].get(job_id)
    if j is None:
        return jsonify({"error": "الوظيفة غير موجودة"}), 404
    user_skills = matching.student_skill_ids(db, g.user["id"])
    m = matching.match_job(db, user_skills, job_id, cat["reqs"].get(job_id, []), cat["smap"])
    roadmap = matching.build_roadmap(db, user_skills, job_id)
    # the history row is written after the response is sent (saves 2 DB round trips)
    log_analysis_later(
        current_app._get_current_object(),
        (g.user["id"], job_id, m["match_pct"],
         json.dumps([e["skill_id"] for e in m["matched"]]),
         json.dumps([e["skill_id"] for e in m["missing"]])))
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

_QC = {}
_QC_TTL = 120  # the live feed only changes on its daily refresh


def _cached_rows(db, sql, args=()):
    """Run a read query through a 2-minute in-process cache (saves DB round trips)."""
    import time
    if current_app.config.get("TESTING"):
        return db.execute(sql, args).fetchall()
    key = (sql, tuple(args))
    hit = _QC.get(key)
    if hit and time.time() - hit[0] < _QC_TTL:
        return hit[1]
    rows = [dict(r) for r in db.execute(sql, args).fetchall()]
    if len(_QC) > 300:
        _QC.clear()
    _QC[key] = (time.time(), rows)
    return rows


def _feed_reqs_map(db):
    m = {}
    for r in _cached_rows(db, 
        """SELECT js.job_id AS job_id, s.id AS id, s.name AS name, s.name_ar AS name_ar, js.importance AS importance
           FROM live_job_skills js JOIN skills s ON s.id = js.skill_id
           ORDER BY js.importance DESC, s.name"""
    ):
        m.setdefault(r["job_id"], []).append(
            {"id": r["id"], "name": r["name"], "name_ar": r["name_ar"], "importance": r["importance"]})
    return m


def _feed_job_row(db, j, user_skills, reqs_map=None):
    reqs = reqs_map.get(j["id"], []) if reqs_map is not None else db.execute(
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


_STATUS_CACHE = {"t": 0.0, "body": None}


@bp.get("/feed/status")
def feed_status():
    import time
    c = _STATUS_CACHE
    if c["body"] is not None and time.time() - c["t"] < 60 and not current_app.config.get("TESTING"):
        return current_app.response_class(c["body"], mimetype="application/json")
    resp = _feed_status()
    c["body"], c["t"] = resp.get_data(), time.time()
    return resp


def _feed_status():
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
                "SELECT COALESCE(field,'other') AS f, COUNT(*) AS c FROM live_courses "
                "WHERE COALESCE(pricing,'free')='free' GROUP BY f ORDER BY c DESC")
        ],
        "paid_course_fields": [
            {"field": r["f"], "label": feed.FIELD_LABELS.get(r["f"], r["f"]), "count": r["c"]}
            for r in db.execute(
                "SELECT COALESCE(field,'other') AS f, COUNT(*) AS c FROM live_courses "
                "WHERE pricing='paid' GROUP BY f ORDER BY c DESC")
        ],
        "total_courses": db.execute(
            "SELECT COUNT(*) AS n FROM live_courses WHERE COALESCE(pricing,'free')='free'").fetchone()["n"],
        "arabic_courses": db.execute(
            "SELECT COUNT(*) AS n FROM live_courses WHERE source='arabic'").fetchone()["n"],
        "paid_courses": db.execute(
            "SELECT COUNT(*) AS n FROM live_courses WHERE pricing='paid'").fetchone()["n"],
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
    reqs_map = _feed_reqs_map(db)
    rows = [_feed_job_row(db, j, user_skills, reqs_map) for j in _cached_rows(db, sql, args)]
    groups = arsearch.parse(q)
    if groups:
        rows = [r for r in rows if arsearch.matches(groups, r["title"], r["company"], r["field_label"], r["location"])]
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
    """Courses in two separate groups: pricing=free (100% free, default) or pricing=paid
    (Coursera: free trial then subscription). The two are never mixed in one list."""
    db = get_db()
    q = (request.args.get("q") or "").strip()
    field = request.args.get("field") or ""
    source = request.args.get("source") or ""
    pricing = "paid" if request.args.get("pricing") == "paid" else "free"
    try:
        limit = max(1, min(int(request.args.get("limit", 30)), 100))
        offset = max(0, int(request.args.get("offset", 0)))
    except ValueError:
        limit, offset = 30, 0
    where = ["COALESCE(pricing,'free') = ?" if pricing == "free" else "pricing = 'paid'"]
    args = ["free"] if pricing == "free" else []
    if field:
        where.append("field = ?")
        args.append(field)
    if source:
        where.append("source = ?")
        args.append(source)
    rows = _cached_rows(db,
        "SELECT id, source, title, summary, url, level, duration_min, field FROM live_courses WHERE "
        + " AND ".join(where) + " ORDER BY CASE WHEN source = 'arabic' THEN 0 ELSE 1 END, id", args)
    groups = arsearch.parse(q)
    if groups:
        rows = [r for r in rows if arsearch.matches(groups, r["title"], r["summary"])]
        # best matches first: a hit in the title beats a hit in the summary only
        rows.sort(key=lambda r: not arsearch.matches(groups, r["title"]))
    total = len(rows)
    out = []
    for r in rows[offset: offset + limit]:
        info = feed.SOURCE_INFO.get(r["source"], {})
        out.append({
            "id": r["id"], "title": r["title"], "summary": r["summary"] or "", "url": r["url"],
            "level": r["level"], "duration_min": r["duration_min"],
            "provider": info.get("name", r["source"]),
            "free": "free" if pricing == "free" else "paid",
            "pricing_note": "" if pricing == "free" else "تجربة مجانية 7 أيام ثم اشتراك مدفوع",
            "field_label": feed.FIELD_LABELS.get(r["field"] or "other", ""),
        })
    return jsonify({"total": total, "pricing": pricing, "courses": out})


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
