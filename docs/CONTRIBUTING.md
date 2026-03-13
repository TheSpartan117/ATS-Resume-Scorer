# Contributing to ATS Resume Scorer

Thank you for your interest in contributing! This guide covers development setup, testing, and code standards.

## Prerequisites

### Minimum Versions
- **Node.js**: 20+
- **Python**: 3.11+
- **PostgreSQL**: 14+
- **Git**: Any recent version

### Development Tools
- Virtual environment tool: `venv` (Python) or equivalent
- Package manager: `npm` (Node.js)
- Database client: `psql` (PostgreSQL)

## Environment Setup

### Backend Setup

1. **Clone and navigate:**
   ```bash
   git clone https://github.com/JoHn11117/ATS-Resume-Scorer.git
   cd ATS-Resume-Scorer/backend
   ```

2. **Create Python virtual environment:**
   ```bash
   python3.11 -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your local configuration:
   # - DATABASE_URL: PostgreSQL connection string
   # - JWT_SECRET_KEY: Generated secret (min 32 chars)
   # - ONLYOFFICE_JWT_SECRET: Generated secret (min 32 chars)
   ```

5. **Generate secrets (if needed):**
   ```bash
   python -c "import secrets; print('JWT_SECRET_KEY:', secrets.token_hex(32))"
   python -c "import secrets; print('ONLYOFFICE_JWT_SECRET:', secrets.token_hex(32))"
   ```

6. **Set up database:**
   ```bash
   # Run migrations (if using Alembic)
   alembic upgrade head

   # Or start PostgreSQL locally
   # psql -U postgres
   # CREATE DATABASE ats_scorer;
   ```

7. **Start development server:**
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

### Frontend Setup

1. **Navigate to frontend:**
   ```bash
   cd ATS-Resume-Scorer/frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Configure environment:**
   ```bash
   cp .env.example .env
   # VITE_API_URL should point to backend (http://localhost:8000)
   ```

4. **Start development server:**
   ```bash
   npm run dev
   ```
   Frontend runs on http://localhost:5173

## NPM Scripts Reference

### Development
- `npm run dev` — Start Vite dev server with HMR
- `npm run preview` — Preview production build locally

### Building
- `npm run build` — TypeScript check + Vite build (optimized)
- `npm run build:prod` — Production build only

### Testing
- `npm run test` — Run unit tests (Vitest)
- `npm run test:ui` — Interactive test UI
- `npm run test:coverage` — Coverage report
- `npm run test:e2e` — Run all E2E tests (Playwright)
- `npm run test:e2e:ui` — Interactive E2E test UI
- `npm run test:e2e:smoke` — Quick health checks
- `npm run test:e2e:report` — View HTML test report

### Code Quality
- `npm run lint` — ESLint checks

## Backend Testing

### Unit Tests
```bash
# Run all tests
python -m pytest

# Run specific test file
python -m pytest tests/test_scorer.py

# Run with coverage
python -m pytest --cov=backend tests/
```

### API Testing
```bash
# Test health endpoint
curl http://localhost:8000/health

# Test roles endpoint
curl http://localhost:8000/api/roles

# Interactive API docs
# Visit http://localhost:8000/docs
```

## E2E Testing (Playwright)

### Local Testing
```bash
# Run all E2E tests
npm run test:e2e

# Run specific test file
npx playwright test e2e/specs/upload.spec.ts

# Run with UI mode (recommended for development)
npm run test:e2e:ui

# Run smoke tests (health checks)
npm run test:e2e:smoke

# View detailed report
npm run test:e2e:report
```

### E2E Test Coverage
- **upload.spec.ts** (206 lines) — File upload, parsing, feedback
- **auth.spec.ts** (185 lines) — Registration, login, session management
- **results.spec.ts** (167 lines) — Score display, feedback, navigation
- **health.spec.ts** (63 lines) — Post-deployment smoke tests

### CI/CD E2E Tests
E2E tests run automatically on:
- Push to main branch
- Pull requests to main
- Manual workflow dispatch with custom URLs

See `.github/workflows/e2e.yml` for CI configuration.

## Code Style & Quality

### Python Backend
- Follow **PEP 8** guidelines
- Use type hints for all functions
- Docstrings for public functions and modules
- Maximum line length: 100 characters
- Use immutable data structures

### TypeScript Frontend
- **Strict mode**: No implicit `any`
- **ESLint**: Run `npm run lint` before committing
- **React best practices**: Functional components, hooks
- **File organization**: Small, focused files (<800 lines)
- **Naming**: Descriptive names for components and functions

### Git Commit Messages
```
<type>: <description>

<optional body>
```

**Types**: `feat`, `fix`, `refactor`, `docs`, `test`, `chore`, `perf`, `ci`

Example:
```
feat: add JWT authentication with configurable expiry

