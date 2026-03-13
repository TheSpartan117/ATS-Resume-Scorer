# ATS Resume Scorer

An intelligent resume scoring and editing platform that helps job seekers optimize their resumes for Applicant Tracking Systems (ATS).

## Features

- **21-Parameter Scoring** — Comprehensive evaluation across 6 categories
- **Role-Specific Optimization** — 19+ job roles with tailored keyword sets
- **Experience-Aware** — Adapts scoring to entry / mid / senior level
- **Research-Backed** — Keywords and action verbs sourced from 30,000+ real resumes
- **Real-Time Feedback** — Actionable, prioritized suggestions for improvement
- **Resume Editor** — In-browser DOCX editing with live re-scoring
- **Auth & History** — Accounts, saved resumes, premium tier

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | FastAPI 0.110, Python 3.11+ |
| Database | PostgreSQL 14+ (SQLAlchemy ORM, Alembic migrations) |
| Auth | JWT (PyJWT 2.8), bcrypt, slowapi rate limiting |
| Parsing | PyMuPDF, pdfplumber, python-docx, spaCy, sentence-transformers |
| Frontend | React 19, TypeScript, Vite, Tailwind CSS 3.4, React Router 7 |
| E2E Tests | Playwright 1.x (34 tests, 4 browsers) |
| Deployment | Render (API), Vercel (frontend), Supabase (database) |

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 20+
- PostgreSQL 14+ (or a Supabase project URL)

### 1. Clone

```bash
git clone https://github.com/TheSpartan117/ATS-Resume-Scorer.git
cd ATS-Resume-Scorer
```

### 2. Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Copy and fill in env vars (see Environment Variables section)
cp .env.example .env
# Edit .env — set DATABASE_URL and generate JWT_SECRET_KEY

uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 3. Frontend

```bash
cd frontend
npm install
cp .env.example .env.local      # set VITE_API_URL=http://localhost:8000
npm run dev
```

### 4. Open

| Service | URL |
|---|---|
| Frontend | http://localhost:5173 |
| API docs (Swagger) | http://localhost:8000/docs |
| Health check | http://localhost:8000/health |

## Environment Variables

### Backend (`backend/.env`)

| Variable | Required | Description |
|---|---|---|
| `DATABASE_URL` | Yes | PostgreSQL connection string |
| `JWT_SECRET_KEY` | Yes | Secret for signing JWTs. Generate: `python -c "import secrets; print(secrets.token_hex(32))"` |
| `ONLYOFFICE_JWT_SECRET` | Yes | Secret for OnlyOffice Document Server JWT. Same generation command. |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | No | Token lifetime in minutes (default: `30`) |
| `ENVIRONMENT` | No | `production` (default) or `development`. Controls CORS strictness. |
| `CORS_ORIGINS` | No | Comma-separated allowed origins (default: localhost ports) |
| `ONLYOFFICE_SERVER_URL` | No | OnlyOffice server URL (default: `http://localhost:8080`) |
| `BACKEND_URL` | No | Public backend URL used in OnlyOffice callbacks |
| `ENABLE_SEMANTIC_MATCHING` | No | `true` to enable sentence-transformers (~90 MB, disabled by default) |

See [`backend/.env.example`](./backend/.env.example) for all variables with descriptions.

### Frontend (`frontend/.env.local`)

| Variable | Required | Description |
|---|---|---|
| `VITE_API_URL` | Yes (prod) | Backend API base URL. Leave unset in dev (proxied via Vite). |

## Scoring System

### Categories (100 pts total, up to 130 with bonuses)

| Category | Standard | Max w/ Bonus |
|---|---|---|
| Keyword Matching | 25 pts | 35 pts |
| Content Quality | 35 pts | 45 pts |
| Format & Structure | 15 pts | 20 pts |
| Professional Polish | 10 pts | 15 pts |
| Experience Validation | 10 pts | 10 pts |
| Readability | 5 pts | 5 pts |

