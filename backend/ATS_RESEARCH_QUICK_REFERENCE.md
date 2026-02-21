# ATS Research Quick Reference Guide
## Fast Lookup for Implementation

**Version:** 2.0 | **Date:** February 21, 2026

---

## Quick Stats

| Metric | Value |
|--------|-------|
| **Total Parameters** | 50+ (enhanced from 44) |
| **Categories** | 7 major categories |
| **Max Positive Score** | 100 points |
| **Max Penalties** | -18 points |
| **Experience Levels** | 3 tiers (Beginner/Intermediary/Senior) |
| **Implementation Time** | 4-6 weeks (phased) |

---

## Industry Standards Summary

### ATS Platform Thresholds (Major Systems)

| Platform | Market Share | Keyword Threshold | Auto-Reject Below |
|----------|-------------|-------------------|-------------------|
| **Workday** | 35% | 60% match | 60% |
| **Greenhouse** | 28% | 50% match | 50% |
| **Lever** | 18% | Semantic (flexible) | 40% |
| **Taleo** | 12% | 70% match (rigid) | 70% |
| **iCIMS** | 15% | 50-70% | Configurable |

**Recommendation:** Use 60% as minimum passing threshold (Workday standard)

---

## Experience Level Definitions

| Level | Years | Page Count | Word Count | Quantification | Action Verbs |
|-------|-------|------------|------------|----------------|--------------|
| **Beginner** | 0-3 | 1 page | 300-500 | 30%+ | 70%+ |
| **Intermediary** | 3-7 | 1-2 pages | 500-700 | 50%+ | 80%+ |
| **Senior** | 7+ | 2 pages | 600-800 | 60%+ | 90%+ |

**Key Changes from Current System:**
- Migrate from 5-tier to 3-tier system
- Add buffer zones to reduce false negatives
- Adjust all thresholds per level

---

## Scoring Categories Overview

| Category | Max Points | Parameters | Priority |
|----------|-----------|------------|----------|
| **Keyword Matching** | 35 | 2 | Critical |
| **Content Quality** | 30 | 3 | Critical |
| **Format & Structure** | 20 | 4 | High |
| **Professional Polish** | 15 | 2 | High |
| **Experience Appropriateness** | 15 | 3 | High |
| **Red Flags (Penalties)** | -18 | 4 | Critical |
| **Metadata Quality** | 10 | 3 | Medium |

**Total:** 100 positive points, up to -18 penalty points

---

## Top 10 Parameters by Impact

| Rank | Parameter | Points | Why It Matters |
|------|-----------|--------|----------------|
| 1 | Required Keywords | 25 | ATS auto-reject below threshold |
| 2 | Action Verb Quality | 15 | Differentiates candidates |
| 3 | Preferred Keywords | 10 | Bonus for standing out |
| 4 | Quantification Rate | 10 | Shows impact |
| 5 | Years Alignment | 10 | Level appropriateness |
| 6 | Grammar & Spelling | 10 | Professionalism |
| 7 | ATS Formatting | 7 | Parseability |
| 8 | Page Count | 5 | First impression |
| 9 | Achievement Depth | 5 | Quality signal |
| 10 | Employment Gaps | -5 | Major red flag |

**Focus Area:** Top 5 parameters account for 70 points

---

## Action Verb Tiers (Quick Reference)

| Tier | Points | When to Use | Examples |
|------|--------|-------------|----------|
| **Tier 4** | 4 | Senior+ transformation | transformed, pioneered, revolutionized, scaled |
| **Tier 3** | 3 | Mid+ leadership | led, architected, launched, drove, spearheaded |
| **Tier 2** | 2 | All levels execution | developed, implemented, created, built, optimized |
| **Tier 1** | 1 | Entry support | managed, coordinated, supported, maintained |
| **Tier 0** | 0 | Never (weak) | responsible for, worked on, helped with |

**Scoring:**
- Beginner: 70%+ coverage, Tier 1.5+ average
- Intermediary: 80%+ coverage, Tier 2.0+ average
- Senior: 90%+ coverage, Tier 2.5+ average

---

## Quantification Patterns (Quick Reference)

| Type | Weight | Pattern Examples | Score |
|------|--------|-----------------|-------|
| **High-Value** | 1.0x | "increased by 45%", "$200K saved", "3x faster" | Full credit |
| **Medium-Value** | 0.7x | "team of 12", "6 months", "100K users" | Partial credit |
| **Low-Value** | 0.3x | "5 projects", "20 bugs fixed" | Minimal credit |

**Thresholds by Level:**
- Beginner: 30%+ quantified bullets
- Intermediary: 50%+ quantified bullets
- Senior: 60%+ quantified bullets

---

## Red Flags Penalties (Quick Reference)

