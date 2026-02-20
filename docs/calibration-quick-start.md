# Quality Coach Calibration - Quick Start Guide

**Purpose**: Get from "code complete" to "production ready" in under 4 hours

This guide assumes Tasks 1-15 (code implementation) are complete and all tests are passing.

---

## Prerequisites Check

Before starting calibration, verify:

```bash
# 1. All unit tests passing
python3 -m pytest tests/test_content_impact_analyzer.py -v
# Expected: 17/17 tests PASS

python3 -m pytest tests/test_writing_quality_analyzer.py -v
# Expected: All tests PASS

python3 -m pytest tests/test_scorer_quality.py -v
# Expected: All tests PASS

# 2. Pattern files in place
ls -la backend/data/patterns/
# Expected: 4 JSON files (action_verb_tiers, weak_phrases, etc.)

# 3. Test CVs available
ls -la backend/data/Sabuj*.docx
ls -la backend/data/SWASTIK*.docx
# Expected: Files exist
```

**If any check fails**: Stop and complete code implementation first.

---

## Step 1: Initial Calibration (30 minutes)

### Run 3-CV Test

```bash
cd /Users/sabuj.mondal/ats-resume-scorer

python3 backend/calibrate_quality_scorer.py \
    --mode initial \
    --output results/calibration_round1.json
```

### Expected Output

```
==================================================
Testing: Sabuj Mondal
Expected Score: 86
==================================================

✓ Actual Score: 84/100
   Delta: -2.0 points (EXCELLENT ±3)

Score Breakdown:
  - achievement_strength: 13.0/15 pts
  - sentence_clarity: 8.5/10 pts
  - specificity: 4.0/5 pts
  - keywords_fit: 20.0/25 pts
  - format: 23.0/25 pts
  - polish: 18.0/20 pts

==================================================
CALIBRATION SUMMARY
==================================================
Tested: 3 CVs
Average Delta: 2.3 points
Max Delta: 3.5 points
Within ±3 points: 3/3 (100%)
Within ±5 points: 3/3 (100%)

✅ TARGET MET: ≥90% within ±3 points
```

---

### Decision Tree

**If all 3 CVs within ±3 points** ✅
→ Proceed to Step 2 (expand to 30 CVs)

**If 2/3 CVs within ±3 points** ⚠️
→ Analyze patterns, tune weights (see Weight Tuning Guide below)

**If 1/3 or 0/3 CVs within ±3 points** ❌
→ Major recalibration needed, review algorithm logic

---

## Step 2: Assemble 30-CV Test Corpus (45 minutes)

### Corpus Requirements

**Minimum Requirements:**
- 30 total CVs
- 3 roles (10 CVs each): Product Manager, Software Engineer, Data Scientist
- 3 levels per role: Entry (3), Mid (4), Senior (3)
- Score range: 40-95 points
- At least 2 CVs from non-US markets

### Sources

**Option A: Use ResumeWorded scores (recommended)**
1. Upload 30 CVs to ResumeWorded (free trial)
2. Record scores in spreadsheet
3. Download CVs to `backend/data/calibration_corpus/`

**Option B: Manual scoring (faster but less accurate)**
1. Gather 30 diverse CVs
2. Manually assess quality (weak=50, moderate=70, strong=85)
3. Add to corpus directory

**Option C: Use existing test resumes**
1. Check `backend/data/test_resumes/` for existing samples
2. Get baseline scores for each
3. Supplement with additional CVs

---

### Create Corpus Manifest

Create `backend/data/calibration_corpus/manifest.json`:

```json
{
  "version": "1.0",
  "created": "2026-02-20",
  "cvs": [
    {
      "id": "cv_001",
      "path": "Sabuj_Mondal_PM_CV_1771577761468.docx",
      "expected_score": 86,
      "role": "product_manager",
      "level": "senior",
      "source": "resumeworded",
      "notes": "Strong achievements, specific metrics"
    },
    {
      "id": "cv_002",
      "path": "SWASTIK PAUL_CV_DIG_TRSFN STGY_PM-2_1771570503119.docx",
      "expected_score": 65,
      "role": "product_manager",
      "level": "mid",
      "source": "resumeworded",
      "notes": "Weak duty statements"
    },
    // ... 28 more CVs
  ]
}
```

---

## Step 3: Full Calibration (1 hour)

### Run 30-CV Test

```bash
# Update calibration script to use manifest
python3 backend/calibrate_quality_scorer.py \
    --mode full \
    --manifest backend/data/calibration_corpus/manifest.json \
    --output results/calibration_round2.json
```

### Analyze Results

```bash
# View summary
cat results/calibration_round2.json | jq '.summary'

# Expected output:
{
  "total_tested": 30,
  "avg_delta": 2.8,
  "max_delta": 5.2,
  "within_3": 28,
  "within_5": 30,
  "pct_within_3": 93.3,
  "pct_within_5": 100
}
```

---

### Decision Tree

**If ≥90% within ±3 points** ✅
→ Proceed to Step 4 (documentation)

