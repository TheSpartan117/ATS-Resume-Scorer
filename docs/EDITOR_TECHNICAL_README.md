# Resume Editor - Technical Documentation

## Architecture Overview

The Resume Editor is built with a React frontend and FastAPI backend, featuring session-based DOCX editing with real-time scoring and suggestions.

### System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     Frontend (React)                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ EditorPage   │  │ Suggestions  │  │ RichEditor   │  │
│  │ (Main)       │  │ Panel        │  │ (TipTap)     │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
│          ↓                  ↓                 ↓          │
│  ┌──────────────────────────────────────────────────┐  │
│  │            API Client (fetch)                     │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
                         ↓ HTTP/REST
┌─────────────────────────────────────────────────────────┐
│                   Backend (FastAPI)                      │
│  ┌──────────────────────────────────────────────────┐  │
│  │              Editor API Router                    │  │
│  │  - POST /api/editor/session                      │  │
│  │  - GET  /api/editor/session/{id}                 │  │
│  │  - POST /api/editor/apply-suggestion             │  │
│  │  - POST /api/editor/update-section               │  │
│  │  - POST /api/editor/rescore                      │  │
│  │  - GET  /api/downloads/{filename}                │  │
│  └──────────────────────────────────────────────────┘  │
│          ↓                  ↓                 ↓          │
│  ┌─────────────┐  ┌────────────────┐  ┌──────────────┐ │
│  │  Template   │  │  Suggestion    │  │  ATS         │ │
│  │  Manager    │  │  Generator     │  │  Scorer      │ │
│  └─────────────┘  └────────────────┘  └──────────────┘ │
│          ↓                                               │
│  ┌──────────────────────────────────────────────────┐  │
│  │  File Storage (DOCX files)                       │  │
│  │  - {sessionId}_original.docx                     │  │
│  │  - {sessionId}_working.docx                      │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

## Technology Stack

### Frontend
- **React** 18.x - UI framework
- **TypeScript** 5.x - Type safety
- **TipTap** 2.x - Rich text editor
- **React Router** 6.x - Routing
- **Vitest** - Testing framework
- **React Testing Library** - Component testing

### Backend
- **Python** 3.10+
- **FastAPI** - API framework
- **python-docx** - DOCX manipulation
- **BeautifulSoup4** - HTML parsing
- **pytest** - Testing framework

### External Services
- **Office Online API** - DOCX preview rendering

## Project Structure

```
ats-resume-scorer/
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── SuggestionCard.tsx
│   │   │   ├── SuggestionsPanel.tsx
│   │   │   ├── RichEditor.tsx
│   │   │   ├── OfficePreview.tsx
│   │   │   └── __tests__/
│   │   ├── pages/
│   │   │   ├── EditorPage.tsx
│   │   │   └── __tests__/
│   │   └── App.tsx
│   └── package.json
├── backend/
│   ├── api/
│   │   ├── editor.py          # Editor endpoints
│   │   └── files.py           # File download
│   ├── services/
│   │   ├── docx_template_manager.py
│   │   ├── section_detector.py
│   │   ├── suggestion_generator.py
│   │   └── ats_scorer.py
│   ├── tests/
│   │   ├── test_api_editor.py
│   │   ├── test_apply_suggestion.py
│   │   ├── test_update_section.py
│   │   ├── test_rescore.py
│   │   ├── test_file_download.py
│   │   └── test_integration_editor.py
│   └── storage/
│       └── templates/          # DOCX files
└── docs/
    ├── EDITOR_USER_GUIDE.md
    └── EDITOR_TECHNICAL_README.md
```

## API Reference

### Session Management

#### Create Session
```http
POST /api/editor/session
Content-Type: application/json

{
  "resume_id": "string",
  "role": "software_engineer",  // optional
  "level": "mid"                // optional
}
```

**Response:**
```json
{
  "session_id": "uuid",
  "working_docx_url": "/api/downloads/{sessionId}_working.docx",
  "sections": [
    {
      "name": "Contact",
      "start_para": 0,
      "end_para": 3
    }
  ],
  "current_score": {
    "overallScore": 75
  },
  "suggestions": [...]
}
```

#### Get Session
```http
GET /api/editor/session/{sessionId}
```

Returns same structure as create session.

### Suggestion Management

#### Apply Suggestion
```http
POST /api/editor/apply-suggestion
Content-Type: application/json

{
  "session_id": "uuid",
  "suggestion_id": "string",
  "action": "add_phone|replace_text|add_section|show_location",
  "value": "string or JSON"
}
```

**Action Types:**

1. **add_phone**: `value = "(555) 123-4567"`
2. **replace_text**: `value = JSON.stringify({current_text, suggested_text, para_idx})`
3. **add_section**: `value = "Section Name\nSection content..."`
4. **show_location**: `value = null` (frontend-only navigation)

**Response:**
```json
{
  "success": true,
  "updated_section": "Contact",
  "content": "<p>Phone: (555) 123-4567</p>"
}
```