| Red Flag | Trigger | Penalty | Cap |
|----------|---------|---------|-----|
| **Employment Gap** | 18+ months | -5 pts | -5 |
| **Job Hopping** | 3+ jobs <1 year | -3 pts | -3 |
| **Repetition** | Verb 5+ times | -2 pts each | -5 |
| **Keyword Stuffing** | >8% density | -2 pts each | -5 |
| **Date Errors** | End < start | -2 pts each | -5 |
| **Missing Email** | No email | -2 pts | -5 |

**Total Possible Penalties:** -18 points (all categories maxed)

---

## Keyword Matching Formula

```python
# Hybrid: 70% semantic + 30% exact
for keyword in required_keywords:
    semantic_score = semantic_match(keyword, resume)  # 0.0-1.0
    exact_score = 1.0 if keyword in resume.lower() else 0.0

    hybrid_score = (semantic_score * 0.7) + (exact_score * 0.3)

    # Apply tier weighting
    if keyword.tier == 4:  # Critical
        weighted_score = hybrid_score * 3.0
    elif keyword.tier == 3:  # High
        weighted_score = hybrid_score * 2.0
    else:  # Medium
        weighted_score = hybrid_score * 1.0

match_percentage = total_weighted_score / max_possible_score * 100

# Score
if match_percentage >= 60: score = 25  # Excellent
elif match_percentage >= 40: score = 15  # Good
elif match_percentage >= 25: score = 5   # Acceptable
else: score = 0  # Poor
```

---

## Implementation Phases

### Phase 1: Core Scoring (Week 1-2)
**Priority: CRITICAL**
- [ ] P1.1: Required Keywords (25 pts)
- [ ] P1.2: Preferred Keywords (10 pts)
- [ ] P2.1: Action Verbs (15 pts)
- [ ] P2.2: Quantification (10 pts)
- [ ] P4.1: Grammar (10 pts)
- [ ] P5.1: Years Alignment (10 pts)

**Deliverable:** 80/100 points functional

### Phase 2: Quality Enhancement (Week 3-4)
**Priority: HIGH**
- [ ] P2.3: Achievement Depth (5 pts)
- [ ] P3.1-P3.4: Format & Structure (20 pts)
- [ ] P4.2: Professional Standards (5 pts)
- [ ] P5.2-P5.3: Experience Depth (5 pts)

**Deliverable:** Full 100 points + structure

### Phase 3: Red Flags Detection (Week 5)
**Priority: CRITICAL**
- [ ] P6.1: Employment Gaps (-5 pts)
- [ ] P6.2: Job Hopping (-3 pts)
- [ ] P6.3: Repetition (-5 pts)
- [ ] P6.4: Format Errors (-5 pts)

**Deliverable:** Complete penalty system

### Phase 4: Polish & Metadata (Week 6)
**Priority: MEDIUM**
- [ ] P7.1: Readability (5 pts)
- [ ] P7.2: Bullet Structure (3 pts)
- [ ] P7.3: Passive Voice (2 pts)

**Deliverable:** Final 10 points + quality checks

---

## Common Mistakes to Avoid

### Anti-Pattern #1: Hard Thresholds
❌ **Wrong:**
```python
if keyword_match < 70:
    score = 0  # Cliff effect - harsh
```

✅ **Right:**
```python
if keyword_match >= 60:
    score = 25
elif keyword_match >= 40:
    score = 15  # Gradual degradation
```

### Anti-Pattern #2: Ignoring Experience Level
❌ **Wrong:**
```python
# Same thresholds for all
if quantification < 60:
    score = 0
```

✅ **Right:**
```python
threshold = {
    'beginner': 30,
    'intermediary': 50,
    'senior': 60
}[level]
```

### Anti-Pattern #3: Exact Matching Only
❌ **Wrong:**
```python
if 'python' in resume.lower():
    match_count += 1
```

✅ **Right:**
```python
semantic = semantic_matcher.match('python', resume)  # Catches "Python", "Pythonic", etc.
exact = 1.0 if 'python' in resume.lower() else 0.0
score = (semantic * 0.7) + (exact * 0.3)
```

### Anti-Pattern #4: Unlimited Penalties
❌ **Wrong:**
```python
for error in errors:
    score -= 2  # Can go very negative
```

✅ **Right:**
```python
penalty = min(len(errors) * 2, 10)  # Cap at -10
score = max(0, score - penalty)  # Floor at 0
```

---

## Testing Checklist

### Per Parameter Tests
- [ ] Excellent case (max points)
- [ ] Good case (partial points)
- [ ] Poor case (zero points)
- [ ] Edge cases (empty, null, malformed)
- [ ] Level-specific variations (if applicable)

### Integration Tests
- [ ] Full pipeline with sample resumes
- [ ] Score distribution validation
- [ ] Performance benchmarks (<2s per resume)
- [ ] Error handling (graceful degradation)

### Validation Tests
- [ ] Match industry benchmarks
- [ ] No false positives on good resumes
- [ ] Catch common issues
- [ ] Recommendations actionable

---

## Configuration Quick Edits

