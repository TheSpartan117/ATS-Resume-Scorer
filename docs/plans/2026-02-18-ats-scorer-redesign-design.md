# ATS Resume Scorer Redesign - Design Document

**Date:** 2026-02-18
**Status:** Approved
**Author:** Design brainstorming session with user

## Executive Summary

Complete redesign of the ATS Resume Scorer to implement harsh but realistic grading that accurately reflects real-world ATS filtering and recruiter expectations. The current system is too lenient (giving 90+ scores to minimal resumes), lacks comprehensive validation checks, and has insufficient keyword coverage.

**Key Changes:**
- Expand from 12 to 44 scoring parameters
- Implement strict thresholds (50%+ keyword match required)
- Dual-mode system with distinct scoring criteria
- Keyword database expansion: 7 → 50-100 keywords per role/level
- Add comprehensive red flag detection (employment gaps, date errors, grammar, etc.)
- Target score distribution: 0-40 (30%), 41-60 (40%), 61-75 (20%), 76-85 (8%), 86-100 (2%)

## Problem Statement

### Current Issues

1. **Excessive Default Scores**
   - No job description? Get 10/15 (67%) for keywords automatically
   - No role data? Get 10/20 (50%) for role scoring
   - System gives "participation trophy" scores

2. **Overly Generous Thresholds**
   - 40% action verbs = 83% score (should require 70%+)
   - 30% quantified bullets = 83% score (should require 60%+)
   - 30% keyword match = 53% score (real ATS needs 50%+)

3. **Limited Penalties**
   - Resume with no experience section can still score 70+
   - Zero quantified achievements still gets 1/6 points

4. **Missing 32 Parameters**
   - No employment gap detection
   - No date validation
   - No grammar/spelling checks
   - No experience-level alignment
   - No professional standards validation

5. **Insufficient Keyword Coverage**
   - Only 7 keywords per role/level
   - Missing synonyms (Python vs Python3)
   - No modern tech terms (Kubernetes, Terraform, etc.)

## Design Philosophy

### Harsh But Realistic Grading

**Target Score Distribution:**
- **0-40 (Poor):** 30% of resumes - needs major work
- **41-60 (Fair):** 40% of resumes - needs improvement
- **61-75 (Good):** 20% of resumes - competitive
- **76-85 (Excellent):** 8% of resumes - top 10%
- **86-100 (Outstanding):** 2% of resumes - top 2%

**Rationale:** Users need brutal honesty about ATS pass rates. Better to set low expectations and help them improve than give false confidence.

### Dual-Mode System

**Mode 1: ATS Simulation**
- **Purpose:** "Will this resume pass the robot?"
- **Focus:** Parseability, keyword matching, red flags
- **Average Score:** 45-55 (without job description)
- **Use Case:** Pre-submission check for ATS compatibility

**Mode 2: Quality Coach**
- **Purpose:** "Will this impress a human recruiter?"
- **Focus:** Content quality, writing, professional polish
- **Average Score:** 50-65
- **Use Case:** Content improvement and storytelling

**Why Keep Dual Modes:** Real hiring involves two stages - automated screening (ATS) and human review. Users need to understand they must pass both.

## Architecture

### High-Level Structure

```
backend/
├── services/
│   ├── scorer_v2.py                 # Main scoring orchestrator
│   ├── ats_mode_scorer.py          # ATS Simulation scoring logic
│   ├── quality_mode_scorer.py      # Quality Coach scoring logic
│   ├── keyword_matcher.py          # Keyword/synonym matching engine
│   ├── red_flags_validator.py      # Validation checks (44 params)
│   ├── grammar_checker.py          # LanguageTool integration
│   └── parser.py                   # EXISTING: Keep as-is
├── data/
│   ├── keywords/
│   │   ├── onet_skills.json        # O*NET bulk data
│   │   ├── linkedin_skills.json    # Scraped LinkedIn terms
│   │   └── role_keywords.json      # Merged taxonomy
│   └── synonyms/
│       └── skill_synonyms.json     # Synonym mappings
└── scripts/
    ├── setup_onet_data.py          # Download O*NET database
    ├── scrape_linkedin_skills.py   # One-time LinkedIn scrape
    ├── build_synonym_database.py   # Build synonym mappings
    └── merge_keyword_sources.py    # Merge all data sources
```

### Modular Design Principles

1. **Separation of Concerns**
   - Each mode is independent (ATS vs Quality)
   - Red flags validator is standalone
   - Keyword matcher is reusable

2. **Data-Driven Configuration**
   - Keywords stored as JSON (easy updates)
   - Thresholds configurable without code changes
   - Synonym mappings externalized

