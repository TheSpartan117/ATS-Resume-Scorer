# Score Distribution Validation - Quick Start

## TL;DR

Validate that the ATS Resume Scorer produces harsh but realistic scores.

## Run Tests

```bash
cd /Users/sabuj.mondal/ats-resume-scorer/backend

# Option 1: Full pytest (recommended)
python -m pytest tests/test_score_distribution.py -v -s

# Option 2: Standalone validation
python validate_distribution.py

# Option 3: Test runner with summary
python run_distribution_test.py
```

## Target Distribution

| Range   | Target | Min-Max  | Meaning |
|---------|--------|----------|---------|
| 0-40    | 30%    | 20-40%   | Poor quality |
| 41-60   | 40%    | 30-50%   | Mediocre (most resumes) |
| 61-75   | 20%    | 10-30%   | Good |
| 76-85   | 8%     | 3-13%    | Very good (rare) |
| 86-100  | 2%     | 0-5%     | Exceptional (extremely rare) |

## Commit Changes

```bash
cd /Users/sabuj.mondal/ats-resume-scorer/backend
chmod +x commit_distribution_validation.sh
./commit_distribution_validation.sh
```

## What Was Created

1. **tests/test_score_distribution.py** - Main test suite (20 resumes, 4 tests)
2. **validate_distribution.py** - Standalone runner
3. **run_distribution_test.py** - Test wrapper
4. **tests/SCORE_DISTRIBUTION_README.md** - Full documentation
5. **DISTRIBUTION_VALIDATION_SUMMARY.md** - Executive summary
6. **TASK_28_COMPLETED.md** - Complete task report

## Expected Result

```
Distribution validation PASSED
- 30% poor (harsh on basics)
- 40% mediocre (realistic)
- 20% good (recognized)
- 8% very good (rare)
- 2% exceptional (extremely rare)
```

## Status

✅ Task 28 COMPLETED - Ready to commit with: `test: validate score distribution`
