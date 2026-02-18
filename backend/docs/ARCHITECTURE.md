# Architecture Documentation

## System Overview

The ATS Resume Scorer is built as a modular FastAPI application with distinct layers for parsing, validation, scoring, and presentation. The system supports dual-mode scoring for different use cases.

```
┌─────────────────────────────────────────────────────────────┐
│                      FastAPI Application                     │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      API Layer (Routes)                      │
│  /upload  /score  /resumes  /export  /roles  /auth         │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     Service Layer                            │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │   Parser    │  │   Scorer    │  │  Validator  │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │  Keywords   │  │  Taxonomy   │  │   Export    │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     Data Layer                               │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │ PostgreSQL  │  │ JSON Data   │  │   Cache     │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
└─────────────────────────────────────────────────────────────┘
```

---

## Core Components

### 1. Parser (`services/parser.py`)

**Purpose**: Extract structured data from PDF/DOCX resumes.

**Key Features:**
- Multi-format support (PDF, DOCX)
- Section detection (Contact, Experience, Education, Skills, Certifications)
- Metadata extraction (page count, word count, file format)
- Date parsing with multiple format support

**Data Structure:**
```python
class ResumeData:
    fileName: str
    contact: Dict[str, Optional[str]]  # name, email, phone, location, linkedin
    experience: List[Dict]  # title, company, startDate, endDate, description
    education: List[Dict]  # degree, institution, graduationDate, description
    skills: List[str]
    certifications: List[Dict]  # name, issuer, date
    metadata: Dict  # pageCount, wordCount, fileFormat, hasPhoto
```

**Dependencies:**
- PyMuPDF (PDF parsing)
- python-docx (DOCX parsing)
- pypdf, pdfplumber (fallback PDF parsing)

---

### 2. RedFlagsValidator (`services/red_flags_validator.py`)

**Purpose**: Comprehensive resume validation against 44 parameters.

**All 44 Parameters:**

#### Employment History (P1-P6)
1. **Employment Gap Detection**: Flags gaps ≥9 months
2. **Date Validation**: Checks for date errors, unparseable dates, future dates
3. **Date Format Consistency**: Ensures uniform date formatting
4. **Job Hopping**: Detects multiple tenures <1 year
5. **Experience Level Alignment**: Validates years vs. claimed level
6. **Missing Dates**: Flags jobs without start/end dates

#### Content Depth (P7-P9)
7. **Achievement Depth**: Detects vague phrases ("responsible for", "worked on")
8. **Bullet Point Length**: Optimal range 50-150 characters
9. **Bullet Structure**: Checks for complete thoughts, strong action verbs

#### Section Completeness (P10-P13)
10. **Required Sections**: Experience, Education, Skills
11. **Section Ordering**: Experience before Education (for experienced candidates)
12. **Recency Check**: Most recent role within 2 years
13. **Summary/Objective**: Suggests adding professional summary

#### Professional Standards (P14-P17)
14. **Email Professionalism**: Checks format, provider, characters
15. **LinkedIn URL**: Validates format (linkedin.com/in/username)
16. **Phone Format Consistency**: Same format throughout
17. **Location Format**: "City, State" or "City, Country"

#### Grammar & Language (P18-P21)
18. **Typo Detection**: Uses LanguageTool for spell checking
19. **Grammar Errors**: Sentence structure, subject-verb agreement
20. **Verb Tense Consistency**: Checked via grammar analysis
21. **Capitalization**: Proper nouns, job titles

#### Metadata Validation (P22-P27)
22. **Page Count**: Optimal 1-2 pages
23. **Word Count**: Optimal 300-800 words
24. **File Format**: PDF preferred
25. **Photo Detection**: Flags photos (not ATS-friendly)
26. **File Size**: Reasonable limits
27. **Character Count**: Completeness checks

#### Content Analysis (P28-P33)
28. **Metrics/Quantification**: Looks for numbers, percentages
29. **Action Verb Usage**: Strong verbs at bullet starts
30. **Keyword Density**: Not too sparse, not keyword-stuffed
31. **Bullet Point Count**: Adequate per role
32. **Section Balance**: Appropriate length per section
33. **Completeness**: All key fields populated

