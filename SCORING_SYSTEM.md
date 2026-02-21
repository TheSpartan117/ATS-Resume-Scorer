# ATS Resume Scorer - Scoring System Deep Dive

**Version**: 3.0
**Last Updated**: February 22, 2026

## Overview

The ATS Resume Scorer uses a comprehensive 21-parameter system to evaluate resumes across 6 major categories. This document explains each parameter in detail, how scores are calculated, and the research backing our methodology.

## Scoring Scale

- **Total Score**: 0-100 points
- **Parameters Total**: 130 points (bonus system allows excellence)
- **Final Score**: Capped at 100 points

## Rating System

| Score Range | Rating | Meaning |
|-------------|--------|---------|
| 85-100 | Excellent | ATS-optimized, highly competitive |
| 70-84 | Good | Strong resume, minor improvements needed |
| 50-69 | Fair | Needs significant improvements |
| 0-49 | Poor | Major overhaul required |

## Category Breakdown

### Category 1: Keyword Matching (25 points standard, 35 max)

#### P1.1: Required Keywords (25 points)
**What it measures**: Presence of essential role-specific keywords

**How it works**:
1. System loads required keywords for selected role (e.g., 28 for Product Manager)
2. Searches resume for each keyword (case-insensitive)
3. Scores incrementally: each matched keyword adds points
4. Formula: `points_per_keyword = min(25 / num_keywords, 1.67)`

**Example (Product Manager)**:
- Required keywords: product, requirements, agile, scrum, stakeholder, data, analytics, metrics, testing, technical, platform, API, integration, release, engineering, UI, UX, design, prototype, wireframe, process, workflow, roadmap, backlog, sprint, launch, deployment, iteration (28 total)
- Points per keyword: 25 / 28 = 0.89 pts
- If 11 matched: 11 × 0.89 = 9.8 points

**Recommendations**:
- Research job descriptions for your target role
- Include core technical terms naturally in experience bullets
- Don't keyword-stuff; integrate keywords into meaningful sentences

#### P1.2: Preferred Keywords (10 points)
**What it measures**: Advanced/specialized skills beyond basics

**How it works**:
1. System loads preferred keywords (32 for PM)
2. Matches similar to P1.1 but with lower point value
3. Formula: `points_per_keyword = min(10 / num_keywords, 1.0)`

**Example (Product Manager preferred)**:
- Keywords: AI, ML, machine learning, automation, cloud, SaaS, digital, transformation, SQL, dashboard, KPI, ROI, revenue, growth, conversion, funnel, Jira, optimization, A/B testing, MVP, go-to-market, PRD, cross-functional, user research, etc.
- Points per keyword: 10 / 32 = 0.31 pts
- If 13 matched: 13 × 0.31 = 4.0 points

**Bonus Potential**: +10 points (if all keywords matched in both P1.1 and P1.2)

---

### Category 2: Content Quality (35 points standard, 45 max)

#### P2.1: Action Verbs (15 points)
**What it measures**: Strength and impact of action verbs in experience bullets

**How it works**:
1. Extracts first verb from each bullet point
2. Classifies verb into 5 tiers:
   - **Tier 4** (Strategic): 4 pts - pioneered, architected, transformed
   - **Tier 3** (Leadership): 3 pts - led, managed, orchestrated
   - **Tier 2** (Achievement): 2 pts - developed, implemented, created
   - **Tier 1** (Operational): 1 pt - maintained, supported, assisted
   - **Tier 0** (Weak): 0 pts - worked, helped, responsible for
3. Averages points across all bullets
4. Scales to 15-point max

**Example**:
- 20 bullets: 5 tier-3, 10 tier-2, 5 tier-1
- Average: (5×3 + 10×2 + 5×1) / 20 = 2.0 pts/bullet
- Score: (2.0 / 4.0) × 15 = 7.5 points

**Verb System Details**:
- **236 verbs** total (expanded from 87 based on corpus analysis)
- **Data source**: 1000 manager resumes from academic corpus
- **High-frequency verbs captured**: managed (1018 uses), performed (873), configured (343)

**Recommendations**:
- Start bullets with strong action verbs (Led, Developed, Architected)
- Avoid weak verbs (Responsible for, Worked on, Helped with)
- Use variety - don't repeat the same verb

