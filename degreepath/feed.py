"""Daily live feed: jobs from several public sources + free courses, linked by skill.

Sources (all public, no API key, no account, no payment):
  jobs:    Remotive, Arbeitnow, RemoteOK, Jobicy, Himalayas
  courses: Microsoft Learn catalog (fully free), Coursera public catalog (free to audit)

Every job and course is run through the same skill dictionary used for the
student's own subjects, so a job -> missing skills -> courses -> apply link chain
is computed from one shared skills table.

The feed is rebuilt from the sources on start-up and whenever the data is more than
24 hours old, so a free-tier restart (which wipes SQLite) never loses anything that
cannot be fetched again.
"""
import html
import json
import re
import sqlite3
import threading
import time
from datetime import datetime, timedelta, timezone

import requests

from . import nlp

UA = {"User-Agent": "DegreePathAI/1.2 (student graduation project; daily fetch)"}
TIMEOUT = 40
STALE_HOURS = 24
PER_SOURCE_JOB_CAP = 120
MAX_DESC = 1800

_lock = threading.Lock()
_running = False

SOURCE_INFO = {
    "remotive": {"name": "Remotive", "kind": "job", "site": "https://remotive.com",
                 "note": "رابط التقديم يفتح صفحة Remotive الأصلية"},
    "arbeitnow": {"name": "Arbeitnow", "kind": "job", "site": "https://www.arbeitnow.com",
                  "note": "وظائف أوروبا، بعضها بتأشيرة/نقل"},
    "remoteok": {"name": "Remote OK", "kind": "job", "site": "https://remoteok.com",
                 "note": "رابط التقديم يفتح Remote OK"},
    "jobicy": {"name": "Jobicy", "kind": "job", "site": "https://jobicy.com",
               "note": "رابط التقديم يفتح Jobicy"},
    "himalayas": {"name": "Himalayas", "kind": "job", "site": "https://himalayas.app",
                  "note": "رابط التقديم يفتح Himalayas"},
    "mslearn": {"name": "Microsoft Learn", "kind": "course", "site": "https://learn.microsoft.com/training/",
                "note": "مجاني بالكامل"},
    "coursera": {"name": "Coursera", "kind": "course", "site": "https://www.coursera.org",
                 "note": "مجاني للمشاهدة (Audit)؛ الشهادة مدفوعة"},
}


def _now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


def clean(text, limit=MAX_DESC):
    text = html.unescape(re.sub(r"<[^>]+>", " ", text or ""))
    text = re.sub(r"\s+", " ", text).strip()
    return text[:limit]


def _get(url, **kw):
    r = requests.get(url, headers=UA, timeout=TIMEOUT, **kw)
    r.raise_for_status()
    return json.loads(r.content.decode("utf-8", errors="replace"))


def _iso(value):
    """Normalise epoch seconds / ISO strings to 'YYYY-MM-DD'."""
    try:
        if value in (None, ""):
            return ""
        s = str(value)
        if s.isdigit():
            return datetime.fromtimestamp(int(s), timezone.utc).strftime("%Y-%m-%d")
        return s[:10]
    except Exception:
        return ""


# ---------------------------------------------------------------- job sources

def fetch_remotive():
    out = []
    for j in _get("https://remotive.com/api/remote-jobs").get("jobs", []):
        out.append(dict(
            ext_id=str(j["id"]), title=j["title"], company=j.get("company_name", ""),
            location=j.get("candidate_required_location") or "Remote", remote=1,
            url=j["url"], description=clean(j.get("description")),
            posted_at=_iso(j.get("publication_date")), tags=" ".join(j.get("tags") or []),
        ))
    return out


def fetch_arbeitnow():
    out = []
    for j in _get("https://www.arbeitnow.com/api/job-board-api").get("data", []):
        out.append(dict(
            ext_id=j["slug"], title=j["title"], company=j.get("company_name", ""),
            location=j.get("location", ""), remote=1 if j.get("remote") else 0,
            url=j["url"], description=clean(j.get("description")),
            posted_at=_iso(j.get("created_at")), tags=" ".join(j.get("tags") or []),
        ))
    return out


