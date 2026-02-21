# API Guide - ATS Resume Scorer

**Version**: 3.0
**Base URL**: `http://localhost:8000` (development)
**Last Updated**: February 22, 2026

## Overview

The ATS Resume Scorer provides a RESTful API built with FastAPI. This guide covers all endpoints, request/response formats, and usage examples.

## Authentication

Currently, the API does not require authentication for basic scoring functionality. Future versions may add user accounts and API keys.

## Base URL

- **Development**: `http://localhost:8000`
- **Production**: (TBD)

## API Documentation

Interactive API documentation is available at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## Endpoints

### 1. Health Check

**GET** `/health`

Check if the API server is running.

**Response**:
```json
{
  "status": "healthy"
}
```

**Example**:
```bash
curl http://localhost:8000/health
```

---

### 2. Get Available Roles

**GET** `/api/roles`

Get all available job roles grouped by category.

**Response**:
```json
{
  "categories": {
    "tech": [
      {"id": "software_engineer", "name": "Software Engineer"},
      {"id": "devops_engineer", "name": "DevOps Engineer"},
      {"id": "qa_engineer", "name": "QA Engineer"}
    ],
    "product": [
      {"id": "product_manager", "name": "Product Manager"},
      {"id": "technical_product_manager", "name": "Technical Product Manager"}
    ],
    "design": [
      {"id": "ux_designer", "name": "UX Designer"},
      {"id": "ui_designer", "name": "UI Designer"},
      {"id": "product_designer", "name": "Product Designer"}
    ],
    "business": [
      {"id": "marketing_manager", "name": "Marketing Manager"},
      {"id": "sales_manager", "name": "Sales Manager"},
      {"id": "business_analyst", "name": "Business Analyst"}
    ],
    "data": [
      {"id": "data_scientist", "name": "Data Scientist"},
      {"id": "data_engineer", "name": "Data Engineer"}
    ],
    "operations": [
      {"id": "operations_manager", "name": "Operations Manager"},
      {"id": "project_manager", "name": "Project Manager"}
    ],
    "finance": [
      {"id": "financial_analyst", "name": "Financial Analyst"},
      {"id": "accountant", "name": "Accountant"}
    ],
    "hr": [
      {"id": "hr_manager", "name": "HR Manager"},
      {"id": "recruiter", "name": "Recruiter"}
    ],
    "legal": [
      {"id": "corporate_lawyer", "name": "Corporate Lawyer"}
    ],
    "customer": [
      {"id": "customer_success_manager", "name": "Customer Success Manager"}
    ],
    "creative": [
      {"id": "content_writer", "name": "Content Writer"}
    ]
  },
  "levels": [
    {"id": "beginner", "name": "Beginner", "description": "0-3 years experience"},
    {"id": "intermediary", "name": "Intermediary", "description": "3-7 years experience"},
    {"id": "senior", "name": "Senior", "description": "7+ years experience"}
  ]
}
```

**Example**:
```bash
curl http://localhost:8000/api/roles
```

---

### 3. Upload Resume

**POST** `/api/upload`

Upload a resume file (PDF or DOCX) for scoring.

**Request** (multipart/form-data):
- `file` (required): Resume file (PDF or DOCX, max 10MB)
- `role` (optional): Job role ID (e.g., "product_manager")
- `level` (optional): Experience level ("beginner", "intermediary", "senior")
- `jobDescription` (optional): Target job description text

**Response**:
```json
{
  "score": {
    "total_score": 89.0,
    "max_score": 100,
    "percentage": 89.0,
    "rating": "Excellent",
    "category_scores": {
      "Keyword Matching": {
        "score": 14.0,
        "max": 25,
        "parameters": {
          "P1.1": {
            "score": 9.8,
            "max_score": 25,
            "percentage": 39.2,
            "status": "success",
            "details": {
              "matched_keywords": ["product", "agile", "data", "analytics", ...],
              "total_keywords": 28,
              "matched_count": 11
            }
          },
          "P1.2": {
            "score": 4.2,
            "max_score": 10,
            "percentage": 42.0,
            "status": "success",
            "details": {
              "matched_keywords": ["AI", "ML", "cloud", ...],
              "total_keywords": 32,
              "matched_count": 13
            }
          }
        }
      },
      "Content Quality": {
        "score": 32.0,
        "max": 35,
        "parameters": { ... }
      },
      "Format & Structure": {
        "score": 20.0,
        "max": 15,
        "parameters": { ... }
      },
      "Professional Polish": {
        "score": 14.0,
        "max": 10,
        "parameters": { ... }
      },
      "Experience Validation": {
        "score": 7.0,
        "max": 10,
        "parameters": { ... }
      },
      "Readability": {
        "score": 4.5,
        "max": 5,
        "parameters": { ... }
      },
      "Red Flags": {
        "score": -2.0,
        "max": 0,
        "parameters": { ... }
      }
    },
    "feedback": {
      "strengths": [
        "Strong keyword matching in required skills",
        "Excellent formatting and structure",
        "Clear action verbs and quantification"
      ],
      "weaknesses": [
        "Missing some preferred keywords (AI, ML)",
        "Could add more metrics to bullets",
        "Minor grammar improvements needed"
      ],
      "recommendations": [
        "Add keywords: AI, machine learning, automation",
        "Quantify achievements with metrics (%, $, numbers)",
        "Review grammar and spelling"
      ],
      "priority_fixes": {
        "P1.2": "Add more preferred keywords from the job description",
        "P2.2": "Quantify more achievements with specific metrics"
      }
    }
  },
  "resume_data": {
    "contact": {
      "name": "John Doe",
      "email": "john.doe@example.com",
      "phone": "+1-555-0100",
      "location": "San Francisco, CA",
      "linkedin": "linkedin.com/in/johndoe"
    },
    "experience": [ ... ],
    "education": [ ... ],
    "skills": [ ... ],
    "metadata": {
      "pageCount": 2,
      "wordCount": 650,
      "hasPhoto": false,
      "fileFormat": "pdf"
    }
  }
}
```