#### P2.2: Quantification (10 points)
**What it measures**: Use of metrics and numbers to quantify achievements

**How it works**:
1. Identifies numbers in experience bullets (%, $, K, M, B, etc.)
2. Classifies impact level:
   - **High impact**: Revenue ($), percentage improvements (%), growth metrics
   - **Medium impact**: Counts (users, projects, team size)
   - **Low impact**: Dates, version numbers
3. Calculates quantification percentage: `quantified_bullets / total_bullets`
4. Scores based on percentage:
   - ≥50%: 10 points (Excellent)
   - ≥30%: 7 points (Good)
   - ≥20%: 5 points (Fair)
   - <20%: 3 points (Needs improvement)

**Example**:
- 20 bullets total
- 12 with metrics: "Increased conversion by 25%", "Managed $2M budget", "Led team of 8"
- Quantification: 12/20 = 60%
- Score: 10 points

**Recommendations**:
- Add metrics wherever possible (%, $, time saved, users impacted)
- Be specific: "Increased sales by 30%" > "Increased sales significantly"
- Include context: team size, budget managed, scope of projects

#### P2.3: Achievement Depth (10 points)
**What it measures**: Completeness and depth of achievement descriptions

**How it works**:
1. Analyzes bullet length and structure
2. Checks for CAR (Challenge-Action-Result) framework
3. Identifies deep bullets (15+ words with impact indicators)
4. Calculates depth percentage
5. Scores based on percentage of deep bullets

**Scoring Tiers**:
- ≥40% deep bullets: 10 points
- ≥25%: 7 points
- ≥15%: 5 points
- <15%: 3 points

**Example of deep bullet**:
"Led cross-functional team of 12 to rebuild checkout flow, reducing cart abandonment by 35% and increasing Q4 revenue by $2.4M through A/B testing and user research"

#### P2.4: CAR Framework (5 points)
**What it measures**: Use of Challenge-Action-Result storytelling structure

**How it works**:
Looks for indicators of:
- **Challenge**: Problem, gap, challenge, issue, bottleneck
- **Action**: Led, developed, implemented, designed
- **Result**: Increased, reduced, improved, achieved (with metrics)

**Scoring**:
- High CAR usage (≥30%): 5 points
- Medium (≥15%): 3 points
- Low (<15%): 1 point

#### P2.5: Impact Scope (5 points)
**What it measures**: Scale and scope of impact (team, company, industry)

**How it works**:
Identifies scope indicators:
- **Team-level**: managed team, led squad, coordinated group
- **Company-level**: company-wide, organization, all teams
- **Industry-level**: market, industry, ecosystem

**Bonus Potential**: +10 points (if excel across all content quality parameters)

---

### Category 3: Format & Structure (15 points standard, 20 max)

#### P3.1: Page Count (5 points)
**What it measures**: Resume length appropriateness for experience level

**Scoring**:
- **Beginner** (0-3 yrs): 1 page = 5 pts, 2 pages = 3 pts, 3+ = 0 pts
- **Intermediary** (3-7 yrs): 1 page = 3 pts, 2 pages = 5 pts, 3+ = 2 pts
- **Senior** (7+ yrs): 1 page = 2 pts, 2 pages = 5 pts, 3 pages = 4 pts, 4+ = 0 pts

#### P3.2: Word Count (3 points)
**What it measures**: Appropriate word count for experience level

**Optimal Ranges**:
- **Beginner**: 400-600 words
- **Intermediary**: 500-800 words
- **Senior**: 600-1000 words

**Scoring**:
- Within optimal range: 3 points
- 80-120% of range: 2 points
- Outside range: 0-1 point

#### P3.3: Section Balance (5 points)
**What it measures**: Proper distribution of content across sections

**How it works**:
1. Calculates word percentage per section
2. Checks for keyword stuffing (Skills >30% of total)
3. Validates experience is primary focus (≥50%)

**Penalties**:
- Keyword stuffing: -2 points
- Poor balance: -1 point
- Minimal experience: -2 points

#### P3.4: ATS Formatting (7 points)
**What it measures**: ATS-friendly formatting (no tables, fancy fonts, text boxes)