def fetch_remoteok():
    out = []
    for j in _get("https://remoteok.com/api"):
        if not isinstance(j, dict) or "position" not in j:
            continue
        out.append(dict(
            ext_id=str(j["id"]), title=j["position"], company=j.get("company", ""),
            location=j.get("location") or "Remote", remote=1,
            url=j.get("url") or j.get("apply_url"), description=clean(j.get("description")),
            posted_at=_iso(j.get("date")), tags=" ".join(j.get("tags") or []),
        ))
    return out


def fetch_jobicy():
    out = []
    for j in _get("https://jobicy.com/api/v2/remote-jobs?count=100").get("jobs", []):
        geo = j.get("jobGeo")
        if isinstance(geo, list):
            geo = ", ".join(geo)
        out.append(dict(
            ext_id=str(j["id"]), title=clean(j["jobTitle"], 200), company=j.get("companyName", ""),
            location=geo or "Remote", remote=1, url=j["url"],
            description=clean(j.get("jobDescription") or j.get("jobExcerpt")),
            posted_at=_iso(j.get("pubDate")), tags="",
        ))
    return out


def fetch_himalayas():
    out, cursor = [], None
    for _ in range(4):
        url = "https://himalayas.app/jobs/api?limit=20" + (f"&cursor={cursor}" if cursor else "")
        d = _get(url)
        for j in d.get("jobs", []):
            loc = j.get("locationRestrictions") or []
            out.append(dict(
                ext_id=j.get("guid") or j["title"], title=j["title"],
                company=j.get("companyName", ""),
                location=", ".join(loc) if loc else "Worldwide", remote=1,
                url=j.get("applicationLink") or j.get("guid"),
                description=clean(j.get("description") or j.get("excerpt")),
                posted_at=_iso(j.get("pubDate")),
                tags=" ".join(j.get("categories") or []),
            ))
        cursor = d.get("nextCursor")
        if not cursor:
            break
        time.sleep(1)
    return out


JOB_FETCHERS = {
    "remotive": fetch_remotive, "arbeitnow": fetch_arbeitnow, "remoteok": fetch_remoteok,
    "jobicy": fetch_jobicy, "himalayas": fetch_himalayas,
}


# -------------------------------------------------------------- course sources

def fetch_mslearn():
    out = []
    for kind, key in (("learningPaths", "learningPaths"), ("modules", "modules")):
        d = _get(f"https://learn.microsoft.com/api/catalog/?type={kind}&locale=en-us")
        for c in d.get(key, []):
            out.append(dict(
                ext_id=c["uid"], title=c["title"], summary=clean(c.get("summary"), 400),
                url=c["url"].split("?")[0],
                level=(c.get("levels") or [""])[0],
                duration_min=int(c.get("duration_in_minutes") or 0),
            ))
    return out


def fetch_coursera(pages=25):
    out = []
    for i in range(pages):
        d = _get("https://api.coursera.org/api/courses.v1",
                 params={"start": i * 100, "limit": 100,
                         "fields": "name,slug,description,primaryLanguages"})
        els = d.get("elements", [])
        for c in els:
            if "en" not in (c.get("primaryLanguages") or ["en"]):
                continue
            out.append(dict(
                ext_id=c["id"], title=c["name"], summary=clean(c.get("description"), 400),
                url="https://www.coursera.org/learn/" + c["slug"], level="", duration_min=0,
            ))
        if len(els) < 100:
            break
    return out


COURSE_FETCHERS = {"mslearn": fetch_mslearn, "coursera": fetch_coursera}


# ------------------------------------------------------------------ refresh

def _title_skill_ids(title, tags, alias_index):
    return set(nlp.extract_skills(f"{title} {tags}", alias_index))


def _connect(db_path):
    db = sqlite3.connect(db_path, timeout=60)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA journal_mode=WAL")
    db.execute("PRAGMA busy_timeout=60000")
    db.execute("PRAGMA foreign_keys = ON")
    return db