**Example (cURL)**:
```bash
curl -X POST http://localhost:8000/api/upload \
  -F "file=@resume.pdf" \
  -F "role=product_manager" \
  -F "level=intermediary" \
  -F "jobDescription=Looking for a Senior Product Manager with 5+ years of experience..."
```

**Example (Python)**:
```python
import requests

url = "http://localhost:8000/api/upload"
files = {"file": open("resume.pdf", "rb")}
data = {
    "role": "product_manager",
    "level": "intermediary",
    "jobDescription": "Looking for a Senior Product Manager..."
}

response = requests.post(url, files=files, data=data)
result = response.json()

print(f"Total Score: {result['score']['total_score']}/100")
print(f"Rating: {result['score']['rating']}")
```

**Example (JavaScript/Fetch)**:
```javascript
const formData = new FormData();
formData.append('file', fileInput.files[0]);
formData.append('role', 'product_manager');
formData.append('level', 'intermediary');
formData.append('jobDescription', 'Looking for a Senior Product Manager...');

const response = await fetch('http://localhost:8000/api/upload', {
  method: 'POST',
  body: formData
});

const result = await response.json();
console.log('Score:', result.score.total_score);
```

---

### 4. Re-score Resume

**POST** `/api/score`

Re-score resume content after editing (without uploading a new file).

**Request** (application/json):
```json
{
  "fileName": "resume.pdf",
  "contact": {
    "name": "John Doe",
    "email": "john.doe@example.com",
    "phone": "+1-555-0100",
    "location": "San Francisco, CA",
    "linkedin": "linkedin.com/in/johndoe"
  },
  "experience": [
    {
      "company": "Tech Corp",
      "title": "Product Manager",
      "startDate": "2020-01",
      "endDate": "2023-12",
      "location": "San Francisco, CA",
      "bullets": [
        "Led cross-functional team of 12 to launch new product feature",
        "Increased user engagement by 35% through A/B testing",
        "Managed $2M product budget and roadmap planning"
      ]
    }
  ],
  "education": [
    {
      "institution": "Stanford University",
      "degree": "BS Computer Science",
      "graduationDate": "2019-06",
      "gpa": "3.8"
    }
  ],
  "skills": ["Python", "SQL", "Product Management", "Agile", "Data Analysis"],
  "certifications": [
    {"name": "Certified Scrum Product Owner", "issuer": "Scrum Alliance", "date": "2021-03"}
  ],
  "metadata": {
    "pageCount": 2,
    "wordCount": 650,
    "hasPhoto": false,
    "fileFormat": "pdf"
  },
  "role": "product_manager",
  "level": "intermediary",
  "jobDescription": "Looking for a Senior Product Manager..."
}
```

**Response**: Same as upload endpoint

**Example (Python)**:
```python
import requests

url = "http://localhost:8000/api/score"
data = {
    "fileName": "resume.pdf",
    "contact": {
        "name": "John Doe",
        "email": "john.doe@example.com"
    },
    "experience": [...],
    "education": [...],
    "skills": [...],
    "certifications": [],
    "metadata": {
        "pageCount": 2,
        "wordCount": 650,
        "hasPhoto": False,
        "fileFormat": "pdf"
    },
    "role": "product_manager",
    "level": "intermediary"
}

response = requests.post(url, json=data)
result = response.json()
```

