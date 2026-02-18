# Score Distribution Validation

## Overview

This test suite validates that the ATS Resume Scorer produces a **harsh but realistic** distribution of scores across diverse resume samples. The goal is to ensure the scoring system is properly calibrated to reflect real-world ATS behavior.

## Target Distribution

The scoring system aims for the following distribution:

| Score Range | Target % | Tolerance | Interpretation |
|-------------|----------|-----------|----------------|
| 0-40        | 30%      | ± 10%     | Poor quality resumes (harsh on missing basics) |
| 41-60       | 40%      | ± 10%     | Mediocre resumes (most resumes fall here) |
| 61-75       | 20%      | ± 10%     | Good resumes (solid but not exceptional) |
| 76-85       | 8%       | ± 5%      | Very good resumes (rare) |
| 86-100      | 2%       | ± 3%      | Exceptional resumes (extremely rare) |

## Test Resumes

The test suite includes **20 carefully crafted resumes** that span the full quality spectrum:

### Poor Quality (6 resumes - ~30%)
1. **Empty Resume** - No content at all
2. **Minimal Resume** - Barely any information, has photo
3. **Too Long Resume** - 5 pages, too verbose
4. **No Contact Info** - Missing critical contact details
5. **Passive Voice Heavy** - Weak language throughout
6. **No Quantification** - No metrics or achievements

### Mediocre Quality (8 resumes - ~40%)
7. **Basic Junior Developer** - Entry-level with minimal experience
8. **Average Mid-level** - Standard mid-level with some metrics
9. **Incomplete Experience** - Missing important details
10. **Decent but Brief** - Good but lacking depth
11. **Missing Keywords** - Poor keyword optimization
12. **Weak Action Verbs** - Uses passive constructions
13. **Limited Scope** - Narrow experience range
14. **Generic Content** - Lacks specificity

### Good Quality (4 resumes - ~20%)
15. **Good Mid-level Engineer** - Strong experience with metrics
16. **Strong Junior with Portfolio** - Excellent for entry-level
17. **Solid Senior Track** - Senior-level with leadership
18. **Well-Rounded Professional** - Balanced and complete

### Very Good Quality (2 resumes - ~8%)
19. **Excellent Senior Engineer** - Outstanding achievements
20. **Strong Staff Engineer Track** - Exceptional leadership and impact

### Exceptional Quality (0 resumes - ~2%)
- No resumes in this category by design
- Exceptional scores (86-100) should be extremely rare

## Running the Tests

### Option 1: Run with pytest (Recommended)

```bash
cd backend
python -m pytest tests/test_score_distribution.py -v -s
```

This will run all 4 test functions:
- `test_score_all_resumes_legacy_scorer()` - Tests scorer_legacy.py
- `test_score_all_resumes_adaptive_scorer_quality_mode()` - Tests scorer_v2.py (Quality Coach)
- `test_score_all_resumes_adaptive_scorer_ats_mode()` - Tests scorer_v2.py (ATS Simulation)
- `test_score_distribution_comparison()` - Compares both scorers

### Option 2: Run standalone script

```bash
cd backend
python validate_distribution.py
```

This runs a simplified version that reports distributions without pytest assertions.

### Option 3: Run via dedicated runner

```bash
cd backend
python run_distribution_test.py
```

This runs all tests and generates a comprehensive report.

## What the Tests Validate

### 1. Score Range Validation
- All scores must be between 0 and 100
- No negative scores or scores exceeding maximum

### 2. Distribution Validation
Each score range is validated against targets:
- **0-40**: Should be 20-40% (harsh on poor quality)
- **41-60**: Should be 30-50% (most resumes are mediocre)
- **61-75**: Should be 10-30% (good resumes are less common)
- **76-85**: Should be 3-13% (very good resumes are rare)
- **86-100**: Should be 0-5% (exceptional resumes are extremely rare)

### 3. Scorer Consistency
- Legacy scorer (scorer_legacy.py) and Adaptive scorer (scorer_v2.py) should produce similar distributions
- Quality Coach mode should be more generous than ATS Simulation mode
- Both modes should still maintain harsh but realistic standards

### 4. Auto-Reject Logic (ATS Mode)
- Resumes with <60% required keyword match should be auto-rejected
- Auto-reject rate should be significant for poor resumes

## Understanding the Results

### Example Output

```
LEGACY SCORER - DISTRIBUTION REPORT
================================================================================
Total resumes scored: 20
Average score: 52.3
Min score: 18.5
Max score: 82.7

Score Distribution:
  0-40:   30.0% (target: 30% ± 10%, range: 20-40%)   [PASS]
  41-60:  40.0% (target: 40% ± 10%, range: 30-50%)   [PASS]
  61-75:  20.0% (target: 20% ± 10%, range: 10-30%)   [PASS]
  76-85:  10.0% (target: 8% ± 5%, range: 3-13%)      [PASS]
  86-100: 0.0%  (target: 2% ± 3%, range: 0-5%)       [PASS]
```

### Interpretation

- **Average score ~50-55**: Indicates harsh but realistic scoring
- **30% below 40**: System is properly harsh on poor quality
- **40% in mediocre range**: Most resumes are average (realistic)
- **Few scores above 75**: Excellence is rare (as it should be)
- **Almost no 86-100 scores**: Exceptional is extremely rare (correct)

## Calibration Guidelines

If tests fail, the scoring system may need adjustment:

### If scores are too high (distribution shifts right):
- Average score > 60: System is too lenient
- Too many scores > 75: Not harsh enough on quality
- Multiple 86+ scores: Exceptional should be extremely rare

**Fix**: Increase scoring thresholds or reduce point values

### If scores are too low (distribution shifts left):
- Average score < 45: System is unrealistically harsh
- >50% below 40: Too many resumes rejected
- No scores above 70: System doesn't recognize quality

**Fix**: Decrease scoring thresholds or increase point values

## Integration with CI/CD

Add to your CI pipeline to ensure scoring remains calibrated:

```yaml
# .github/workflows/test.yml
- name: Validate Score Distribution
  run: |
    cd backend
    python -m pytest tests/test_score_distribution.py -v
```

## Maintenance

When modifying scoring logic:
1. Run distribution tests before changes
2. Make scoring adjustments
3. Run distribution tests after changes
4. Compare distributions to ensure changes had intended effect
5. Update test resumes if new edge cases discovered

## Philosophy

This scoring system follows the principle:

> "Harsh but realistic - Most resumes are mediocre, good resumes are uncommon, and exceptional resumes are rare."

The goal is not to make candidates feel good, but to accurately simulate real-world ATS systems that are:
- Strict about formatting and structure
- Heavily keyword-driven (in ATS mode)
- Quality-focused but still demanding (in Quality Coach mode)
- Realistic about what constitutes excellence

## Contact

For questions about score distribution validation, contact the ATS Resume Scorer development team.