def claim_run(db_path):
    """Cross-worker guard: return a new run id, or None if a run started <20 min ago is unfinished."""
    db = _connect(db_path)
    try:
        db.execute("BEGIN IMMEDIATE")
        busy = db.execute(
            """SELECT 1 FROM feed_runs WHERE finished_at IS NULL
               AND started_at > datetime('now', '-20 minutes')"""
        ).fetchone()
        if busy:
            db.execute("ROLLBACK")
            return None
        rid = db.execute("INSERT INTO feed_runs (started_at) VALUES (datetime('now'))").lastrowid
        db.execute("COMMIT")
        return rid
    finally:
        db.close()


def refresh(db_path, run_id=None):
    """Fetch every source, store jobs/courses, tag them with skills. Returns a report."""
    started = _now()
    report = {"started_at": started, "sources": {}}
    db = _connect(db_path)
    if run_id is None:
        run_id = db.execute("INSERT INTO feed_runs (started_at) VALUES (?)", (started,)).lastrowid
        db.commit()
    alias_index = nlp.build_alias_index(db)

    for src, fn in JOB_FETCHERS.items():
        try:
            items = fn()
            scored = []
            for it in items:
                if not it.get("url"):
                    continue
                text = f"{it['title']} {it['tags']} {it['description']}"
                ids = nlp.extract_skills(text, alias_index)
                if len(ids) < 2:
                    continue
                core = _title_skill_ids(it["title"], it["tags"], alias_index)
                scored.append((len(ids), it, ids, core))
            scored.sort(key=lambda t: t[1]["posted_at"] or "", reverse=True)
            kept = scored[:PER_SOURCE_JOB_CAP]
            for _n, it, ids, core in kept:
                db.execute(
                    """INSERT INTO live_jobs (source, ext_id, title, company, location, remote,
                       url, description, posted_at, fetched_at)
                       VALUES (?,?,?,?,?,?,?,?,?,?)
                       ON CONFLICT(source, ext_id) DO UPDATE SET title=excluded.title,
                       company=excluded.company, location=excluded.location, url=excluded.url,
                       description=excluded.description, posted_at=excluded.posted_at,
                       fetched_at=excluded.fetched_at""",
                    (src, it["ext_id"], it["title"][:200], it["company"][:120], it["location"][:120],
                     it["remote"], it["url"], it["description"], it["posted_at"], _now()),
                )
                jid = db.execute("SELECT id FROM live_jobs WHERE source=? AND ext_id=?",
                                 (src, it["ext_id"])).fetchone()["id"]
                db.execute("DELETE FROM live_job_skills WHERE job_id=?", (jid,))
                for sid in ids:
                    db.execute("INSERT INTO live_job_skills (job_id, skill_id, importance) VALUES (?,?,?)",
                               (jid, sid, 3 if sid in core else 2))
                db.commit()
            # source succeeded: drop its rows that were not in this fetch (expired jobs)
            db.execute("DELETE FROM live_jobs WHERE source=? AND fetched_at < ?", (src, started))
            db.commit()
            report["sources"][src] = {"ok": True, "fetched": len(items), "stored": len(kept)}
        except Exception as e:  # keep old rows for this source, report the failure
            db.rollback()
            report["sources"][src] = {"ok": False, "error": str(e)[:200]}

    for src, fn in COURSE_FETCHERS.items():
        try:
            items = fn()
            stored = 0
            for it in items:
                ids = nlp.extract_skills(f"{it['title']} {it['summary']}", alias_index)
                if not ids:
                    continue
                db.execute(
                    """INSERT INTO live_courses (source, ext_id, title, summary, url, level,
                       duration_min, fetched_at) VALUES (?,?,?,?,?,?,?,?)
                       ON CONFLICT(source, ext_id) DO UPDATE SET title=excluded.title,
                       summary=excluded.summary, url=excluded.url, level=excluded.level,
                       duration_min=excluded.duration_min, fetched_at=excluded.fetched_at""",
                    (src, it["ext_id"], it["title"][:200], it["summary"], it["url"],
                     it["level"], it["duration_min"], _now()),
                )
                cid = db.execute("SELECT id FROM live_courses WHERE source=? AND ext_id=?",
                                 (src, it["ext_id"])).fetchone()["id"]
                db.execute("DELETE FROM live_course_skills WHERE course_id=?", (cid,))
                for sid in ids:
                    db.execute("INSERT INTO live_course_skills (course_id, skill_id) VALUES (?,?)",
                               (cid, sid))
                stored += 1
                if stored % 100 == 0:
                    db.commit()
            db.execute("DELETE FROM live_courses WHERE source=? AND fetched_at < ?", (src, started))
            db.commit()
            report["sources"][src] = {"ok": True, "fetched": len(items), "stored": stored}
        except Exception as e:
            db.rollback()
            report["sources"][src] = {"ok": False, "error": str(e)[:200]}

    report["finished_at"] = _now()
    db.execute("UPDATE feed_runs SET finished_at=?, report=? WHERE id=?",
               (report["finished_at"], json.dumps(report, ensure_ascii=False), run_id))
    db.commit()
    db.close()
    return report


