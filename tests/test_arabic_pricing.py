"""Arabic search, free/paid course split, add-a-skill flow."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest

from degreepath import arsearch, create_app
from degreepath.db import get_db


@pytest.fixture()
def client(tmp_path):
    app = create_app({"DATABASE": str(tmp_path / "t.sqlite3"), "TESTING": True, "FEED_AUTO": False})
    c = app.test_client()
    with app.app_context():
        db = get_db()
        rows = [
            ("mslearn", "a1", "Python for beginners", "Learn Python programming basics", "free"),
            ("mslearn", "a2", "Introduction to cybersecurity", "Security fundamentals", "free"),
            ("curated", "a3", "SQLBolt - Interactive SQL lessons", "SQL (course)", "free"),
            ("coursera", "c1", "Python for Everybody", "Python programming specialization", "paid"),
            ("coursera", "c2", "Google Data Analytics", "data analysis with spreadsheets and SQL", "paid"),
        ]
        for src, ext, title, summ, pr in rows:
            db.execute("INSERT INTO live_courses (source, ext_id, title, summary, url, pricing) VALUES (?,?,?,?,?,?)",
                       (src, ext, title, summ, "https://example.org/" + ext, pr))
        db.commit()
    return c


def headers(client, email="s@example.com"):
    r = client.post("/api/register", json={"email": email, "password": "secret123", "name": "T"})
    assert r.status_code == 201
    return {"Authorization": "Bearer " + r.get_json()["token"]}


def titles(res):
    return [c["title"] for c in res.get_json()["courses"]]


def test_arabic_query_finds_english_courses(client):
    h = headers(client)
    assert "Python for beginners" in titles(client.get("/api/feed/courses?q=بايثون", headers=h))
    assert "Introduction to cybersecurity" in titles(client.get("/api/feed/courses?q=الأمن السيبراني", headers=h))
    assert "SQLBolt - Interactive SQL lessons" in titles(client.get("/api/feed/courses?q=اس كيو ال", headers=h))
    r = client.get("/api/feed/courses?q=كورس بايثون للمبتدئين", headers=h)
    assert titles(r) == ["Python for beginners"]


def test_english_query_still_works(client):
    h = headers(client)
    assert titles(client.get("/api/feed/courses?q=python", headers=h)) == ["Python for beginners"]
    assert titles(client.get("/api/feed/courses?q=zzzzqq", headers=h)) == []


def test_free_and_paid_never_mixed(client):
    h = headers(client)
    free = client.get("/api/feed/courses", headers=h).get_json()
    assert free["pricing"] == "free" and free["total"] == 3
    assert all(c["free"] == "free" and "coursera" not in c["url"] for c in free["courses"])
    paid = client.get("/api/feed/courses?pricing=paid", headers=h).get_json()
    assert paid["total"] == 2
    assert all(c["free"] == "paid" and c["pricing_note"] for c in paid["courses"])
    # arabic search inside the paid group only returns paid
    p = client.get("/api/feed/courses?pricing=paid&q=بايثون", headers=h)
    assert titles(p) == ["Python for Everybody"]


def test_roadmap_never_recommends_paid(client):
    from degreepath import feed
    app = client.application
    with app.app_context():
        db = get_db()
        sid = db.execute("SELECT id FROM skills WHERE name = 'Python'").fetchone()["id"]
        for ext in ("a1", "c1"):
            cid = db.execute("SELECT id FROM live_courses WHERE ext_id = ?", (ext,)).fetchone()["id"]
            db.execute("INSERT INTO live_course_skills (course_id, skill_id) VALUES (?, ?)", (cid, sid))
        db.commit()
        got = feed.courses_for_skill(db, sid, limit=10)
    assert got and all("coursera" not in c["url"] and c["free"] == "free" for c in got)


def test_status_reports_both_groups(client):
    st = client.get("/api/feed/status").get_json()
    assert st["total_courses"] == 3 and st["paid_courses"] == 2


def test_add_skill_by_arabic_name(client):
    h = headers(client)
    r = client.get("/api/skills/search?q=بايثون", headers=h).get_json()["skills"]
    assert r and r[0]["name"] == "Python" and not r[0]["have"]
    add = client.post("/api/skills/add", json={"skill_id": r[0]["id"]}, headers=h)
    assert add.status_code == 201
    assert client.post("/api/skills/add", json={"skill_id": r[0]["id"]}, headers=h).get_json()["already"] is True
    mine = client.get("/api/skills", headers=h).get_json()["skills"]
    assert [s["name"] for s in mine] == ["Python"]
    assert client.get("/api/skills/search?q=python", headers=h).get_json()["skills"][0]["have"] is True
    assert client.post("/api/skills/add", json={"skill_id": 999999}, headers=h).status_code == 404
    assert client.post("/api/skills/add", json={}, headers=h).status_code == 400


def test_arabic_normalisation_and_short_words():
    g = arsearch.parse("أمن المعلومات")
    assert arsearch.matches(g, "Information Security Basics")
    assert arsearch.matches(arsearch.parse("ذكاء اصطناعي"), "AI for everyone")
    assert not arsearch.matches(arsearch.parse("ذكاء اصطناعي"), "How to maintain your garden")
    assert arsearch.norm("الإِسْلَام") == "الاسلام"


def test_arabic_job_search(client):
    app = client.application
    with app.app_context():
        db = get_db()
        db.execute("""INSERT INTO live_jobs (source, ext_id, title, company, location, url, description, fetched_at, field, country)
                      VALUES ('workable','j1','Senior Accountant','Acme','Cairo, Egypt','https://e.org/j','desc', datetime('now'),'finance','EG')""")
        db.commit()
    h = headers(client)
    r = client.get("/api/feed/jobs?q=محاسب", headers=h).get_json()
    assert [j["title"] for j in r["jobs"]] == ["Senior Accountant"]
