import copy
from fastapi.testclient import TestClient

from src import app as app_module

client = TestClient(app_module.app)


def setup_function():
    # ARRANGE: reset the in-memory activities before each test
    app_module.reset_data()


def test_root_redirect():
    # ARRANGE: (setup_function already ran)
    # ACT
    resp = client.get("/")
    # ASSERT
    assert resp.status_code == 307
    assert "/static/index.html" in resp.headers["location"]


def test_get_activities_structure():
    # ARRANGE: nothing additional
    # ACT
    resp = client.get("/activities")
    # ASSERT
    assert resp.status_code == 200
    data = resp.json()
    # expect at least a couple of known activities
    assert "Chess Club" in data
    assert isinstance(data["Chess Club"], dict)


def test_successful_signup_and_duplicate():
    # ARRANGE: choose an existing activity
    activity = "Chess Club"
    email = "new@student.edu"

    # ACT
    resp1 = client.post(f"/activities/{activity}/signup?email={email}")
    # ASSERT first signup succeeds
    assert resp1.status_code == 200
    assert "Signed up" in resp1.json()["message"]

    # ACT again with same email
    resp2 = client.post(f"/activities/{activity}/signup?email={email}")
    # ASSERT duplicate rejected
    assert resp2.status_code == 400


def test_remove_participant_flow():
    # ARRANGE: manually add someone to Gym Class participants
    activity = "Gym Class"
    email = "drop@student.edu"
    app_module.activities[activity]["participants"].append(email)

    # ACT: remove them
    resp = client.delete(f"/activities/{activity}/participants?email={email}")
    # ASSERT
    assert resp.status_code == 200
    assert email not in app_module.activities[activity]["participants"]

    # ACT again, should 404
    resp2 = client.delete(f"/activities/{activity}/participants?email={email}")
    assert resp2.status_code == 404


def test_activity_not_found_errors():
    # ARRANGE
    bad = "NoSuchActivity"
    # ACT & ASSERT
    assert client.post(f"/activities/{bad}/signup?email=x").status_code == 404
    assert client.delete(f"/activities/{bad}/participants?email=x").status_code == 404