def last_run(db):
    row = db.execute(
        "SELECT * FROM feed_runs WHERE finished_at IS NOT NULL ORDER BY id DESC LIMIT 1"
    ).fetchone()
    if row is None:
        return None
    rep = json.loads(row["report"] or "{}")
    rep["finished_at"] = row["finished_at"]
    return rep


def is_stale(db):
    row = db.execute(
        """SELECT finished_at FROM feed_runs WHERE finished_at IS NOT NULL
           AND report LIKE '%"ok": true%' ORDER BY id DESC LIMIT 1"""
    ).fetchone()
    if row is None:
        return True
    try:
        t = datetime.strptime(row["finished_at"], "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
    except Exception:
        return True
    return datetime.now(timezone.utc) - t > timedelta(hours=STALE_HOURS)


def refresh_in_background(app):
    """Start a refresh thread unless one is already running."""
    global _running
    with _lock:
        if _running:
            return False
        run_id = claim_run(app.config["DATABASE"])
        if run_id is None:
            return False
        _running = True

    def work():
        global _running
        try:
            refresh(app.config["DATABASE"], run_id)
        except Exception:
            pass
        finally:
            with _lock:
                _running = False

    threading.Thread(target=work, daemon=True).start()
    return True


def is_running(db=None):
    if _running:
        return True
    if db is not None:
        return db.execute(
            """SELECT 1 FROM feed_runs WHERE finished_at IS NULL
               AND started_at > datetime('now', '-20 minutes')"""
        ).fetchone() is not None
    return False


def maybe_refresh(app, db):
    """Called on feed requests and at start-up: refresh when the data is >24h old."""
    if app.config.get("FEED_AUTO", True) and is_stale(db):
        return refresh_in_background(app)
    return False


# ------------------------------------------------------- linking: job -> courses

def courses_for_skill(db, skill_id, limit=3):
    """Free courses for one skill: mix providers so one site never dominates."""
    rows = db.execute(
        """SELECT c.title, c.url, c.source, c.level, c.duration_min FROM live_courses c
           JOIN live_course_skills cs ON cs.course_id = c.id
           WHERE cs.skill_id = ? ORDER BY c.source,
             (SELECT COUNT(*) FROM live_course_skills x WHERE x.course_id = c.id), c.title""",
        (skill_id,),
    ).fetchall()
    by_src = {}
    for r in rows:
        by_src.setdefault(r["source"], []).append(r)
    picked = []
    cur = db.execute(
        "SELECT title, url, kind FROM resources WHERE skill_id = ? ORDER BY id LIMIT 1", (skill_id,)
    ).fetchone()
    if cur:
        picked.append({"title": cur["title"], "url": cur["url"], "provider": "مصدر مختار",
                       "free": "free", "level": "", "duration_min": 0})
    i = 0
    while len(picked) < limit and any(by_src.values()):
        for src in list(by_src):
            if by_src[src] and len(picked) < limit:
                r = by_src[src].pop(0)
                info = SOURCE_INFO.get(src, {})
                picked.append({
                    "title": r["title"], "url": r["url"], "provider": info.get("name", src),
                    "free": "audit" if src == "coursera" else "free",
                    "level": r["level"], "duration_min": r["duration_min"],
                })
        i += 1
        if i > 10:
            break
    return picked
