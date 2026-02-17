"""Tests for authentication endpoints"""
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
from auth.password import hash_password


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


def test_signup_creates_user():
    """Test user signup creates new account"""
    response = client.post(
        "/api/signup",
        json={
            "email": "newuser@example.com",
            "password": "securePassword123"
        }
    )

    assert response.status_code == 201
    data = response.json()

    assert "accessToken" in data
    assert "user" in data
    assert "id" in data["user"]
    assert data["user"]["email"] == "newuser@example.com"
    assert "password" not in data  # Should not return password
    assert "password" not in data["user"]  # Should not return password in user object


def test_signup_duplicate_email_fails():
    """Test signup with existing email returns 400"""
    # Create first user
    client.post(
        "/api/signup",
        json={"email": "duplicate@example.com", "password": "pass123"}
    )

    # Try to create duplicate
    response = client.post(
        "/api/signup",
        json={"email": "duplicate@example.com", "password": "pass456"}
    )

    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]


def test_signup_invalid_email_fails():
    """Test signup with invalid email returns 422"""
    response = client.post(
        "/api/signup",
        json={"email": "not-an-email", "password": "pass123"}
    )

    assert response.status_code == 422


def test_login_with_correct_credentials():
    """Test login with correct email/password"""
    # Create user first
    client.post(
        "/api/signup",
        json={"email": "user@example.com", "password": "myPassword123"}
    )

    # Login
    response = client.post(
        "/api/login",
        json={"email": "user@example.com", "password": "myPassword123"}
    )

    assert response.status_code == 200
    data = response.json()

    assert "accessToken" in data
    assert "user" in data
    assert data["user"]["email"] == "user@example.com"


def test_login_with_wrong_password_fails():
    """Test login with wrong password returns 401"""
    # Create user
    client.post(
        "/api/signup",
        json={"email": "user@example.com", "password": "correctPassword"}
    )

    # Try to login with wrong password
    response = client.post(
        "/api/login",
        json={"email": "user@example.com", "password": "wrongPassword"}
    )

    assert response.status_code == 401
    assert "Invalid credentials" in response.json()["detail"]


def test_login_nonexistent_user_fails():
    """Test login with non-existent user returns 401"""
    response = client.post(
        "/api/login",
        json={"email": "nonexistent@example.com", "password": "pass123"}
    )

    assert response.status_code == 401


def test_get_me_with_valid_token():
    """Test /me endpoint returns current user"""
    # Signup to get token
    signup_response = client.post(
        "/api/signup",
        json={"email": "me@example.com", "password": "pass123"}
    )
    token = signup_response.json()["accessToken"]

    # Call /me
    response = client.get(
        "/api/me",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    data = response.json()

    assert data["email"] == "me@example.com"
    assert "password" not in data


def test_get_me_without_token_fails():
    """Test /me endpoint without token returns 401"""
    response = client.get("/api/me")

    assert response.status_code == 401


def test_get_me_with_invalid_token_fails():
    """Test /me endpoint with invalid token returns 401"""
    response = client.get(
        "/api/me",
        headers={"Authorization": "Bearer invalid.token.here"}
    )

    assert response.status_code == 401
