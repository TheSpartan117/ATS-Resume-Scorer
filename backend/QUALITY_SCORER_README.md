# Quality Mode Scorer

## Overview

The Quality Mode Scorer is a content-focused scoring system that evaluates resumes based on writing quality, achievement depth, and professional polish rather than just keyword matching.

## Scoring Breakdown (100 points total)

### 1. Content Quality (30 points)
Evaluates the quality and effectiveness of resume content:

- **Action Verbs (15 points)** - STRICT THRESHOLDS:
  - < 70%: 0 points
  - 70-89%: 7.5 points
  - 90%+: 15 points

- **Quantification (10 points)** - STRICT THRESHOLDS:
  - < 40%: 0 points
  - 40-59%: 5 points
  - 60%+: 10 points

- **Content Depth (5 points)**:
  - Bullet point completeness
  - Substantive descriptions
  - Complete thoughts

### 2. Achievement Depth (20 points)
Measures the specificity and impact of achievements:

- **Specific Metrics (10 points)**:
  - Impact statements (reduced by X%, increased Y)
  - Quantifiable results
  - Business outcomes

- **Vague Phrase Penalty (10 points)**:
  - Starts with 10 points
  - Deducts 2 points per vague phrase
  - Flags: "responsible for", "worked on", "helped with", etc.

### 3. Keywords/Fit (20 points)
Evaluates role relevance:

- **With Job Description**:
  - Required keywords: 15 points
  - Preferred keywords: 5 points

- **Without Job Description**:
  - Role-specific keywords: 20 points
  - Based on typical keywords for role and level

### 4. Polish (15 points)
Assesses professional presentation:

- **Grammar/Spelling (10 points)**:
  - Starts with 10 points
  - Deducts 1 point per error
  - Uses LanguageTool for detection

- **Professional Standards (5 points)**:
  - Email professionalism
  - Phone format consistency
  - LinkedIn presence
  - Location format

### 5. Readability (15 points)
Evaluates structure and clarity:

- **Structure (8 points)**:
  - Required sections present (3 points)
  - Bullet point usage (3 points)
  - Proper formatting (2 points)

- **Length Appropriateness (7 points)**:
  - Optimal: 400-800 words, 1-2 pages (7 points)
  - Good: 300-1000 words, 1-2 pages (5 points)
  - Acceptable: 200-1200 words (3 points)
  - Needs work: Outside ranges (1 point)

## Usage

```python
from services.scorer_quality import QualityScorer
from services.parser import ResumeData

scorer = QualityScorer()

result = scorer.score(
    resume_data=resume,
    role_id="software_engineer",
    level="senior",
    job_description=optional_jd  # Optional
)

# Result structure
{
    'score': 78.5,
    'breakdown': {
        'content_quality': {
            'score': 25.0,
            'max_score': 30,
            'details': {
                'action_verbs_score': 15.0,
                'action_verbs_feedback': 'Excellent action verb usage (92%)',
                'quantification_score': 10.0,
                'quantification_feedback': 'Excellent quantification (65%)',
                'depth_score': 5.0,
                'depth_feedback': 'Excellent bullet point quality'
            }
        },
        'achievement_depth': { ... },
        'keywords_fit': { ... },
        'polish': { ... },
        'readability': { ... }
    }
}
```

## Key Features

### Strict Thresholds
Unlike ATS mode which is more lenient, Quality Mode uses strict thresholds:
- Action verbs must be 90%+ for full points (vs 70% minimum)
- Quantification must be 60%+ for full points (vs 40% minimum)

### Validation Integration
Leverages the RedFlagsValidator to detect:
- Grammar and spelling errors
- Vague phrases
- Professional standard issues
- Bullet structure problems

### Role-Aware Scoring
Uses role taxonomy to evaluate:
- Role-appropriate action verbs
- Expected keywords for the role
- Level-appropriate experience expectations

### Detailed Feedback
Every category provides:
- Numeric score
- Maximum possible score
- Detailed breakdown
- Actionable feedback messages

## Scoring Philosophy

Quality Mode focuses on **content quality over keyword quantity**:

1. **Action-Oriented Writing**: Rewards strong action verbs that demonstrate leadership and impact
2. **Quantifiable Results**: Emphasizes measurable achievements over general statements
3. **Professional Polish**: Values error-free, well-formatted content
4. **Clear Communication**: Prioritizes readability and structure
5. **Role Relevance**: Considers context-appropriate keywords without being keyword-obsessed

## Scoring Ranges

- **85-100**: Excellent - Ready to submit
- **75-84**: Very Good - Minor improvements recommended
- **65-74**: Good - Some improvements needed
- **50-64**: Fair - Significant improvements required
- **Below 50**: Needs Work - Major revision needed

## Implementation Details

### Dependencies
- `RedFlagsValidator`: Grammar and content validation
- `keyword_extractor`: Keyword matching with synonyms
- `role_taxonomy`: Role-specific scoring data
- `parser`: Resume data structure

### Performance
- O(n) complexity where n = number of resume bullets
- Caches grammar checks to avoid redundant processing
- Efficient regex-based pattern matching

### Testing
Comprehensive test suite covers:
- All scoring categories
- Edge cases (empty resumes, no experience)
- Different quality levels
- Multiple roles and experience levels
- Detailed breakdown structure validation

## Future Enhancements

Potential improvements for future versions:
1. Machine learning for impact detection
2. Industry-specific thresholds
3. Custom weighting per role
4. Competitor comparison
5. Historical score tracking
