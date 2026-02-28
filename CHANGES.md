# Bug Fix Summary — `fix/bug-fixes-and-improvements`

**Branch:** `fix/bug-fixes-and-improvements`
**Commit:** `43a2f25`
**Date:** 28 Feb 2026
**Author:** Aishik Das

---

## Overview

This branch fixes 4 backend bugs and 1 frontend display bug that were causing incorrect scoring, false positive flags, and unreadable UI output.

---

## 1. Keyword Matching — Score Always Showing 0

**File:** `backend/services/hybrid_keyword_matcher.py`

**Problem:**
The hybrid matcher combines semantic similarity (70%) and exact match (30%). When a keyword like `sql` or `python` was literally present in the resume, it still scored ~0.51 and failed the 0.6 match threshold. This happened because cosine similarity between a short keyword and a long document is naturally low (~0.3–0.4), pulling the hybrid score below the threshold even for verbatim matches.

**Fix:**
Take the maximum of the exact score and the hybrid score, so a verbatim match always passes.

```python
# Before
return hybrid_score

# After
return max(exact_score, hybrid_score)
```

**Impact:** Keyword Matching score went from 0/25 to a non-zero value reflecting actual keyword presence.

---

## 2. Experience Parser — Multiple Jobs Lumped Into One

**File:** `backend/services/parser.py`

**Problem (a) — Multi-job blocks not split:**
When a resume had multiple work experiences, the parser treated all of them as one large block and only extracted the first job's details. Subsequent jobs were silently ignored.

**Fix:**
Added a `split_experience_entries()` function that detects job boundaries by looking for company name patterns (all-caps lines) followed by date ranges, then splits the text into individual job blocks before parsing each one.

**Problem (b) — Wrong format assumption:**
The parser assumed resumes follow `Title → Company → Date` order. The actual resume used `COMPANY: Location → Date → Title → bullets` order. This caused dates to be parsed as job titles and titles to be lost.

**Fix:**
Rewrote `parse_experience_entry()` to detect and handle three layout formats:
- Format A: `COMPANY → DATE → TITLE → bullets` (e.g. AMERICAN EXPRESS → Dec 2024–Present → Risk Analyst)
- Format B: `TITLE → COMPANY → DATE → bullets`
- Format C: `COMPANY → TITLE → DATE → bullets`

**Problem (c) — Uppercase ratio check failing on `COMPANY: Location` lines:**
`AMERICAN EXPRESS: Gurgaon, Haryana` has 17 uppercase letters out of 29 alphabetic characters = 0.586, just below the 0.6 detection threshold. This caused the company line to not be recognized.

**Fix:**
Only evaluate uppercase ratio on the part before the `:` separator.

```python
# Before
alpha = [c for c in line if c.isalpha()]

# After
first_part = re.split(r'[:\-,]', line.strip())[0].strip()
alpha = [c for c in first_part if c.isalpha()]
```

**Impact:** Parser now correctly extracts all jobs (e.g. 2 jobs found instead of 1), with correct titles, companies, and date ranges.

---

## 3. False Positive Employment Gaps

**File:** `backend/services/scorer_v3.py` and `backend/services/scorer_v3_adapter.py`

**Problem (a) — P6 penalty parameters always scoring 0%:**
The P6 scorers (Employment Gaps, Job Hopping, Formatting Errors) return a `penalty` key in their result dict, not a `score` key. But `scorer_v3.py` was reading `result.get('score', 0)`, which always returned 0. This made the percentage calculation `(0/max_penalty) * 100 = 0%`, triggering penalty flags even for clean resumes.

**Fix:**
Added dedicated handling for P6.1, P6.2, and P6.4 that reads the `penalty` key and computes the correct percentage:

```python
# P6.1: Employment Gaps — penalty range is 0 to -5
result = scorer.score(employment_history=experience)
penalty = result.get('penalty', 0)
pct = round(((5 + penalty) / 5) * 100, 1)  # 0 penalty → 100%, -5 penalty → 0%
```

