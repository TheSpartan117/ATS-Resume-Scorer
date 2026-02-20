# Quality Coach Recalibration - Deployment Guide

**Date**: 2026-02-20
**Version**: 1.0.0
**Status**: Ready for Deployment

---

## Overview

This guide covers the deployment of the recalibrated Quality Coach scoring system, which implements sophisticated content impact analysis to achieve ±3 point accuracy with ResumeWorded.

**Key Changes:**
- New `ContentImpactAnalyzer` service for CAR structure detection
- New `WritingQualityAnalyzer` service for severity-weighted grammar
- Enhanced `QualityScorer` with content-focused evaluation
- Pattern data files for verb tiers, weak phrases, and metrics

**Target Accuracy:**
- ±3 points on 90% of CVs
- ±5 points on 100% of CVs

---

## Pre-Deployment Checklist

### Code Review
- [ ] All 17 tests in `test_content_impact_analyzer.py` passing
- [ ] All tests in `test_writing_quality_analyzer.py` passing
- [ ] Integration tests passing
- [ ] Code reviewed and approved
- [ ] No security vulnerabilities identified

### Calibration Validation
- [ ] Task 16 complete: 3 known CVs within ±5 points
- [ ] Task 17 complete: 30 CVs with 90% within ±3 points
- [ ] Edge cases documented
- [ ] Known issues documented

### Infrastructure
- [ ] Pattern data files deployed to production
- [ ] Database migrations complete (if any)
- [ ] Monitoring dashboards updated
- [ ] Logging configured for new services

### Documentation
- [ ] Calibration results documented
- [ ] API changes documented
- [ ] Deployment guide reviewed
- [ ] Rollback procedures tested

---

## API Changes

### New Services

#### 1. ContentImpactAnalyzer

**Location:** `backend/services/content_impact_analyzer.py`

**Purpose:** Analyzes resume content quality using CAR structure detection

**Key Methods:**
```python
from backend.services.content_impact_analyzer import ContentImpactAnalyzer

analyzer = ContentImpactAnalyzer()

# Classify verb strength (0-4)
tier = analyzer.classify_verb_tier("architected")  # Returns: 3

# Extract metrics from text
metrics = analyzer.extract_metrics("Increased revenue by 45%")
# Returns: [{'value': '45%', 'type': 'percentage', 'quality': 1.0}]

# Analyze achievement structure (CAR detection)
result = analyzer.analyze_achievement_structure(
    "Led team of 8 to deliver $2M project ahead of schedule"
)
# Returns: {
#   'score': 12,
#   'has_context': True,
#   'action_strength': 3,
#   'metrics_found': [...],
#   'has_causality': False,
#   'explanation': '...'
# }

# Score overall achievement strength (0-15 pts)
score = analyzer.score_achievement_strength(bullets, level="senior")

# Score sentence clarity (0-10 pts)
score = analyzer.score_sentence_clarity(bullets, section="experience")

# Score specificity (0-5 pts)
score = analyzer.score_specificity(bullets)

# Main entry point: Score impact quality (0-30 pts)
result = analyzer.score_impact_quality(
    bullets=experience_bullets,
    level="senior",
    section="experience"
)
# Returns: {
#   'total_score': 25.5,
#   'achievement_strength': 13.0,
#   'sentence_clarity': 8.5,
#   'specificity': 4.0,
#   'details': '...'
# }
```

**Dependencies:**
- Pattern data files in `backend/data/patterns/`
- No external API calls
- Thread-safe for concurrent requests

---

#### 2. WritingQualityAnalyzer

**Location:** `backend/services/writing_quality_analyzer.py`

**Purpose:** Evaluates writing polish with severity-weighted grammar

**Key Methods:**
```python
from backend.services.writing_quality_analyzer import WritingQualityAnalyzer

analyzer = WritingQualityAnalyzer()

# Score grammar with severity weighting (0-10 pts)
errors = [
    {'category': 'spelling', 'message': 'Typo: managment'},
    {'category': 'grammar', 'message': 'Subject-verb agreement'}
]
result = analyzer.score_grammar_with_severity(errors)
# Returns: {
#   'score': 6.5,  # 10 - 2.0 (spelling) - 1.5 (grammar)
#   'total_errors': 2,
#   'deduction': 3.5,
#   'by_category': {...}
# }

# Check word variety (0-5 pts)
result = analyzer.check_word_variety(text)

# Analyze sentence structure diversity (0-5 pts)
result = analyzer.analyze_sentence_structure(text)
```

**Dependencies:**
- Existing grammar checker service
- No external API calls
- Thread-safe for concurrent requests

---

### Modified Services

#### QualityScorer (Enhanced)

