"""
Updated role keywords based on analysis of 371 real PM resumes from resume corpus.

Analysis findings:
- Top keywords in actual PM resumes: UI (97%), AI (95%), ML (80%), data (75%),
  process (66%), agile (61%), technical (59%), testing (58%)
- Our old keywords were too theoretical: "product strategy" (6%), "product vision" (9%)
- Modern PM resumes focus on: technical delivery, data/analytics, automation, APIs

New keyword strategy:
- P1.1 Required: High-frequency practical keywords (40%+ in corpus)
- P1.2 Preferred: Medium-frequency specialized keywords (20-40% in corpus)
"""

from typing import Dict, List

# Role keyword database - UPDATED based on real resume corpus analysis
ROLE_KEYWORDS: Dict[str, Dict[str, List[str]]] = {
    # Product Manager - UPDATED from resume corpus analysis
    'product_manager': {
        'required': [
            # Core technical/delivery keywords (40%+ frequency in real PM resumes)
            'product', 'requirements', 'agile', 'scrum', 'stakeholder',
            'data', 'analytics', 'metrics', 'testing', 'technical',
            'platform', 'API', 'integration', 'release', 'engineering',

            # Modern PM skills (high frequency in corpus)
            'UI', 'UX', 'design', 'prototype', 'wireframe',

            # Process & delivery
            'process', 'workflow', 'roadmap', 'backlog', 'sprint',
            'launch', 'deployment', 'iteration'
        ],
        'preferred': [
            # Advanced/specialized technical (20-40% frequency)
            'AI', 'ML', 'machine learning', 'automation', 'cloud',
            'SaaS', 'digital', 'transformation', 'innovation',

            # Analytics & growth
            'SQL', 'dashboard', 'KPI', 'ROI', 'revenue',
            'growth', 'conversion', 'funnel', 'engagement', 'retention',

            # Tools & methods
            'Jira', 'optimization', 'A/B testing', 'MVP',
            'product-market fit', 'go-to-market', 'PRD',

            # Leadership
            'cross-functional', 'user research', 'customer feedback',
            'prioritization', 'strategy', 'vision'
        ]
    },

    # Software Engineer - Keep existing with minor updates
    'software_engineer': {
        'required': [
            'programming', 'software development', 'code', 'API', 'database',
            'testing', 'debugging', 'git', 'version control', 'algorithms',
            'data structures', 'system design', 'architecture', 'scalability',
            'performance', 'CI/CD', 'deployment', 'problem-solving'
        ],
        'preferred': [
            'Python', 'Java', 'JavaScript', 'TypeScript', 'React', 'Node.js',
            'AWS', 'cloud', 'Docker', 'Kubernetes', 'microservices',
            'SQL', 'NoSQL', 'Redis', 'REST', 'GraphQL', 'agile'
        ]
    },

    # Data Scientist - Keep existing
    'data_scientist': {
        'required': [
            'machine learning', 'statistics', 'data analysis', 'modeling',
            'Python', 'SQL', 'data visualization', 'hypothesis testing',
            'regression', 'classification', 'predictive modeling', 'feature engineering',
            'A/B testing', 'experimentation', 'metrics', 'insights'
        ],
        'preferred': [
            'deep learning', 'neural networks', 'NLP', 'computer vision',
            'TensorFlow', 'PyTorch', 'scikit-learn', 'pandas', 'numpy',
            'Spark', 'big data', 'cloud', 'AWS', 'data pipeline',
            'Tableau', 'R', 'Jupyter'
        ]
    },

    # Product Designer / UX Designer - Keep existing
    'product_designer': {
        'required': [
            'user experience', 'UX', 'user interface', 'UI', 'design',
            'wireframes', 'prototypes', 'user research', 'usability testing',
            'information architecture', 'interaction design', 'visual design',
            'user flows', 'design systems', 'accessibility', 'responsive design'
        ],
        'preferred': [
            'Figma', 'Sketch', 'Adobe XD', 'InVision', 'design tokens',
            'user personas', 'journey mapping', 'design thinking', 'A/B testing',
            'analytics', 'Framer', 'HTML', 'CSS', 'front-end', 'agile'
        ]
    },

    # Marketing Manager - Keep existing
    'marketing_manager': {
        'required': [
            'marketing strategy', 'campaign', 'brand', 'market research',
            'customer acquisition', 'lead generation', 'conversion',
            'analytics', 'metrics', 'ROI', 'digital marketing',
            'content marketing', 'social media', 'SEO', 'SEM', 'email marketing'
        ],
        'preferred': [
            'Google Analytics', 'Google Ads', 'Facebook Ads', 'marketing automation',
            'HubSpot', 'Salesforce', 'CRM', 'A/B testing', 'growth hacking',
            'influencer marketing', 'PR', 'copywriting', 'brand strategy'
        ]
    },

    # Sales Manager - Keep existing
    'sales_manager': {
        'required': [
            'sales', 'revenue', 'quota', 'pipeline', 'lead generation',
            'prospecting', 'cold calling', 'closing', 'negotiation',
            'CRM', 'customer relationship', 'account management',
            'sales strategy', 'forecasting', 'team leadership', 'coaching'
        ],
        'preferred': [
            'Salesforce', 'B2B', 'B2C', 'SaaS', 'enterprise sales',
            'solution selling', 'consultative selling', 'value proposition',
            'ROI', 'sales enablement', 'territory management', 'key accounts'
        ]
    },

    # Business Analyst - Keep existing
    'business_analyst': {
        'required': [
            'requirements gathering', 'business analysis', 'stakeholder management',
            'process improvement', 'workflow', 'documentation', 'use cases',
            'data analysis', 'SQL', 'reporting', 'metrics', 'KPIs',
            'business process', 'gap analysis', 'user stories'
        ],
        'preferred': [
            'Jira', 'Confluence', 'agile', 'scrum', 'Tableau', 'Power BI',
            'Excel', 'data visualization', 'process mapping', 'Visio',
            'business intelligence', 'ETL', 'data modeling'
        ]
    },

    # DevOps Engineer - Keep existing
    'devops_engineer': {
        'required': [
            'CI/CD', 'automation', 'deployment', 'infrastructure', 'cloud',
            'monitoring', 'logging', 'container', 'orchestration',
            'configuration management', 'scripting', 'reliability',
            'scalability', 'security', 'version control', 'git'
        ],
        'preferred': [
            'Docker', 'Kubernetes', 'Jenkins', 'GitLab CI', 'AWS', 'Azure',
            'Terraform', 'Ansible', 'Chef', 'Puppet', 'Python', 'Bash',
            'Prometheus', 'Grafana', 'ELK', 'Linux', 'networking'
        ]
    },

    # QA Engineer / Test Engineer - Keep existing
    'qa_engineer': {
        'required': [
            'testing', 'quality assurance', 'test cases', 'test automation',
            'bug tracking', 'regression testing', 'integration testing',
            'functional testing', 'test planning', 'defect management',
            'test coverage', 'quality metrics', 'documentation'
        ],
        'preferred': [
            'Selenium', 'Cypress', 'JUnit', 'TestNG', 'Jira', 'Postman',
            'API testing', 'performance testing', 'load testing', 'JMeter',
            'Python', 'Java', 'JavaScript', 'CI/CD', 'agile', 'scrum'
        ]
    },

    # Project Manager - Keep existing
    'project_manager': {
        'required': [
            'project management', 'planning', 'scheduling', 'resource allocation',
            'risk management', 'stakeholder management', 'budget', 'timeline',
            'milestones', 'deliverables', 'agile', 'scrum', 'waterfall',
            'communication', 'coordination', 'reporting', 'documentation'
        ],
        'preferred': [
            'PMP', 'PMI', 'Jira', 'MS Project', 'Asana', 'Monday.com',
            'gantt chart', 'critical path', 'change management',
            'vendor management', 'contract management', 'Confluence'
        ]
    }
}

