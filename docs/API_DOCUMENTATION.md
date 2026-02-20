# API Documentation

**ATS Resume Scorer - Complete API Reference**

This document provides comprehensive documentation for all API endpoints.

---

## Table of Contents

1. [Base URL](#base-url)
2. [Authentication](#authentication)
3. [Resume Upload & Parsing](#resume-upload--parsing)
4. [Scoring Endpoints](#scoring-endpoints)
5. [ATS Analysis](#ats-analysis)
6. [Grammar & Quality](#grammar--quality)
7. [Skills Analysis](#skills-analysis)
8. [Document Operations](#document-operations)
9. [Testing & Benchmarking](#testing--benchmarking)
10. [Error Handling](#error-handling)
11. [Rate Limiting](#rate-limiting)
12. [Examples](#examples)

---

## Base URL

```
Development: http://localhost:8000
Production: https://api.atsscorer.com
```

All endpoints are prefixed with `/api/v1/`

---

## Authentication

Currently, the API is open for public use. Future versions may require API keys for rate limiting.

```http
Authorization: Bearer <api_key>  # Future implementation
```

---

## Resume Upload & Parsing

### Upload Resume

Upload a resume file for parsing and analysis.

**Endpoint:** `POST /api/v1/resumes/upload`

**Request:**
```http
POST /api/v1/resumes/upload
Content-Type: multipart/form-data

file: <resume.pdf|resume.docx>
job_description: <optional_text>
```

**Response:**
```json
{
  "resume_id": "uuid-string",
  "filename": "resume.pdf",
  "parsed_text": "John Doe\nSoftware Engineer...",
  "metadata": {
    "pages": 2,
    "word_count": 450,
    "format": "pdf"
  },
  "status": "success"
}
```

**Supported Formats:**
- PDF (.pdf)
- Microsoft Word (.docx, .doc)
- Plain text (.txt)

**File Size Limit:** 10 MB

---

### Parse Resume Text

Parse resume from raw text without file upload.

**Endpoint:** `POST /api/v1/resumes/parse`

**Request:**
```json
{
  "resume_text": "John Doe\nSoftware Engineer...",
  "format": "text"
}
```

**Response:**
```json
{
  "parsed_data": {
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "555-1234",
    "sections": {
      "experience": [...],
      "education": [...],
      "skills": [...]
    }
  },
  "status": "success"
}
```

---

## Scoring Endpoints

### Score Resume

Get comprehensive ATS score for a resume.

**Endpoint:** `POST /api/v1/score`

**Request:**
```json
{
  "resume_text": "Full resume text...",
  "job_description": "Job description text..."
}
```

**Response:**
```json
{
  "overall_score": 78,
  "confidence_interval": {
    "lower": 73,
    "upper": 83,
    "confidence_level": 0.95
  },
  "component_scores": {
    "ats_compatibility": 82,
    "keyword_match": 75,
    "quality_score": 80,
    "format_score": 85
  },
  "pass_probability": {
    "overall": 73,
    "by_platform": {
      "taleo": 65,
      "workday": 78,
      "greenhouse": 85
    }
  },
  "top_issues": [
    {
      "severity": "high",
      "category": "keywords",
      "message": "Missing 5 key skills from job description",
      "suggestion": "Add: Python, AWS, Docker, Kubernetes, CI/CD"
    },
    {
      "severity": "medium",
      "category": "quantification",
      "message": "Only 35% of bullets contain metrics",
      "suggestion": "Add numbers to 3-5 more accomplishments"
    },
    {
      "severity": "medium",
      "category": "format",
      "message": "Tables detected - may fail Taleo parsing",
      "suggestion": "Convert tables to standard bullet points"
    }
  ],
  "detailed_analysis": {
    "keyword_matches": [...],
    "missing_keywords": [...],
    "grammar_issues": [...],
    "skills_breakdown": {...}
  },
  "timestamp": "2026-02-20T10:30:00Z"
}
```

---

### Quick Score

Get fast score without detailed analysis (cached results).

**Endpoint:** `POST /api/v1/score/quick`

**Request:**
```json
{
  "resume_id": "uuid-string"
}
```

**Response:**
```json
{
  "overall_score": 78,
  "cached": true,
  "timestamp": "2026-02-20T10:30:00Z"
}
```

---

### Rescore

Rescore resume after edits.

**Endpoint:** `POST /api/v1/resumes/{resume_id}/rescore`

**Request:**
```json
{
  "updated_text": "Modified resume text..."
}
```

**Response:**
```json
{
  "new_score": 82,
  "previous_score": 78,
  "improvement": 4,
  "changes_detected": [
    "Added 3 keywords",
    "Improved quantification",
    "Fixed 2 grammar issues"
  ]
}
```

---

## ATS Analysis

### Simulate ATS Parsing

Test how different ATS platforms would parse your resume.

**Endpoint:** `POST /api/v1/ats/simulate`

**Request:**
```json
{
  "resume_text": "Resume text...",
  "platforms": ["taleo", "workday", "greenhouse"]
}
```

**Response:**
```json
{
  "results": {
    "taleo": {
      "pass_probability": 65,
      "issues": [
        "Tables detected - cannot parse",
        "Missing clear section headers"
      ],
      "recommendation": "Use simple formatting, no tables",
      "severity": "high"
    },
    "workday": {
      "pass_probability": 78,
      "issues": ["Some structure ambiguity"],
      "recommendation": "Add clearer section headers",
      "severity": "medium"
    },
    "greenhouse": {
      "pass_probability": 85,
      "issues": [],
      "recommendation": "Format looks good",
      "severity": "low"
    }
  },
  "overall_compatibility": 76,
  "recommendation": "Optimize for Taleo (most strict)"
}
```

---

### Check ATS Compatibility

Quick check for ATS-friendly formatting.

**Endpoint:** `POST /api/v1/ats/check`

**Request:**
```json
{
  "resume_text": "Resume text..."
}
```

**Response:**
```json
{
  "compatible": true,
  "warnings": [
    "Some complex formatting detected",
    "Consider simplifying tables"
  ],
  "score": 82
}
```

---

## Grammar & Quality

### Check Grammar

Get grammar and spelling analysis.

**Endpoint:** `POST /api/v1/quality/grammar`

**Request:**
```json
{
  "text": "Text to check..."
}
```

**Response:**
```json
{
  "grammar_score": 88,
  "issues": [
    {
      "type": "spelling",
      "severity": "high",
      "message": "Possible spelling mistake",
      "context": "...devloped applications...",
      "offset": 45,
      "length": 8,
      "suggestions": ["developed", "development"]
    },
    {
      "type": "grammar",
      "severity": "medium",
      "message": "Subject-verb agreement",
      "context": "...team have completed...",
      "suggestions": ["has completed"]
    }
  ],
  "total_issues": 2,
  "critical_issues": 1,
  "minor_issues": 1
}
```

---

### Analyze Quality

Get content quality analysis.

**Endpoint:** `POST /api/v1/quality/analyze`

**Request:**
```json
{
  "resume_text": "Resume text..."
}
```

**Response:**
```json
{
  "quality_score": 80,
  "metrics": {
    "action_verbs_percentage": 75,
    "quantification_percentage": 45,
    "impact_words_count": 12,
    "average_bullet_length": 15,
    "readability_score": 65
  },
  "suggestions": [
    "Add metrics to 3 more bullet points",
    "Use stronger action verbs in experience section",
    "Simplify some complex sentences"
  ]
}
```

---

## Skills Analysis

### Extract Skills

Extract and categorize skills from resume.

**Endpoint:** `POST /api/v1/skills/extract`

**Request:**
```json
{
  "resume_text": "Resume text..."
}
```

**Response:**
```json
{
  "hard_skills": [
    {
      "skill": "Python",
      "category": "programming_language",
      "confidence": 0.95,
      "occurrences": 5
    },
    {
      "skill": "AWS",
      "category": "cloud_platform",
      "confidence": 0.90,
      "occurrences": 3
    }
  ],
  "soft_skills": [
    {
      "skill": "Leadership",
      "evidence": ["Led team of 5", "Managed cross-functional projects"],
      "confidence": 0.85
    },
    {
      "skill": "Communication",
      "evidence": ["Presented to stakeholders", "Collaborated with teams"],
      "confidence": 0.80
    }
  ],
  "total_skills": 28,
  "unique_skills": 22
}
```

---

### Match Skills

Compare resume skills with job requirements.

**Endpoint:** `POST /api/v1/skills/match`

**Request:**
```json
{
  "resume_text": "Resume text...",
  "job_description": "Job description..."
}
```

**Response:**
```json
{
  "match_score": 75,
  "matched_skills": [
    {
      "skill": "Python",
      "match_type": "exact",
      "importance": "high"
    },
    {
      "skill": "Cloud Computing",
      "match_type": "semantic",
      "resume_term": "AWS",
      "job_term": "cloud platforms",
      "similarity": 0.85
    }
  ],
  "missing_skills": [
    {
      "skill": "Docker",
      "importance": "high",
      "category": "hard_skill"
    },
    {
      "skill": "Kubernetes",
      "importance": "medium",
      "category": "hard_skill"
    }
  ],
  "extra_skills": ["Photoshop", "Java"],
  "recommendations": [
    "Add Docker experience if you have it",
    "Highlight Kubernetes projects",
    "Consider removing irrelevant skills like Photoshop"
  ]
}
```

---

## Document Operations

### Convert to PDF

Convert resume to PDF format.

**Endpoint:** `POST /api/v1/documents/convert/pdf`

**Request:**
```json
{
  "resume_id": "uuid-string"
}
```

**Response:**
```json
{
  "pdf_url": "/api/v1/documents/download/uuid-string.pdf",
  "expires_at": "2026-02-20T11:30:00Z"
}
```

---

### Export to LaTeX

Export resume as LaTeX document.

**Endpoint:** `POST /api/v1/documents/export/latex`

**Request:**
```json
{
  "resume_id": "uuid-string",
  "template": "modern"
}
```

**Response:**
```json
{
  "latex_content": "\\documentclass{article}...",
  "download_url": "/api/v1/documents/download/uuid-string.tex"
}
```

---

## Testing & Benchmarking

### Run A/B Test

Compare two scoring algorithms (admin only).

**Endpoint:** `POST /api/v1/testing/ab-test`

**Request:**
```json
{
  "test_name": "semantic_matching_v2",
  "test_resumes": ["resume_id_1", "resume_id_2", ...],
  "control_scorer": "v1",
  "variant_scorer": "v2"
}
```

**Response:**
```json
{
  "test_id": "uuid-string",
  "results": {
    "sample_size": 20,
    "mean_delta": 5.2,
    "p_value": 0.003,
    "statistically_significant": true,
    "recommendation": "DEPLOY",
    "confidence": "high"
  }
}
```

---

### Performance Benchmark

Get current system performance metrics.

**Endpoint:** `GET /api/v1/benchmark/performance`

**Response:**
```json
{
  "avg_scoring_time_ms": 1250,
  "cached_scoring_time_ms": 380,
  "memory_usage_mb": 245,
  "success_rate": 99.2,
  "requests_per_second": 50,
  "meets_targets": {
    "first_run_under_2s": true,
    "cached_under_500ms": true
  }
}
```

---

## Error Handling

All errors follow this format:

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": {
      "field": "specific field with issue",
      "reason": "why it failed"
    },
    "timestamp": "2026-02-20T10:30:00Z"
  }
}
```

### Common Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `INVALID_FILE_FORMAT` | 400 | Unsupported file type |
| `FILE_TOO_LARGE` | 413 | File exceeds 10MB limit |
| `PARSING_ERROR` | 422 | Cannot parse resume |
| `MISSING_REQUIRED_FIELD` | 400 | Required field missing |
| `RATE_LIMIT_EXCEEDED` | 429 | Too many requests |
| `RESUME_NOT_FOUND` | 404 | Resume ID not found |
| `INTERNAL_ERROR` | 500 | Server error |

---

## Rate Limiting

Current limits (subject to change):

- **Anonymous users:** 10 requests/minute
- **Registered users:** 60 requests/minute
- **Premium users:** Unlimited

Rate limit headers:
```http
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1708434600
```

---

## Examples

### Complete Workflow Example

```python
import requests

BASE_URL = "http://localhost:8000/api/v1"

# 1. Upload resume
with open("resume.pdf", "rb") as f:
    response = requests.post(
        f"{BASE_URL}/resumes/upload",
        files={"file": f},
        data={"job_description": "Python developer..."}
    )
resume_id = response.json()["resume_id"]

# 2. Score resume
score_response = requests.post(
    f"{BASE_URL}/score",
    json={
        "resume_text": response.json()["parsed_text"],
        "job_description": "Python developer..."
    }
)
score = score_response.json()["overall_score"]
print(f"Score: {score}")

# 3. Check ATS compatibility
ats_response = requests.post(
    f"{BASE_URL}/ats/simulate",
    json={
        "resume_text": response.json()["parsed_text"],
        "platforms": ["taleo", "workday"]
    }
)
compatibility = ats_response.json()
print(f"ATS Compatibility: {compatibility['overall_compatibility']}")

# 4. Get grammar feedback
grammar_response = requests.post(
    f"{BASE_URL}/quality/grammar",
    json={"text": response.json()["parsed_text"]}
)
issues = grammar_response.json()["issues"]
print(f"Grammar issues: {len(issues)}")
```

### JavaScript Example

```javascript
const BASE_URL = "http://localhost:8000/api/v1";

// Upload and score resume
async function scoreResume(resumeFile, jobDescription) {
  // Upload
  const formData = new FormData();
  formData.append("file", resumeFile);
  formData.append("job_description", jobDescription);

  const uploadResponse = await fetch(`${BASE_URL}/resumes/upload`, {
    method: "POST",
    body: formData
  });

  const uploadData = await uploadResponse.json();

  // Score
  const scoreResponse = await fetch(`${BASE_URL}/score`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      resume_text: uploadData.parsed_text,
      job_description: jobDescription
    })
  });

  const scoreData = await scoreResponse.json();
  return scoreData;
}

// Usage
const result = await scoreResume(fileInput.files[0], jobDescriptionText);
console.log(`Overall Score: ${result.overall_score}`);
console.log(`Top Issues:`, result.top_issues);
```

### cURL Examples

```bash
# Upload resume
curl -X POST http://localhost:8000/api/v1/resumes/upload \
  -F "file=@resume.pdf" \
  -F "job_description=Python developer position"

# Score resume
curl -X POST http://localhost:8000/api/v1/score \
  -H "Content-Type: application/json" \
  -d '{
    "resume_text": "Resume text...",
    "job_description": "Job description..."
  }'

# Check grammar
curl -X POST http://localhost:8000/api/v1/quality/grammar \
  -H "Content-Type: application/json" \
  -d '{"text": "Text to check..."}'
```

---

## Webhooks

Future feature: Get notified when scoring completes.

```json
{
  "webhook_url": "https://your-app.com/webhook",
  "events": ["score_complete", "ats_check_complete"]
}
```

---

## SDK Support

Official SDKs (planned):

- Python: `pip install ats-scorer-sdk`
- JavaScript: `npm install @ats-scorer/sdk`
- Ruby: `gem install ats_scorer`

---

## Versioning

API versioning follows semantic versioning:

- Current version: `v1`
- Breaking changes will increment major version
- New features increment minor version
- Bug fixes increment patch version

Legacy versions supported for 6 months after new major version release.

---

## Support

- Documentation: https://docs.atsscorer.com
- GitHub: https://github.com/yourusername/ats-resume-scorer
- Email: api-support@atsscorer.com

---

**Version:** 1.0.0
**Last Updated:** 2026-02-20
**Status:** Production Ready
