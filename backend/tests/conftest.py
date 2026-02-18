"""
Shared pytest configuration and fixtures for all tests.
"""
import pytest
import tempfile
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from backend.main import app
from backend.database import Base, get_db
# Import all models to ensure they are registered with Base
from backend.models.user import User
from backend.models.resume import Resume
from backend.models.ad_view import AdView


# Create test database (SQLite file-based for persistence during test run)
test_db_fd, test_db_path = tempfile.mkstemp()
TEST_DATABASE_URL = f"sqlite:///{test_db_path}"
test_engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


# Override the get_db dependency
def override_get_db():
    """Override get_db for tests"""
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()


# Set up app with test database
app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """Create database schema once for all tests"""
    Base.metadata.create_all(bind=test_engine)
    yield
    # Cleanup: close and remove test database file
    os.close(test_db_fd)
    os.unlink(test_db_path)


@pytest.fixture(scope="function", autouse=True)
def clean_database():
    """Clean all tables before each test"""
    # Drop and recreate all tables for clean state
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)
    yield


@pytest.fixture(scope="module")
def client():
    """FastAPI test client"""
    return TestClient(app)