**Penalties**:
- Tables: -2 pts (parsing issues)
- Text boxes: -2 pts (extraction fails)
- Headers/footers: -1 pt (inconsistent parsing)
- Images: -1 pt (unparseable)
- Fancy fonts: -1 pt (OCR errors)

**Clean format**: 7/7 points

**Bonus Potential**: +5 points (if excel in all format parameters)

---

### Category 4: Professional Polish (10 points standard, 15 max)

#### P4.1: Grammar & Spelling (10 points)
**What it measures**: Grammar, spelling, and language quality

**How it works**:
1. Uses LanguageTool for grammar checking
2. Categorizes errors by severity
3. Deducts points per error

**Penalties**:
- Spelling errors: -0.5 pts each
- Grammar errors: -0.3 pts each
- Capitalization: -0.2 pts each

**Scoring**:
- 0 errors: 10 points
- 1-3 minor: 8 points
- 4-7: 6 points
- 8+: 0-4 points

#### P4.2: Professional Standards (5 points)
**What it measures**: Professional language and formatting consistency

**How it works**:
Checks for:
- Contact information present (email, phone)
- No unprofessional language
- Consistent formatting (bullet styles, spacing)
- Professional email domain

**Penalties**:
- Missing contact: -2 pts
- Unprofessional email: -1 pt
- Inconsistent formatting: -1 pt
- Poor punctuation: -1 pt

**Bonus Potential**: +5 points (if excel in both polish parameters)

---

### Category 5: Experience Validation (10 points standard, 10 max)

#### P5.1: Years Alignment (4 points)
**What it measures**: Total experience matches claimed level

**How it works**:
1. Sums years from all experience entries
2. Compares to declared level
3. Flags mismatches

**Scoring**:
- Perfect match: 4 points
- Close match (±1 year): 3 points
- Mismatch: 0-2 points

#### P5.2: Career Recency (3 points)
**What it measures**: Recent work history (gaps, current employment)

**Scoring**:
- Currently employed: 3 points
- Left within 6 months: 2 points
- 6-12 months gap: 1 point
- 12+ months gap: 0 points

#### P5.3: Experience Depth (3 points)
**What it measures**: Sufficient detail per role

**How it works**:
- Counts bullets per role
- Flags roles with <2 bullets
- Scores based on average depth

---

### Category 6: Red Flags (0 points, penalties only)

#### P6.1: Employment Gaps (up to -5 pts)
**Penalties**:
- Gap >6 months: -2 pts per gap
- Gap >1 year: -3 pts per gap
- Multiple gaps: additional -1 pt

#### P6.2: Job Hopping (up to -3 pts)
**Penalties**:
- 3+ roles <1 year each: -3 pts
- 2 roles <1 year: -2 pts
- 1 role <6 months: -1 pt

#### P6.3: Repetition (up to -3 pts)
**Penalties**:
- Excessive bullet repetition: -2 pts
- Repeated phrases/keywords: -1 pt

#### P6.4: Formatting Errors (up to -2 pts)
**Penalties**:
- Date inconsistencies: -1 pt
- Mixed date formats: -1 pt

---

### Category 7: Readability (5 points)

#### P7.1: Readability Score (2 points)
**What it measures**: Text readability (Flesch-Kincaid level)

**Optimal**: Grade 10-12 (professional level)
**Penalties**: Too simple (<8) or too complex (>14)

#### P7.2: Bullet Structure (2 points)
**What it measures**: Proper bullet formatting

**Scoring**:
- Consistent bullet markers: +1 pt
- Appropriate bullet length (10-30 words): +1 pt

#### P7.3: Passive Voice (1 point)
**What it measures**: Active vs passive voice ratio

**Scoring**:
- <10% passive: 1 point
- 10-20%: 0.5 points
- >20%: 0 points

---

## Bonus System Explained

### How Bonuses Work

**Standard Category Maxes** (adds to 100):
- Keyword Matching: 25 pts
- Content Quality: 35 pts
- Format & Structure: 15 pts
- Professional Polish: 10 pts
- Experience Validation: 10 pts
- Readability: 5 pts

