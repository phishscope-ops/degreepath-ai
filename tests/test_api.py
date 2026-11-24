"""End-to-end API tests (persons 3-8, 12-14 acceptance)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest

from degreepath import create_app


@pytest.fixture()
def client(tmp_path):
    app = create_app({"DATABASE": str(tmp_path / "test.sqlite3"), "TESTING": True, "FEED_AUTO": False})
    return app.test_client()


def auth_headers(client, email="student@example.com"):
    res = client.post(
        "/api/register",
        json={"email": email, "password": "secret123", "name": "Test Student"},
    )
    assert res.status_code == 201, res.get_json()
    return {"Authorization": "Bearer " + res.get_json()["token"]}


def test_register_login_logout(client):
    h = auth_headers(client)
    res = client.get("/api/me", headers=h)
    assert res.status_code == 200
    assert res.get_json()["user"]["email"] == "student@example.com"

    res = client.post("/api/login", json={"email": "student@example.com", "password": "secret123"})
    assert res.status_code == 200

    res = client.post("/api/login", json={"email": "student@example.com", "password": "wrong"})
    assert res.status_code == 401

    res = client.post("/api/logout", headers=h)
    assert res.status_code == 200
    assert client.get("/api/me", headers=h).status_code == 401


def test_register_validation(client):
    assert client.post("/api/register", json={"email": "bad", "password": "secret123", "name": "X"}).status_code == 400
    assert client.post("/api/register", json={"email": "a@b.co", "password": "123", "name": "X"}).status_code == 400
    auth_headers(client)
    assert client.post(
        "/api/register", json={"email": "student@example.com", "password": "secret123", "name": "Dup"}
    ).status_code == 409


def test_requires_auth(client):
    for path in ["/api/profile", "/api/courses", "/api/skills", "/api/jobs", "/api/matches"]:
        assert client.get(path).status_code == 401, path


def test_profile_roundtrip(client):
    h = auth_headers(client)
    res = client.put("/api/profile", json={"university": "Cairo University", "major": "CS", "study_year": "الثالثة"}, headers=h)
    assert res.status_code == 200
    p = client.get("/api/profile", headers=h).get_json()["profile"]
    assert p["university"] == "Cairo University"
    assert p["major"] == "CS"


def test_course_add_extracts_skills(client):
    h = auth_headers(client)
    res = client.post(
        "/api/courses",
        json={"title": "Python Programming", "description": "Covers Python, pandas and data analysis with SQL."},
        headers=h,
    )
    assert res.status_code == 201
    names = {s["name"] for s in res.get_json()["extracted_skills"]}
    assert {"Python", "Pandas", "Data Analysis", "SQL"} <= names

    skills = client.get("/api/skills", headers=h).get_json()["skills"]
    assert {s["name"] for s in skills} >= {"Python", "SQL"}

    courses = client.get("/api/courses", headers=h).get_json()["courses"]
    assert len(courses) == 1
    cid = courses[0]["id"]
    assert client.delete(f"/api/courses/{cid}", headers=h).status_code == 200
    assert client.get("/api/courses", headers=h).get_json()["courses"] == []


def test_users_are_isolated(client):
    h1 = auth_headers(client, "one@example.com")
    h2 = auth_headers(client, "two@example.com")
    client.post("/api/courses", json={"title": "Python Programming", "description": "python sql"}, headers=h1)
    assert client.get("/api/courses", headers=h2).get_json()["courses"] == []


def test_extract_endpoint(client):
    h = auth_headers(client)
    res = client.post("/api/extract", json={"text": "Excel and Power BI dashboards"}, headers=h)
    names = {s["name"] for s in res.get_json()["skills"]}
    assert {"Excel", "Power BI"} <= names


def test_jobs_and_matching_and_roadmap(client):
    h = auth_headers(client)
    jobs = client.get("/api/jobs", headers=h).get_json()["jobs"]
    assert len(jobs) >= 8
    da = next(j for j in jobs if j["title"] == "Data Analyst")

    # Add a course covering part of the Data Analyst requirements
    client.post(
        "/api/courses",
        json={"title": "Data Analysis with Excel and SQL", "description": "Excel, SQL, data analysis, statistics"},
        headers=h,
    )

    matches = client.get("/api/matches", headers=h).get_json()["matches"]
    assert matches, "expected ranked matches"
    pcts = [m["match_pct"] for m in matches]
    assert pcts == sorted(pcts, reverse=True)
    da_match = next(m for m in matches if m["title"] == "Data Analyst")
    assert 0 < da_match["match_pct"] <= 100
    matched_names = {s["name"] for s in da_match["matched"]}
    missing_names = {s["name"] for s in da_match["missing"]}
    assert "SQL" in matched_names
    assert matched_names.isdisjoint(missing_names)

    res = client.get(f"/api/analysis/{da['id']}", headers=h)
    assert res.status_code == 200
    data = res.get_json()
    assert data["job"]["title"] == "Data Analyst"
    assert 0 < data["match_pct"] <= 100
    assert isinstance(data["roadmap"], list)
    if data["roadmap"]:
        step = data["roadmap"][0]
        assert step["step"] == 1
        assert step["skill"]
        assert "resources" in step
        # core skills come before nice-to-have
        imps = [s["importance"] for s in data["roadmap"]]
        assert imps == sorted(imps, reverse=True)


def test_catalog_and_quick_add(client):
    h = auth_headers(client)
    cat = client.get("/api/catalog", headers=h).get_json()["catalog"]
    assert len(cat) >= 30
    db_course = next(c for c in cat if c["title"] == "قواعد البيانات")
    res = client.post("/api/courses/from-catalog", json={"catalog_id": db_course["id"]}, headers=h)
    assert res.status_code == 201
    names = {s["name"] for s in res.get_json()["extracted_skills"]}
    assert "SQL" in names
    # duplicate add is refused
    assert client.post("/api/courses/from-catalog", json={"catalog_id": db_course["id"]}, headers=h).status_code == 409
    assert client.post("/api/courses/from-catalog", json={"catalog_id": 9999}, headers=h).status_code == 404


def test_empty_student_gets_zero_match(client):
    h = auth_headers(client)
    matches = client.get("/api/matches", headers=h).get_json()["matches"]
    assert all(m["match_pct"] == 0 for m in matches)


def test_feed_linking_and_status(client):
    """Insert a fake live job + course and check job -> missing skill -> course -> apply link."""
    from degreepath.db import get_db

    h = auth_headers(client)
    app = client.application
    with app.app_context():
        db = get_db()
        sid = db.execute("SELECT id FROM skills WHERE name='Python'").fetchone()["id"]
        jid = db.execute(
            "INSERT INTO live_jobs (source, ext_id, title, company, url) VALUES ('remotive','1','Python Dev','Acme','https://example.com/apply')"
        ).lastrowid
        db.execute("INSERT INTO live_job_skills (job_id, skill_id, importance) VALUES (?,?,3)", (jid, sid))
        cid = db.execute(
            "INSERT INTO live_courses (source, ext_id, title, url) VALUES ('mslearn','c1','Learn Python','https://learn.microsoft.com/x')"
        ).lastrowid
        db.execute("INSERT INTO live_course_skills (course_id, skill_id) VALUES (?,?)", (cid, sid))
        db.commit()
    st = client.get("/api/feed/status").get_json()
    assert st["total_jobs"] == 1 and st["total_courses"] == 1
    lst = client.get("/api/feed/jobs", headers=h).get_json()
    assert lst["jobs"][0]["apply_url"] == "https://example.com/apply"
    d = client.get(f"/api/feed/jobs/{jid}", headers=h).get_json()["job"]
    urls = [c["url"] for s in d["roadmap"] for c in s["courses"]]
    assert "https://learn.microsoft.com/x" in urls
    assert client.get("/api/feed/jobs").status_code == 401
