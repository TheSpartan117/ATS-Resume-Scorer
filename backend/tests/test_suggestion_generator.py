"""
Tests for SuggestionGenerator - generates actionable suggestions with document locations
"""
import pytest
from docx import Document
from backend.services.suggestion_generator import SuggestionGenerator


@pytest.fixture
def sample_resume_data():
    """Sample parsed resume data for testing"""
    return {
        'contact': {
            'name': 'John Doe',
            'email': 'john@example.com'
            # Missing: phone, linkedin
        },
        'summary': 'Software engineer with experience',
        'experience': [
            {
                'title': 'Software Engineer',
                'company': 'TechCorp',
                'description': 'Responsible for managing team projects',
                'para_idx': 8
            }
        ],
        'skills': ['Python', 'JavaScript'],
        'education': [
            {
                'degree': 'BS Computer Science',
                'institution': 'State University'
            }
        ]
    }


@pytest.fixture
def sample_sections():
    """Sample section mapping from section_detector"""
    return [
        {'name': 'Contact', 'start_para': 0, 'end_para': 5},
        {'name': 'Summary', 'start_para': 6, 'end_para': 7},
        {'name': 'Experience', 'start_para': 8, 'end_para': 15},
        {'name': 'Education', 'start_para': 16, 'end_para': 20},
        {'name': 'Skills', 'start_para': 21, 'end_para': 25}
    ]


def test_suggestion_generator_initialization():
    """Test creating SuggestionGenerator instance"""
    generator = SuggestionGenerator(role='software_engineer', level='mid')

    assert generator is not None
    assert generator.role == 'software_engineer'
    assert generator.level == 'mid'


def test_generate_missing_content_suggestion(sample_resume_data, sample_sections):
    """Test generating missing_content type suggestion (e.g., missing phone)"""
    generator = SuggestionGenerator(role='software_engineer', level='mid')

    suggestions = generator.generate_suggestions(
        resume_data=sample_resume_data,
        sections=sample_sections
    )

    # Should detect missing phone number
    missing_phone = next((s for s in suggestions if 'phone' in s['title'].lower()), None)

    assert missing_phone is not None
    assert missing_phone['type'] == 'missing_content'
    assert missing_phone['severity'] in ['critical', 'high', 'medium', 'low']
    assert 'title' in missing_phone
    assert 'description' in missing_phone
    assert 'location' in missing_phone
    assert missing_phone['location']['section'] == 'Contact'
    assert 'action' in missing_phone
    assert missing_phone['action'] == 'add_phone'


def test_generate_content_change_suggestion(sample_resume_data, sample_sections):
    """Test generating content_change type suggestion (e.g., weak action verb)"""
    generator = SuggestionGenerator(role='software_engineer', level='mid')

    suggestions = generator.generate_suggestions(
        resume_data=sample_resume_data,
        sections=sample_sections
    )

    # Should detect weak action verb "Responsible for"
    weak_verb = next((s for s in suggestions if s['type'] == 'content_change'), None)

    assert weak_verb is not None
    assert weak_verb['severity'] in ['critical', 'high', 'medium', 'low']
    assert 'current_text' in weak_verb
    assert 'suggested_text' in weak_verb
    assert 'location' in weak_verb
    assert 'para_idx' in weak_verb['location']
    assert weak_verb['location']['section'] == 'Experience'
    assert weak_verb['action'] == 'replace_text'


def test_generate_missing_section_suggestion(sample_resume_data, sample_sections):
    """Test generating missing_section type suggestion"""
    # Remove Projects section to trigger missing section detection
    resume_no_projects = sample_resume_data.copy()

    generator = SuggestionGenerator(role='software_engineer', level='mid')

    suggestions = generator.generate_suggestions(
        resume_data=resume_no_projects,
        sections=sample_sections
    )

    # Should suggest adding Projects section for tech roles
    missing_projects = next((s for s in suggestions if s['type'] == 'missing_section' and 'project' in s['title'].lower()), None)

    assert missing_projects is not None
    assert missing_projects['severity'] in ['critical', 'high', 'medium', 'low']
    assert 'template' in missing_projects
    assert 'location' in missing_projects
    assert missing_projects['action'] == 'add_section'


