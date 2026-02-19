import pytest
from fastapi.testclient import TestClient
from docx import Document
from io import BytesIO
from backend.main import app
from backend.services.docx_template_manager import DocxTemplateManager

client = TestClient(app)

@pytest.fixture
def test_session(tmp_path):
    """Create test session with DOCX"""
    # Create test DOCX
    doc = Document()
    doc.add_heading('Test Resume', level=1)
    doc.add_paragraph('Test content')

    docx_bytes = BytesIO()
    doc.save(docx_bytes)
    docx_bytes.seek(0)

    # Save via template manager
    manager = DocxTemplateManager(storage_dir=str(tmp_path / "templates"))
    session_id = "test_preview_session"
    manager.save_template(session_id, docx_bytes.read())

    return session_id

def test_get_preview_docx(test_session):
    """Test serving preview DOCX file"""
    response = client.get(f"/api/preview/{test_session}.docx")

    assert response.status_code == 200
    assert response.headers['content-type'] == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    assert len(response.content) > 0