#### Advanced Checks (P34-P44)
34. **Contact Info Completeness**: All fields present
35. **Role Title Consistency**: Professional naming
36. **Company Names**: No abbreviations without context
37. **Education Details**: Degree, institution, year
38. **Skills Section**: Adequate number of skills
39. **Certification Relevance**: Recent and industry-relevant
40. **Description Quality**: Substantive content
41. **Chronological Order**: Most recent first
42. **Date Overlaps**: No impossible overlaps
43. **Location Consistency**: Format matches throughout
44. **Professional Tone**: Appropriate language

**Issue Severity Levels:**
- **Critical**: Major red flags (missing sections, date errors)
- **Warning**: Moderate issues (gaps, job hopping, vague phrases)
- **Suggestion**: Minor improvements (LinkedIn, summary)

**Methods:**
```python
validate_resume(resume, role, level) -> Dict
validate_employment_history(resume) -> List[Dict]
validate_experience_level(resume, level) -> List[Dict]
validate_content_depth(resume) -> List[Dict]
validate_section_completeness(resume) -> List[Dict]
validate_professional_standards(resume) -> List[Dict]
validate_grammar(resume) -> List[Dict]
validate_metadata(resume) -> List[Dict]
validate_content_analysis(resume) -> List[Dict]
```

**Grammar Checking:**
- Uses LanguageTool Python library
- Caches results by text hash for performance
- Limits to 10 issues per category to avoid spam
- Falls back gracefully if LanguageTool unavailable

---

### 3. KeywordMatcher (`services/keyword_matcher.py`)

**Purpose**: Match keywords with synonym support and fuzzy matching.

**Key Features:**
- **O(1) Lookup**: Hash set-based keyword matching
- **Synonym Support**: Expands keywords with variations (e.g., "JS" → "JavaScript")
- **Fuzzy Matching**: 80% threshold for typo tolerance
- **Bigram Support**: Matches multi-word terms ("machine learning")

**Synonym Database:**
Located at `data/synonyms/skill_synonyms.json`:
```json
{
  "javascript": ["js", "ecmascript", "es6"],
  "python": ["py"],
  "react": ["reactjs", "react.js"],
  "node": ["nodejs", "node.js"]
}
```

**Methods:**
```python
match_keywords(resume_text, keywords) -> Dict
match_role_keywords(resume_text, role, level) -> Dict
match_job_description(resume_text, jd) -> Dict
```

**Performance:**
- Text normalization: lowercase, remove special chars
- Tokenization: words + bigrams
- Synonym expansion: reverse lookup map
- Match complexity: O(n * m) where n=keywords, m=resume tokens

---

### 4. AdaptiveScorer (`services/scorer_v2.py`)

**Purpose**: Main orchestrator for dual-mode scoring.

**Architecture:**
```
AdaptiveScorer
  ├── score() - Entry point with mode detection
  ├── _score_ats_simulation() - Mode A (70/20/10)
  └── _score_quality_coach() - Mode B (25/30/25/20)
```

**Mode A: ATS Simulation (70/20/10)**
```python
def _score_ats_simulation(resume_data, role_data, job_description):
    # 1. Keyword Match (70 points)
    #    - Required keywords: 50 points
    #    - Preferred keywords: 20 points
    #    - Auto-reject if required < 60%

    # 2. Format Check (20 points)
    #    - Section presence
    #    - Contact info

    # 3. Structure (10 points)
    #    - Experience entries
    #    - Education entries
    #    - Skills count
```

**Mode B: Quality Coach (25/30/25/20)**
```python
def _score_quality_coach(resume_data, role_data):
    # 1. Role Keywords (25 points) - Generous scoring
    #    - 60%+ match = 25 pts
    #    - 50%+ match = 22 pts
    #    - 40%+ match = 18 pts

    # 2. Content Quality (30 points)
    #    - Metrics: 15 pts
    #    - Bullets: 10 pts
    #    - Verbs: 5 pts

    # 3. Format (25 points)
    #    - Same as Mode A, scaled to 25

    # 4. Professional Polish (20 points)
    #    - Word count: 10 pts
    #    - Page count: 5 pts
    #    - Contact: 5 pts
```

**Scoring Methods:**
```python
_score_ats_keywords() -> Dict
_score_role_keywords() -> Dict
_score_content_quality() -> Dict
_score_professional_polish() -> Dict
_score_format() -> Dict
_score_structure() -> Dict
```

**Issue Conversion:**
- Converts score percentages to severity levels
- 80%+ = info
- 60-80% = suggestion
- 40-60% = warning
- <40% = critical

