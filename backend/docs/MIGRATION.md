# Migration Guide: v1 to v2

## Overview

Version 2 introduces a complete redesign of the scoring system with dual-mode scoring, comprehensive validation, and transparent keyword matching. This guide helps you migrate from v1 to v2.

---

## Breaking Changes

### 1. Scoring System Redesign

**v1 (Single Mode)**
```json
{
  "score": 78.5,
  "breakdown": {
    "keywords": 35,
    "format": 15,
    "experience": 20,
    "education": 10
  }
}
```

**v2 (Dual Mode)**
```json
{
  "overallScore": 78.5,
  "mode": "ats_simulation",
  "breakdown": {
    "keyword_match": {
      "score": 52.0,
      "maxScore": 70,
      "issues": [...]
    },
    "format": {
      "score": 18.0,
      "maxScore": 20,
      "issues": [...]
    },
    "structure": {
      "score": 8.5,
      "maxScore": 10,
      "issues": [...]
    }
  },
  "issues": {
    "critical": [...],
    "warnings": [...],
    "suggestions": [...],
    "info": [...]
  },
  "strengths": [...],
  "keyword_details": {...},
  "auto_reject": false
}
```

**Migration Steps:**
1. Update response parsing to handle nested breakdown structure
2. Extract scores from `breakdown[category].score` instead of `breakdown[category]`
3. Handle new `mode`, `issues`, `strengths`, and `keyword_details` fields
4. Check for `auto_reject` flag to warn users

### 2. Mode Detection

**v1**: Single scoring algorithm for all resumes

**v2**: Automatic mode detection based on job description
- **With job description** → ATS Simulation mode (harsh, keyword-focused)
- **Without job description** → Quality Coach mode (balanced, quality-focused)

**Migration Steps:**
1. Decide which mode to use for your use case
2. Pass `jobDescription` parameter to trigger ATS Simulation mode
3. Omit `jobDescription` for Quality Coach mode
4. Or explicitly set `mode` parameter: `"ats_simulation"` or `"quality_coach"`

### 3. API Response Structure

**v1**: Flat score object
```json
{
  "score": 78.5,
  "breakdown": {...}
}
```

**v2**: Rich response with categorized issues
```json
{
  "overallScore": 78.5,
  "mode": "ats_simulation",
  "breakdown": {...},
  "issues": {
    "critical": [],
    "warnings": [],
    "suggestions": [],
    "info": []
  },
  "strengths": [],
  "keywordDetails": {...}
}
```

**Migration Steps:**
1. Update frontend to display `issues` by severity
2. Show `strengths` to encourage users
3. Display `keywordDetails` for transparency
4. Handle `mode` indicator in UI

---

## New Scoring System Explained

### Mode A: ATS Simulation (70/20/10)

**Purpose**: Simulate harsh ATS filtering for specific job descriptions

**When to Use**:
- User has a specific job description
- Need to optimize for keyword matching
- Want to simulate auto-reject behavior

**Scoring Breakdown**:
```
Keyword Match:  70 points (50 required + 20 preferred)
Format:         20 points
Structure:      10 points
────────────────────────
Total:         100 points
```

**Harsh Characteristics**:
- Auto-reject if required keywords < 60%
- Heavy weight on keyword matching (70%)
- Less emphasis on content quality
- Simulates real ATS behavior

**Example Use Case**:
```javascript
// User uploads resume and provides job description
const response = await fetch('/api/upload', {
  method: 'POST',
  body: formData // includes jobDescription
});

// Response will be in ATS Simulation mode
// Check auto_reject flag
if (response.auto_reject) {
  alert('Warning: This resume may be auto-rejected by ATS');
}
```

### Mode B: Quality Coach (25/30/25/20)

**Purpose**: Provide balanced feedback for general resume improvement

**When to Use**:
- User wants to improve resume generally
- No specific job description available
- Focus on content quality and professionalism

**Scoring Breakdown**:
```
Role Keywords:       25 points (generous thresholds)
Content Quality:     30 points (metrics, bullets, verbs)
Format:              25 points
Professional Polish: 20 points
────────────────────────────────
Total:              100 points
```

