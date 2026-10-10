from fastapi.testclient import TestClient

from src.app import activities, app


client = TestClient(app)


def test_get_activities_returns_activity_data():
    # Arrange
    activity_name = "Chess Club"

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    payload = response.json()
    assert activity_name in payload
    assert "participants" in payload[activity_name]
    assert "max_participants" in payload[activity_name]


def test_signup_for_activity_success():
    # Arrange
    activity_name = "Chess Club"
    email = "new.student@mergington.edu"
    original_participants = list(activities[activity_name]["participants"])
    activities[activity_name]["participants"] = [email for email in original_participants]

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email=unique.student@mergington.edu")

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == "Signed up unique.student@mergington.edu for Chess Club"
    assert "unique.student@mergington.edu" in activities[activity_name]["participants"]

    # Cleanup
    activities[activity_name]["participants"] = original_participants


def test_signup_for_activity_duplicate_email_returns_400():
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_signup_for_activity_when_full_returns_400():
    # Arrange
    activity_name = "Chess Club"
    email = "late.student@mergington.edu"
    original_participants = list(activities[activity_name]["participants"])
    max_participants = activities[activity_name]["max_participants"]
    activities[activity_name]["participants"] = [f"student{i}@mergington.edu" for i in range(max_participants)]

    try:
        # Act
        response = client.post(f"/activities/{activity_name}/signup?email={email}")

        # Assert
        assert response.status_code == 400
        assert response.json()["detail"] == "Activity is full"
    finally:
        activities[activity_name]["participants"] = original_participants


def test_unregister_participant_from_activity_success():
    # Arrange
    activity_name = "Chess Club"
    email = "temp.student@mergington.edu"
    original_participants = list(activities[activity_name]["participants"])
    activities[activity_name]["participants"] = original_participants + [email]

    try:
        # Act
        response = client.delete(f"/activities/{activity_name}/participants/{email}")

        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Removed {email} from {activity_name}"
        assert email not in activities[activity_name]["participants"]
    finally:
        activities[activity_name]["participants"] = original_participants


def test_unregister_missing_participant_returns_404():
    # Arrange
    activity_name = "Chess Club"
    email = "missing.student@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity_name}/participants/{email}")

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Student not found in this activity"


def test_signup_for_missing_activity_returns_404():
    # Arrange
    activity_name = "Does Not Exist"
    email = "someone@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"
