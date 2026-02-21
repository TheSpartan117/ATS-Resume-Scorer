# Development Guide - ATS Resume Scorer

**Version**: 3.0
**Last Updated**: February 22, 2026

## Overview

This guide covers everything you need to develop, extend, and contribute to the ATS Resume Scorer project.

## Prerequisites

### Required Software
- **Python**: 3.10+ (tested on 3.14)
- **Node.js**: 18+ (tested on 20.x)
- **Git**: 2.x
- **Code Editor**: VS Code recommended

### Optional Tools
- **Docker**: For containerized deployment
- **Postman/Insomnia**: For API testing
- **pytest**: For running backend tests

---

## Project Setup

### 1. Clone Repository

```bash
git clone https://github.com/JoHn11117/ATS-Resume-Scorer.git
cd ATS-Resume-Scorer
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Verify installation
python -c "import fastapi; print('FastAPI:', fastapi.__version__)"
```

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Verify installation
npm list react react-dom
```

### 4. Run Development Servers

**Terminal 1 - Backend**:
```bash
cd backend
source venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

**Terminal 2 - Frontend**:
```bash
cd frontend
npm run dev
```

**Access**:
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

---

## Project Structure

```
ats-resume-scorer/
├── backend/
│   ├── api/                      # API endpoints
│   │   ├── main.py              # FastAPI app
│   │   ├── upload.py            # Upload endpoint
│   │   └── roles.py             # Roles endpoint
│   ├── services/                 # Business logic
│   │   ├── scorer_v3.py         # Main scoring engine
│   │   ├── parser.py            # Document parsing
│   │   ├── role_keywords.py     # Role-specific keywords
│   │   └── parameters/          # 21 scoring parameters
│   │       ├── p1_1_required_keywords.py
│   │       ├── p1_2_preferred_keywords.py
│   │       ├── p2_1_action_verbs.py
│   │       └── ... (18 more)
│   ├── data/
│   │   ├── action_verb_tiers.json  # 236 categorized verbs
│   │   └── corpus_source/          # Resume corpus data
│   ├── tests/                    # Backend tests
│   └── requirements.txt          # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── components/          # React components
│   │   │   ├── UploadPage.tsx   # File upload UI
│   │   │   ├── ResultsPage.tsx  # Score display
│   │   │   └── FileDropZone.tsx # Drag-drop upload
│   │   ├── api/
│   │   │   └── client.ts        # API client
│   │   └── types/
│   │       └── resume.ts        # TypeScript types
│   ├── public/                  # Static assets
│   ├── package.json             # Node dependencies
│   └── vite.config.ts           # Vite configuration
└── docs/                        # Documentation
    ├── SYSTEM_OVERVIEW.md
    ├── SCORING_SYSTEM.md
    ├── KEYWORDS_AND_VERBS.md
    └── API_GUIDE.md
```

---

## Adding New Features

### 1. Adding a New Scoring Parameter

**Step 1: Create parameter file**

```bash
cd backend/services/parameters
touch p8_1_new_parameter.py
```

**Step 2: Implement scorer class**

```python
# p8_1_new_parameter.py
"""
P8.1: New Parameter Name (X points)

Description of what this parameter measures.
"""

from typing import Dict, Any

class NewParameterScorer:
    """Scores resumes based on [specific criteria]."""

    def __init__(self):
        """Initialize scorer."""
        self.max_score = 5  # Define max points

    def score(self, resume: Any, **kwargs) -> Dict[str, Any]:
        """
        Calculate score for this parameter.

        Args:
            resume: Resume data object

        Returns:
            Dictionary with score and details
        """
        # Your scoring logic here
        score = 0
        details = {}

        # Example: Check for specific condition
        if self._check_condition(resume):
            score += 2.5

        return {
            'score': score,
            'max_score': self.max_score,
            'percentage': (score / self.max_score) * 100 if self.max_score > 0 else 0,
            'status': 'success',
            'details': details
        }

    def _check_condition(self, resume: Any) -> bool:
        """Helper method to check condition."""
        return True  # Implement your logic

# Convenience function
def score_new_parameter(resume: Any, **kwargs) -> Dict[str, Any]:
    """Score new parameter."""
    scorer = NewParameterScorer()
    return scorer.score(resume, **kwargs)
```

**Step 3: Register parameter**