3. **Backward Compatibility**
   - Keep existing API endpoints
   - Same response format (different scores)
   - Old scorer preserved as scorer_legacy.py

4. **Performance First**
   - All keyword lookups: O(1) with hash maps
   - Grammar checking: Cached per content hash
   - Target: <2 seconds for full scoring

## Scoring Systems

### ATS Simulation Mode (100 points)

| Category | Points | Key Criteria |
|----------|--------|--------------|
| Keywords/Skills Match | 35 | Role keywords (50-100 per level), synonyms, JD matching |
| Red Flags | 20 | Employment gaps, date errors, job hopping, level misalignment |
| Experience Structure | 20 | Complete dates, company names, titles, bullet formatting |
| Formatting/Parseability | 20 | PDF/DOCX, page count, word count, clean sections |
| Contact Info | 5 | Email, phone, name, location, LinkedIn |

**Keyword Scoring Thresholds:**
- 0-30% match: 0-5 pts (Critical - likely auto-rejected)
- 31-50% match: 6-15 pts (Warning - borderline)
- 51-70% match: 16-25 pts (Good - passes screening)
- 71-90% match: 26-32 pts (Excellent - strong match)
- 91-100% match: 33-35 pts (Outstanding - perfect fit)

**Red Flag Deductions:**
- Employment gap 9-18 months: -3 pts
- Employment gap 18+ months: -5 pts
- Date errors (end before start): -4 pts
- Job hopping (<1 year, 2+ times): -3 pts
- Experience-level mismatch: -4 pts
- Unprofessional email: -3 pts
- Missing dates: -2 pts per entry

### Quality Coach Mode (100 points)

| Category | Points | Key Criteria |
|----------|--------|--------------|
| Content Quality | 30 | Action verbs (90%+ bullets), quantification (60%+ bullets) |
| Achievement Depth | 20 | Specific vs vague, impact clarity, CAR structure |
| Keywords/Role Fit | 20 | Keywords used in context (not just listed) |
| Professional Polish | 15 | Grammar/spelling, verb tense, no buzzwords |
| Formatting/Readability | 15 | Clean structure, consistent bullets, section order |

**Content Quality Thresholds (Strict):**

Action Verbs:
- 90-100%: Full 12 points
- 70-89%: 9 points
- 50-69%: 6 points
- <50%: 3 points

Quantification:
- 60-100%: Full 12 points
- 40-59%: 9 points
- 20-39%: 6 points
- <20%: 3 points

## Comprehensive Parameter List (44 Total)

### Employment History Validation (6 parameters)

1. **Employment Gaps:** 9+ months = warning, 18+ months = critical
2. **Date Validation:** End before start, future dates, format errors
3. **Date Format Consistency:** All dates use same format (Jan 2020 vs 01/2020)
4. **Job Hopping:** <1 year tenure at 2+ jobs
5. **Experience-Level Alignment:** Years vs claimed seniority
   - Entry: 0-3 years
   - Mid: 2-6 years
   - Senior: 5-12 years
   - Lead: 8-15 years
   - Executive: 12+ years
6. **Missing Dates:** Any experience entry without start/end date

### Content Depth Analysis (3 parameters)

7. **Achievement Depth:** Detect vague phrases ("responsible for", "worked on")
8. **Bullet Point Length:** 50-150 chars optimal
9. **Bullet Structure:** Complete thoughts, not fragments

### Section Completeness (4 parameters)

10. **Required Sections:** Experience, Education, Skills must be present
11. **Section Ordering:** Experience before Education for experienced pros (2+ years)
12. **Recency Check:** Most recent role should be within 2 years
13. **Summary/Objective:** Presence recommended

### Professional Standards (4 parameters)

14. **Email Professionalism:** firstname.lastname@ format, avoid outdated providers
15. **LinkedIn URL Validation:** Proper format linkedin.com/in/username
16. **Phone Format Consistency:** Use one format throughout
17. **Location Format:** "City, State" or "City, Country"

### Grammar & Spelling (4 parameters)

18. **Typo Detection:** Using LanguageTool library
19. **Grammar Errors:** Sentence structure, agreement issues
20. **Verb Tense Consistency:** Present for current job, past for previous
21. **Capitalization:** Job titles, company names properly capitalized

### Formatting Details (4 parameters)

22. **Bullet Consistency:** All bullets use same marker (• vs -)
23. **Font Readability:** No decorative fonts that break ATS parsing
24. **Section Header Consistency:** All CAPS or all Title Case
25. **Header/Footer Content:** Critical info shouldn't be in headers/footers