**Balanced Characteristics**:
- No auto-reject (coaching, not filtering)
- More weight on content quality (30%)
- Generous keyword thresholds
- Encourages best practices

**Example Use Case**:
```javascript
// User uploads resume without job description
const response = await fetch('/api/upload', {
  method: 'POST',
  body: formData // no jobDescription
});

// Response will be in Quality Coach mode
// Display CTA (call-to-action)
console.log(response.cta); // "Your resume is good. Consider minor improvements."
```

---

## All 44 Validation Parameters

v2 introduces comprehensive validation with 44 parameters across 11 categories:

### Employment History (6 parameters)
1. **P1: Employment Gap Detection** - Flags gaps ≥9 months (critical if ≥18 months)
2. **P2: Date Validation** - Checks for date errors, unparseable dates, future dates
3. **P3: Date Format Consistency** - Ensures uniform date formatting throughout
4. **P4: Job Hopping** - Detects multiple tenures <1 year (warning if 2+)
5. **P5: Experience Level Alignment** - Validates total years vs. claimed level
6. **P6: Missing Dates** - Flags jobs without start/end dates (critical)

### Content Depth (3 parameters)
7. **P7: Achievement Depth** - Detects vague phrases like "responsible for", "worked on"
8. **P8: Bullet Point Length** - Optimal 50-150 chars, critical if <30 or >200
9. **P9: Bullet Structure** - Checks for complete thoughts and strong action verbs

### Section Completeness (4 parameters)
10. **P10: Required Sections** - Experience, Education, Skills must be present
11. **P11: Section Ordering** - Experience before Education for 2+ years exp
12. **P12: Recency Check** - Most recent role should be within 2 years
13. **P13: Summary/Objective** - Suggests adding professional summary

### Professional Standards (4 parameters)
14. **P14: Email Professionalism** - Checks format, provider (no AOL/Yahoo), no numbers
15. **P15: LinkedIn URL** - Validates format (linkedin.com/in/username)
16. **P16: Phone Format Consistency** - Same format throughout resume
17. **P17: Location Format** - "City, State" or "City, Country" format

### Grammar & Language (4 parameters)
18. **P18: Typo Detection** - Uses LanguageTool for spell checking
19. **P19: Grammar Errors** - Sentence structure, subject-verb agreement
20. **P20: Verb Tense Consistency** - Past tense for old roles, present for current
21. **P21: Capitalization** - Proper nouns, job titles, company names

### Metadata Validation (6 parameters)
22. **P22: Page Count** - Optimal 1-2 pages, warning if 3+
23. **P23: Word Count** - Optimal 300-800 words
24. **P24: File Format** - PDF preferred (4 pts), DOCX acceptable (3 pts)
25. **P25: Photo Detection** - Flags photos (not ATS-friendly)
26. **P26: File Size** - Reasonable limits (5MB max)
27. **P27: Character Count** - Completeness checks

### Content Analysis (6 parameters)
28. **P28: Metrics/Quantification** - Looks for numbers (10%, 5x, $1M)
29. **P29: Action Verb Usage** - Strong verbs at bullet starts (Led, Built, Achieved)
30. **P30: Keyword Density** - Not too sparse, not keyword-stuffed
31. **P31: Bullet Point Count** - Adequate per role (3-5 bullets)
32. **P32: Section Balance** - Appropriate length per section
33. **P33: Completeness** - All key fields populated

### Advanced Checks (11 parameters)
34. **P34: Contact Info Completeness** - Name, email, phone, location, LinkedIn
35. **P35: Role Title Consistency** - Professional naming conventions
36. **P36: Company Names** - No abbreviations without context
37. **P37: Education Details** - Degree, institution, year all present
38. **P38: Skills Section** - Adequate number of skills (5+ recommended)
39. **P39: Certification Relevance** - Recent and industry-relevant certs
40. **P40: Description Quality** - Substantive content (50+ chars per bullet)
41. **P41: Chronological Order** - Most recent roles first
42. **P42: Date Overlaps** - No impossible date overlaps
43. **P43: Location Consistency** - Format matches throughout
44. **P44: Professional Tone** - Appropriate language and formatting