**Location:** `backend/services/scorer_quality.py`

**Changes:**
- Now uses `ContentImpactAnalyzer` for content scoring
- Now uses `WritingQualityAnalyzer` for polish scoring
- Scoring breakdown changed (see below)

**New Scoring Breakdown:**
```
Role Keywords: 25 points (unchanged)
Impact Quality: 30 points (NEW - ContentImpactAnalyzer)
├─ Achievement Strength: 15 pts
├─ Sentence Clarity: 10 pts
└─ Specificity: 5 pts

Format & Structure: 25 points (enhanced)
Writing Polish: 20 points (enhanced - WritingQualityAnalyzer)
├─ Grammar: 10 pts (severity-weighted)
├─ Word Variety: 5 pts
└─ Sentence Structure: 5 pts
```

**API Compatibility:**
- ✅ Same method signature: `score(resume_data, role_id, level, job_description)`
- ✅ Same return format: `{'score': float, 'breakdown': {...}}`
- ⚠️ Breakdown structure changed (see Migration section)

---

## Migration Steps

### Step 1: Deploy Pattern Data Files

```bash
# Ensure pattern files are in place
ls -la backend/data/patterns/
# Should contain:
# - action_verb_tiers.json
# - weak_phrases.json
# - metric_patterns.json
# - generic_to_specific.json

# Set correct permissions
chmod 644 backend/data/patterns/*.json
```

---

### Step 2: Deploy New Services

```bash
# Copy new service files to production
scp backend/services/content_impact_analyzer.py production:/app/backend/services/
scp backend/services/writing_quality_analyzer.py production:/app/backend/services/

# Verify files deployed
ssh production "ls -la /app/backend/services/content_impact_analyzer.py"
ssh production "ls -la /app/backend/services/writing_quality_analyzer.py"
```

---

### Step 3: Update QualityScorer

```bash
# Deploy updated scorer
scp backend/services/scorer_quality.py production:/app/backend/services/

# Verify deployment
ssh production "grep 'ContentImpactAnalyzer' /app/backend/services/scorer_quality.py"
```

---

### Step 4: Run Smoke Tests

```bash
# SSH to production
ssh production

# Activate environment
source /app/venv/bin/activate

# Run smoke tests
python3 -m pytest tests/test_content_impact_analyzer.py -v
python3 -m pytest tests/test_writing_quality_analyzer.py -v
python3 -m pytest tests/test_scorer_quality.py -v

# Test single CV
python3 backend/calibrate_quality_scorer.py \
    --mode single \
    --cv backend/data/test_resumes/sample_resume_3_product_manager.json \
    --expected 75 \
    --role product_manager \
    --level mid
```

---

### Step 5: Enable Feature Flag (if using)

```python
# In feature_flags.py or environment variables
ENABLE_RECALIBRATED_QUALITY_SCORER = True

# Or via environment variable
export ENABLE_RECALIBRATED_QUALITY_SCORER=true
```

---

### Step 6: Monitor Initial Traffic

**Metrics to Watch:**
- Average score changes (expected: some CVs +10, some -10)
- Score distribution (should be more spread out)
- Processing time (should be <2s per CV)
- Error rate (should be <0.1%)

**Grafana Dashboard:**
```
Quality Scorer Metrics:
- Request count
- Average score
- Score distribution (histogram)
- Processing time (p50, p95, p99)
- Error rate
```

**Alert Thresholds:**
- Processing time >2s: Warning
- Processing time >5s: Critical
- Error rate >1%: Warning
- Error rate >5%: Critical

---

## Testing Checklist

### Unit Tests
```bash
# ContentImpactAnalyzer tests
python3 -m pytest tests/test_content_impact_analyzer.py -v

# Expected: 17 tests passing
# - 6 tests for verb tier classification
# - 6 tests for metric detection
# - 5 tests for CAR structure detection
```

```bash
# WritingQualityAnalyzer tests
python3 -m pytest tests/test_writing_quality_analyzer.py -v

# Expected: TBD tests passing
```

---

### Integration Tests
```bash
# Full pipeline test
python3 -m pytest tests/integration/test_full_pipeline.py -v

# Calibration validation
python3 backend/calibrate_quality_scorer.py --mode initial

# Expected output:
# ✅ Sabuj: 86 ± 3 points
# ✅ Aishik: 80 ± 3 points
# ✅ Swastik: 65 ± 3 points
```

---

### Performance Tests
```bash
# Load test with 100 concurrent requests
python3 tests/performance/load_test_scorer.py \
    --requests 100 \
    --concurrent 10 \
    --mode quality

# Expected:
# - p95 latency < 2s
# - p99 latency < 5s
# - Error rate < 0.1%
```

---

## Rollback Procedures

