"""
Tests for P4.2: Professional Standards Scorer (5 points)

Tests professional content and presentation checks:
1. Personal pronouns (I, me, my) = -2 pts
2. Unprofessional email (e.g., cooldude@) = -1 pt
3. Inappropriate content = -2 pts
4. Inconsistent formatting = -1 pt

Scoring:
- Start with 5 points
- Deduct penalties (minimum 0)
"""

import pytest
from backend.services.parameters.p4_2_professional_standards import (
    ProfessionalStandardsScorer,
    score_professional_standards
)


class TestProfessionalStandardsScorer:
    """Test cases for Professional Standards scoring."""

    @pytest.fixture
    def scorer(self):
        """Create scorer instance."""
        return ProfessionalStandardsScorer()

    def test_perfect_professional_resume(self, scorer):
        """Test resume with perfect professional standards."""
        contact = {
            'email': 'john.smith@gmail.com',
            'name': 'John Smith',
            'phone': '+1-555-123-4567'
        }
        bullets = [
            'Led team of 5 engineers to deliver scalable microservices architecture',
            'Developed REST API serving 10K requests per second',
            'Implemented CI/CD pipeline reducing deployment time by 60%'
        ]
        full_text = ' '.join(bullets)

        result = scorer.score(contact, bullets, full_text)

        assert result['score'] == 5
        assert result['max_score'] == 5
        assert len(result['issues']) == 0
        assert result['has_professional_email'] is True
        assert result['personal_pronoun_count'] == 0
        assert result['unprofessional_email'] is False
        assert result['has_inappropriate_content'] is False
        assert result['has_formatting_issues'] is False

    def test_personal_pronouns_penalty(self, scorer):
        """Test penalty for using personal pronouns."""
        contact = {
            'email': 'john.smith@gmail.com',
            'name': 'John Smith'
        }
        bullets = [
            'I led a team of 5 engineers',
            'My responsibilities included backend development',
            'Developed REST API that me and my team built'
        ]
        full_text = ' '.join(bullets)

        result = scorer.score(contact, bullets, full_text)

        # 5 - 2 (personal pronouns) = 3
        assert result['score'] == 3
        assert result['personal_pronoun_count'] > 0
        assert any('personal pronouns' in issue.lower() for issue in result['issues'])

    def test_unprofessional_email_penalty(self, scorer):
        """Test penalty for unprofessional email."""
        contact = {
            'email': 'cooldude123@gmail.com',
            'name': 'John Smith'
        }
        bullets = [
            'Led team of 5 engineers',
            'Developed REST API'
        ]
        full_text = ' '.join(bullets)

        result = scorer.score(contact, bullets, full_text)

        # 5 - 1 (unprofessional email) = 4
        assert result['score'] == 4
        assert result['unprofessional_email'] is True
        assert any('unprofessional email' in issue.lower() for issue in result['issues'])

    def test_inappropriate_content_penalty(self, scorer):
        """Test penalty for inappropriate or controversial content."""
        contact = {
            'email': 'john.smith@gmail.com',
            'name': 'John Smith'
        }
        bullets = [
            'Led team of 5 engineers',
            'Developed innovative solutions',
            'Participated in religious activities at work'
        ]
        full_text = ' '.join(bullets)

        result = scorer.score(contact, bullets, full_text)

        # 5 - 2 (inappropriate content) = 3
        assert result['score'] == 3
        assert result['has_inappropriate_content'] is True
        assert any('inappropriate content' in issue.lower() for issue in result['issues'])

    def test_formatting_inconsistency_penalty(self, scorer):
        """Test penalty for inconsistent formatting."""
        contact = {
            'email': 'john.smith@gmail.com',
            'name': 'John Smith'
        }
        bullets = [
            'Led team of 5 engineers',
            'developed REST API',  # Inconsistent capitalization
            'IMPLEMENTED CI/CD PIPELINE',  # All caps
            'created microservices'  # Inconsistent
        ]
        full_text = ' '.join(bullets)

        result = scorer.score(contact, bullets, full_text)

        # 5 - 1 (formatting issues) = 4
        assert result['score'] == 4
        assert result['has_formatting_issues'] is True
        assert any('formatting' in issue.lower() for issue in result['issues'])

    def test_multiple_penalties_applied(self, scorer):
        """Test multiple penalties are cumulative."""
        contact = {
            'email': 'partyboi@yahoo.com',
            'name': 'John Smith'
        }
        bullets = [
            'I led a team and my role included architecture',  # Pronouns
            'developed REST API',  # Formatting issue
            'Worked on religious community projects'  # Inappropriate content
        ]
        full_text = ' '.join(bullets)

        result = scorer.score(contact, bullets, full_text)

        # 5 - 2 (pronouns) - 1 (email) - 2 (inappropriate) - 1 (formatting) = -1 -> 0 (minimum)
        assert result['score'] == 0
        assert result['personal_pronoun_count'] > 0
        assert result['unprofessional_email'] is True
        assert result['has_inappropriate_content'] is True
        assert result['has_formatting_issues'] is True
        assert len(result['issues']) >= 4

    def test_minimum_score_is_zero(self, scorer):
        """Test that score cannot go below 0."""
        contact = {
            'email': 'xxxparty123@hotmail.com',
            'name': 'John Smith'
        }
        bullets = [
            'I personally led my team in religious activities',  # All issues
            'me and My colleagues worked on political campaigns',
            'DEVELOPED solutions',  # Formatting
            'i helped with controversial projects'
        ]
        full_text = ' '.join(bullets)

        result = scorer.score(contact, bullets, full_text)

        assert result['score'] == 0
        assert result['score'] >= 0  # Verify minimum

    def test_empty_contact_info(self, scorer):
        """Test handling of missing contact info."""
        contact = {}
        bullets = [
            'Led team of 5 engineers',
            'Developed REST API'
        ]
        full_text = ' '.join(bullets)

        result = scorer.score(contact, bullets, full_text)

        # Should still score based on content
        assert result['score'] >= 0
        assert result['score'] <= 5

    def test_professional_email_patterns(self, scorer):
        """Test various professional email patterns."""
        professional_emails = [
            'john.smith@gmail.com',
            'j.smith@company.com',
            'johnsmith123@outlook.com',
            'john_smith@yahoo.com',
            'john-smith@protonmail.com'
        ]

        for email in professional_emails:
            contact = {'email': email, 'name': 'John Smith'}
            bullets = ['Led team of engineers']
            result = scorer.score(contact, bullets, ' '.join(bullets))

            assert result['unprofessional_email'] is False, f"Email {email} should be professional"

    def test_unprofessional_email_patterns(self, scorer):
        """Test various unprofessional email patterns."""
        unprofessional_emails = [
            'cooldude@gmail.com',
            'partytime123@yahoo.com',
            'ilovepizza@hotmail.com',
            'xxxgamer@gmail.com',
            'cutiegirl@outlook.com',
            'rockstar2023@gmail.com',
            'bigboss@hotmail.com'
        ]

        for email in unprofessional_emails:
            contact = {'email': email, 'name': 'John Smith'}
            bullets = ['Led team of engineers']
            result = scorer.score(contact, bullets, ' '.join(bullets))

            assert result['unprofessional_email'] is True, f"Email {email} should be unprofessional"

    def test_pronoun_detection_case_insensitive(self, scorer):
        """Test pronoun detection is case insensitive."""
        contact = {'email': 'john.smith@gmail.com'}
        bullets = [
            'I Led a team',
            'My responsibilities included',
            'Me and the team delivered'
        ]
        full_text = ' '.join(bullets)

        result = scorer.score(contact, bullets, full_text)

        assert result['personal_pronoun_count'] > 0
        assert result['score'] < 5

    def test_formatting_consistency_checks(self, scorer):
        """Test detection of formatting inconsistencies."""
        # Consistent formatting (good)
        contact = {'email': 'john.smith@gmail.com'}
        bullets_consistent = [
            'Led team of engineers',
            'Developed REST API',
            'Implemented CI/CD pipeline'
        ]
        result = scorer.score(contact, bullets_consistent, ' '.join(bullets_consistent))
        assert result['has_formatting_issues'] is False

        # Inconsistent formatting (bad)
        bullets_inconsistent = [
            'Led team of engineers',
            'developed REST API',  # lowercase
            'IMPLEMENTED CI/CD PIPELINE',  # all caps
            'Created microservices'  # mixed
        ]
        result = scorer.score(contact, bullets_inconsistent, ' '.join(bullets_inconsistent))
        assert result['has_formatting_issues'] is True

    def test_convenience_function(self):
        """Test convenience function works."""
        contact = {'email': 'john.smith@gmail.com'}
        bullets = ['Led team of engineers']
        full_text = ' '.join(bullets)

        result = score_professional_standards(contact, bullets, full_text)

        assert 'score' in result
        assert 'max_score' in result
        assert result['max_score'] == 5

    def test_detailed_issue_descriptions(self, scorer):
        """Test that issues have detailed descriptions."""
        contact = {'email': 'cooldude@gmail.com'}
        bullets = [
            'I led my team',
            'developed solutions',
            'Worked on religious projects'
        ]
        full_text = ' '.join(bullets)

        result = scorer.score(contact, bullets, full_text)

        assert len(result['issues']) > 0
        for issue in result['issues']:
            assert isinstance(issue, str)
            assert len(issue) > 10  # Should have meaningful description

    def test_issue_details_structure(self, scorer):
        """Test that issue_details provides granular information."""
        contact = {'email': 'partydude@gmail.com'}
        bullets = [
            'I personally managed my team',
            'developed solutions',
            'Worked with controversial political groups'
        ]
        full_text = ' '.join(bullets)

        result = scorer.score(contact, bullets, full_text)

        assert 'issue_details' in result
        assert 'pronouns' in result['issue_details']
        assert 'email' in result['issue_details']
        assert 'content' in result['issue_details']
        assert 'formatting' in result['issue_details']