```python
# services/parameters/registry.py

class ParameterRegistry:
    def _initialize_registry(self):
        # ... existing imports ...
        from backend.services.parameters.p8_1_new_parameter import NewParameterScorer

        self.parameters = {
            # ... existing parameters ...
            'P8.1': {
                'code': 'P8.1',
                'name': 'New Parameter Name',
                'description': 'Description of what it measures',
                'category': 'New Category',  # or existing category
                'max_score': 5,
                'scorer_class': NewParameterScorer
            }
        }
```

**Step 4: Update scorer_v3.py** (if adding new category)

```python
# services/scorer_v3.py

category_scores = {
    # ... existing categories ...
    'New Category': {'score': 0, 'max': 5, 'parameters': {}}
}
```

**Step 5: Write tests**

```python
# tests/services/parameters/test_p8_1_new_parameter.py

import pytest
from backend.services.parameters.p8_1_new_parameter import NewParameterScorer

def test_new_parameter_basic():
    """Test basic functionality."""
    scorer = NewParameterScorer()
    result = scorer.score(mock_resume)

    assert result['score'] >= 0
    assert result['max_score'] == 5
    assert 'details' in result

def test_new_parameter_perfect_score():
    """Test perfect score scenario."""
    scorer = NewParameterScorer()
    result = scorer.score(perfect_resume)

    assert result['score'] == 5
```

---

### 2. Adding a New Job Role

**Step 1: Define keywords**

```python
# services/role_keywords.py

ROLE_KEYWORDS = {
    # ... existing roles ...
    'new_role_id': {
        'required': [
            'keyword1', 'keyword2', 'keyword3',
            # Core role-specific terms
        ],
        'preferred': [
            'advanced_keyword1', 'advanced_keyword2',
            # Specialized/advanced terms
        ]
    }
}
```

**Step 2: Add to roles endpoint**

```python
# api/roles.py

class RoleCategory(str, Enum):
    # ... existing categories ...
    NEW_CATEGORY = "new_category"

ROLES_BY_CATEGORY = {
    # ... existing roles ...
    RoleCategory.NEW_CATEGORY: [
        ('new_role_id', 'New Role Name'),
    ]
}
```

**Step 3: Test the new role**

```bash
curl http://localhost:8000/api/roles | jq '.categories.new_category'
```

---

### 3. Adding Action Verbs

**Edit** `backend/data/action_verb_tiers.json`:

```json
{
  "tier_2": {
    "description": "Execution - Individual contribution",
    "points": 2,
    "verbs": [
      "existing_verb1",
      "existing_verb2",
      "new_verb_here"  // Add your verb
    ]
  }
}
```

**Verify**:
```bash
cd backend
python3 -c "
import json
with open('data/action_verb_tiers.json') as f:
    data = json.load(f)
    print(f\"Tier 2 verbs: {len(data['tier_2']['verbs'])}\")
"
```

---

## Testing

### Backend Tests

**Run all tests**:
```bash
cd backend
pytest
```

**Run specific test file**:
```bash
pytest tests/services/test_scorer_v3.py -v
```

**Run with coverage**:
```bash
pytest --cov=services --cov-report=html
open htmlcov/index.html
```

**Test scoring on a CV**:
```bash
cd backend
python3 -c "
from services.scorer_v3 import ScorerV3
from services.parser import parse_resume

resume_data = parse_resume('path/to/resume.pdf')
scorer = ScorerV3()
result = scorer.score(resume_data, role='product_manager', experience_level='intermediary')
print(f\"Score: {result['total_score']}/100\")
"
```

### Frontend Tests

```bash
cd frontend
npm test
```

### Integration Tests

```bash
# Terminal 1: Start backend
cd backend && uvicorn main:app --port 8000

# Terminal 2: Test upload
curl -X POST http://localhost:8000/api/upload \
  -F "file=@test_resume.pdf" \
  -F "role=product_manager"
```

---

## Debugging

### Backend Debugging

**1. Enable debug logging**:

```python
# main.py
import logging
logging.basicConfig(level=logging.DEBUG)
```

**2. Use pdb for breakpoints**:

```python
# In any file
import pdb; pdb.set_trace()
```

**3. Check logs**:

```bash
# Backend logs
tail -f backend.log

# Uvicorn logs
uvicorn main:app --log-level debug
```

### Frontend Debugging

**1. Console logging**:

```typescript
console.log('Debug:', variable);
console.table(data);
```

**2. React DevTools**:
- Install React Developer Tools browser extension
- Inspect component props and state

**3. Network tab**:
- Open browser DevTools (F12)
- Network tab → Filter by XHR
- Inspect API requests/responses

---

