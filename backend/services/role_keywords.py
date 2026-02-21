"""
Role-specific keywords for ATS scoring.

Updated from corpus analysis of 29,783 resumes.
Source: https://github.com/florex/resume_corpus

Keywords are categorized as:
- Required: Core keywords (50%+ frequency in role resumes)
- Preferred: Advanced/specialized keywords (20-50% frequency)
"""

ROLE_KEYWORDS = {
    'accountant': {
        # Accountant (411 resumes analyzed)
        'required': [
            'ai', 'ui', 'data', 'team',
            'design', 'product', 'database', 'excel',
            'web', 'ml', 'communication', 'sql',
        ],
        'preferred': [
            'sales',
        ]
    },
    'business_analyst': {
        # Business Analyst (16194 resumes analyzed)
        'required': [
            'ai', 'ui', 'data', 'team',
            'design', 'database', 'sql', 'web',
            'product', 'ml', 'windows', 'java',
            'testing', 'html',
        ],
        'preferred': [
            'ux', 'communication', 'rest', 'javascript',
            'excel', 'git', 'css', 'linux',
            'oracle', 'api', 'mysql', 'sql server',
            'agile', 'analytics', 'cloud', 'unix',
            'python', 'node', 'scrum', 'aws',
            'jira', 'sales', 'angular', 'scala',
        ]
    },
    'content_writer': {
        # Content Writer (89 resumes analyzed)
        'required': [
            'ai', 'ui', 'design', 'data',
            'team', 'web', 'product', 'ml',
            'communication', 'database', 'html',
        ],
        'preferred': [
            'css', 'git', 'java', 'excel',
            'javascript', 'sql', 'marketing', 'testing',
            'analytics', 'sales', 'windows', 'project management',
            'rest', 'agile', 'ux', 'php',
            'seo', 'leadership', 'lean', 'api',
            'stakeholder', 'qa', 'mobile', '.net',
            'strategy', 'python', 'cloud',
        ]
    },
    'corporate_lawyer': {
        # Corporate Lawyer (28 resumes analyzed)
        'required': [
            'ai', 'ui', 'data', 'database',
            'team', 'product', 'design', 'web',
            'excel', 'rest', 'ml', 'testing',
        ],
        'preferred': [
            'communication',
        ]
    },
    'customer_success_manager': {
        # Customer Success Manager (380 resumes analyzed)
        'required': [
            'ai', 'ui', 'team', 'data',
            'product', 'design', 'communication', 'project management',
            'sales', 'web', 'excel',
        ],
        'preferred': [
            'agile', 'scrum', 'ml', 'stakeholder',
            'database', 'leadership', 'sql', 'testing',
            'analytics', 'marketing', 'jira', 'waterfall',
            'ux', 'windows', 'git', 'html',
            'revenue', 'cross-functional', 'rest', 'cloud',
            'scala', 'java', 'api', 'strategy',
            'sprint', 'mobile', 'collaboration',
        ]
    },
    'data_engineer': {
        # Data Engineer (162 resumes analyzed)
        'required': [
            'data', 'ai', 'analytics', 'ui',
            'sql', 'database', 'design', 'team',
            'python', 'web', 'product', 'ml',
            'java', 'mysql', 'api', 'oracle',
            'sql server', 'ux', 'testing', 'rest',
            'html', 'linux', 'git', 'aws',
            'cloud', 'etl', 'windows', 'javascript',
            'agile',
        ],
        'preferred': [
            'spark', 'css', 'excel', 'unix',
            'hadoop', 'communication', 'scala', 'lean',
            'node',
        ]
    },
    'data_scientist': {
        # Data Scientist (175 resumes analyzed)
        'required': [
            'analytics', 'data', 'ai', 'sql',
            'python', 'ui', 'design', 'database',
            'ml', 'web', 'team', 'git',
            'java', 'machine learning', 'api', 'product',
            'rest', 'mysql', 'testing', 'html',
            'aws', 'pandas', 'excel', 'numpy',
            'css', 'ux', 'javascript', 'tableau',
            'spark', 'lean', 'cloud', 'linux',
        ],
        'preferred': [
            'oracle', 'agile', 'hadoop', 'sql server',
            'windows', 'communication',
        ]
    },
    'devops_engineer': {
        # DevOps Engineer (703 resumes analyzed)
        'required': [
            'ai', 'ui', 'data', 'team',
            'web', 'devops', 'design', 'sql',
            'product', 'ux', 'linux', 'database',
            'git', 'windows', 'ml', 'java',
            'cloud', 'testing', 'aws',
        ],
        'preferred': [
            'mysql', 'rest', 'api', 'communication',
            'python', 'agile', 'automation', 'html',
            'jenkins', 'javascript', 'oracle', 'jira',
            'css', 'docker', 'unix', 'sql server',
            'excel', 'scala', 'node',
        ]
    },
    'financial_analyst': {
        # Financial Analyst (98 resumes analyzed)
        'required': [
            'ai', 'ui', 'data', 'team',
            'product', 'design', 'excel', 'database',
            'web', 'ml', 'sql', 'project management',
        ],
        'preferred': [
            'communication',
        ]
    },
    'hr_manager': {
        # HR Manager (126 resumes analyzed)
        'required': [
            'ai', 'ui', 'team', 'data',
            'excel', 'design', 'communication', 'product',
            'database', 'sales', 'web', 'leadership',
        ],
        'preferred': [
            'ml',
        ]
    },
    'marketing_manager': {
        # Marketing Manager (335 resumes analyzed)
        'required': [
            'analytics', 'marketing', 'ai', 'web',
            'ui', 'design', 'git', 'ml',
            'team', 'product', 'html', 'data',
            'seo', 'css', 'sales', 'java',
            'javascript', 'communication',
        ],
        'preferred': [
            'strategy', 'sql', 'database', 'testing',
            'php', 'mobile', 'ux', 'project management',
            'excel', 'rest', 'api', 'leadership',
            'mysql', 'agile', 'windows',
        ]
    },
    'operations_manager': {
        # Operations Manager (330 resumes analyzed)
        'required': [
            'ai', 'ui', 'team', 'data',
            'design', 'product', 'communication', 'windows',
            'project management', 'web', 'excel', 'leadership',
        ],
        'preferred': [
            'sales',
        ]
    },
    'product_designer': {
        # Product Designer (31 resumes analyzed)
        'required': [
            'product', 'design', 'ai', 'web',
            'ml', 'ux', 'ui', 'team',
            'html', 'marketing', 'css', 'mobile',
            'git', 'testing', 'java', 'javascript',
            'data', 'wireframe', 'prototype',
        ],
        'preferred': [
            'sketch', 'agile', 'analytics', 'communication',
            'user research', 'strategy', 'stakeholder', 'github',
            'sql', 'php', 'cloud', 'sales',
            'seo', 'api', 'qa', 'rest',
            'collaboration', 'express',
        ]
    },
    'product_manager': {
        # Product Manager (348 resumes analyzed)
        'required': [
            'product', 'ai', 'ui', 'team',
            'design', 'data', 'web', 'agile',
            'ml', 'analytics', 'communication', 'testing',
            'project management', 'git',
        ],
        'preferred': [
            'sql', 'html', 'java', 'scrum',
            'sales', 'marketing', 'database', 'jira',
            'stakeholder', 'mobile', 'ux', 'css',
            'api', 'javascript', 'excel', 'leadership',
            'strategy', 'rest', 'cloud', 'qa',
            'windows', 'backlog', 'oracle', 'roadmap',
        ]
    },
    'project_manager': {
        # Project Manager (4065 resumes analyzed)
        'required': [
            'ai', 'ui', 'team', 'data',
            'design', 'product', 'project management', 'communication',
            'web', 'excel', 'testing', 'ml',
        ],
        'preferred': [
            'database',
        ]
    },
    'qa_engineer': {
        # QA Engineer (715 resumes analyzed)
        'required': [
            'ai', 'ui', 'data', 'team',
            'design', 'product', 'testing', 'web',
            'sql', 'database', 'ml', 'java',
            'communication', 'html', 'windows',
        ],
        'preferred': [
            'qa', 'excel', 'ux', 'agile',
            'analytics', 'javascript', 'linux', 'rest',
            'css', 'automation', 'api', 'oracle',
            'mysql', 'git', 'scrum', 'python',
            'project management', 'sql server', 'sales', 'jira',
            'unix', 'stakeholder', 'selenium',
        ]
    },
    'recruiter': {
        # Recruiter (94 resumes analyzed)
        'required': [
            'ui', 'ai', 'team', 'data',
            'product', 'excel', 'communication', 'sales',
            'design', 'database', 'web',
        ],
        'preferred': [
            'ml', 'project management', 'sql', 'marketing',
            'rest', 'leadership', 'java', 'analytics',
            'api', 'testing', 'windows', 'powerpoint',
            'html', 'stakeholder', 'agile', 'mobile',
            'lean', 'javascript', 'git', 'revenue',
            'css', 'ux',
        ]
    },
    'sales_manager': {
        # Sales Manager (134 resumes analyzed)
        'required': [
            'ai', 'ui', 'sales', 'team',
            'product', 'data', 'design', 'web',
            'marketing', 'analytics', 'communication', 'excel',
        ],
        'preferred': [
            'ml',
        ]
    },
    'software_engineer': {
        # Software Engineer (7051 resumes analyzed)
        'required': [
            'ai', 'ui', 'java', 'web',
            'sql', 'data', 'design', 'ml',
            'javascript', 'html', 'team', 'database',
            'css', 'git', 'product', 'api',
            'testing', 'rest', 'mysql', 'ux',
            'agile', 'windows',
        ],
        'preferred': [
            'angular', 'oracle', 'linux', 'sql server',
            'communication', 'python', 'node', 'scrum',
            'excel', 'analytics', 'cloud', 'jira',
            'php', 'backend', 'aws', 'c++',
        ]
    },
    'technical_product_manager': {
        # Technical Product Manager (11 resumes analyzed)
        'required': [
            'ai', 'ui', 'product', 'design',
            'team', 'sql', 'data', 'ml',
            'database', 'mobile', 'analytics', 'api',
            'git', 'agile', 'jira', 'testing',
            'communication', 'java', 'html', 'mysql',
            'web', 'windows', 'stakeholder', 'excel',
        ],
        'preferred': [
            'javascript', 'qa', 'cloud', 'oracle',
            'sales', 'strategy', 'css', 'node',
            'sql server', 'ux', 'backlog', 'marketing',
            'leadership', 'scala',
        ]
    },
    'ui_designer': {
        # UI Designer (1184 resumes analyzed)
        'required': [
            'ui', 'design', 'web', 'ai',
            'ml', 'html', 'java', 'javascript',
            'css', 'team', 'git', 'data',
            'ux', 'product', 'sql', 'testing',
            'api', 'database', 'angular', 'agile',
            'rest', 'node', 'react', 'mobile',
            'mysql', 'communication', 'analytics',
        ],
        'preferred': [
            'scrum', 'windows', 'php', 'excel',
            'jira', 'github', 'prototype', 'backend',
            'oracle', 'wireframe', 'marketing',
        ]
    },
    'ux_designer': {
        # UX Designer (679 resumes analyzed)
        'required': [
            'ui', 'design', 'ai', 'web',
            'ml', 'html', 'css', 'java',
            'javascript', 'team', 'ux', 'git',
            'product', 'data', 'analytics', 'testing',
            'sql', 'mobile', 'php',
        ],
        'preferred': [
            'communication', 'api', 'agile', 'marketing',
            'database', 'prototype', 'rest', 'mysql',
            'react', 'wireframe', 'angular', 'node',
            'excel', 'sales', 'windows', '.net',
            'jira', 'seo', 'github',
        ]
    },
}

def get_role_keywords(role_id: str):
    """
    Get keywords for a specific role.

    Args:
        role_id: Role identifier (e.g., 'product_manager')

    Returns:
        Dictionary with 'required' and 'preferred' keyword lists,
        or None if role not found.
    """
    return ROLE_KEYWORDS.get(role_id)

def get_all_roles():
    """Get list of all available role IDs."""
    return list(ROLE_KEYWORDS.keys())
