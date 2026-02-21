# P5.3: Experience Depth (2 points)

## Overview
Validates that resume has sufficient detailed experience entries appropriate for the candidate's experience level. Ensures credibility and completeness of work history.

## Scoring Logic

### Level-Specific Minimums
- **Beginner** (0-3 years): ≥2 detailed entries = 2 points
- **Intermediary** (3-7 years): ≥3 detailed entries = 2 points
- **Senior** (7+ years): ≥4 detailed entries = 2 points

### Scoring
- **Meets minimum**: 2 points
- **Below minimum**: 0 points

## Entry Requirements
Each experience entry must include ALL of the following:
1. **Company name** (non-empty)
2. **Job title** (non-empty)
3. **Dates** (both start and end date, non-empty)
4. **Content** (achievements/bullets OR description, at least one)

## Implementation Details

### Complete Entry Validation
```python
def _is_complete_entry(self, entry: Dict) -> bool:
    # Must have title (non-empty string)
    # Must have company (non-empty string)
    # Must have startDate and endDate (both non-empty)
    # Must have achievements (non-empty list) OR description (non-empty string)
```

### Edge Cases Handled
1. **Empty/None experiences**: Returns 0 points with appropriate feedback
2. **Whitespace-only fields**: Treated as missing (uses `.strip()`)
3. **Empty strings**: Treated as missing
4. **Missing fields**: Entry doesn't count as complete
5. **Partial dates**: Both start and end required
6. **Empty bullets list**: Must have description if no bullets
7. **Case-insensitive levels**: Level parameter normalized to lowercase
8. **Unknown levels**: Defaults to intermediary (3 entries minimum)

## Research Basis
- **TopResume**: Detailed experience entries demonstrate depth and credibility
- **ResumeWorded**: ATS systems prioritize resumes with complete work history
- **Career Experts**: Level-appropriate depth prevents gaps and builds trust
- **LinkedIn**: Complete profiles with detailed work history receive 40% more opportunities

## Usage Example

```python
from backend.services.parameters.p5_3_experience_depth import score_experience_depth

experiences = [
    {
        'title': 'Software Engineer',
        'company': 'Tech Corp',
        'startDate': 'Jan 2020',
        'endDate': 'Dec 2021',
        'achievements': ['Built API', 'Led team']
    },
    {
        'title': 'Junior Developer',
        'company': 'Startup Inc',
        'startDate': 'Jun 2018',
        'endDate': 'Dec 2019',
        'description': 'Developed web applications'
    }
]

result = score_experience_depth(experiences, 'beginner')
print(f"Score: {result['score']}/2")
print(f"Entries: {result['entry_count']}")
print(f"Meets minimum: {result['meets_minimum']}")
```

## Return Structure

```python
{
    'score': int,           # 0 or 2
    'max_score': int,       # Always 2
    'entry_count': int,     # Number of complete entries found
    'level': str,           # Experience level used
    'meets_minimum': bool,  # Whether minimum was met
    'details': str          # Detailed feedback
}
```

## Test Coverage
- ✅ Beginner level (2 entries minimum)
- ✅ Intermediary level (3 entries minimum)
- ✅ Senior level (4 entries minimum)
- ✅ Missing company field
- ✅ Missing title field
- ✅ Missing dates (start, end, or both)
- ✅ Missing content (no bullets/description)
- ✅ Empty bullets list
- ✅ Description without bullets (valid)
- ✅ Bullets without description (valid)
- ✅ Empty experience list
- ✅ None experience list
- ✅ Whitespace-only fields
- ✅ Empty string fields
- ✅ Case-insensitive level
- ✅ Unknown level defaults
- ✅ Mixed complete/incomplete entries
- ✅ Boundary conditions (exactly at minimum)

## Files
- **Implementation**: `backend/services/parameters/p5_3_experience_depth.py`
- **Tests**: `backend/tests/services/parameters/test_p5_3_experience_depth.py`
- **Validation**: `backend/validate_p5_3.py`

## Integration Notes
This parameter should be integrated into:
1. Overall scoring system
2. Parameter registry (when P5 category is added)
3. Resume scoring API endpoints
4. Feedback generation system

The scorer accepts the standard `experience` field from parsed resume data, making integration straightforward with existing resume parsing pipeline.
