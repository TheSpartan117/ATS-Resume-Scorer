# CV Parser Testing & Validation Plan

**Purpose:** Ensure parser improvements achieve 90-95% accuracy across diverse CV formats
**Timeline:** 2 weeks for comprehensive testing
**Owner:** Engineering Team

---

## Testing Strategy Overview

### 3-Phase Approach

1. **Unit Tests** (2 days) - Test individual parsing functions
2. **Integration Tests** (3 days) - Test with real CV corpus
3. **Regression Tests** (Ongoing) - Prevent accuracy degradation

### Success Criteria

| Metric | Current | Target | Critical Threshold |
|--------|---------|--------|-------------------|
| Overall Accuracy | 40-60% | 90-95% | > 85% |
| Section Detection | 60% | 95%+ | > 90% |
| Institution Names | 40% | 90%+ | > 85% |
| Duplicate Entries | 30% | 0% | < 5% |
| Skills Quality | 30% | 80%+ | > 70% |
| Contact Info | 70% | 95%+ | > 90% |

---

## Phase 1: Unit Tests (2 days)

### Test Suite 1: Text Cleaning

**File:** `backend/tests/test_parser_text_cleaning.py`

```python
import pytest
from backend.services.parser import clean_spacing_artifacts

class TestTextCleaning:
    """Test spacing artifact removal"""

    def test_basic_spacing_artifact(self):
        """Test 'I N D I A N' → 'INDIAN'"""
        assert clean_spacing_artifacts('I N D I A N') == 'INDIAN'

    def test_institution_name(self):
        """Test full institution name cleaning"""
        input_text = 'I N DI AN I N STI T UTE OF T ECHN OLOGY'
        expected = 'INDIAN INSTITUTE OF TECHNOLOGY'
        assert clean_spacing_artifacts(input_text) == expected

    def test_company_name(self):
        """Test company name with artifacts"""
        assert clean_spacing_artifacts('A I R  I N D I A') == 'AIR INDIA'

    def test_mixed_spacing(self):
        """Test mixed normal and artifact spacing"""
        input_text = 'T E C H  Corp International'
        expected = 'TECH Corp International'
        assert clean_spacing_artifacts(input_text) == expected

    def test_no_artifact(self):
        """Test normal text passes through unchanged"""
        text = 'Stanford University'
        assert clean_spacing_artifacts(text) == text

    def test_empty_string(self):
        """Test empty string handling"""
        assert clean_spacing_artifacts('') == ''

    def test_all_caps_with_spaces(self):
        """Test 'M B A' → 'MBA'"""
        assert clean_spacing_artifacts('M B A') == 'MBA'

    def test_partial_artifacts(self):
        """Test 'B T E C H' → 'BTECH'"""
        assert clean_spacing_artifacts('B T E C H') == 'BTECH'

    @pytest.mark.parametrize('input_text,expected', [
        ('I N D I A N', 'INDIAN'),
        ('T E C H N O L O G Y', 'TECHNOLOGY'),
        ('M A S T E R', 'MASTER'),
        ('B A C H E L O R', 'BACHELOR'),
        ('E N G I N E E R I N G', 'ENGINEERING')
    ])
    def test_common_words(self, input_text, expected):
        """Test common words with spacing artifacts"""
        assert clean_spacing_artifacts(input_text) == expected
```

**Run:** `pytest backend/tests/test_parser_text_cleaning.py -v`

---

### Test Suite 2: Section Detection

**File:** `backend/tests/test_parser_section_detection.py`