**Migration Impact**:
- Many more issues detected than v1
- Issues categorized by severity (critical, warning, suggestion)
- Users get more actionable feedback
- Better ATS compatibility checking

---

## Score Distribution Changes

### v1 Score Distribution
```
90-100: Excellent (rare, ~5% of resumes)
80-89:  Good (common, ~30%)
70-79:  Fair (common, ~40%)
60-69:  Poor (common, ~20%)
<60:    Critical (rare, ~5%)
```

### v2 Score Distribution (ATS Mode)
```
85-100: Excellent (rare, ~2% - harsh thresholds)
70-84:  Good (uncommon, ~15%)
55-69:  Fair (common, ~40%)
40-54:  Poor (common, ~30%)
<40:    Critical (common, ~13% - auto-reject)
```

**Why Lower Scores?**
- Simulates harsh ATS filtering
- More parameters (44 vs ~20 in v1)
- Stricter keyword matching
- Auto-reject threshold at 60% required keywords

### v2 Score Distribution (Quality Coach Mode)
```
85-100: Excellent (uncommon, ~10%)
70-84:  Good (common, ~35%)
55-69:  Fair (common, ~40%)
40-54:  Poor (uncommon, ~12%)
<40:    Critical (rare, ~3%)
```

**Why More Balanced?**
- Generous keyword thresholds
- Focus on quality over strict matching
- Coaching mindset (help improve, not reject)
- No auto-reject

**Migration Recommendation**:
- Educate users about new scoring system
- Display mode indicator prominently
- Explain that lower scores are expected in ATS mode
- Show score distribution chart for context

---

## Examples: Harsh vs Lenient Scoring

### Example 1: Keyword Mismatch

**Resume**: Software Engineer with Python, React, SQL
**Job Description**: Requires Python, React, SQL, Kubernetes, Docker, CI/CD

**v1 Score**:
```json
{
  "score": 75,
  "breakdown": {
    "keywords": 25  // Matched 3/6 = 50%
  }
}
```

**v2 ATS Simulation**:
```json
{
  "overallScore": 42,
  "mode": "ats_simulation",
  "breakdown": {
    "keyword_match": {
      "score": 25.0,
      "maxScore": 70
    }
  },
  "keyword_details": {
    "required_matched": 3,
    "required_total": 6,
    "required_match_pct": 50.0
  },
  "auto_reject": true,
  "rejection_reason": "Required keywords match < 60%"
}
```

**v2 Quality Coach**:
```json
{
  "overallScore": 68,
  "mode": "quality_coach",
  "breakdown": {
    "role_keywords": {
      "score": 18.0,
      "maxScore": 25
    }
  },
  "cta": "Your resume needs improvement. Review the feedback."
}
```

**Analysis**:
- v1: Moderate penalty (75/100)
- v2 ATS: Harsh penalty + auto-reject (42/100)
- v2 Quality: Lenient, focuses on improvement (68/100)

### Example 2: Employment Gap

**Resume**: 15-month gap between jobs (2020-2021)

**v1**: Not detected or minor deduction

**v2**:
```json
{
  "issues": {
    "critical": [
      ["critical", "Employment gap of 15 months between Company A and Company B. Consider adding explanation."]
    ]
  }
}
```

**Score Impact**:
- ATS Mode: -8 points from red flags section
- Quality Coach Mode: -5 points

### Example 3: Vague Phrases

**Resume**: "Responsible for developing features"

**v1**: No detection

**v2**:
```json
{
  "issues": {
    "warnings": [
      ["warning", "Senior Engineer at Tech Corp: Vague phrase detected 'responsible for'. Use specific achievements with metrics instead."]
    ]
  }
}
```

**Score Impact**:
- Content quality reduced by 3-5 points
- User gets actionable feedback to improve

---

## API Endpoint Changes

### Upload Endpoint

**v1**:
```
POST /api/upload
Body: multipart/form-data (file only)
Response: { score: 78.5, breakdown: {...} }
```