**Parameter Totals** (adds to 130):
- Keyword Matching: 35 pts (P1.1 + P1.2)
- Content Quality: 45 pts (P2.1-P2.5)
- Format & Structure: 20 pts (P3.1-P3.4)
- Professional Polish: 15 pts (P4.1-P4.2)
- Experience Validation: 10 pts (P5.1-P5.3)
- Readability: 5 pts (P7.1-P7.3)

**Bonus Potential**: +30 points total

### Example Bonus Scenario

**Excellent Resume**:
- Keyword Matching: 30/25 (+5 bonus from matching all required + preferred)
- Content Quality: 40/35 (+5 bonus from strong verbs, quantification, depth)
- Format & Structure: 20/15 (+5 bonus from perfect format)
- Professional Polish: 14/10 (+4 bonus from zero errors)
- **Total**: 104 raw points → **capped at 100**

### Why Bonuses?

1. **Rewards Excellence**: Going above and beyond gets recognized
2. **Easier to Reach 100**: Multiple paths to perfect score
3. **Forgiving**: Can score lower in one area, compensate in another
4. **Realistic**: Acknowledges resumes can be exceptional in multiple dimensions

---

## Research & Data Sources

### Resume Corpus Analysis

**Source**: https://github.com/florex/resume_corpus.git
- **Total Resumes**: 29,783
- **PM Resumes**: 371 analyzed
- **Manager Resumes**: 1,000 analyzed

**Research Paper**:
> Jiechieu, K.F.F., Tsopze, N. Skills prediction based on multi-label resume classification using CNN with model predictions explanation. Neural Comput & Applic (2020). https://doi.org/10.1007/s00521-020-05302-x

### Keyword Frequency Data (PM Resumes)

| Keyword | Frequency | Percentage |
|---------|-----------|------------|
| UI | 360/371 | 97% |
| AI | 352/371 | 95% |
| ML | 297/371 | 80% |
| data | 278/371 | 75% |
| agile | 226/371 | 61% |
| technical | 219/371 | 59% |
| testing | 215/371 | 58% |
| SQL | 212/371 | 57% |

### Action Verb Frequency (Manager Resumes)

| Verb | Uses | Rank |
|------|------|------|
| created | 1,415 | 1 |
| worked | 1,294 | 2 |
| developed | 1,138 | 3 |
| managed | 1,018 | 4 |
| provided | 888 | 5 |
| performed | 873 | 6 |
| designed | 727 | 7 |

---

## Calibration Results

**Test CVs vs ResumeWorded Targets**:

| Resume | Score | Target | Gap | Status |
|--------|-------|--------|-----|--------|
| Sabuj PM | 89 | 86 | +3 | ✅ Exceeded |
| Aishik PM | 81 | 81 | 0 | ✅ Perfect |
| Swastik PM | 64 | 65 | -1 | ✅ Close |

**Average Gap**: 1.3 points
**Accuracy**: 98.7%

---

## Improvement History

### February 2026 Updates

**Keyword Expansion**:
- Required: 19 → 28 (+47%)
- Preferred: 14 → 32 (+129%)
- Impact: +3-5 points per CV

**Action Verb Expansion**:
- Total: 87 → 236 (+171%)
- Added high-frequency: managed, performed, configured, migrated
- Impact: +0.4-1.0 points per CV

**Scoring Algorithm**:
- Changed from percentage-based tiers to incremental scoring
- Better CV differentiation
- More accurate point allocation

---

## Using This System

### For Job Seekers

1. **Upload your resume** (PDF or DOCX)
2. **Select your target role** (PM, Engineer, Data Scientist, etc.)
3. **Choose experience level** (Beginner, Intermediary, Senior)
4. **Review your score** across all 21 parameters
5. **Follow suggestions** for specific improvements
6. **Re-score** after making changes

### For Developers

See [DEVELOPMENT_GUIDE.md](./DEVELOPMENT_GUIDE.md) for:
- Adding new parameters
- Modifying scoring weights
- Extending role-specific keywords
- Contributing to the project

---

## Further Reading

- **[KEYWORDS_AND_VERBS.md](./KEYWORDS_AND_VERBS.md)** - Complete keyword and verb lists
- **[API_GUIDE.md](./API_GUIDE.md)** - API endpoint documentation
- **[SYSTEM_OVERVIEW.md](./SYSTEM_OVERVIEW.md)** - High-level architecture