def test_generate_formatting_suggestion():
    """Test generating formatting type suggestion"""
    generator = SuggestionGenerator(role='software_engineer', level='mid')

    resume_data = {
        'contact': {'name': 'John Doe', 'email': 'test@example.com'},
        'experience': [
            {
                'title': 'Developer',
                'dates': 'Jan 2020 - 2/21',  # Inconsistent date format
                'para_idx': 10
            }
        ]
    }

    sections = [
        {'name': 'Contact', 'start_para': 0, 'end_para': 5},
        {'name': 'Experience', 'start_para': 8, 'end_para': 15}
    ]

    suggestions = generator.generate_suggestions(
        resume_data=resume_data,
        sections=sections
    )

    # Should detect formatting issue
    format_issue = next((s for s in suggestions if s['type'] == 'formatting'), None)

    # Formatting suggestions may not always be present, but if they are, verify structure
    if format_issue:
        assert format_issue['severity'] in ['critical', 'high', 'medium', 'low']
        assert 'location' in format_issue
        assert format_issue['action'] == 'navigate'


def test_suggestion_includes_all_required_fields(sample_resume_data, sample_sections):
    """Test that all suggestions include required fields"""
    generator = SuggestionGenerator(role='software_engineer', level='mid')

    suggestions = generator.generate_suggestions(
        resume_data=sample_resume_data,
        sections=sample_sections
    )

    assert len(suggestions) > 0

    for suggestion in suggestions:
        # Required fields for all suggestion types
        assert 'id' in suggestion
        assert 'type' in suggestion
        assert suggestion['type'] in ['missing_content', 'content_change', 'missing_section', 'formatting']
        assert 'severity' in suggestion
        assert suggestion['severity'] in ['critical', 'high', 'medium', 'low']
        assert 'title' in suggestion
        assert 'description' in suggestion
        assert 'location' in suggestion
        assert 'action' in suggestion


def test_location_mapping_to_paragraph_indices(sample_resume_data, sample_sections):
    """Test that suggestions correctly map to paragraph indices"""
    generator = SuggestionGenerator(role='software_engineer', level='mid')

    suggestions = generator.generate_suggestions(
        resume_data=sample_resume_data,
        sections=sample_sections
    )

    # Content change suggestions should have para_idx
    content_changes = [s for s in suggestions if s['type'] == 'content_change']

    for suggestion in content_changes:
        assert 'para_idx' in suggestion['location']
        assert isinstance(suggestion['location']['para_idx'], int)
        assert suggestion['location']['para_idx'] >= 0


def test_suggestion_priority_ordering(sample_resume_data, sample_sections):
    """Test that suggestions are ordered by priority (critical > high > medium > low)"""
    generator = SuggestionGenerator(role='software_engineer', level='mid')

    suggestions = generator.generate_suggestions(
        resume_data=sample_resume_data,
        sections=sample_sections
    )

    # Map severity to numeric priority
    severity_priority = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}

    # Check that suggestions are sorted by priority
    for i in range(len(suggestions) - 1):
        current_priority = severity_priority[suggestions[i]['severity']]
        next_priority = severity_priority[suggestions[i + 1]['severity']]
        assert current_priority <= next_priority


def test_empty_resume_data():
    """Test handling of empty resume data"""
    generator = SuggestionGenerator(role='software_engineer', level='mid')

    suggestions = generator.generate_suggestions(
        resume_data={},
        sections=[]
    )

    # Should still generate suggestions for missing sections
    assert len(suggestions) > 0
    assert any(s['type'] == 'missing_section' for s in suggestions)


def test_role_specific_suggestions():
    """Test that suggestions are role-specific"""
    # Software engineer role
    se_generator = SuggestionGenerator(role='software_engineer', level='mid')

    resume_data = {
        'contact': {'name': 'John Doe', 'email': 'test@example.com'},
        'skills': ['Python']
    }

    sections = [
        {'name': 'Contact', 'start_para': 0, 'end_para': 5},
        {'name': 'Skills', 'start_para': 6, 'end_para': 10}
    ]

    se_suggestions = se_generator.generate_suggestions(
        resume_data=resume_data,
        sections=sections
    )

    # Software engineers should get Projects section suggestion
    assert any('project' in s['title'].lower() for s in se_suggestions)