- Implement JWT-based auth with ACCESS_TOKEN_EXPIRE_MINUTES env var
- Add password validation with bcrypt
- Add rate limiting on auth endpoints
```

## Environment Variables

### Backend (.env)
<!-- AUTO-GENERATED -->

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DATABASE_URL` | ✓ | — | PostgreSQL connection string |
| `JWT_SECRET_KEY` | ✓ | — | JWT signing key (min 32 chars) |
| `JWT_ALGORITHM` | ✗ | HS256 | JWT algorithm (must be HS256) |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | ✗ | 30 | Token expiration time (minutes) |
| `ONLYOFFICE_SERVER_URL` | ✗ | http://localhost:8080 | OnlyOffice Document Server URL |
| `ONLYOFFICE_JWT_SECRET` | ✓ | — | OnlyOffice JWT secret (min 32 chars) |
| `CORS_ORIGINS` | ✗ | localhost:3000,5173... | Comma-separated CORS origins |
| `BACKEND_URL` | ✗ | http://localhost:8000 | Backend URL (for OnlyOffice callbacks) |
| `MAX_FILE_SIZE_MB` | ✗ | 10 | Max upload file size |
| `ENABLE_SEMANTIC_MATCHING` | ✗ | false | Enable semantic keyword matching |
| `ENABLE_CORPUS_KEYWORDS` | ✗ | true | Enable corpus-based keywords |
| `ENABLE_CORPUS_SYNONYMS` | ✗ | false | Enable synonym expansion |
| `ENABLE_ROLE_MAPPINGS` | ✗ | false | Enable role mapping suggestions |
| `ENABLE_ML_SUGGESTIONS` | ✗ | false | Enable ML suggestions |
| `ENVIRONMENT` | ✗ | production | Environment mode (production/development) |

### Frontend (.env)
<!-- AUTO-GENERATED -->

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `VITE_API_URL` | ✗ | http://localhost:8000 | Backend API URL |

## Deployment

### Backend Deployment (Render)
1. Set all required environment variables in Render dashboard
2. Database: Use Render PostgreSQL or Supabase
3. Ensure `ENVIRONMENT=production`
4. Set `CORS_ORIGINS` to your frontend domain
5. Health check: `GET /health` (should return 200)

### Frontend Deployment (Vercel)
1. Environment: Set `VITE_API_URL` to production backend URL
2. Build command: `npm run build`
3. Output directory: `dist`
4. Install command: `npm ci`

### Database (Supabase/PostgreSQL)
1. Create PostgreSQL database
2. Set connection string in backend `.env`
3. Run migrations: `alembic upgrade head`

## Security Checklist

Before committing code:

- [ ] No hardcoded secrets (API keys, passwords)
- [ ] All user inputs validated
- [ ] SQL injection prevention (use parameterized queries)
- [ ] XSS prevention (sanitize HTML output)
- [ ] CSRF protection on state-changing operations
- [ ] Authentication/authorization on protected endpoints
- [ ] Error messages don't leak sensitive information
- [ ] Rate limiting on sensitive endpoints

## Troubleshooting

### Backend Issues

**Import errors when running backend:**
```bash
# Ensure venv is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

**Port 8000 already in use:**
```bash
# Find and kill process
lsof -ti:8000 | xargs kill -9

# Or run on different port
uvicorn main:app --port 8001
```

**Database connection failed:**
```bash
# Check PostgreSQL is running
psql -U postgres -c "SELECT 1"

# Verify DATABASE_URL format
# Should be: postgresql://user:password@host:port/database
```

### Frontend Issues

**API requests failing:**
```bash
# Check backend is running on port 8000
curl http://localhost:8000/health

# Verify VITE_API_URL in .env points to backend
cat .env | grep VITE_API_URL

# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

**Port 5173 already in use:**
```bash
# Kill process or run on different port
npm run dev -- --port 5174
```

### E2E Test Issues

**Playwright browsers not installed:**
```bash
npx playwright install chromium
```

**Tests timeout:**
```bash
# Increase timeout in playwright.config.ts
# Or run with longer timeout
npx playwright test --timeout=60000
```

## Getting Help

1. Check existing [GitHub Issues](https://github.com/JoHn11117/ATS-Resume-Scorer/issues)
2. Search documentation in `docs/` directory
3. Review code comments and type hints
4. Ask in [Discussions](https://github.com/JoHn11117/ATS-Resume-Scorer/discussions)

## Code Review Process

1. Create a feature branch: `git checkout -b feature/your-feature`
2. Implement changes with tests
3. Run: `npm run lint`, `npm run test`, `npm run test:e2e`
4. Commit with descriptive message
5. Push and create pull request
6. Address review feedback
7. Merge when approved

---

**Last Updated**: March 2026
**Maintainers**: See GitHub repository for contact info
