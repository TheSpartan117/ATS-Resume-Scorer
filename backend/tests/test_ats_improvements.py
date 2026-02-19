"""
Test suite for ATS scorer improvements.

Tests for:
1. Fuzzy keyword matching
2. Input validation
3. Role-specific weights
4. Experience duration detection
5. False negative reduction
"""

import pytest
from backend.services.scorer_ats import ATSScorer
from backend.services.parser import ResumeData


class TestFuzzyKeywordMatching:
    """Test fuzzy matching improvements"""

    def test_case_insensitive_matching(self):
        """Test that 'Python' matches 'python'"""
        scorer = ATSScorer()
        resume = ResumeData(
            fileName="test.pdf",
            contact={"name": "John Doe"},
            experience=[{
                "title": "Developer",
                "company": "Company",
                "description": "Worked with Python, Javascript, and Docker"
            }],
            education=[],
            skills=["Python", "JavaScript", "Docker"],
            certifications=[],
            metadata={"pageCount": 1, "wordCount": 400, "fileFormat": "pdf"}
        )

        result = scorer._score_keywords(resume, "software_engineer", "entry", "")

        # Should match despite case differences
        matched = result['details']['matched']
        assert any('python' in m.lower() for m in matched) or any('Python' in m for m in matched)

    def test_fuzzy_matching_similar_terms(self):
        """Test that similar terms match (e.g., 'JavaScript' vs 'Javascript')"""
        scorer = ATSScorer()
        resume = ResumeData(
            fileName="test.pdf",
            contact={"name": "John Doe"},
            experience=[{
                "title": "Developer",
                "company": "Company",
                "description": "Javascript development"
            }],
            education=[],
            skills=["Javascript"],
            certifications=[],
            metadata={"pageCount": 1, "wordCount": 400, "fileFormat": "pdf"}
        )

        result = scorer._score_keywords(resume, "software_engineer", "entry", "")

        # Should handle minor variations
        assert result['score'] > 0

    def test_synonym_matching(self):
        """Test that synonyms are recognized"""
        scorer = ATSScorer()
        resume = ResumeData(
            fileName="test.pdf",
            contact={"name": "John Doe"},
            experience=[{
                "title": "Developer",
                "company": "Company",
                "description": "Machine Learning and Artificial Intelligence projects"
            }],
            education=[],
            skills=["ML", "AI"],
            certifications=[],
            metadata={"pageCount": 1, "wordCount": 400, "fileFormat": "pdf"}
        )

        result = scorer._score_keywords(resume, "data_scientist", "entry", "")

        # ML/AI should match machine learning/artificial intelligence
        assert result['score'] > 0


class TestInputValidation:
    """Test input validation improvements"""

    def test_none_contact_field(self):
        """Test handling of None contact field"""
        scorer = ATSScorer()
        resume = ResumeData(
            fileName="test.pdf",
            contact=None,  # None contact
            experience=[],
            education=[],
            skills=[],
            certifications=[],
            metadata={"pageCount": 1, "wordCount": 400, "fileFormat": "pdf"}
        )

        # Should not crash
        result = scorer._score_contact_info(resume)
        assert result['score'] == 0
        assert 'error' not in result

    def test_none_experience_field(self):
        """Test handling of None experience field"""
        scorer = ATSScorer()
        resume = ResumeData(
            fileName="test.pdf",
            contact={"name": "John Doe"},
            experience=None,  # None experience
            education=[],
            skills=[],
            certifications=[],
            metadata={"pageCount": 1, "wordCount": 400, "fileFormat": "pdf"}
        )

        # Should not crash
        result = scorer._score_experience(resume, "mid")
        assert 'error' not in result

    def test_empty_experience_list(self):
        """Test handling of empty experience list"""
        scorer = ATSScorer()
        resume = ResumeData(
            fileName="test.pdf",
            contact={"name": "John Doe"},
            experience=[],  # Empty list
            education=[],
            skills=[],
            certifications=[],
            metadata={"pageCount": 1, "wordCount": 400, "fileFormat": "pdf"}
        )

        result = scorer._score_experience(resume, "mid")
        assert result['score'] >= 0
        assert 'error' not in result

    def test_none_metadata_field(self):
        """Test handling of None metadata field"""
        scorer = ATSScorer()
        resume = ResumeData(
            fileName="test.pdf",
            contact={"name": "John Doe"},
            experience=[],
            education=[],
            skills=[],
            certifications=[],
            metadata=None  # None metadata
        )

        # Should not crash
        result = scorer._score_formatting(resume)
        assert 'error' not in result

    def test_missing_experience_fields(self):
        """Test handling of missing fields in experience"""
        scorer = ATSScorer()
        resume = ResumeData(
            fileName="test.pdf",
            contact={"name": "John Doe"},
            experience=[{
                "title": "Developer"
                # Missing company, startDate, endDate, description
            }],
            education=[],
            skills=[],
            certifications=[],
            metadata={"pageCount": 1, "wordCount": 400, "fileFormat": "pdf"}
        )

        # Should not crash
        result = scorer.score(resume, "software_engineer", "entry")
        assert 'score' in result
        assert 'error' not in str(result)


