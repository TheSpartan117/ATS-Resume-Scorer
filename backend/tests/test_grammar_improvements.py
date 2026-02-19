"""
Tests for grammar checking improvements (Solution 1).

Tests the enhanced pyspellchecker implementation with:
1. Resume-specific vocabulary (500+ terms)
2. Enhanced grammar patterns (10-15 new patterns)
3. Reduced false positive rate

Following TDD: write tests first, then implement.
"""

import pytest
from backend.services.red_flags_validator import RedFlagsValidator
from backend.services.parser import ResumeData


class TestResumeVocabulary:
    """Test that resume-specific vocabulary is not flagged as typos"""

    def test_programming_languages_not_flagged(self):
        """Test that programming languages are recognized"""
        validator = RedFlagsValidator()

        # Programming language terms that should NOT be flagged
        test_texts = [
            "Developed applications using Python and JavaScript",
            "Built microservices with Golang and Rust",
            "Created mobile apps with Kotlin and Swift",
            "Implemented features in TypeScript and Ruby"
        ]

        for text in test_texts:
            resume = self._create_resume_with_description(text)
            result = validator.validate_grammar(resume)

            # Should not flag these as typos
            typo_issues = [i for i in result if i['category'] == 'typo']
            flagged_words = [i['message'] for i in typo_issues]

            # Check that common programming languages are not flagged
            programming_langs = ['python', 'javascript', 'typescript', 'golang',
                                'rust', 'kotlin', 'swift', 'ruby']
            for lang in programming_langs:
                assert not any(lang in msg.lower() for msg in flagged_words), \
                    f"{lang} should not be flagged as typo"

    def test_frameworks_not_flagged(self):
        """Test that popular frameworks are recognized"""
        validator = RedFlagsValidator()

        resume = self._create_resume_with_description(
            "Built web applications using React, Angular, Vue, and Django. "
            "Deployed with Docker and Kubernetes."
        )

        result = validator.validate_grammar(resume)
        typo_issues = [i for i in result if i['category'] == 'typo']
        flagged_words = [i['message'] for i in typo_issues]

        # These should NOT be flagged
        frameworks = ['react', 'angular', 'vue', 'django', 'docker', 'kubernetes']
        for framework in frameworks:
            assert not any(framework in msg.lower() for msg in flagged_words), \
                f"{framework} should not be flagged as typo"

    def test_databases_not_flagged(self):
        """Test that database technologies are recognized"""
        validator = RedFlagsValidator()

        resume = self._create_resume_with_description(
            "Worked with PostgreSQL, MongoDB, Redis, and Elasticsearch. "
            "Managed MySQL and DynamoDB databases."
        )

        result = validator.validate_grammar(resume)
        typo_issues = [i for i in result if i['category'] == 'typo']
        flagged_words = [i['message'] for i in typo_issues]

        databases = ['postgresql', 'mongodb', 'redis', 'elasticsearch',
                    'mysql', 'dynamodb']
        for db in databases:
            assert not any(db in msg.lower() for msg in flagged_words), \
                f"{db} should not be flagged as typo"

    def test_cloud_providers_not_flagged(self):
        """Test that cloud provider terms are recognized"""
        validator = RedFlagsValidator()

        resume = self._create_resume_with_description(
            "Deployed infrastructure on AWS, Azure, and GCP. "
            "Used Terraform and Ansible for automation."
        )

        result = validator.validate_grammar(resume)
        typo_issues = [i for i in result if i['category'] == 'typo']
        flagged_words = [i['message'] for i in typo_issues]

        cloud_terms = ['aws', 'azure', 'terraform', 'ansible']
        for term in cloud_terms:
            assert not any(term in msg.lower() for msg in flagged_words), \
                f"{term} should not be flagged as typo"

    def test_certifications_not_flagged(self):
        """Test that certification acronyms are recognized"""
        validator = RedFlagsValidator()

        resume = self._create_resume_with_description(
            "Certified professional with CISSP, CCNA, and CompTIA certifications. "
            "Also holds AWS SAA and GCP ACE credentials."
        )

        result = validator.validate_grammar(resume)
        typo_issues = [i for i in result if i['category'] == 'typo']
        flagged_words = [i['message'] for i in typo_issues]

        certs = ['cissp', 'ccna', 'comptia']
        for cert in certs:
            assert not any(cert in msg.lower() for msg in flagged_words), \
                f"{cert} should not be flagged as typo"

    def test_methodologies_not_flagged(self):
        """Test that methodology terms are recognized"""
        validator = RedFlagsValidator()

        resume = self._create_resume_with_description(
            "Practiced Agile and Scrum methodologies. "
            "Implemented DevOps and MLOps practices with CI/CD pipelines."
        )

        result = validator.validate_grammar(resume)
        typo_issues = [i for i in result if i['category'] == 'typo']
        flagged_words = [i['message'] for i in typo_issues]

        methodologies = ['agile', 'scrum', 'devops', 'mlops', 'cicd']
        for method in methodologies:
            assert not any(method in msg.lower() for msg in flagged_words), \
                f"{method} should not be flagged as typo"

    def test_company_names_not_flagged(self):
        """Test that common company names are recognized"""
        validator = RedFlagsValidator()

        resume = self._create_resume_with_description(
            "Worked at Google, Microsoft, and Amazon. "
            "Collaborated with teams at Meta and Netflix."
        )

        result = validator.validate_grammar(resume)
        typo_issues = [i for i in result if i['category'] == 'typo']
        flagged_words = [i['message'] for i in typo_issues]

        companies = ['google', 'microsoft', 'amazon', 'meta', 'netflix']
        for company in companies:
            assert not any(company in msg.lower() for msg in flagged_words), \
                f"{company} should not be flagged as typo"

    def _create_resume_with_description(self, description: str) -> ResumeData:
        """Helper to create resume with given description"""
        return ResumeData(
            fileName="test.pdf",
            contact={"name": "Test User"},
            experience=[{
                "title": "Software Engineer",
                "company": "Tech Company",
                "startDate": "Jan 2020",
                "endDate": "Present",
                "description": description
            }],
            education=[],
            skills=["Python"],
            certifications=[],
            metadata={"pageCount": 1, "wordCount": 400, "fileFormat": "pdf"}
        )