---

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Invalid file format. Only PDF and DOCX files are supported."
}
```

### 413 Payload Too Large
```json
{
  "detail": "File size exceeds 10MB limit."
}
```

### 422 Unprocessable Entity
```json
{
  "detail": [
    {
      "loc": ["body", "role"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

### 500 Internal Server Error
```json
{
  "detail": "Failed to parse resume. Please ensure the file is a valid PDF or DOCX."
}
```

---

## Rate Limiting

Currently, no rate limiting is implemented. Future versions will enforce:
- **Free tier**: 10 requests per hour
- **Premium tier**: Unlimited requests

---

## Response Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 400 | Bad request (invalid parameters) |
| 413 | File too large |
| 422 | Validation error |
| 500 | Server error |

---

## Data Models

### ScoreResult
```typescript
interface ScoreResult {
  total_score: number;        // 0-100
  max_score: number;          // Always 100
  raw_score: number;          // Before normalization
  percentage: number;         // Same as total_score
  rating: "Excellent" | "Good" | "Fair" | "Poor";
  category_scores: {
    [category: string]: {
      score: number;
      max: number;
      parameters: {
        [code: string]: ParameterResult
      }
    }
  };
  feedback: Feedback;
}
```

### ParameterResult
```typescript
interface ParameterResult {
  score: number;
  max_score: number;
  percentage: number;
  status: "success" | "error" | "skipped";
  details: any;  // Parameter-specific details
}
```

### Feedback
```typescript
interface Feedback {
  strengths: string[];
  weaknesses: string[];
  recommendations: string[];
  priority_fixes: {
    [parameter_code: string]: string
  };
}
```

### ResumeData
```typescript
interface ResumeData {
  contact: Contact;
  experience: Experience[];
  education: Education[];
  skills: string[];
  certifications: Certification[];
  metadata: Metadata;
}

interface Contact {
  name?: string;
  email?: string;
  phone?: string;
  location?: string;
  linkedin?: string;
  website?: string;
}

interface Experience {
  company: string;
  title: string;
  startDate: string;       // YYYY-MM format
  endDate: string | "Present";
  location?: string;
  bullets: string[];
}

interface Education {
  institution: string;
  degree: string;
  graduationDate: string;  // YYYY-MM format
  gpa?: string;
  location?: string;
}

interface Certification {
  name: string;
  issuer: string;
  date: string;
}

interface Metadata {
  pageCount: number;
  wordCount: number;
  hasPhoto: boolean;
  fileFormat: "pdf" | "docx";
}
```

---

## Frontend Integration

### React/TypeScript Example

```typescript
// api/client.ts
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export async function uploadResume(
  file: File,
  role?: string,
  level?: string,
  jobDescription?: string
): Promise<UploadResponse> {
  const formData = new FormData();
  formData.append('file', file);

  if (role) formData.append('role', role);
  if (level) formData.append('level', level);
  if (jobDescription) formData.append('jobDescription', jobDescription);

  const response = await apiClient.post<UploadResponse>('/api/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });

  return response.data;
}

export async function getRoles(): Promise<RolesResponse> {
  const response = await apiClient.get<RolesResponse>('/api/roles');
  return response.data;
}
```

### Usage in Component

```typescript
import { uploadResume, getRoles } from './api/client';

function UploadPage() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [selectedRole, setSelectedRole] = useState('');
  const [selectedLevel, setSelectedLevel] = useState('');
  const [rolesData, setRolesData] = useState<RolesResponse | null>(null);

  useEffect(() => {
    const fetchRoles = async () => {
      const data = await getRoles();
      setRolesData(data);
    };
    fetchRoles();
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedFile) return;

    try {
      const result = await uploadResume(
        selectedFile,
        selectedRole,
        selectedLevel
      );

      console.log('Score:', result.score.total_score);
      navigate('/results', { state: { result } });
    } catch (error) {
      console.error('Upload failed:', error);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      {/* UI components */}
    </form>
  );
}
```

---

## CORS Configuration

The API is configured to accept requests from:
- `http://localhost:5173` (Vite dev server)
- `http://localhost:3000` (Alternative frontend port)

For production deployments, update CORS origins in `backend/main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://your-production-domain.com"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## Testing the API

### Using cURL

**1. Health check**:
```bash
curl http://localhost:8000/health
```

**2. Get roles**:
```bash
curl http://localhost:8000/api/roles
```

**3. Upload resume**:
```bash
curl -X POST http://localhost:8000/api/upload \
  -F "file=@resume.pdf" \
  -F "role=product_manager" \
  -F "level=intermediary"
```

### Using Python

```python
import requests

# Health check
response = requests.get("http://localhost:8000/health")
print(response.json())

# Get roles
response = requests.get("http://localhost:8000/api/roles")
roles = response.json()
print(f"Available roles: {len(roles['categories'])} categories")

# Upload resume
files = {"file": open("resume.pdf", "rb")}
data = {"role": "product_manager", "level": "intermediary"}
response = requests.post("http://localhost:8000/api/upload", files=files, data=data)
result = response.json()
print(f"Score: {result['score']['total_score']}/100")
```

---

## Performance

- **Average response time**: ~3 seconds per resume
- **File size limit**: 10MB
- **Concurrent requests**: Handled by Uvicorn workers
- **Caching**: Resume data cached during session (localStorage in frontend)

---

## Security

### Current Status
- No authentication required (open API)
- File size validation (max 10MB)
- File type validation (PDF, DOCX only)
- CORS enabled for localhost

### Planned Improvements
- User authentication with JWT tokens
- API key system for external integrations
- Rate limiting per user/IP
- File scanning for malware
- Data encryption at rest

---

## Further Reading

- **[SYSTEM_OVERVIEW.md](./SYSTEM_OVERVIEW.md)** - System architecture
- **[SCORING_SYSTEM.md](./SCORING_SYSTEM.md)** - Scoring methodology
- **[DEVELOPMENT_GUIDE.md](./DEVELOPMENT_GUIDE.md)** - Developer guide
