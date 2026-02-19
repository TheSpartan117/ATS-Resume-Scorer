# ATS Resume Scorer - Backend API

FastAPI backend for the ATS Resume Scorer platform. This API provides resume parsing, scoring, and analysis capabilities to help job seekers optimize their resumes for Applicant Tracking Systems.

## Features

- Resume parsing (PDF/DOCX support)
- ATS compatibility scoring with 50+ rules across 6 categories
- RESTful API with automatic OpenAPI documentation
- PostgreSQL database integration
- JWT authentication
- Rate limiting
- CORS support for React frontend

## Prerequisites

Choose one of the following setups:

### Option A: Docker (Recommended)
- Docker installed
- Docker Compose (optional, for database)

### Option B: Local Python Development
- Python 3.11+ (3.11 recommended for full compatibility)
- PostgreSQL 14+
- pip

**Note:** Python 3.14 has compatibility issues with some dependencies. See [PYTHON_314_COMPATIBILITY.md](PYTHON_314_COMPATIBILITY.md) for details.

## Quick Start

### Option A: Using Docker (Recommended)

1. **Build the Docker image:**
   ```bash
   cd backend
   docker build -t ats-backend .
   ```

2. **Run the container:**
   ```bash
   docker run -p 8000:8000 ats-backend
   ```

3. **Access the API:**
   - API: http://localhost:8000
   - Health check: http://localhost:8000/health
   - Interactive docs: http://localhost:8000/docs
   - Alternative docs: http://localhost:8000/redoc

### Option B: Local Development Setup

1. **Install Python 3.11** (if using Python 3.14, see compatibility notes):
   ```bash
   # Using pyenv (recommended)
   pyenv install 3.11.9
   pyenv local 3.11.9
   ```

2. **Create and activate virtual environment:**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Download spaCy language model:**
   ```bash
   python -m spacy download en_core_web_sm
   ```

5. **Create environment configuration:**
   ```bash
   cp .env.example .env
   # Edit .env with your actual configuration
   ```

6. **Run the development server:**
   ```bash
   python main.py
   ```

   Or with uvicorn directly:
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

7. **Access the API:**
   - API: http://localhost:8000
   - Health check: http://localhost:8000/health
   - Interactive docs: http://localhost:8000/docs

## Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
# Database
DATABASE_URL=postgresql://username:password@localhost/ats_scorer

# JWT Authentication
JWT_SECRET_KEY=your-secure-secret-key-min-32-characters
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=10080

# CORS (comma-separated origins)
CORS_ORIGINS=http://localhost:3000,http://localhost:5173

# File Upload Limits
MAX_FILE_SIZE_MB=10

# Environment (development/production)
ENVIRONMENT=development
```

**Security Notes:**
- Change `JWT_SECRET_KEY` to a strong random value (minimum 32 characters)
- Update `DATABASE_URL` with your actual credentials
- In production, set `ENVIRONMENT=production` for stricter CORS policies

## Testing

### Test Health Endpoint

```bash
curl http://localhost:8000/health
# Expected: {"status":"healthy"}
```

### Test Root Endpoint

```bash
curl http://localhost:8000/
# Expected: {"message":"ATS Resume Scorer API","version":"1.0.0"}
```

### Interactive API Documentation

Visit http://localhost:8000/docs for Swagger UI where you can:
- View all available endpoints
- Test API requests interactively
- See request/response schemas

## Project Structure

```
backend/
├── main.py                         # FastAPI application entry point
├── requirements.txt                # Python dependencies
├── Dockerfile                      # Docker configuration
├── .env.example                    # Environment variables template
├── .gitignore                      # Git ignore patterns
├── README.md                       # This file
└── PYTHON_314_COMPATIBILITY.md    # Python 3.14 compatibility notes
```

## API Endpoints

### Current Endpoints

- `GET /` - Root endpoint, returns API info
- `GET /health` - Health check endpoint

### Planned Endpoints (MVP Phase 1)

- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/resumes/upload` - Upload and parse resume
- `GET /api/v1/resumes/{id}` - Get resume details
- `POST /api/v1/resumes/{id}/score` - Score resume
- `GET /api/v1/resumes/{id}/analysis` - Get detailed analysis

## Development

### Code Style

- Follow PEP 8 guidelines
- Use type hints
- Document functions with docstrings
- Keep functions small and focused

### Running in Development Mode

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The `--reload` flag enables auto-restart on code changes.

### Database Setup (Coming in Task 2)

Database schema and models will be implemented in the next task.

## Troubleshooting

### Python 3.14 Compatibility Issues

If you're running Python 3.14, you may encounter build errors with `PyMuPDF==1.23.0` and `spacy==3.7.0`. See [PYTHON_314_COMPATIBILITY.md](PYTHON_314_COMPATIBILITY.md) for:
- Detailed error descriptions
- Recommended solutions
- Alternative approaches

**Recommended solution:** Use Docker or Python 3.11 for development.

### Port Already in Use

If port 8000 is already in use:

```bash
# Find and kill the process
lsof -ti:8000 | xargs kill -9

# Or run on a different port
uvicorn main:app --port 8001
```

### Import Errors

Make sure your virtual environment is activated and all dependencies are installed:

```bash
source venv/bin/activate
pip install -r requirements.txt
```

## Split-View Resume Editor

### Architecture

The split-view editor preserves original resume formatting while allowing section-based editing:

1. **Template Storage:** Original DOCX saved as template, working copy for edits
2. **Section Detection:** Dynamic detection of resume sections (no hardcoded names)
3. **Live Preview:** Microsoft Office Online viewer shows pixel-perfect preview
4. **Debounced Updates:** 500ms delay after typing before preview updates

### Components

- `services/section_detector.py` - Detect sections by heading styles, bold text, ALL CAPS
- `services/docx_template_manager.py` - Update sections while preserving formatting
- `api/preview.py` - Serve DOCX files and handle section updates

### Usage

```python
# Detect sections
detector = SectionDetector()
sections = detector.detect(docx_bytes)

# Update section
manager = DocxTemplateManager()
result = manager.update_section(
    session_id="abc123",
    start_para_idx=5,
    end_para_idx=8,
    new_content="Updated text"
)
```

## Contributing

1. Follow the existing code structure
2. Add tests for new features
3. Update documentation
4. Use meaningful commit messages

## License

[Add your license here]

## Support

For issues and questions:
- Create an issue in the project repository
- Contact the development team

---

**Next Steps:** Implement database schema and models (Task 2)
