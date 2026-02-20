"""
Skills Categorization Service

Categorizes skills into Hard Skills (technical) and Soft Skills (interpersonal).
Provides separate match rates for each category to help users understand gaps.

Hard Skills: Technical, measurable skills (Python, AWS, Project Management)
Soft Skills: Interpersonal, behavioral skills (Leadership, Communication, Teamwork)
"""

import re
from typing import Dict, List, Set, Tuple, Any
from dataclasses import dataclass


@dataclass
class SkillMatch:
    """Represents a skill match between resume and job description"""
    skill: str
    category: str  # 'hard' or 'soft'
    found_in_resume: bool
    found_in_job: bool
    similarity_score: float = 1.0  # For semantic matching (future enhancement)


class SkillsCategorizer:
    """
    Categorizes and matches skills between resume and job description.

    Uses comprehensive taxonomies for hard and soft skills across
    common industries and roles.
    """

    # Comprehensive Hard Skills Taxonomy
    HARD_SKILLS = {
        # Programming Languages
        'programming': [
            'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'ruby',
            'go', 'golang', 'rust', 'php', 'swift', 'kotlin', 'scala', 'r',
            'matlab', 'perl', 'shell', 'bash', 'powershell', 'sql', 'nosql'
        ],

        # Web Development
        'web_development': [
            'html', 'css', 'react', 'angular', 'vue', 'node.js', 'express',
            'django', 'flask', 'fastapi', 'spring boot', 'asp.net', 'nextjs',
            'gatsby', 'webpack', 'vite', 'rest api', 'graphql', 'websockets'
        ],

        # Cloud & DevOps
        'cloud_devops': [
            'aws', 'azure', 'gcp', 'google cloud', 'docker', 'kubernetes', 'k8s',
            'jenkins', 'gitlab ci', 'github actions', 'circleci', 'terraform',
            'ansible', 'puppet', 'chef', 'cloudformation', 'ci/cd', 'devops'
        ],

        # Data & Analytics
        'data_analytics': [
            'machine learning', 'deep learning', 'data science', 'data analysis',
            'pandas', 'numpy', 'scikit-learn', 'tensorflow', 'pytorch', 'keras',
            'tableau', 'power bi', 'looker', 'sql', 'spark', 'hadoop', 'etl',
            'data visualization', 'statistics', 'predictive modeling'
        ],

        # Databases
        'databases': [
            'postgresql', 'mysql', 'mongodb', 'redis', 'elasticsearch',
            'oracle', 'sql server', 'dynamodb', 'cassandra', 'neo4j',
            'database design', 'database administration', 'dba'
        ],

        # Business & Finance
        'business_finance': [
            'excel', 'financial modeling', 'financial analysis', 'accounting',
            'quickbooks', 'sap', 'erp', 'crm', 'salesforce', 'hubspot',
            'budget management', 'forecasting', 'p&l', 'gaap', 'ifrs'
        ],

        # Project Management
        'project_management': [
            'jira', 'asana', 'trello', 'monday.com', 'ms project', 'agile',
            'scrum', 'kanban', 'waterfall', 'pmp', 'prince2', 'six sigma',
            'lean', 'change management', 'risk management'
        ],

        # Design & Creative
        'design': [
            'photoshop', 'illustrator', 'indesign', 'figma', 'sketch', 'adobe xd',
            'ui design', 'ux design', 'graphic design', 'web design', 'wireframing',
            'prototyping', 'user research', 'usability testing', 'accessibility'
        ],

        # Marketing
        'marketing': [
            'seo', 'sem', 'google analytics', 'google ads', 'facebook ads',
            'email marketing', 'content marketing', 'social media marketing',
            'marketing automation', 'mailchimp', 'hootsuite', 'buffer'
        ],

        # Security
        'security': [
            'cybersecurity', 'information security', 'penetration testing',
            'ethical hacking', 'cissp', 'ceh', 'security+', 'firewall',
            'encryption', 'vulnerability assessment', 'compliance', 'gdpr'
        ],

        # Engineering
        'engineering': [
            'autocad', 'solidworks', 'catia', 'ansys', 'matlab', 'cad',
            'circuit design', 'pcb design', 'plc programming', 'hvac'
        ],

        # Healthcare
        'healthcare': [
            'electronic medical records', 'emr', 'epic', 'cerner', 'medical coding',
            'icd-10', 'cpt', 'hipaa', 'patient care', 'clinical research'
        ],

        # Languages (Foreign)
        'languages': [
            'spanish', 'french', 'german', 'mandarin', 'chinese', 'japanese',
            'arabic', 'portuguese', 'italian', 'bilingual', 'multilingual'
        ],

        # Certifications
        'certifications': [
            'aws certified', 'azure certified', 'google cloud certified',
            'certified scrum master', 'csm', 'pmp', 'comptia', 'ccna', 'ccnp'
        ]
    }

    # Comprehensive Soft Skills Taxonomy
    SOFT_SKILLS = {
        # Leadership
        'leadership': [
            'leadership', 'team leadership', 'people management', 'coaching',
            'mentoring', 'delegation', 'strategic thinking', 'vision',
            'decision making', 'conflict resolution', 'empowerment'
        ],

        # Communication
        'communication': [
            'communication', 'verbal communication', 'written communication',
            'presentation', 'public speaking', 'active listening', 'negotiation',
            'persuasion', 'storytelling', 'interpersonal skills', 'articulate'
        ],

        # Teamwork & Collaboration
        'teamwork': [
            'teamwork', 'collaboration', 'cross-functional collaboration',
            'team player', 'cooperative', 'supportive', 'relationship building',
            'networking', 'stakeholder management', 'partnership'
        ],

        # Problem Solving
        'problem_solving': [
            'problem solving', 'analytical thinking', 'critical thinking',
            'troubleshooting', 'root cause analysis', 'creative thinking',
            'innovation', 'resourcefulness', 'solution oriented'
        ],

        # Adaptability
        'adaptability': [
            'adaptability', 'flexibility', 'agile', 'resilience', 'learning agility',
            'open minded', 'versatile', 'quick learner', 'change management',
            'growth mindset', 'continuous learning'
        ],

        # Work Ethic
        'work_ethic': [
            'work ethic', 'dedication', 'commitment', 'reliability', 'dependable',
            'self motivated', 'initiative', 'proactive', 'driven', 'diligent',
            'conscientious', 'professional'
        ],

        # Time Management
        'time_management': [
            'time management', 'organizational skills', 'prioritization',
            'multitasking', 'deadline driven', 'efficient', 'productivity',
            'planning', 'scheduling', 'task management'
        ],

        # Emotional Intelligence
        'emotional_intelligence': [
            'emotional intelligence', 'empathy', 'self awareness', 'social awareness',
            'relationship management', 'emotional regulation', 'sensitivity',
            'compassion', 'understanding'
        ],

        # Customer Service
        'customer_service': [
            'customer service', 'customer focus', 'client relations',
            'customer satisfaction', 'patient', 'friendly', 'helpful',
            'service oriented', 'customer centric'
        ],

        # Attention to Detail
        'attention_to_detail': [
            'attention to detail', 'detail oriented', 'accuracy', 'precision',
            'thoroughness', 'quality focused', 'meticulous', 'careful'
        ]
    }

    def __init__(self):
        """Initialize skills categorizer with flattened skill lists"""
        # Flatten hard skills into a single set
        self.hard_skills_set = set()
        for category_skills in self.HARD_SKILLS.values():
            self.hard_skills_set.update(skill.lower() for skill in category_skills)

        # Flatten soft skills into a single set
        self.soft_skills_set = set()
        for category_skills in self.SOFT_SKILLS.values():
            self.soft_skills_set.update(skill.lower() for skill in category_skills)

        # Create reverse lookup for skill categories
        self.skill_to_category = {}

        # Map hard skills to their categories
        for category, skills in self.HARD_SKILLS.items():
            for skill in skills:
                self.skill_to_category[skill.lower()] = ('hard', category)

        # Map soft skills to their categories
        for category, skills in self.SOFT_SKILLS.items():
            for skill in skills:
                self.skill_to_category[skill.lower()] = ('soft', category)

    def extract_skills(self, text: str) -> Dict[str, List[str]]:
        """
        Extract both hard and soft skills from text.

        Args:
            text: Resume or job description text

        Returns:
            Dict with 'hard_skills' and 'soft_skills' lists
        """
        text_lower = text.lower()

        # Extract hard skills
        hard_skills_found = []
        for skill in self.hard_skills_set:
            # Use word boundaries to avoid partial matches
            # e.g., "java" should not match "javascript"
            pattern = r'\b' + re.escape(skill) + r'\b'
            if re.search(pattern, text_lower):
                hard_skills_found.append(skill)

        # Extract soft skills
        soft_skills_found = []
        for skill in self.soft_skills_set:
            pattern = r'\b' + re.escape(skill) + r'\b'
            if re.search(pattern, text_lower):
                soft_skills_found.append(skill)

        return {
            'hard_skills': sorted(list(set(hard_skills_found))),
            'soft_skills': sorted(list(set(soft_skills_found)))
        }

    def categorize_skills(self, resume_text: str, job_description: str = None) -> Dict[str, Any]:
        """
        Categorize and match skills between resume and job description.

        Args:
            resume_text: Full resume text
            job_description: Optional job description text

        Returns:
            Dict with comprehensive skills analysis
        """
        # Extract skills from resume
        resume_skills = self.extract_skills(resume_text)

        result = {
            'resume_skills': resume_skills,
            'resume_skills_count': {
                'hard_skills': len(resume_skills['hard_skills']),
                'soft_skills': len(resume_skills['soft_skills']),
                'total': len(resume_skills['hard_skills']) + len(resume_skills['soft_skills'])
            }
        }

        # If job description provided, calculate matches
        if job_description:
            job_skills = self.extract_skills(job_description)

            # Calculate matches for hard skills
            hard_matches = self._calculate_matches(
                resume_skills['hard_skills'],
                job_skills['hard_skills']
            )

            # Calculate matches for soft skills
            soft_matches = self._calculate_matches(
                resume_skills['soft_skills'],
                job_skills['soft_skills']
            )

            result.update({
                'job_skills': job_skills,
                'job_skills_count': {
                    'hard_skills': len(job_skills['hard_skills']),
                    'soft_skills': len(job_skills['soft_skills']),
                    'total': len(job_skills['hard_skills']) + len(job_skills['soft_skills'])
                },
                'hard_skills_analysis': hard_matches,
                'soft_skills_analysis': soft_matches,
                'overall_match': self._calculate_overall_match(hard_matches, soft_matches),
                'recommendations': self._generate_recommendations(hard_matches, soft_matches)
            })

        return result

    def _calculate_matches(self, resume_skills: List[str], job_skills: List[str]) -> Dict[str, Any]:
        """
        Calculate match statistics between resume and job skills.

        Args:
            resume_skills: Skills found in resume
            job_skills: Skills found in job description

        Returns:
            Dict with match statistics
        """
        if not job_skills:
            return {
                'match_rate': 0.0,
                'matched_skills': [],
                'missing_skills': [],
                'extra_skills': resume_skills,
                'match_count': 0,
                'missing_count': 0
            }

        resume_set = set(skill.lower() for skill in resume_skills)
        job_set = set(skill.lower() for skill in job_skills)

        # Calculate matches
        matched = resume_set.intersection(job_set)
        missing = job_set - resume_set
        extra = resume_set - job_set

        # Calculate match rate
        match_rate = (len(matched) / len(job_set) * 100) if job_set else 0

        return {
            'match_rate': round(match_rate, 1),
            'matched_skills': sorted(list(matched)),
            'missing_skills': sorted(list(missing)),
            'extra_skills': sorted(list(extra)),
            'match_count': len(matched),
            'missing_count': len(missing),
            'rating': self._get_match_rating(match_rate)
        }

    def _calculate_overall_match(self, hard_analysis: Dict, soft_analysis: Dict) -> Dict[str, Any]:
        """
        Calculate overall match score combining hard and soft skills.

        Weighting: 70% hard skills, 30% soft skills (typical ATS priority)

        Args:
            hard_analysis: Hard skills match analysis
            soft_analysis: Soft skills match analysis

        Returns:
            Dict with overall match statistics
        """
        hard_rate = hard_analysis.get('match_rate', 0)
        soft_rate = soft_analysis.get('match_rate', 0)

        # Weighted average (hard skills weighted more heavily)
        overall_rate = (hard_rate * 0.70) + (soft_rate * 0.30)

        return {
            'overall_match_rate': round(overall_rate, 1),
            'hard_skills_weight': '70%',
            'soft_skills_weight': '30%',
            'rating': self._get_match_rating(overall_rate),
            'summary': self._generate_match_summary(overall_rate, hard_rate, soft_rate)
        }

    def _get_match_rating(self, match_rate: float) -> str:
        """Convert match rate to human-readable rating"""
        if match_rate >= 80:
            return "Excellent"
        elif match_rate >= 60:
            return "Very Good"
        elif match_rate >= 40:
            return "Good"
        elif match_rate >= 25:
            return "Fair"
        else:
            return "Needs Improvement"

    def _generate_match_summary(self, overall: float, hard: float, soft: float) -> str:
        """Generate human-readable summary of match results"""
        if overall >= 70:
            return f"Strong match! Your skills align well with the job requirements."
        elif overall >= 50:
            return f"Good foundation. Consider adding a few key skills to strengthen your match."
        elif overall >= 30:
            return f"Moderate match. Several important skills are missing from your resume."
        else:
            return f"Weak match. Your resume is missing many required skills for this role."

    def _generate_recommendations(self, hard_analysis: Dict, soft_analysis: Dict) -> List[str]:
        """
        Generate actionable recommendations based on skills analysis.

        Args:
            hard_analysis: Hard skills match analysis
            soft_analysis: Soft skills match analysis

        Returns:
            List of recommendation strings
        """
        recommendations = []

        # Hard skills recommendations
        hard_missing = hard_analysis.get('missing_skills', [])
        if len(hard_missing) > 0:
            top_missing = hard_missing[:5]  # Show top 5
            skills_str = ", ".join(top_missing)
            recommendations.append(
                f"Add these technical skills to your resume: {skills_str}"
            )

        if hard_analysis.get('match_rate', 0) < 50:
            recommendations.append(
                "Your technical skills match is below 50%. Focus on adding relevant technical skills from the job description."
            )

        # Soft skills recommendations
        soft_missing = soft_analysis.get('missing_skills', [])
        if len(soft_missing) > 0:
            top_missing = soft_missing[:3]  # Show top 3
            skills_str = ", ".join(top_missing)
            recommendations.append(
                f"Highlight these soft skills in your experience: {skills_str}"
            )

        # Balance recommendation
        hard_count = len(hard_analysis.get('matched_skills', []))
        soft_count = len(soft_analysis.get('matched_skills', []))

        if hard_count > 0 and soft_count == 0:
            recommendations.append(
                "Your resume focuses heavily on technical skills. Consider adding soft skills to show well-roundedness."
            )
        elif soft_count > 0 and hard_count == 0:
            recommendations.append(
                "Your resume highlights soft skills but lacks technical skills. Add specific technical competencies."
            )

        # General recommendation if doing well
        if not recommendations:
            recommendations.append(
                "Great job! Your skills are well-aligned with the job requirements."
            )

        return recommendations

    def get_skill_category(self, skill: str) -> Tuple[str, str]:
        """
        Get the category of a specific skill.

        Args:
            skill: Skill name

        Returns:
            Tuple of (type, category) where type is 'hard' or 'soft'
            Returns (None, None) if skill not in taxonomy
        """
        skill_lower = skill.lower()
        return self.skill_to_category.get(skill_lower, (None, None))

    def get_skills_by_category(self, skills: List[str]) -> Dict[str, List[str]]:
        """
        Group skills by their sub-categories (e.g., programming, leadership).

        Args:
            skills: List of skill names

        Returns:
            Dict mapping category names to lists of skills
        """
        categorized = {}

        for skill in skills:
            skill_type, category = self.get_skill_category(skill)
            if category:
                if category not in categorized:
                    categorized[category] = []
                categorized[category].append(skill)

        return categorized


# Convenience function for quick analysis
def analyze_skills(resume_text: str, job_description: str = None) -> Dict[str, Any]:
    """
    Quick function to analyze skills in a resume.

    Usage:
        result = analyze_skills(resume_text, job_description)
        print(f"Hard Skills Match: {result['hard_skills_analysis']['match_rate']}%")
        print(f"Soft Skills Match: {result['soft_skills_analysis']['match_rate']}%")
    """
    categorizer = SkillsCategorizer()
    return categorizer.categorize_skills(resume_text, job_description)
