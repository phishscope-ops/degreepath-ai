"""Job matching, skill gap analysis and learning roadmap generation."""


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
    jobs = db.execute(
        "SELECT id, title, title_ar, category, description FROM jobs"
    ).fetchall()
    results = []
    smap = _skill_map(db)
    reqs_by_job = {}
    for r in db.execute("SELECT job_id, skill_id, importance FROM job_skills").fetchall():
        reqs_by_job.setdefault(r["job_id"], []).append(r)
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
    m = match_job(db, user_skills, job_id)
    if m is None:
        return None
    demand = {}
    for row in db.execute(
        "SELECT skill_id, COUNT(*) AS c FROM job_skills GROUP BY skill_id"
    ).fetchall():
        demand[row["skill_id"]] = row["c"]

    missing = sorted(
        m["missing"], key=lambda e: (-e["importance"], -demand.get(e["skill_id"], 0))
    )
    steps = []
    for i, entry in enumerate(missing, 1):
        res = db.execute(
            "SELECT title, url, kind FROM resources WHERE skill_id = ? ORDER BY id LIMIT 2",
            (entry["skill_id"],),
        ).fetchall()
        steps.append(
            {
                "step": i,
                "skill": entry["name"],
                "skill_ar": entry["name_ar"],
                "importance": entry["importance"],
                "resources": [dict(r) for r in res],
            }
        )
    return {"job_id": job_id, "match_pct": m["match_pct"], "steps": steps}
