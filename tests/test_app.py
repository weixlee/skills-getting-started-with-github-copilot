import pytest
from fastapi.testclient import TestClient
from src.app import app, activities

# Initial activities data for resetting
initial_activities = {
    "Chess Club": {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
    },
    "Programming Class": {
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
    },
    "Gym Class": {
        "description": "Physical education and sports activities",
        "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
        "max_participants": 30,
        "participants": ["john@mergington.edu", "olivia@mergington.edu"]
    },
    "Basketball Team": {
        "description": "Competitive basketball training and intramural games",
        "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
        "max_participants": 15,
        "participants": ["mason@mergington.edu"]
    },
    "Tennis Club": {
        "description": "Learn tennis skills and compete in matches",
        "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:00 PM",
        "max_participants": 10,
        "participants": ["ava@mergington.edu"]
    },
    "Art Studio": {
        "description": "Explore painting, drawing, and mixed media techniques",
        "schedule": "Mondays and Wednesdays, 3:30 PM - 5:00 PM",
        "max_participants": 16,
        "participants": ["lily@mergington.edu", "noah@mergington.edu"]
    },
    "Drama Club": {
        "description": "Acting, theater production, and stage performance",
        "schedule": "Thursdays, 3:30 PM - 5:00 PM",
        "max_participants": 20,
        "participants": ["grace@mergington.edu"]
    },
    "Science Club": {
        "description": "Hands-on experiments and STEM research projects",
        "schedule": "Fridays, 3:00 PM - 4:30 PM",
        "max_participants": 18,
        "participants": ["lucas@mergington.edu", "isabella@mergington.edu"]
    },
    "Debate Team": {
        "description": "Develop public speaking and argumentation skills",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 5:00 PM",
        "max_participants": 14,
        "participants": ["alexander@mergington.edu"]
    }
}

@pytest.fixture(autouse=True)
def reset_activities():
    activities.clear()
    activities.update(initial_activities)

client = TestClient(app)

def test_root_redirect():
    # Arrange: No special setup needed

    # Act: Make GET request to root
    response = client.get("/")

    # Assert: Should redirect to static index
    assert response.status_code == 307  # Temporary redirect
    assert response.headers["location"] == "/static/index.html"

def test_get_activities():
    # Arrange: Activities are set up by fixture

    # Act: Make GET request to activities endpoint
    response = client.get("/activities")

    # Assert: Returns 200 and correct data structure
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert data["Chess Club"]["description"] == "Learn strategies and compete in chess tournaments"
    assert len(data["Chess Club"]["participants"]) == 2

def test_signup_success():
    # Arrange: Use initial activities data

    # Act: Attempt to sign up a new student
    response = client.post("/activities/Chess Club/signup?email=newstudent@mergington.edu")

    # Assert: Signup succeeds and student is added
    assert response.status_code == 200
    data = response.json()
    assert "Signed up newstudent@mergington.edu for Chess Club" == data["message"]

    # Verify added
    response = client.get("/activities")
    data = response.json()
    assert "newstudent@mergington.edu" in data["Chess Club"]["participants"]

def test_signup_duplicate():
    # Arrange: michael@mergington.edu is already signed up for Chess Club

    # Act: Try to sign up the same student again
    response = client.post("/activities/Chess Club/signup?email=michael@mergington.edu")

    # Assert: Returns 400 with error message
    assert response.status_code == 400
    data = response.json()
    assert "Student already signed up for this activity" == data["detail"]

def test_signup_invalid_activity():
    # Arrange: No activity named "Invalid Activity" exists

    # Act: Attempt signup for non-existent activity
    response = client.post("/activities/Invalid Activity/signup?email=test@test.com")

    # Assert: Returns 404 with error
    assert response.status_code == 404
    data = response.json()
    assert "Activity not found" == data["detail"]

def test_delete_participant_success():
    # Arrange: michael@mergington.edu is enrolled in Chess Club

    # Act: Delete the participant
    response = client.delete("/activities/Chess Club/participants/michael@mergington.edu")

    # Assert: Deletion succeeds and participant is removed
    assert response.status_code == 200
    data = response.json()
    assert "Removed michael@mergington.edu from Chess Club" == data["message"]

    # Verify removed
    response = client.get("/activities")
    data = response.json()
    assert "michael@mergington.edu" not in data["Chess Club"]["participants"]

def test_delete_invalid_activity():
    # Arrange: No activity named "Invalid Activity" exists

    # Act: Attempt to delete from non-existent activity
    response = client.delete("/activities/Invalid Activity/participants/test@test.com")

    # Assert: Returns 404
    assert response.status_code == 404
    data = response.json()
    assert "Activity not found" == data["detail"]

def test_delete_not_enrolled():
    # Arrange: notenrolled@test.com is not in Chess Club

    # Act: Try to delete non-enrolled participant
    response = client.delete("/activities/Chess Club/participants/notenrolled@test.com")

    # Assert: Returns 404
    assert response.status_code == 404
    data = response.json()
    assert "Participant not enrolled in this activity" == data["detail"]