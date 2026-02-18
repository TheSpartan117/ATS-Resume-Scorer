"""Tests for authentication utilities"""
import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from backend.auth.password import hash_password, verify_password
from backend.auth.jwt import create_access_token, verify_token


def test_hash_password():
    """Test password hashing"""
    password = "mySecurePassword123"
    hashed = hash_password(password)

    assert hashed != password  # Should be hashed
    assert len(hashed) > 50  # Bcrypt hash is long
    assert hashed.startswith("$2b$")  # Bcrypt format


def test_verify_password_correct():
    """Test password verification with correct password"""
    password = "mySecurePassword123"
    hashed = hash_password(password)

    assert verify_password(password, hashed) is True


def test_verify_password_incorrect():
    """Test password verification with incorrect password"""
    password = "mySecurePassword123"
    hashed = hash_password(password)

    assert verify_password("wrongPassword", hashed) is False


def test_create_access_token():
    """Test JWT token creation"""
    user_id = "123e4567-e89b-12d3-a456-426614174000"
    token = create_access_token({"sub": user_id})

    assert isinstance(token, str)
    assert len(token) > 50  # JWT tokens are long


def test_verify_token_valid():
    """Test JWT token verification with valid token"""
    user_id = "123e4567-e89b-12d3-a456-426614174000"
    token = create_access_token({"sub": user_id})

    payload = verify_token(token)

    assert payload is not None
    assert payload["sub"] == user_id


def test_verify_token_invalid():
    """Test JWT token verification with invalid token"""
    invalid_token = "invalid.jwt.token"

    payload = verify_token(invalid_token)

    assert payload is None
