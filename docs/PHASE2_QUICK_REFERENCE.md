# Phase 2: Quick Reference Guide

**Quick access guide to Phase 2 features, APIs, and usage examples**

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [API Endpoints](#api-endpoints)
3. [Code Examples](#code-examples)
4. [Frontend Integration](#frontend-integration)
5. [Testing](#testing)
6. [Troubleshooting](#troubleshooting)

---

## Quick Start

### Installation

```bash
# Install Phase 2 dependencies (if not already installed)
cd /Users/sabuj.mondal/ats-resume-scorer/backend
pip install -r requirements.txt

# Or install individually:
pip install sentence-transformers==2.3.1 KeyBERT==0.8.3 diskcache==5.6.3
```

### Verify Installation

```bash
# Run Phase 2 tests
python -m pytest tests/test_phase2_features.py -v

# Start backend server
uvicorn main:app --reload --port 8000

# Test health endpoint
curl http://localhost:8000/api/phase2/health
```

---

## API Endpoints

### Base URL
```
http://localhost:8000/api/phase2
```

### 1. ATS Platform Simulation

**Overall Compatibility**
```bash
POST /api/phase2/ats-simulation

curl -X POST http://localhost:8000/api/phase2/ats-simulation \
  -H "Content-Type: application/json" \
  -d '{
    "resume_text": "Your resume text here...",
    "resume_metadata": {
      "format": "pdf",
      "page_count": 2
    }
  }'
```

**Response:**
```json
{
  "success": true,
  "data": {
    "overall_score": 78.5,
    "rating": "Good",
    "platforms_passed": "2/3 major platforms",
    "platforms": {
      "Taleo": {
        "pass_probability": 65,
        "rating": "Fair",
        "issues": [...],
        "recommendations": [...]
      },
      "Workday": {
        "pass_probability": 85,
        "rating": "Very Good"
      },
      "Greenhouse": {
        "pass_probability": 95,
        "rating": "Excellent"
      }
    }
  }
}
```

**Specific Platform**
```bash
POST /api/phase2/ats-simulation/platform/{platform}
# platforms: taleo, workday, greenhouse

curl -X POST http://localhost:8000/api/phase2/ats-simulation/platform/taleo \
  -H "Content-Type: application/json" \
  -d '{"resume_text": "..."}'
```

### 2. Skills Categorization

```bash
POST /api/phase2/skills-analysis

curl -X POST http://localhost:8000/api/phase2/skills-analysis \
  -H "Content-Type: application/json" \
  -d '{
    "resume_text": "Skills: Python, AWS, Leadership...",
    "job_description": "Looking for Python developer..."
  }'
```

**Response:**
```json
{
  "success": true,
  "data": {
    "resume_skills": {
      "hard_skills": ["python", "aws", "docker"],
      "soft_skills": ["leadership", "communication"]
    },
    "hard_skills_analysis": {
      "match_rate": 75.5,
      "matched_skills": ["python", "aws"],
      "missing_skills": ["kubernetes"],
      "rating": "Very Good"
    },
    "soft_skills_analysis": {
      "match_rate": 66.7,
      "matched_skills": ["leadership"],
      "missing_skills": ["problem solving"]
    },
    "overall_match": {
      "overall_match_rate": 73.1,
      "summary": "Strong match! Your skills align well..."
    }
  }
}
```

### 3. Heat Map Data

```bash
POST /api/phase2/heat-map

curl -X POST http://localhost:8000/api/phase2/heat-map \
  -H "Content-Type: application/json" \
  -d '{
    "resume_text": "...",
    "job_description": "...",
    "threshold": 0.7
  }'
```

**Response:**
```json
{
  "success": true,
  "data": {
    "match_rate": 70.5,
    "matched_keywords": [
      {"keyword": "python", "similarity": 0.95},
      {"keyword": "aws", "similarity": 0.88}
    ],
    "missing_keywords": ["kubernetes", "terraform"],
    "method": "semantic"
  }
}
```

### 4. Confidence Intervals

```bash
POST /api/phase2/confidence-intervals

curl -X POST http://localhost:8000/api/phase2/confidence-intervals \
  -H "Content-Type: application/json" \
  -d '{
    "scores": {
      "keyword_score": 75.0,
      "quality_score": 82.0
    },
    "sample_sizes": {
      "keyword_score": 30,
      "quality_score": 50
    }
  }'
```

**Response:**
```json
{
  "success": true,
  "confidence_level": "95%",
  "data": {
    "keyword_score": {
      "score": 75.0,
      "confidence_interval": "[70.2, 79.8]",
      "margin_of_error": 4.8,
      "text": "75 ± 5 points (95% confidence)",
      "reliability": "High"
    }
  }
}
```

### 5. Comprehensive Analysis (All Features)

```bash
POST /api/phase2/comprehensive-analysis

curl -X POST http://localhost:8000/api/phase2/comprehensive-analysis \
  -H "Content-Type: application/json" \
  -d '{
    "resume_text": "...",
    "job_description": "...",
    "resume_metadata": {"format": "pdf"}
  }'
```

**Response:** Includes all Phase 2 features in one response.

---

## Code Examples

### Python Backend Usage

#### 1. ATS Simulation

```python
from backend.services.ats_simulator import ATSSimulator, analyze_ats_compatibility

# Quick analysis
result = analyze_ats_compatibility(resume_text)
print(f"Overall ATS Score: {result['overall_score']}%")
print(f"Passed {result['platforms_passed']}")

# Detailed platform simulation
simulator = ATSSimulator()

taleo_result = simulator.simulate_taleo(resume_text)
print(f"Taleo: {taleo_result['pass_probability']}%")
print(f"Issues: {len(taleo_result['issues'])}")

workday_result = simulator.simulate_workday(resume_text)
greenhouse_result = simulator.simulate_greenhouse(resume_text)
```

#### 2. Skills Categorization

```python
from backend.services.skills_categorizer import SkillsCategorizer, analyze_skills

# Quick analysis
result = analyze_skills(resume_text, job_description)
print(f"Hard Skills Match: {result['hard_skills_analysis']['match_rate']}%")
print(f"Soft Skills Match: {result['soft_skills_analysis']['match_rate']}%")

# Detailed categorization
categorizer = SkillsCategorizer()
skills = categorizer.extract_skills(resume_text)
print(f"Found {len(skills['hard_skills'])} hard skills")
print(f"Found {len(skills['soft_skills'])} soft skills")

# With job matching
detailed = categorizer.categorize_skills(resume_text, job_description)
print(f"Missing Skills: {detailed['hard_skills_analysis']['missing_skills']}")
```

#### 3. Confidence Scoring

```python
from backend.services.confidence_scorer import (
    ConfidenceScorer,
    add_confidence_intervals,
    format_score_with_confidence
)

# Single score
scorer = ConfidenceScorer()
confidence = scorer.calculate_with_confidence(score=75.0, sample_size=30)
print(confidence.confidence_text)  # "75 ± 5 points (95% confidence)"

# Multiple scores
scores = {'keyword_score': 75.0, 'quality_score': 82.0}
sample_sizes = {'keyword_score': 30, 'quality_score': 50}
results = add_confidence_intervals(scores, sample_sizes)

# Quick formatting
text = format_score_with_confidence(78, 35)
print(text)  # "78 ± 4 points (95% confidence)"
```

#### 4. Semantic Matching

```python
from backend.services.semantic_matcher import SemanticKeywordMatcher, match_resume_to_job

# Quick matching
result = match_resume_to_job(resume_text, job_description)
print(f"Match Rate: {result['match_rate']}%")
print(f"Missing Keywords: {result['missing_keywords']}")

# Detailed matching
matcher = SemanticKeywordMatcher()

# Extract keywords
keywords = matcher.extract_keywords(job_description, top_n=20)

# Match against resume
match_result = matcher.semantic_match_score(resume_text, keywords, threshold=0.7)
print(f"Matched {match_result['matches']} of {match_result['total_keywords']} keywords")
```

---

## Frontend Integration

### TypeScript/React Usage

#### 1. ResumeHeatMap Component

```typescript
import ResumeHeatMap, { extractKeywordsFromScore } from './components/ResumeHeatMap';

function EditorPage() {
  const [resumeText, setResumeText] = useState('');
  const [keywords, setKeywords] = useState<KeywordMatch[]>([]);

  // Fetch heat map data
  const fetchHeatMap = async () => {
    const response = await axios.post('/api/phase2/heat-map', {
      resume_text: resumeText,
      job_description: jobDescription,
      threshold: 0.7
    });

    const keywordMatches = response.data.data.matched_keywords;
    setKeywords(keywordMatches);
  };

  return (
    <div>
      <ResumeHeatMap
        resumeText={resumeText}
        keywords={keywords}
        showHeatMap={true}
        onToggle={(show) => console.log('Heat map toggled:', show)}
      />
    </div>
  );
}
```

#### 2. ATS Compatibility Display

```typescript
interface ATSCompatibilityProps {
  compatibility: ATSCompatibilityResult;
}

function ATSCompatibilityCard({ compatibility }: ATSCompatibilityProps) {
  return (
    <div className="ats-card">
      <h3>ATS Compatibility: {compatibility.overall_score}%</h3>
      <p className="rating">{compatibility.rating}</p>
      <p>{compatibility.summary}</p>

      <div className="platforms">
        {Object.entries(compatibility.platforms).map(([name, data]) => (
          <PlatformBadge
            key={name}
            name={name}
            probability={data.pass_probability}
            rating={data.rating}
          />
        ))}
      </div>

      {compatibility.critical_issues.length > 0 && (
        <div className="critical-issues">
          <h4>Critical Issues:</h4>
          {compatibility.critical_issues.map((issue, idx) => (
            <div key={idx} className="issue">
              <p>{issue.message}</p>
              <p className="recommendation">{issue.recommendation}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
```

#### 3. Skills Breakdown Display

```typescript
function SkillsBreakdown({ skillsAnalysis }) {
  const { hard_skills_analysis, soft_skills_analysis, overall_match } = skillsAnalysis;

  return (
    <div className="skills-breakdown">
      <h3>Skills Match: {overall_match.overall_match_rate}%</h3>

      <div className="skill-category">
        <h4>Hard Skills (Technical): {hard_skills_analysis.match_rate}%</h4>
        <div className="matched">
          <strong>Matched:</strong> {hard_skills_analysis.matched_skills.join(', ')}
        </div>
        {hard_skills_analysis.missing_skills.length > 0 && (
          <div className="missing">
            <strong>Missing:</strong> {hard_skills_analysis.missing_skills.join(', ')}
          </div>
        )}
      </div>

      <div className="skill-category">
        <h4>Soft Skills (Interpersonal): {soft_skills_analysis.match_rate}%</h4>
        <div className="matched">
          <strong>Matched:</strong> {soft_skills_analysis.matched_skills.join(', ')}
        </div>
      </div>
    </div>
  );
}
```

#### 4. Score with Confidence Display

```typescript
function ScoreWithConfidence({ score, confidence }) {
  return (
    <div className="score-confidence">
      <div className="score-main">
        <span className="score-value">{score}</span>
        <span className="score-margin">± {confidence.margin_of_error}</span>
      </div>
      <div className="confidence-details">
        <p className="confidence-text">{confidence.text}</p>
        <p className="confidence-interval">
          Range: [{confidence.confidence_lower}, {confidence.confidence_upper}]
        </p>
        <span className={`reliability ${confidence.reliability.toLowerCase()}`}>
          {confidence.reliability} Reliability
        </span>
      </div>
    </div>
  );
}
```

---

## Testing

### Run All Tests

```bash
cd /Users/sabuj.mondal/ats-resume-scorer/backend
python -m pytest tests/test_phase2_features.py -v
```

### Run Specific Test Suite

```bash
# ATS Simulator tests
python -m pytest tests/test_phase2_features.py::TestATSSimulator -v

# Skills Categorizer tests
python -m pytest tests/test_phase2_features.py::TestSkillsCategorizer -v

# Confidence Scorer tests
python -m pytest tests/test_phase2_features.py::TestConfidenceScorer -v

# Semantic Matcher tests
python -m pytest tests/test_phase2_features.py::TestSemanticMatcher -v
```

### Run with Coverage

```bash
python -m pytest tests/test_phase2_features.py \
  --cov=services \
  --cov-report=html \
  --cov-report=term-missing
```

### Manual API Testing

```bash
# Start backend
uvicorn backend.main:app --reload --port 8000

# Open Swagger UI
open http://localhost:8000/docs

# Navigate to Phase 2 section
# Test endpoints interactively
```

---

## Troubleshooting

### Common Issues

#### 1. sentence-transformers Not Found

**Error:**
```
ModuleNotFoundError: No module named 'sentence_transformers'
```

**Solution:**
```bash
pip install sentence-transformers==2.3.1
```

**Fallback:** System automatically falls back to fuzzy matching if not installed.

#### 2. Model Download Slow

**Issue:** First run downloads ~300MB model

**Solution:** Be patient, model is cached for future use.

**Alternative:** Use fuzzy matching (set `use_semantic=False`)

#### 3. Memory Error with Large Resumes

**Error:**
```
MemoryError: Cannot allocate memory
```

**Solution:**
- Limit resume text to 10,000 words
- Use fuzzy matching instead of semantic
- Increase available RAM

#### 4. Heat Map Not Rendering

**Issue:** Frontend shows blank heat map

**Solution:**
- Check browser console for errors
- Verify keywords array is not empty
- Check API response format

#### 5. API Timeout

**Error:**
```
504 Gateway Timeout
```

**Solution:**
- Increase API timeout
- Optimize resume text size
- Use individual endpoints instead of comprehensive

### Debug Mode

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Performance Monitoring

```python
import time

start = time.time()
result = analyze_ats_compatibility(resume_text)
elapsed = time.time() - start
print(f"Analysis took {elapsed:.2f}s")
```

---

## Configuration

### Environment Variables

```bash
# .env file
ENVIRONMENT=development
CORS_ORIGINS=http://localhost:3000,http://localhost:5173

# Optional: Disable semantic matching to save memory
USE_SEMANTIC_MATCHING=false

# Optional: Set cache directory
CACHE_DIR=/tmp/ats_cache
```

### Service Configuration

```python
# Customize ATS Simulator
simulator = ATSSimulator()
simulator.platforms = ['Taleo', 'Workday', 'Greenhouse', 'iCIMS']

# Customize Skills Categorizer
categorizer = SkillsCategorizer()
# Add custom skills to taxonomy
categorizer.hard_skills_set.add('my_custom_skill')

# Customize Confidence Scorer
scorer = ConfidenceScorer(confidence_level=0.99)  # 99% confidence

# Customize Semantic Matcher
matcher = SemanticKeywordMatcher(
    model_name='all-MiniLM-L6-v2',  # Fast, 80MB
    use_semantic=True
)
```

---

## Performance Tips

1. **Use Comprehensive Analysis Endpoint**
   - Single request for all Phase 2 features
   - Reduces round trips
   - Better performance

2. **Cache Results**
   - ATS simulation results rarely change
   - Cache by resume hash
   - Use diskcache for persistent caching

3. **Batch Processing**
   - Process multiple resumes in background
   - Use async/await for parallel processing

4. **Optimize Resume Text**
   - Remove unnecessary whitespace
   - Limit to essential content
   - Pre-process before sending to API

---

## Quick Reference Table

| Feature | Service | API Endpoint | Response Time |
|---------|---------|--------------|---------------|
| ATS Simulation | `ats_simulator.py` | `/ats-simulation` | ~50ms |
| Skills Categorization | `skills_categorizer.py` | `/skills-analysis` | ~30ms |
| Heat Map Data | `semantic_matcher.py` | `/heat-map` | ~200ms |
| Confidence Intervals | `confidence_scorer.py` | `/confidence-intervals` | ~5ms |
| All Features | All services | `/comprehensive-analysis` | ~365ms |

---

## Support

- **Documentation:** `/docs/PHASE2_IMPLEMENTATION_REPORT.md`
- **Tests:** `/backend/tests/test_phase2_features.py`
- **API Docs:** `http://localhost:8000/docs`
- **Source Code:** `/backend/services/` and `/backend/api/phase2_features.py`

---

**Last Updated:** February 20, 2026
**Version:** 1.0