```python
import pytest
from backend.services.parser import extract_resume_sections

class TestSectionDetection:
    """Test section header detection with variations"""

    def test_standard_headers(self):
        """Test basic section headers"""
        text = """
        EXPERIENCE
        Software Engineer at Tech Corp

        EDUCATION
        Bachelor of Science

        SKILLS
        Python, Java
        """
        sections = extract_resume_sections(text)
        assert len(sections['experience']) > 0
        assert len(sections['education']) > 0
        assert len(sections['skills']) > 0

    def test_header_variations(self):
        """Test various header formats"""
        text = """
        EXPERIENCE SUMMARY
        Developer role

        EDUCATIONAL BACKGROUND
        Master's Degree

        TECHNICAL SKILLS
        JavaScript, React
        """
        sections = extract_resume_sections(text)
        assert len(sections['experience']) > 0
        assert len(sections['education']) > 0
        assert len(sections['skills']) > 0

    def test_professional_summary_header(self):
        """Test 'Professional Summary' detected as experience"""
        text = """
        PROFESSIONAL SUMMARY
        10 years of software development
        """
        sections = extract_resume_sections(text)
        assert len(sections['experience']) > 0 or len(sections.get('summary', [])) > 0

    def test_career_history_header(self):
        """Test 'Career History' detected as experience"""
        text = """
        CAREER HISTORY
        Senior Developer
        Tech Company
        """
        sections = extract_resume_sections(text)
        assert len(sections['experience']) > 0

    def test_case_insensitive_detection(self):
        """Test headers in different cases"""
        test_cases = [
            'EXPERIENCE',
            'Experience',
            'experience',
            'ExPeRiEnCe'
        ]
        for header in test_cases:
            text = f"{header}\nSoftware Engineer"
            sections = extract_resume_sections(text)
            assert len(sections['experience']) > 0, f"Failed for: {header}"

    def test_multiple_sections_same_type(self):
        """Test CV with multiple experience sections"""
        text = """
        PROFESSIONAL EXPERIENCE
        Job 1

        WORK HISTORY
        Job 2
        """
        sections = extract_resume_sections(text)
        # Should merge into one experience list
        assert len(sections['experience']) >= 1

    def test_section_order_independence(self):
        """Test sections detected regardless of order"""
        text = """
        SKILLS
        Python, Java

        EXPERIENCE
        Developer

        EDUCATION
        Bachelor's Degree
        """
        sections = extract_resume_sections(text)
        assert len(sections['skills']) > 0
        assert len(sections['experience']) > 0
        assert len(sections['education']) > 0
```

**Run:** `pytest backend/tests/test_parser_section_detection.py -v`

---

### Test Suite 3: Education Parsing & Deduplication

**File:** `backend/tests/test_parser_education.py`

```python
import pytest
from backend.services.parser import parse_education_entry, split_education_entries

class TestEducationParsing:
    """Test education entry parsing and deduplication"""

    def test_basic_education_entry(self):
        """Test simple education entry"""
        text = """
        Bachelor of Science in Computer Science
        Stanford University
        2015
        """
        entry = parse_education_entry(text)
        assert 'bachelor' in entry['degree'].lower()
        assert 'stanford' in entry['institution'].lower()
        assert '2015' in entry['graduationDate']

    def test_education_with_location(self):
        """Test education with location"""
        text = """
        Master of Business Administration
        Harvard Business School - Boston, MA
        2020
        """
        entry = parse_education_entry(text)
        assert 'master' in entry['degree'].lower()
        assert 'harvard' in entry['institution'].lower()
        assert 'boston' in entry['location'].lower()

    def test_split_multiple_degrees(self):
        """Test splitting multiple education entries"""
        text = """
        Bachelor of Technology (ECE)
        National Institute of Technology, Durgapur
        2010 - 2014

        Master of Business Administration
        Indian Institute of Technology, Kharagpur
        2018 - 2020
        """
        entries = split_education_entries(text)
        assert len(entries) == 2
        assert 'bachelor' in entries[0].lower()
        assert 'master' in entries[1].lower()

    def test_deduplication(self):
        """Test duplicate education entries are removed"""
        text = """
        Master of Business Administration
        Indian Institute of Technology

        Master of Business Administration
        Indian Institute of Technology
        """
        entries = split_education_entries(text)
        assert len(entries) == 1, "Should deduplicate identical entries"

    def test_partial_duplicate_prevention(self):
        """Test entries that look like duplicates but split across lines"""
        text = """
        MASTER OF BUSINESS ADMINISTRATION
        INDIAN INSTITUTE OF TECHNOLOGY, Kharagpur
        """
        entries = split_education_entries(text)
        assert len(entries) == 1, "Should not create multiple entries from one degree"

    def test_different_degree_types(self):
        """Test various degree formats"""
        test_cases = [
            ("Bachelor of Science", "bachelor"),
            ("B.Tech", "btech"),
            ("Master of Arts", "master"),
            ("MBA", "mba"),
            ("PhD in Computer Science", "phd"),
            ("Associate Degree", "associate"),
            ("High School Diploma", "high school")
        ]
        for degree_text, expected_keyword in test_cases:
            text = f"{degree_text}\nSome University\n2020"
            entry = parse_education_entry(text)
            assert expected_keyword.lower() in entry['degree'].lower(), f"Failed for: {degree_text}"

    def test_education_with_gpa(self):
        """Test education entry with GPA"""
        text = """
        Bachelor of Science in Computer Science
        MIT
        GPA: 3.9/4.0
        2019
        """
        entry = parse_education_entry(text)
        assert entry['gpa'] == '3.9' or '3.9' in entry['gpa']
```