### Rating Scale

| Score | Rating |
|---|---|
| 85–100 | Excellent — ATS-optimized, highly competitive |
| 70–84 | Good — strong resume, minor improvements needed |
| 50–69 | Fair — needs significant improvements |
| 0–49 | Poor — major overhaul required |

## Project Structure

```
ATS-Resume-Scorer/
├── backend/
│   ├── api/              # FastAPI routers (upload, auth, editor, export …)
│   ├── auth/             # JWT + bcrypt helpers, FastAPI dependencies
│   ├── models/           # SQLAlchemy models (User, EditorSession)
│   ├── services/         # Scoring engine, parsers, NLP, formatters
│   ├── schemas/          # Pydantic response schemas
│   ├── alembic/          # DB migrations
│   └── main.py           # FastAPI app entry point
├── frontend/
│   ├── src/
│   │   ├── components/   # React components (UploadPage, ResultsPage, AuthModal …)
│   │   ├── api/          # Typed API client
│   │   └── types/        # TypeScript types
│   ├── e2e/
│   │   ├── specs/        # Playwright test specs
│   │   └── pages/        # Page Object Models
│   └── playwright.config.ts
├── docs/
│   ├── CONTRIBUTING.md
│   └── RUNBOOK.md
└── .github/
    └── workflows/
        └── e2e.yml       # CI: Playwright E2E on push/PR
```

## Running Tests

### E2E (Playwright)

```bash
cd frontend

# Run all tests (starts Vite dev server automatically)
npm run test:e2e

# Interactive UI mode
npm run test:e2e:ui

# Smoke tests against a deployed URL
BASE_URL=https://your-app.vercel.app npm run test:e2e:smoke
```

34 tests across 4 specs: `upload`, `auth`, `results`, `health`.

### Backend unit tests

```bash
cd backend
python -m pytest tests/
```

## API Reference

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `POST` | `/api/upload` | No | Upload PDF/DOCX and get score |
| `GET` | `/api/roles` | No | List all roles and levels |
| `POST` | `/api/signup` | No | Create account |
| `POST` | `/api/login` | No | Get JWT token |
| `GET` | `/api/me` | Bearer | Current user info |
| `POST` | `/api/editor/session` | Bearer | Create editor session |
| `POST` | `/api/editor/rescore` | Bearer | Re-score after edits |
| `GET` | `/health` | No | Health check |

Full interactive docs at `/docs` (Swagger UI) when the backend is running.

## Security

All security controls are implemented and active:

- **Authentication** — JWT with configurable expiry; app refuses to start without `JWT_SECRET_KEY`
- **Password validation** — min 8 / max 128 chars, bcrypt hashing
- **File upload** — magic byte validation (PDF: `%PDF-`, DOCX: `PK\x03\x04`), 10 MB limit, path traversal prevention
- **Rate limiting** — login: 10 req/min, signup: 5 req/min, upload: 20 req/min (per IP)
- **Session ownership** — all editor endpoints check `user_id` before read/write
- **Error responses** — no internal paths or exception messages returned to clients
- **CORS** — strict methods/headers in production; permissive only when `ENVIRONMENT=development`
- **SSRF** — OnlyOffice callback URL validated against configured server origin before any outbound request
- **CVE-2024-33663** — `python-jose` replaced by `pyjwt` throughout

## Deployment

See [`docs/RUNBOOK.md`](./docs/RUNBOOK.md) for step-by-step deployment to Render + Vercel + Supabase.

## Contributing

See [`docs/CONTRIBUTING.md`](./docs/CONTRIBUTING.md) for dev setup, coding conventions, testing guide, and PR checklist.

## License

MIT — see [LICENSE](./LICENSE).

## Acknowledgments

- Resume corpus: [Jiechieu & Tsopze (2020)](https://doi.org/10.1007/s00521-020-05302-x) — 29,783 resumes analyzed
- ResumeWorded for calibration benchmarks
- FastAPI and React communities