# Aliases for common role name variations (keep existing)
ROLE_ALIASES = {
    'pm': 'product_manager',
    'product': 'product_manager',
    'swe': 'software_engineer',
    'engineer': 'software_engineer',
    'developer': 'software_engineer',
    'data_scientist': 'data_scientist',
    'ds': 'data_scientist',
    'ml_engineer': 'data_scientist',
    'designer': 'product_designer',
    'ux': 'product_designer',
    'ui': 'product_designer',
    'marketing': 'marketing_manager',
    'sales': 'sales_manager',
    'analyst': 'business_analyst',
    'ba': 'business_analyst',
    'devops': 'devops_engineer',
    'sre': 'devops_engineer',
    'qa': 'qa_engineer',
    'qe': 'qa_engineer',
    'tester': 'qa_engineer',
    'project_manager': 'project_manager',
    'pm_traditional': 'project_manager'
}


def get_role_keywords(role: str) -> Dict[str, List[str]]:
    """
    Get default keywords for a specific role.

    Args:
        role: Role identifier (e.g., 'product_manager', 'software_engineer')
              Supports aliases (e.g., 'pm', 'swe', 'engineer')

    Returns:
        Dictionary with 'required' and 'preferred' keyword lists.
        If role not found, returns generic software keywords.

    Example:
        >>> keywords = get_role_keywords('product_manager')
        >>> keywords['required'][:3]
        ['product', 'requirements', 'agile']
    """
    # Normalize role name
    role_normalized = role.lower().replace(' ', '_').replace('-', '_')

    # Check aliases first
    if role_normalized in ROLE_ALIASES:
        role_normalized = ROLE_ALIASES[role_normalized]

    # Return role keywords or default to software engineer
    return ROLE_KEYWORDS.get(role_normalized, ROLE_KEYWORDS['software_engineer'])


def get_all_roles() -> List[str]:
    """
    Get list of all supported roles.

    Returns:
        List of role identifiers
    """
    return list(ROLE_KEYWORDS.keys())


# Print summary for verification
if __name__ == "__main__":
    pm_keywords = get_role_keywords('product_manager')
    print("="*80)
    print("UPDATED PRODUCT MANAGER KEYWORDS")
    print("="*80)
    print(f"\nP1.1 Required ({len(pm_keywords['required'])} keywords):")
    for i, kw in enumerate(pm_keywords['required'], 1):
        print(f"  {i:2d}. {kw}")

    print(f"\nP1.2 Preferred ({len(pm_keywords['preferred'])} keywords):")
    for i, kw in enumerate(pm_keywords['preferred'], 1):
        print(f"  {i:2d}. {kw}")

    print(f"\nTotal: {len(pm_keywords['required']) + len(pm_keywords['preferred'])} keywords")
    print("\nKey improvements:")
    print("  - Added: AI, ML, automation, API, platform, engineering, UI, UX")
    print("  - Added: process, workflow, testing, technical, integration, release")
    print("  - Added: digital, cloud, SaaS, dashboard, SQL")
    print("  - Kept high-value keywords: agile, scrum, stakeholder, requirements")
    print("  - Moved low-frequency to preferred: product strategy, product vision")
