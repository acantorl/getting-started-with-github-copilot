from fastapi.testclient import TestClient

from src.app import app


client = TestClient(app)


def test_unregister_participant_from_activity():
    activity_name = "Chess Club"
    email = "new.student@mergington.edu"

    # Ensure participant is not already present.
    response = client.delete(f"/activities/{activity_name}/participants/{email}")
    assert response.status_code in {200, 404}

    signup_response = client.post(f"/activities/{activity_name}/signup?email={email}")
    assert signup_response.status_code == 200

    response = client.get("/activities")
    assert email in response.json()[activity_name]["participants"]

    delete_response = client.delete(f"/activities/{activity_name}/participants/{email}")
    assert delete_response.status_code == 200
    assert delete_response.json()["message"] == f"Removed {email} from {activity_name}"

    response = client.get("/activities")
    assert email not in response.json()[activity_name]["participants"]


def test_unregister_missing_participant_returns_404():
    activity_name = "Chess Club"
    email = "missing.student@mergington.edu"

    response = client.delete(f"/activities/{activity_name}/participants/{email}")
    assert response.status_code == 404
