"""
Tests for content analysis validation (Parameters 26-35).
"""

import pytest
from backend.services.red_flags_validator import RedFlagsValidator
from backend.services.parser import ResumeData


def test_action_verbs_percentage_critical():
    """Test P26: Action verbs <70% triggers critical"""
    resume = ResumeData(
        fileName="test.pdf",
        contact={"name": "John Doe"},
        experience=[{
            "title": "Software Engineer",
            "company": "Company A",
            "startDate": "Jan 2020",
            "endDate": "Present",
            "description": "• Developed scalable applications\n• Was responsible for API design\n• Involved in code reviews\n• Built microservices"
        }],
        education=[{"degree": "BS Computer Science", "institution": "University"}],
        skills=["Python", "FastAPI"],
        certifications=[],
        metadata={"pageCount": 1, "wordCount": 400, "fileFormat": "pdf"}
    )

    validator = RedFlagsValidator()
    issues = validator.validate_content_analysis(resume)

    action_verb_issues = [i for i in issues if i['category'] == 'action_verbs']
    assert len(action_verb_issues) >= 1
    assert action_verb_issues[0]['severity'] == 'critical'


def test_action_verbs_percentage_warning():
    """Test P26: Action verbs 70-90% triggers warning"""
    resume = ResumeData(
        fileName="test.pdf",
        contact={"name": "John Doe"},
        experience=[{
            "title": "Software Engineer",
            "company": "Company A",
            "startDate": "Jan 2020",
            "endDate": "Present",
            "description": "• Developed scalable applications\n• Built microservices architecture\n• Was responsible for API design\n• Implemented CI/CD pipeline\n• Created automated testing framework"
        }],
        education=[{"degree": "BS Computer Science", "institution": "University"}],
        skills=["Python"],
        certifications=[],
        metadata={"pageCount": 1, "wordCount": 400, "fileFormat": "pdf"}
    )

    validator = RedFlagsValidator()
    issues = validator.validate_content_analysis(resume)

    action_verb_issues = [i for i in issues if i['category'] == 'action_verbs']
    # 4/5 = 80% should trigger warning
    assert len(action_verb_issues) >= 1
    assert action_verb_issues[0]['severity'] == 'warning'


def test_action_verbs_percentage_pass():
    """Test P26: Action verbs >90% passes"""
    resume = ResumeData(
        fileName="test.pdf",
        contact={"name": "John Doe"},
        experience=[{
            "title": "Software Engineer",
            "company": "Company A",
            "startDate": "Jan 2020",
            "endDate": "Present",
            "description": "• Developed scalable applications\n• Built microservices architecture\n• Implemented CI/CD pipeline\n• Created automated testing framework\n• Optimized database queries"
        }],
        education=[{"degree": "BS Computer Science", "institution": "University"}],
        skills=["Python"],
        certifications=[],
        metadata={"pageCount": 1, "wordCount": 400, "fileFormat": "pdf"}
    )

    validator = RedFlagsValidator()
    issues = validator.validate_content_analysis(resume)

    action_verb_issues = [i for i in issues if i['category'] == 'action_verbs']
    # 5/5 = 100% should pass
    assert len(action_verb_issues) == 0


def test_quantified_achievements_critical():
    """Test P27: <40% quantified triggers critical"""
    resume = ResumeData(
        fileName="test.pdf",
        contact={"name": "John Doe"},
        experience=[{
            "title": "Software Engineer",
            "company": "Company A",
            "startDate": "Jan 2020",
            "endDate": "Present",
            "description": "• Developed web applications\n• Built REST APIs\n• Implemented authentication\n• Created database schemas\n• Improved code quality"
        }],
        education=[{"degree": "BS Computer Science", "institution": "University"}],
        skills=["Python"],
        certifications=[],
        metadata={"pageCount": 1, "wordCount": 400, "fileFormat": "pdf"}
    )

    validator = RedFlagsValidator()
    issues = validator.validate_content_analysis(resume)

    quantified_issues = [i for i in issues if i['category'] == 'quantified_achievements']
    assert len(quantified_issues) >= 1
    assert quantified_issues[0]['severity'] == 'critical'