### Quick Rollback (5 minutes)

If critical issues detected, rollback immediately:

```bash
# 1. Disable feature flag
export ENABLE_RECALIBRATED_QUALITY_SCORER=false

# 2. Restart application
sudo systemctl restart ats-scorer

# 3. Verify old scorer in use
curl http://localhost:8000/api/score/health
# Should return: {"scorer_version": "quality_v1"}
```

---

### Full Rollback (15 minutes)

If feature flag not available:

```bash
# 1. Restore old scorer file
ssh production
cd /app/backend/services
cp scorer_quality.py.backup scorer_quality.py

# 2. Restart application
sudo systemctl restart ats-scorer

# 3. Run smoke tests
python3 -m pytest tests/test_scorer_quality.py -v

# 4. Monitor for 5 minutes
tail -f /var/log/ats-scorer/app.log
```

---

### Rollback Decision Matrix

| Issue | Severity | Action | Timeframe |
|-------|----------|--------|-----------|
| Error rate >5% | Critical | Immediate rollback | <5 min |
| Processing time >5s | Critical | Immediate rollback | <5 min |
| Incorrect scores (>20% delta) | High | Rollback within 1 hour | <15 min |
| Minor scoring differences | Medium | Monitor, fix forward | Next release |
| User complaints | Low-Medium | Investigate, document | TBD |

---

## Monitoring Strategy

### Key Metrics

**1. Score Distribution**
```sql
-- Expected distribution after recalibration
-- More spread out, better differentiation

SELECT
    score_bucket,
    COUNT(*) as count,
    ROUND(AVG(score), 1) as avg_score
FROM (
    SELECT
        CASE
            WHEN score >= 90 THEN '90-100'
            WHEN score >= 80 THEN '80-89'
            WHEN score >= 70 THEN '70-79'
            WHEN score >= 60 THEN '60-69'
            ELSE '<60'
        END as score_bucket,
        score
    FROM resume_scores
    WHERE created_at > NOW() - INTERVAL '1 day'
        AND mode = 'quality'
) t
GROUP BY score_bucket
ORDER BY score_bucket DESC;
```

**Expected Distribution:**
- 90-100: 10-15% (excellent CVs)
- 80-89: 20-25% (strong CVs)
- 70-79: 30-35% (good CVs)
- 60-69: 20-25% (needs work)
- <60: 10-15% (weak CVs)

---

**2. Processing Time**
```python
# Add timing instrumentation
import time

start = time.time()
result = scorer.score(resume_data, role_id, level)
duration = time.time() - start

# Log to metrics
log_metric('scorer.quality.duration', duration)
log_metric('scorer.quality.score', result['score'])
```

**Expected Latency:**
- p50: <500ms
- p95: <1.5s
- p99: <2.5s

---

**3. Component Breakdown**
```python
# Track time per component
timings = {
    'content_impact': duration_content,
    'writing_quality': duration_writing,
    'format': duration_format,
    'keywords': duration_keywords,
    'total': duration_total
}

log_metrics('scorer.quality.component_timings', timings)
```

---

### Alert Rules

**Critical Alerts (PagerDuty):**
```yaml
alerts:
  - name: scorer_high_error_rate
    condition: error_rate > 5%
    severity: critical
    notify: on-call-engineer

  - name: scorer_high_latency
    condition: p99_latency > 5s
    severity: critical
    notify: on-call-engineer
```

**Warning Alerts (Slack):**
```yaml
alerts:
  - name: scorer_elevated_error_rate
    condition: error_rate > 1%
    severity: warning
    notify: #eng-alerts

  - name: scorer_elevated_latency
    condition: p95_latency > 2s
    severity: warning
    notify: #eng-alerts
```

---

## A/B Testing Plan (Optional)

If deploying as A/B test rather than full rollout:

### Configuration

```python
# Feature flag with percentage rollout
QUALITY_SCORER_RECALIBRATION = {
    'enabled': True,
    'rollout_percentage': 10,  # Start with 10%
    'whitelist_users': ['user_123', 'user_456'],  # Beta testers
    'blacklist_users': []  # Exclude problematic users
}

# Usage
def get_scorer(user_id):
    if should_use_recalibrated_scorer(user_id):
        return QualityScorerV2()  # New scorer
    else:
        return QualityScorerV1()  # Old scorer
```

---

### Rollout Schedule

**Week 1: 10% rollout**
- Monitor: Error rate, latency, user feedback
- Target: <1% error rate, <2s p95 latency
- Action: If stable, proceed to Week 2

**Week 2: 25% rollout**
- Monitor: Score distribution changes, user complaints
- Target: No major issues, positive feedback
- Action: If stable, proceed to Week 3

