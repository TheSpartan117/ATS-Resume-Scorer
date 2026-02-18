# Main Scorer Orchestrator Implementation

## Overview
Implemented the Main Scorer Orchestrator (`ResumeScorer` class) in `services/scorer_v2.py` as part of Task 18 of the ATS Resume Scorer redesign.

## Features Implemented

### 1. Dual-Mode Support
- **ATS Mode**: Simulates ATS keyword matching (70/20/10 scoring)
  - Keyword Match: 70 points (50 required + 20 preferred)
  - Format Check: 20 points
  - Structure: 10 points

- **Quality Mode**: Balanced quality scoring (25/30/25/20)
  - Role Keywords: 25 points
  - Content Quality: 30 points
  - Format: 25 points
  - Professional Polish: 20 points

### 2. Score Interpretation Layer
Human-readable interpretations for score ranges:
- **86-100**: Excellent
- **76-85**: Very good
- **61-75**: Good
- **41-60**: Needs improvement
- **0-40**: Needs significant improvement

### 3. Actionable Recommendations
The orchestrator generates up to 7 actionable recommendations based on:
- Critical issues (highest priority)
- Warnings (top 3)
- Mode-specific guidance based on breakdown scores
- Suggestions from detailed analysis

Recommendation types:
- **CRITICAL**: High-priority issues requiring immediate attention
- **WARNING**: Important issues to address
- **TIP**: Suggestions for improvement

### 4. Caching Support
Validator results can be cached for quick mode switching:
- `cache_validation_results(hash, data)`: Store validation results
- `get_cached_validation(hash)`: Retrieve cached results
- `clear_cache()`: Clear all cached data

This allows users to switch between ATS and Quality modes without re-running expensive validations.

### 5. Comprehensive Return Structure
```python
{
    'score': 75.0,                    # Overall score (0-100)
    'mode': 'ats',                    # Mode used ('ats' or 'quality')
    'interpretation': 'Good',         # Human-readable interpretation
    'breakdown': {                    # Detailed scoring breakdown
        'keyword_match': {
            'score': 52.5,
            'maxScore': 70,
            'issues': [...]
        },
        ...
    },
    'recommendations': [              # Actionable recommendations (max 7)
        "Add 2 missing required keywords to improve ATS compatibility",
        "Include 3 more preferred keywords to stand out",
        ...
    ],
    'issues': {                       # Categorized issues
        'critical': [],
        'warnings': [],
        'suggestions': [],
        'info': []
    },
    'strengths': [                    # Identified strengths
        "Strong keyword match with required skills",
        "ATS-compatible format"
    ],
    'keyword_details': {              # Keyword matching details
        'required_matched': 4,
        'required_total': 5,
        'required_match_pct': 80.0,
        ...
    },
    # Mode-specific fields
    'auto_reject': False,             # ATS mode only
    'rejection_reason': None,         # ATS mode only
    'cta': 'Your resume is good...'  # Quality mode only
}
```

## API Usage

### Basic Usage

```python
from services.scorer_v2 import ResumeScorer
from services.parser import ResumeData
from services.role_taxonomy import ExperienceLevel

# Initialize scorer
scorer = ResumeScorer()

# Score in ATS mode (requires job description)
result = scorer.score(
    resume=resume_data,
    role="software_engineer",
    level=ExperienceLevel.SENIOR,
    mode='ats',
    job_description="Required: Python, AWS..."
)

# Score in Quality mode (no job description needed)
result = scorer.score(
    resume=resume_data,
    role="software_engineer",
    level=ExperienceLevel.SENIOR,
    mode='quality'
)
```

### Using Cache for Mode Switching

```python
# Cache validator results
resume_hash = "abc123"  # Generate from resume content
scorer.cache_validation_results(resume_hash, validation_data)

# Switch modes quickly without re-validation
ats_result = scorer.score(resume, role, level, mode='ats', job_description=jd)
quality_result = scorer.score(resume, role, level, mode='quality')

# Clear cache when done
scorer.clear_cache()
```

## Implementation Details

### Class: ResumeScorer

The main orchestrator class that coordinates scoring operations.

**Methods:**
- `score()`: Main entry point for scoring
- `_interpret_score()`: Convert numeric score to interpretation
- `_generate_recommendations()`: Generate actionable recommendations
- `cache_validation_results()`: Cache validator results
- `get_cached_validation()`: Retrieve cached results
- `clear_cache()`: Clear all cached data

