"""
Tests for the Mergington High School Activities API
"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add src directory to path so we can import app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app


@pytest.fixture
def client():
    """Create a test client"""
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """Reset activities to initial state after each test"""
    from app import activities
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
            "description": "Join our competitive basketball team and develop athletic skills",
            "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
            "max_participants": 15,
            "participants": ["alex@mergington.edu"]
        },
        "Tennis Club": {
            "description": "Learn tennis techniques and participate in friendly matches",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:00 PM",
            "max_participants": 10,
            "participants": ["grace@mergington.edu", "james@mergington.edu"]
        },
        "Drama Club": {
            "description": "Perform in theatrical productions and develop acting skills",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 20,
            "participants": ["isabella@mergington.edu"]
        },
        "Art Studio": {
            "description": "Create paintings, sculptures, and digital art in a collaborative studio",
            "schedule": "Mondays and Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 16,
            "participants": ["nina@mergington.edu", "lucas@mergington.edu"]
        },
        "Debate Team": {
            "description": "Develop critical thinking and public speaking through competitive debates",
            "schedule": "Thursdays, 3:30 PM - 5:00 PM",
            "max_participants": 14,
            "participants": ["marcus@mergington.edu"]
        },
        "Robotics Club": {
            "description": "Build and program robots to compete in regional competitions",
            "schedule": "Tuesdays, 4:00 PM - 5:30 PM",
            "max_participants": 18,
            "participants": ["ryan@mergington.edu", "sophia@mergington.edu"]
        }
    }
    
    yield
    
    # Reset after test
    activities.clear()
    activities.update(initial_activities)


class TestGetActivities:
    """Tests for GET /activities endpoint"""

    def test_get_activities_returns_all_activities(self, client, reset_activities):
        """Test that GET /activities returns all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) == 9
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert "Basketball Team" in data

    def test_get_activities_contains_expected_fields(self, client, reset_activities):
        """Test that activities have expected fields"""
        response = client.get("/activities")
        data = response.json()
        
        chess_club = data["Chess Club"]
        assert "description" in chess_club
        assert "schedule" in chess_club
        assert "max_participants" in chess_club
        assert "participants" in chess_club

    def test_get_activities_shows_current_participants(self, client, reset_activities):
        """Test that participants list is accurate"""
        response = client.get("/activities")
        data = response.json()
        
        chess_club = data["Chess Club"]
        assert len(chess_club["participants"]) == 2
        assert "michael@mergington.edu" in chess_club["participants"]
        assert "daniel@mergington.edu" in chess_club["participants"]


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint"""

    def test_signup_successful(self, client, reset_activities):
        """Test successful signup for an activity"""
        response = client.post(
            "/activities/Chess%20Club/signup?email=newstudent@mergington.edu"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "Signed up" in data["message"]
        assert "newstudent@mergington.edu" in data["message"]

    def test_signup_adds_participant_to_list(self, client, reset_activities):
        """Test that signup actually adds participant"""
        client.post(
            "/activities/Chess%20Club/signup?email=newstudent@mergington.edu"
        )
        
        response = client.get("/activities")
        data = response.json()
        chess_club = data["Chess Club"]
        
        assert len(chess_club["participants"]) == 3
        assert "newstudent@mergington.edu" in chess_club["participants"]

    def test_signup_duplicate_fails(self, client, reset_activities):
        """Test that signing up twice fails"""
        response = client.post(
            "/activities/Chess%20Club/signup?email=michael@mergington.edu"
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"]

    def test_signup_nonexistent_activity(self, client, reset_activities):
        """Test that signing up for nonexistent activity fails"""
        response = client.post(
            "/activities/Nonexistent%20Club/signup?email=student@mergington.edu"
        )
        
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]

    def test_signup_multiple_students(self, client, reset_activities):
        """Test that multiple students can sign up for the same activity"""
        emails = ["student1@mergington.edu", "student2@mergington.edu", "student3@mergington.edu"]
        
        for email in emails:
            response = client.post(
                f"/activities/Programming%20Class/signup?email={email}"
            )
            assert response.status_code == 200
        
        response = client.get("/activities")
        data = response.json()
        prog_class = data["Programming Class"]
        
        assert len(prog_class["participants"]) == 5  # 2 original + 3 new
        for email in emails:
            assert email in prog_class["participants"]


class TestUnregisterFromActivity:
    """Tests for DELETE /activities/{activity_name}/unregister endpoint"""

    def test_unregister_successful(self, client, reset_activities):
        """Test successful unregistration from an activity"""
        response = client.delete(
            "/activities/Chess%20Club/unregister?email=michael@mergington.edu"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "Unregistered" in data["message"]
        assert "michael@mergington.edu" in data["message"]

    def test_unregister_removes_participant(self, client, reset_activities):
        """Test that unregister actually removes participant"""
        client.delete(
            "/activities/Chess%20Club/unregister?email=michael@mergington.edu"
        )
        
        response = client.get("/activities")
        data = response.json()
        chess_club = data["Chess Club"]
        
        assert len(chess_club["participants"]) == 1
        assert "michael@mergington.edu" not in chess_club["participants"]
        assert "daniel@mergington.edu" in chess_club["participants"]

    def test_unregister_nonexistent_student(self, client, reset_activities):
        """Test that unregistering a non-signed-up student fails"""
        response = client.delete(
            "/activities/Chess%20Club/unregister?email=nostudent@mergington.edu"
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "not signed up" in data["detail"]

    def test_unregister_nonexistent_activity(self, client, reset_activities):
        """Test that unregistering from nonexistent activity fails"""
        response = client.delete(
            "/activities/Nonexistent%20Club/unregister?email=student@mergington.edu"
        )
        
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]

    def test_unregister_then_signup_again(self, client, reset_activities):
        """Test that student can unregister and sign up again"""
        # Unregister
        response = client.delete(
            "/activities/Chess%20Club/unregister?email=michael@mergington.edu"
        )
        assert response.status_code == 200
        
        # Sign up again
        response = client.post(
            "/activities/Chess%20Club/signup?email=michael@mergington.edu"
        )
        assert response.status_code == 200
        
        # Verify participant is back
        response = client.get("/activities")
        data = response.json()
        chess_club = data["Chess Club"]
        
        assert "michael@mergington.edu" in chess_club["participants"]


class TestIntegration:
    """Integration tests"""

    def test_full_lifecycle(self, client, reset_activities):
        """Test complete user lifecycle: signup, view, unregister"""
        email = "integration@mergington.edu"
        activity = "Programming%20Class"
        
        # Initial check
        response = client.get("/activities")
        initial_count = len(response.json()["Programming Class"]["participants"])
        
        # Sign up
        response = client.post(f"/activities/{activity}/signup?email={email}")
        assert response.status_code == 200
        
        # Verify signup
        response = client.get("/activities")
        assert len(response.json()["Programming Class"]["participants"]) == initial_count + 1
        assert email in response.json()["Programming Class"]["participants"]
        
        # Unregister
        response = client.delete(f"/activities/{activity}/unregister?email={email}")
        assert response.status_code == 200
        
        # Verify unregister
        response = client.get("/activities")
        assert len(response.json()["Programming Class"]["participants"]) == initial_count
        assert email not in response.json()["Programming Class"]["participants"]

    def test_multiple_activities(self, client, reset_activities):
        """Test signup and unregister across multiple activities"""
        email = "multi@mergington.edu"
        
        # Sign up for multiple activities
        response = client.post("/activities/Chess%20Club/signup?email=" + email)
        assert response.status_code == 200
        
        response = client.post("/activities/Basketball%20Team/signup?email=" + email)
        assert response.status_code == 200
        
        # Verify both signups
        response = client.get("/activities")
        data = response.json()
        assert email in data["Chess Club"]["participants"]
        assert email in data["Basketball Team"]["participants"]
        
        # Unregister from one
        response = client.delete(f"/activities/Chess%20Club/unregister?email={email}")
        assert response.status_code == 200
        
        # Verify partial unregister
        response = client.get("/activities")
        data = response.json()
        assert email not in data["Chess Club"]["participants"]
        assert email in data["Basketball Team"]["participants"]