**Run:** `pytest backend/tests/test_parser_education.py -v`

---

### Test Suite 4: Skills Extraction

**File:** `backend/tests/test_parser_skills.py`

```python
import pytest
from backend.services.parser import extract_resume_sections

class TestSkillsExtraction:
    """Test skills extraction and filtering"""

    def test_comma_separated_skills(self):
        """Test standard comma-separated skills"""
        text = """
        SKILLS
        Python, Java, JavaScript, React, Docker, Kubernetes
        """
        sections = extract_resume_sections(text)
        skills = sections['skills']
        assert 'Python' in skills
        assert 'Java' in skills
        assert 'React' in skills
        assert len(skills) >= 6

    def test_bullet_point_skills(self):
        """Test skills with bullet points"""
        text = """
        SKILLS
        • Python
        • JavaScript
        • AWS
        """
        sections = extract_resume_sections(text)
        skills = sections['skills']
        assert 'Python' in skills
        assert 'JavaScript' in skills
        assert 'AWS' in skills

    def test_filter_sentence_fragments(self):
        """Test filtering out sentence fragments"""
        text = """
        SKILLS
        Python, Java
        Experience in developing pricing models
        Deep understanding of digital transformation
        Docker, Kubernetes
        """
        sections = extract_resume_sections(text)
        skills = sections['skills']
        # Should have Python, Java, Docker, Kubernetes
        assert 'Python' in skills
        assert 'Docker' in skills
        # Should NOT have sentence fragments
        assert 'Experience in developing pricing models' not in skills
        assert 'Deep understanding of digital transformation' not in skills

    def test_deduplication(self):
        """Test skills are deduplicated"""
        text = """
        SKILLS
        Python, Java, Python, JavaScript, Java
        """
        sections = extract_resume_sections(text)
        skills = sections['skills']
        # Count occurrences
        python_count = sum(1 for s in skills if s.lower() == 'python')
        java_count = sum(1 for s in skills if s.lower() == 'java')
        assert python_count == 1, "Python should appear only once"
        assert java_count == 1, "Java should appear only once"

    def test_compound_skills(self):
        """Test multi-word skills are preserved"""
        text = """
        SKILLS
        Machine Learning, Natural Language Processing, Computer Vision
        """
        sections = extract_resume_sections(text)
        skills = sections['skills']
        # Should keep as compound terms
        assert any('Machine Learning' in s for s in skills) or \
               any('machine learning' in s.lower() for s in skills)

    def test_technical_abbreviations(self):
        """Test technical abbreviations (C++, C#, Node.js)"""
        text = """
        SKILLS
        C++, C#, Node.js, ASP.NET, Vue.js
        """
        sections = extract_resume_sections(text)
        skills = sections['skills']
        assert any('C++' in s or 'c++' in s.lower() for s in skills)
        assert any('Node' in s for s in skills)

    def test_max_50_skills_limit(self):
        """Test skills limited to 50"""
        # Generate 100 skills
        skills_list = [f"Skill{i}" for i in range(100)]
        text = f"SKILLS\n{', '.join(skills_list)}"
        sections = extract_resume_sections(text)
        skills = sections['skills']
        assert len(skills) <= 50, "Should limit to 50 skills"
```