### Integration with AdaptiveScorer

`ResumeScorer` wraps the existing `AdaptiveScorer` class and adds:
- Simplified API (mode parameter instead of auto-detection)
- Interpretation layer
- Enhanced recommendations system
- Caching support
- Standardized return structure

## Testing

Comprehensive test suite in `tests/test_scorer_v2.py`:

### Test Coverage:
1. **Dual-mode functionality**
   - `test_resume_scorer_ats_mode()`: Verify ATS mode
   - `test_resume_scorer_quality_mode()`: Verify Quality mode
   - `test_mode_switching_seamless()`: Test mode switching

2. **Score interpretation**
   - `test_score_interpretation_ranges()`: Verify all score ranges

3. **Recommendations**
   - `test_recommendations_generated()`: Verify recommendations exist
   - `test_recommendations_actionable()`: Verify recommendation quality

4. **Error handling**
   - `test_ats_mode_requires_job_description()`: Verify validation
   - `test_invalid_mode_raises_error()`: Verify mode validation

5. **Caching**
   - `test_cache_functionality()`: Verify cache operations

6. **Return structure**
   - `test_breakdown_structure_ats()`: Verify ATS breakdown
   - `test_breakdown_structure_quality()`: Verify Quality breakdown
   - `test_issues_categorized()`: Verify issue categorization
   - `test_strengths_identified()`: Verify strength identification

### Running Tests

```bash
# Run all scorer_v2 tests
python -m pytest tests/test_scorer_v2.py -v

# Run specific test
python -m pytest tests/test_scorer_v2.py::test_resume_scorer_ats_mode -v

# Run with coverage
python -m pytest tests/test_scorer_v2.py --cov=services.scorer_v2
```

## Design Decisions

### 1. Wrapper Pattern
Used wrapper pattern (ResumeScorer wraps AdaptiveScorer) to:
- Maintain backward compatibility with existing AdaptiveScorer
- Add new features without modifying core logic
- Provide cleaner API for end users

### 2. Mode Parameter
Changed from auto-detection to explicit mode parameter:
- More predictable behavior
- Clearer API
- Easier to test

### 3. Recommendation Generation
Algorithm prioritizes:
1. Critical issues (always shown)
2. Top 3 warnings
3. Mode-specific recommendations based on scores
4. Suggestions (if space available)
5. Generic positive message (if no issues)

Capped at 7 recommendations to avoid overwhelming users.

### 4. Caching Strategy
Simple in-memory cache with hash-based keys:
- Fast access for mode switching
- Minimal memory overhead
- Can be extended to persistent storage if needed

## Future Enhancements

Potential improvements for future iterations:

1. **Persistent Cache**: Redis or database-backed cache
2. **Weighted Recommendations**: Prioritize by impact/effort ratio
3. **Custom Score Ranges**: Allow configuration of interpretation thresholds
4. **Multi-language Support**: Internationalized interpretations
5. **Historical Tracking**: Track score improvements over time
6. **Validator Integration**: Direct integration with RedFlagsValidator
7. **Batch Scoring**: Score multiple resumes efficiently
8. **A/B Testing**: Different recommendation strategies

## Dependencies

- `backend.services.keyword_extractor`: Keyword extraction and matching
- `backend.services.role_taxonomy`: Role-specific data and ExperienceLevel
- `backend.services.parser`: ResumeData model

## File Structure

```
backend/
├── services/
│   └── scorer_v2.py              # Main implementation
├── tests/
│   └── test_scorer_v2.py         # Comprehensive test suite
└── SCORER_V2_IMPLEMENTATION.md   # This documentation
```

## Commit Message

```
feat: implement main scorer orchestrator

- Add ResumeScorer class with dual-mode support (ATS/Quality)
- Implement score interpretation layer (5 ranges)
- Generate actionable recommendations based on issues
- Add caching support for quick mode switching
- Comprehensive test suite with 15+ tests
- Support job description matching in ATS mode
- Standardized return structure with breakdown and recommendations

Features:
- Score interpretation: 0-40 (Needs significant improvement) to 86-100 (Excellent)
- Up to 7 prioritized recommendations (Critical > Warning > Tips)
- Cache validator results for seamless mode switching
- Detailed breakdown from both scoring modes
- Categorized issues: critical, warnings, suggestions, info
```
