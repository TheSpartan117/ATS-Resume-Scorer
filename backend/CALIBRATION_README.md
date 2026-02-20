# Quality Coach Calibration System

**Purpose**: Tools and documentation for calibrating the Quality Coach scoring system to achieve ±3 point accuracy with ResumeWorded.

---

## Quick Links

- 📊 **Run Calibration**: `python3 calibrate_quality_scorer.py --mode initial`
- 📖 **Quick Start Guide**: `../docs/calibration-quick-start.md`
- 📋 **Results Tracking**: `../docs/calibration-results.md`
- 🚀 **Deployment Guide**: `../docs/deployment-guide.md`
- 📈 **Status Tracker**: `../docs/quality-coach-recalibration-status.md`

---

## Overview

The calibration system tests the Quality Coach scorer against known benchmarks and provides tuning recommendations to achieve target accuracy.

**Target Accuracy**:
- ±3 points on 90% of CVs
- ±5 points on 100% of CVs

**Calibration Process**:
1. Test 3 known CVs (Sabuj=86, Aishik=80, Swastik=65)
2. Tune weights based on results
3. Expand to 30 diverse CVs
4. Fine-tune until target met
5. Document final configuration

---

## Files in This Directory

### Calibration Script
- `calibrate_quality_scorer.py` - Main calibration test script

### Test Data
- `data/Sabuj_Mondal_PM_CV_1771577761468.docx` - Baseline CV (86 pts)
- `data/SWASTIK PAUL_CV_DIG_TRSFN STGY_PM-2_*.docx` - Baseline CV (65 pts)
- `data/calibration_corpus/` - (To be created) 30-CV test corpus

### Pattern Data
- `data/patterns/action_verb_tiers.json` - Verb strength classification
- `data/patterns/weak_phrases.json` - Weak phrase library
- `data/patterns/metric_patterns.json` - Metric detection patterns
- `data/patterns/generic_to_specific.json` - Technology specificity mappings

---

## Usage

### Test 3 Known CVs (Task 16)

```bash
python3 calibrate_quality_scorer.py --mode initial
```

**Expected Output**:
```
==================================================
Testing: Sabuj Mondal
Expected Score: 86
==================================================

✅ Actual Score: 84/100
   Delta: -2.0 points (EXCELLENT ±3)

==================================================
CALIBRATION SUMMARY
==================================================
Tested: 3 CVs
Within ±3 points: 3/3 (100%)
✅ TARGET MET
```

---

### Test Single CV

```bash
python3 calibrate_quality_scorer.py \
    --mode single \
    --cv path/to/cv.docx \
    --expected 75 \
    --role product_manager \
    --level mid
```

**Use Cases**:
- Debug specific CV scoring
- Test edge cases
- Validate individual CVs

---

### Test 30 CVs (Task 17)

```bash
# First, create corpus manifest (see Quick Start Guide)
# Then run:
python3 calibrate_quality_scorer.py \
    --mode full \
    --manifest data/calibration_corpus/manifest.json \
    --output results/calibration_full.json
```

**Output**:
- Console: Summary statistics
- JSON file: Detailed results for analysis

---

## Understanding Results

### Accuracy Status Classification

| Status | Range | Meaning | Action |
|--------|-------|---------|--------|
| **EXCELLENT ±3** | ≤3 pts | Perfect match | None needed |
| **GOOD ±5** | 3-5 pts | Close match | Minor tuning |
| **ACCEPTABLE ±8** | 5-8 pts | Reasonable | Moderate tuning |
| **NEEDS TUNING >8** | >8 pts | Poor match | Significant tuning |

---

### Score Breakdown

Each test shows component scores:

```
Score Breakdown:
  - achievement_strength: 13.0/15 pts  # CAR structure quality
  - sentence_clarity: 8.5/10 pts       # Length, weak phrases, voice
  - specificity: 4.0/5 pts              # Tech, metrics, actions
  - keywords_fit: 20.0/25 pts           # Role-specific keywords
  - format: 23.0/25 pts                 # ATS compatibility
  - polish: 18.0/20 pts                 # Grammar, variety, structure
```

**Use for Tuning**:
- If achievement_strength consistently low → increase CAR bonus
- If all scores high but total low → check weight distribution
- If polish consistently high → increase grammar penalties

---

### Tuning Recommendations

The script automatically suggests tuning based on patterns:

**Example Output**:
```
TUNING RECOMMENDATIONS
==================================================

⚠️  2 CVs scored TOO HIGH:
   - Aishik: +8.5 points
   - Swastik: +6.2 points

   Recommendation:
   - Increase penalties for weak achievements
   - Strengthen CAR structure requirements
   - Add penalties for vague metrics
```

---

## Weight Tuning Guide

### Common Patterns

#### Pattern A: All Scores Too High

**Symptoms**: Every CV scores 5-15 points above expected

