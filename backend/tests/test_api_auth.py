"""Tests for authentication endpoints"""
import pytest
from backend.auth.password import hash_password


def test_signup_creates_user(client):
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


def test_signup_duplicate_email_fails(client):
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


def test_signup_invalid_email_fails(client):
    """Test signup with invalid email returns 422"""
    response = client.post(
        "/api/signup",
        json={"email": "not-an-email", "password": "pass123"}
    )

    assert response.status_code == 422


def test_login_with_correct_credentials(client):
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


def test_login_with_wrong_password_fails(client):
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


def test_login_nonexistent_user_fails(client):
    """Test login with non-existent user returns 401"""
    response = client.post(
        "/api/login",
        json={"email": "nonexistent@example.com", "password": "pass123"}
    )

    assert response.status_code == 401


def test_get_me_with_valid_token(client):
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


def test_get_me_without_token_fails(client):
    """Test /me endpoint without token returns 401"""
    response = client.get("/api/me")

    assert response.status_code == 401


def test_get_me_with_invalid_token_fails(client):
    """Test /me endpoint with invalid token returns 401"""
    response = client.get(
        "/api/me",
        headers={"Authorization": "Bearer invalid.token.here"}
    )

    assert response.status_code == 401