### Content Analysis (10 parameters)

26. **Action Verbs:** % of bullets starting with strong action verbs
27. **Quantified Achievements:** % of bullets with metrics
28. **Passive Voice:** Count of passive constructions
29. **Professional Language:** No first-person pronouns, informal words
30. **Buzzword Density:** Count of empty buzzwords (synergy, rockstar, ninja)
31. **Skills Density:** Skills mentioned in experience, not just listed
32. **Keyword Context:** Keywords used in achievement context
33. **Sentence Structure:** Proper bullet length, no run-ons
34. **First-Person Pronouns:** Resume should use third-person format
35. **Informal Language:** Avoid "stuff", "things", "lots of"

### Metadata (9 parameters)

36. **Page Count:** 1-2 pages optimal
37. **Word Count:** 300-800 words optimal
38. **File Format:** PDF preferred, DOCX acceptable
39. **Contact Completeness:** Name, email, phone, location, LinkedIn
40. **Company Recognition:** Fortune 500 companies noted
41. **Education Relevance:** Degree aligns with target role
42. **Overqualification:** PhD for entry-level flags warning
43. **Career Progression:** Promotions within companies noted
44. **Industry Consistency:** Flag if >2 industry switches

## Keyword Database System

### Three-Layer Architecture

**Layer 1: O*NET Foundation**
- Source: US Department of Labor O*NET database
- Coverage: 1000+ occupations
- Content: Core skills, knowledge areas, abilities
- Update: Quarterly via bulk data download
- Authoritative but may lack cutting-edge tech terms

**Layer 2: LinkedIn Modern Tech Terms**
- Source: One-time scrape of LinkedIn Skills pages
- Coverage: Top 100 skills per role
- Content: Trending skills, frameworks, tools
- Update: One-time during implementation
- Use user's LinkedIn credentials from job search project

**Layer 3: Synonym & Variation Mappings**
- Python → [Python, Python3, py, CPython, PyPy]
- JavaScript → [JavaScript, JS, ECMAScript, ES6, ES2020]
- React → [React, ReactJS, React.js, React Native]
- AWS → [AWS, Amazon Web Services, EC2, S3, Lambda]
- 100+ technology synonym mappings

### Target Coverage

**Per Role/Level: 50-100 Keywords**

Example - Software Engineer (Mid Level):
- Required Core: 8 keywords (programming, git, testing, etc.)
- Technical Skills: 35 keywords (Python, React, AWS, Docker, etc.)
- Practices: 15 keywords (agile, code review, TDD, API design, etc.)
- Soft Skills: 7 keywords (collaboration, mentoring, debugging, etc.)
- **Total: 65 keywords** (vs current 7)

### Matching Algorithm

**Multi-Strategy Approach:**
1. **Text Normalization:** Lowercase, lemmatize
2. **Synonym Expansion:** Expand keywords with synonyms
3. **Context Awareness:** Keywords in achievement context score higher
4. **Fuzzy Matching:** 80% similarity threshold for typos
5. **Deduplication:** Python/Python3 counts as one match

**Performance:** O(1) keyword lookup using hash sets

## Red Flags Validation System

### RedFlagsValidator Class

Comprehensive validation checking all 44 parameters, returning issues categorized by severity:
- **Critical:** Likely auto-rejection (employment gaps 18+, date errors, missing sections)
- **Warning:** Significant issues (employment gaps 9-18, job hopping, grammar errors)
- **Suggestion:** Improvements (bullet length, buzzwords, LinkedIn format)

### Validation Categories

**Employment History:**
- Gap detection with flexible thresholds (9/18 month)
- Date validation (chronological order, format consistency)
- Job tenure analysis
- Experience-level alignment with flexible ranges

**Content Quality:**
- Vague phrase detection ("responsible for", "worked on")
- Bullet length analysis (50-150 chars)
- Structure validation (complete thoughts)

**Professional Standards:**
- Email format validation (avoid coolguy420@...)
- LinkedIn URL format
- Phone/location consistency

**Grammar & Spelling:**
- LanguageTool library integration (local, unlimited)
- Spelling error detection
- Grammar issue flagging
- Verb tense consistency checking

**Formatting:**
- Bullet character consistency
- Font readability (flag decorative fonts)
- Section header consistency
- Header/footer content warnings

## Implementation Plan

### Phase 1: Data Setup (Day 1-2)

**Scripts to Execute:**
1. `setup_onet_data.py` - Download O*NET bulk data
2. `scrape_linkedin_skills.py` - One-time LinkedIn scrape using credentials from ~/job-search-project/
3. `build_synonym_database.py` - Create 100+ synonym mappings
4. `merge_keyword_sources.py` - Merge all data into role_keywords.json