---

### 5. ATSScorer (`services/scorer_ats.py`)

**Purpose**: Alternative ATS-focused scorer (legacy, being phased out).

**Scoring Breakdown (100 points):**
- Keywords: 35 points (strict thresholds)
- Red Flags: 20 points (from validator)
- Experience: 20 points (years, relevance, recency)
- Formatting: 20 points (ATS-friendly)
- Contact Info: 5 points

**Integration:**
- Uses KeywordMatcher for keyword scoring
- Uses RedFlagsValidator for red flag detection
- More modular than AdaptiveScorer

---

### 6. RoleTaxonomy (`services/role_taxonomy.py`)

**Purpose**: Role-specific scoring criteria and keywords.

**Structure:**
```python
{
  "software_engineer": {
    "entry": {
      "typical_keywords": [...],
      "action_verbs": [...],
      "metrics_expected": 3
    },
    "mid": {...},
    "senior": {...}
  },
  "product_manager": {...},
  "data_scientist": {...}
}
```

**Experience Levels:**
- Entry: 0-3 years
- Mid: 2-6 years
- Senior: 5-12 years
- Lead: 8-15 years
- Executive: 12+ years

**Role-Specific Data:**
- Typical keywords (technical skills, tools)
- Action verbs (relevant to role)
- Expected metrics count
- Industry context

---

### 7. KeywordExtractor (`services/keyword_extractor.py`)

**Purpose**: Extract keywords from job descriptions.

**Methods:**
```python
extract_keywords_from_jd(jd_text) -> Dict
  # Returns: {
  #   "required": [...],
  #   "preferred": [...]
  # }

match_with_synonyms(keyword, text) -> bool
  # Checks if keyword (or synonym) exists in text
```

**Extraction Logic:**
1. Parse job description sections
2. Identify "required" vs "preferred" keywords
3. Filter out stopwords
4. Return categorized keywords

---

## Data Flow

### Upload Flow
```
1. Client uploads resume file
   ↓
2. API validates file (size, format)
   ↓
3. Parser extracts text and structure
   ↓
4. Parser creates ResumeData object
   ↓
5. Scorer determines mode (job_description present?)
   ↓
6. Scorer runs appropriate scoring method
   ↓
7. Validator runs all 44 parameter checks
   ↓
8. Results aggregated and returned
   ↓
9. Resume saved to database
```

### Scoring Flow (Editor)
```
1. Client sends updated resume data
   ↓
2. API receives ResumeData via /score endpoint
   ↓
3. AdaptiveScorer.score() called
   ↓
4. Mode detected (auto or explicit)
   ↓
5. Appropriate scoring method called
   ↓
6. Keywords matched (with synonyms)
   ↓
7. Format and structure checked
   ↓
8. Issues categorized by severity
   ↓
9. Results returned (no database save)
```

### Keyword Matching Flow
```
1. Resume text extracted
   ↓
2. Text normalized (lowercase, no special chars)
   ↓
3. Text tokenized (words + bigrams)
   ↓
4. Keywords expanded with synonyms
   ↓
5. Exact match attempted (O(1) lookup)
   ↓
6. If no match, fuzzy match attempted
   ↓
7. Match percentage calculated
   ↓
8. Results returned with matched/missing lists
```

---

## Caching Strategy

### 1. Grammar Cache
**Location**: In-memory (RedFlagsValidator)
**Key**: MD5 hash of text
**TTL**: Session-based
**Purpose**: Avoid re-checking same text with LanguageTool

```python
self._grammar_cache = {}  # {text_hash: matches}
```

### 2. Synonym Lookup Cache
**Location**: In-memory (KeywordMatcher)
**Key**: Synonym variation
**TTL**: Persistent (loaded at startup)
**Purpose**: O(1) reverse lookup for synonyms

```python
self.reverse_synonyms = {}  # {variation: primary}
```

### 3. Role Data Cache
**Location**: In-memory (RoleTaxonomy)
**TTL**: Persistent (loaded at startup)
**Purpose**: Fast role criteria lookup

### 4. Future: Redis Cache
**Planned for production:**
- Parsed resume data (TTL: 1 hour)
- Scoring results (TTL: 30 minutes)
- Job description keywords (TTL: 1 day)

---

## Database Schema