def test_quantified_achievements_warning():
    """Test P27: 40-60% quantified triggers warning"""
    resume = ResumeData(
        fileName="test.pdf",
        contact={"name": "John Doe"},
        experience=[{
            "title": "Software Engineer",
            "company": "Company A",
            "startDate": "Jan 2020",
            "endDate": "Present",
            "description": "• Developed web applications\n• Reduced response time by 50%\n• Implemented authentication\n• Scaled system to 10k users\n• Created database schemas"
        }],
        education=[{"degree": "BS Computer Science", "institution": "University"}],
        skills=["Python"],
        certifications=[],
        metadata={"pageCount": 1, "wordCount": 400, "fileFormat": "pdf"}
    )

    validator = RedFlagsValidator()
    issues = validator.validate_content_analysis(resume)

    quantified_issues = [i for i in issues if i['category'] == 'quantified_achievements']
    # 2/5 = 40% should trigger warning
    assert len(quantified_issues) >= 1
    assert quantified_issues[0]['severity'] == 'warning'


def test_quantified_achievements_pass():
    """Test P27: >60% quantified passes"""
    resume = ResumeData(
        fileName="test.pdf",
        contact={"name": "John Doe"},
        experience=[{
            "title": "Software Engineer",
            "company": "Company A",
            "startDate": "Jan 2020",
            "endDate": "Present",
            "description": "• Reduced response time by 50%\n• Scaled system to 10k users\n• Improved performance by 2x\n• Deployed $1M revenue feature"
        }],
        education=[{"degree": "BS Computer Science", "institution": "University"}],
        skills=["Python"],
        certifications=[],
        metadata={"pageCount": 1, "wordCount": 400, "fileFormat": "pdf"}
    )

    validator = RedFlagsValidator()
    issues = validator.validate_content_analysis(resume)

    quantified_issues = [i for i in issues if i['category'] == 'quantified_achievements']
    # 4/4 = 100% should pass
    assert len(quantified_issues) == 0


def test_passive_voice_detection():
    """Test P28: Passive voice >5 instances triggers warning"""
    resume = ResumeData(
        fileName="test.pdf",
        contact={"name": "John Doe"},
        experience=[{
            "title": "Software Engineer",
            "company": "Company A",
            "startDate": "Jan 2020",
            "endDate": "Present",
            "description": "• The system was developed by me\n• APIs were implemented for clients\n• Code has been reviewed thoroughly\n• Tests have been completed successfully\n• Features were delivered on time\n• The database was optimized for performance"
        }],
        education=[{"degree": "BS Computer Science", "institution": "University"}],
        skills=["Python"],
        certifications=[],
        metadata={"pageCount": 1, "wordCount": 400, "fileFormat": "pdf"}
    )

    validator = RedFlagsValidator()
    issues = validator.validate_content_analysis(resume)

    passive_issues = [i for i in issues if i['category'] == 'passive_voice']
    assert len(passive_issues) >= 1
    assert passive_issues[0]['severity'] == 'warning'
    assert '6' in passive_issues[0]['message'] or 'instances' in passive_issues[0]['message'].lower()


def test_first_person_pronouns_detection():
    """Test P29/P34: First-person pronouns trigger warning"""
    resume = ResumeData(
        fileName="test.pdf",
        contact={"name": "John Doe"},
        experience=[{
            "title": "Software Engineer",
            "company": "Company A",
            "startDate": "Jan 2020",
            "endDate": "Present",
            "description": "• I developed scalable applications\n• Built my own microservices\n• We implemented CI/CD pipeline\n• Our team created automated tests"
        }],
        education=[{"degree": "BS Computer Science", "institution": "University"}],
        skills=["Python"],
        certifications=[],
        metadata={"pageCount": 1, "wordCount": 400, "fileFormat": "pdf"}
    )

    validator = RedFlagsValidator()
    issues = validator.validate_content_analysis(resume)

    pronoun_issues = [i for i in issues if i['category'] == 'first_person_pronouns']
    assert len(pronoun_issues) >= 1
    assert pronoun_issues[0]['severity'] == 'warning'
    assert 'I' in pronoun_issues[0]['message'] or 'my' in pronoun_issues[0]['message']