**Verification:**
- Confirm 50-100 keywords per role/level
- Verify synonym mappings work
- Test keyword matching accuracy

### Phase 2: Core Implementation (Day 3-10)

**Components to Build:**
1. `keyword_matcher.py` - O(1) matching with synonym support
2. `red_flags_validator.py` - All 44 parameter checks
3. `grammar_checker.py` - LanguageTool integration with caching
4. `ats_mode_scorer.py` - ATS Simulation scoring logic
5. `quality_mode_scorer.py` - Quality Coach scoring logic
6. `scorer_v2.py` - Main orchestrator

**Dependencies:**
- `language-tool-python` library (~50MB)
- O*NET data files
- LinkedIn scraped data
- Synonym database

### Phase 3: Testing (Day 11-14)

**Test Resume Corpus:**
- Outstanding (90+): 4 resumes across roles
- Excellent (80+): 4 resumes
- Good (65+): 4 resumes
- Fair (50+): 4 resumes
- Poor (30-): 4 resumes
- **Total: 20 test resumes**

**Test Coverage:**
- Unit tests for each scoring component
- Integration tests for end-to-end flow
- Manual verification of score distributions
- Threshold adjustment based on results

### Phase 4: API Integration (Day 15-17)

**Changes:**
1. Update `/api/score` endpoint to use scorer_v2
2. Add `mode` parameter ('ats' or 'quality')
3. Keep scorer_legacy.py for comparison
4. Update response format to include mode-specific breakdowns

**Backward Compatibility:**
- Existing API contracts maintained
- Same response structure
- Add new fields, don't remove old ones

### Phase 5: Documentation & Launch (Day 18-21)

**Deliverables:**
1. Design document (this file)
2. Implementation plan document
3. API documentation updates
4. User-facing scoring criteria guide
5. Migration notes

**Launch:**
- Deploy to production
- Monitor score distributions
- Collect user feedback
- Adjust thresholds if needed (within 10% of target)

## Testing Strategy

### Test Pyramid

**Unit Tests (60%):**
- Keyword matching accuracy
- Red flag detection precision
- Grammar checking integration
- Scoring calculation logic
- Threshold validation

**Integration Tests (30%):**
- End-to-end resume flow
- Mode switching
- API response format
- Caching behavior

**Manual Testing (10%):**
- Score distribution verification
- User experience validation
- Edge case exploration

### Success Criteria

**Score Distribution Validation:**
After testing 100 real resumes, distribution should match:
- 0-40: ~30 resumes
- 41-60: ~40 resumes
- 61-75: ~20 resumes
- 76-85: ~8 resumes
- 86-100: ~2 resumes

**Performance:**
- Full scoring: <2 seconds
- Keyword matching: <100ms
- Grammar check (cached): <50ms
- Redis/cache hit rate: >80%

**Accuracy:**
- Keyword match precision: >90%
- Red flag detection: >95% (no false negatives)
- Grammar detection: >85% (LanguageTool accuracy)

## Performance Optimization

### Optimization Strategies

**1. Keyword Matching - O(1) Lookup**
```python
# Use hash sets for instant lookup
keyword_set = set(keywords)
resume_tokens = set(tokenize(resume_text))
matches = keyword_set.intersection(resume_tokens)
```

**2. Grammar Checking - Content-Based Caching**
```python
# Cache by MD5 hash of content
text_hash = hashlib.md5(text.encode()).hexdigest()
if text_hash in cache:
    return cache[text_hash]
```

**3. Lazy Loading - Only Load When Needed**
```python
# LanguageTool only loads for Quality mode
@property
def grammar_checker(self):
    if self._grammar_checker is None:
        self._grammar_checker = GrammarChecker()
    return self._grammar_checker
```

**4. Data Pre-loading**
- Load all keywords into memory at startup
- Build hash sets for O(1) lookup
- Pre-process synonym mappings

### Expected Performance

- **Startup Time:** <5 seconds (load all data)
- **ATS Mode Scoring:** 0.5-1.0 seconds
- **Quality Mode Scoring:** 1.0-1.5 seconds (includes grammar check)
- **Re-scoring (cached):** <0.5 seconds
- **Memory Footprint:** ~100MB (data + LanguageTool)

## Migration & Rollout

### Rollout Strategy

**Big Bang Approach:**
- Complete rebuild in one release
- No phased rollout (system is fundamentally broken)
- Clear communication to users about scoring changes