**Week 3: 50% rollout**
- Monitor: Overall system health, comparison metrics
- Target: Improved accuracy, similar latency
- Action: If stable, proceed to Week 4

**Week 4: 100% rollout**
- Monitor: Full system metrics, user satisfaction
- Target: Meets accuracy targets, stable performance
- Action: Consider permanent deployment

---

### Comparison Metrics

Track both scorers side-by-side:

```python
# Score with both old and new scorer
result_v1 = scorer_v1.score(resume_data, role_id, level)
result_v2 = scorer_v2.score(resume_data, role_id, level)

# Log comparison
log_comparison({
    'user_id': user_id,
    'resume_id': resume_id,
    'score_v1': result_v1['score'],
    'score_v2': result_v2['score'],
    'delta': result_v2['score'] - result_v1['score'],
    'breakdown_v1': result_v1['breakdown'],
    'breakdown_v2': result_v2['breakdown']
})
```

**Analyze:**
- Average delta per user segment
- Score distribution comparison
- User preference (if surveys conducted)

---

## Known Issues and Limitations

### Issue 1: Entry-Level CVs
**Description:** TBD

**Workaround:** TBD

**Fix Timeline:** TBD

---

### Issue 2: International CVs
**Description:** TBD

**Workaround:** TBD

**Fix Timeline:** TBD

---

## Support and Troubleshooting

### Common Issues

**Issue: "Pattern file not found" error**
```
Error: RuntimeError: Pattern file not found: [Errno 2] No such file or directory
```

**Solution:**
```bash
# Verify pattern files exist
ls -la backend/data/patterns/

# If missing, copy from repository
cp -r deployment/patterns/* backend/data/patterns/

# Verify permissions
chmod 644 backend/data/patterns/*.json
```

---

**Issue: Scores drastically different from expected**
```
Expected: 86, Got: 45 (delta: -41)
```

**Solution:**
1. Check if pattern files are correct version
2. Verify verb tier mappings loaded correctly
3. Review calibration results for similar cases
4. Check if CV has unusual structure

---

**Issue: High processing time (>5s)**
```
Score took 8.5s to compute
```

**Solution:**
1. Check if pattern file loading is cached
2. Verify no network calls in scoring logic
3. Profile code to identify bottleneck
4. Consider caching parsed resume data

---

### Contact Information

**Engineering Team:**
- Lead: TBD
- On-call: TBD
- Slack: #eng-ats-scorer

**Product Team:**
- PM: TBD
- Slack: #product-quality-coach

---

## Post-Deployment Validation

### Week 1 Checklist
- [ ] All metrics within expected ranges
- [ ] No critical alerts triggered
- [ ] User feedback reviewed
- [ ] Calibration accuracy validated with new CVs
- [ ] Documentation updated with learnings

### Week 2 Checklist
- [ ] A/B test results analyzed (if applicable)
- [ ] Score distribution matches expectations
- [ ] Performance stable under load
- [ ] Edge cases documented and handled
- [ ] Team trained on new system

### Week 4 Checklist
- [ ] Full rollout complete
- [ ] Rollback procedures tested
- [ ] Monitoring dashboards finalized
- [ ] Feature flag removed (if full rollout)
- [ ] Post-mortem completed

---

## Appendix: Configuration Reference

### Pattern Data Files

**Location:** `backend/data/patterns/`

**Files:**
1. `action_verb_tiers.json` - Verb strength classification (0-4 tiers)
2. `weak_phrases.json` - Weak phrase library (5 categories)
3. `metric_patterns.json` - Regex patterns for metric extraction
4. `generic_to_specific.json` - Technology/tool specificity mappings

**Validation:**
```python
# Validate pattern files on startup
from backend.services.content_impact_analyzer import ContentImpactAnalyzer

try:
    analyzer = ContentImpactAnalyzer()
    print("✅ Pattern files loaded successfully")
except Exception as e:
    print(f"❌ Pattern file validation failed: {e}")
```

---

### Environment Variables

```bash
# Feature flags
export ENABLE_RECALIBRATED_QUALITY_SCORER=true

# Logging
export SCORER_LOG_LEVEL=INFO  # DEBUG for troubleshooting
export SCORER_LOG_BREAKDOWN=true  # Log component scores

# Performance
export SCORER_CACHE_ENABLED=true
export SCORER_CACHE_TTL=3600  # 1 hour
```

---

## Changelog

### Version 1.0.0 (2026-02-20)
- Initial release of recalibrated Quality Coach scorer
- Added ContentImpactAnalyzer service
- Added WritingQualityAnalyzer service
- Enhanced QualityScorer with content-focused evaluation
- Target accuracy: ±3 points on 90% of CVs