def test_buzzword_density_detection():
    """Test P30: Buzzwords >3 instances triggers warning"""
    resume = ResumeData(
        fileName="test.pdf",
        contact={"name": "John Doe"},
        experience=[{
            "title": "Software Engineer",
            "company": "Company A",
            "startDate": "Jan 2020",
            "endDate": "Present",
            "description": "• Developed synergy between teams\n• Built world-class solutions\n• Created game changer features\n• Implemented innovative rockstar approach"
        }],
        education=[{"degree": "BS Computer Science", "institution": "University"}],
        skills=["Python"],
        certifications=[],
        metadata={"pageCount": 1, "wordCount": 400, "fileFormat": "pdf"}
    )

    validator = RedFlagsValidator()
    issues = validator.validate_content_analysis(resume)

    buzzword_issues = [i for i in issues if i['category'] == 'buzzword_density']
    assert len(buzzword_issues) >= 1
    assert buzzword_issues[0]['severity'] == 'warning'
    assert 'synergy' in buzzword_issues[0]['message'].lower() or 'rockstar' in buzzword_issues[0]['message'].lower()


def test_skills_density_detection():
    """Test P31: Skills density <40% triggers warning"""
    resume = ResumeData(
        fileName="test.pdf",
        contact={"name": "John Doe"},
        experience=[{
            "title": "Software Engineer",
            "company": "Company A",
            "startDate": "Jan 2020",
            "endDate": "Present",
            "description": "• Developed scalable web applications\n• Built REST APIs using Python\n• Implemented authentication systems"
        }],
        education=[{"degree": "BS Computer Science", "institution": "University"}],
        skills=["Python", "Java", "JavaScript", "Go", "Rust", "C++", "Ruby", "PHP", "TypeScript", "Kotlin"],
        certifications=[],
        metadata={"pageCount": 1, "wordCount": 400, "fileFormat": "pdf"}
    )

    validator = RedFlagsValidator()
    issues = validator.validate_content_analysis(resume)

    skills_density_issues = [i for i in issues if i['category'] == 'skills_density']
    assert len(skills_density_issues) >= 1
    assert skills_density_issues[0]['severity'] == 'warning'


def test_keyword_context_detection():
    """Test P32: Keywords without achievement context trigger suggestion"""
    resume = ResumeData(
        fileName="test.pdf",
        contact={"name": "John Doe"},
        experience=[{
            "title": "Software Engineer",
            "company": "Company A",
            "startDate": "Jan 2020",
            "endDate": "Present",
            "description": "• Worked with Python on projects\n• Used Java for development\n• Built scalable systems with Go reducing latency by 50%"
        }],
        education=[{"degree": "BS Computer Science", "institution": "University"}],
        skills=["Python", "Java", "Go"],
        certifications=[],
        metadata={"pageCount": 1, "wordCount": 400, "fileFormat": "pdf"}
    )

    validator = RedFlagsValidator()
    issues = validator.validate_content_analysis(resume)

    context_issues = [i for i in issues if i['category'] == 'keyword_context']
    # Only 1/3 skills (Go) has context with action verb/metric
    assert len(context_issues) >= 1
    assert context_issues[0]['severity'] == 'suggestion'


