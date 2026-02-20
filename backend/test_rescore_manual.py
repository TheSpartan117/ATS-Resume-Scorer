"""
Manual test for the rescore endpoint.
Run this to verify the rescore endpoint works correctly.

Usage:
    python test_rescore_manual.py
"""

import sys
import requests

BASE_URL = "http://localhost:8000"


def test_rescore_endpoint():
    """Test the rescore endpoint manually"""
    print("Testing rescore endpoint...")
    print("-" * 50)

    # Step 1: Create a session
    print("\n1. Creating editor session...")
    response = requests.post(
        f"{BASE_URL}/api/editor/session",
        json={"resume_id": "test_rescore"}
    )

    if response.status_code != 200:
        print(f"❌ Failed to create session: {response.status_code}")
        print(response.text)
        return False

    session_data = response.json()
    session_id = session_data["session_id"]
    initial_score = session_data["current_score"]["overallScore"]

    print(f"✅ Session created: {session_id}")
    print(f"   Initial score: {initial_score}")

    # Step 2: Re-score the resume
    print("\n2. Re-scoring resume...")
    response = requests.post(
        f"{BASE_URL}/api/editor/rescore",
        json={"session_id": session_id}
    )

    if response.status_code != 200:
        print(f"❌ Failed to rescore: {response.status_code}")
        print(response.text)
        return False

    rescore_data = response.json()
    print("✅ Rescore successful!")

    # Verify response structure
    print("\n3. Verifying response structure...")
    checks = []

    if "score" in rescore_data:
        print("   ✅ 'score' field present")
        checks.append(True)
    else:
        print("   ❌ 'score' field missing")
        checks.append(False)

    if "suggestions" in rescore_data:
        print("   ✅ 'suggestions' field present")
        checks.append(True)
    else:
        print("   ❌ 'suggestions' field missing")
        checks.append(False)

    if "score" in rescore_data and "overallScore" in rescore_data["score"]:
        print("   ✅ 'overallScore' field present")
        checks.append(True)
    else:
        print("   ❌ 'overallScore' field missing")
        checks.append(False)

    # Display score details
    if "score" in rescore_data:
        score = rescore_data["score"]
        print(f"\n   Overall Score: {score.get('overallScore', 'N/A')}")

        if "breakdown" in score:
            print("   Breakdown:")
            for category, details in score["breakdown"].items():
                cat_score = details.get("score", 0)
                max_score = details.get("maxScore", 0)
                print(f"     - {category}: {cat_score}/{max_score}")

    # Display suggestions
    if "suggestions" in rescore_data:
        suggestions = rescore_data["suggestions"]
        print(f"\n   Suggestions count: {len(suggestions)}")
        if len(suggestions) > 0:
            print("   Sample suggestions:")
            for i, sug in enumerate(suggestions[:3]):
                print(f"     {i+1}. {sug.get('title', 'No title')} ({sug.get('severity', 'unknown')})")

    # Step 3: Test invalid session
    print("\n4. Testing invalid session handling...")
    response = requests.post(
        f"{BASE_URL}/api/editor/rescore",
        json={"session_id": "invalid_session_12345"}
    )

    if response.status_code in [400, 404]:
        print("   ✅ Invalid session rejected correctly")
        checks.append(True)
    else:
        print(f"   ❌ Expected 400/404, got {response.status_code}")
        checks.append(False)

    # Final results
    print("\n" + "=" * 50)
    if all(checks):
        print("✅ ALL TESTS PASSED")
        return True
    else:
        passed = sum(checks)
        total = len(checks)
        print(f"⚠️  SOME TESTS FAILED: {passed}/{total} passed")
        return False


if __name__ == "__main__":
    print("ATS Resume Scorer - Rescore Endpoint Test")
    print("=" * 50)
    print("\nNOTE: Make sure the server is running on localhost:8000")
    print("      Start with: cd backend && uvicorn backend.main:app --reload\n")

    input("Press Enter to start tests...")

    try:
        success = test_rescore_endpoint()
        sys.exit(0 if success else 1)
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Could not connect to server at localhost:8000")
        print("   Please start the server first:")
        print("   cd backend && uvicorn backend.main:app --reload")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
