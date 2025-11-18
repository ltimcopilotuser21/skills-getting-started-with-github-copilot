"""
Test suite for the Mergington High School API
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
    """Reset activities database before each test"""
    # Store original state
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
            "description": "Competitive basketball training and inter-school matches",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 6:00 PM",
            "max_participants": 15,
            "participants": ["james@mergington.edu", "lucas@mergington.edu"]
        },
        "Swimming Club": {
            "description": "Swimming techniques and endurance training",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 20,
            "participants": ["ava@mergington.edu", "mia@mergington.edu"]
        },
        "Art Studio": {
            "description": "Painting, drawing, and mixed media art projects",
            "schedule": "Thursdays, 3:30 PM - 5:30 PM",
            "max_participants": 15,
            "participants": ["isabella@mergington.edu", "charlotte@mergington.edu"]
        },
        "Drama Club": {
            "description": "Acting, stage performance, and annual theater productions",
            "schedule": "Mondays and Wednesdays, 4:00 PM - 6:00 PM",
            "max_participants": 25,
            "participants": ["william@mergington.edu", "amelia@mergington.edu"]
        },
        "Debate Team": {
            "description": "Develop critical thinking and public speaking skills through competitive debates",
            "schedule": "Fridays, 4:00 PM - 5:30 PM",
            "max_participants": 16,
            "participants": ["ethan@mergington.edu", "harper@mergington.edu"]
        },
        "Science Olympiad": {
            "description": "Prepare for science competitions and conduct experiments",
            "schedule": "Tuesdays, 3:30 PM - 5:00 PM",
            "max_participants": 18,
            "participants": ["benjamin@mergington.edu", "evelyn@mergington.edu"]
        }
    }
    
    # Clear and reset activities
    activities.clear()
    activities.update(original_activities)
    
    yield
    
    # Clean up after test
    activities.clear()
    activities.update(original_activities)


class TestRootEndpoint:
    """Tests for the root endpoint"""
    
    def test_root_redirects_to_static(self, client):
        """Test that root endpoint redirects to static/index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestGetActivities:
    """Tests for GET /activities endpoint"""
    
    def test_get_activities_returns_200(self, client):
        """Test that getting activities returns status 200"""
        response = client.get("/activities")
        assert response.status_code == 200
    
    def test_get_activities_returns_all_activities(self, client):
        """Test that all activities are returned"""
        response = client.get("/activities")
        data = response.json()
        assert len(data) == 9
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert "Gym Class" in data
        assert "Basketball Team" in data
        assert "Swimming Club" in data
        assert "Art Studio" in data
        assert "Drama Club" in data
        assert "Debate Team" in data
        assert "Science Olympiad" in data
    
    def test_get_activities_has_correct_structure(self, client):
        """Test that activities have the correct structure"""
        response = client.get("/activities")
        data = response.json()
        
        for activity_name, activity_data in data.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)
    
    def test_chess_club_has_correct_data(self, client):
        """Test that Chess Club has the expected data"""
        response = client.get("/activities")
        data = response.json()
        chess_club = data["Chess Club"]
        
        assert chess_club["description"] == "Learn strategies and compete in chess tournaments"
        assert chess_club["schedule"] == "Fridays, 3:30 PM - 5:00 PM"
        assert chess_club["max_participants"] == 12
        assert len(chess_club["participants"]) == 2
        assert "michael@mergington.edu" in chess_club["participants"]
        assert "daniel@mergington.edu" in chess_club["participants"]


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_for_existing_activity_success(self, client):
        """Test successful signup for an existing activity"""
        response = client.post(
            "/activities/Chess Club/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200
        assert response.json() == {
            "message": "Signed up newstudent@mergington.edu for Chess Club"
        }
    
    def test_signup_adds_student_to_participants(self, client):
        """Test that signup actually adds the student to participants list"""
        email = "newstudent@mergington.edu"
        client.post(f"/activities/Chess Club/signup?email={email}")
        
        # Verify student was added
        response = client.get("/activities")
        chess_club = response.json()["Chess Club"]
        assert email in chess_club["participants"]
    
    def test_signup_for_nonexistent_activity_returns_404(self, client):
        """Test that signing up for a non-existent activity returns 404"""
        response = client.post(
            "/activities/Nonexistent Club/signup?email=student@mergington.edu"
        )
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"
    
    def test_signup_when_already_registered_returns_400(self, client):
        """Test that signing up when already registered returns 400"""
        email = "michael@mergington.edu"  # Already in Chess Club
        response = client.post(f"/activities/Chess Club/signup?email={email}")
        assert response.status_code == 400
        assert response.json()["detail"] == "Student already signed up for this activity"
    
    def test_signup_for_multiple_activities(self, client):
        """Test that a student can sign up for multiple different activities"""
        email = "multisport@mergington.edu"
        
        # Sign up for Chess Club
        response1 = client.post(f"/activities/Chess Club/signup?email={email}")
        assert response1.status_code == 200
        
        # Sign up for Programming Class
        response2 = client.post(f"/activities/Programming Class/signup?email={email}")
        assert response2.status_code == 200
        
        # Verify both signups
        activities_response = client.get("/activities")
        data = activities_response.json()
        assert email in data["Chess Club"]["participants"]
        assert email in data["Programming Class"]["participants"]
    
    def test_signup_with_special_characters_in_activity_name(self, client):
        """Test signup with URL-encoded activity names"""
        response = client.post(
            "/activities/Programming%20Class/signup?email=coder@mergington.edu"
        )
        assert response.status_code == 200


class TestUnregisterFromActivity:
    """Tests for DELETE /activities/{activity_name}/unregister endpoint"""
    
    def test_unregister_from_activity_success(self, client):
        """Test successful unregistration from an activity"""
        email = "michael@mergington.edu"  # Already in Chess Club
        response = client.delete(f"/activities/Chess Club/unregister?email={email}")
        assert response.status_code == 200
        assert response.json() == {
            "message": f"Unregistered {email} from Chess Club"
        }
    
    def test_unregister_removes_student_from_participants(self, client):
        """Test that unregister actually removes the student from participants list"""
        email = "michael@mergington.edu"
        client.delete(f"/activities/Chess Club/unregister?email={email}")
        
        # Verify student was removed
        response = client.get("/activities")
        chess_club = response.json()["Chess Club"]
        assert email not in chess_club["participants"]
    
    def test_unregister_from_nonexistent_activity_returns_404(self, client):
        """Test that unregistering from a non-existent activity returns 404"""
        response = client.delete(
            "/activities/Nonexistent Club/unregister?email=student@mergington.edu"
        )
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"
    
    def test_unregister_when_not_registered_returns_400(self, client):
        """Test that unregistering when not registered returns 400"""
        email = "notregistered@mergington.edu"
        response = client.delete(f"/activities/Chess Club/unregister?email={email}")
        assert response.status_code == 400
        assert response.json()["detail"] == "Student not signed up for this activity"
    
    def test_signup_and_unregister_workflow(self, client):
        """Test the complete workflow of signing up and then unregistering"""
        email = "workflow@mergington.edu"
        
        # Sign up
        signup_response = client.post(f"/activities/Drama Club/signup?email={email}")
        assert signup_response.status_code == 200
        
        # Verify signup
        activities = client.get("/activities").json()
        assert email in activities["Drama Club"]["participants"]
        
        # Unregister
        unregister_response = client.delete(f"/activities/Drama Club/unregister?email={email}")
        assert unregister_response.status_code == 200
        
        # Verify unregistration
        activities = client.get("/activities").json()
        assert email not in activities["Drama Club"]["participants"]
    
    def test_unregister_with_special_characters_in_activity_name(self, client):
        """Test unregister with URL-encoded activity names"""
        email = "emma@mergington.edu"  # Already in Programming Class
        response = client.delete(
            "/activities/Programming%20Class/unregister?email=" + email
        )
        assert response.status_code == 200


class TestEdgeCases:
    """Tests for edge cases and boundary conditions"""
    
    def test_activity_names_are_case_sensitive(self, client):
        """Test that activity names are case-sensitive"""
        response = client.post(
            "/activities/chess club/signup?email=student@mergington.edu"
        )
        assert response.status_code == 404
    
    def test_multiple_students_can_join_same_activity(self, client):
        """Test that multiple different students can join the same activity"""
        emails = [
            "student1@mergington.edu",
            "student2@mergington.edu",
            "student3@mergington.edu"
        ]
        
        for email in emails:
            response = client.post(f"/activities/Art Studio/signup?email={email}")
            assert response.status_code == 200
        
        # Verify all were added
        activities = client.get("/activities").json()
        art_studio = activities["Art Studio"]
        for email in emails:
            assert email in art_studio["participants"]
    
    def test_can_rejoin_after_unregistering(self, client):
        """Test that a student can rejoin an activity after unregistering"""
        email = "rejoin@mergington.edu"
        
        # First signup
        client.post(f"/activities/Swimming Club/signup?email={email}")
        
        # Unregister
        client.delete(f"/activities/Swimming Club/unregister?email={email}")
        
        # Signup again
        response = client.post(f"/activities/Swimming Club/signup?email={email}")
        assert response.status_code == 200
        
        # Verify in participants
        activities = client.get("/activities").json()
        assert email in activities["Swimming Club"]["participants"]