**Rationale:**
- Current system gives false confidence (90+ scores for poor resumes)
- No existing users will complain (system is new/early stage)
- Piecemeal changes would cause score inconsistency
- Harsh grading requires all 44 parameters working together

### Communication Plan

**User-Facing Changes:**
1. **Scoring Explanation Page:**
   - "Why did my score drop?" FAQ
   - Explanation of harsh but realistic grading
   - Breakdown of all 44 parameters
   - Examples of each score tier

2. **Mode Selection Guide:**
   - When to use ATS vs Quality mode
   - How to interpret dual scores
   - Action items for each mode

3. **Keyword Transparency:**
   - Show matched/missing keywords
   - Suggest specific terms to add
   - Explain synonym matching

### Backward Compatibility

**Preserved:**
- API endpoint paths
- Response JSON structure
- File upload flow
- Authentication

**Changed:**
- Score values (will be lower)
- Issue severity classifications
- Keyword match percentages

**Added:**
- Mode parameter ('ats' or 'quality')
- Extended breakdown fields
- Red flag details

## Risk Mitigation

### Identified Risks

**1. LinkedIn Scraping Failure**
- **Risk:** LinkedIn blocks scraping or changes structure
- **Mitigation:** Use O*NET as fallback, manually curate top 50 modern terms
- **Impact:** Medium (reduces keyword coverage by 30%)

**2. LanguageTool Performance**
- **Risk:** Grammar checking slows down scoring
- **Mitigation:** Aggressive caching, make optional for free users
- **Impact:** Low (caching solves 90% of cases)

**3. Score Shock for Users**
- **Risk:** Users upset their 90+ score drops to 50
- **Mitigation:** Clear communication, show what's missing, provide actionable feedback
- **Impact:** High (user churn risk) - Address with excellent UX

**4. O*NET Data Staleness**
- **Risk:** Government data lacks newest tech terms
- **Mitigation:** Layer 2 (LinkedIn) + Layer 3 (custom) fill gaps
- **Impact:** Low (supplemental layers cover modern terms)

**5. False Positive Red Flags**
- **Risk:** Valid career breaks flagged as gaps
- **Mitigation:** Flexible thresholds (9/18 months), clear suggestions to explain
- **Impact:** Medium (can reduce with user education)

## Future Enhancements (Post-Launch)

### Phase 2 Features (Optional)

1. **AI-Powered Suggestions:**
   - Use Claude API to generate bullet rewrites
   - Suggest specific metrics to add
   - Rewrite vague phrases

2. **Industry-Specific Scoring:**
   - Different thresholds by industry (tech vs finance vs healthcare)
   - Industry-specific red flags
   - Custom keyword databases per industry

3. **ATS System Profiles:**
   - Score against specific ATS systems (Greenhouse vs Workday vs Taleo)
   - Each ATS has different parsing quirks
   - System-specific optimization suggestions

4. **Resume Version Comparison:**
   - Track score changes across edits
   - A/B test different versions
   - Show what changed and why

5. **Job Description Auto-Import:**
   - Parse job postings from URLs
   - Extract keywords automatically
   - Match resume against specific JD

6. **Batch Processing:**
   - Score multiple resumes at once
   - Comparative analysis
   - Recruiter/hiring manager view

## Success Metrics

### Key Performance Indicators

**Product Metrics:**
- Average ATS score: 45-55 (target distribution)
- Average Quality score: 50-65 (target distribution)
- Score improvement after edits: >15 points average
- User retention: >60% return for re-scoring

**Technical Metrics:**
- API response time: <2 seconds (p95)
- Cache hit rate: >80%
- Grammar check accuracy: >85%
- Keyword match precision: >90%

**Business Metrics:**
- User satisfaction with feedback: >4.0/5.0
- Premium conversion (for advanced features): >5%
- Resume quality improvement (external validation): measurable

## Conclusion

This redesign transforms the ATS Resume Scorer from a lenient "participation trophy" system into a rigorous, realistic tool that provides actionable feedback. By expanding from 12 to 44 parameters, implementing strict thresholds, and building a comprehensive keyword database (7 → 50-100 keywords per role), we give users the harsh truth about their resume's competitiveness.

The dual-mode system (ATS Simulation + Quality Coach) educates users about the two-stage hiring process while providing specific, actionable improvements. With proper testing, clear communication, and excellent UX, this redesign will help users create resumes that actually pass ATS screening and impress human recruiters.

**Next Steps:**
1. Review and approve this design document
2. Create implementation plan with detailed task breakdown
3. Begin Phase 1: Data Setup
4. Proceed through 21-day implementation timeline
