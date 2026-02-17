"""Tests for ad tracking endpoints"""
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
    """Override get_db for tests"""
    try:
        db = TestSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


@pytest.fixture(scope="function", autouse=True)
def setup_database():
    """Create test database tables"""
    Base.metadata.create_all(bind=test_engine)
    yield
    # Clean up tables after each test
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)


def test_log_ad_view_as_guest():
    """Test logging ad view for guest user"""
    response = client.post(
        "/api/ad-view",
        json={
            "sessionId": "guest-session-123",
            "skipped": False
        }
    )

    assert response.status_code == 201
    data = response.json()

    assert "id" in data
    assert data["sessionId"] == "guest-session-123"
    assert data["skipped"] is False


def test_log_ad_view_authenticated_user():
    """Test logging ad view for authenticated user"""
    # Create user
    signup_response = client.post(
        "/api/signup",
        json={"email": "user@example.com", "password": "pass123"}
    )
    token = signup_response.json()["accessToken"]

    # Log ad view
    response = client.post(
        "/api/ad-view",
        json={"skipped": True},
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 201
    data = response.json()

    assert "userId" in data
    assert data["skipped"] is True


def test_should_show_ad_first_action():
    """Test should NOT show ad on first action"""
    response = client.get(
        "/api/should-show-ad",
        params={"sessionId": "new-session"}
    )

    assert response.status_code == 200
    data = response.json()

    assert data["shouldShowAd"] is False
    assert data["actionCount"] == 0


def test_should_show_ad_after_first_score():
    """Test SHOULD show ad after first free score"""
    session_id = "test-session-456"

    # Simulate first action (upload/score) - no ad
    response1 = client.get(
        "/api/should-show-ad",
        params={"sessionId": session_id, "actionCount": 1}
    )
    assert response1.json()["shouldShowAd"] is False

    # Second action - should show ad
    response2 = client.get(
        "/api/should-show-ad",
        params={"sessionId": session_id, "actionCount": 2}
    )
    assert response2.json()["shouldShowAd"] is True


def test_premium_user_never_sees_ads():
    """Test premium users don't see ads"""
    # Create user (would need to manually set is_premium in real scenario)
    # For now, test the logic with isPremium parameter

    response = client.get(
        "/api/should-show-ad",
        params={"sessionId": "premium-session", "actionCount": 10, "isPremium": True}
    )

    assert response.status_code == 200
    assert response.json()["shouldShowAd"] is False
