import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.services.docx_template_manager import DocxTemplateManager
from pathlib import Path
import uuid

client = TestClient(app)

@pytest.fixture
def template_manager():
    """Get template manager instance"""
    return DocxTemplateManager()

@pytest.fixture
def sample_session(template_manager):
    """Create a sample session with a working DOCX file"""
    session_id = str(uuid.uuid4())

    # Create minimal DOCX file
    from docx import Document
    doc = Document()
    doc.add_paragraph("Test resume content")

    # Save as bytes
    import io
    docx_bytes = io.BytesIO()
    doc.save(docx_bytes)
    docx_bytes.seek(0)

    # Save template
    template_manager.save_template(session_id, docx_bytes.read())

    yield session_id

    # Cleanup
    working_path = template_manager.get_working_path(session_id)
    if working_path.exists():
        working_path.unlink()

    original_path = template_manager.storage_dir / f"{session_id}_original.docx"
    if original_path.exists():
        original_path.unlink()


def test_download_working_docx(sample_session):
    """Test downloading the working DOCX file"""
    session_id = sample_session

    # Download working DOCX
    response = client.get(f"/api/downloads/{session_id}_working.docx")

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    assert len(response.content) > 0

    # Verify it's a valid DOCX by checking magic bytes
    # DOCX files are ZIP files, so they start with 'PK'
    assert response.content[:2] == b'PK', "Response should be a valid ZIP/DOCX file"


def test_download_nonexistent_file():
    """Test downloading file that doesn't exist"""
    # Use a valid UUID that doesn't have a corresponding file
    nonexistent_uuid = str(uuid.uuid4())
    response = client.get(f"/api/downloads/{nonexistent_uuid}_working.docx")
    assert response.status_code == 404


def test_download_invalid_filename():
    """Test downloading with invalid filename format"""
    response = client.get("/api/downloads/invalid.txt")
    assert response.status_code == 400
    assert "Invalid filename format" in response.json()["detail"]


def test_download_invalid_session_id_format():
    """Test downloading with invalid session ID (not a UUID)"""
    response = client.get("/api/downloads/not-a-uuid_working.docx")
    assert response.status_code == 400
    assert "Invalid session ID format" in response.json()["detail"]


def test_download_path_traversal_attempt():
    """Test that path traversal attempts are blocked"""
    # FastAPI normalizes the path and blocks path traversal at route level
    # The ../ gets removed, so the path doesn't match our route pattern
    response = client.get("/api/downloads/../../../etc/passwd_working.docx")
    assert response.status_code == 404  # Route not found after path normalization
