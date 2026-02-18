# Dual-Mode Scoring API Documentation

## Overview

The ATS Resume Scorer now supports **dual-mode scoring** with automatic mode detection:

1. **ATS Simulation Mode** (`ats_simulation`): Harsh keyword-heavy scoring focused on ATS compatibility (70/20/10 breakdown)
2. **Quality Coach Mode** (`quality_coach`): Balanced quality scoring focused on resume quality (25/30/25/20 breakdown)

## API Endpoints

### 1. POST `/api/score` - Re-score Resume

Re-scores resume data with updated content (used by editor).

#### Request Body

```json
{
  "fileName": "resume.pdf",
  "contact": {
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "555-1234"
  },
  "experience": [...],
  "education": [...],
  "skills": ["Python", "AWS"],
  "certifications": [],
  "metadata": {
    "pageCount": 1,
    "wordCount": 500,
    "hasPhoto": false,
    "fileFormat": "pdf"
  },
  "role": "software_engineer",
  "level": "mid",
  "jobDescription": "Python developer needed",
  "mode": "auto"  // Optional: "ats", "quality", or "auto" (default)
}
```

#### Mode Parameter

- **`"auto"`** (default): Auto-detects mode based on job description presence
  - With job description → ATS Simulation mode
  - Without job description → Quality Coach mode
- **`"ats"`** or **`"ats_simulation"`**: Force ATS Simulation mode (requires job description)
- **`"quality"`** or **`"quality_coach"`**: Force Quality Coach mode

#### Response

```json
{
  "overallScore": 75.5,
  "mode": "ats_simulation",
  "breakdown": {
    "keyword_match": {
      "score": 50.0,
      "maxScore": 70.0,
      "issues": ["Missing required keyword: Docker"]
    },
    "format": {
      "score": 18.0,
      "maxScore": 20.0,
      "issues": []
    },
    "structure": {
      "score": 7.5,
      "maxScore": 10.0,
      "issues": ["Add more experience entries"]
    }
  },
  "issues": {
    "critical": ["Missing phone number"],
    "warnings": ["Add more quantified results"],
    "suggestions": ["Consider adding LinkedIn profile"]
  },
  "issueCounts": {
    "critical": 1,
    "warnings": 1,
    "suggestions": 1
  },
  "strengths": [
    "Strong keyword match with required skills",
    "ATS-compatible format"
  ],
  "keywordDetails": {
    "required_matched": 5,
    "required_total": 8,
    "required_match_pct": 62.5,
    "preferred_matched": 3,
    "preferred_total": 5,
    "preferred_match_pct": 60.0
  },
  "autoReject": false
}
```

### 2. POST `/api/upload` - Upload Resume

Uploads and parses a resume file, returning initial score.

#### Request (multipart/form-data)

- **`file`**: PDF or DOCX file (max 10MB)
- **`role`**: Role identifier (e.g., "software_engineer")
- **`level`**: Experience level ("entry", "mid", "senior", "lead", "executive")
- **`jobDescription`**: (Optional) Job description text
- **`mode`**: (Optional) Scoring mode: "ats", "quality", or "auto" (default: "auto")

#### Response

Same structure as `/api/score` response, plus additional fields:

```json
{
  "resumeId": null,
  "fileName": "resume.pdf",
  "fileId": "uuid-string",
  "originalFileUrl": "/api/files/uuid.pdf",
  "previewPdfUrl": null,
  "editableHtml": "<html>...</html>",
  "contact": {...},
  "experience": [...],
  "education": [...],
  "skills": [...],
  "certifications": [],
  "metadata": {...},
  "score": {
    // Same as /api/score response
  },
  "formatCheck": {
    "passed": true,
    "score": 0.95,
    "checks": {...},
    "issues": []
  },
  "scoringMode": "ats_simulation",
  "role": "software_engineer",
  "level": "mid",
  "jobDescription": "...",
  "uploadedAt": "2026-02-19T10:30:00Z"
}
```

## Mode-Specific Scoring Breakdowns

### ATS Simulation Mode (`ats_simulation`)

**Total: 100 points (70/20/10)**

- **Keyword Match** (70 points)
  - Required keywords: 50 points
  - Preferred keywords: 20 points
- **Format** (20 points)
  - Has required sections
  - Contact info completeness
- **Structure** (10 points)
  - Number of experience/education entries
  - Skills count

**Response Fields:**
- `keywordDetails`: Detailed keyword matching statistics
- `autoReject`: Boolean flag if required keyword match < 60%

