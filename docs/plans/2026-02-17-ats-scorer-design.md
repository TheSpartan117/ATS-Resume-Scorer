# ATS Resume Scorer - Design Document

**Date:** 2026-02-17
**Status:** Approved
**Version:** 1.0

## Executive Summary

An AI-powered resume scoring platform that helps job seekers optimize their resumes for Applicant Tracking Systems (ATS). Users upload their resume (PDF/DOCX), receive a comprehensive score (0-100), edit their resume in a rich text editor, and re-score to see improvements in real-time.

### Key Features

- **Unlimited free scoring** (ad-supported)
- **Rich text editor** for in-platform resume editing
- **Comprehensive scoring** across 6 categories with 50+ rules
- **Real-time feedback** on ATS compatibility
- **Optional accounts** to save work
- **Premium tier** for ad-free experience

### Business Model

- **Free tier**: Unlimited scoring with skippable ads (after first free score)
- **Premium tier**: Ad-free experience ($9-19/month, to be determined)
- **Target market**: All job seekers (entry to senior level, all industries)

### Competitive Advantage

Better than Resume Worded by offering:
1. More comprehensive scoring (50+ criteria)
2. Truly unlimited re-scoring (not limited like competitors)
3. Better editing experience (rich text editor)
4. Free forever with ads (vs restrictive paywalls)
5. Industry-specific analysis

---

## 1. High-Level Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                         FRONTEND                             │
│  React App (Vercel/Netlify)                                 │
│                                                               │
│  ┌──────────────┐  ┌─────────────┐  ┌──────────────┐       │
│  │ Upload Page  │  │ Editor Page │  │ Results Page │       │
│  │              │  │             │  │              │       │
│  │ - File drop  │  │ - Rich text │  │ - Score card │       │
│  │ - Job desc   │  │ - TipTap    │  │ - Issues     │       │
│  │              │  │ - Sections  │  │ - Ad space   │       │
│  └──────────────┘  └─────────────┘  └──────────────┘       │
└─────────────────────────────────────────────────────────────┘
                            │ HTTP/REST
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                       BACKEND API                            │
│  FastAPI (Render.com)                                        │
│                                                               │
│  ┌─────────────────┐  ┌──────────────────┐                 │
│  │ Upload Service  │  │  Scoring Engine  │                 │
│  │ - Parse PDF     │  │  - 50+ rules     │                 │
│  │ - Parse DOCX    │  │  - Calculate     │                 │
│  │ - Extract data  │  │  - Suggestions   │                 │
│  └─────────────────┘  └──────────────────┘                 │
│                                                               │
│  ┌─────────────────┐  ┌──────────────────┐                 │
│  │  User Service   │  │   Ad Tracking    │                 │
│  │ - Auth          │  │ - Action count   │                 │
│  │ - Save resumes  │  │ - Show ad flag   │                 │
│  └─────────────────┘  └──────────────────┘                 │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                       DATABASE                               │
│  PostgreSQL (Render.com)                                     │
│                                                               │
│  Tables: users, resumes, scores, ad_views                   │
└─────────────────────────────────────────────────────────────┘
```

### Technology Stack

| Layer | Technology | Why |
|-------|------------|-----|
| Frontend | React 18 + TypeScript | Component architecture, type safety |
| UI Library | Tailwind CSS | Fast styling, consistent design |
| Editor | TipTap | Best React rich text editor |
| Backend | FastAPI | Fast, modern Python, auto docs |
| Parsing | python-docx, PyMuPDF | Best Python resume parsers |
| NLP | spaCy | Action verbs, keyword extraction |
| Database | PostgreSQL | Relational data, robust |
| Auth | JWT + bcrypt | Stateless, secure |
| Hosting | Vercel (frontend) + Render (backend) | Free tiers, auto-deploy |
| Ads | Google AdSense | Standard, easy integration |

### Key Design Decisions

1. **Monorepo structure**: `/frontend`, `/backend`, `/docs` in one repo
2. **Rule-based scoring**: No AI costs, full control, fast (add AI later)
3. **Stateless API**: Backend doesn't hold session state
4. **Frontend-driven flow**: React manages user journey
5. **Optional persistence**: Works without account, saves if logged in
6. **Manual re-scoring**: Users click button (not real-time) to control costs

---

## 2. Data Models

### Resume Structure (Parsed from Upload)

```typescript
interface ResumeData {
  id: string
  fileName: string
  uploadedAt: Date

