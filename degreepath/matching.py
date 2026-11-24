"""Job matching, skill gap analysis and learning roadmap generation."""


import time

from flask import current_app

_CAT = {"t": 0.0, "data": None}
_CAT_TTL = 600  # jobs, required skills and resources only change at seed time


def catalog(db):
    """In-memory copy of the static career data (jobs, requirements, resources).

    Every API call used to re-read this from the remote database; now it is read
    once per 10 minutes per process. Disabled while testing."""
    testing = current_app.config.get("TESTING")
    if not testing and _CAT["data"] is not None and time.time() - _CAT["t"] < _CAT_TTL:
        return _CAT["data"]
    smap = {r["id"]: dict(r) for r in db.execute("SELECT id, name, name_ar, category FROM skills").fetchall()}
    jobs = [dict(r) for r in db.execute(
        "SELECT id, title, title_ar, category, description FROM jobs ORDER BY id").fetchall()]
    reqs = {}
    demand = {}
    for r in db.execute(
        "SELECT job_id, skill_id, importance FROM job_skills ORDER BY importance DESC, skill_id").fetchall():
        reqs.setdefault(r["job_id"], []).append({"skill_id": r["skill_id"], "importance": r["importance"]})
        demand[r["skill_id"]] = demand.get(r["skill_id"], 0) + 1
    res = {}
    for r in db.execute("SELECT skill_id, title, url, kind FROM resources ORDER BY id").fetchall():
        lst = res.setdefault(r["skill_id"], [])
        if len(lst) < 2:
            lst.append({"title": r["title"], "url": r["url"], "kind": r["kind"]})
    data = {"smap": smap, "jobs": jobs, "jobs_by_id": {j["id"]: j for j in jobs},
            "reqs": reqs, "demand": demand, "res": res}
    if not testing:
        _CAT["t"], _CAT["data"] = time.time(), data
    return data


def student_skill_ids(db, user_id):
    rows = db.execute(
        """SELECT DISTINCT cs.skill_id FROM course_skills cs
           JOIN courses c ON c.id = cs.course_id WHERE c.user_id = ?""",
        (user_id,),
    ).fetchall()
    return {r["skill_id"] for r in rows}


def _skill_map(db):
    rows = db.execute("SELECT id, name, name_ar, category FROM skills").fetchall()
    return {r["id"]: dict(r) for r in rows}


def _job_requirements(db, job_id):
    return db.execute(
        "SELECT skill_id, importance FROM job_skills WHERE job_id = ?", (job_id,)
    ).fetchall()


def match_job(db, user_skills, job_id, reqs=None, smap=None):
    """Weighted coverage: sum(importance of matched) / sum(importance of all)."""
    if reqs is None:
        reqs = _job_requirements(db, job_id)
    if not reqs:
        return None
    if smap is None:
        smap = _skill_map(db)
    total = sum(r["importance"] for r in reqs)
    matched, missing = [], []
    got = 0
    for r in reqs:
        skill = smap.get(r["skill_id"], {"name": "?", "name_ar": "", "category": ""})
        entry = {
            "skill_id": r["skill_id"],
            "name": skill["name"],
            "name_ar": skill["name_ar"],
            "importance": r["importance"],
        }
        if r["skill_id"] in user_skills:
            got += r["importance"]
            matched.append(entry)
        else:
            missing.append(entry)
    matched.sort(key=lambda e: -e["importance"])
    missing.sort(key=lambda e: -e["importance"])
    return {
        "job_id": job_id,
        "match_pct": round(100.0 * got / total, 1),
        "matched": matched,
        "missing": missing,
    }


def rank_jobs(db, user_id):
    user_skills = student_skill_ids(db, user_id)
    cat = catalog(db)
    jobs = cat["jobs"]
    results = []
    smap = cat["smap"]
    reqs_by_job = cat["reqs"]
    for j in jobs:
        m = match_job(db, user_skills, j["id"], reqs_by_job.get(j["id"], []), smap)
        if m is None:
            continue
        m.update(
            title=j["title"], title_ar=j["title_ar"],
            category=j["category"], description=j["description"],
        )
        results.append(m)
    results.sort(key=lambda m: -m["match_pct"])
    return results


def build_roadmap(db, user_skills, job_id):
    """Ordered learning roadmap for the missing skills of one job.

    Order: core (importance 3) first, then 2, then 1; ties broken by how many
    other jobs need the skill (more useful first).
    """
    cat = catalog(db)
    m = match_job(db, user_skills, job_id, cat["reqs"].get(job_id, []), cat["smap"])
    if m is None:
        return None
    demand = cat["demand"]
    missing = sorted(
        m["missing"], key=lambda e: (-e["importance"], -demand.get(e["skill_id"], 0))
    )
    steps = []
    for i, entry in enumerate(missing, 1):
        steps.append(
            {
                "step": i,
                "skill": entry["name"],
                "skill_ar": entry["name_ar"],
                "importance": entry["importance"],
                "resources": list(cat["res"].get(entry["skill_id"], [])),
            }
        )
    return {"job_id": job_id, "match_pct": m["match_pct"], "steps": steps}


def full_roadmap(db, job_id, user_skills=()):
    """The complete career roadmap (every required skill, in three stages),
    independent of what the student already has. `have` marks skills they own."""
    cat = catalog(db)
    job = cat["jobs_by_id"].get(job_id)
    if job is None:
        return None
    stages = {3: [], 2: [], 1: []}
    for r in cat["reqs"].get(job_id, []):
        sk = cat["smap"].get(r["skill_id"])
        if sk is None:
            continue
        stages.setdefault(r["importance"], []).append({
            "skill": sk["name"], "skill_ar": sk["name_ar"],
            "have": r["skill_id"] in user_skills,
            "resources": list(cat["res"].get(r["skill_id"], [])),
            "_d": cat["demand"].get(r["skill_id"], 0),
        })
    labels = {3: "المرحلة 1: الأساسيات (ابدأ بيها)", 2: "المرحلة 2: المهارات المتوسطة", 1: "المرحلة 3: التخصص والتميّز"}
    out, n = [], 0
    for imp in (3, 2, 1):
        items = sorted(stages.get(imp, []), key=lambda x: -x["_d"])
        for it in items:
            n += 1
            it["step"] = n
            it.pop("_d", None)
        if items:
            out.append({"importance": imp, "label": labels[imp], "skills": items})
    return {"job": job, "stages": out, "total_skills": n}
