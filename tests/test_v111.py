import pytest
from degreepath import create_app


@pytest.fixture()
def client(tmp_path):
    return create_app({"DATABASE": str(tmp_path / "t.sqlite3"), "TESTING": True, "FEED_AUTO": False}).test_client()


def _auth(client):
    r = client.post('/api/register', json={"name": "T", "email": "v111@x.com", "password": "password123"})
    j = r.get_json(); return {"Authorization": "Bearer " + (j.get("token") or j.get("access_token"))}


def test_catalog_has_four_departments(client):
    h = _auth(client)
    d = client.get('/api/catalog', headers=h).get_json()
    assert {x["key"] for x in d["departments"]} == {"ims", "bis", "bmt", "act"}
    assert {x["department"] for x in d["catalog"]} == {"ims", "bis", "bmt", "act"}


def test_bulk_add_and_skills(client):
    h = _auth(client)
    cat = client.get('/api/catalog', headers=h).get_json()["catalog"]
    ids = [x["id"] for x in cat if x["department"] == "act" and x["level"] == 3 and x["semester"] == 1]
    r = client.post('/api/courses/from-catalog', headers=h, json={"catalog_ids": ids}).get_json()
    assert r["added"] == len(ids) and r["extracted_skills"]
    r2 = client.post('/api/courses/from-catalog', headers=h, json={"catalog_ids": ids}).get_json()
    assert r2["added"] == 0 and r2["skipped"] == len(ids)


def test_cyber_track_real_skills_and_sources(client):
    h = _auth(client)
    careers = client.get('/api/careers', headers=h).get_json()["careers"]
    assert len(careers) >= 40
    jid = [c["id"] for c in careers if c["title"] == "Cybersecurity Analyst"][0]
    r = client.get(f'/api/careers/{jid}', headers=h).get_json()
    names = {s["skill"] for st in r["stages"] for s in st["skills"]}
    assert {"SIEM", "Log Analysis", "Incident Response", "MITRE ATT&CK"} <= names
    assert len(r["sources"]) >= 3


def test_every_new_track_has_sources(client):
    h = _auth(client)
    for c in client.get('/api/careers', headers=h).get_json()["careers"]:
        if c["category"] in ("finance", "iot") or c["title"] in ("SOC Analyst", "BI Developer"):
            r = client.get(f'/api/careers/{c["id"]}', headers=h).get_json()
            assert len(r["sources"]) >= 2, c["title"]
