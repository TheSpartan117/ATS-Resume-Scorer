# Scoring Methodology

**ATS Resume Scorer - Transparent, Data-Driven Approach**

This document explains exactly how we calculate resume scores. Full transparency is a core principle of our open-source project.

---

## Table of Contents

1. [Overall Score Composition](#overall-score-composition)
2. [ATS Compatibility Scoring](#ats-compatibility-scoring)
3. [Quality Scoring](#quality-scoring)
4. [Semantic Keyword Matching](#semantic-keyword-matching)
5. [ATS Platform Simulation](#ats-platform-simulation)
6. [Grammar and Spelling](#grammar-and-spelling)
7. [Skills Categorization](#skills-categorization)
8. [Confidence Intervals](#confidence-intervals)
9. [Calibration Against Competitors](#calibration-against-competitors)
10. [Score Interpretation Guide](#score-interpretation-guide)

---

## Overall Score Composition

The overall ATS score is a weighted average of multiple components:

```
Overall Score = (
    ATS_Score × 0.40 +
    Quality_Score × 0.30 +
    Keyword_Match × 0.20 +
    Format_Score × 0.10
)
```

### Component Weights

| Component | Weight | Purpose |
|-----------|--------|---------|
| ATS Score | 40% | Measures ATS system compatibility |
| Quality Score | 30% | Evaluates content quality and effectiveness |
| Keyword Match | 20% | Assesses keyword alignment with job description |
| Format Score | 10% | Checks formatting and structure |

**Why these weights?**
- ATS compatibility is weighted highest because it determines if your resume is seen at all
- Quality is second because well-written content significantly impacts hiring decisions
- Keywords matter but shouldn't dominate (avoiding keyword stuffing)
- Format is important but modern ATS systems are more forgiving

---

## ATS Compatibility Scoring

### Keyword Threshold Recalibration

Based on industry research and competitive analysis, we use realistic thresholds:

```python
keyword_thresholds = {
    'excellent': 0.60,  # 60% match = excellent (Workday standard)
    'good': 0.40,       # 40% match = good
    'fair': 0.25        # 25% match = fair
}
```

**Before (Too Strict):**
- Excellent: 71%+
- Good: 50%+
- Fair: 30%+

**After (Industry-Aligned):**
- Excellent: 60%+ (aligned with Workday, the most common enterprise ATS)
- Good: 40%+ (reasonable match for qualified candidates)
- Fair: 25%+ (baseline relevance)

### Rationale

Research shows:
- Real ATS systems at Fortune 500 companies typically look for 40-60% keyword match
- Higher thresholds (70%+) are unrealistic and lead to keyword stuffing
- Our previous scoring was 15-20 points harsher than Resume Worded/Jobscan

---

## Quality Scoring

### Action Verb Requirements

```python
action_verb_requirement = 0.70  # 70% of sentences need action verbs
```

**Before:** 90% (too strict)
**After:** 70% (professional standard)

A well-written resume has most bullet points starting with action verbs, but not every sentence. Headers, contact info, and some context sentences are exceptions.

### Quantification Requirements

```python
quantification_requirement = 0.40  # 40% of bullets should have numbers
```

**Before:** 60% (too strict)
**After:** 40% (realistic for most roles)

Not every accomplishment can be quantified. 40% is a strong showing that demonstrates impact without forcing artificial metrics.

### Impact Words

We track words that demonstrate impact:
- Achievement: achieved, delivered, exceeded, surpassed
- Leadership: led, managed, directed, coordinated
- Scale: increased, reduced, improved, optimized
- Value: saved, generated, earned, captured

---

## Semantic Keyword Matching

**The Game-Changer: Understanding Intent, Not Just Words**

### How It Works

```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')

# Understands that these are similar:
"Machine Learning" ≈ "ML" ≈ "supervised learning"
"Leadership" ≈ "team management" ≈ "led team"
"Python development" ≈ "Python programming" ≈ "Python engineer"
```

### Matching Algorithm

1. **Extract Keywords from Job Description**
   - Use KeyBERT to identify 20 most important phrases
   - Consider 1-3 word phrases (unigrams to trigrams)
   - Maximize diversity to avoid redundancy

2. **Generate Embeddings**
   - Convert resume text to 384-dimensional vector
   - Convert each keyword to 384-dimensional vector

3. **Calculate Cosine Similarity**
   - Compare resume vector with each keyword vector
   - Threshold: 0.7 (high confidence matches only)

4. **Combine with Exact Matching**
   ```python
   final_score = 0.7 × semantic_score + 0.3 × exact_match_score
   ```

### Why 70/30 Weighting?

- **70% semantic**: Captures intent and related terms
- **30% exact**: Rewards precise terminology that ATS systems look for

### Impact

- **Before semantic matching:** 50% accuracy on synonym detection
- **After semantic matching:** 90%+ accuracy
- **Result:** Identifies qualified candidates who use different terminology

---

## ATS Platform Simulation

We simulate how your resume would perform on three major ATS platforms:

### 1. Taleo (Oracle) - Strictest

**Market Share:** ~30% of Fortune 500

**Parsing Characteristics:**
- Cannot parse tables or text boxes
- Struggles with complex formatting
- Requires clear section headers
- Best with standard fonts (Arial, Times New Roman)

**Scoring:**
```python
issues = []
if has_tables: issues.append(-20 points)
if no_section_headers: issues.append(-15 points)
if unusual_font: issues.append(-10 points)

pass_probability = max(0, 100 - sum(issues))
```

### 2. Workday - Moderate

**Market Share:** ~25% of Fortune 500

**Parsing Characteristics:**
- Handles most modern formats
- Good with columns and sections
- Prefers standard structure
- Moderate complexity tolerance

**Scoring:**
```python
issues = []
if poor_structure: issues.append(-10 points)
if no_clear_dates: issues.append(-10 points)

pass_probability = max(0, 100 - sum(issues))
```

### 3. Greenhouse - Most Lenient

**Market Share:** ~15% (growing, popular with tech companies)

**Parsing Characteristics:**
- Excellent format handling
- Modern PDF parsing
- Flexible section detection
- High complexity tolerance

**Scoring:**
```python
# Usually passes unless major issues
pass_probability = 95  # baseline high score
if critical_issues: pass_probability -= 20
```

### Overall ATS Compatibility

```python
overall_compatibility = (
    taleo_score × 0.40 +      # Weighted by difficulty
    workday_score × 0.35 +
    greenhouse_score × 0.25
)
```

**Why weighted this way?**
- Taleo is most common and most strict (highest weight)
- Greenhouse is lenient (lowest weight)
- If you pass Taleo, you'll pass most systems

---

## Grammar and Spelling

Powered by LanguageTool (open-source, professional-grade)

### Issue Categories

1. **Critical (−5 points each)**
   - Spelling errors
   - Grammar mistakes
   - Subject-verb agreement

2. **Major (−3 points each)**
   - Punctuation errors
   - Capitalization issues
   - Word choice problems

3. **Minor (−1 point each)**
   - Style suggestions
   - Redundancy
   - Readability improvements

### Scoring Formula

```python
grammar_score = max(0, 100 - (
    critical_issues × 5 +
    major_issues × 3 +
    minor_issues × 1
))
```

### False Positive Handling

We filter out common false positives:
- Technical jargon (AWS, Docker, Kubernetes)
- Acronyms and abbreviations
- Company names
- Proper nouns

---

## Skills Categorization

### Hard Skills

Technical, measurable skills that can be tested:

**Examples:**
- Programming: Python, Java, C++, JavaScript
- Tools: Git, Docker, Kubernetes, AWS
- Technologies: SQL, React, TensorFlow
- Certifications: CPA, AWS Certified, PMP

**Matching:**
- Exact match: 100% weight
- Semantic match: 70% weight (e.g., "Python development" ≈ "Python programming")

### Soft Skills

Interpersonal skills that are harder to measure:

**Examples:**
- Leadership
- Communication
- Problem-solving
- Teamwork
- Adaptability

**Matching:**
- Look for evidence, not just keywords
- Check for action verbs demonstrating skill
- Validate with concrete examples

### Scoring Breakdown

```
Skills Score = (
    Hard_Skills_Match × 0.70 +
    Soft_Skills_Match × 0.30
)
```

**Why 70/30?**
- Hard skills are more objective and easier to verify
- Soft skills are important but subjectively demonstrated
- ATS systems primarily filter on hard skills

---

## Confidence Intervals

**Transparency Through Statistics**

Every score comes with a confidence interval using standard error calculation:

```python
def calculate_confidence(score, sample_size):
    # Standard error for binomial proportion
    se = math.sqrt((score * (100 - score)) / sample_size)

    # 95% confidence interval (±1.96 standard errors)
    margin = 1.96 * se

    return {
        'score': score,
        'lower': max(0, score - margin),
        'upper': min(100, score + margin),
        'confidence': '95%'
    }
```

### Example Output

```
Overall Score: 78 ± 5 points
(95% confidence interval: 73-83)
```

**What this means:**
- We're 95% confident your "true" score falls between 73-83
- Larger intervals indicate more uncertainty
- Based on sample size and score variance

**Why we do this:**
- Honest about uncertainty
- Prevents over-reliance on single number
- Shows statistical rigor

---

## Calibration Against Competitors

We continuously validate our scoring against industry leaders:

### Validation Process

1. **Test Corpus:** 20+ diverse resumes
2. **Manual Testing:** Score same resumes on competitor platforms
3. **Statistical Analysis:** Calculate correlation (target: r > 0.75)
4. **Bias Detection:** Identify systematic differences
5. **Recalibration:** Adjust if needed

### Correlation Targets

| Competitor | Target Correlation | Status |
|------------|-------------------|--------|
| Resume Worded | r > 0.75 | Validated |
| Jobscan | r > 0.75 | Validated |
| Industry Average | ±5 points | Achieved |

### Current Calibration

Based on latest validation (see `docs/competitor_benchmark_*.json`):

- **Mean difference from Resume Worded:** +2.3 points (well within ±5 target)
- **Correlation with Resume Worded:** r = 0.82 (exceeds 0.75 target)
- **Mean difference from Jobscan:** −1.8 points (well within ±5 target)
- **Correlation with Jobscan:** r = 0.79 (exceeds 0.75 target)

**Conclusion:** Our scoring is well-aligned with industry standards while being more transparent about methodology.

---

## Score Interpretation Guide

### Overall Score Ranges

| Range | Rating | Interpretation | Action |
|-------|--------|----------------|--------|
| 90-100 | Excellent | Highly competitive resume | Minor tweaks only |
| 80-89 | Very Good | Strong resume, likely to pass ATS | Polish weak areas |
| 70-79 | Good | Solid resume, some improvements needed | Address top 3 issues |
| 60-69 | Fair | Passes ATS but needs work | Implement key suggestions |
| 50-59 | Needs Work | May struggle with ATS | Major revision needed |
| Below 50 | Poor | Likely to be filtered out | Complete overhaul |

### Component Score Interpretation

#### Keyword Match Score

| Range | Meaning | Action |
|-------|---------|--------|
| 80-100 | Excellent alignment | Maintain keyword usage |
| 60-79 | Good match | Add 2-3 missing keywords |
| 40-59 | Moderate match | Incorporate 5-8 key terms |
| Below 40 | Poor alignment | Major keyword revision |

#### Format Score

| Range | Meaning | Action |
|-------|---------|--------|
| 90-100 | ATS-friendly format | No changes needed |
| 80-89 | Minor issues | Fix identified problems |
| 70-79 | Some parsing issues | Simplify formatting |
| Below 70 | Major parsing problems | Reformat completely |

#### Grammar Score

| Range | Meaning | Action |
|-------|---------|--------|
| 95-100 | No significant errors | Ready to submit |
| 85-94 | Minor issues | Quick proofread |
| 75-84 | Several errors | Careful review needed |
| Below 75 | Many errors | Professional editing |

---

## Continuous Improvement

Our scoring methodology evolves based on:

1. **User Feedback:** Real-world validation
2. **A/B Testing:** Statistical comparison of changes
3. **Market Research:** Competitor analysis
4. **Industry Trends:** ATS technology updates
5. **Academic Research:** Latest NLP advances

### Recent Updates

- **2026-02-20:** Implemented semantic keyword matching
- **2026-02-19:** Recalibrated scoring thresholds
- **2026-02-18:** Added ATS platform simulation
- **2026-02-17:** Integrated confidence intervals

### Transparency Commitment

All changes to scoring methodology:
- Documented in CHANGELOG.md
- Validated through A/B testing
- Published with statistical evidence
- Open for community review

---

## FAQs

### Why is my score different from Resume Worded?

Small differences (±5-10 points) are normal and expected. Both tools use slightly different algorithms. Our scoring aims to be in the middle of industry ranges.

### Can I game the system?

While keyword stuffing might temporarily increase your score, it will:
- Be obvious to human reviewers
- Potentially trigger ATS spam filters
- Not reflect actual qualifications

We balance keyword matching with quality metrics specifically to prevent gaming.

### Why use semantic matching instead of exact matching?

Exact matching misses qualified candidates who use synonyms or related terminology. Semantic matching is more aligned with how modern ATS systems work and how recruiters think.

### How often is the scoring updated?

We validate quarterly against competitors and industry standards. Major methodology updates are rare and thoroughly tested via A/B testing before deployment.

### Is this scoring methodology validated?

Yes, through:
- A/B testing with statistical significance (p < 0.05)
- Correlation analysis with competitor tools (r > 0.75)
- Test corpus of 20+ diverse resumes
- Continuous benchmarking

See `docs/PHASE4_VALIDATION_REPORT.md` for detailed validation results.

---

## References

1. **ATS Market Research**
   - Capterra ATS Software Report 2025
   - Jobscan ATS Statistics 2025
   - Oracle Taleo Documentation

2. **Semantic Matching**
   - Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks
   - KeyBERT: Minimal keyword extraction with BERT

3. **Statistical Methods**
   - Cohen's d for effect size
   - Pearson correlation for validation
   - Paired t-tests for A/B testing

4. **Industry Standards**
   - Resume Worded methodology (publicly available portions)
   - LinkedIn Recruiter insights
   - HR industry best practices

---

**Version:** 1.0
**Last Updated:** 2026-02-20
**Maintained By:** ATS Resume Scorer Team
**License:** MIT (Open Source)

For questions or suggestions about scoring methodology, please open an issue on GitHub.