**Run:** `pytest backend/tests/test_parser_skills.py -v`

---

## Phase 2: Integration Tests (3 days)

### Test Suite 5: Real CV Corpus Testing

**Goal:** Test parser on 50+ diverse real CVs

#### Step 1: Build Test Corpus (Day 1)

**Collect CVs from:**
1. Production uploads: `/Users/sabuj.mondal/ats-resume-scorer/backend/storage/uploads/`
2. Test samples from team members
3. Online CV templates (various formats)

**Diversity Matrix:**

| Category | Count | Examples |
|----------|-------|----------|
| **Layout Types** | | |
| Standard (text-based) | 10 | Traditional format |
| Table-based | 10 | Modern ATS-friendly |
| Two-column | 10 | European style |
| Creative/Designer | 5 | Portfolio style |
| **Industries** | | |
| Technology | 15 | Software, IT |
| Business | 10 | MBA, Consulting |
| Healthcare | 5 | Doctors, nurses |
| Education | 5 | Teachers, professors |
| Other | 5 | Various |
| **Experience Levels** | | |
| Entry-level | 10 | 0-2 years |
| Mid-level | 15 | 3-7 years |
| Senior | 15 | 8-15 years |
| Executive | 10 | 15+ years |
| **Total** | **50** | |

#### Step 2: Create Ground Truth Labels (Day 1-2)

**File:** `backend/tests/fixtures/cv_corpus_labels.json`

```json
{
  "cvs": [
    {
      "filename": "791201e4-be38-4885-ad55-1da24e46167a.pdf",
      "ground_truth": {
        "contact": {
          "name": "Candidate Name",
          "email": "email@example.com",
          "phone": "(555) 123-4567",
          "linkedin": "linkedin.com/in/profile"
        },
        "experience_count": 3,
        "education_count": 2,
        "skills_count": 15,
        "education_degrees": [
          "Master of Business Administration",
          "Bachelor of Technology"
        ],
        "institutions": [
          "Indian Institute of Technology",
          "National Institute of Technology"
        ]
      }
    }
  ]
}
```

**Manual Review Process:**
1. For each CV, manually review and extract:
   - Contact info (name, email, phone, LinkedIn)
   - Number of experience entries
   - Number of education entries
   - Education degrees and institutions
   - Top 15 skills
2. Save to JSON file
3. Use as test oracle

#### Step 3: Automated Corpus Testing (Day 2-3)

**File:** `backend/tests/test_parser_corpus.py`