class TestEnhancedGrammarPatterns:
    """Test enhanced grammar pattern detection"""

    def test_verb_tense_consistency(self):
        """Test detection of mixed verb tenses"""
        validator = RedFlagsValidator()

        # Mixed tenses: past and present
        resume = self._create_resume_with_description(
            "Managed a team of 5 engineers and developing new features for the product"
        )

        result = validator.validate_grammar(resume)
        grammar_issues = [i for i in result if i['category'] == 'grammar']

        # Should detect tense inconsistency
        assert len(grammar_issues) > 0, "Should detect mixed verb tenses"
        assert any('tense' in i['message'].lower() for i in grammar_issues), \
            "Should mention tense issue"

    def test_plural_with_numbers(self):
        """Test detection of singular nouns with numbers"""
        validator = RedFlagsValidator()

        # Incorrect: "year" instead of "years"
        resume = self._create_resume_with_description(
            "Software engineer with 5 year of experience in web development"
        )

        result = validator.validate_grammar(resume)
        grammar_issues = [i for i in result if i['category'] == 'grammar']

        # Should detect plural error
        assert len(grammar_issues) > 0, "Should detect singular/plural error"
        assert any('years' in i['message'].lower() or 'plural' in i['message'].lower()
                  for i in grammar_issues), \
            "Should suggest using 'years' (plural)"

    def test_passive_voice_detection(self):
        """Test detection of passive voice overuse"""
        validator = RedFlagsValidator()

        # Multiple passive voice constructions
        resume = self._create_resume_with_description(
            "The project was completed by the team. "
            "The features were implemented by me. "
            "The tests were written by the QA team."
        )

        result = validator.validate_grammar(resume)
        grammar_issues = [i for i in result if i['category'] == 'grammar']

        # Should detect passive voice
        assert len(grammar_issues) > 0, "Should detect passive voice"
        assert any('passive' in i['message'].lower() or 'active' in i['message'].lower()
                  for i in grammar_issues), \
            "Should mention passive voice issue"

    def test_article_errors(self):
        """Test detection of missing articles before professions"""
        validator = RedFlagsValidator()

        # Missing article: should be "an engineer"
        resume = self._create_resume_with_description(
            "I am engineer with 5 years of experience"
        )

        result = validator.validate_grammar(resume)
        grammar_issues = [i for i in result if i['category'] == 'grammar']

        # Should detect missing article
        assert len(grammar_issues) > 0, "Should detect missing article"
        assert any('article' in i['message'].lower() for i in grammar_issues), \
            "Should mention missing article"

    def test_preposition_errors(self):
        """Test detection of incorrect prepositions with companies"""
        validator = RedFlagsValidator()

        # Incorrect: "in Google" should be "at Google"
        resume = self._create_resume_with_description(
            "Worked in Google as a software engineer"
        )

        result = validator.validate_grammar(resume)
        grammar_issues = [i for i in result if i['category'] == 'grammar']

        # Should detect preposition error
        assert len(grammar_issues) > 0, "Should detect preposition error"
        assert any('at' in i['message'].lower() or 'preposition' in i['message'].lower()
                  for i in grammar_issues), \
            "Should suggest using 'at' instead of 'in'"

    def test_sentence_fragments(self):
        """Test detection of sentence fragments without verbs"""
        validator = RedFlagsValidator()

        # Fragment: no verb
        resume = self._create_resume_with_description(
            "Experience in software development. Strong technical skills."
        )

        result = validator.validate_grammar(resume)
        grammar_issues = [i for i in result if i['category'] == 'grammar']

        # Should detect fragments
        assert len(grammar_issues) > 0, "Should detect sentence fragments"
        assert any('fragment' in i['message'].lower() for i in grammar_issues), \
            "Should mention sentence fragment"

    def test_run_on_sentences(self):
        """Test detection of very long sentences"""
        validator = RedFlagsValidator()

        # Very long sentence (40+ words)
        long_sentence = (
            "I managed a team of ten software engineers and we worked on multiple "
            "projects simultaneously and delivered them all on time and within budget "
            "while maintaining high quality standards and meeting all stakeholder "
            "requirements and expectations throughout the entire development cycle "
            "from planning to deployment."
        )
        resume = self._create_resume_with_description(long_sentence)

        result = validator.validate_grammar(resume)
        grammar_issues = [i for i in result if i['category'] == 'grammar']

        # Should detect long sentence
        assert len(grammar_issues) > 0, "Should detect run-on sentence"
        assert any('long' in i['message'].lower() or 'sentence' in i['message'].lower()
                  for i in grammar_issues), \
            "Should mention long sentence"

    def test_no_false_positives_on_good_grammar(self):
        """Test that correct grammar doesn't trigger false positives"""
        validator = RedFlagsValidator()

        # Well-written description
        resume = self._create_resume_with_description(
            "Led a team of 5 engineers in developing scalable microservices. "
            "Implemented CI/CD pipelines using Jenkins and Docker. "
            "Improved system performance by 40% through optimization."
        )

        result = validator.validate_grammar(resume)
        grammar_issues = [i for i in result if i['category'] == 'grammar']

        # Should have minimal or no grammar issues
        assert len(grammar_issues) <= 1, \
            f"Good grammar should not trigger many issues. Found: {grammar_issues}"

    def _create_resume_with_description(self, description: str) -> ResumeData:
        """Helper to create resume with given description"""
        return ResumeData(
            fileName="test.pdf",
            contact={"name": "Test User"},
            experience=[{
                "title": "Software Engineer",
                "company": "Tech Company",
                "startDate": "Jan 2020",
                "endDate": "Present",
                "description": description
            }],
            education=[],
            skills=["Python"],
            certifications=[],
            metadata={"pageCount": 1, "wordCount": 400, "fileFormat": "pdf"}
        )


