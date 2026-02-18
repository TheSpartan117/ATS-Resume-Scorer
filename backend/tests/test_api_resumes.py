"""Tests for protected resume endpoints"""
import pytest


@pytest.fixture
def auth_token(client):
    """Create user and return auth token"""
    response = client.post(
        "/api/signup",
        json={"email": "testuser@example.com", "password": "pass123"}
    )
    return response.json()["accessToken"]


def test_create_resume_requires_auth(client):
    """Test creating resume without auth returns 401"""
    resume_data = {
        "fileName": "test.pdf",
        "contact": {"name": "John", "email": "john@example.com"},
        "metadata": {"pageCount": 1, "wordCount": 500, "hasPhoto": False, "fileFormat": "pdf"}
    }

    response = client.post("/api/resumes", json=resume_data)

    assert response.status_code == 401


def test_create_resume_saves_to_database(client, auth_token):
    """Test creating resume saves it to database"""
    resume_data = {
        "fileName": "my_resume.pdf",
        "contact": {"name": "Jane Doe", "email": "jane@example.com"},
        "experience": [],
        "education": [],
        "skills": ["Python", "React"],
        "metadata": {"pageCount": 1, "wordCount": 500, "hasPhoto": False, "fileFormat": "pdf"}
    }

    response = client.post(
        "/api/resumes",
        json=resume_data,
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    assert response.status_code == 201
    data = response.json()

    assert "id" in data
    assert data["fileName"] == "my_resume.pdf"
    assert data["contact"]["name"] == "Jane Doe"


def test_list_resumes_returns_user_resumes(client, auth_token):
    """Test listing resumes returns only user's resumes"""
    # Create two resumes
    resume1 = {
        "fileName": "resume1.pdf",
        "contact": {"name": "User"},
        "metadata": {"pageCount": 1, "wordCount": 500, "hasPhoto": False, "fileFormat": "pdf"}
    }
    resume2 = {
        "fileName": "resume2.pdf",
        "contact": {"name": "User"},
        "metadata": {"pageCount": 1, "wordCount": 600, "hasPhoto": False, "fileFormat": "pdf"}
    }

    client.post("/api/resumes", json=resume1, headers={"Authorization": f"Bearer {auth_token}"})
    client.post("/api/resumes", json=resume2, headers={"Authorization": f"Bearer {auth_token}"})

    # List resumes
    response = client.get(
        "/api/resumes",
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    assert response.status_code == 200
    data = response.json()

    assert len(data) == 2
    assert data[0]["fileName"] in ["resume1.pdf", "resume2.pdf"]


def test_get_resume_by_id(client, auth_token):
    """Test getting specific resume by ID"""
    # Create resume
    resume_data = {
        "fileName": "test.pdf",
        "contact": {"name": "Test"},
        "metadata": {"pageCount": 1, "wordCount": 500, "hasPhoto": False, "fileFormat": "pdf"}
    }
    create_response = client.post(
        "/api/resumes",
        json=resume_data,
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    resume_id = create_response.json()["id"]

    # Get resume
    response = client.get(
        f"/api/resumes/{resume_id}",
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    assert response.status_code == 200
    data = response.json()

    assert data["id"] == resume_id
    assert data["fileName"] == "test.pdf"


def test_get_nonexistent_resume_returns_404(client, auth_token):
    """Test getting non-existent resume returns 404"""
    fake_id = "00000000-0000-0000-0000-000000000000"

    response = client.get(
        f"/api/resumes/{fake_id}",
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    assert response.status_code == 404


def test_update_resume(client, auth_token):
    """Test updating resume"""
    # Create resume
    resume_data = {
        "fileName": "original.pdf",
        "contact": {"name": "Original"},
        "metadata": {"pageCount": 1, "wordCount": 500, "hasPhoto": False, "fileFormat": "pdf"}
    }
    create_response = client.post(
        "/api/resumes",
        json=resume_data,
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    resume_id = create_response.json()["id"]

    # Update resume
    updated_data = {
        "fileName": "updated.pdf",
        "contact": {"name": "Updated", "email": "new@example.com"},
        "metadata": {"pageCount": 2, "wordCount": 800, "hasPhoto": False, "fileFormat": "pdf"}
    }
    response = client.put(
        f"/api/resumes/{resume_id}",
        json=updated_data,
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    assert response.status_code == 200
    data = response.json()

    assert data["fileName"] == "updated.pdf"
    assert data["contact"]["name"] == "Updated"
    assert data["metadata"]["wordCount"] == 800


def test_delete_resume(client, auth_token):
    """Test deleting resume"""
    # Create resume
    resume_data = {
        "fileName": "to_delete.pdf",
        "contact": {"name": "Delete Me"},
        "metadata": {"pageCount": 1, "wordCount": 500, "hasPhoto": False, "fileFormat": "pdf"}
    }
    create_response = client.post(
        "/api/resumes",
        json=resume_data,
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    resume_id = create_response.json()["id"]

    # Delete resume
    response = client.delete(
        f"/api/resumes/{resume_id}",
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    assert response.status_code == 204

    # Verify it's deleted
    get_response = client.get(
        f"/api/resumes/{resume_id}",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert get_response.status_code == 404


def test_user_cannot_access_other_user_resume(client):
    """Test user cannot access another user's resume"""
    # Create user 1 and their resume
    user1_response = client.post(
        "/api/signup",
        json={"email": "user1@example.com", "password": "pass123"}
    )
    user1_token = user1_response.json()["accessToken"]

    resume_response = client.post(
        "/api/resumes",
        json={
            "fileName": "user1_resume.pdf",
            "contact": {"name": "User 1"},
            "metadata": {"pageCount": 1, "wordCount": 500, "hasPhoto": False, "fileFormat": "pdf"}
        },
        headers={"Authorization": f"Bearer {user1_token}"}
    )
    resume_id = resume_response.json()["id"]

    # Create user 2
    user2_response = client.post(
        "/api/signup",
        json={"email": "user2@example.com", "password": "pass123"}
    )
    user2_token = user2_response.json()["accessToken"]

    # Try to access user1's resume as user2
    response = client.get(
        f"/api/resumes/{resume_id}",
        headers={"Authorization": f"Bearer {user2_token}"}
    )

    assert response.status_code == 403  # Forbidden