```python
import pytest
import json
from pathlib import Path
from backend.services.parser import parse_pdf

class TestCVCorpus:
    """Integration tests with real CV corpus"""

    @pytest.fixture
    def corpus_labels(self):
        """Load ground truth labels"""
        with open('backend/tests/fixtures/cv_corpus_labels.json') as f:
            return json.load(f)['cvs']

    def test_full_corpus(self, corpus_labels):
        """Test parser on entire corpus"""
        results = {
            'total': len(corpus_labels),
            'passed': 0,
            'failed': 0,
            'failures': []
        }

        for cv_label in corpus_labels:
            filename = cv_label['filename']
            ground_truth = cv_label['ground_truth']

            # Parse CV
            with open(f'backend/storage/uploads/{filename}', 'rb') as f:
                result = parse_pdf(f.read(), filename)

            # Validate results
            passed = True
            errors = []

            # Check contact info
            if result.contact.get('email') != ground_truth['contact']['email']:
                errors.append(f"Email mismatch: {result.contact.get('email')} != {ground_truth['contact']['email']}")
                passed = False

            # Check counts
            if len(result.experience) != ground_truth['experience_count']:
                errors.append(f"Experience count: {len(result.experience)} != {ground_truth['experience_count']}")
                passed = False

            if len(result.education) != ground_truth['education_count']:
                errors.append(f"Education count: {len(result.education)} != {ground_truth['education_count']}")
                passed = False

            # Check institution names
            for expected_institution in ground_truth['institutions']:
                found = any(expected_institution.lower() in edu.get('institution', '').lower()
                           for edu in result.education)
                if not found:
                    errors.append(f"Missing institution: {expected_institution}")
                    passed = False

            # Check duplicates
            degrees = [edu.get('degree', '') for edu in result.education]
            if len(degrees) != len(set(degrees)):
                errors.append("Duplicate education entries detected")
                passed = False

            if passed:
                results['passed'] += 1
            else:
                results['failed'] += 1
                results['failures'].append({
                    'filename': filename,
                    'errors': errors
                })

        # Print summary
        accuracy = (results['passed'] / results['total']) * 100
        print(f"\n=== Corpus Test Results ===")
        print(f"Total CVs: {results['total']}")
        print(f"Passed: {results['passed']}")
        print(f"Failed: {results['failed']}")
        print(f"Accuracy: {accuracy:.1f}%")

        # Print failures
        if results['failures']:
            print(f"\n=== Failures ===")
            for failure in results['failures']:
                print(f"\n{failure['filename']}:")
                for error in failure['errors']:
                    print(f"  - {error}")

        # Assert target accuracy
        assert accuracy >= 85, f"Accuracy {accuracy:.1f}% below target 85%"

    def test_no_spacing_artifacts(self, corpus_labels):
        """Test institution names have no spacing artifacts"""
        for cv_label in corpus_labels:
            filename = cv_label['filename']
            with open(f'backend/storage/uploads/{filename}', 'rb') as f:
                result = parse_pdf(f.read(), filename)

            for edu in result.education:
                institution = edu.get('institution', '')
                # Check for spacing pattern: 'I N D I A N'
                has_artifact = bool(re.search(r'\b([A-Z]\s){3,}', institution))
                assert not has_artifact, f"Spacing artifact in: {institution}"

    def test_no_duplicate_education(self, corpus_labels):
        """Test no duplicate education entries"""
        for cv_label in corpus_labels:
            filename = cv_label['filename']
            with open(f'backend/storage/uploads/{filename}', 'rb') as f:
                result = parse_pdf(f.read(), filename)

            degrees = [edu.get('degree', '').lower()[:30] for edu in result.education]
            unique_degrees = set(degrees)
            assert len(degrees) == len(unique_degrees), \
                f"Duplicate education in {filename}: {degrees}"
```

**Run:** `pytest backend/tests/test_parser_corpus.py -v -s`

---

### Test Suite 6: Edge Cases

**File:** `backend/tests/test_parser_edge_cases.py`

```python
import pytest
from backend.services.parser import parse_pdf, parse_docx

class TestEdgeCases:
    """Test parser on edge cases and unusual formats"""

    def test_cv_with_no_sections(self):
        """Test CV with no clear section headers"""
        # Should handle gracefully, not crash
        pass

    def test_cv_with_table_layout(self):
        """Test CV where entire content is in tables"""
        pass

    def test_cv_with_two_column_layout(self):
        """Test two-column CV (common in Europe)"""
        pass

    def test_cv_with_emoji_decorations(self):
        """Test CV with emoji in section headers (🎓 Education)"""
        pass

    def test_cv_with_photos(self):
        """Test CV with candidate photo"""
        # Should not affect parsing
        pass

    def test_minimal_cv(self):
        """Test very short CV (< 100 words)"""
        pass

    def test_very_long_cv(self):
        """Test CV with 5+ pages"""
        pass

    def test_non_english_cv(self):
        """Test CV with some non-English content"""
        # Should still extract English sections
        pass

    def test_cv_with_special_characters(self):
        """Test CV with special characters in names (José, Müller)"""
        pass
```

---

## Phase 3: Regression Testing (Ongoing)

### Automated Regression Suite

**Goal:** Prevent accuracy from degrading after code changes

**Setup:**
1. Save 20 representative CVs as permanent fixtures
2. Run regression tests after every parser code change
3. Alert if accuracy drops below 85%

**File:** `backend/tests/test_parser_regression.py`

