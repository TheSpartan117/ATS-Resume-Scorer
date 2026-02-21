"""
Enhanced suggestion generator with specific, actionable recommendations.

This module transforms vague suggestions into concrete, actionable guidance
with templates, examples, and specific keywords.
"""

from typing import List, Dict, Optional, Set
import re
from backend.services.parser import ResumeData
from backend.services.role_taxonomy import get_role_scoring_data


class EnhancedSuggestionGenerator:
    """
    Generates specific, actionable suggestions for resume improvement.

    Features:
    - Role-specific templates with examples
    - Exact keyword lists to add
    - Before/after writing improvements
    - Specific formatting fixes
    - Placement guidance
    """

    def __init__(self, role: str, level: str, job_description: str = ""):
        """
        Initialize generator with role context.

        Args:
            role: Role ID (e.g., "software_engineer")
            level: Experience level (e.g., "mid", "senior")
            job_description: Optional job description for keyword extraction
        """
        self.role = role
        self.level = level
        self.job_description = job_description
        self.role_data = get_role_scoring_data(role, level)

    def generate_suggestions(
        self,
        resume_data: ResumeData,
        missing_keywords: List[str] = None,
        weak_bullets: List[Dict] = None,
        format_issues: List[str] = None
    ) -> List[Dict]:
        """
        Generate comprehensive, specific suggestions.

        Args:
            resume_data: Parsed resume data
            missing_keywords: List of missing important keywords
            weak_bullets: List of weak bullet points to improve
            format_issues: List of formatting issues detected

        Returns:
            List of detailed suggestion objects
        """
        suggestions = []

        # 1. Missing content with templates
        if not resume_data.contact or not resume_data.contact.get('name'):
            suggestions.append(self._missing_summary_template())

        # 2. Missing keywords with exact terms and placement
        if missing_keywords and len(missing_keywords) > 0:
            suggestions.append(self._missing_keywords_specific(missing_keywords))

        # 3. Weak descriptions with rewrites
        if weak_bullets and len(weak_bullets) > 0:
            suggestions.append(self._strengthen_bullets(weak_bullets))

        # 4. Formatting issues with exact fixes
        if format_issues and len(format_issues) > 0:
            suggestions.append(self._format_fixes(format_issues))

        # 5. Missing sections
        missing_sections = self._detect_missing_sections(resume_data)
        for section in missing_sections:
            suggestions.append(self._missing_section_template(section))

        return suggestions

    def _missing_summary_template(self) -> Dict:
        """Generate specific template for professional summary."""
        role_name = self.role.replace('_', ' ').title()

        # Level-specific templates
        templates = {
            'entry': f"Entry-level {role_name} with [X years/months] of experience in [specific skills]. "
                    f"Passionate about [area of interest]. Strong foundation in [key technologies]. "
                    f"Seeking to contribute [your strengths] to a dynamic team.",

            'mid': f"Results-driven {role_name} with [X years] of experience in [specialization]. "
                  f"Proven track record in [key achievements with metrics]. "
                  f"Proficient in [tech stack/tools]. "
                  f"Seeking to leverage [your strengths] in a [target role] position.",

            'senior': f"Senior {role_name} with [X+ years] of extensive experience in [domain]. "
                     f"Led [number] teams/projects delivering [impact with metrics]. "
                     f"Expert in [technologies/methodologies]. "
                     f"Seeking to drive [technical strategy/innovation] as [Lead/Principal/target role].",

            'lead': f"Accomplished {role_name} leader with [X+ years] of experience. "
                   f"Directed [scale of responsibility]. "
                   f"Proven expertise in [strategic areas]. "
                   f"Seeking to shape [organization/team] direction as [target role].",

            'executive': f"Visionary {role_name} executive with [X+ years] at scale. "
                        f"Transformed [organizations/products] achieving [business outcomes]. "
                        f"Strategic leader in [domain expertise]. "
                        f"Driving [business value/innovation] as [target role]."
        }

        template = templates.get(self.level, templates['mid'])

        # Role-specific example
        examples = self._get_role_examples()
        example = examples.get('summary', '')

        return {
            'id': 'missing-summary',
            'type': 'missing_content',
            'severity': 'high',
            'title': 'Add Professional Summary',
            'description': 'Professional summary is missing - this is the first thing recruiters and ATS systems read',
            'template': f"""<div class="space-y-4">
<h3 class="text-lg font-semibold text-gray-900">Professional Summary Template</h3>
<div class="bg-blue-50 border-l-4 border-blue-500 p-4 rounded">
<p class="text-sm text-gray-800">{template}</p>
</div>

<h4 class="text-md font-semibold text-gray-900 mt-4">Example for {role_name} ({self.level}):</h4>
<div class="bg-green-50 border-l-4 border-green-500 p-4 rounded">
<p class="text-sm text-gray-800">{example}</p>
</div>

<div class="mt-4">
<h4 class="text-sm font-semibold text-gray-700 mb-2">Fill in these placeholders:</h4>
<ul class="list-disc list-inside text-sm text-gray-700 space-y-1">
<li><strong>[X years]:</strong> Your years of experience (e.g., "5+ years", "3 years")</li>
<li><strong>[Key Skills]:</strong> Your top 3-5 technical/core skills</li>
<li><strong>[Achievements]:</strong> Your biggest accomplishments with numbers</li>
<li><strong>[Target Role]:</strong> The role you're applying for</li>
</ul>
</div>

<div class="mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded">
<p class="text-sm text-gray-800"><strong>Pro Tip:</strong> Keep it to 3-4 sentences (50-100 words). Place at the very top of your resume, right after your contact information.</p>
</div>
</div>""",
            'quickFix': {
                'before': '[No professional summary]',
                'after': template,
                'action': 'insert',
                'location': 'Top of resume, after contact info'
            }
        }

    def _missing_keywords_specific(self, missing_keywords: List[str]) -> Dict:
        """Generate specific keyword suggestions with categorization."""

        # Categorize keywords by type
        categories = {
            'Programming Languages': [],
            'Frameworks & Libraries': [],
            'Cloud & DevOps': [],
            'Databases': [],
            'Tools & Technologies': [],
            'Methodologies': [],
            'Soft Skills': []
        }

        # Common patterns for categorization
        programming_langs = {'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'ruby', 'go', 'rust', 'php', 'swift', 'kotlin'}
        frameworks = {'react', 'angular', 'vue', 'django', 'flask', 'spring', 'express', 'node.js', 'next.js', '.net', 'fastapi'}
        cloud_devops = {'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'jenkins', 'ci/cd', 'terraform', 'ansible', 'gitlab'}
        databases = {'mysql', 'postgresql', 'mongodb', 'redis', 'dynamodb', 'elasticsearch', 'cassandra', 'oracle'}
        methodologies = {'agile', 'scrum', 'kanban', 'devops', 'tdd', 'ci/cd', 'microservices', 'rest', 'graphql'}
        soft_skills = {'leadership', 'communication', 'collaboration', 'problem-solving', 'mentoring', 'team player'}

        for keyword in missing_keywords[:25]:  # Top 25
            kw_lower = keyword.lower()

            if any(lang in kw_lower for lang in programming_langs):
                categories['Programming Languages'].append(keyword)
            elif any(fw in kw_lower for fw in frameworks):
                categories['Frameworks & Libraries'].append(keyword)
            elif any(cloud in kw_lower for cloud in cloud_devops):
                categories['Cloud & DevOps'].append(keyword)
            elif any(db in kw_lower for db in databases):
                categories['Databases'].append(keyword)
            elif any(meth in kw_lower for meth in methodologies):
                categories['Methodologies'].append(keyword)
            elif any(skill in kw_lower for skill in soft_skills):
                categories['Soft Skills'].append(keyword)
            else:
                categories['Tools & Technologies'].append(keyword)

        # Build keyword list HTML
        keyword_list_html = []
        for category, terms in categories.items():
            if terms:
                keyword_list_html.append(
                    f'<li><strong>{category}:</strong> {", ".join(terms[:8])}</li>'
                )

        total_keywords = len(missing_keywords)
        role_name = self.role.replace('_', ' ').title()

        return {
            'id': 'missing-keywords',
            'type': 'keyword',
            'severity': 'high',
            'title': f'Add {total_keywords} Missing Keywords',
            'description': f'Your resume is missing {total_keywords} important keywords for {role_name} roles. ATS systems will flag this.',
            'template': f"""<div class="space-y-4">
<h3 class="text-lg font-semibold text-gray-900">Keywords to Add</h3>
<div class="bg-red-50 border-l-4 border-red-500 p-4 rounded">
<p class="text-sm text-red-900 mb-3"><strong>Critical:</strong> These keywords are essential for passing ATS screening for {role_name} positions.</p>
</div>

<div class="mt-4">
<h4 class="text-md font-semibold text-gray-900 mb-2">Add these keywords by category:</h4>
<ul class="list-disc list-inside text-sm text-gray-700 space-y-2">
{''.join(keyword_list_html)}
</ul>
</div>

<div class="mt-4">
<h4 class="text-md font-semibold text-gray-900 mb-2">Where to Add Them:</h4>
<ol class="list-decimal list-inside text-sm text-gray-700 space-y-2">
<li><strong>Skills Section:</strong> Create or update a "Technical Skills" or "Core Competencies" section
<div class="ml-6 mt-1 p-2 bg-gray-100 rounded text-xs font-mono">
Technical Skills<br/>
• Programming Languages: Python (Expert), JavaScript (Proficient), Java (Familiar)<br/>
• Frameworks: React, Django, Flask, Node.js<br/>
• Cloud & DevOps: AWS (EC2, S3, Lambda), Docker, Kubernetes
</div>
</li>
<li><strong>Experience Descriptions:</strong> Weave keywords naturally into your bullet points
<div class="ml-6 mt-1 p-2 bg-gray-100 rounded text-xs">
<span class="text-red-600">Bad:</span> "Worked on web applications"<br/>
<span class="text-green-600">Good:</span> "Developed scalable web applications using <strong>React</strong> and <strong>Node.js</strong>, deployed on <strong>AWS</strong>"
</div>
</li>
<li><strong>Project Sections:</strong> Mention technologies in project descriptions</li>
</ol>
</div>

<div class="mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded">
<p class="text-sm text-gray-800"><strong>Important:</strong> Only add skills you actually have experience with. Be prepared to discuss any keyword on your resume in interviews.</p>
</div>

<div class="mt-4">
<h4 class="text-sm font-semibold text-gray-700 mb-2">Consider Adding Proficiency Levels:</h4>
<ul class="text-xs text-gray-600 space-y-1">
<li>• <strong>Expert:</strong> 3+ years, can mentor others</li>
<li>• <strong>Proficient:</strong> 1-3 years, comfortable working independently</li>
<li>• <strong>Familiar:</strong> Some experience, can work with guidance</li>
</ul>
</div>
</div>""",
            'quickFix': {
                'before': '[Keywords missing from resume]',
                'after': f"Added {min(total_keywords, 10)} keywords: {', '.join(missing_keywords[:10])}...",
                'action': 'insert',
                'location': 'Skills section and Experience descriptions'
            },
            'keywords': missing_keywords[:25]  # Include raw list for frontend
        }

    def _strengthen_bullets(self, weak_bullets: List[Dict]) -> Dict:
        """Generate specific rewrites for weak bullet points."""

        # Get action verbs from role taxonomy
        action_verbs = self.role_data.get('action_verbs', []) if self.role_data else []

        # Build rewrite examples for top 3 weak bullets
        rewrites = []
        for i, bullet in enumerate(weak_bullets[:3]):
            original = bullet.get('text', bullet.get('description', ''))
            improved = self._rewrite_bullet(original, action_verbs)

            rewrites.append(f"""<div class="border-b border-gray-200 pb-3 mb-3">
<div class="bg-red-50 border border-red-200 rounded p-3 mb-2">
<div class="text-xs font-semibold text-red-700 mb-1">❌ Original (Weak):</div>
<div class="text-sm text-red-900">{original}</div>
</div>
<div class="bg-green-50 border border-green-200 rounded p-3">
<div class="text-xs font-semibold text-green-700 mb-1">✅ Improved (Strong):</div>
<div class="text-sm text-green-900">{improved}</div>
</div>
</div>""")

        # Get role-specific action verbs
        verb_categories = {
            'Leadership': ['Led', 'Managed', 'Directed', 'Coordinated', 'Mentored', 'Supervised', 'Guided', 'Spearheaded'],
            'Achievement': ['Achieved', 'Delivered', 'Exceeded', 'Accelerated', 'Improved', 'Increased', 'Boosted', 'Enhanced'],
            'Technical': ['Developed', 'Architected', 'Implemented', 'Optimized', 'Automated', 'Engineered', 'Built', 'Designed'],
            'Collaboration': ['Collaborated', 'Partnered', 'Coordinated', 'Facilitated', 'Consulted', 'Engaged', 'Aligned']
        }

        verb_html = []
        for category, verbs in verb_categories.items():
            verb_html.append(f'<li><strong>{category}:</strong> {", ".join(verbs)}</li>')

        return {
            'id': 'weak-bullets',
            'type': 'writing',
            'severity': 'medium',
            'title': 'Strengthen Experience Descriptions',
            'description': 'Your experience bullets lack impact, specificity, and quantifiable results',
            'template': f"""<div class="space-y-4">
<h3 class="text-lg font-semibold text-gray-900">Before & After Examples</h3>
<div class="space-y-3">
{''.join(rewrites)}
</div>

<div class="mt-6 p-4 bg-blue-50 border border-blue-200 rounded">
<h4 class="text-md font-semibold text-gray-900 mb-3">Formula for Strong Bullets:</h4>
<div class="bg-white p-3 rounded border border-blue-300 font-mono text-sm">
[Action Verb] + [What you did] + [Technology/Tools used] + [Measurable Impact/Result]
</div>
<div class="mt-3 text-sm text-gray-700">
<p><strong>Example:</strong></p>
<p class="mt-1 text-green-800">"<strong>Developed</strong> and launched 5 microservices using <strong>Python and Docker</strong>, reducing system latency by <strong>40%</strong> and improving user experience for <strong>50K+ daily users</strong>"</p>
</div>
</div>

<div class="mt-4">
<h4 class="text-md font-semibold text-gray-900 mb-2">Power Action Verbs by Type:</h4>
<ul class="list-disc list-inside text-sm text-gray-700 space-y-1">
{''.join(verb_html)}
</ul>
</div>

<div class="mt-4">
<h4 class="text-md font-semibold text-gray-900 mb-2">Always Include Metrics:</h4>
<ul class="text-sm text-gray-700 space-y-1">
<li>• <strong>Team size:</strong> "Led team of 5 engineers"</li>
<li>• <strong>User impact:</strong> "Serving 10K+ daily active users"</li>
<li>• <strong>Performance:</strong> "Reduced load time by 40%"</li>
<li>• <strong>Timeline:</strong> "Delivered 2 weeks ahead of schedule"</li>
<li>• <strong>Revenue/Cost:</strong> "Generated $500K in savings"</li>
<li>• <strong>Scale:</strong> "Processing 1M+ transactions daily"</li>
</ul>
</div>

<div class="mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded">
<p class="text-sm text-gray-800"><strong>Pro Tip:</strong> If you don't have exact metrics, use estimates: "~50K users", "multiple projects", "significant improvement"</p>
</div>
</div>""",
            'quickFix': {
                'before': weak_bullets[0].get('text', weak_bullets[0].get('description', '')),
                'after': self._rewrite_bullet(weak_bullets[0].get('text', weak_bullets[0].get('description', '')), action_verbs),
                'action': 'replace',
                'location': 'Experience section bullet points'
            }
        }

    def _rewrite_bullet(self, original: str, action_verbs: List[str] = None) -> str:
        """Rewrite a weak bullet point with impact."""

        # Common weak patterns and their improvements
        if 'worked on' in original.lower():
            return original.replace('Worked on', 'Developed and maintained').replace('worked on', 'developed and maintained') + ' [Add: serving X users OR achieving Y% improvement]'

        if 'responsible for' in original.lower():
            return original.replace('Responsible for', 'Led').replace('responsible for', 'led') + ' [Add: achieving X result with Y team in Z timeframe]'

        if 'helped' in original.lower() or 'assisted' in original.lower():
            return original.replace('Helped', 'Collaborated with').replace('helped', 'collaborated with').replace('Assisted', 'Supported').replace('assisted', 'supported') + ' [Add: delivering X outcome using Y technology]'

        # If no weak pattern detected, add guidance
        if not any(char.isdigit() for char in original):
            return f"{original} [Add specific metrics: X% improvement, Y users impacted, Z projects delivered]"

        return original + " [Add: technology stack used and business impact]"

    def _format_fixes(self, format_issues: List[str]) -> Dict:
        """Generate specific formatting fix instructions."""

        fixes = []
        for i, issue in enumerate(format_issues[:5]):  # Top 5 issues
            fix_html = self._get_format_fix(issue)
            if fix_html:
                fixes.append(fix_html)

        return {
            'id': 'format-fixes',
            'type': 'formatting',
            'severity': 'medium',
            'title': 'Fix Formatting Issues',
            'description': f'{len(format_issues)} formatting issues detected that may cause ATS parsing errors',
            'template': f"""<div class="space-y-4">
<h3 class="text-lg font-semibold text-gray-900">Formatting Fixes Needed</h3>
<div class="space-y-3">
{''.join(fixes)}
</div>

<div class="mt-4 p-4 bg-blue-50 border border-blue-200 rounded">
<h4 class="text-md font-semibold text-gray-900 mb-2">ATS-Friendly Formatting Checklist:</h4>
<ul class="text-sm text-gray-700 space-y-1">
<li>✓ Use standard section headers (Experience, Education, Skills)</li>
<li>✓ Use simple bullet points (•, -, or *)</li>
<li>✓ Avoid tables, text boxes, and columns</li>
<li>✓ Use standard fonts (Arial, Calibri, Times New Roman)</li>
<li>✓ Save as .docx or simple PDF</li>
<li>✓ No headers/footers with important info</li>
<li>✓ Consistent date format (MM/YYYY)</li>
</ul>
</div>
</div>""",
            'quickFix': {
                'before': 'Multiple formatting issues',
                'after': 'Apply ATS-friendly formatting',
                'action': 'format'
            }
        }

    def _get_format_fix(self, issue: str) -> str:
        """Get specific fix instruction for a format issue."""

        issue_lower = issue.lower()

        if 'date' in issue_lower:
            return """<div class="border-b border-gray-200 pb-2 mb-2">
<div class="text-sm font-semibold text-gray-800">Date Format</div>
<div class="text-xs text-gray-600 mt-1">
<span class="text-red-600">❌ Avoid:</span> "Jan 2020", "1/2020", "2020-01"<br/>
<span class="text-green-600">✅ Use:</span> "January 2020", "01/2020", "2020 - 2023"
</div>
</div>"""

        if 'bullet' in issue_lower or 'list' in issue_lower:
            return """<div class="border-b border-gray-200 pb-2 mb-2">
<div class="text-sm font-semibold text-gray-800">Bullet Points</div>
<div class="text-xs text-gray-600 mt-1">
<span class="text-red-600">❌ Avoid:</span> ▪, ►, ✓, custom symbols<br/>
<span class="text-green-600">✅ Use:</span> • (bullet), - (hyphen), or * (asterisk)
</div>
</div>"""

        if 'font' in issue_lower:
            return """<div class="border-b border-gray-200 pb-2 mb-2">
<div class="text-sm font-semibold text-gray-800">Font Choice</div>
<div class="text-xs text-gray-600 mt-1">
<span class="text-red-600">❌ Avoid:</span> Fancy fonts, script fonts, decorative fonts<br/>
<span class="text-green-600">✅ Use:</span> Arial, Calibri, Times New Roman, Georgia (10-12pt)
</div>
</div>"""

        return f'<div class="text-sm text-gray-700">{issue}</div>'

    def _detect_missing_sections(self, resume_data: ResumeData) -> List[str]:
        """Detect which key sections are missing from resume."""

        missing = []

        # Check for professional summary/objective
        has_summary = False
        # Check if summary field exists and is not empty
        if hasattr(resume_data, 'summary') and resume_data.summary:
            has_summary = True
        # Also check contact for backward compatibility
        elif resume_data.contact and resume_data.contact.get('summary'):
            has_summary = True
        if not has_summary:
            missing.append('summary')

        # Check for skills section
        if not resume_data.skills or len(resume_data.skills) < 3:
            missing.append('skills')

        # Check for experience
        if not resume_data.experience or len(resume_data.experience) == 0:
            missing.append('experience')

        # Check for education
        if not resume_data.education or len(resume_data.education) == 0:
            missing.append('education')

        # Check for projects (recommended for tech roles)
        if self.role in ['software_engineer', 'data_scientist', 'devops_engineer', 'qa_engineer']:
            # Projects would be in metadata or certifications
            has_projects = False
            if resume_data.certifications and len(resume_data.certifications) > 0:
                has_projects = any('project' in str(cert).lower() for cert in resume_data.certifications)
            if not has_projects:
                missing.append('projects')

        return missing

    def _missing_section_template(self, section: str) -> Dict:
        """Generate template for a missing section."""

        templates = {
            'skills': {
                'title': 'Add Skills Section',
                'description': 'Skills section is missing - this is crucial for ATS keyword matching',
                'template': self._get_skills_template(),
                'severity': 'high'
            },
            'experience': {
                'title': 'Add Experience Section',
                'description': 'Work experience section is missing - this is essential for any resume',
                'template': self._get_experience_template(),
                'severity': 'critical'
            },
            'education': {
                'title': 'Add Education Section',
                'description': 'Education section is missing - many roles require this information',
                'template': self._get_education_template(),
                'severity': 'high'
            },
            'projects': {
                'title': 'Add Projects Section',
                'description': 'Projects section recommended for technical roles to showcase hands-on experience',
                'template': self._get_projects_template(),
                'severity': 'medium'
            }
        }

        section_data = templates.get(section, {})

        return {
            'id': f'missing-{section}',
            'type': 'missing_content',
            'severity': section_data.get('severity', 'medium'),
            'title': section_data.get('title', f'Add {section.title()} Section'),
            'description': section_data.get('description', f'{section.title()} section is missing'),
            'template': section_data.get('template', f'<p>Add a {section} section to your resume</p>'),
            'quickFix': {
                'before': f'[No {section} section]',
                'after': f'{section.title()} section added',
                'action': 'insert'
            }
        }

    def _get_skills_template(self) -> str:
        """Get skills section template."""

        role_name = self.role.replace('_', ' ').title()

        # Get typical keywords from role data
        typical_keywords = self.role_data.get('typical_keywords', []) if self.role_data else []
        keywords_sample = ', '.join(typical_keywords[:10]) if typical_keywords else 'List your skills here'

        return f"""<div class="space-y-4">
<h3 class="text-lg font-semibold text-gray-900">Skills Section Template</h3>
<div class="bg-blue-50 border-l-4 border-blue-500 p-4 rounded">
<h4 class="font-semibold mb-2">Technical Skills (or Core Competencies)</h4>
<div class="space-y-2 text-sm">
<p>• <strong>Category 1:</strong> Skill1, Skill2, Skill3, Skill4</p>
<p>• <strong>Category 2:</strong> Skill1, Skill2, Skill3, Skill4</p>
<p>• <strong>Category 3:</strong> Skill1, Skill2, Skill3</p>
</div>
</div>

<div class="mt-4">
<h4 class="text-md font-semibold text-gray-900">Example for {role_name}:</h4>
<div class="bg-green-50 border-l-4 border-green-500 p-4 rounded text-sm">
<p><strong>Technical Skills</strong></p>
<p>• <strong>Sample keywords:</strong> {keywords_sample}</p>
<p class="mt-2 text-xs text-gray-600">Organize these into relevant categories for your role</p>
</div>
</div>

<div class="mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded">
<p class="text-sm"><strong>Placement:</strong> Add this section after your Experience or near the top if you're entry-level</p>
</div>
</div>"""

    def _get_experience_template(self) -> str:
        """Get experience section template."""

        return """<div class="space-y-4">
<h3 class="text-lg font-semibold text-gray-900">Experience Section Template</h3>
<div class="bg-blue-50 border-l-4 border-blue-500 p-4 rounded text-sm">
<p><strong>Job Title</strong> | Company Name | Location</p>
<p class="text-xs text-gray-600">Month YYYY - Present (or Month YYYY)</p>
<ul class="mt-2 space-y-1 ml-4">
<li>• [Action verb] [what you did] [technologies used] [quantifiable result]</li>
<li>• [Action verb] [what you did] [technologies used] [quantifiable result]</li>
<li>• [Action verb] [what you did] [technologies used] [quantifiable result]</li>
</ul>
</div>

<div class="mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded">
<p class="text-sm"><strong>Pro Tip:</strong> List experiences in reverse chronological order (most recent first). Include 3-5 bullet points per role.</p>
</div>
</div>"""

    def _get_education_template(self) -> str:
        """Get education section template."""

        return """<div class="space-y-4">
<h3 class="text-lg font-semibold text-gray-900">Education Section Template</h3>
<div class="bg-blue-50 border-l-4 border-blue-500 p-4 rounded text-sm">
<p><strong>Degree Name</strong> in [Major/Field]</p>
<p class="text-gray-700">Institution Name | Location</p>
<p class="text-xs text-gray-600">Graduation Month YYYY (or Expected Month YYYY)</p>
<p class="mt-2 text-xs">• GPA: X.XX/4.0 (if above 3.5)</p>
<p class="text-xs">• Relevant Coursework: Course1, Course2, Course3</p>
<p class="text-xs">• Honors: Dean's List, Scholarships, Awards</p>
</div>

<div class="mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded">
<p class="text-sm"><strong>Placement:</strong> Place after Experience (or before if you're a recent graduate)</p>
</div>
</div>"""

    def _get_projects_template(self) -> str:
        """Get projects section template."""

        return """<div class="space-y-4">
<h3 class="text-lg font-semibold text-gray-900">Projects Section Template</h3>
<div class="bg-blue-50 border-l-4 border-blue-500 p-4 rounded text-sm">
<p><strong>Project Name</strong> | [Technologies Used] | [GitHub/Live Link]</p>
<ul class="mt-2 space-y-1 ml-4">
<li>• Brief description of what the project does and its purpose</li>
<li>• Key technologies and frameworks used</li>
<li>• Impact: users, performance metrics, or learning outcomes</li>
</ul>
</div>

<div class="mt-4 p-3 bg-green-50 border border-green-200 rounded text-sm">
<p><strong>Example:</strong></p>
<p class="mt-1"><strong>E-commerce Platform</strong> | React, Node.js, MongoDB | github.com/user/project</p>
<ul class="mt-1 space-y-1 ml-4 text-xs">
<li>• Built full-stack e-commerce application with user authentication and payment processing</li>
<li>• Implemented responsive UI using React and Material-UI, achieving 95+ Lighthouse score</li>
<li>• Designed RESTful API with Node.js and Express, handling 1000+ concurrent users</li>
</ul>
</div>

<div class="mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded">
<p class="text-sm"><strong>Pro Tip:</strong> Include 2-4 relevant projects. Great for showcasing skills not demonstrated in work experience.</p>
</div>
</div>"""

    def _get_role_examples(self) -> Dict[str, str]:
        """Get role-specific examples for different sections."""

        role_examples = {
            'software_engineer': {
                'summary': 'Results-driven Software Engineer with 5+ years of experience in full-stack development. '
                          'Proven track record in building scalable web applications using Python, React, and AWS, '
                          'serving 100K+ daily users. Led 3 cross-functional teams delivering projects 20% ahead of schedule. '
                          'Seeking to leverage technical expertise and leadership skills in a Senior Engineer role.'
            },
            'data_scientist': {
                'summary': 'Data Scientist with 4+ years of experience in predictive modeling and machine learning. '
                          'Developed ML models that increased revenue by $2M+ annually. Expert in Python, TensorFlow, and SQL. '
                          'Passionate about transforming complex data into actionable business insights. '
                          'Seeking to drive data strategy in a forward-thinking organization.'
            },
            'product_manager': {
                'summary': 'Product Manager with 6+ years of experience leading B2B SaaS products from concept to launch. '
                          'Managed products generating $10M+ ARR with 95% customer retention. Skilled in roadmap prioritization, '
                          'stakeholder management, and data-driven decision making. '
                          'Seeking to shape product vision and strategy in a growth-stage company.'
            },
            'devops_engineer': {
                'summary': 'DevOps Engineer with 5+ years of experience in cloud infrastructure and automation. '
                          'Architected CI/CD pipelines reducing deployment time by 60% and improving system reliability to 99.9%. '
                          'Expert in Kubernetes, Terraform, and AWS. '
                          'Seeking to drive infrastructure excellence and engineering efficiency.'
            }
        }

        return role_examples.get(self.role, {
            'summary': 'Professional with proven experience and strong skills. '
                      'Track record of delivering results and driving impact. '
                      'Seeking to contribute expertise in target role.'
        })


class SuggestionGenerator:
    """
    Generates actionable suggestions mapped to document locations for editor UX.

    This class creates suggestions with 4 action types:
    1. missing_content - Quick add with modal (phone, email, linkedin)
    2. content_change - Navigate & highlight OR replace text (weak verbs, grammar)
    3. missing_section - Template insert (Projects, Skills)
    4. formatting - Navigate only (date formats, bullet styles)

    Each suggestion includes location mapping to paragraph indices for navigation.
    """

    # Weak action verbs to detect
    WEAK_VERBS = [
        'responsible for', 'worked on', 'helped with', 'assisted with',
        'involved in', 'participated in', 'handled', 'dealt with'
    ]

    # Strong replacement verbs by category
    STRONG_VERBS = {
        'leadership': ['Led', 'Managed', 'Directed', 'Coordinated', 'Supervised', 'Guided'],
        'achievement': ['Achieved', 'Delivered', 'Exceeded', 'Accelerated', 'Improved', 'Increased'],
        'technical': ['Developed', 'Architected', 'Implemented', 'Optimized', 'Automated', 'Engineered'],
        'collaboration': ['Collaborated', 'Partnered', 'Facilitated', 'Consulted', 'Engaged']
    }

    # Tech roles that should have Projects section
    TECH_ROLES = ['software_engineer', 'data_scientist', 'devops_engineer', 'qa_engineer', 'frontend_developer', 'backend_developer']

    def __init__(self, role: str, level: str):
        """
        Initialize suggestion generator.

        Args:
            role: Role ID (e.g., "software_engineer")
            level: Experience level (e.g., "mid", "senior")
        """
        self.role = role
        self.level = level

    def generate_suggestions(
        self,
        resume_data: Dict,
        sections: List[Dict]
    ) -> List[Dict]:
        """
        Generate actionable suggestions with document locations.

        Args:
            resume_data: Parsed resume data with contact, experience, skills, education
            sections: Section mappings from section_detector with start_para/end_para

        Returns:
            List of suggestion dictionaries sorted by priority (critical > high > medium > low)
        """
        suggestions = []

        # Create section lookup for easy access
        section_map = {s['name']: s for s in sections}

        # 1. Missing content suggestions (critical/high priority)
        suggestions.extend(self._detect_missing_contact(resume_data, section_map))

        # 2. Content change suggestions (medium priority)
        suggestions.extend(self._detect_weak_action_verbs(resume_data, section_map))

        # 3. Missing section suggestions (high/medium priority)
        suggestions.extend(self._detect_missing_sections(resume_data, section_map))

        # 4. Formatting suggestions (low priority)
        suggestions.extend(self._detect_formatting_issues(resume_data, section_map))

        # Sort by priority
        suggestions = self._sort_by_priority(suggestions)

        return suggestions

    def _detect_missing_contact(
        self,
        resume_data: Dict,
        section_map: Dict
    ) -> List[Dict]:
        """Detect missing contact information (phone, linkedin)."""
        suggestions = []
        contact = resume_data.get('contact', {})
        contact_section = section_map.get('Contact', {})

        # Missing phone number
        if not contact.get('phone'):
            suggestions.append({
                'id': 'missing-phone',
                'type': 'missing_content',
                'severity': 'critical',
                'title': 'Missing phone number',
                'description': 'ATS systems expect phone number in contact information',
                'location': {
                    'section': 'Contact',
                    'line': None
                },
                'action': 'add_phone',
                'example': '(555) 123-4567'
            })

        # Missing LinkedIn
        if not contact.get('linkedin'):
            suggestions.append({
                'id': 'missing-linkedin',
                'type': 'missing_content',
                'severity': 'high',
                'title': 'Missing LinkedIn profile',
                'description': 'LinkedIn profile increases ATS score and recruiter confidence',
                'location': {
                    'section': 'Contact',
                    'line': None
                },
                'action': 'add_linkedin',
                'example': 'linkedin.com/in/yourprofile'
            })

        return suggestions

    def _detect_weak_action_verbs(
        self,
        resume_data: Dict,
        section_map: Dict
    ) -> List[Dict]:
        """Detect weak action verbs in experience descriptions."""
        suggestions = []
        experience = resume_data.get('experience', [])
        experience_section = section_map.get('Experience', {})

        for exp in experience:
            description = exp.get('description', '')
            para_idx = exp.get('para_idx')

            # Check for weak verbs
            for weak_verb in self.WEAK_VERBS:
                if weak_verb.lower() in description.lower():
                    # Find appropriate strong replacement
                    strong_verb = self._get_strong_verb_replacement(weak_verb)

                    # Create improved version
                    improved_text = description.replace(
                        weak_verb.title(),
                        strong_verb
                    ).replace(
                        weak_verb.lower(),
                        strong_verb.lower()
                    )

                    suggestions.append({
                        'id': f'weak-verb-{para_idx}',
                        'type': 'content_change',
                        'severity': 'medium',
                        'title': 'Weak action verb detected',
                        'description': f'Replace "{weak_verb}" with stronger action verb',
                        'location': {
                            'section': 'Experience',
                            'line': None,
                            'para_idx': para_idx
                        },
                        'current_text': description,
                        'suggested_text': improved_text,
                        'action': 'replace_text'
                    })
                    break  # Only one suggestion per bullet

        return suggestions

    def _get_strong_verb_replacement(self, weak_verb: str) -> str:
        """Get strong verb replacement for weak verb."""
        weak_lower = weak_verb.lower()

        if 'responsible' in weak_lower or 'managed' in weak_lower:
            return 'Led'
        elif 'worked' in weak_lower or 'helped' in weak_lower:
            return 'Developed'
        elif 'assisted' in weak_lower or 'involved' in weak_lower:
            return 'Collaborated with'
        else:
            return 'Achieved'

    def _detect_missing_sections(
        self,
        resume_data: Dict,
        section_map: Dict
    ) -> List[Dict]:
        """Detect missing sections (Skills, Projects, etc.)."""
        suggestions = []

        # Check for missing Skills section
        if 'Skills' not in section_map or not resume_data.get('skills'):
            suggestions.append({
                'id': 'missing-skills',
                'type': 'missing_section',
                'severity': 'high',
                'title': 'Missing Skills section',
                'description': 'Skills section is crucial for ATS keyword matching',
                'location': {
                    'section': 'After Experience',
                    'line': None
                },
                'action': 'add_section',
                'template': 'Technical Skills\n• Category 1: Skill1, Skill2, Skill3\n• Category 2: Skill1, Skill2, Skill3'
            })

        # Check for missing Projects section (tech roles only)
        if self.role in self.TECH_ROLES and 'Projects' not in section_map:
            suggestions.append({
                'id': 'missing-projects',
                'type': 'missing_section',
                'severity': 'medium',
                'title': 'Missing Projects section',
                'description': 'Projects section recommended for technical roles to showcase hands-on experience',
                'location': {
                    'section': 'After Experience',
                    'line': None
                },
                'action': 'add_section',
                'template': 'Projects\n\nProject Name | Technologies Used\n• Brief description of project\n• Key achievements and impact'
            })

        # Check for missing Professional Summary
        has_summary_field = resume_data.get('summary')
        has_summary_section = 'Summary' in section_map
        # Debug logging
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Summary check - has_summary_field: {bool(has_summary_field)}, has_summary_section: {has_summary_section}, summary length: {len(str(has_summary_field)) if has_summary_field else 0}")

        if not has_summary_field and not has_summary_section:
            suggestions.append({
                'id': 'missing-summary',
                'type': 'missing_section',
                'severity': 'high',
                'title': 'Missing Professional Summary',
                'description': 'Professional summary is the first thing recruiters and ATS systems read',
                'location': {
                    'section': 'After Contact',
                    'line': None
                },
                'action': 'add_section',
                'template': f'{self._get_summary_template()}'
            })

        return suggestions

    def _get_summary_template(self) -> str:
        """Get role and level-specific summary template."""
        role_name = self.role.replace('_', ' ').title()

        templates = {
            'entry': f"Entry-level {role_name} with [X months/years] of experience. Strong foundation in [key skills]. Seeking to contribute to [target role].",
            'mid': f"Results-driven {role_name} with [X years] of experience. Proven track record in [key achievements]. Proficient in [tech stack].",
            'senior': f"Senior {role_name} with [X+ years] of experience. Led [teams/projects] delivering [impact]. Expert in [technologies].",
            'lead': f"Accomplished {role_name} leader with [X+ years]. Directed [scale]. Proven expertise in [areas].",
            'executive': f"Visionary {role_name} executive with [X+ years]. Transformed [organizations] achieving [outcomes]."
        }

        return templates.get(self.level, templates['mid'])

    def _detect_formatting_issues(
        self,
        resume_data: Dict,
        section_map: Dict
    ) -> List[Dict]:
        """Detect formatting issues (inconsistent dates, etc.)."""
        suggestions = []
        experience = resume_data.get('experience', [])

        # Check for inconsistent date formats
        date_formats = []
        for exp in experience:
            dates = exp.get('dates', '')
            if dates:
                date_formats.append(dates)

        # Simple check: if dates vary widely in format
        if len(date_formats) > 1:
            has_inconsistent = any('/' in d for d in date_formats) and any('/' not in d for d in date_formats)

            if has_inconsistent:
                suggestions.append({
                    'id': 'inconsistent-dates',
                    'type': 'formatting',
                    'severity': 'low',
                    'title': 'Inconsistent date format',
                    'description': 'Use consistent date format throughout (e.g., "MM/YYYY" or "Month YYYY")',
                    'location': {
                        'section': 'Experience',
                        'line': None
                    },
                    'action': 'navigate'
                })

        return suggestions

    def _sort_by_priority(self, suggestions: List[Dict]) -> List[Dict]:
        """Sort suggestions by severity (critical > high > medium > low)."""
        severity_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}

        return sorted(
            suggestions,
            key=lambda s: severity_order.get(s['severity'], 4)
        )
