"""Daily live feed: jobs from several public sources + free courses, linked by skill.

Sources (all public, no API key, no account, no payment):
  jobs:    Remotive, Arbeitnow, RemoteOK, Jobicy, Himalayas
  courses: Microsoft Learn catalog (fully free), curated free resources

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
import sys
import threading
import time
import traceback
from datetime import datetime, timedelta, timezone

import requests

from . import nlp

UA = {"User-Agent": "DegreePathAI/1.2 (student graduation project; daily fetch)"}
TIMEOUT = 40


def _log(msg):
    print("[feed] " + msg, file=sys.stderr, flush=True)
STALE_HOURS = 24
JOB_CAPS = {"workable": 220, "arbeitnow": 30, "jobicy": 20, "himalayas": 15,
            "remoteok": 10, "remotive": 5}          # ~300 open jobs, ~3/4 in Egypt
PER_COMPANY_CAP = 5
EXTRA_COURSES = 300          # non-tech courses (no skill match) added on top
MAX_AGE_DAYS = 60            # windowed sources: keep until closed, or this old
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
    "workable": {"name": "Workable (مصر)", "kind": "job", "site": "https://jobs.workable.com/search?location=Egypt",
                 "note": "وظائف داخل مصر، التقديم من صفحة الشركة على Workable"},
    "himalayas": {"name": "Himalayas", "kind": "job", "site": "https://himalayas.app",
                  "note": "رابط التقديم يفتح Himalayas"},
    "mslearn": {"name": "Microsoft Learn", "kind": "course", "site": "https://learn.microsoft.com/training/",
                "note": "مجاني بالكامل", "pricing": "free"},
    "curated": {"name": "مصادر مجانية مختارة", "kind": "course", "site": "https://www.freecodecamp.org/",
                "note": "مصادر مجانية من الأول للآخر (freeCodeCamp, Kaggle, Khan Academy, Google وغيرها)",
                "pricing": "free"},
    "arabic": {"name": "بالعربي (يوتيوب ومنصات عربية)", "kind": "course", "site": "https://www.youtube.com/",
               "note": "قوائم تشغيل ومنصات عربية مجانية بالكامل", "pricing": "free"},
    "coursera": {"name": "Coursera", "kind": "course", "site": "https://www.coursera.org/",
                 "note": "تجربة مجانية 7 أيام ثم اشتراك مدفوع (بعض الكورسات ليها خيار مراجعة مجاني، اتأكد في صفحة الكورس)",
                 "pricing": "paid"},
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


def fetch_workable(max_pages=140):
    """Every open Workable job located in Egypt (all fields). Full listing, so a job that
    disappears from it has been closed."""
    out, token = [], None
    for _ in range(max_pages):
        params = {"location": "Egypt", "limit": 20}
        if token:
            params["pageToken"] = token
        d = _get("https://jobs.workable.com/api/v1/jobs", params=params)
        for j in d.get("jobs", []):
            loc = j.get("location") or {}
            if (loc.get("countryName") or "") != "Egypt" or j.get("state") != "published":
                continue
            place = ", ".join(x for x in (loc.get("city"), loc.get("subregion"), "Egypt") if x)
            desc = " ".join(clean(j.get(k), 900) for k in ("description", "requirementsSection"))
            out.append(dict(
                ext_id=j["id"], title=clean(j["title"], 200),
                company=(j.get("company") or {}).get("title", ""),
                location=place, remote=1 if j.get("workplace") == "remote" else 0,
                url=j["url"], description=desc[:MAX_DESC],
                posted_at=_iso(j.get("created")), tags=j.get("department") or "",
                country="EG",
            ))
        token = d.get("nextPageToken")
        if not token:
            break
        time.sleep(0.1)
    return out


JOB_FETCHERS = {
    "workable": fetch_workable, "arbeitnow": fetch_arbeitnow, "jobicy": fetch_jobicy,
    "himalayas": fetch_himalayas, "remoteok": fetch_remoteok, "remotive": fetch_remotive,
}
FULL_LISTING = {"workable"}   # a missing job is closed; other sources only expose a window

FIELDS = [
    ("tech", "تكنولوجيا وبرمجة", r"software|developer|programmer|devops|data (?:scien|engineer|analy)|machine learning|\bai\b|\bit\b|cyber|security eng|backend|front-?end|full.?stack|qa |tester|cloud|network|system admin|sap |erp|odoo|mobile|android|ios|web |database|python|java\b|\.net|react|technical support|tech"),
    ("sales", "مبيعات وتسويق", r"sales|marketing|business development|seo|social media|brand|content|copywrit|growth|account manager|telesales|e-?commerce|media buyer|digital"),
    ("finance", "محاسبة ومالية", r"account|financ|audit|tax|treasury|payroll|bank|invest|credit|budget|procurement|purchas"),
    ("hr", "موارد بشرية وإدارة", r"\bhr\b|human resources|recruit|talent|admin|office manager|secretary|receptionist|executive assistant|project manag|operations manag|\bpmo\b|manager"),
    ("eng", "هندسة وتصنيع", r"engineer|mechanical|electrical|civil|architect|maintenance|production|manufactur|quality|safety|hse|technician|site |construction|planning"),
    ("health", "طب وصيدلة", r"doctor|physician|nurse|pharmac|medical|clinic|dental|dentist|health|patient|laborator|physio"),
    ("edu", "تعليم وتدريب", r"teacher|tutor|instructor|school|education|trainer|lecturer|curriculum|academic|kindergarten|nursery|coach"),
    ("design", "تصميم وإبداع", r"design|graphic|ui/?ux|video|motion|animat|photograph|editor|creative|illustrat|art director"),
    ("service", "خدمة عملاء ودعم", r"customer|support|call center|service|agent|care|representative|hospitality|hotel|front desk"),
    ("ops", "لوجستيات وعمليات", r"logistic|supply chain|warehouse|driver|delivery|shipping|inventory|operations|store|retail|cashier|supervisor|coordinator"),
    ("legal", "قانون واستشارات", r"legal|lawyer|law |counsel|compliance|consult|research"),
]
FIELD_LABELS = {k: v for k, v, _ in FIELDS}
FIELD_LABELS["other"] = "مجالات أخرى"


def classify_field(title, tags=""):
    """Broad field for the filter chips: title first, then tags/department."""
    for text in (title or "", f"{title} {tags}"):
        low = text.lower()
        for key, _label, rx in FIELDS:
            if re.search(rx, low):
                return key
    return "other"


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


def fetch_curated():
    """The hand-picked resources (free end to end) as feed items, so they show in the free group."""
    import hashlib
    from . import seed
    out = []
    for skill, title, url, kind in seed.RESOURCES:
        if "coursera.org" in url or url in getattr(seed, "PAID_URLS", ()):
            continue
        out.append(dict(ext_id=hashlib.sha1(url.encode()).hexdigest()[:16], title=title,
                        summary=f"{skill} ({kind})", url=url, level="", duration_min=0))
    return out


COURSERA_PAGES = 12          # 12 x 100 courses scanned from the public catalog
COURSERA_KEEP = 300


def fetch_coursera():
    """Public Coursera catalog (no key). Marked paid: 7-day trial, then subscription."""
    out = []
    for page in range(COURSERA_PAGES):
        d = _get("https://api.coursera.org/api/courses.v1?start=%d&limit=100"
                 "&fields=name,slug,description,primaryLanguages,workload" % (page * 100))
        for c in d.get("elements", []):
            langs = c.get("primaryLanguages") or []
            if langs and "en" not in langs and "ar" not in langs:
                continue
            out.append(dict(ext_id=c["id"], title=c["name"], summary=clean(c.get("description"), 400),
                            url="https://www.coursera.org/learn/" + c["slug"], level="",
                            duration_min=0))
        if not d.get("paging", {}).get("next"):
            break
    return out


def fetch_arabic():
    """Arabic free courses: YouTube playlists and Arabic platforms (static list, no API key)."""
    import hashlib
    from .arabic_courses import ARABIC_COURSES
    return [dict(ext_id=hashlib.sha1(c["url"].encode()).hexdigest()[:16], title=c["title"][:200],
                 summary=c["summary"], url=c["url"], level="", duration_min=0) for c in ARABIC_COURSES]


COURSE_FETCHERS = {"mslearn": fetch_mslearn, "curated": fetch_curated, "arabic": fetch_arabic,
                   "coursera": fetch_coursera}


# ------------------------------------------------------------------ refresh

def _title_skill_ids(title, tags, alias_index):
    return set(nlp.extract_skills(f"{title} {tags}", alias_index))


def _connect(db_path):
    from . import db as dbmod

    return dbmod.connect_dsn(db_path)


def claim_run(db_path):
    """Cross-worker guard: return a new run id, or None if a run started <20 min ago is unfinished."""
    from . import db as dbmod

    pg = dbmod.is_pg_dsn(db_path)
    db = _connect(db_path)
    try:
        if not pg:
            db.execute("BEGIN IMMEDIATE")
        busy = db.execute(
            """SELECT 1 FROM feed_runs WHERE finished_at IS NULL
               AND started_at > datetime('now', '-20 minutes')"""
        ).fetchone()
        if busy:
            if pg:
                db.rollback()
            else:
                db.execute("ROLLBACK")
            return None
        rid = db.execute("INSERT INTO feed_runs (started_at) VALUES (datetime('now'))").lastrowid
        db.commit()
        return rid
    finally:
        db.close()


def _url_closed(url):
    """True only when the posting page clearly says the job is gone (404/410)."""
    try:
        r = requests.get(url, headers=UA, timeout=12, allow_redirects=True, stream=True)
        r.close()
        return r.status_code in (404, 410)
    except Exception:
        return False


def _pick_jobs(db, src, items, alias_index):
    """Choose which jobs to store. Jobs already stored and still open at the source are
    always kept (a job leaves only when it closes). New ones fill the cap, spread across
    fields and companies."""
    cap = JOB_CAPS.get(src, 20)
    have = {r["ext_id"] for r in db.execute("SELECT ext_id FROM live_jobs WHERE source=?", (src,))}
    by_id = {it["ext_id"]: it for it in items if it.get("url")}
    keep = [by_id[e] for e in have if e in by_id]
    per_company = {}
    for it in keep:
        per_company[it["company"]] = per_company.get(it["company"], 0) + 1
    fresh = [it for e, it in by_id.items() if e not in have]
    fresh.sort(key=lambda it: it["posted_at"] or "", reverse=True)
    buckets = {}
    for it in fresh:
        it["field"] = classify_field(it["title"], it["tags"])
        buckets.setdefault(it["field"], []).append(it)
    order = sorted(buckets, key=lambda f: -len(buckets[f]))
    while len(keep) < cap and any(buckets.values()):
        for f in order:
            while buckets[f]:
                it = buckets[f].pop(0)
                if per_company.get(it["company"], 0) >= PER_COMPANY_CAP:
                    continue
                per_company[it["company"]] = per_company.get(it["company"], 0) + 1
                keep.append(it)
                break
            if len(keep) >= cap:
                break
    return keep


def _ingest_courses(db, src, items, alias_index, started):
    stored, extra, listed = 0, 0, set()
    for it in items:
        ids = nlp.extract_skills(f"{it['title']} {it['summary']}", alias_index)
        if not ids and src not in ("curated", "arabic"):
            if extra >= EXTRA_COURSES or src != "coursera":
                continue
            extra += 1
        fld = classify_field(it["title"], it["summary"][:200])
        listed.add(it["ext_id"])
        db.execute(
            """INSERT INTO live_courses (source, ext_id, title, summary, url, level,
               duration_min, fetched_at, field, pricing) VALUES (?,?,?,?,?,?,?,?,?,?)
               ON CONFLICT(source, ext_id) DO UPDATE SET title=excluded.title,
               summary=excluded.summary, url=excluded.url, level=excluded.level,
               duration_min=excluded.duration_min, fetched_at=excluded.fetched_at,
               field=excluded.field, pricing=excluded.pricing""",
            (src, it["ext_id"], it["title"][:200], it["summary"], it["url"],
             it["level"], it["duration_min"], _now(), fld,
             SOURCE_INFO.get(src, {}).get("pricing", "free")),
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
    # courses no longer in the catalog are gone
    db.execute("DELETE FROM live_courses WHERE source=? AND fetched_at < ?", (src, started))
    db.commit()
    return stored


def refresh(db_path, run_id=None):
    """Fetch every source, store jobs/courses, tag them with skills. Returns a report.

    Jobs persist between refreshes: a stored job is removed only when its source no longer
    lists it (closed/expired), or, for sources that only show a recent window, when its
    posting page is gone (404/410) or it is older than MAX_AGE_DAYS."""
    started = _now()
    report = {"started_at": started, "sources": {}}
    db = _connect(db_path)
    try:
        db.execute("SET lock_timeout = '20s'")
        db.execute("SET statement_timeout = '90s'")
        db.commit()
    except Exception:
        try:
            db.rollback()
        except Exception:
            pass
    _log("refresh start")
    if run_id is None:
        run_id = db.execute("INSERT INTO feed_runs (started_at) VALUES (?)", (started,)).lastrowid
        db.commit()
    alias_index = nlp.build_alias_index(db)

    for src, fn in JOB_FETCHERS.items():
        _log("jobs source " + src)
        try:
            items = fn()
            if not items:
                raise RuntimeError("source returned no jobs, keeping stored ones")
            kept = _pick_jobs(db, src, items, alias_index)
            seen = set()
            for it in kept:
                seen.add(it["ext_id"])
                text = f"{it['title']} {it['tags']} {it['description']}"
                ids = nlp.extract_skills(text, alias_index)
                core = _title_skill_ids(it["title"], it["tags"], alias_index)
                fld = it.get("field") or classify_field(it["title"], it["tags"])
                country = it.get("country", "")
                db.execute(
                    """INSERT INTO live_jobs (source, ext_id, title, company, location, remote,
                       url, description, posted_at, fetched_at, field, country)
                       VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
                       ON CONFLICT(source, ext_id) DO UPDATE SET title=excluded.title,
                       company=excluded.company, location=excluded.location, url=excluded.url,
                       description=excluded.description, posted_at=excluded.posted_at,
                       fetched_at=excluded.fetched_at, field=excluded.field,
                       country=excluded.country""",
                    (src, it["ext_id"], it["title"][:200], it["company"][:120], it["location"][:120],
                     it["remote"], it["url"], it["description"], it["posted_at"], _now(), fld, country),
                )
                jid = db.execute("SELECT id FROM live_jobs WHERE source=? AND ext_id=?",
                                 (src, it["ext_id"])).fetchone()["id"]
                db.execute("DELETE FROM live_job_skills WHERE job_id=?", (jid,))
                for sid in ids:
                    db.execute("INSERT INTO live_job_skills (job_id, skill_id, importance) VALUES (?,?,?)",
                               (jid, sid, 3 if sid in core else 2))
            db.commit()
            # jobs stored earlier but not kept this time
            listed = {it["ext_id"] for it in items}
            removed = 0
            checks = 0
            for r in db.execute("SELECT id, ext_id, url, posted_at FROM live_jobs WHERE source=?",
                                (src,)).fetchall():
                if r["ext_id"] in seen:
                    continue
                gone = False
                if src in FULL_LISTING:
                    gone = r["ext_id"] not in listed          # closed at the source
                else:
                    if r["ext_id"] in listed:
                        continue                              # still open, just over the cap
                    old = (r["posted_at"] or "9999") < (datetime.now(timezone.utc) - timedelta(days=MAX_AGE_DAYS)).strftime("%Y-%m-%d")
                    if old:
                        gone = True
                    elif checks < 40:
                        checks += 1
                        gone = _url_closed(r["url"])
                if gone:
                    db.execute("DELETE FROM live_jobs WHERE id=?", (r["id"],))
                    removed += 1
            db.commit()
            report["sources"][src] = {"ok": True, "fetched": len(items), "stored": len(kept),
                                      "removed_closed": removed}
        except Exception as e:  # keep old rows for this source, report the failure
            db.rollback()
            report["sources"][src] = {"ok": False, "error": str(e)[:200]}

    for src, fn in COURSE_FETCHERS.items():
        _log("courses source " + src)
        try:
            items = fn()
            if not items:
                raise RuntimeError("source returned no courses, keeping stored ones")
            stored = _ingest_courses(db, src, items, alias_index, started)
            report["sources"][src] = {"ok": True, "fetched": len(items), "stored": stored}
            _log("courses %s ok fetched=%d stored=%d" % (src, len(items), stored))
        except Exception as e:
            db.rollback()
            _log("courses %s FAILED %r" % (src, e))
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
    # first run after the free/paid split: fetch the paid group once
    for src in ("coursera", "arabic"):
        if not db.execute("SELECT 1 FROM live_courses WHERE source = ? LIMIT 1", (src,)).fetchone() \
                and not db.execute("SELECT 1 FROM feed_runs WHERE report LIKE ? LIMIT 1",
                                   ('%"' + src + '"%',)).fetchone():
            return True
    try:
        t = datetime.strptime(row["finished_at"], "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
    except Exception:
        return True
    return datetime.now(timezone.utc) - t > timedelta(hours=STALE_HOURS)


def refresh_in_background(app):
    """Start a refresh thread unless one is already running."""
    global _running
    dsn = app.config["DATABASE"]  # resolve now: `app` may be the current_app proxy, unusable in the thread
    with _lock:
        if _running:
            return False
        run_id = claim_run(dsn)
        if run_id is None:
            return False
        _running = True

    def work():
        global _running
        try:
            refresh(dsn, run_id)
            _log("refresh finished")
        except Exception:
            _log("refresh crashed: " + traceback.format_exc()[-600:])
            try:
                d = _connect(dsn)
                d.execute("UPDATE feed_runs SET finished_at=?, report=? WHERE id=?",
                          (_now(), json.dumps({"error": "crashed"}), run_id))
                d.commit()
                d.close()
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


_extras_lock = threading.Lock()
_extras_running = False


def _run_extra_source(db_path, src):
    """Fetch and store one course source on its own connection, independent of the full refresh."""
    db = _connect(db_path)
    try:
        try:
            db.execute("SET lock_timeout = '20s'")
            db.execute("SET statement_timeout = '90s'")
            db.commit()
        except Exception:
            db.rollback()
        started = _now()
        items = COURSE_FETCHERS[src]()
        n = _ingest_courses(db, src, items, nlp.build_alias_index(db), started)
        _log("extra %s stored=%d" % (src, n))
    except Exception as e:
        _log("extra %s FAILED %r" % (src, e))
        try:
            db.rollback()
        except Exception:
            pass
    finally:
        try:
            db.close()
        except Exception:
            pass


def ensure_extras(app, db):
    """Arabic list (tiny, static) is stored right away; the paid Coursera group runs in a
    background thread. Both run on their own, so a slow full refresh never blocks them."""
    global _extras_running
    dsn = app.config["DATABASE"]
    try:
        have = {r["source"]: r["c"] for r in db.execute(
            "SELECT source, COUNT(*) AS c FROM live_courses WHERE source IN ('arabic','coursera') GROUP BY source")}
        from .arabic_courses import ARABIC_COURSES
        need_ar = have.get("arabic", 0) != len(ARABIC_COURSES)
        # rows stored by older versions carry pricing=free: flip them to paid right away
        db.execute("UPDATE live_courses SET pricing='paid' WHERE source='coursera' AND COALESCE(pricing,'free')!='paid'")
        db.commit()
        need_pa = db.execute("SELECT COUNT(*) AS n FROM live_courses WHERE source='coursera' AND pricing='paid'").fetchone()["n"] == 0
    except Exception:
        return False
    if not (need_ar or need_pa):
        return False
    with _extras_lock:
        if _extras_running:
            return False
        _extras_running = True

    def work():
        global _extras_running
        try:
            if need_ar:
                _run_extra_source(dsn, "arabic")
            if need_pa:
                _run_extra_source(dsn, "coursera")
        finally:
            with _extras_lock:
                _extras_running = False

    threading.Thread(target=work, daemon=True).start()
    return True


def maybe_refresh(app, db):
    """Called on feed requests and at start-up: refresh when the data is >24h old."""
    if app.config.get("FEED_AUTO", True):
        ensure_extras(app, db)
        if is_stale(db):
            return refresh_in_background(app)
    return False


# ------------------------------------------------------- linking: job -> courses

def courses_for_skill(db, skill_id, limit=3):
    """Free courses for one skill: mix providers so one site never dominates."""
    rows = db.execute(
        """SELECT c.title, c.url, c.source, c.level, c.duration_min FROM live_courses c
           JOIN live_course_skills cs ON cs.course_id = c.id
           WHERE cs.skill_id = ? AND COALESCE(c.pricing, 'free') = 'free' ORDER BY c.source,
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
                    "free": "free",
                    "level": r["level"], "duration_min": r["duration_min"],
                })
        i += 1
        if i > 10:
            break
    return picked