### Quality Coach Mode (`quality_coach`)

**Total: 100 points (25/30/25/20)**

- **Role Keywords** (25 points)
  - Generous scoring based on role-specific keywords
  - Action verbs usage
- **Content Quality** (30 points)
  - Quantified achievements
  - Bullet point format
  - Action verbs
- **Format** (25 points)
  - Section completeness
  - ATS compatibility
- **Professional Polish** (20 points)
  - Word count appropriateness
  - Page count
  - Contact info completeness

**Response Fields:**
- `keywordDetails`: Role-specific keyword matching stats

## Issue Severity Levels

Issues are categorized into four severity levels:

1. **`critical`**: Must fix (e.g., missing email, no experience)
2. **`warnings`**: Should fix (e.g., missing phone, few quantified results)
3. **`suggestions`**: Nice to have (e.g., add LinkedIn, more keywords)
4. **`info`**: Informational (e.g., PDF preferred over DOCX)

## Backward Compatibility

The API maintains full backward compatibility:

- If `mode` parameter is omitted, defaults to `"auto"`
- Auto mode behavior:
  - With `jobDescription` → ATS Simulation mode
  - Without `jobDescription` → Quality Coach mode
- All existing response fields remain unchanged
- New fields (`mode`, `issueCounts`) are added without breaking existing clients

## Frontend Integration Hints

The API response includes fields designed for frontend mode-toggle UIs:

```json
{
  "mode": "ats_simulation",  // Current scoring mode
  "issueCounts": {           // Quick summary for UI badges
    "critical": 2,
    "warnings": 5,
    "suggestions": 3
  },
  "breakdown": {             // Mode-specific category breakdown
    // ATS mode: keyword_match, format, structure
    // Quality mode: role_keywords, content_quality, format, professional_polish
  }
}
```

## Example Usage

### Example 1: Auto Mode (with JD → ATS)

```bash
curl -X POST http://localhost:8000/api/score \
  -H "Content-Type: application/json" \
  -d '{
    "fileName": "resume.pdf",
    "contact": {"name": "John", "email": "john@example.com"},
    "experience": [...],
    "skills": ["Python", "AWS"],
    "metadata": {...},
    "jobDescription": "Python developer with AWS experience",
    "role": "software_engineer",
    "level": "mid"
  }'

# Response: mode="ats_simulation"
```

### Example 2: Auto Mode (no JD → Quality)

```bash
curl -X POST http://localhost:8000/api/score \
  -H "Content-Type: application/json" \
  -d '{
    "fileName": "resume.pdf",
    "contact": {"name": "Jane", "email": "jane@example.com"},
    "experience": [...],
    "skills": ["JavaScript", "React"],
    "metadata": {...},
    "role": "software_engineer",
    "level": "mid"
  }'

# Response: mode="quality_coach"
```

### Example 3: Force Quality Mode

```bash
curl -X POST http://localhost:8000/api/score \
  -H "Content-Type: application/json" \
  -d '{
    "fileName": "resume.pdf",
    "contact": {"name": "Alice", "email": "alice@example.com"},
    "experience": [...],
    "skills": ["Python"],
    "metadata": {...},
    "jobDescription": "Python developer",
    "role": "software_engineer",
    "level": "senior",
    "mode": "quality"
  }'

# Response: mode="quality_coach" (even with JD)
```

## Testing

Run the validation script to verify dual-mode scoring:

```bash
cd backend
python validate_dual_mode_api.py
```

Run comprehensive tests:

```bash
cd backend
pytest tests/test_api_score.py -v
pytest tests/test_api_upload.py -v
```

## Migration Guide

### For Frontend Developers

1. **No breaking changes**: Existing code continues to work
2. **Add mode toggle**: Use the `mode` parameter in requests
3. **Display mode indicator**: Show current mode from response
4. **Show issue counts**: Use `issueCounts` for UI badges
5. **Handle mode-specific breakdowns**:
   - ATS mode: Show keyword matching details
   - Quality mode: Show content quality details

### For API Consumers

1. **Update request schema**: Add optional `mode` field
2. **Handle new response fields**: `mode`, `issueCounts`
3. **Update UI**: Display mode-specific information
4. **Test both modes**: Verify behavior with/without job descriptions

## Version History

- **v1.0.0** (2026-02-19): Initial dual-mode scoring API release
  - Added `mode` parameter to `/api/score` and `/api/upload`
  - Added `issueCounts` to response
  - Auto-detection based on job description presence
  - Full backward compatibility maintained
