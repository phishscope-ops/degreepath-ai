"""Owner dashboard tests: login gate, token auth, overview contents."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest

from degreepath import create_app


@pytest.fixture()
def client(tmp_path):
    app = create_app(
        {
            "DATABASE": str(tmp_path / "test.sqlite3"),
            "TESTING": True,
            "FEED_AUTO": False,
            "ADMIN_PASSWORD": "owner-secret",
        }
    )
    return app.test_client()


@pytest.fixture()
def client_no_password(tmp_path):
    app = create_app(
        {
            "DATABASE": str(tmp_path / "test2.sqlite3"),
            "TESTING": True,
            "FEED_AUTO": False,
            "ADMIN_PASSWORD": "",
        }
    )
    return app.test_client()


def _register_student(client):
    res = client.post(
        "/api/register",
        json={"email": "student@example.com", "password": "secret123", "name": "Test Student"},
    )
    assert res.status_code == 201
    return res.get_json()["token"]


def test_admin_disabled_without_password(client_no_password):
    res = client_no_password.post("/api/admin/login", json={"password": "x"})
    assert res.status_code == 403
    res = client_no_password.get("/api/admin/overview")
    assert res.status_code == 403


def test_admin_login_and_overview(client):
    # wrong password
    res = client.post("/api/admin/login", json={"password": "nope"})
    assert res.status_code == 401

    # no token -> rejected
    res = client.get("/api/admin/overview")
    assert res.status_code == 401

    # a regular user token is not an admin token
    user_token = _register_student(client)
    res = client.get("/api/admin/overview", headers={"Authorization": "Bearer " + user_token})
    assert res.status_code == 401

    # correct password -> token -> overview lists the registered account
    res = client.post("/api/admin/login", json={"password": "owner-secret"})
    assert res.status_code == 200
    token = res.get_json()["token"]
    res = client.get("/api/admin/overview", headers={"Authorization": "Bearer " + token})
    assert res.status_code == 200
    data = res.get_json()
    assert data["stats"]["total_users"] == 1
    assert data["stats"]["signups_today"] == 1
    assert data["users"][0]["email"] == "student@example.com"

    # logout invalidates the token
    res = client.post("/api/admin/logout", headers={"Authorization": "Bearer " + token})
    assert res.status_code == 200
    res = client.get("/api/admin/overview", headers={"Authorization": "Bearer " + token})
    assert res.status_code == 401


def test_admin_page_served(client):
    res = client.get("/admin")
    assert res.status_code == 200
    assert "admin.js" in res.get_data(as_text=True)
