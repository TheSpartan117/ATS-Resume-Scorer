# Test Resume Corpus

This directory contains 20 test resumes across 5 score tiers for validating the ATS scoring system.

## Structure

The corpus consists of 20 realistic resumes (4 per tier) designed to test different scoring scenarios:

### Outstanding Tier (90-100 points)
- `outstanding_01_senior_swe.json` - Senior Software Engineer
- `outstanding_02_senior_pm.json` - Senior Product Manager
- `outstanding_03_senior_ds.json` - Senior Data Scientist
- `outstanding_04_lead_eng.json` - Engineering Lead

**Characteristics:**
- 90%+ keyword match for role
- 95%+ action verbs (strong, level-appropriate)
- 70%+ quantified achievements
- Complete contact information
- No critical issues or red flags
- 400-520 word count
- Well-structured content

### Excellent Tier (80-89 points)
- `excellent_01_mid_swe.json` - Mid-level Software Engineer
- `excellent_02_mid_pm.json` - Mid-level Product Manager
- `excellent_03_mid_ds.json` - Mid-level Data Scientist
- `excellent_04_senior_eng.json` - Senior Software Engineer

**Characteristics:**
- 70%+ keyword match
- 85%+ action verbs
- 55%+ quantified achievements
- Complete contact info (may miss 1-2 optional fields)
- 0-1 warnings, no critical issues
- 220-250 word count
- Good structure

### Good Tier (65-79 points)
- `good_01_entry_swe.json` - Entry-level Software Developer
- `good_02_mid_pm.json` - Mid-level Product Manager
- `good_03_entry_ds.json` - Entry-level Data Analyst
- `good_04_mid_eng.json` - Mid-level Software Engineer

**Characteristics:**
- 50%+ keyword match
- 75%+ action verbs
- 45%+ quantified achievements
- Basic contact info (may miss LinkedIn/website)
- 2-3 warnings
- 160-190 word count
- Adequate structure

### Fair Tier (50-64 points)
- `fair_01_entry_swe.json` - Entry-level Developer
- `fair_02_entry_pm.json` - Entry-level Product Coordinator
- `fair_03_entry_analyst.json` - Entry-level Data Analyst
- `fair_04_mid_dev.json` - Mid-level Developer

**Characteristics:**
- 35%+ keyword match
- 60%+ action verbs
- 30%+ quantified achievements
- Incomplete contact info (missing phone or location)
- 1 critical issue + multiple warnings
- 95-125 word count
- Weak structure

### Poor Tier (<50 points)
- `poor_01_entry.json` - Entry-level (multiple critical issues)
- `poor_02_entry.json` - Entry-level (buzzwords, vague content)
- `poor_03_mid.json` - Mid-level (long, has photo, weak content)
- `poor_04_entry.json` - Entry-level (minimal info, no structure)

**Characteristics:**
- <30% keyword match
- <40% action verbs
- <15% quantified achievements
- Missing critical contact info (email or phone)
- Multiple critical issues and red flags
- <100 word count or excessively long
- Poor/no structure
- May include red flags (photo, buzzwords, typos)

## Usage

### Load All Resumes
```python
from tests.test_corpus import get_all_test_resumes

resumes_by_tier = get_all_test_resumes()
# Returns dict with tier names as keys, list of (filename, ResumeData) tuples as values
```

### Validate Corpus Structure
```python
from tests.test_corpus import validate_corpus_structure

is_valid, issues = validate_corpus_structure()
```

### Run Tests
```bash
# Run all corpus tests
pytest tests/test_corpus.py -v

# Run specific test
pytest tests/test_corpus.py::test_score_distribution_by_tier -v

# Run with output
pytest tests/test_corpus.py::test_score_distribution_by_tier -v -s
```

## Test Coverage

The test suite (`test_corpus.py`) validates:

1. **Structure Tests**
   - 20 total resumes
   - 4 resumes per tier
   - All files loadable as ResumeData

2. **Tier Characteristic Tests**
   - Outstanding: complete info, many skills, quantified achievements
   - Excellent: strong content, minor gaps
   - Good: adequate content, some weaknesses
   - Fair: incomplete info, weak content
   - Poor: critical issues, major gaps

3. **Distribution Tests**
   - Score distribution matches expected tiers
   - Keyword variety correlates with tier
   - Word count appropriate for tier
   - Contact completeness decreases with tier

4. **Validation Tests**
   - Higher tiers have more skills
   - Higher tiers have better contact info
   - Content quality correlates with tier

## Resume Design Principles

Each resume was designed to test specific aspects of the scoring system:

- **Keywords**: Match to role taxonomy definitions
- **Action Verbs**: Level-appropriate (entry vs senior)
- **Metrics**: Quantified achievements with numbers
- **Structure**: Section organization and clarity
- **Contact Info**: Completeness and correctness
- **Red Flags**: Photo, buzzwords, typos, excessive length
- **Content Quality**: Specificity vs vagueness

## Maintenance

When updating the corpus:

1. Maintain 20 total resumes (4 per tier)
2. Ensure tier characteristics remain distinct
3. Update README if adding new test scenarios
4. Run `pytest tests/test_corpus.py` to validate
5. Keep resumes realistic and representative

## File Format

All resumes are JSON files matching the ResumeData schema:

```json
{
  "fileName": "resume_name.json",
  "contact": {
    "name": "Full Name",
    "email": "email@example.com",
    "phone": "(555) 555-0123",
    "location": "City, State",
    "linkedin": "linkedin.com/in/username",
    "website": "github.com/username"
  },
  "experience": [...],
  "education": [...],
  "skills": [...],
  "certifications": [...],
  "metadata": {
    "pageCount": 1,
    "wordCount": 250,
    "hasPhoto": false,
    "fileFormat": "json"
  }
}
```