**Fix**: Reduce base achievement weights
```python
# In services/content_impact_analyzer.py
ACHIEVEMENT_WEIGHTS = {
    "perfect_car": 14.0,  # Was 15.0
    "strong_ar": 11.0,    # Was 12.0
    "moderate": 8.0,      # Was 9.0
}
```

---

#### Pattern B: Weak CVs Too High

**Symptoms**: Low-quality CVs (expected <70) scoring 75+

**Fix**: Increase weak phrase penalties
```python
# In services/content_impact_analyzer.py
def detect_weak_phrases(self, text: str) -> Dict:
    # Increase penalty multiplier
    score = max(0, 4 - min(penalties * 1.5, 4))  # Was 1.0
```

---

#### Pattern C: Strong CVs Too Low

**Symptoms**: High-quality CVs (expected 85+) scoring <80

**Fix**: Reduce grammar penalties or increase achievement bonuses
```python
# Option 1: Reduce grammar severity
GRAMMAR_SEVERITY_WEIGHTS = {
    "spelling": -1.5,      # Was -2.0
    "grammar": -1.0,       # Was -1.5
}

# Option 2: Increase perfect CAR bonus
ACHIEVEMENT_WEIGHTS = {
    "perfect_car": 15.0,   # Keep at max
}
```

---

### Iterative Tuning Process

```bash
# 1. Make weight adjustment
vim services/content_impact_analyzer.py

# 2. Run tests to verify no regressions
python3 -m pytest tests/test_content_impact_analyzer.py -v

# 3. Re-run calibration
python3 calibrate_quality_scorer.py --mode initial

# 4. Check if improvement
# Compare delta: was +8.5, now +4.2 → good progress

# 5. Repeat until target met
# Target: ≥90% within ±3 points
```

**Tip**: Make small adjustments (0.5-1.0 points at a time) to avoid overcorrection.

---

## Calibration Workflow

### Phase 1: Initial Validation (Task 16)

**Goal**: Validate approach with 3 known CVs
**Time**: 30 minutes
**Success**: All 3 CVs within ±5 points

```bash
# 1. Run initial test
python3 calibrate_quality_scorer.py --mode initial

# 2. If not meeting target, tune weights
# See "Weight Tuning Guide" above

# 3. Re-test
python3 calibrate_quality_scorer.py --mode initial

# 4. Iterate until passing
# Target: 3/3 within ±5 points
```

**Document**: Record results in `../docs/calibration-results.md` (Task 16 section)

---

### Phase 2: Full Calibration (Task 17)

**Goal**: Achieve ±3 accuracy on 90% of diverse CVs
**Time**: 2-3 hours
**Success**: 27/30 CVs within ±3 points

```bash
# 1. Assemble 30-CV corpus
# See Quick Start Guide for details

# 2. Create corpus manifest
vim data/calibration_corpus/manifest.json

# 3. Run full calibration
python3 calibrate_quality_scorer.py \
    --mode full \
    --manifest data/calibration_corpus/manifest.json \
    --output results/calibration_round1.json

# 4. Analyze results
cat results/calibration_round1.json | jq '.summary'

# 5. Tune weights if needed
# Identify patterns (weak CVs high? strong CVs low?)
# Adjust weights accordingly

# 6. Re-run calibration
python3 calibrate_quality_scorer.py \
    --mode full \
    --manifest data/calibration_corpus/manifest.json \
    --output results/calibration_round2.json

# 7. Compare rounds
python3 scripts/compare_calibration_rounds.py \
    results/calibration_round1.json \
    results/calibration_round2.json

# 8. Iterate until target met
# Target: 27/30 (90%) within ±3 points
```

**Document**: Record all rounds in `../docs/calibration-results.md` (Task 17 section)

---

## Corpus Requirements (Task 17)

### Diversity Matrix

| Role | Entry | Mid | Senior | Total |
|------|-------|-----|--------|-------|
| Product Manager | 3 | 4 | 3 | 10 |
| Software Engineer | 3 | 4 | 3 | 10 |
| Data Scientist | 3 | 4 | 3 | 10 |
| **Total** | **9** | **12** | **9** | **30** |

### Quality Distribution

- Excellent (85-95): 6 CVs (20%)
- Strong (75-84): 9 CVs (30%)
- Good (65-74): 9 CVs (30%)
- Moderate (55-64): 4 CVs (13%)
- Weak (40-54): 2 CVs (7%)

### Geographic Diversity

- North America: 18 CVs (60%)
- Europe: 6 CVs (20%)
- Asia: 6 CVs (20%)

---

## Troubleshooting

### Issue: Script fails with "Pattern file not found"

```bash
# Verify pattern files exist
ls -la data/patterns/

# If missing, they should be at:
# - data/patterns/action_verb_tiers.json
# - data/patterns/weak_phrases.json
# - data/patterns/metric_patterns.json
# - data/patterns/generic_to_specific.json

# Check if running from wrong directory
pwd
# Should be: /Users/sabuj.mondal/ats-resume-scorer
# If not, cd to project root
```

---

### Issue: All scores are 0 or very low

