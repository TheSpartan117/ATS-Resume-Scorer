# API Documentation

## Overview

The ATS Resume Scorer API provides intelligent resume analysis with dual-mode scoring:
- **Mode A (ATS Simulation)**: Harsh keyword-heavy scoring for job description matching
- **Mode B (Quality Coach)**: Balanced quality scoring for general resume improvement

Base URL: `http://localhost:8000`

---

## Authentication

Most endpoints require JWT authentication. Include the token in the Authorization header:

```
Authorization: Bearer <your_jwt_token>
```

### POST /api/auth/register
Register a new user account.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123",
  "full_name": "John Doe"
}
```

**Response:**
```json
{
  "id": 1,
  "email": "user@example.com",
  "full_name": "John Doe",
  "created_at": "2026-02-19T10:00:00Z"
}
```

### POST /api/auth/login
Login and receive JWT token.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

---

## Resume Upload & Parsing

### POST /api/upload
Upload and parse a resume file (PDF, DOCX).

**Headers:**
- `Authorization: Bearer <token>`
- `Content-Type: multipart/form-data`

**Form Data:**
- `file`: Resume file (PDF or DOCX, max 5MB)
- `jobDescription` (optional): Job description text
- `role` (optional): Role ID (e.g., "software_engineer", "product_manager")
- `level` (optional): Experience level ("entry", "mid", "senior", "lead", "executive")

**Response:**
```json
{
  "id": 123,
  "fileName": "john_doe_resume.pdf",
  "contact": {
    "name": "John Doe",
    "email": "john.doe@example.com",
    "phone": "555-1234",
    "location": "San Francisco, CA",
    "linkedin": "linkedin.com/in/johndoe"
  },
  "experience": [
    {
      "title": "Senior Software Engineer",
      "company": "Tech Corp",
      "startDate": "Jan 2020",
      "endDate": "Present",
      "description": "Led development of microservices architecture..."
    }
  ],
  "education": [
    {
      "degree": "BS Computer Science",
      "institution": "Stanford University",
      "graduationDate": "2019"
    }
  ],
  "skills": ["Python", "React", "AWS", "Docker"],
  "certifications": [
    {
      "name": "AWS Solutions Architect",
      "issuer": "Amazon",
      "date": "2021"
    }
  ],
  "metadata": {
    "pageCount": 2,
    "wordCount": 450,
    "fileFormat": "pdf",
    "hasPhoto": false
  },
  "score": {
    "overallScore": 78.5,
    "mode": "ats_simulation",
    "breakdown": {
      "keyword_match": {
        "score": 52.0,
        "maxScore": 70,
        "issues": [
          ["warning", "Missing 3 required keywords: kubernetes, terraform, jenkins"]
        ]
      },
      "format": {
        "score": 18.0,
        "maxScore": 20,
        "issues": [
          ["info", "Has contact section, Has experience section, Has education section, Has skills section, Complete contact info"]
        ]
      },
      "structure": {
        "score": 8.5,
        "maxScore": 10,
        "issues": [
          ["info", "3 experience entries, 1 education entry, 12 skills"]
        ]
      }
    },
    "issues": {
      "critical": [],
      "warnings": [
        ["warning", "Missing 3 required keywords: kubernetes, terraform, jenkins"]
      ],
      "suggestions": [
        ["suggestion", "Consider adding more certifications"]
      ],
      "info": [
        ["info", "Strong experience match"]
      ]
    },
    "strengths": [
      "Strong keyword match with required skills",
      "ATS-compatible format"
    ],
    "keyword_details": {
      "required_matched": 12,
      "required_total": 15,
      "required_match_pct": 80.0,
      "preferred_matched": 6,
      "preferred_total": 10,
      "preferred_match_pct": 60.0
    },
    "auto_reject": false,
    "rejection_reason": null
  }
}
```

---

## Scoring Endpoints

### POST /api/score
Re-score resume with updated data (used by editor).

**Headers:**
- `Authorization: Bearer <token>`
- `Content-Type: application/json`

**Request Body:**
```json
{
  "fileName": "john_doe_resume.pdf",
  "contact": {
    "name": "John Doe",
    "email": "john.doe@example.com",
    "phone": "555-1234",
    "location": "San Francisco, CA",
    "linkedin": "linkedin.com/in/johndoe"
  },
  "experience": [...],
  "education": [...],
  "skills": [...],
  "certifications": [...],
  "metadata": {...},
  "jobDescription": "We are looking for a Senior Software Engineer...",
  "role": "software_engineer",
  "level": "senior"
}
```

**Response:**
```json
{
  "overallScore": 78.5,
  "mode": "ats_simulation",
  "breakdown": {
    "keyword_match": {...},
    "format": {...},
    "structure": {...}
  },
  "issues": {
    "critical": [],
    "warnings": [...],
    "suggestions": [...],
    "info": [...]
  },
  "strengths": [...],
  "keywordDetails": {
    "required_matched": 12,
    "required_total": 15,
    "required_match_pct": 80.0,
    "preferred_matched": 6,
    "preferred_total": 10,
    "preferred_match_pct": 60.0
  },
  "autoReject": false
}
```

---

## Dual-Mode Scoring System

### Mode Detection

The system automatically detects which mode to use:
- **ATS Simulation Mode**: Triggered when `jobDescription` is provided
- **Quality Coach Mode**: Used when no `jobDescription` is provided

You can also explicitly set the mode using the `mode` parameter:
```json
{
  "mode": "ats_simulation"  // or "quality_coach"
}
```

### Mode A: ATS Simulation (70/20/10)

Used when matching against a specific job description.

**Scoring Breakdown:**
- **Keyword Match (70 points)**
  - Required Keywords: 50 points
  - Preferred Keywords: 20 points
  - Auto-reject if required match < 60%
- **Format (20 points)**
  - Section presence
  - Contact info completeness
  - ATS-friendly structure
- **Structure (10 points)**
  - Experience entries
  - Education entries
  - Skills count

**Example Response:**
```json
{
  "overallScore": 78.5,
  "mode": "ats_simulation",
  "breakdown": {
    "keyword_match": {
      "score": 52.0,
      "maxScore": 70
    },
    "format": {
      "score": 18.0,
      "maxScore": 20
    },
    "structure": {
      "score": 8.5,
      "maxScore": 10
    }
  },
  "keyword_details": {
    "required_matched": 12,
    "required_total": 15,
    "required_match_pct": 80.0,
    "preferred_matched": 6,
    "preferred_total": 10,
    "preferred_match_pct": 60.0
  },
  "auto_reject": false,
  "rejection_reason": null
}
```

**Keyword Transparency:**
The `keyword_details` object shows:
- `required_matched`: Number of required keywords found
- `required_total`: Total number of required keywords
- `required_match_pct`: Percentage match for required keywords
- `preferred_matched`: Number of preferred keywords found
- `preferred_total`: Total number of preferred keywords
- `preferred_match_pct`: Percentage match for preferred keywords

**Auto-Reject Logic:**
- If `required_match_pct < 60%`, then `auto_reject = true`
- This simulates harsh ATS filtering

### Mode B: Quality Coach (25/30/25/20)

Used for general resume improvement without a specific job description.

**Scoring Breakdown:**
- **Role Keywords (25 points)** - Generous scoring
  - Match percentage ≥60% = 25 points
  - Match percentage ≥50% = 22 points
  - Match percentage ≥40% = 18 points
  - Match percentage ≥30% = 15 points
  - Match percentage ≥20% = 12 points
  - Linear scaling below 20%
- **Content Quality (30 points)**
  - Metrics/quantification: up to 15 points
  - Bullet points: up to 10 points
  - Action verbs: up to 5 points
- **Format (25 points)**
  - Same as ATS mode but scaled to 25 points
- **Professional Polish (20 points)**
  - Word count: up to 10 points
  - Page count: up to 5 points
  - Contact completeness: up to 5 points

**Example Response:**
```json
{
  "overallScore": 82.0,
  "mode": "quality_coach",
  "breakdown": {
    "role_keywords": {
      "score": 22.0,
      "maxScore": 25
    },
    "content_quality": {
      "score": 25.0,
      "maxScore": 30
    },
    "format": {
      "score": 20.0,
      "maxScore": 25
    },
    "professional_polish": {
      "score": 15.0,
      "maxScore": 20
    }
  },
  "keyword_details": {
    "keywords_matched": 18,
    "keywords_total": 25,
    "verbs_matched": 12,
    "verbs_total": 20,
    "overall_match_pct": 66.7
  },
  "cta": "Your resume is good. Consider minor improvements."
}
```

---

## Resume Management

### GET /api/resumes
Get all resumes for authenticated user.

**Response:**
```json
[
  {
    "id": 123,
    "fileName": "john_doe_resume.pdf",
    "uploadedAt": "2026-02-19T10:00:00Z",
    "score": 78.5,
    "role": "software_engineer",
    "level": "senior"
  }
]
```

### GET /api/resumes/{id}
Get specific resume by ID.

**Response:**
```json
{
  "id": 123,
  "fileName": "john_doe_resume.pdf",
  "contact": {...},
  "experience": [...],
  "education": [...],
  "skills": [...],
  "certifications": [...],
  "metadata": {...},
  "score": {...}
}
```

### DELETE /api/resumes/{id}
Delete a resume.

**Response:**
```json
{
  "message": "Resume deleted successfully"
}
```

---

## Export Endpoints

### GET /api/export/{resume_id}/pdf
Export resume as PDF.

**Response:**
PDF file download

### GET /api/export/{resume_id}/docx
Export resume as DOCX.

**Response:**
DOCX file download

---

## Role Taxonomy

### GET /api/roles
Get available roles and experience levels.

**Response:**
```json
{
  "roles": [
    {
      "id": "software_engineer",
      "name": "Software Engineer",
      "levels": ["entry", "mid", "senior", "lead"]
    },
    {
      "id": "product_manager",
      "name": "Product Manager",
      "levels": ["entry", "mid", "senior", "lead", "executive"]
    }
  ]
}
```

---

## Issues and Severity Levels

All scoring responses include an `issues` object with four severity levels:

### Critical Issues
- **Impact**: Major red flags that severely hurt ATS compatibility
- **Examples**:
  - Missing required sections
  - Date errors (end before start)
  - Extremely short bullet points (<30 chars)
  - Unparseable dates

### Warnings
- **Impact**: Moderate issues that should be addressed
- **Examples**:
  - Employment gaps (9-18 months)
  - Job hopping (multiple <1 year tenures)
  - Vague phrases ("responsible for")
  - Email professionalism issues

### Suggestions
- **Impact**: Minor improvements for better presentation
- **Examples**:
  - Missing LinkedIn profile
  - Could add professional summary
  - Bullet points could be more concise

### Info
- **Impact**: Neutral observations or positive findings
- **Examples**:
  - "Has all required sections"
  - "Good keyword match"
  - "Appropriate length"

**Example:**
```json
{
  "issues": {
    "critical": [
      ["critical", "Missing required section: Experience"]
    ],
    "warnings": [
      ["warning", "Employment gap of 12 months detected"]
    ],
    "suggestions": [
      ["suggestion", "Consider adding LinkedIn profile"]
    ],
    "info": [
      ["info", "Resume has optimal word count"]
    ]
  }
}
```

---

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Invalid file format. Only PDF and DOCX supported."
}
```