class TestFalsePositiveReduction:
    """Test that false positives are reduced compared to baseline"""

    def test_technical_resume_false_positive_rate(self):
        """Test false positive rate on a typical technical resume"""
        validator = RedFlagsValidator()

        # Realistic technical resume description
        resume = ResumeData(
            fileName="test.pdf",
            contact={"name": "John Smith"},
            experience=[{
                "title": "Senior Software Engineer",
                "company": "Tech Corp",
                "startDate": "Jan 2020",
                "endDate": "Present",
                "description": (
                    "Developed microservices using Python, Django, and PostgreSQL. "
                    "Deployed applications on AWS using Docker and Kubernetes. "
                    "Implemented CI/CD pipelines with Jenkins and GitLab. "
                    "Led a team of 5 engineers in building scalable APIs. "
                    "Improved system performance by 45% through optimization."
                )
            }],
            education=[{
                "degree": "Bachelor of Science in Computer Science",
                "institution": "University of Technology",
                "graduationDate": "2019"
            }],
            skills=["Python", "JavaScript", "React", "AWS", "Docker"],
            certifications=[],
            metadata={"pageCount": 1, "wordCount": 500, "fileFormat": "pdf"}
        )

        result = validator.validate_grammar(resume)
        typo_issues = [i for i in result if i['category'] == 'typo']

        # Should have very few or no false positives on technical terms
        # Target: <5% false positive rate (0-1 issues in this text)
        assert len(typo_issues) <= 1, \
            f"Too many false positives. Expected ≤1, got {len(typo_issues)}: {typo_issues}"

    def test_devops_resume_false_positive_rate(self):
        """Test false positive rate on DevOps-focused resume"""
        validator = RedFlagsValidator()

        resume = ResumeData(
            fileName="test.pdf",
            contact={"name": "Jane Doe"},
            experience=[{
                "title": "DevOps Engineer",
                "company": "Cloud Inc",
                "startDate": "Jan 2019",
                "endDate": "Present",
                "description": (
                    "Managed infrastructure on AWS, Azure, and GCP. "
                    "Automated deployments using Terraform and Ansible. "
                    "Implemented monitoring with Prometheus and Grafana. "
                    "Built CI/CD pipelines using Jenkins and GitLab. "
                    "Containerized applications with Docker and Kubernetes."
                )
            }],
            education=[],
            skills=["AWS", "Terraform", "Docker", "Kubernetes"],
            certifications=[],
            metadata={"pageCount": 1, "wordCount": 400, "fileFormat": "pdf"}
        )

        result = validator.validate_grammar(resume)
        typo_issues = [i for i in result if i['category'] == 'typo']

        # Should recognize all DevOps terms
        assert len(typo_issues) <= 1, \
            f"DevOps terms flagged as typos: {typo_issues}"


