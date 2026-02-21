# P6.3: Word Repetition Penalty (-5 points max)

## Overview
Penalizes poor vocabulary diversity when action verbs are overused in resume bullets.

## Scoring Structure

### Penalty Rules
- **Each verb used 3+ times**: -1 point
- **Maximum penalty**: -5 points
- **Threshold**: 3+ uses triggers penalty (2 uses or less is OK)

### Examples

#### No Penalty (0 pts)
```
✓ Led team of 10 engineers
✓ Developed scalable API
✓ Implemented CI/CD pipeline
✓ Architected cloud infrastructure
```
All unique verbs = 0 penalty

#### -1 Point Penalty
```
✗ Developed feature A
✗ Developed feature B
✗ Developed feature C
✓ Implemented feature D
```
"Developed" used 3 times = -1 pt

#### -3 Points Penalty
```
✗ Developed feature A (3x)
✗ Developed feature B
✗ Developed feature C
✗ Implemented feature D (3x)
✗ Implemented feature E
✗ Implemented feature F
✗ Built feature G (3x)
✗ Built feature H
✗ Built feature I
```
3 different verbs repeated = -3 pts

#### Capped at -5 Points
```
6+ different verbs each used 3+ times
```
Even with 10 repeated verbs, penalty capped at -5 pts

## Research Basis

### Career Coach Recommendations
- Maximum 2 uses of same verb per resume
- Vocabulary diversity demonstrates strong writing skills
- Repetition signals lazy or rushed writing

### ATS Systems
- Flag keyword stuffing when same term repeated 3+ times
- May penalize or reject resumes with excessive repetition
- Modern ATS detects unnatural language patterns

### Hiring Manager Perception
- Notice and negatively judge repetitive writing
- Prefer varied, dynamic language
- Repetition suggests limited vocabulary or experience

## Implementation Details

### Technology
Uses `RepetitionDetector` from `backend/services/repetition_detector.py`:
- Extracts action verbs from bullet points (first meaningful word)
- Counts occurrences (case-insensitive)
- Ignores common words (the, a, and, etc.)
- Sorts by count (most repeated first)

### Configuration
```python
RepetitionDetector(
    repetition_threshold=3,  # Penalty at 3+ uses
    max_penalty=5           # Cap at -5 pts
)
```

### Result Structure
```python
{
    'penalty': int,              # 0 to -5
    'repeated_verbs': [str],     # List of problematic verbs
    'repetition_details': [      # Full details
        {
            'word': str,
            'count': int,
            'penalty': -1
        }
    ]
}
```

## Usage

### Basic Usage
```python
from backend.services.parameters.p6_3_repetition import RepetitionPenaltyScorer

scorer = RepetitionPenaltyScorer()
bullets = [
    "Developed feature A",
    "Developed feature B",
    "Developed feature C"
]

result = scorer.score(bullets)
# {
#     'penalty': -1,
#     'repeated_verbs': ['developed'],
#     'repetition_details': [
#         {'word': 'developed', 'count': 3, 'penalty': -1}
#     ]
# }
```

### Convenience Function
```python
from backend.services.parameters.p6_3_repetition import score_repetition_penalty

result = score_repetition_penalty(bullets)
```

## Testing

Comprehensive test suite in `backend/tests/services/parameters/test_p6_3_repetition.py`:

- ✓ No repetition (0 penalty)
- ✓ Verb used 2 times (below threshold, 0 penalty)
- ✓ Verb used 3 times (-1 pt)
- ✓ Multiple verbs repeated
- ✓ Cap at -5 pts (6+ repeated verbs)
- ✓ Case insensitivity
- ✓ Edge cases (bullets with markers, whitespace, etc.)
- ✓ Integration with RepetitionDetector

## Best Practices

### For Resume Writers
1. Use varied action verbs throughout resume
2. Limit each verb to 2 uses maximum
3. Consult thesaurus for alternatives
4. Review bullet points for repetition before submitting

### For Developers
1. RepetitionDetector is reusable foundation component
2. Threshold and max_penalty are configurable
3. Case-insensitive matching prevents evasion
4. Sorted results show worst offenders first

## Related Components
- `backend/services/repetition_detector.py` - Foundation detector
- `backend/services/parameters/p2_1_action_verbs.py` - Action verb quality scoring
- Task 6 - Original RepetitionDetector implementation
