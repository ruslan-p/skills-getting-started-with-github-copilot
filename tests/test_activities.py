"""
Tests for the High School Management System API
"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add the src directory to the path so we can import app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app

client = TestClient(app)


@pytest.fixture
def reset_activities():
    """Reset activities to initial state before each test"""
    # Store original activities
    from app import activities
    original_activities = {
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
            "description": "Competitive basketball team for intramural and tournament play",
            "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
            "max_participants": 15,
            "participants": ["james@mergington.edu"]
        },
        "Tennis Club": {
            "description": "Develop tennis skills and compete in friendly matches",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:00 PM",
            "max_participants": 10,
            "participants": ["sarah@mergington.edu"]
        },
        "Drama Club": {
            "description": "Act in theatrical productions and develop stage presence",
            "schedule": "Wednesdays and Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 25,
            "participants": ["lucas@mergington.edu", "ava@mergington.edu"]
        },
        "Art Studio": {
            "description": "Explore painting, drawing, and mixed media techniques",
            "schedule": "Mondays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 18,
            "participants": ["isabella@mergington.edu"]
        },
        "Robotics Club": {
            "description": "Build and program robots for competitions and demonstrations",
            "schedule": "Tuesdays and Fridays, 4:00 PM - 5:30 PM",
            "max_participants": 16,
            "participants": ["noah@mergington.edu", "mia@mergington.edu"]
        },
        "Debate Team": {
            "description": "Develop argumentation and public speaking skills",
            "schedule": "Wednesdays, 4:00 PM - 5:30 PM",
            "max_participants": 12,
            "participants": ["ethan@mergington.edu"]
        }
    }
    
    # Clear and restore original activities
    activities.clear()
    activities.update(original_activities)
    
    yield
    
    # Reset again after test
    activities.clear()
    activities.update(original_activities)


class TestGetActivities:
    """Tests for GET /activities endpoint"""
    
    def test_get_activities_returns_200(self, reset_activities):
        """Test that GET /activities returns status 200"""
        response = client.get("/activities")
        assert response.status_code == 200
    
    def test_get_activities_returns_dict(self, reset_activities):
        """Test that GET /activities returns a dictionary"""
        response = client.get("/activities")
        assert isinstance(response.json(), dict)
    
    def test_get_activities_contains_all_activities(self, reset_activities):
        """Test that GET /activities contains all expected activities"""
        response = client.get("/activities")
        activities_data = response.json()
        
        expected_activities = [
            "Chess Club", "Programming Class", "Gym Class", "Basketball Team",
            "Tennis Club", "Drama Club", "Art Studio", "Robotics Club", "Debate Team"
        ]
        
        for activity in expected_activities:
            assert activity in activities_data
    
    def test_activity_has_required_fields(self, reset_activities):
        """Test that each activity has required fields"""
        response = client.get("/activities")
        activities_data = response.json()
        
        required_fields = ["description", "schedule", "max_participants", "participants"]
        
        for activity_name, activity_data in activities_data.items():
            for field in required_fields:
                assert field in activity_data, f"Field '{field}' missing from {activity_name}"


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_successful(self, reset_activities):
        """Test successful signup for an activity"""
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": "newstudent@mergington.edu"}
        )
        assert response.status_code == 200
        assert "Signed up" in response.json()["message"]
        assert "newstudent@mergington.edu" in response.json()["message"]
    
    def test_signup_adds_participant(self, reset_activities):
        """Test that signup actually adds the participant"""
        email = "newstudent@mergington.edu"
        client.post("/activities/Chess Club/signup", params={"email": email})
        
        response = client.get("/activities")
        activities_data = response.json()
        assert email in activities_data["Chess Club"]["participants"]
    
    def test_signup_activity_not_found(self, reset_activities):
        """Test signup for non-existent activity"""
        response = client.post(
            "/activities/Non-Existent Activity/signup",
            params={"email": "student@mergington.edu"}
        )
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]
    
    def test_signup_already_registered(self, reset_activities):
        """Test signup when student is already registered"""
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": "michael@mergington.edu"}
        )
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]
    
    def test_multiple_signups(self, reset_activities):
        """Test multiple students can sign up for the same activity"""
        student1 = "student1@mergington.edu"
        student2 = "student2@mergington.edu"
        
        response1 = client.post("/activities/Tennis Club/signup", params={"email": student1})
        response2 = client.post("/activities/Tennis Club/signup", params={"email": student2})
        
        assert response1.status_code == 200
        assert response2.status_code == 200


class TestUnregisterFromActivity:
    """Tests for POST /activities/{activity_name}/unregister endpoint"""
    
    def test_unregister_successful(self, reset_activities):
        """Test successful unregistration from an activity"""
        response = client.post(
            "/activities/Chess Club/unregister",
            params={"email": "michael@mergington.edu"}
        )
        assert response.status_code == 200
        assert "Unregistered" in response.json()["message"]
    
    def test_unregister_removes_participant(self, reset_activities):
        """Test that unregister actually removes the participant"""
        email = "michael@mergington.edu"
        client.post("/activities/Chess Club/unregister", params={"email": email})
        
        response = client.get("/activities")
        activities_data = response.json()
        assert email not in activities_data["Chess Club"]["participants"]
    
    def test_unregister_activity_not_found(self, reset_activities):
        """Test unregister from non-existent activity"""
        response = client.post(
            "/activities/Non-Existent Activity/unregister",
            params={"email": "student@mergington.edu"}
        )
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]
    
    def test_unregister_not_registered(self, reset_activities):
        """Test unregister when student is not registered"""
        response = client.post(
            "/activities/Chess Club/unregister",
            params={"email": "notstudent@mergington.edu"}
        )
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"]


class TestSignupAndUnregisterFlow:
    """Integration tests for signup and unregister flows"""
    
    def test_signup_then_unregister(self, reset_activities):
        """Test signup followed by unregister"""
        email = "testuser@mergington.edu"
        activity = "Robotics Club"
        
        # Sign up
        signup_response = client.post(f"/activities/{activity}/signup", params={"email": email})
        assert signup_response.status_code == 200
        
        # Verify signup
        get_response = client.get("/activities")
        assert email in get_response.json()[activity]["participants"]
        
        # Unregister
        unregister_response = client.post(f"/activities/{activity}/unregister", params={"email": email})
        assert unregister_response.status_code == 200
        
        # Verify unregister
        get_response = client.get("/activities")
        assert email not in get_response.json()[activity]["participants"]
    
    def test_signup_again_after_unregister(self, reset_activities):
        """Test can signup again after unregistering"""
        email = "testuser@mergington.edu"
        activity = "Drama Club"
        
        # Sign up
        client.post(f"/activities/{activity}/signup", params={"email": email})
        
        # Unregister
        client.post(f"/activities/{activity}/unregister", params={"email": email})
        
        # Sign up again
        response = client.post(f"/activities/{activity}/signup", params={"email": email})
        assert response.status_code == 200
