# ATS Scoring Recalibration

## Problem
Our scorer gives 68/100, Resume Worded gives 86/100 for the same resume (18-point gap).

## Industry Standard ATS Scoring (Resume Worded, Jobscan)

### Scoring Philosophy
- **Reward what's present**, don't over-penalize what's missing
- **Contextual scoring** - automation PM ≠ traditional PM
- **Generous thresholds** - 40% match is "good", not "poor"
- **Focus on critical issues only** - suggestions shouldn't reduce score significantly

### Score Distribution
1. **Contact Info (10 points)** - If name, email, phone exist → 10/10
2. **Format (20 points)** - If parseable → 18-20/20
3. **Content (25 points)** - If bullets with numbers exist → 20-23/25
4. **Keywords (15 points)** - 30% match → 8-10/15, 50% match → 12-15/15
5. **Length (10 points)** - 400-800 words → 10/10
6. **Role-specific (20 points)** - Any relevant experience → 15-18/20

### Key Differences from Our Scorer

#### Content Scoring (Currently 16/25, should be 22/25)
**Too Harsh:**
- Detecting "first-person pronouns" that don't exist
- Flagging "informal language" when none present
- Over-penalizing action verb coverage (we need 80%+, industry standard is 40%+)

**Fix:** Lower thresholds, focus on positive signals:
- 40% action verbs → 4/6 points (not 2/6)
- 40% quantified → 4/6 points (not 2/6)
- Remove false positive checks

#### Keywords Scoring (Currently 5/15, should be 10-12/15)
**Too Strict:**
- Expecting 60%+ match for full score (industry: 40%+)
- Keywords too narrow (missing automation-specific terms)

**Fix:**
- 30-40% match → 8-10/15 points
- 40-60% match → 10-13/15 points
- 60%+ match → 13-15/15 points
- Add more automation/operations keywords

#### Role-Specific Scoring (Currently 7/20, should be 16/20)
**Too Strict:**
- Same keyword matching as above
- Required skills are too narrow

**Fix:**
- Lower keyword threshold from 60% to 40% for full score
- Make "required skills" more flexible

## Target Score After Recalibration

With these changes:
- Contact: 10/10
- Formatting: 20/20
- **Content: 22/25** (+6 from lowered thresholds)
- **Keywords: 10/15** (+5 from broader matching)
- LengthDensity: 10/10
- **RoleSpecific: 16/20** (+9 from lowered thresholds)

**Total: 88/100** (matches Resume Worded range)

## Implementation Plan

1. Lower action verb threshold from 80% to 40% for good score
2. Lower quantified achievement threshold from 60% to 40%
3. Remove false positive checks (first-person, informal language)
4. Adjust keyword scoring: 30%→8pts, 40%→10pts, 50%→12pts, 60%→15pts
5. Add more automation keywords to product_manager role
6. Lower role-specific keyword threshold from 60% to 40%