**v2**:
```
POST /api/upload
Body: multipart/form-data (file + optional fields)
  - file (required)
  - jobDescription (optional - triggers ATS mode)
  - role (optional - e.g., "software_engineer")
  - level (optional - e.g., "senior")

Response: {
  overallScore: 78.5,
  mode: "ats_simulation",
  breakdown: {...},
  issues: {...},
  strengths: [...],
  keyword_details: {...},
  auto_reject: false
}
```

### Score Endpoint

**v1**: Not available

**v2**: New endpoint for re-scoring edited data
```
POST /api/score
Body: application/json (complete resume data)

Response: Same as upload endpoint
```

**Use Case**: Real-time scoring in resume editor

---

## Frontend Migration Checklist

### 1. Update API Client
```javascript
// OLD
const response = await uploadResume(file);
const score = response.score;

// NEW
const response = await uploadResume(file, jobDescription, role, level);
const score = response.overallScore;
const mode = response.mode;
const autoReject = response.auto_reject;
```

### 2. Display Mode Indicator
```jsx
// Show which mode was used
<Badge color={mode === 'ats_simulation' ? 'red' : 'blue'}>
  {mode === 'ats_simulation' ? 'ATS Simulation' : 'Quality Coach'}
</Badge>
```

### 3. Handle Auto-Reject
```jsx
// Warn user about auto-reject
{autoReject && (
  <Alert severity="error">
    Warning: This resume may be auto-rejected by ATS systems.
    Required keyword match is below 60%.
  </Alert>
)}
```

### 4. Display Keyword Details
```jsx
// Show keyword transparency
<div>
  <h3>Keyword Match</h3>
  <Progress value={keywordDetails.required_match_pct} />
  <p>Required: {keywordDetails.required_matched}/{keywordDetails.required_total}</p>
  <p>Preferred: {keywordDetails.preferred_matched}/{keywordDetails.preferred_total}</p>
</div>
```

### 5. Categorize Issues
```jsx
// Display issues by severity
<div>
  <h3>Critical Issues ({issues.critical.length})</h3>
  {issues.critical.map(([severity, message]) => (
    <Alert severity="error">{message}</Alert>
  ))}

  <h3>Warnings ({issues.warnings.length})</h3>
  {issues.warnings.map(([severity, message]) => (
    <Alert severity="warning">{message}</Alert>
  ))}

  <h3>Suggestions ({issues.suggestions.length})</h3>
  {issues.suggestions.map(([severity, message]) => (
    <Alert severity="info">{message}</Alert>
  ))}
</div>
```

### 6. Show Strengths
```jsx
// Encourage users with strengths
<div>
  <h3>Strengths</h3>
  {strengths.map(strength => (
    <Chip color="success" label={strength} />
  ))}
</div>
```

### 7. Update Score Display
```jsx
// OLD
<CircularProgress value={score} />

// NEW
<CircularProgress value={overallScore} />
<Typography variant="caption">
  {mode === 'ats_simulation' ? 'ATS Simulation Mode' : 'Quality Coach Mode'}
</Typography>
```

---

## Backend Migration Steps

### 1. Update Dependencies
```bash
pip install -r requirements.txt
```

New dependencies in v2:
- `language-tool-python==2.7.1` (grammar checking)
- `fuzzywuzzy==0.18.0` (fuzzy matching)
- `python-Levenshtein==0.23.0` (faster fuzzy matching)

### 2. Update Database Schema
```sql
-- Add new columns to resumes table
ALTER TABLE resumes ADD COLUMN mode VARCHAR(50);
ALTER TABLE resumes ADD COLUMN auto_reject BOOLEAN DEFAULT FALSE;

-- Update indexes
CREATE INDEX idx_resumes_mode ON resumes(mode);
CREATE INDEX idx_resumes_auto_reject ON resumes(auto_reject);
```

### 3. Migrate Existing Scores
```python
# Script to re-score existing resumes with v2
from services.scorer_v2 import AdaptiveScorer
from models.resume import Resume

scorer = AdaptiveScorer()

for resume in Resume.query.all():
    # Re-score with v2
    result = scorer.score(
        resume_data=resume.parsed_data,
        role_id=resume.role or "software_engineer",
        level=resume.level or "mid",
        mode="quality_coach"  # Default to quality coach for existing resumes
    )

    # Update database
    resume.score_data = result
    resume.mode = "quality_coach"

db.session.commit()
```