def test_sentence_structure_run_on_detection():
    """Test P33: Run-on sentences trigger suggestion"""
    resume = ResumeData(
        fileName="test.pdf",
        contact={"name": "John Doe"},
        experience=[{
            "title": "Software Engineer",
            "company": "Company A",
            "startDate": "Jan 2020",
            "endDate": "Present",
            "description": "• Developed web applications and built APIs and created microservices and implemented CI/CD and deployed to production"
        }],
        education=[{"degree": "BS Computer Science", "institution": "University"}],
        skills=["Python"],
        certifications=[],
        metadata={"pageCount": 1, "wordCount": 400, "fileFormat": "pdf"}
    )

    validator = RedFlagsValidator()
    issues = validator.validate_content_analysis(resume)

    run_on_issues = [i for i in issues if i['category'] == 'sentence_structure']
    assert len(run_on_issues) >= 1
    assert run_on_issues[0]['severity'] == 'suggestion'


def test_informal_language_detection():
    """Test P35: Informal language triggers warning"""
    resume = ResumeData(
        fileName="test.pdf",
        contact={"name": "John Doe"},
        experience=[{
            "title": "Software Engineer",
            "company": "Company A",
            "startDate": "Jan 2020",
            "endDate": "Present",
            "description": "• Worked on lots of things\n• Built stuff for the platform\n• Really improved performance\n• Kinda optimized the database"
        }],
        education=[{"degree": "BS Computer Science", "institution": "University"}],
        skills=["Python"],
        certifications=[],
        metadata={"pageCount": 1, "wordCount": 400, "fileFormat": "pdf"}
    )

    validator = RedFlagsValidator()
    issues = validator.validate_content_analysis(resume)

    informal_issues = [i for i in issues if i['category'] == 'informal_language']
    assert len(informal_issues) >= 1
    assert informal_issues[0]['severity'] == 'warning'
    assert 'stuff' in informal_issues[0]['message'].lower() or 'things' in informal_issues[0]['message'].lower()


def test_content_analysis_with_good_resume():
    """Test content analysis with well-written resume passes most checks"""
    resume = ResumeData(
        fileName="test.pdf",
        contact={"name": "John Doe"},
        experience=[{
            "title": "Software Engineer",
            "company": "Company A",
            "startDate": "Jan 2020",
            "endDate": "Present",
            "description": "• Developed scalable REST APIs using Python and FastAPI, reducing response time by 40%\n• Built microservices architecture serving 100k+ daily users\n• Implemented CI/CD pipeline decreasing deployment time from 2 hours to 15 minutes\n• Optimized database queries improving performance by 3x"
        }],
        education=[{"degree": "BS Computer Science", "institution": "University"}],
        skills=["Python", "FastAPI"],
        certifications=[],
        metadata={"pageCount": 1, "wordCount": 400, "fileFormat": "pdf"}
    )

    validator = RedFlagsValidator()
    issues = validator.validate_content_analysis(resume)

    # Should have minimal or no content analysis issues
    critical_issues = [i for i in issues if i['severity'] == 'critical']
    assert len(critical_issues) == 0


def test_content_analysis_no_experience():
    """Test content analysis with no experience returns empty"""
    resume = ResumeData(
        fileName="test.pdf",
        contact={"name": "John Doe"},
        experience=[],
        education=[{"degree": "BS Computer Science", "institution": "University"}],
        skills=["Python"],
        certifications=[],
        metadata={"pageCount": 1, "wordCount": 400, "fileFormat": "pdf"}
    )

    validator = RedFlagsValidator()
    issues = validator.validate_content_analysis(resume)

    # Should return empty list
    assert isinstance(issues, list)
    assert len(issues) == 0


def test_content_analysis_no_bullets():
    """Test content analysis with experience but no bullets"""
    resume = ResumeData(
        fileName="test.pdf",
        contact={"name": "John Doe"},
        experience=[{
            "title": "Software Engineer",
            "company": "Company A",
            "startDate": "Jan 2020",
            "endDate": "Present"
        }],
        education=[{"degree": "BS Computer Science", "institution": "University"}],
        skills=["Python"],
        certifications=[],
        metadata={"pageCount": 1, "wordCount": 400, "fileFormat": "pdf"}
    )

    validator = RedFlagsValidator()
    issues = validator.validate_content_analysis(resume)

    # Should return empty list
    assert isinstance(issues, list)
    assert len(issues) == 0