```python
import pytest
from backend.services.parser import parse_pdf

class TestRegression:
    """Regression tests to ensure accuracy doesn't degrade"""

    @pytest.fixture
    def regression_cvs(self):
        """Load regression test CVs"""
        return [
            'regression_cv_1.pdf',
            'regression_cv_2.pdf',
            # ... 20 total
        ]

    def test_regression_suite(self, regression_cvs):
        """Run full regression suite"""
        passed = 0
        for cv_file in regression_cvs:
            with open(f'backend/tests/fixtures/regression/{cv_file}', 'rb') as f:
                result = parse_pdf(f.read(), cv_file)
                # Validate against saved expected output
                if self._validate_result(result, cv_file):
                    passed += 1

        accuracy = (passed / len(regression_cvs)) * 100
        assert accuracy >= 85, f"Regression: accuracy {accuracy}% below 85%"

    def _validate_result(self, result, cv_file):
        """Validate result against expected output"""
        # Load expected from fixtures/regression/{cv_file}.expected.json
        # Compare and return True/False
        pass
```

**CI/CD Integration:**
```yaml
# .github/workflows/test.yml
name: Parser Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run parser tests
        run: |
          pytest backend/tests/test_parser_*.py -v
          pytest backend/tests/test_parser_regression.py -v
      - name: Check accuracy threshold
        run: |
          python scripts/check_parser_accuracy.py --threshold 85
```

---

## Metrics & Reporting

### Accuracy Metrics

**Calculate for each CV:**
```python
def calculate_accuracy(parsed, ground_truth):
    """Calculate accuracy score for a CV"""
    scores = {
        'contact': {
            'email': 1 if parsed.contact.get('email') == ground_truth['contact']['email'] else 0,
            'phone': 1 if parsed.contact.get('phone') == ground_truth['contact']['phone'] else 0,
            'name': 1 if parsed.contact.get('name') == ground_truth['contact']['name'] else 0,
        },
        'experience_count': 1 if len(parsed.experience) == ground_truth['experience_count'] else 0,
        'education_count': 1 if len(parsed.education) == ground_truth['education_count'] else 0,
        'no_duplicates': 1 if len(parsed.education) == len(set([e['degree'] for e in parsed.education])) else 0,
        'institution_names': sum(1 for inst in ground_truth['institutions']
                                  if any(inst.lower() in edu.get('institution', '').lower()
                                        for edu in parsed.education)) / len(ground_truth['institutions']),
        'skills_quality': calculate_skills_precision(parsed.skills, ground_truth['skills'])
    }

    # Weighted average
    weights = {
        'contact': 0.20,
        'experience_count': 0.15,
        'education_count': 0.15,
        'no_duplicates': 0.15,
        'institution_names': 0.20,
        'skills_quality': 0.15
    }

    total_score = sum(scores[k] * weights[k] for k in weights)
    return total_score * 100  # Convert to percentage
```

### Test Report Template

**File:** `backend/tests/test_report_template.md`

```markdown
# Parser Test Report - [Date]

## Summary
- **Total CVs Tested:** 50
- **Overall Accuracy:** 92.5%
- **Target Accuracy:** 90-95%
- **Status:** ✅ PASSED

## Breakdown by Category
| Category | Accuracy | Target | Status |
|----------|----------|--------|--------|
| Section Detection | 96% | 95% | ✅ |
| Institution Names | 91% | 90% | ✅ |
| Duplicate Entries | 100% | 100% | ✅ |
| Skills Quality | 83% | 80% | ✅ |
| Contact Info | 94% | 95% | ⚠️ |

## Failures (3 CVs)
1. `cv_042.pdf` - Email not detected (in image)
2. `cv_017.pdf` - Institution name has artifact
3. `cv_033.pdf` - Duplicate education entry

## Recommendations
1. Improve image-based contact info extraction
2. Add more spacing artifact patterns
3. Strengthen deduplication logic

## Next Steps
- [ ] Fix identified issues
- [ ] Re-test failed CVs
- [ ] Update regression suite
```

---

## Continuous Improvement Process

### Weekly Review Cycle

**Every Monday:**
1. Collect CVs that failed parsing (confidence < 70%)
2. Manually review top 5 failures
3. Identify new patterns
4. Update parser logic or add to LLM fallback list
5. Re-test and measure improvement