### Content Management

#### Update Section
```http
POST /api/editor/update-section
Content-Type: application/json

{
  "session_id": "uuid",
  "section": "Experience",
  "content": "<p>HTML from TipTap editor</p>",
  "start_para": 5,
  "end_para": 10
}
```

**Response:**
```json
{
  "success": true,
  "updated_url": "/api/downloads/{sessionId}_working.docx"
}
```

### Scoring

#### Re-score Resume
```http
POST /api/editor/rescore
Content-Type: application/json

{
  "session_id": "uuid"
}
```

**Response:**
```json
{
  "score": {
    "overallScore": 82,
    "breakdown": {
      "keywords": {"score": 28, "maxScore": 35},
      "red_flags": {"score": 18, "maxScore": 20},
      "experience": {"score": 16, "maxScore": 20},
      "formatting": {"score": 15, "maxScore": 20},
      "contact": {"score": 5, "maxScore": 5}
    }
  },
  "suggestions": [...]
}
```

### File Management

#### Download DOCX
```http
GET /api/downloads/{sessionId}_working.docx
```

Returns DOCX file stream with proper MIME type.

## Data Models

### Suggestion Model

```typescript
interface Suggestion {
  id: string;                    // Unique identifier
  type: 'missing_content' | 'content_change' | 'missing_section' | 'formatting';
  severity: 'critical' | 'warning' | 'suggestion' | 'info';
  title: string;                 // Short description
  description: string;           // Detailed explanation
  location: {
    section: string | null;      // e.g., "Contact", "Experience"
    line: number | null;         // Line number if applicable
    para_idx?: number;           // Paragraph index for replacement
  };
  action: string;                // Action identifier
  example?: string;              // Example of correct format
  current_text?: string;         // For replacement suggestions
  suggested_text?: string;       // For replacement suggestions
  template?: string;             // For section addition
  state?: 'pending' | 'fixed' | 'dismissed';
}
```

### Score Model

```typescript
interface Score {
  overallScore: number;          // 0-100
  breakdown?: {
    keywords?: {
      score: number;
      maxScore: number;
      details?: any;
    };
    // ... other categories
  };
}
```

### Section Model

```typescript
interface Section {
  name: string;                  // Section name
  start_para: number;            // Starting paragraph index
  end_para: number;              // Ending paragraph index
}
```

## Component Reference

### EditorPage

**Location**: `frontend/src/pages/EditorPage.tsx`

**Props**: None (uses URL params)

**State**:
- `activeTab`: Current tab ('editor' | 'preview')
- `sections`: Resume sections
- `currentScore`: Scoring data
- `suggestions`: Suggestion list
- `workingDocxUrl`: DOCX file URL
- `lastScored`: Last scoring timestamp

**Key Methods**:
- `handleSuggestionClick(suggestion)`: Navigate to suggestion location
- `handleRescore()`: Trigger re-scoring
- `handleDownload()`: Download DOCX file

### SuggestionsPanel

**Location**: `frontend/src/components/SuggestionsPanel.tsx`

**Props**:
```typescript
{
  suggestions: Suggestion[];
  currentScore: Score;
  onSuggestionClick: (suggestion: Suggestion) => void;
  onRescore: () => void;
  lastScored?: Date;
}
```

**Features**:
- Groups suggestions by severity
- Collapsible groups
- Progress tracking
- Re-score button

### RichEditor

**Location**: `frontend/src/components/RichEditor.tsx`

**Props**:
```typescript
{
  content: string;               // HTML content
  onChange: (html: string) => void;
  sectionId?: string;            // Optional section identifier
  compact?: boolean;             // Compact toolbar mode
  editable?: boolean;            // Read-only mode
  onReady?: () => void;          // Editor initialized callback
}
```

**Extensions**:
- StarterKit (basic formatting)
- Placeholder
- TextAlign
- Underline

### OfficePreview

**Location**: `frontend/src/components/OfficePreview.tsx`

**Props**:
```typescript
{
  docxUrl: string;               // URL to DOCX file
  sessionId: string;             // Session identifier
}
```

**Features**:
- Office Online iframe embed
- Zoom controls
- Refresh button
- Download button
- Error handling for localhost

## Testing

### Running Tests

**Backend:**
```bash
cd backend
pytest tests/ -v                           # All tests
pytest tests/test_api_editor.py -v        # Specific file
pytest tests/test_integration_editor.py -v # Integration tests
```

**Frontend:**
```bash
cd frontend
npm test                                   # All tests
npm test EditorPage.test.tsx              # Specific file
npm run test:coverage                      # With coverage
```

### Test Coverage

**Backend**:
- Unit tests: 26 tests (100% passing)
- Integration tests: 6 tests (3 skipped)
- Coverage: API endpoints, services, error handling

**Frontend**:
- Component tests: All components
- Integration tests: EditorPage
- Mocked API calls for isolation