**If 80-89% within ±3 points** ⚠️
→ Analyze outliers, minor tuning needed

**If <80% within ±3 points** ❌
→ Significant tuning needed (see Weight Tuning Guide)

---

## Weight Tuning Guide

If scores are not meeting targets, follow this systematic approach:

### 1. Analyze Score Patterns

```bash
# Identify over-scored CVs
cat results/calibration_round2.json | jq '.results[] | select(.delta > 3) | {name: .cv_name, delta: .delta}'

# Identify under-scored CVs
cat results/calibration_round2.json | jq '.results[] | select(.delta < -3) | {name: .cv_name, delta: .delta}'
```

---

### 2. Common Patterns & Fixes

#### Pattern A: All CVs scored too high (+5 to +15)

**Cause**: Base weights too generous

**Fix**: Reduce achievement weights
```python
# In backend/services/content_impact_analyzer.py
ACHIEVEMENT_WEIGHTS = {
    "perfect_car": 14.0,  # Was 15.0
    "strong_ar": 11.0,    # Was 12.0
    "moderate": 8.0,      # Was 9.0
    "weak_duty": 4.0,     # Was 5.0
    "very_weak": 0.5      # Was 1.0
}
```

---

#### Pattern B: Weak CVs scored too high

**Cause**: Not enough penalty for weak achievements

**Fix**: Increase weak phrase penalties
```python
# In backend/services/content_impact_analyzer.py
def detect_weak_phrases(self, text: str) -> Dict:
    # ...
    # Increase penalty per weak phrase
    score = max(0, 4 - min(penalties * 1.5, 4))  # Was: penalties * 1.0
```

---

#### Pattern C: Strong CVs scored too low

**Cause**: Penalties too harsh or not enough credit for quality

**Fix**: Reduce clarity penalties
```python
# In backend/services/content_impact_analyzer.py
CLARITY_WEIGHTS = {
    "sentence_length": 3.0,
    "weak_phrases": 3.0,      # Was 4.0 - reduce penalty
    "active_voice": 3.0
}
```

---

#### Pattern D: Entry-level CVs scored too low

**Cause**: Expecting senior-level achievements

**Fix**: Adjust level multipliers
```python
# In backend/services/content_impact_analyzer.py
level_multipliers = {
    "entry": 0.7,      # Was 0.6 - more lenient
    "mid": 0.8,
    "senior": 1.0,
    "lead": 1.1,
    "executive": 1.2
}
```

---

### 3. Iterative Tuning Process

```bash
# 1. Make weight adjustments
vim backend/services/content_impact_analyzer.py

# 2. Re-run tests
python3 -m pytest tests/test_content_impact_analyzer.py -v

# 3. Re-run calibration
python3 backend/calibrate_quality_scorer.py --mode full --output results/calibration_round3.json

# 4. Compare results
python3 scripts/compare_calibration_rounds.py results/calibration_round2.json results/calibration_round3.json

# 5. Repeat until target met
```

**Target**: ≥90% within ±3 points, 100% within ±5 points

---

## Step 4: Document Results (30 minutes)

### Update Calibration Results

```bash
# 1. Open template
vim docs/calibration-results.md

# 2. Fill in Round 1 results (Task 16 - 3 CVs)
# Copy data from results/calibration_round1.json

# 3. Fill in Round 2 results (Task 17 - 30 CVs)
# Copy data from results/calibration_round2.json

# 4. Document final weights
# Copy from backend/services/content_impact_analyzer.py
# Copy from backend/services/writing_quality_analyzer.py

# 5. Add edge cases
# Document any CVs that consistently score outside ±3 range
```

### Document Final Configuration

```bash
# 1. Export final weights to JSON
python3 scripts/export_weights.py > docs/final_weights.json

# 2. Take screenshots of sample results
python3 backend/calibrate_quality_scorer.py \
    --mode single \
    --cv backend/data/Sabuj_Mondal_PM_CV_1771577761468.docx \
    --expected 86 \
    --output results/sample_result.json

# 3. Update deployment guide with actual values
vim docs/deployment-guide.md
```

---

## Step 5: Pre-Production Validation (30 minutes)

### Final Checks

```bash
# 1. All tests passing
python3 -m pytest tests/ -v --tb=short
# Expected: 100% pass rate

# 2. Performance test
python3 tests/performance/test_scorer_performance.py
# Expected: <2s per CV, p95 <1.5s

# 3. Smoke test with random CVs
for i in {1..10}; do
    python3 backend/calibrate_quality_scorer.py \
        --mode single \
        --cv "backend/data/test_resumes/sample_resume_${i}.json" \
        --expected 75 \
        --role product_manager \
        --level mid
done

# 4. Check for edge cases
python3 scripts/check_edge_cases.py
```

---

### Create Deployment Package