### Monthly Accuracy Audit

**First Friday of month:**
1. Run full corpus test (50+ CVs)
2. Calculate accuracy metrics
3. Generate test report
4. Present to team
5. Plan improvements for next month

---

## Tools & Scripts

### Script 1: Batch Test Runner

**File:** `backend/scripts/test_parser_batch.py`

```python
#!/usr/bin/env python3
"""Batch test parser on multiple CVs"""

import sys
import json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.parser import parse_pdf

def test_batch(cv_directory, labels_file, output_file):
    """Test parser on batch of CVs"""
    with open(labels_file) as f:
        labels = json.load(f)['cvs']

    results = []
    for label in labels:
        cv_path = Path(cv_directory) / label['filename']
        with open(cv_path, 'rb') as f:
            result = parse_pdf(f.read(), label['filename'])

        # Calculate accuracy
        accuracy = calculate_accuracy(result, label['ground_truth'])
        results.append({
            'filename': label['filename'],
            'accuracy': accuracy,
            'passed': accuracy >= 85
        })

    # Save results
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)

    # Print summary
    avg_accuracy = sum(r['accuracy'] for r in results) / len(results)
    print(f"Average Accuracy: {avg_accuracy:.1f}%")
    print(f"Passed: {sum(1 for r in results if r['passed'])}/{len(results)}")

if __name__ == '__main__':
    test_batch(
        cv_directory='backend/storage/uploads',
        labels_file='backend/tests/fixtures/cv_corpus_labels.json',
        output_file='backend/tests/results/batch_test_results.json'
    )
```

**Usage:** `python backend/scripts/test_parser_batch.py`

---

### Script 2: Confidence Scorer

**File:** `backend/scripts/check_parse_confidence.py`

```python
#!/usr/bin/env python3
"""Check parsing confidence for a CV"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.parser import parse_pdf, calculate_parse_confidence

def check_confidence(cv_path):
    """Check parsing confidence"""
    with open(cv_path, 'rb') as f:
        content = f.read()
        result = parse_pdf(content, cv_path.name)

    confidence = calculate_parse_confidence(result, extract_raw_text(content))

    print(f"CV: {cv_path.name}")
    print(f"Confidence: {confidence}%")
    print(f"Status: {'GOOD' if confidence >= 70 else 'NEEDS LLM FALLBACK'}")
    print(f"\nBreakdown:")
    print(f"  Experience: {len(result.experience)} entries")
    print(f"  Education: {len(result.education)} entries")
    print(f"  Skills: {len(result.skills)} items")
    print(f"  Contact: {result.contact}")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python check_parse_confidence.py <cv_path>")
        sys.exit(1)

    check_confidence(Path(sys.argv[1]))
```

**Usage:** `python backend/scripts/check_parse_confidence.py path/to/cv.pdf`

---

## Timeline & Milestones

### Week 1: Unit Tests + Quick Fixes
- **Day 1-2:** Implement 5 quick fixes
- **Day 3:** Write unit tests
- **Day 4:** Run unit tests, fix bugs
- **Day 5:** Build CV corpus, create labels

**Milestone:** Unit tests pass, quick fixes deployed

### Week 2: Integration Tests + Hybrid Implementation
- **Day 1-2:** Run corpus tests, measure accuracy
- **Day 3:** Implement hybrid LLM fallback
- **Day 4:** Test hybrid approach
- **Day 5:** Deploy to staging, monitor

**Milestone:** 90-95% accuracy achieved, hybrid deployed

---

## Success Criteria Checklist

### Before Deployment
- [ ] All unit tests pass
- [ ] Corpus test accuracy >= 90%
- [ ] No spacing artifacts in institution names
- [ ] Zero duplicate education entries
- [ ] Skills list quality >= 80%
- [ ] Contact info detection >= 95%
- [ ] Regression tests pass

### After Deployment
- [ ] Production accuracy >= 85% (first week)
- [ ] Production accuracy >= 90% (second week)
- [ ] User complaints reduce by 80%
- [ ] "Apply Change" button working
- [ ] Missing content suggestions populated

**Questions?** Contact engineering team for support.