def test_validate_resume_includes_content_analysis():
    """Test that validate_resume calls validate_content_analysis"""
    resume = ResumeData(
        fileName="test.pdf",
        contact={"name": "John Doe"},
        experience=[{
            "title": "Software Engineer",
            "company": "Company A",
            "startDate": "Jan 2020",
            "endDate": "Present",
            "description": "• Responsible for development\n• Worked on projects\n• Helped with code reviews"
        }],
        education=[{"degree": "BS Computer Science", "institution": "University"}],
        skills=["Python", "Java", "JavaScript"],
        certifications=[],
        metadata={"pageCount": 1, "wordCount": 400, "fileFormat": "pdf"}
    )

    validator = RedFlagsValidator()
    result = validator.validate_resume(resume, "software_engineer", "mid")

    # Should have content analysis issues
    all_issues = result['critical'] + result['warnings'] + result['suggestions']
    content_issues = [i for i in all_issues if i['category'] in [
        'action_verbs', 'quantified_achievements', 'passive_voice',
        'first_person_pronouns', 'buzzword_density', 'skills_density',
        'keyword_context', 'sentence_structure', 'informal_language'
    ]]
    assert len(content_issues) > 0


def test_content_analysis_multiple_experiences():
    """Test content analysis across multiple experience entries"""
    resume = ResumeData(
        fileName="test.pdf",
        contact={"name": "John Doe"},
        experience=[
            {
                "title": "Senior Engineer",
                "company": "Company A",
                "startDate": "Jan 2022",
                "endDate": "Present",
                "description": "• Developed scalable systems reducing latency by 60%\n• Led team of 5 engineers"
            },
            {
                "title": "Engineer",
                "company": "Company B",
                "startDate": "Jan 2020",
                "endDate": "Dec 2021",
                "description": "• I built web applications\n• Worked on lots of things\n• Was responsible for APIs"
            }
        ],
        education=[{"degree": "BS Computer Science", "institution": "University"}],
        skills=["Python"],
        certifications=[],
        metadata={"pageCount": 1, "wordCount": 400, "fileFormat": "pdf"}
    )

    validator = RedFlagsValidator()
    issues = validator.validate_content_analysis(resume)

    # Should detect issues from both experiences
    pronoun_issues = [i for i in issues if i['category'] == 'first_person_pronouns']
    assert len(pronoun_issues) >= 1

    informal_issues = [i for i in issues if i['category'] == 'informal_language']
    assert len(informal_issues) >= 1


def test_all_content_analysis_categories():
    """Test that all 10 content analysis parameters can be triggered"""
    # Create resume with issues in all categories
    resume = ResumeData(
        fileName="test.pdf",
        contact={"name": "John Doe"},
        experience=[{
            "title": "Rockstar Engineer",
            "company": "Company A",
            "startDate": "Jan 2020",
            "endDate": "Present",
            "description": "• I was responsible for synergy stuff and things and worked on lots of projects and helped with things\n• Built world-class innovative systems"
        }],
        education=[{"degree": "BS Computer Science", "institution": "University"}],
        skills=["Python", "Java", "JavaScript", "Go", "Ruby"],
        certifications=[],
        metadata={"pageCount": 1, "wordCount": 400, "fileFormat": "pdf"}
    )

    validator = RedFlagsValidator()
    issues = validator.validate_content_analysis(resume)

    # Should have issues in multiple categories
    categories = set(i['category'] for i in issues)

    # Check that multiple categories are detected
    expected_categories = {
        'action_verbs',
        'quantified_achievements',
        'passive_voice',
        'first_person_pronouns',
        'buzzword_density',
        'skills_density',
        'sentence_structure',
        'informal_language',
    }

    # Should have at least 5 different categories of issues
    assert len(categories.intersection(expected_categories)) >= 5