```bash
# 1. Create release branch
git checkout -b release/quality-coach-recalibration-v1.0

# 2. Commit all changes
git add .
git commit -m "feat: quality coach recalibration v1.0

Complete recalibration of Quality Coach scorer with:
- ContentImpactAnalyzer for CAR structure detection
- WritingQualityAnalyzer for severity-weighted grammar
- Calibrated to ±3 points accuracy on 90% of CVs

Calibration Results:
- Round 1 (3 CVs): 100% within ±3 points
- Round 2 (30 CVs): 93% within ±3 points
- Final weights documented in docs/calibration-results.md

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"

# 3. Tag release
git tag -a v1.0.0 -m "Quality Coach Recalibration v1.0"

# 4. Push to remote
git push origin release/quality-coach-recalibration-v1.0
git push origin v1.0.0
```

---

## Step 6: Deployment (Follow Deployment Guide)

See `docs/deployment-guide.md` for detailed deployment steps.

**Quick Deployment:**
```bash
# 1. Copy files to production
./scripts/deploy_quality_scorer.sh production

# 2. Run smoke tests on production
ssh production "cd /app && python3 -m pytest tests/test_scorer_quality.py -v"

# 3. Enable feature flag
ssh production "export ENABLE_RECALIBRATED_QUALITY_SCORER=true"

# 4. Restart service
ssh production "sudo systemctl restart ats-scorer"

# 5. Monitor for 30 minutes
ssh production "tail -f /var/log/ats-scorer/app.log"
```

---

## Troubleshooting

### Issue: "Pattern file not found"

```bash
# Verify files exist
ssh production "ls -la /app/backend/data/patterns/"

# If missing, copy files
scp -r backend/data/patterns/* production:/app/backend/data/patterns/

# Restart service
ssh production "sudo systemctl restart ats-scorer"
```

---

### Issue: Scores wildly different from expected

```bash
# 1. Check if correct scorer version loaded
ssh production "python3 -c 'from backend.services.scorer_quality import QualityScorer; print(QualityScorer.__doc__)'"

# 2. Verify pattern files are correct version
ssh production "cat /app/backend/data/patterns/action_verb_tiers.json | jq '.tier_4_transformational'"

# 3. Check logs for errors
ssh production "grep ERROR /var/log/ats-scorer/app.log | tail -20"

# 4. Test single CV on production
ssh production "cd /app && python3 backend/calibrate_quality_scorer.py --mode single --cv test.docx --expected 80"
```

---

### Issue: High processing time (>5s)

```bash
# 1. Profile scoring
ssh production "cd /app && python3 -m cProfile -o scorer.prof backend/calibrate_quality_scorer.py --mode single --cv test.docx"

# 2. Analyze profile
ssh production "cd /app && python3 -c 'import pstats; p = pstats.Stats(\"scorer.prof\"); p.sort_stats(\"cumulative\"); p.print_stats(20)'"

# 3. Check for repeated pattern file loading
# Should load once and cache, not reload per request
```

---

## Success Criteria Checklist

Before declaring "production ready", verify:

### Code Quality
- [ ] All unit tests passing (100%)
- [ ] All integration tests passing
- [ ] Code reviewed and approved
- [ ] No TODOs or FIXMEs in production code
- [ ] Documentation complete and reviewed

### Calibration Accuracy
- [ ] ≥90% of 30 CVs within ±3 points
- [ ] 100% of 30 CVs within ±5 points
- [ ] Known edge cases documented
- [ ] Weights frozen and documented

### Performance
- [ ] p95 latency <2s per CV
- [ ] p99 latency <5s per CV
- [ ] No memory leaks detected
- [ ] Thread-safe confirmed

### Operations
- [ ] Deployment guide complete
- [ ] Rollback procedures tested
- [ ] Monitoring dashboards configured
- [ ] Alert rules defined
- [ ] On-call team trained

---

## Timeline Summary

| Step | Duration | Critical Path |
|------|----------|---------------|
| 1. Initial Calibration (3 CVs) | 30 min | ✅ Yes |
| 2. Assemble 30-CV Corpus | 45 min | ✅ Yes |
| 3. Full Calibration (30 CVs) | 1 hour | ✅ Yes |
| 4. Document Results | 30 min | ⚠️ Parallel |
| 5. Pre-Production Validation | 30 min | ✅ Yes |
| 6. Deployment | 30 min | ✅ Yes |
| **Total** | **4 hours** | **3.5 hours** |

**Optimized Path**: Can be done in 3.5 hours if documentation is done in parallel with corpus assembly.

---

## Next Steps

**Right now:**
1. ✅ Verify prerequisites (all tests passing)
2. ✅ Run Step 1 (initial calibration)

**If Step 1 passes:**
3. Begin Step 2 (assemble corpus)

**If Step 1 fails:**
3. Analyze patterns and tune weights
4. Iterate until passing

**Questions?** Check:
- Full implementation plan: `docs/plans/2026-02-20-quality-coach-recalibration-implementation.md`
- Design document: `docs/plans/2026-02-20-quality-coach-recalibration-design.md`
- Status tracker: `docs/quality-coach-recalibration-status.md`