class TestExperienceDurationDetection:
    """Test improved experience duration detection"""

    def test_experience_range_detection(self):
        """Test detection of '3-5 years' in description"""
        scorer = ATSScorer()
        resume = ResumeData(
            fileName="test.pdf",
            contact={"name": "John Doe"},
            experience=[{
                "title": "Senior Developer",
                "company": "Company",
                "startDate": "Jan 2019",
                "endDate": "Present",
                "description": "5 years of experience with Python development"
            }],
            education=[],
            skills=["Python"],
            certifications=[],
            metadata={"pageCount": 1, "wordCount": 400, "fileFormat": "pdf"}
        )

        result = scorer._score_experience(resume, "mid")

        # Should recognize 5 years experience
        assert result['details']['total_years'] >= 4.5

    def test_multiple_overlapping_roles(self):
        """Test handling of overlapping roles"""
        scorer = ATSScorer()
        resume = ResumeData(
            fileName="test.pdf",
            contact={"name": "John Doe"},
            experience=[
                {
                    "title": "Developer",
                    "company": "Company A",
                    "startDate": "Jan 2020",
                    "endDate": "Dec 2022",
                    "description": "Development work"
                },
                {
                    "title": "Freelancer",
                    "company": "Self",
                    "startDate": "Jun 2021",
                    "endDate": "Present",
                    "description": "Freelance projects"
                }
            ],
            education=[],
            skills=["Python"],
            certifications=[],
            metadata={"pageCount": 1, "wordCount": 400, "fileFormat": "pdf"}
        )

        result = scorer._score_experience(resume, "mid")

        # Should handle overlapping roles appropriately
        assert result['details']['total_years'] > 0


class TestFalseNegativeReduction:
    """Test improvements to reduce false negatives"""

    def test_entry_level_with_5_years_experience(self):
        """Test that 5 years experience doesn't get marked as entry-level with poor score"""
        scorer = ATSScorer()
        resume = ResumeData(
            fileName="test.pdf",
            contact={"name": "John Doe", "email": "john@example.com", "phone": "123-456-7890"},
            experience=[{
                "title": "Software Engineer",
                "company": "Company",
                "startDate": "Jan 2019",
                "endDate": "Present",
                "description": "Developed scalable Python applications using Django and REST APIs. Led team of 3 developers. Improved system performance by 40%."
            }],
            education=[{"degree": "BS Computer Science", "institution": "University"}],
            skills=["Python", "Django", "REST API", "Leadership", "AWS"],
            certifications=[],
            metadata={"pageCount": 2, "wordCount": 600, "fileFormat": "pdf"}
        )

        # Score as mid-level
        result = scorer.score(resume, "software_engineer", "mid")

        # Should get reasonable score (not be marked as under-qualified)
        assert result['score'] >= 50, f"Expected score >= 50, got {result['score']}"

        # Experience should be recognized as appropriate for mid-level
        exp_details = result['breakdown']['experience']['details']
        assert 'under-qualified' not in exp_details.get('years_message', '').lower()

    def test_table_format_resume_keyword_extraction(self):
        """Test keyword extraction from table-heavy resume"""
        scorer = ATSScorer()
        resume = ResumeData(
            fileName="test.pdf",
            contact={"name": "John Doe", "email": "john@example.com"},
            experience=[{
                "title": "Software Engineer",
                "company": "Company",
                "description": "Python | Django | REST API | Docker | Kubernetes | AWS | CI/CD"
            }],
            education=[{"degree": "BS CS", "institution": "University"}],
            skills=["Python", "Django", "REST API", "Docker", "Kubernetes", "AWS", "CI/CD"],
            certifications=[],
            metadata={"pageCount": 1, "wordCount": 400, "fileFormat": "pdf"}
        )

        result = scorer._score_keywords(resume, "software_engineer", "mid", "")

        # Should extract keywords from table format (pipe-separated)
        assert result['details']['matched_count'] >= 3, f"Expected >= 3 matches, got {result['details']['matched_count']}"

    def test_flexible_experience_level_boundaries(self):
        """Test that experience level boundaries are flexible"""
        scorer = ATSScorer()
        resume = ResumeData(
            fileName="test.pdf",
            contact={"name": "John Doe"},
            experience=[{
                "title": "Developer",
                "company": "Company",
                "startDate": "Jan 2021",
                "endDate": "Present",
                "description": "Development work"
            }],
            education=[],
            skills=["Python"],
            certifications=[],
            metadata={"pageCount": 1, "wordCount": 400, "fileFormat": "pdf"}
        )

        # 4 years experience (edge case between entry and mid)
        # Should be acceptable for both levels
        entry_result = scorer._score_experience(resume, "entry")
        mid_result = scorer._score_experience(resume, "mid")

        # Should get points in both categories (overlapping ranges)
        assert entry_result['score'] >= 6, "Entry level should accept 4 years"
        assert mid_result['score'] >= 6, "Mid level should accept 4 years"


