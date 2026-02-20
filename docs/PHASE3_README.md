# Phase 3: UI Simplification - Developer Guide

**Quick Reference for Phase 3 Features**

---

## Overview

Phase 3 introduces two major features to simplify the user experience:

1. **Suggestion Prioritization** - Shows top 3 critical issues prominently
2. **ATS Pass Probability** - Clear percentage with platform breakdown

---

## Quick Start

### Backend

```python
# 1. Prioritize suggestions
from backend.services.suggestion_prioritizer import SuggestionPrioritizer

prioritizer = SuggestionPrioritizer()
result = prioritizer.prioritize_suggestions(suggestions, top_n=3)

# result contains:
# - top_issues: List[Dict]  # Top 3 most critical
# - remaining_by_priority: Dict[Priority, List[Dict]]
# - total_count: int

# 2. Calculate pass probability (ATS mode only)
from backend.services.pass_probability_calculator import PassProbabilityCalculator

calculator = PassProbabilityCalculator()
prob = calculator.calculate_pass_probability(
    overall_score=75.0,
    breakdown=score_breakdown,
    auto_reject=False,
    critical_issues=[],
    keyword_details={"match_rate": 0.65},
    job_description="Job description text"
)

# prob contains:
# - overall_probability: float (0-100)
# - platform_breakdown: Dict[str, Dict]
# - confidence_level: str (high/moderate/low)
# - interpretation: str
# - color_code: str (green/yellow/red)
```

### Frontend

```tsx
import PassProbabilityCard from './PassProbabilityCard';
import SuggestionsPanel from './SuggestionsPanel';

// Enhanced SuggestionsPanel with Phase 3 features
<SuggestionsPanel
  suggestions={suggestions}
  currentScore={currentScore}
  onSuggestionClick={handleClick}
  onRescore={handleRescore}
  lastScored={lastScored}
  isRescoring={isRescoring}
  // Phase 3 additions
  prioritizedSuggestions={prioritizedSuggestions}
  passProbability={passProbability}
  mode="ats_simulation"  // or "quality_coach"
/>
```

---

## API Response Format

### Enhanced Score Response

```json
{
  "overallScore": 73.0,
  "breakdown": { /* ... */ },
  "issues": { /* ... */ },
  "strengths": [ /* ... */ ],
  "mode": "ats_simulation",

  // Phase 3 additions
  "prioritizedSuggestions": {
    "top_issues": [
      {
        "id": "1",
        "type": "keyword",
        "severity": "critical",
        "title": "Missing required keywords",
        "description": "Job requires Python, AWS, Docker",
        "impact_score": 240.0,
        "priority": "critical",
        "action_cta": "Add keywords"
      }
    ],
    "remaining_by_priority": {
      "critical": [],
      "important": [ /* ... */ ],
      "optional": [ /* ... */ ]
    },
    "total_count": 7
  },

  "passProbability": {
    "overall_probability": 70.5,
    "platform_breakdown": {
      "Taleo": {
        "probability": 65.2,
        "status": "fair"
      },
      "Workday": {
        "probability": 72.8,
        "status": "good"
      },
      "Greenhouse": {
        "probability": 75.5,
        "status": "good"
      }
    },
    "confidence_level": "moderate",
    "interpretation": "Moderate chance of passing ATS",
    "color_code": "yellow",
    "based_on_score": 73.0
  }
}
```

---

## Prioritization Algorithm

### Impact Score Formula

```
Impact Score = Base Impact Score × Severity Multiplier

Base Impact Scores:
- ATS_REJECTION: 100  (auto-reject keywords)
- KEYWORD_MATCH: 80   (keyword issues)
- FORMATTING: 60      (format issues)
- CONTENT_QUALITY: 40 (writing)
- MINOR: 20           (minor fixes)

Severity Multipliers:
- critical: 3.0
- high: 2.0
- warning: 1.5
- medium: 1.0
- suggestion: 0.7
- low: 0.5
- info: 0.3
```

### Priority Assignment

```
Impact Score >= 150  → CRITICAL
Impact Score >= 80   → IMPORTANT
Impact Score < 80    → OPTIONAL
```

### Examples

```python
# Example 1: Critical keyword issue
{
  "type": "keyword",
  "severity": "critical",
  "description": "auto-reject"
}
# → Base: 100 (ATS_REJECTION)
# → Multiplier: 3.0 (critical)
# → Impact: 300 → CRITICAL priority

# Example 2: Warning formatting issue
{
  "type": "formatting",
  "severity": "warning",
  "description": "format problem"
}
# → Base: 60 (FORMATTING)
# → Multiplier: 1.5 (warning)
# → Impact: 90 → IMPORTANT priority
```

---

## Pass Probability Calculation

### Base Probability Mapping

```
Overall Score → Base Probability:
90-100: 95%
80-89:  85%
70-79:  70%
60-69:  50%
50-59:  30%
0-49:   15%
```

### Adjustments

```python
# Auto-reject penalty
if auto_reject:
    probability *= 0.3  # -70%

# Critical issue penalty
for each critical_issue:
    probability *= 0.95  # -5% per issue
```

### Platform-Specific Calculation

```python
platform_prob = (
    base_prob * (1 - format_weight) +
    format_score * format_weight
) * platform_difficulty

# Platform difficulties:
Taleo: 0.85      (strictest)
Workday: 0.90    (moderate)
Greenhouse: 0.95 (lenient)

# Format weights (Taleo penalizes bad format more):
Taleo: 0.4
Workday: 0.3
Greenhouse: 0.2
```

### Confidence Level