## Code Style

### Python (Backend)

**Follow PEP 8**:
```bash
# Install formatters
pip install black flake8

# Format code
black services/

# Check linting
flake8 services/
```

**Docstrings**:
```python
def score_parameter(resume: Any, **kwargs) -> Dict[str, Any]:
    """
    Score a specific parameter.

    Args:
        resume: Resume data object
        **kwargs: Additional scoring parameters

    Returns:
        Dictionary containing:
        - score: Points earned
        - max_score: Maximum possible points
        - details: Parameter-specific details

    Raises:
        ValueError: If resume data is invalid
    """
```

### TypeScript (Frontend)

**Use ESLint + Prettier**:
```bash
# Install
npm install --save-dev eslint prettier

# Format
npm run lint
npm run format
```

**Type Safety**:
```typescript
// Define interfaces
interface ScoreResult {
  total_score: number;
  rating: string;
}

// Use type annotations
const uploadResume = async (file: File): Promise<ScoreResult> => {
  // ...
}
```

---

## Git Workflow

### Branching Strategy

```bash
# Create feature branch
git checkout -b feature/new-parameter

# Make changes and commit
git add .
git commit -m "feat: add P8.1 new parameter"

# Push to GitHub
git push origin feature/new-parameter

# Create pull request on GitHub
```

### Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: add new scoring parameter P8.1
fix: correct action verb classification
docs: update API guide with new endpoint
refactor: simplify keyword matching logic
test: add tests for P2.2 quantification
```

---

## Deployment

### Production Build

**Backend**:
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

**Frontend**:
```bash
cd frontend
npm run build
npm run preview  # Test production build locally
```

### Docker (Future)

```dockerfile
# Dockerfile (backend)
FROM python:3.14-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## Performance Optimization

### Backend

**1. Profile slow endpoints**:
```python
import cProfile
import pstats

profiler = cProfile.Profile()
profiler.enable()

# Your code here

profiler.disable()
stats = pstats.Stats(profiler)
stats.sort_stats('cumtime')
stats.print_stats(10)
```

**2. Cache expensive computations**:
```python
from functools import lru_cache

@lru_cache(maxsize=128)
def expensive_function(param):
    # Cached result
    pass
```

### Frontend

**1. Lazy load components**:
```typescript
const ResultsPage = lazy(() => import('./components/ResultsPage'))
```

**2. Memoize expensive computations**:
```typescript
const expensiveValue = useMemo(() => {
  return computeExpensiveValue(data)
}, [data])
```

---

## Troubleshooting

### Backend Issues

**Problem**: `ModuleNotFoundError: No module named 'backend'`
**Solution**: Run from project root or use `PYTHONPATH`:
```bash
export PYTHONPATH=/path/to/ats-resume-scorer:$PYTHONPATH
```

**Problem**: LanguageTool connection errors
**Solution**: LanguageTool is optional, gracefully falls back to basic checking

**Problem**: PDF parsing failures
**Solution**: Ensure PyMuPDF is installed: `pip install pymupdf`

### Frontend Issues

**Problem**: API requests fail with CORS error
**Solution**: Check Vite proxy config in `vite.config.ts`

**Problem**: TypeScript errors after updating types
**Solution**: Restart TypeScript server in VSCode: `Cmd+Shift+P` → "Restart TS Server"

---

## Contributing

### Code Review Checklist

- [ ] Code follows style guidelines
- [ ] Tests added for new functionality
- [ ] Documentation updated
- [ ] No breaking changes (or documented)
- [ ] Performance impact considered
- [ ] Security implications reviewed

### Pull Request Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
How was this tested?

## Checklist
- [ ] Tests pass
- [ ] Documentation updated
- [ ] Code formatted
```

---

## Resources

### Documentation
- **FastAPI**: https://fastapi.tiangolo.com/
- **React**: https://react.dev/
- **TypeScript**: https://www.typescriptlang.org/docs/

### Tools
- **PyMuPDF**: https://pymupdf.readthedocs.io/
- **python-docx**: https://python-docx.readthedocs.io/
- **Vite**: https://vitejs.dev/

### Research
- **Resume Corpus**: https://github.com/florex/resume_corpus
- **ATS Research**: Search "ATS resume optimization" on Google Scholar

---

## Contact

- **GitHub**: https://github.com/JoHn11117/ATS-Resume-Scorer
- **Issues**: https://github.com/JoHn11117/ATS-Resume-Scorer/issues

---

## License

MIT License - See LICENSE file for details