  // Extracted sections
  contact: {
    name: string
    email: string
    phone: string
    location: string
    linkedin?: string
    website?: string
  }

  summary?: string

  experience: Array<{
    title: string
    company: string
    duration: string
    bullets: string[]
  }>

  education: Array<{
    degree: string
    school: string
    year: string
  }>

  skills: string[]

  certifications?: Array<{
    name: string
    issuer: string
    year: string
  }>

  // Metadata for scoring
  metadata: {
    pageCount: number
    wordCount: number
    hasPhoto: boolean
    fileFormat: 'pdf' | 'docx'
  }
}
```

### Score Result

```typescript
interface ScoreResult {
  overallScore: number  // 0-100

  categoryScores: {
    contactInfo: number       // /10
    formatting: number        // /20
    keywords: number          // /15
    contentQuality: number    // /25
    length: number            // /10
    industrySpecific: number  // /20
  }

  issues: Array<{
    category: string
    severity: 'critical' | 'warning' | 'suggestion'
    message: string
    location?: string  // Which section
  }>

  strengths: string[]  // What they did well

  metadata: {
    scoredAt: Date
    jobDescription?: string
    targetRole?: string
    targetLevel?: string
  }
}
```

### Database Models

```python
class User(Base):
    id: UUID
    email: str
    password_hash: str
    created_at: datetime
    is_premium: bool
    resumes: List[Resume]

class Resume(Base):
    id: UUID
    user_id: UUID  # nullable (for guest users)
    file_name: str
    resume_data: JSON
    latest_score: JSON
    created_at: datetime
    updated_at: datetime

class AdView(Base):
    id: UUID
    user_id: UUID  # nullable
    session_id: str  # for non-logged users
    action_count: int
    viewed_at: datetime
    skipped: bool