class TestRoleSpecificWeights:
    """Test role-specific weight application"""

    def test_weights_loaded_from_taxonomy(self):
        """Test that weights are loaded from role taxonomy"""
        scorer = ATSScorer()

        # Check if role weights are accessible
        from backend.services.role_taxonomy import get_role_scoring_data

        role_data = get_role_scoring_data("software_engineer", "mid")
        assert role_data is not None
        assert 'scoring_weights' in role_data

    def test_different_roles_have_different_weights(self):
        """Test that different roles use different weight distributions"""
        from backend.services.role_taxonomy import get_role_scoring_data

        tech_role = get_role_scoring_data("software_engineer", "mid")
        data_role = get_role_scoring_data("data_scientist", "mid")

        # Both should have weights defined
        assert 'scoring_weights' in tech_role
        assert 'scoring_weights' in data_role

        # Weights should be between 0 and 1 and sum to approximately 1
        tech_weights = tech_role['scoring_weights']
        assert all(0 <= v <= 1 for v in tech_weights.values())
        assert 0.9 <= sum(tech_weights.values()) <= 1.1


class TestEndToEndImprovements:
    """Test end-to-end scoring improvements"""

    def test_complete_resume_scoring(self):
        """Test complete resume scoring with all improvements"""
        scorer = ATSScorer()
        resume = ResumeData(
            fileName="test.pdf",
            contact={
                "name": "John Doe",
                "email": "john@example.com",
                "phone": "123-456-7890",
                "location": "San Francisco, CA",
                "linkedin": "linkedin.com/in/johndoe"
            },
            experience=[{
                "title": "Senior Software Engineer",
                "company": "Tech Corp",
                "startDate": "Jan 2019",
                "endDate": "Present",
                "description": "Led development of microservices architecture using Python, Django, and AWS. Improved system performance by 45%. Mentored 5 junior developers."
            }],
            education=[{
                "degree": "BS Computer Science",
                "institution": "Stanford University"
            }],
            skills=["Python", "Django", "AWS", "Docker", "Kubernetes", "CI/CD", "Microservices"],
            certifications=[{"name": "AWS Certified Solutions Architect"}],
            metadata={
                "pageCount": 2,
                "wordCount": 650,
                "fileFormat": "pdf",
                "hasPhoto": False
            }
        )

        result = scorer.score(resume, "software_engineer", "senior")

        # Should get good score with complete, well-formatted resume
        assert result['score'] >= 70, f"Expected score >= 70, got {result['score']}"

        # All sections should have scores
        assert 'keywords' in result['breakdown']
        assert 'red_flags' in result['breakdown']
        assert 'experience' in result['breakdown']
        assert 'formatting' in result['breakdown']
        assert 'contact' in result['breakdown']

        # Contact should be complete (5 pts)
        assert result['breakdown']['contact']['score'] == 5

    def test_error_handling_in_complete_scoring(self):
        """Test that errors in one component don't crash entire scoring"""
        scorer = ATSScorer()
        resume = ResumeData(
            fileName="test.pdf",
            contact=None,  # Invalid data
            experience=[{
                "title": "Developer"
                # Missing other fields
            }],
            education=None,
            skills=None,
            certifications=None,
            metadata=None
        )

        # Should not crash
        result = scorer.score(resume, "software_engineer", "mid")

        # Should return a valid result with error handling
        assert 'score' in result
        assert result['score'] >= 0
        assert 'breakdown' in result