class TestPerformance:
    """Test that performance is not regressed"""

    def test_grammar_check_performance(self):
        """Test that grammar checking completes in reasonable time"""
        import time

        validator = RedFlagsValidator()

        # Create resume with multiple sections
        resume = ResumeData(
            fileName="test.pdf",
            contact={
                "name": "Test User",
                "summary": "Experienced software engineer with 10 years in web development"
            },
            experience=[{
                "title": "Software Engineer",
                "company": "Tech Company",
                "startDate": "Jan 2020",
                "endDate": "Present",
                "description": (
                    "Developed web applications using React and Node.js. "
                    "Built RESTful APIs with Express and MongoDB. "
                    "Implemented automated testing with Jest and Cypress. "
                    "Deployed applications to AWS using Docker containers."
                )
            }] * 3,  # Multiple experiences
            education=[{
                "degree": "Bachelor of Science",
                "institution": "University",
                "graduationDate": "2015"
            }],
            skills=["Python", "JavaScript"],
            certifications=[],
            metadata={"pageCount": 1, "wordCount": 600, "fileFormat": "pdf"}
        )

        start_time = time.time()
        result = validator.validate_grammar(resume)
        end_time = time.time()

        duration = end_time - start_time

        # Should complete in under 2 seconds for typical resume
        assert duration < 2.0, \
            f"Grammar check took too long: {duration:.2f}s (expected <2s)"

        # Should return some results (not empty)
        assert isinstance(result, list), "Should return a list of issues"


class TestIntegration:
    """Integration tests for the complete validation flow"""

    def test_full_resume_validation(self):
        """Test complete validation including grammar improvements"""
        validator = RedFlagsValidator()

        resume = ResumeData(
            fileName="test.pdf",
            contact={
                "name": "John Doe",
                "email": "john.doe@gmail.com",
                "phone": "555-1234",
                "location": "San Francisco, CA",
                "summary": "Senior engineer with 8 years of experience"
            },
            experience=[{
                "title": "Senior Software Engineer",
                "company": "Google",
                "startDate": "Jan 2020",
                "endDate": "Present",
                "description": (
                    "Led development of microservices using Python and Kubernetes. "
                    "Improved system performance by 50% through optimization. "
                    "Mentored junior engineers in best practices."
                )
            }],
            education=[{
                "degree": "Bachelor of Science in Computer Science",
                "institution": "Stanford University",
                "graduationDate": "2015"
            }],
            skills=["Python", "Kubernetes", "AWS", "Docker"],
            certifications=[],
            metadata={"pageCount": 1, "wordCount": 500, "fileFormat": "pdf"}
        )

        # Run all validations
        result = validator.validate_resume(resume, role="Software Engineer", level="senior")

        # Should successfully complete
        assert 'critical' in result
        assert 'warnings' in result
        assert 'suggestions' in result

        # Should have minimal issues on well-formatted resume
        total_issues = (
            len(result['critical']) +
            len(result['warnings']) +
            len(result['suggestions'])
        )
        assert total_issues < 10, \
            f"Well-formatted resume should have few issues. Found {total_issues}"

    def test_backwards_compatibility(self):
        """Test that existing functionality still works"""
        validator = RedFlagsValidator()

        # Test with old-style resume (minimal data)
        resume = ResumeData(
            fileName="test.pdf",
            contact={},
            experience=[{
                "title": "Engineer",
                "company": "Company",
                "startDate": "Jan 2020",
                "endDate": "Present",
                "description": "Worked on projects"
            }],
            education=[],
            skills=["Python"],
            certifications=[],
            metadata={"pageCount": 1, "wordCount": 200, "fileFormat": "pdf"}
        )

        # Should not crash with minimal data
        result = validator.validate_resume(resume, role="Engineer", level="mid")

        assert isinstance(result, dict)
        assert 'critical' in result
        assert 'warnings' in result
        assert 'suggestions' in result


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