**Problem (b) — Field name mismatch between parser and gap detector:**
The parser outputs experience entries with camelCase keys (`startDate`, `endDate`). The gap detector reads snake_case keys (`start_date`, `end_date`). This mismatch meant all dates were `None` from the gap detector's perspective, causing it to flag every resume as having gaps.

**Fix:**
Added snake_case aliases in `scorer_v3_adapter.py` before passing experience data to the gap detector:

```python
exp_copy['start_date'] = exp.get('startDate', '') or exp.get('start_date', '')
exp_copy['end_date'] = exp.get('endDate', '') or exp.get('end_date', '')
```

**Impact:** Resumes with no actual employment gaps no longer get flagged.

---

## 4. Cryptic P-Code Messages in Issues Panel

**File:** `backend/services/scorer_v3_adapter.py`

**Problem:**
The issues/suggestions panel was showing raw parameter codes like `P6.1: Score 0%` or `P1.1: Score 45%` instead of actionable improvement tips.

**Fix:**
Added a `_ISSUE_MESSAGES` dictionary mapping every parameter code to a human-readable message, and a `_get_issue_message()` method that formats it with context:

```python
_ISSUE_MESSAGES = {
    'P1.1': 'Required Keywords: Your resume is missing key terms from the job description...',
    'P6.1': 'Employment Gaps: Significant unexplained gaps found between jobs...',
    # ... all 23 parameters
}
```

**Impact:** The suggestions panel now shows clear, actionable improvement tips instead of internal parameter codes.

---

## 5. Raw Float Numbers in Score Display

**Files:**
- `frontend/src/components/CategoryBreakdown.tsx`
- `frontend/src/components/ModeIndicator.tsx`
- `frontend/src/components/SimplifiedIssuesList.tsx`
- `frontend/src/components/EnhancedResultsDisplay.tsx`

**Problem:**
Category scores were displaying as raw Python floats (e.g. `10.723809523809525/35`) because the backend accumulates scores via repeated addition of floats.

**Fix (backend):** Round accumulated scores to 2 decimal places in `scorer_v3.py`:

```python
# Before
category_scores[category]['score'] += result['score']

# After
category_scores[category]['score'] = round(
    category_scores[category]['score'] + result['score'], 2
)
```

**Fix (frontend):** Added `toFixed(1)` on all score display points as an additional safeguard:

```tsx
// Before
{categoryData.score}/{categoryData.maxScore}

// After
{Number(categoryData.score).toFixed(1)}/{categoryData.maxScore}
```

**Impact:** All scores now display cleanly (e.g. `10.7/35`).

---

## Files Changed

| File | Type | Change |
|---|---|---|
| `backend/services/hybrid_keyword_matcher.py` | Backend | `max(exact, hybrid)` to fix keyword threshold |
| `backend/services/parser.py` | Backend | Multi-job splitting, 3-format detection, uppercase fix |
| `backend/services/scorer_v3.py` | Backend | P6 penalty fix, `None` guard, score rounding |
| `backend/services/scorer_v3_adapter.py` | Backend | snake_case aliases, human-readable issue messages |
| `frontend/src/components/CategoryBreakdown.tsx` | Frontend | `toFixed(1)` on score |
| `frontend/src/components/ModeIndicator.tsx` | Frontend | `toFixed(1)` on score |
| `frontend/src/components/SimplifiedIssuesList.tsx` | Frontend | `toFixed(1)` on score |
| `frontend/src/components/EnhancedResultsDisplay.tsx` | Frontend | P-code to human-readable card renderer |

---

## Test Results (after fixes)

```
[1] Health check:           ✓
[2] Roles:                  11 categories, 3 levels ✓
[3] Upload + Score:         ✓  Overall score: 60.0
[4] Experience parsing:     2 jobs found ✓
     • Risk Management Analyst @ AMERICAN EXPRESS | Dec 2024 → Present
     • Strategy Consultant @ CAPGEMINI INVENT | Aug 2024 → Dec 2024
[5] Keyword Matching:       2.39/25 ✓  (non-zero confirmed)
[6] Category scores:        All clean, no long floats ✓
[7] Red Flags:              No false employment gap flags ✓

RESULT: ALL TESTS PASSED ✓
```