### 4. Update API Routes
```python
# OLD
@router.post("/upload")
async def upload_resume(file: UploadFile):
    parsed = parse_resume(file)
    score = score_resume_v1(parsed)
    return {"score": score, "breakdown": breakdown}

# NEW
@router.post("/upload")
async def upload_resume(
    file: UploadFile,
    jobDescription: Optional[str] = "",
    role: Optional[str] = "software_engineer",
    level: Optional[str] = "mid"
):
    parsed = parse_resume(file)
    mode = "ats_simulation" if jobDescription else "quality_coach"
    result = scorer.score(parsed, role, level, jobDescription, mode)
    return result
```

---

## Testing Migration

### Test Cases

1. **ATS Mode with High Keyword Match**
   - Expected: Score 80+, no auto-reject
   - Verify: keyword_details shows 80%+ match

2. **ATS Mode with Low Keyword Match**
   - Expected: Score <60, auto-reject = true
   - Verify: rejection_reason present

3. **Quality Coach Mode**
   - Expected: Balanced scoring, no auto-reject
   - Verify: mode = "quality_coach", CTA present

4. **All 44 Parameters**
   - Test resume with intentional issues
   - Verify: All issue types detected and categorized

5. **Synonym Matching**
   - Resume has "JS", JD requires "JavaScript"
   - Verify: Keyword matched via synonym

6. **Grammar Checking**
   - Resume with typos/grammar errors
   - Verify: Issues detected and categorized

### Sample Test Script
```python
def test_v2_scoring():
    # Test ATS mode
    result = scorer.score(
        resume_data=sample_resume,
        role_id="software_engineer",
        level="senior",
        job_description=sample_jd,
        mode="ats_simulation"
    )

    assert result["mode"] == "ats_simulation"
    assert "keyword_details" in result
    assert "auto_reject" in result
    assert result["overallScore"] >= 0
    assert result["overallScore"] <= 100

    # Test Quality Coach mode
    result = scorer.score(
        resume_data=sample_resume,
        role_id="software_engineer",
        level="senior",
        mode="quality_coach"
    )

    assert result["mode"] == "quality_coach"
    assert "cta" in result
    assert "auto_reject" not in result
```

---

## Rollback Plan

If v2 causes issues, you can rollback:

### 1. Code Rollback
```bash
git revert <v2-commit-hash>
git push
```

### 2. Database Rollback
```sql
-- Remove v2 columns
ALTER TABLE resumes DROP COLUMN mode;
ALTER TABLE resumes DROP COLUMN auto_reject;
```

### 3. API Compatibility Layer
Keep both v1 and v2 endpoints:
```python
@router.post("/upload")  # v2
@router.post("/upload/v1")  # v1 fallback
```

---

## Support & FAQ

### Q: Will my old scores still work?
A: Yes, old scores are preserved in the database. New uploads use v2 scoring.

### Q: How do I force a specific mode?
A: Pass the `mode` parameter explicitly: `"ats_simulation"` or `"quality_coach"`

### Q: Why is my score lower in v2?
A: v2 is more comprehensive (44 parameters vs ~20 in v1) and ATS mode is intentionally harsh to simulate real ATS systems.

### Q: Can I disable grammar checking?
A: Yes, set `LANGUAGETOOL_ENABLED=false` in environment. Validation will gracefully skip grammar checks.

### Q: How do I customize scoring weights?
A: Edit `scorer_v2.py` scoring methods to adjust point allocations.

---

## Timeline

- **v2.0.0 Release**: February 19, 2026
- **Migration Period**: February - March 2026 (both v1 and v2 supported)
- **v1 Deprecation**: April 1, 2026
- **v1 Sunset**: May 1, 2026

---

## Getting Help

- **Documentation**: See API.md and ARCHITECTURE.md
- **Issues**: GitHub Issues
- **Support**: support@atsresumescorer.com
- **Community**: Discord server