### 401 Unauthorized
```json
{
  "detail": "Not authenticated"
}
```

### 404 Not Found
```json
{
  "detail": "Resume not found"
}
```

### 422 Unprocessable Entity
```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "value is not a valid email address",
      "type": "value_error.email"
    }
  ]
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error"
}
```

---

## Rate Limiting

API endpoints are rate-limited to prevent abuse:
- **Upload endpoint**: 10 requests per minute
- **Other endpoints**: 60 requests per minute

Rate limit headers:
```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1645267200
```

---

## Health Check

### GET /health
Check API health status.

**Response:**
```json
{
  "status": "healthy"
}
```

---

## Best Practices

1. **Always provide role and level** for accurate scoring
2. **Include job description** for ATS Simulation mode
3. **Cache parsed resumes** on client side to avoid re-parsing
4. **Use /api/score endpoint** for real-time scoring during editing
5. **Handle auto_reject flag** to warn users about harsh ATS filtering
6. **Display keyword transparency** to help users improve keyword match
7. **Show severity-categorized issues** for better user experience
8. **Respect rate limits** by implementing client-side throttling

---

## Webhook Support (Coming Soon)

Subscribe to events:
- `resume.uploaded`
- `resume.scored`
- `resume.deleted`

---

## Version History

- **v2.0.0** (Current): Dual-mode scoring system with 44-parameter validation
- **v1.0.0**: Initial release with basic ATS scoring
