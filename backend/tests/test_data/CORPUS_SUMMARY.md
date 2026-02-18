# Test Resume Corpus - Summary

## Overview
Created 20 realistic test resumes across 5 score tiers (4 resumes per tier) for comprehensive ATS scoring validation.

## Corpus Statistics

### Total Resumes: 20

| Tier | Count | Score Range | Avg Word Count | Avg Skills |
|------|-------|-------------|----------------|------------|
| Outstanding | 4 | 90-100 | 478 | 27 |
| Excellent | 4 | 80-89 | 236 | 15 |
| Good | 4 | 65-79 | 177 | 9 |
| Fair | 4 | 50-64 | 109 | 4 |
| Poor | 4 | 0-49 | 76 | 2 |

## Role Distribution

- Software Engineers: 9 resumes
- Product Managers: 4 resumes
- Data Scientists: 3 resumes
- Analysts: 2 resumes
- Generic roles: 2 resumes

## Experience Levels

- Entry-level: 8 resumes
- Mid-level: 7 resumes
- Senior: 4 resumes
- Lead: 1 resume

## Key Characteristics by Tier

### Outstanding (90-100)
✓ 90%+ role-specific keywords
✓ 95%+ strong action verbs (spearheaded, pioneered, architected)
✓ 70%+ quantified achievements (with numbers and percentages)
✓ Complete contact info (all 6 fields)
✓ 2-3 experience entries with substantial detail
✓ 15-30 technical skills
✓ 1-2 certifications
✓ Education from top institutions
✓ 400-520 words
✓ No red flags

### Excellent (80-89)
✓ 70%+ role keywords
✓ 85%+ action verbs (architected, optimized, led)
✓ 55%+ quantified achievements
✓ Near-complete contact info (5-6 fields)
✓ 2 experience entries
✓ 10-16 technical skills
✓ 1 certification
✓ 220-250 words
✓ 0-1 minor warnings

### Good (65-79)
✓ 50%+ role keywords
✓ 75%+ action verbs (developed, built, implemented)
✓ 45%+ quantified achievements
✓ Basic contact info (4-5 fields, may miss LinkedIn)
✓ 1-2 experience entries
✓ 5-10 skills
✓ May lack certifications
✓ 160-190 words
✓ 2-3 warnings

### Fair (50-64)
⚠ 35%+ role keywords
⚠ 60%+ action verbs (some weak: "worked", "helped")
⚠ 30%+ quantified achievements
⚠ Incomplete contact (missing phone or location)
⚠ 1-2 experience entries with limited detail
⚠ 3-5 generic skills
⚠ No certifications
⚠ 95-125 words
⚠ 1 critical issue + warnings

### Poor (<50)
✗ <30% role keywords
✗ <40% action verbs (mostly passive: "was responsible for")
✗ <15% quantified achievements
✗ Missing critical contact (no email or phone)
✗ Vague experience descriptions
✗ 0-2 generic skills
✗ <100 words or poorly structured
✗ Multiple critical issues (photo, buzzwords, typos)

## Test Coverage

The `test_corpus.py` file provides comprehensive testing:

1. **Structure Validation**
   - Correct file count (20 total, 4 per tier)
   - All files loadable as ResumeData
   - Proper JSON structure

2. **Tier Characteristics**
   - Each tier has expected attributes
   - Contact info completeness by tier
   - Skills count correlates with quality
   - Word count appropriate for tier

3. **Score Distribution**
   - Resumes score within expected ranges
   - Higher tiers consistently outperform lower tiers
   - Scoring system differentiates quality levels

4. **Content Quality**
   - Action verb strength by level
   - Keyword relevance to role
   - Quantification of achievements
   - Red flag detection

## Usage Examples

### Load Specific Tier
```python
from tests.test_corpus import get_all_test_resumes

resumes = get_all_test_resumes()
outstanding = resumes["outstanding"]

for filename, resume_data in outstanding:
    print(f"Resume: {filename}")
    print(f"Name: {resume_data.contact['name']}")
    print(f"Skills: {len(resume_data.skills)}")
```

