"""
Tests for the Mergington High School Activities API
"""
import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities data before each test"""
    global activities
    activities.clear()
    activities.update({
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
        }
    })


class TestRootEndpoint:
    """Tests for the root endpoint"""

    def test_root_redirects_to_static_index(self, client):
        """Test that root path redirects to static index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestGetActivities:
    """Tests for GET /activities endpoint"""

    def test_get_activities_returns_all_activities(self, client):
        """Test that get_activities returns all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert "Gym Class" in data

    def test_get_activities_includes_participant_info(self, client):
        """Test that activities include participant information"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert len(data["Chess Club"]["participants"]) == 2
        assert "michael@mergington.edu" in data["Chess Club"]["participants"]


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint"""

    def test_signup_for_existing_activity(self, client):
        """Test successful signup for an existing activity"""
        response = client.post("/activities/Chess Club/signup?email=test@mergington.edu")
        assert response.status_code == 200
        data = response.json()
        assert "Signed up test@mergington.edu for Chess Club" in data["message"]

    def test_signup_for_nonexistent_activity(self, client):
        """Test signup for non-existent activity returns 404"""
        response = client.post("/activities/Nonexistent Club/signup?email=test@mergington.edu")
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Activity not found"

    def test_duplicate_signup_prevented(self, client):
        """Test that duplicate signups are prevented"""
        # First signup should succeed
        response1 = client.post("/activities/Chess Club/signup?email=newstudent@mergington.edu")
        assert response1.status_code == 200

        # Second signup for same student should fail
        response2 = client.post("/activities/Chess Club/signup?email=newstudent@mergington.edu")
        assert response2.status_code == 400
        data = response2.json()
        assert data["detail"] == "Student is already signed up"

    def test_signup_adds_student_to_participants(self, client):
        """Test that signup actually adds student to participants list"""
        email = "newstudent@mergington.edu"
        client.post(f"/activities/Programming Class/signup?email={email}")
        
        # Verify student was added
        response = client.get("/activities")
        data = response.json()
        assert email in data["Programming Class"]["participants"]


class TestUnregisterFromActivity:
    """Tests for DELETE /activities/{activity_name}/signup endpoint"""

    def test_unregister_from_activity(self, client):
        """Test successful unregistration from an activity"""
        response = client.delete("/activities/Chess Club/signup?email=michael@mergington.edu")
        assert response.status_code == 200
        data = response.json()
        assert "Unregistered michael@mergington.edu from Chess Club" in data["message"]

    def test_unregister_from_nonexistent_activity(self, client):
        """Test unregister from non-existent activity returns 404"""
        response = client.delete("/activities/Nonexistent Club/signup?email=test@mergington.edu")
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Activity not found"

    def test_unregister_student_not_registered(self, client):
        """Test unregistering student who is not registered returns 400"""
        response = client.delete("/activities/Chess Club/signup?email=notregistered@mergington.edu")
        assert response.status_code == 400
        data = response.json()
        assert data["detail"] == "Student is not registered for this activity"

    def test_unregister_removes_student_from_participants(self, client):
        """Test that unregister actually removes student from participants list"""
        email = "michael@mergington.edu"
        
        # Verify student is initially in the list
        response1 = client.get("/activities")
        data1 = response1.json()
        assert email in data1["Chess Club"]["participants"]
        
        # Unregister student
        client.delete(f"/activities/Chess Club/signup?email={email}")
        
        # Verify student was removed
        response2 = client.get("/activities")
        data2 = response2.json()
        assert email not in data2["Chess Club"]["participants"]


class TestIntegrationScenarios:
    """Integration tests for complete user flows"""

    def test_signup_and_unregister_flow(self, client):
        """Test complete flow of signing up and then unregistering"""
        email = "testuser@mergington.edu"
        activity = "Gym Class"
        
        # Signup
        signup_response = client.post(f"/activities/{activity}/signup?email={email}")
        assert signup_response.status_code == 200
        
        # Verify signup
        get_response = client.get("/activities")
        activities_data = get_response.json()
        assert email in activities_data[activity]["participants"]
        
        # Unregister
        unregister_response = client.delete(f"/activities/{activity}/signup?email={email}")
        assert unregister_response.status_code == 200
        
        # Verify unregistration
        final_response = client.get("/activities")
        final_data = final_response.json()
        assert email not in final_data[activity]["participants"]

    def test_multiple_students_same_activity(self, client):
        """Test multiple students can sign up for the same activity"""
        activity = "Programming Class"
        students = [
            "student1@mergington.edu",
            "student2@mergington.edu",
            "student3@mergington.edu"
        ]
        
        # Sign up all students
        for email in students:
            response = client.post(f"/activities/{activity}/signup?email={email}")
            assert response.status_code == 200
        
        # Verify all students are registered
        response = client.get("/activities")
        data = response.json()
        for email in students:
            assert email in data[activity]["participants"]