```bash
# Likely scorer initialization failed
# Check for errors in scorer loading

# Test scorer directly
python3 -c "
from services.scorer_quality import QualityScorer
from services.parser import parse_docx

scorer = QualityScorer()
data = parse_docx('data/Sabuj_Mondal_PM_CV_1771577761468.docx')
result = scorer.score(data, 'product_manager', 'senior')
print(result)
"

# If this fails, check:
# 1. All dependencies installed
# 2. Pattern files loaded correctly
# 3. No syntax errors in scorer code
```

---

### Issue: Scores drastically different from expected

```bash
# Example: Expected 86, got 45 (delta: -41)

# Possible causes:
# 1. Wrong CV tested
ls -la data/*.docx  # Verify CV path

# 2. Pattern files corrupted
cat data/patterns/action_verb_tiers.json | jq '.'  # Should be valid JSON

# 3. Scorer logic changed
git diff services/content_impact_analyzer.py  # Check for unexpected changes

# 4. Expected score wrong
# Verify expected score is correct ResumeWorded baseline
```

---

### Issue: Test hangs or takes too long

```bash
# If scoring takes >30 seconds per CV:

# 1. Check for infinite loops
# Add debug logging to scorer

# 2. Profile code
python3 -m cProfile -o calibrate.prof calibrate_quality_scorer.py --mode single --cv test.docx --expected 75

# 3. Analyze profile
python3 -c "
import pstats
p = pstats.Stats('calibrate.prof')
p.sort_stats('cumulative')
p.print_stats(20)
"

# 4. Common bottlenecks:
# - Pattern file loading not cached
# - Regex matching inefficient
# - Repeated parsing of same text
```

---

## Best Practices

### Before Calibration

1. **Ensure code complete**: All tests passing
2. **Verify test CVs**: Files exist and parse correctly
3. **Document baseline**: Record expected scores source
4. **Clean environment**: No uncommitted code changes

### During Calibration

1. **Make small adjustments**: 0.5-1.0 point changes
2. **Test after each change**: Verify no regressions
3. **Document each round**: Record results and rationale
4. **Track patterns**: Note which CVs consistently off

### After Calibration

1. **Document final weights**: Copy to calibration-results.md
2. **Test edge cases**: Unusual CVs, different formats
3. **Performance test**: Ensure <2s per CV
4. **Create backup**: Save working configuration

---

## Output Files

### Calibration Results (JSON)

```json
{
  "timestamp": "2026-02-20T22:00:00",
  "mode": "initial",
  "results": [
    {
      "cv_name": "Sabuj Mondal",
      "expected_score": 86,
      "actual_score": 84.5,
      "delta": -1.5,
      "accuracy_status": "EXCELLENT (±3)",
      "breakdown": {
        "achievement_strength": 13.0,
        "sentence_clarity": 8.5,
        "specificity": 4.0,
        ...
      }
    }
  ],
  "summary": {
    "total_tested": 3,
    "avg_delta": 2.1,
    "within_3": 3,
    "pct_within_3": 100.0
  }
}
```

**Use for**:
- Tracking progress across rounds
- Identifying trends
- Generating reports

---

## Integration with CI/CD

### Automated Testing

Add calibration tests to CI pipeline:

```yaml
# .github/workflows/calibration.yml
name: Calibration Tests

on: [push, pull_request]

jobs:
  calibrate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run calibration
        run: |
          python3 backend/calibrate_quality_scorer.py --mode initial
      - name: Check accuracy
        run: |
          python3 scripts/check_calibration_accuracy.py results/latest.json
          # Fails if <90% within ±3 points
```

---

### Pre-Deployment Validation

Before deploying scorer changes:

```bash
# 1. Run full calibration
python3 calibrate_quality_scorer.py --mode full

# 2. Verify targets met
# Must pass: 90% within ±3 points

# 3. Generate report
python3 scripts/generate_calibration_report.py > CALIBRATION_REPORT.md

# 4. Attach to PR
git add CALIBRATION_REPORT.md
git commit -m "docs: add calibration validation"
```

---

## Next Steps

### After Completing Calibration

1. ✅ Document results (`../docs/calibration-results.md`)
2. ✅ Update deployment guide with final weights
3. ✅ Create deployment package
4. ✅ Set up monitoring dashboards
5. ✅ Prepare rollback procedures
6. 🚀 Deploy to production

### Ongoing Maintenance

- Re-run calibration quarterly
- Add new CVs to corpus as edge cases discovered
- Monitor production scores vs calibration
- Adjust weights if drift detected

---

## Support

### Documentation
- Quick Start: `../docs/calibration-quick-start.md`
- Full Process: `../docs/plans/2026-02-20-quality-coach-recalibration-implementation.md`
- Deployment: `../docs/deployment-guide.md`

### Questions?
- Check status: `../docs/quality-coach-recalibration-status.md`
- Review design: `../docs/plans/2026-02-20-quality-coach-recalibration-design.md`

---

**Last Updated**: 2026-02-20
**Version**: 1.0.0
**Status**: Production Ready
