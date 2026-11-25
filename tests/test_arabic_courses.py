"""Arabic free course list: valid, stored in the free group, never mixed with Coursera."""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest

from degreepath import create_app, feed, nlp
from degreepath.arabic_courses import ARABIC_COURSES
from degreepath.db import get_db


@pytest.fixture()
def app(tmp_path):
    return create_app({"DATABASE": str(tmp_path / "t.sqlite3"), "TESTING": True, "FEED_AUTO": False})


def test_list_is_valid():
    urls = [c["url"] for c in ARABIC_COURSES]
    assert len(urls) == len(set(urls)) >= 40
    for c in ARABIC_COURSES:
        assert c["url"].startswith("https://") and c["title"] and c["summary"]
        assert "coursera" not in c["url"].lower()
    assert sum(bool(re.search(r"[\u0600-\u06FF]", c["title"] + c["summary"])) for c in ARABIC_COURSES) >= 40


def test_arabic_stored_free_and_filterable(app):
    with app.app_context():
        db = get_db()
        items = feed.fetch_arabic()
        n = feed._ingest_courses(db, "arabic", items, nlp.build_alias_index(db), feed._now())
        assert n == len(ARABIC_COURSES)
        assert db.execute("SELECT COUNT(*) AS n FROM live_courses WHERE source='arabic' AND COALESCE(pricing,'free')='free'").fetchone()["n"] == n
        db.execute("INSERT INTO live_courses (source, ext_id, title, summary, url, pricing) VALUES ('coursera','c1','X','Y','https://www.coursera.org/learn/x','paid')")
        db.commit()
    c = app.test_client()
    r = c.post("/api/register", json={"email": "a@example.com", "password": "secret123", "name": "T"})
    h = {"Authorization": "Bearer " + r.get_json()["token"]}
    free = c.get("/api/feed/courses?limit=100", headers=h).get_json()
    assert free["total"] == n and free["courses"][0]["provider"].startswith("بالعربي")
    assert all("coursera" not in x["url"] for x in free["courses"])
    ar = c.get("/api/feed/courses?source=arabic&limit=100", headers=h).get_json()
    assert ar["total"] == n
    paid = c.get("/api/feed/courses?pricing=paid", headers=h).get_json()
    assert [x["title"] for x in paid["courses"]] == ["X"]
    st = c.get("/api/feed/status").get_json()
    assert st["arabic_courses"] == n and st["paid_courses"] == 1


def test_arabic_search_hits_python_playlist(app):
    with app.app_context():
        db = get_db()
        feed._ingest_courses(db, "arabic", feed.fetch_arabic(), nlp.build_alias_index(db), feed._now())
    c = app.test_client()
    r = c.post("/api/register", json={"email": "b@example.com", "password": "secret123", "name": "T"})
    h = {"Authorization": "Bearer " + r.get_json()["token"]}
    res = c.get("/api/feed/courses?q=بايثون&source=arabic", headers=h).get_json()
    assert res["total"] >= 2


def test_background_refresh_works_with_current_app_proxy(app, monkeypatch):
    """Regression: api.py passes the current_app proxy; the thread must not touch it."""
    import threading
    from flask import current_app
    seen = {}
    done = threading.Event()

    def fake_refresh(dsn, run_id):
        seen["dsn"] = dsn
        done.set()
        return {}

    monkeypatch.setattr(feed, "refresh", fake_refresh)
    monkeypatch.setattr(feed, "_running", False)
    with app.app_context():
        assert feed.refresh_in_background(current_app) is True
    assert done.wait(10) and seen["dsn"] == app.config["DATABASE"]
