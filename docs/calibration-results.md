# Quality Coach Scoring Calibration Results

**Date**: 2026-02-20
**Status**: In Progress
**Goal**: Achieve ±3 point accuracy with ResumeWorded on 90% of CVs

---

## Executive Summary

This document tracks the calibration process for the recalibrated Quality Coach scoring system, documenting test results, weight adjustments, and final accuracy metrics.

**Target Accuracy:**
- ±3 points on 90% of CVs
- ±5 points on 100% of CVs

**Baseline (ResumeWorded Scores):**
- Sabuj CV: 86 points (strong achievement structure)
- Aishik CV: 80 points (good content, over-formatted)
- Swastik CV: 65 points (weak duty statements)

---

## Task 16: Initial Calibration (3 Known CVs)

### Test Results

#### Round 1: Initial Weights (Date: TBD)

| CV Name | Expected | Actual | Delta | Status | Notes |
|---------|----------|--------|-------|--------|-------|
| Sabuj   | 86       | TBD    | TBD   | TBD    | Strong achievements, specific metrics |
| Aishik  | 80       | TBD    | TBD   | TBD    | Good content, overly formatted |
| Swastik | 65       | TBD    | TBD   | TBD    | Weak duty statements, lacks metrics |

**Summary:**
- Average Delta: TBD
- Max Delta: TBD
- Within ±3: TBD/3 (TBD%)
- Within ±5: TBD/3 (TBD%)

**Issues Identified:**
- TBD

**Weight Adjustments Needed:**
- TBD

---

#### Round 2: Adjusted Weights (Date: TBD)

| CV Name | Expected | Actual | Delta | Status | Notes |
|---------|----------|--------|-------|--------|-------|
| Sabuj   | 86       | TBD    | TBD   | TBD    | TBD |
| Aishik  | 80       | TBD    | TBD   | TBD    | TBD |
| Swastik | 65       | TBD    | TBD   | TBD    | TBD |

**Summary:**
- Average Delta: TBD
- Max Delta: TBD
- Within ±3: TBD/3 (TBD%)
- Within ±5: TBD/3 (TBD%)

**Improvements:**
- TBD

**Further Adjustments:**
- TBD

---

## Task 17: Full Calibration (30 CVs)

### Test Corpus Composition

**Diversity Requirements:**
- 3 roles: Product Manager, Software Engineer, Data Scientist
- 3 levels: Entry, Mid, Senior
- Geographic diversity: US, Europe, Asia
- Quality range: 40-95 points

### Corpus Preparation

**Sources:**
1. Known CVs (3): Sabuj, Aishik, Swastik
2. High-quality CVs (10): Strong achievements, clear metrics
3. Medium-quality CVs (10): Mixed quality, some issues
4. Low-quality CVs (7): Weak achievements, formatting issues

**Status:** TBD

---

### Full Test Results (Date: TBD)

| CV ID | Role | Level | Expected | Actual | Delta | Status |
|-------|------|-------|----------|--------|-------|--------|
| TBD   | TBD  | TBD   | TBD      | TBD    | TBD   | TBD    |

**Summary:**
- Total Tested: TBD
- Average Delta: TBD
- Max Delta: TBD
- Within ±3: TBD/30 (TBD%)
- Within ±5: TBD/30 (TBD%)

**Target Achievement:**
- ✅/❌ ±3 points on ≥90% of CVs: TBD
- ✅/❌ ±5 points on 100% of CVs: TBD

---

## Final Weight Configuration

### ContentImpactAnalyzer Weights

```python
# Achievement Strength (15 pts)
ACHIEVEMENT_WEIGHTS = {
    "perfect_car": 15.0,      # Context + Action + Result + Causality
    "strong_ar": 12.0,        # Action + Quantified Result
    "moderate": 9.0,          # Action + Vague Result
    "weak_duty": 5.0,         # Just action, no result
    "very_weak": 1.0          # No clear action
}

# Verb Tier Multipliers
VERB_TIER_WEIGHTS = {
    4: 1.0,    # Transformational (led, architected, launched)
    3: 0.9,    # Leadership (delivered, drove, championed)
    2: 0.8,    # Execution (developed, implemented, optimized)
    1: 0.6,    # Support (managed, coordinated, maintained)
    0: 0.3     # Weak (responsible for, worked on, helped with)
}

# Metric Quality Weights
METRIC_QUALITY_WEIGHTS = {
    "money": 1.0,         # $2M, $500K
    "percentage": 1.0,    # 45%, 60%
    "comparison": 0.9,    # increased by X
    "multiplier": 0.8,    # 3x, 5x
    "range": 0.8,         # from X to Y
    "count": 0.7,         # 12 teams, 150 users
    "time": 0.7,          # 6 months, 2 years
    "plus": 0.6           # 10+, 100+
}

# Sentence Clarity (10 pts)
CLARITY_WEIGHTS = {
    "sentence_length": 3.0,      # Optimal 15-25 words
    "weak_phrases": 4.0,         # Penalty for "responsible for", etc.
    "active_voice": 3.0          # Prefer active over passive
}

# Specificity (5 pts)
SPECIFICITY_WEIGHTS = {
    "technology": 2.0,    # Specific tech vs generic terms
    "metrics": 2.0,       # Precise numbers vs vague claims
    "actions": 1.0        # Concrete vs abstract verbs
}
```