```python
if has_job_description and keyword_match_rate and format_score >= 80:
    confidence = "high"
elif has_job_description or format_score >= 70:
    confidence = "moderate"
else:
    confidence = "low"
```

---

## Component API

### PassProbabilityCard

```tsx
interface PassProbabilityCardProps {
  passProbability: {
    overall_probability: number;
    platform_breakdown: {
      [platform: string]: {
        probability: number;
        status: string;
      };
    };
    confidence_level: string;
    interpretation: string;
    color_code: string;
    based_on_score: number;
  };
  className?: string;
}

// Usage
<PassProbabilityCard
  passProbability={passProbability}
  className="mb-6"
/>
```

### SuggestionsPanel (Updated)

```tsx
interface SuggestionsPanelProps {
  // Existing props
  suggestions: Suggestion[];
  currentScore: CurrentScore;
  onSuggestionClick: (suggestion: Suggestion) => void;
  onRescore: () => void;
  lastScored?: Date;
  isRescoring?: boolean;

  // Phase 3 additions (all optional for backward compatibility)
  prioritizedSuggestions?: PrioritizedSuggestions;
  passProbability?: PassProbability;
  mode?: 'ats_simulation' | 'quality_coach';
}
```

---

## Testing

### Run Unit Tests

```bash
cd backend
python -m pytest tests/test_phase3_ui.py -v
```

### Run Demo

```bash
cd backend
python demo_phase3.py
```

### Expected Output

```
🚨 TOP 3 CRITICAL ISSUES:

#1 - Missing required keywords
   Priority: CRITICAL
   Impact Score: 300.0
   Action: Add keywords

🔴 ATS Pass Probability: 70.5%
💬 Moderate chance of passing ATS

📍 PLATFORM BREAKDOWN:
  ⚠️  Taleo        65.2%  (fair)
  ✓  Workday      72.8%  (good)
  ✓  Greenhouse   75.5%  (good)
```

---

## Customization

### Adjust Priority Thresholds

```python
# In suggestion_prioritizer.py
class SuggestionPrioritizer:
    IMPACT_SCORES = {
        ImpactCategory.ATS_REJECTION: 150,  # Change from 100
        # ...
    }
```

### Add New Platforms

```python
# In pass_probability_calculator.py
class ATSPlatform(str, Enum):
    TALEO = "Taleo"
    WORKDAY = "Workday"
    GREENHOUSE = "Greenhouse"
    LEVER = "Lever"  # Add new platform

class PassProbabilityCalculator:
    PLATFORM_DIFFICULTY = {
        ATSPlatform.LEVER: 0.92,  # Add difficulty
    }

    PLATFORM_MARKET_SHARE = {
        ATSPlatform.LEVER: 0.08,  # Add market share
    }
```

### Customize Color Thresholds

```python
# In pass_probability_calculator.py
def _get_color_code(self, probability: float) -> str:
    if probability >= 85:  # Change from 80
        return "green"
    # ...
```

---

## Troubleshooting

### Issue: No prioritized suggestions showing

**Solution:** Ensure `enhanced_suggestions` exist in score result:

```python
# In scorer
score_result = SuggestionIntegrator.enrich_score_result(
    score_result=score_result,
    resume_data=resume_data,
    role=role,
    level=level,
    job_description=job_description
)
```

### Issue: Pass probability always None

**Solution:** Only calculated for ATS mode:

```python
if mode in ["ats_simulation", "ats"]:
    calculator = PassProbabilityCalculator()
    # ...
```

### Issue: Platform breakdown not showing

**Solution:** Check format score in breakdown:

```python
breakdown = {
    "formatting": {
        "score": 18,
        "maxScore": 20,
        "issues": []
    }
}
```

---

## Performance Tips

1. **Cache calculations:** Both services are stateless and can be cached
2. **Lazy loading:** Only calculate pass probability in ATS mode
3. **Debounce:** Don't recalculate on every keystroke
4. **Memoization:** Use `@lru_cache` for repeated calls

---

## Migration Guide

### Updating Existing Code

**Before:**
```python
# Old API
return ScoreResponse(
    overallScore=score,
    breakdown=breakdown,
    issues=issues,
    strengths=strengths,
    mode=mode
)
```

**After:**
```python
# Phase 3 API (backward compatible)
prioritizer = SuggestionPrioritizer()
prioritized = prioritizer.prioritize_suggestions(suggestions, top_n=3)

calculator = PassProbabilityCalculator()
pass_prob = calculator.calculate_pass_probability(...)

return ScoreResponse(
    overallScore=score,
    breakdown=breakdown,
    issues=issues,
    strengths=strengths,
    mode=mode,
    prioritizedSuggestions=prioritized,  # New
    passProbability=pass_prob  # New
)
```

---

## Best Practices

1. **Always provide job description:** Increases confidence level
2. **Show pass probability only in ATS mode:** Avoids confusion
3. **Top 3 is the sweet spot:** Don't overwhelm with top 5 or 10
4. **Progressive disclosure:** Hide details by default
5. **Clear CTAs:** Make action items obvious

---

## References

- **Implementation Report:** `/docs/PHASE3_IMPLEMENTATION_REPORT.md`
- **Unified Plan:** `/docs/UNIFIED_IMPLEMENTATION_PLAN.md`
- **Tests:** `/backend/tests/test_phase3_ui.py`
- **Demo:** `/backend/demo_phase3.py`

---

## Support

For questions or issues:
1. Check tests for examples
2. Run demo script
3. Review implementation report
4. Check API response format

---

**Last Updated:** February 20, 2026
**Phase:** 3 of Unified Implementation Plan
**Status:** ✅ Complete