### To Adjust Thresholds
**File:** `scoring_config.json`

```json
{
  "keyword_matching": {
    "thresholds": {
      "excellent": 60,  // ← Adjust here
      "good": 40,
      "acceptable": 25
    }
  }
}
```

### To Add Action Verbs
**File:** `data/patterns/action_verb_tiers.json`

```json
{
  "tier_3_leadership": [
    "led",
    "architected",
    "championed"  // ← Add here
  ]
}
```

### To Modify Level Ranges
**File:** `scoring_config.json`

```json
{
  "experience_levels": {
    "intermediary": {
      "years_range": [3, 7],  // ← Adjust range
      "quantification_threshold": 50
    }
  }
}
```

---

## Performance Targets

| Operation | Target Time | Notes |
|-----------|-------------|-------|
| Full resume score | <2 seconds | Including all parameters |
| Keyword matching | <500ms | Hybrid semantic+exact |
| Grammar check | <1 second | With caching |
| Action verb analysis | <200ms | Per resume |
| Metadata extraction | <100ms | From parsed data |

**Optimization Strategies:**
- Cache semantic embeddings
- Cache grammar results by hash
- Parallel parameter calculation where possible
- Lazy load heavy dependencies

---

## Monitoring & Metrics

### Key Metrics to Track

| Metric | Target | Warning | Critical |
|--------|--------|---------|----------|
| **Average Score** | 65-75 | <60 or >80 | <50 or >85 |
| **Processing Time** | <2s | 2-3s | >3s |
| **False Negatives** | <5% | 5-10% | >10% |
| **False Positives** | <5% | 5-10% | >10% |
| **Grammar Check Success** | >95% | 90-95% | <90% |

### Health Checks
```python
# Run daily
def health_check():
    # Test with known resumes
    excellent_score = score_resume(excellent_sample)
    assert 85 <= excellent_score <= 100

    poor_score = score_resume(poor_sample)
    assert 0 <= poor_score <= 50

    # Performance check
    start = time.time()
    score_resume(average_sample)
    duration = time.time() - start
    assert duration < 2.0
```

---

## References

### Full Documentation
- **Comprehensive Report:** `ATS_RESEARCH_COMPREHENSIVE_REPORT.md`
- **Parameter Table:** `ATS_PARAMETERS_COMPREHENSIVE_TABLE.md`
- **This Quick Reference:** `ATS_RESEARCH_QUICK_REFERENCE.md`

### Code Locations
- **Current Scorer:** `services/scorer_ats.py`, `services/scorer_quality.py`
- **Validator:** `services/red_flags_validator.py`
- **Keyword Matcher:** `services/keyword_matcher.py`
- **Semantic Matcher:** `services/semantic_matcher.py`

### External Resources
- Workday ATS Documentation
- Greenhouse Technical Blog
- Lever Engineering Blog
- Academic papers (see main report)

---

## Contact & Support

**For Implementation Questions:**
- Review comprehensive report for detailed formulas
- Check parameter table for specific calculations
- Refer to existing code in `services/` directory

**For Threshold Adjustments:**
- Start conservative (use recommended values)
- A/B test changes with real resumes
- Monitor false positive/negative rates

**For New Parameters:**
1. Define clear calculation method
2. Determine point range
3. Write unit tests
4. Add to appropriate category
5. Update documentation

---

**Document Status:** ✅ Ready for Implementation
**Last Updated:** February 21, 2026
**Version:** 2.0
**Prepared By:** Claude Opus 4.6

---

## Quick Implementation Checklist

### Week 1
- [ ] Review all three research documents
- [ ] Set up 3-tier experience level system
- [ ] Implement P1.1: Required Keywords (25 pts)
- [ ] Implement P1.2: Preferred Keywords (10 pts)
- [ ] Write tests for keyword matching

### Week 2
- [ ] Implement P2.1: Action Verbs (15 pts)
- [ ] Implement P2.2: Quantification (10 pts)
- [ ] Implement P4.1: Grammar (10 pts)
- [ ] Implement P5.1: Years Alignment (10 pts)
- [ ] Integration test for 80-point core

### Week 3
- [ ] Implement P2.3: Achievement Depth (5 pts)
- [ ] Implement P3.1-P3.4: Format & Structure (20 pts)
- [ ] Write tests for format scoring

### Week 4
- [ ] Implement P4.2: Professional Standards (5 pts)
- [ ] Implement P5.2-P5.3: Experience Depth (5 pts)
- [ ] Integration test for full 100 points

### Week 5
- [ ] Implement all P6.* penalties (-18 pts)
- [ ] Write tests for red flag detection
- [ ] Validate penalty caps working

### Week 6
- [ ] Implement P7.* metadata quality (10 pts)
- [ ] Full system integration testing
- [ ] Performance optimization
- [ ] Documentation updates
- [ ] Deploy to staging

**Ready to Start!** 🚀