### WritingQualityAnalyzer Weights

```python
# Grammar Severity (10 pts)
GRAMMAR_SEVERITY_WEIGHTS = {
    "spelling": -2.0,      # Critical - unprofessional
    "grammar": -1.5,       # Serious - affects clarity
    "punctuation": -1.0,   # Moderate - minor issue
    "style": -0.5,         # Suggestion - nitpicky
    "typo": -2.0           # Critical - careless
}

# Word Variety (5 pts)
WORD_VARIETY_THRESHOLDS = {
    "repetition_threshold": 3,    # Flag words used >3 times
    "penalty_per_repeat": 0.5     # Deduct 0.5 pts per repeat
}

# Sentence Structure (5 pts)
STRUCTURE_DIVERSITY_WEIGHTS = {
    "variety_bonus": 5.0,         # Full points for diverse structures
    "repetitive_penalty": 2.0     # Penalty for same structure repeated
}
```

---

## Score Distribution Analysis

### Distribution by Category

**Achievement Strength (15 pts):**
- Excellent (13-15): TBD CVs (TBD%)
- Good (10-12): TBD CVs (TBD%)
- Moderate (7-9): TBD CVs (TBD%)
- Weak (0-6): TBD CVs (TBD%)

**Sentence Clarity (10 pts):**
- Excellent (9-10): TBD CVs (TBD%)
- Good (7-8): TBD CVs (TBD%)
- Moderate (5-6): TBD CVs (TBD%)
- Weak (0-4): TBD CVs (TBD%)

**Specificity (5 pts):**
- Excellent (4.5-5): TBD CVs (TBD%)
- Good (3.5-4): TBD CVs (TBD%)
- Moderate (2.5-3): TBD CVs (TBD%)
- Weak (0-2): TBD CVs (TBD%)

---

## Known Edge Cases

### Edge Case 1: Entry-Level CVs
**Issue:** TBD
**Example:** TBD
**Handling:** TBD

### Edge Case 2: Executive CVs
**Issue:** TBD
**Example:** TBD
**Handling:** TBD

### Edge Case 3: Technical vs Non-Technical Roles
**Issue:** TBD
**Example:** TBD
**Handling:** TBD

### Edge Case 4: International CVs
**Issue:** TBD
**Example:** TBD
**Handling:** TBD

---

## Accuracy Metrics

### Overall Performance

**Target vs Actual:**
- Target: ±3 points on 90% of CVs
- Actual: TBD% within ±3 points
- Status: TBD

**By Role:**
| Role | Count | Avg Delta | Within ±3 | Within ±5 |
|------|-------|-----------|-----------|-----------|
| Product Manager | TBD | TBD | TBD% | TBD% |
| Software Engineer | TBD | TBD | TBD% | TBD% |
| Data Scientist | TBD | TBD | TBD% | TBD% |

**By Level:**
| Level | Count | Avg Delta | Within ±3 | Within ±5 |
|-------|-------|-----------|-----------|-----------|
| Entry | TBD | TBD | TBD% | TBD% |
| Mid | TBD | TBD | TBD% | TBD% |
| Senior | TBD | TBD | TBD% | TBD% |

---

## Comparison with Old System

### Before Recalibration

| CV Name | Old Score | ResumeWorded | Delta | Issue |
|---------|-----------|--------------|-------|-------|
| Sabuj   | 75.4      | 86           | -10.6 | Under-scored |
| Aishik  | 96        | 80           | +16   | Over-scored |
| Swastik | 75        | 65           | +10   | Over-scored |

**Problems:**
- Score inversion: Weak CV (Swastik) scored same as strong CV (Sabuj)
- Over-rewarded formatting over content
- No distinction between achievements and duties

### After Recalibration

| CV Name | New Score | ResumeWorded | Delta | Status |
|---------|-----------|--------------|-------|--------|
| Sabuj   | TBD       | 86           | TBD   | TBD    |
| Aishik  | TBD       | 80           | TBD   | TBD    |
| Swastik | TBD       | 65           | TBD   | TBD    |

**Improvements:**
- TBD

---

## Recommendations for Production

### Monitoring Strategy
- TBD

### Fallback Procedures
- TBD

### A/B Testing Plan
- TBD

---

## Appendix: Detailed Test Data

### Test Run Logs
- TBD

### Weight Evolution History
- TBD

### Statistical Analysis
- TBD