### Writing Tests

**Backend Example:**
```python
def test_update_section():
    # Create session
    response = client.post("/api/editor/session", json={
        "resume_id": "test"
    })
    session_id = response.json()["session_id"]

    # Create DOCX file
    create_docx_for_session(session_id)

    # Update section
    response = client.post("/api/editor/update-section", json={
        "session_id": session_id,
        "section": "Experience",
        "content": "<p>New content</p>",
        "start_para": 5,
        "end_para": 7
    })

    assert response.status_code == 200
```

**Frontend Example:**
```typescript
it('should render editor page', async () => {
  render(
    <BrowserRouter>
      <EditorPage />
    </BrowserRouter>
  );

  await waitFor(() => {
    expect(screen.getByText(/Resume Editor/i)).toBeInTheDocument();
  });
});
```

## Development Setup

### Prerequisites
- Node.js 18+
- Python 3.10+
- npm or yarn

### Installation

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

**Frontend:**
```bash
cd frontend
npm install
```

### Running Locally

**Backend:**
```bash
cd backend
uvicorn backend.main:app --reload --port 8000
```

**Frontend:**
```bash
cd frontend
npm run dev
```

**Access**:
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Environment Variables

**Backend** (`.env`):
```env
ENVIRONMENT=development
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

**Frontend** (`.env`):
```env
VITE_API_URL=http://localhost:8000
```

## Deployment

### Production Considerations

**Backend**:
1. Set `ENVIRONMENT=production`
2. Configure proper CORS origins
3. Use production ASGI server (uvicorn with gunicorn)
4. Set up file storage (S3/Azure Blob)
5. Implement session persistence (database)
6. Add rate limiting
7. Enable HTTPS

**Frontend**:
1. Build: `npm run build`
2. Serve `dist/` folder
3. Configure API URL
4. Enable CDN
5. Set up proper routing (SPA fallback)

### Docker Deployment

```dockerfile
# Backend Dockerfile
FROM python:3.10
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```dockerfile
# Frontend Dockerfile
FROM node:18 AS build
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
```

## Performance Optimization

### Backend
- **Caching**: Cache scoring results (Redis)
- **Async I/O**: Use async file operations
- **Connection Pooling**: Database connections
- **CDN**: Serve static DOCX files from CDN

### Frontend
- **Code Splitting**: Lazy load routes
- **Memoization**: React.memo for heavy components
- **Debouncing**: Auto-save with 2s debounce
- **Virtual Scrolling**: For large suggestion lists

## Security

### Implemented
- UUID validation (path traversal prevention)
- Session isolation
- CORS configuration
- Input sanitization (HTML parsing)
- File type validation

### Recommended
- Authentication/Authorization
- Rate limiting
- CSRF protection
- File size limits
- Malware scanning for uploads

## Known Issues & Limitations

1. **Session Persistence**: In-memory only (resets on restart)
2. **Concurrent Editing**: Not supported
3. **Large Files**: May timeout on very large DOCX files
4. **Complex Formatting**: Tables/columns may parse incorrectly
5. **Offline Mode**: Preview requires internet connection

## Future Enhancements

### Planned Features
- [ ] Session persistence (database)
- [ ] PDF support
- [ ] Collaborative editing
- [ ] Version history
- [ ] Template library
- [ ] AI-powered suggestions
- [ ] Mobile responsive design
- [ ] Real-time preview updates
- [ ] Export to multiple formats
- [ ] Integration with job boards

### Technical Debt
- Replace in-memory session store with database
- Add proper error tracking (Sentry)
- Implement file storage abstraction
- Add comprehensive logging
- Set up CI/CD pipeline
- Add performance monitoring

## Contributing

### Code Style
- **Backend**: PEP 8, Black formatter
- **Frontend**: Prettier, ESLint
- **Commits**: Conventional commits format

### Pull Request Process
1. Create feature branch from `main`
2. Write tests (TDD approach)
3. Ensure all tests pass
4. Update documentation
5. Create PR with clear description
6. Get code review approval
7. Merge to main

## Support

### Debugging

**Enable Debug Logging (Backend)**:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

**Enable Debug Mode (Frontend)**:
```typescript
console.log('Debug mode enabled');
localStorage.setItem('debug', 'true');
```

### Common Issues

**Issue**: Session not found (404)
**Solution**: Check session_id is valid UUID, session may have expired

**Issue**: Preview not loading
**Solution**: Verify DOCX file exists, check internet connection

**Issue**: Changes not saving
**Solution**: Wait for debounce (2s), check console for errors

## Version Information

- **Current Version**: 1.0.0
- **Release Date**: February 19, 2026
- **Last Updated**: February 19, 2026

## License

See LICENSE file in repository root.

## Credits

Built with Claude Opus 4.6 using Test-Driven Development (TDD) methodology.

---

**For user documentation, see:** `/docs/EDITOR_USER_GUIDE.md`
