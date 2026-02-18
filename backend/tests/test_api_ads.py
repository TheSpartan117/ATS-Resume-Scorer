"""Tests for ad tracking endpoints"""
import pytest


def test_log_ad_view_as_guest(client):
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


def test_log_ad_view_authenticated_user(client):
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


def test_should_show_ad_first_action(client):
    """Test should NOT show ad on first action"""
    response = client.get(
        "/api/should-show-ad",
        params={"sessionId": "new-session"}
    )

    assert response.status_code == 200
    data = response.json()

    assert data["shouldShowAd"] is False
    assert data["actionCount"] == 0


def test_should_show_ad_after_first_score(client):
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


def test_premium_user_never_sees_ads(client):
    """Test premium users don't see ads"""
    # Create user (would need to manually set is_premium in real scenario)
    # For now, test the logic with isPremium parameter

    response = client.get(
        "/api/should-show-ad",
        params={"sessionId": "premium-session", "actionCount": 10, "isPremium": True}
    )

    assert response.status_code == 200
    assert response.json()["shouldShowAd"] is False
