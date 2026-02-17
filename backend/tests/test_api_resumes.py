"""Tests for protected resume endpoints"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import app
from database import Base, get_db
# Import all models to ensure they are registered with Base
from models.user import User
from models.resume import Resume
from models.ad_view import AdView


# Create test database (SQLite in-memory)
# Note: Use file-based SQLite for test persistence during test run
import tempfile
import os

test_db_fd, test_db_path = tempfile.mkstemp()
TEST_DATABASE_URL = f"sqlite:///{test_db_path}"
test_engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

# Create tables immediately
Base.metadata.create_all(bind=test_engine)


# Override the get_db dependency
def override_get_db():
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


# Test database setup
@pytest.fixture(scope="function", autouse=True)
def setup_database():
    """Clear database tables before each test"""
    # Clear all tables
    with test_engine.connect() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            conn.execute(table.delete())
            conn.commit()
    yield

@pytest.fixture(scope="session", autouse=True)
def cleanup_test_db():
    """Remove test database file after all tests"""
    yield
    os.close(test_db_fd)
    os.unlink(test_db_path)


@pytest.fixture
def auth_token():
    """Create user and return auth token"""
    response = client.post(
        "/api/signup",
        json={"email": "testuser@example.com", "password": "pass123"}
    )
    return response.json()["accessToken"]


def test_create_resume_requires_auth():
    """Test creating resume without auth returns 401"""
    resume_data = {
        "fileName": "test.pdf",
        "contact": {"name": "John", "email": "john@example.com"},
        "metadata": {"pageCount": 1, "wordCount": 500, "hasPhoto": False, "fileFormat": "pdf"}
    }

    response = client.post("/api/resumes", json=resume_data)

    assert response.status_code == 401


def test_create_resume_saves_to_database(auth_token):
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


def test_list_resumes_returns_user_resumes(auth_token):
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


def test_get_resume_by_id(auth_token):
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


def test_get_nonexistent_resume_returns_404(auth_token):
    """Test getting non-existent resume returns 404"""
    fake_id = "00000000-0000-0000-0000-000000000000"

    response = client.get(
        f"/api/resumes/{fake_id}",
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    assert response.status_code == 404


def test_update_resume(auth_token):
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


def test_delete_resume(auth_token):
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


def test_user_cannot_access_other_user_resume():
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