### Score All Resumes
```python
from tests.test_corpus import get_all_test_resumes
from backend.services.scorer import calculate_overall_score

resumes = get_all_test_resumes()

for tier, tier_resumes in resumes.items():
    print(f"\n{tier.upper()}:")
    for filename, resume in tier_resumes:
        result = calculate_overall_score(resume, "", "software_engineer", "mid")
        print(f"  {filename}: {result['overallScore']:.1f}")
```

### Validate Corpus
```python
from tests.test_corpus import validate_corpus_structure

is_valid, issues = validate_corpus_structure()
if is_valid:
    print("✓ Corpus is valid")
else:
    for issue in issues:
        print(f"✗ {issue}")
```

## Files Created

### Resume Files (20)
- `outstanding_01_senior_swe.json` through `outstanding_04_lead_eng.json`
- `excellent_01_mid_swe.json` through `excellent_04_senior_eng.json`
- `good_01_entry_swe.json` through `good_04_mid_eng.json`
- `fair_01_entry_swe.json` through `fair_04_mid_dev.json`
- `poor_01_entry.json` through `poor_04_entry.json`

### Test Files
- `test_corpus.py` - Comprehensive test suite with 12 test functions
- `README.md` - Detailed documentation of corpus structure

### Documentation
- `CORPUS_SUMMARY.md` - This file

## Design Philosophy

Each resume was carefully crafted to:

1. **Be Realistic** - Based on real-world resume patterns
2. **Test Specific Features** - Each tier tests different scoring aspects
3. **Show Clear Progression** - Quality decreases systematically across tiers
4. **Cover Multiple Roles** - Software, Product, Data, etc.
5. **Include Edge Cases** - Missing fields, red flags, extreme lengths
6. **Enable Validation** - Provides ground truth for scoring system

## Red Flags Included

The corpus includes various red flags to test detection:

- **Missing Contact Info**: Poor tier missing email/phone
- **Photo in Resume**: poor_01 and poor_03 have photos
- **Buzzwords**: poor_02 uses "team player", "hard worker"
- **Passive Voice**: Poor/Fair tiers use "was responsible for"
- **Vague Content**: Fair/Poor lack specifics
- **Wrong Length**: poor_03 has 3 pages (too long)
- **Typos/Formatting**: Poor tier has inconsistent formatting

## Quantification Examples

### Outstanding Tier
- "reducing deployment time by 75%"
- "processing 50TB+ data daily"
- "Mentored team of 8 engineers"
- "increasing code coverage from 45% to 95%"

### Excellent Tier
- "serving 500K+ daily requests"
- "reducing response time by 35%"
- "Mentored 2 junior developers"

### Good Tier
- Some numbers present but less consistent
- "Built REST APIs serving requests"

### Fair/Poor Tier
- Minimal to no quantification
- "Did programming work"
- "Worked on projects"

## Maintenance Guidelines

When updating the corpus:

1. **Maintain Balance**: Keep 4 resumes per tier
2. **Update Together**: If scoring changes, review all tiers
3. **Document Changes**: Update this summary and README
4. **Test Thoroughly**: Run full test suite after changes
5. **Keep Realistic**: Base on actual resume patterns
6. **Version Control**: Commit changes with clear descriptions

## Testing Workflow

```bash
# 1. Validate structure
pytest tests/test_corpus.py::test_corpus_structure -v

# 2. Check tier characteristics
pytest tests/test_corpus.py -k "characteristics" -v

# 3. Verify score distribution
pytest tests/test_corpus.py::test_score_distribution_by_tier -v -s

# 4. Run all corpus tests
pytest tests/test_corpus.py -v

# 5. Run with coverage
pytest tests/test_corpus.py --cov=services --cov-report=term-missing
```

## Next Steps

This corpus enables:

1. **Regression Testing**: Ensure scoring changes don't break expectations
2. **Benchmarking**: Compare scoring algorithm versions
3. **Validation**: Verify new features work across quality levels
4. **Documentation**: Demonstrate system capabilities
5. **Training**: Help understand what makes a good resume

## Version

- **Created**: 2026-02-19
- **Version**: 1.0
- **Total Resumes**: 20
- **Test Functions**: 12
- **Coverage**: All major scoring dimensions