### Users Table
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW()
);
```

### Resumes Table
```sql
CREATE TABLE resumes (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    file_name VARCHAR(255) NOT NULL,
    file_path VARCHAR(512),
    parsed_data JSONB,
    score_data JSONB,
    role VARCHAR(100),
    level VARCHAR(50),
    uploaded_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### Ad Views Table (Analytics)
```sql
CREATE TABLE ad_views (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    ad_id VARCHAR(100),
    viewed_at TIMESTAMP DEFAULT NOW()
);
```

---

## External Dependencies

### Required Services
1. **PostgreSQL**: Database for user data and resumes
2. **LanguageTool**: Grammar and spell checking
   - Optional but recommended
   - Graceful degradation if unavailable
   - Can run as standalone service or Java library

### Python Libraries
- **FastAPI**: Web framework
- **SQLAlchemy**: ORM
- **PyMuPDF**: PDF parsing
- **python-docx**: DOCX parsing
- **language-tool-python**: Grammar checking
- **fuzzywuzzy**: Fuzzy string matching
- **spacy**: NLP (future use)

---

## Configuration

### Environment Variables
```bash
# Database
DATABASE_URL=postgresql://user:pass@localhost/ats_db

# JWT
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
ENVIRONMENT=development

# File Upload
MAX_FILE_SIZE_MB=5
ALLOWED_EXTENSIONS=pdf,docx

# LanguageTool (optional)
LANGUAGETOOL_ENABLED=true
LANGUAGETOOL_URL=http://localhost:8081  # If using remote server
```

---

## Performance Considerations

### Parsing Performance
- **PDF**: ~500ms for 2-page resume
- **DOCX**: ~300ms for 2-page resume
- **Optimization**: Consider async parsing for batch uploads

### Scoring Performance
- **Mode A (ATS)**: ~200ms (keyword-heavy)
- **Mode B (Quality)**: ~300ms (more checks)
- **Bottleneck**: Grammar checking (500ms per section)

### Database Performance
- **Index on user_id, uploaded_at**: Fast resume retrieval
- **JSONB for parsed_data**: Flexible schema, fast queries
- **Connection pooling**: Max 20 connections

### Scaling Strategy
1. **Horizontal**: Multiple API instances behind load balancer
2. **Vertical**: Increase worker processes (gunicorn/uvicorn)
3. **Caching**: Redis for frequently accessed data
4. **Async**: Background tasks for heavy operations (Celery)

---

## Security

### Authentication
- JWT tokens with 30-minute expiry
- Password hashing with bcrypt
- Rate limiting on auth endpoints

### File Upload Security
- File type validation (magic number checking)
- File size limits (5MB default)
- Sanitized filenames
- Virus scanning (planned)

### Database Security
- Parameterized queries (SQLAlchemy ORM)
- Row-level security (users can only access their resumes)
- Connection encryption (SSL)

---

## Testing Strategy

### Unit Tests
- Parser: Test each section extraction
- Validator: Test all 44 parameters individually
- KeywordMatcher: Test synonym expansion, fuzzy matching
- Scorers: Test scoring logic for each category

### Integration Tests
- Upload flow: File → Parse → Score → Save
- Score flow: Data → Mode detection → Scoring → Response
- Auth flow: Register → Login → Token validation

### Test Data
- Sample resumes (PDF, DOCX)
- Sample job descriptions
- Edge cases (gaps, errors, missing sections)

---

## Monitoring & Observability

### Logging
- Request/response logging
- Error tracking with stack traces
- Performance metrics (parsing time, scoring time)

### Metrics (Planned)
- Upload success rate
- Average scoring time
- Error rate by endpoint
- User activity

### Health Checks
- `/health`: API status
- Database connectivity check
- External service checks (LanguageTool)

---

## Future Enhancements

1. **AI-Powered Suggestions**: Use LLM for content improvement
2. **Real-time Collaboration**: Multiple users editing same resume
3. **Template Library**: Pre-built ATS-friendly templates
4. **Cover Letter Analysis**: Extend to cover letters
5. **Interview Prep**: Q&A based on resume content
6. **Job Matching**: Recommend jobs based on resume
7. **Skill Gap Analysis**: Compare resume to role requirements
8. **Batch Processing**: Upload multiple resumes at once
9. **Advanced Analytics**: Career trajectory insights
10. **Mobile App**: Native iOS/Android apps
