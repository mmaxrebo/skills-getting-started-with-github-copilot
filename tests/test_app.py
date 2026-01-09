"""
Tests for the Mergington High School Activities API
"""
import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add src to path to import app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app

client = TestClient(app)


@pytest.fixture
def reset_activities():
    """Reset activities to initial state before each test"""
    from app import activities
    initial_activities = {
        "Art Studio": {
            "description": "Explore painting, drawing, and other visual arts",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 16,
            "participants": ["maya@mergington.edu"]
        },
        "Basketball": {
            "description": "Team sport focusing on basketball skills and competitive play",
            "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
            "max_participants": 15,
            "participants": ["alex@mergington.edu"]
        },
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Debate Team": {
            "description": "Develop argumentation and public speaking skills",
            "schedule": "Mondays and Fridays, 3:30 PM - 4:30 PM",
            "max_participants": 14,
            "participants": ["lucas@mergington.edu", "ava@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        },
        "Music Ensemble": {
            "description": "Play instruments and perform in group concerts",
            "schedule": "Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 20,
            "participants": ["james@mergington.edu", "hannah@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Robotics Club": {
            "description": "Design and build robots for competitions",
            "schedule": "Saturdays, 10:00 AM - 12:00 PM",
            "max_participants": 18,
            "participants": ["david@mergington.edu"]
        }
    }
    activities.clear()
    activities.update(initial_activities)
    yield
    activities.clear()
    activities.update(initial_activities)


class TestGetActivities:
    """Tests for GET /activities endpoint"""
    
    def test_get_activities(self, reset_activities):
        """Test that all activities are returned"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        
        assert "Art Studio" in data
        assert "Basketball" in data
        assert "Chess Club" in data
        assert len(data) == 8
    
    def test_activity_structure(self, reset_activities):
        """Test that activities have correct structure"""
        response = client.get("/activities")
        data = response.json()
        activity = data["Art Studio"]
        
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity
    
    def test_activity_participants(self, reset_activities):
        """Test that participants are correctly listed"""
        response = client.get("/activities")
        data = response.json()
        
        assert "maya@mergington.edu" in data["Art Studio"]["participants"]
        assert "michael@mergington.edu" in data["Chess Club"]["participants"]


class TestSignup:
    """Tests for POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_success(self, reset_activities):
        """Test successful signup"""
        response = client.post(
            "/activities/Art Studio/signup?email=newstudent@mergington.edu",
            follow_redirects=True
        )
        assert response.status_code == 200
        data = response.json()
        assert "Signed up" in data["message"]
    
    def test_signup_adds_participant(self, reset_activities):
        """Test that signup adds participant to activity"""
        client.post(
            "/activities/Basketball/signup?email=newplayer@mergington.edu",
            follow_redirects=True
        )
        
        response = client.get("/activities")
        data = response.json()
        assert "newplayer@mergington.edu" in data["Basketball"]["participants"]
    
    def test_signup_duplicate_student(self, reset_activities):
        """Test that duplicate signup is rejected"""
        response = client.post(
            "/activities/Art Studio/signup?email=maya@mergington.edu",
            follow_redirects=True
        )
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"]
    
    def test_signup_invalid_activity(self, reset_activities):
        """Test signup for non-existent activity"""
        response = client.post(
            "/activities/Nonexistent Activity/signup?email=student@mergington.edu",
            follow_redirects=True
        )
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"]


class TestUnregister:
    """Tests for POST /activities/{activity_name}/unregister endpoint"""
    
    def test_unregister_success(self, reset_activities):
        """Test successful unregister"""
        response = client.post(
            "/activities/Art Studio/unregister?email=maya@mergington.edu",
            follow_redirects=True
        )
        assert response.status_code == 200
        data = response.json()
        assert "Unregistered" in data["message"]
    
    def test_unregister_removes_participant(self, reset_activities):
        """Test that unregister removes participant from activity"""
        client.post(
            "/activities/Basketball/unregister?email=alex@mergington.edu",
            follow_redirects=True
        )
        
        response = client.get("/activities")
        data = response.json()
        assert "alex@mergington.edu" not in data["Basketball"]["participants"]
    
    def test_unregister_not_registered(self, reset_activities):
        """Test unregister for student not in activity"""
        response = client.post(
            "/activities/Art Studio/unregister?email=notaparticipant@mergington.edu",
            follow_redirects=True
        )
        assert response.status_code == 400
        data = response.json()
        assert "not signed up" in data["detail"]
    
    def test_unregister_invalid_activity(self, reset_activities):
        """Test unregister for non-existent activity"""
        response = client.post(
            "/activities/Nonexistent Activity/unregister?email=student@mergington.edu",
            follow_redirects=True
        )
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"]


class TestIntegration:
    """Integration tests combining multiple endpoints"""
    
    def test_signup_then_unregister(self, reset_activities):
        """Test signing up and then unregistering"""
        email = "testuser@mergington.edu"
        activity = "Programming Class"
        
        # Sign up
        response = client.post(
            f"/activities/{activity}/signup?email={email}",
            follow_redirects=True
        )
        assert response.status_code == 200
        
        # Verify signup
        response = client.get("/activities")
        assert email in response.json()[activity]["participants"]
        
        # Unregister
        response = client.post(
            f"/activities/{activity}/unregister?email={email}",
            follow_redirects=True
        )
        assert response.status_code == 200
        
        # Verify unregister
        response = client.get("/activities")
        assert email not in response.json()[activity]["participants"]
    
    def test_multiple_signups_and_unregisters(self, reset_activities):
        """Test multiple participants in an activity"""
        activity = "Robotics Club"
        emails = ["student1@mergington.edu", "student2@mergington.edu", "student3@mergington.edu"]
        
        # Sign up multiple students
        for email in emails:
            client.post(
                f"/activities/{activity}/signup?email={email}",
                follow_redirects=True
            )
        
        # Verify all are signed up
        response = client.get("/activities")
        participants = response.json()[activity]["participants"]
        for email in emails:
            assert email in participants
        
        # Unregister one student
        client.post(
            f"/activities/{activity}/unregister?email={emails[0]}",
            follow_redirects=True
        )
        
        # Verify correct removal
        response = client.get("/activities")
        participants = response.json()[activity]["participants"]
        assert emails[0] not in participants
        assert emails[1] in participants
        assert emails[2] in participants