```

---

## 3. User Flows

### Flow 1: First-Time Guest User

1. **Landing** → User sees upload zone
2. **Upload** → Drop PDF/DOCX file
3. **Optional context** → Paste job description OR select role/level
4. **Parse & Score** (FREE) → Backend extracts data and scores
5. **View results** → See score + issues + category breakdown
6. **Edit resume** → Click "Edit Resume" → TipTap editor loads
7. **Make changes** → Edit text, add bullets, fix issues
8. **Re-score** (AD SHOWN) → Click "Re-calculate Score" → Watch skippable ad → New score
9. **Iterate** → Edit → Ad → Re-score → Edit → Ad → Re-score
10. **Optional signup** → "Save My Work" → Create account

### Flow 2: Returning User (With Account)

1. **Login** → Dashboard with saved resumes
2. **Load resume** → Click to edit
3. **Edit & Re-score** → Same flow, ads still shown
4. **Upgrade** → "Go Premium" → No more ads

### Flow 3: Premium User

1. **Login** → Dashboard
2. **Upload/Edit** → Same experience
3. **NO ADS** → Unlimited re-scores without interruption

---

## 4. Scoring Algorithm (Core Engine)

### Overall Score Breakdown (100 points)

- **Contact Information**: 10 points
- **Formatting & Structure**: 20 points
- **Keyword Optimization**: 15 points
- **Content Quality**: 25 points
- **Length & Density**: 10 points
- **Industry-Specific**: 20 points

### Category 1: Contact Information (10 pts)

**Rules:**
- Name present: 2 pts
- Valid email: 2 pts
- Phone number: 2 pts
- Location: 2 pts
- LinkedIn/Portfolio: 2 pts

**Issues flagged:**
- Missing critical contact info
- Invalid email format
- No professional links

### Category 2: Formatting & Structure (20 pts)

**Rules:**
- Page count (1-2 pages ideal): 4 pts
- No photo (ATS can't parse): 2 pts
- Has required sections (experience, education, skills): 6 pts (2 each)
- Consistent formatting: 4 pts
- ATS-friendly format (DOCX > PDF): 2 pts
- No headers/footers/tables: 2 pts

**Issues flagged:**
- Too long (>2 pages) or too short (<1 page)
- Photo detected
- Missing required sections
- Inconsistent date formats or bullet styles
- Complex formatting (tables, columns)

### Category 3: Keyword Optimization (15 pts)

**Rules:**
- If JD provided: Match resume keywords to JD (0-100% = 0-15 pts)
- If role selected: Match to expected role keywords
- If neither: Default 10 pts, suggest adding JD

**Issues flagged:**
- Missing key terms from job description
- Low keyword match for target role
- Generic keywords without specifics

### Category 4: Content Quality (25 pts)

**Rules:**
- Action verbs (led, managed, developed): 5 pts
- Quantified achievements (numbers, %, $): 8 pts
- Low buzzword count (synergy, ninja, rockstar): 5 pts
- No excessive repetition: 4 pts
- Optimal bullet length (50-150 chars): 3 pts

**Issues flagged:**
- Bullets don't start with action verbs
- No measurable results
- Too many buzzwords
- Repeated phrases
- Bullets too short or too long

### Category 5: Length & Density (10 pts)

**Rules:**
- 1 page: 400-600 words (5 pts)
- 2 pages: 600-900 words (5 pts)
- Good white space (40-70% density): 5 pts

**Issues flagged:**
- Too brief or too wordy
- Too dense (needs white space)

### Category 6: Industry-Specific (20 pts)

**Tech roles:**
- Technical skills section: 5 pts
- GitHub/portfolio link: 5 pts
- Tech keywords present: 10 pts

**Sales/Marketing roles:**
- Metrics-heavy (revenue, deals, growth): 10 pts
- Client/relationship keywords: 10 pts

**Seniority adjustments:**
- Entry level: More forgiving on experience length
- Senior: Expect leadership keywords (led, managed team, mentored)

---

## 5. API Endpoints

### Public Endpoints

```python
POST   /api/upload              # Upload resume, get initial score
POST   /api/score               # Re-score with updated content
GET    /api/health              # Health check
```

### Authentication

```python
POST   /api/signup              # Create account
POST   /api/login               # Login (returns JWT)
POST   /api/logout              # Logout
GET    /api/me                  # Get current user
```

### Protected Endpoints (Requires JWT)

```python
GET    /api/resumes             # List user's resumes
GET    /api/resume/:id          # Get saved resume
POST   /api/resumes             # Save new resume
PUT    /api/resumes/:id         # Update resume
DELETE /api/resumes/:id         # Delete resume
```

### Ad Tracking

```python
POST   /api/ad-view             # Track ad impression
GET    /api/should-show-ad      # Check if ad should show
```

---

## 6. Error Handling

### File Upload Errors

- **Invalid file type**: HTTP 400 "Please upload PDF or DOCX only"
- **File too large** (>10MB): HTTP 400 "File too large. Maximum 10MB"
- **Corrupted file**: HTTP 400 "Unable to read file. May be corrupted or password-protected"
- **Empty resume**: HTTP 400 "Resume appears empty or unreadable"
- **Scanned PDF**: HTTP 400 "Scanned PDFs not supported. Upload text-based resume"
- **Password-protected**: HTTP 400 "Password-protected files not supported"

### Scoring Edge Cases

- Missing sections: Score 0 for that category, add generic warning
- Undefined job role: Use generic tech keywords
- Extreme lengths (>2000 or <50 words): Return critical error
- Non-English: HTTP 400 "English resumes only for now"

### Network & Timeout

- API timeout: 30 seconds
- Retry failed requests: 2 retries with exponential backoff
- Database connection failure: HTTP 503 "Service temporarily unavailable"

### Data Loss Prevention

- Auto-save to localStorage every 2 seconds
- Warn before closing tab with unsaved changes
- Restore draft on page load

### Rate Limiting

```python
/api/upload:  10/minute per IP
/api/login:   5/minute per IP
/api/score:   30/minute per IP
```

### Graceful Degradation

- Database down: Allow guest upload/score (no save)
- AdSense blocked: Skip ads, allow usage
- spaCy unavailable: Fall back to regex matching
- Parser fails: Try alternative parser

---

## 7. Testing Strategy

### Unit Tests (Backend)

- Test each scoring function individually
- Test resume parsing (PDF, DOCX)
- Test keyword matching
- Test content analysis
- **Coverage goal: 80%+**

### Integration Tests (API)

- Test full upload → score flow
- Test re-score flow
- Test auth (signup, login, protected routes)
- Test edge cases (invalid files, timeouts)

### Frontend Tests (React Testing Library)

- Test component rendering
- Test file upload validation
- Test score display
- Test editor interactions

### E2E Tests (Playwright)

- Complete guest user flow
- User signup and save flow
- Premium user (no ads) flow
- Multiple browsers (Chrome, Firefox, Safari)

### Performance Targets

- Parse + Score: < 2 seconds (p95)
- Re-score: < 500ms (p95)
- API response: < 100ms (median)
- Support 50 concurrent users

### Manual Testing

- Test with 10 real resumes
- Compare scores with Resume Worded
- Test on mobile devices
- Test with ad blockers

---

## 8. Deployment

### Hosting

- **Frontend**: Vercel (free tier, auto-deploy)
- **Backend**: Render (free tier → $7/month)
- **Database**: Render PostgreSQL (free tier → $7/month)
- **Total cost**: $0-14/month

### CI/CD

- GitHub Actions for automated testing
- Auto-deploy on push to main branch
- Separate staging environment

### Environment Variables

**Frontend:**
```bash
VITE_API_URL=https://ats-api.onrender.com
VITE_ADSENSE_CLIENT_ID=ca-pub-xxxxx
```

**Backend:**
```bash
DATABASE_URL=postgresql://...
JWT_SECRET_KEY=...
CORS_ORIGINS=https://ats-scorer.vercel.app
MAX_FILE_SIZE_MB=10
ENVIRONMENT=production
```

### Monitoring

- Logging: All API calls, errors, scoring events
- Error tracking: Sentry (optional)
- Performance: Monitor response times
- Database: Monitor connection pool, query times

---

## 9. Security

### Authentication

- JWT tokens with 7-day expiration
- Bcrypt password hashing
- HTTP-only cookies (future enhancement)

### Input Validation

- Pydantic models for all inputs
- File type validation (extension + magic bytes)
- Filename sanitization (prevent path traversal)
- SQL injection prevention (SQLAlchemy ORM)

### Rate Limiting

- Prevent brute force attacks
- Prevent abuse of free tier
- slowapi library for rate limiting

### CORS

- Strict origin whitelist in production
- Localhost allowed in development

### Secure Headers

- X-Content-Type-Options: nosniff
- X-Frame-Options: DENY
- X-XSS-Protection: 1; mode=block
- Strict-Transport-Security

### HTTPS Only

- Force HTTPS in production
- Redirect HTTP → HTTPS

### Data Privacy

- Don't log sensitive data (emails, passwords)
- Hash all passwords
- Option to delete account + all data

---

## 10. Future Enhancements

### Phase 2 (Months 2-3)

- AI-powered content suggestions (GPT-4 rewrites)
- 5-10 ATS-friendly resume templates
- LinkedIn profile import
- Export to multiple formats
- Cover letter generator

### Phase 3 (Months 4-6)

- Job description matcher (paste JD, get match %)
- Industry-specific templates
- Resume version history
- A/B testing (compare two versions)
- Browser extension

### Phase 4 (Months 6-12)

- Mobile app (React Native)
- Team/recruiter accounts (B2B)
- API for third-party integrations
- White-label solution
- Multi-language support

---

## Success Metrics

### Quality Metrics

- User satisfaction: >80% rate conversion as "accurate"
- Score consistency: ±5 points on same resume
- False positive rate: <10% (flagging issues that aren't real)

### Performance Metrics

- Average conversion time: <3 seconds
- API uptime: >99.5%
- Page load time: <2 seconds
- Mobile performance score: >90

### Business Metrics

- User retention: >40% return within 7 days
- Conversion to premium: 2-5% of active users
- Ad revenue: $2-5 CPM (cost per thousand impressions)
- User growth: 20% month-over-month

---

## Appendix: Technical References

**Parsing Libraries:**
- python-docx: https://python-docx.readthedocs.io/
- PyMuPDF: https://pymupdf.readthedocs.io/
- pdfplumber: https://github.com/jsvine/pdfplumber

**NLP:**
- spaCy: https://spacy.io/
- NLTK: https://www.nltk.org/

**Frontend:**
- React: https://react.dev/
- TipTap: https://tiptap.dev/
- Tailwind CSS: https://tailwindcss.com/

**Backend:**
- FastAPI: https://fastapi.tiangolo.com/
- SQLAlchemy: https://www.sqlalchemy.org/
- Pydantic: https://docs.pydantic.dev/

**Hosting:**
- Vercel: https://vercel.com/docs
- Render: https://render.com/docs

---

## Design Approval

**Status:** ✅ Approved
**Date:** 2026-02-17
**Next Steps:** Create implementation plan

---

**Document Version**: 1.0
**Last Updated**: 2026-02-17
**Author**: Claude Code Assistant
**Owner**: Sabuj Mondal
