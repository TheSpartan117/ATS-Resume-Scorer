"""
Role-specific keywords for ATS scoring - FIXED VERSION.

Non-tech roles: Manually curated based on industry standards and real job descriptions
Tech roles: Refined from corpus analysis with relevance filtering

Keywords categorized as:
- Required: Core essential skills (target 10-15 keywords)
- Preferred: Advanced/specialized skills (target 15-25 keywords)
"""

ROLE_KEYWORDS = {
    # ===== FINANCE & ACCOUNTING =====
    'accountant': {
        'required': [
            'accounting', 'gaap', 'financial reporting', 'reconciliation',
            'general ledger', 'accounts payable', 'accounts receivable',
            'journal entries', 'month-end close', 'excel'
        ],
        'preferred': [
            'quickbooks', 'sap', 'erp', 'audit', 'tax', 'financial statements',
            'variance analysis', 'budgeting', 'forecasting', 'sox compliance',
            'cost accounting', 'ifrs', 'balance sheet', 'income statement',
            'fixed assets', 'accruals'
        ]
    },
    'financial_analyst': {
        'required': [
            'financial analysis', 'financial modeling', 'excel', 'forecasting',
            'budgeting', 'financial reporting', 'data analysis', 'valuation'
        ],
        'preferred': [
            'fp&a', 'variance analysis', 'dcf', 'sql', 'tableau', 'power bi',
            'kpi tracking', 'financial planning', 'strategic planning',
            'investment analysis', 'bloomberg', 'capital iq', 'powerpoint',
            'financial statements', 'roi analysis', 'business intelligence'
        ]
    },

    # ===== HR & LEGAL =====
    'hr_manager': {
        'required': [
            'human resources', 'recruitment', 'employee relations', 'talent management',
            'performance management', 'hris', 'hr policy', 'compensation'
        ],
        'preferred': [
            'workday', 'successfactors', 'adp', 'benefits administration',
            'onboarding', 'talent acquisition', 'employee engagement',
            'organizational development', 'change management', 'hr compliance',
            'training', 'workforce planning', 'hr strategy', 'labor relations',
            'diversity', 'inclusion', 'retention'
        ]
    },
    'recruiter': {
        'required': [
            'recruiting', 'talent acquisition', 'sourcing', 'screening',
            'interviewing', 'applicant tracking', 'ats', 'linkedin'
        ],
        'preferred': [
            'boolean search', 'candidate experience', 'employer branding',
            'recruitment marketing', 'pipeline management', 'greenhouse', 'lever',
            'workday recruiting', 'diversity hiring', 'negotiation', 'onboarding',
            'social recruiting', 'job posting', 'sourcing strategies',
            'talent pool', 'recruitment metrics'
        ]
    },
    'corporate_lawyer': {
        'required': [
            'legal', 'contracts', 'compliance', 'corporate law', 'litigation',
            'legal counsel', 'due diligence', 'legal research'
        ],
        'preferred': [
            'mergers', 'acquisitions', 'corporate governance', 'securities law',
            'intellectual property', 'employment law', 'regulatory compliance',
            'contract negotiation', 'westlaw', 'lexisnexis', 'legal analysis',
            'risk management', 'commercial law', 'corporate transactions'
        ]
    },

    # ===== SALES & MARKETING =====
    'sales_manager': {
        'required': [
            'sales', 'revenue', 'quota', 'pipeline', 'crm', 'salesforce',
            'account management', 'forecasting', 'business development'
        ],
        'preferred': [
            'sales strategy', 'territory management', 'negotiation', 'closing',
            'sales operations', 'sales enablement', 'hubspot', 'coaching',
            'sales leadership', 'performance metrics', 'lead generation',
            'b2b sales', 'enterprise sales', 'channel sales', 'sales training'
        ]
    },
    'marketing_manager': {
        'required': [
            'marketing', 'digital marketing', 'campaigns', 'content marketing',
            'seo', 'social media', 'google analytics', 'marketing strategy'
        ],
        'preferred': [
            'sem', 'email marketing', 'marketing automation', 'hubspot', 'marketo',
            'brand management', 'lead generation', 'roi', 'campaign management',
            'analytics', 'budget management', 'creative direction', 'copywriting',
            'marketing operations', 'cms', 'paid advertising', 'conversion optimization'
        ]
    },

    # ===== OPERATIONS & CUSTOMER SUCCESS =====
    'operations_manager': {
        'required': [
            'operations', 'process improvement', 'project management', 'team management',
            'operations strategy', 'efficiency', 'productivity', 'kpi tracking'
        ],
        'preferred': [
            'supply chain', 'logistics', 'inventory', 'lean', 'six sigma',
            'continuous improvement', 'process optimization', 'vendor management',
            'quality control', 'erp', 'process mapping', 'cost reduction',
            'capacity planning', 'workflow optimization'
        ]
    },
    'customer_success_manager': {
        'required': [
            'customer success', 'customer retention', 'account management',
            'customer satisfaction', 'onboarding', 'crm', 'renewals'
        ],
        'preferred': [
            'churn reduction', 'upselling', 'customer advocacy', 'gainsight',
            'customer engagement', 'product adoption', 'escalation management',
            'customer feedback', 'metrics tracking', 'relationship management',
            'customer health', 'expansion revenue', 'zendesk', 'customer journey'
        ]
    },

    # ===== CONTENT & DESIGN =====
    'content_writer': {
        'required': [
            'content writing', 'copywriting', 'content strategy', 'seo',
            'editing', 'research', 'cms', 'blogging'
        ],
        'preferred': [
            'content marketing', 'wordpress', 'seo writing', 'storytelling',
            'proofreading', 'social media content', 'content planning',
            'tone of voice', 'audience targeting', 'grammarly', 'style guide',
            'content calendar', 'keyword research', 'editorial', 'articles'
        ]
    },
    'product_designer': {
        'required': [
            'product design', 'ux', 'ui', 'figma', 'user research',
            'wireframing', 'prototyping', 'design systems', 'user testing'
        ],
        'preferred': [
            'sketch', 'adobe xd', 'invision', 'user flows', 'design thinking',
            'interaction design', 'visual design', 'usability testing', 'personas',
            'journey mapping', 'a/b testing', 'accessibility', 'responsive design',
            'design sprint', 'collaboration', 'agile'
        ]
    },
    'ui_designer': {
        'required': [
            'ui design', 'user interface', 'figma', 'visual design',
            'design systems', 'prototyping', 'html', 'css'
        ],
        'preferred': [
            'sketch', 'adobe xd', 'responsive design', 'mobile design',
            'web design', 'typography', 'color theory', 'layout design',
            'interaction design', 'javascript', 'react', 'animation',
            'design tokens', 'accessibility', 'usability', 'wireframing'
        ]
    },
    'ux_designer': {
        'required': [
            'ux design', 'user experience', 'user research', 'figma',
            'wireframing', 'prototyping', 'usability testing', 'user flows'
        ],
        'preferred': [
            'sketch', 'adobe xd', 'personas', 'journey mapping', 'information architecture',
            'interaction design', 'design thinking', 'a/b testing', 'user interviews',
            'heuristic evaluation', 'card sorting', 'design sprint', 'accessibility',
            'quantitative research', 'qualitative research', 'analytics'
        ]
    },

    # ===== TECH ROLES (Refined from corpus) =====
    'software_engineer': {
        'required': [
            'programming', 'software development', 'coding', 'algorithms',
            'data structures', 'git', 'api', 'testing', 'debugging', 'code review'
        ],
        'preferred': [
            'python', 'java', 'javascript', 'c++', 'typescript', 'react', 'node',
            'sql', 'docker', 'kubernetes', 'aws', 'microservices', 'rest', 'agile',
            'ci/cd', 'linux', 'cloud', 'nosql', 'graphql', 'redis'
        ]
    },
    'data_scientist': {
        'required': [
            'machine learning', 'python', 'data analysis', 'statistics',
            'sql', 'data visualization', 'modeling', 'analytics'
        ],
        'preferred': [
            'deep learning', 'nlp', 'tensorflow', 'pytorch', 'scikit-learn',
            'pandas', 'numpy', 'jupyter', 'tableau', 'r', 'big data',
            'spark', 'hadoop', 'feature engineering', 'a/b testing',
            'predictive modeling', 'neural networks', 'computer vision'
        ]
    },
    'data_engineer': {
        'required': [
            'data engineering', 'etl', 'sql', 'python', 'data pipeline',
            'data warehousing', 'database', 'big data'
        ],
        'preferred': [
            'spark', 'airflow', 'kafka', 'aws', 'redshift', 'snowflake',
            'hadoop', 'scala', 'docker', 'kubernetes', 'data modeling',
            'data quality', 'dbt', 'bigquery', 'azure', 'real-time processing',
            'stream processing', 'data architecture'
        ]
    },
    'devops_engineer': {
        'required': [
            'devops', 'ci/cd', 'docker', 'kubernetes', 'aws', 'linux',
            'automation', 'infrastructure'
        ],
        'preferred': [
            'terraform', 'ansible', 'jenkins', 'git', 'monitoring', 'logging',
            'cloud', 'azure', 'gcp', 'python', 'bash', 'helm', 'prometheus',
            'grafana', 'microservices', 'networking', 'security', 'sre'
        ]
    },
    'qa_engineer': {
        'required': [
            'testing', 'qa', 'test automation', 'test cases', 'bug tracking',
            'quality assurance', 'manual testing', 'test planning'
        ],
        'preferred': [
            'selenium', 'automation framework', 'api testing', 'regression testing',
            'integration testing', 'performance testing', 'jira', 'python', 'java',
            'agile', 'test strategy', 'ci/cd', 'postman', 'load testing',
            'security testing', 'mobile testing', 'sql'
        ]
    },
    'business_analyst': {
        'required': [
            'business analysis', 'requirements gathering', 'documentation',
            'stakeholder management', 'sql', 'data analysis', 'agile'
        ],
        'preferred': [
            'user stories', 'process improvement', 'wireframing', 'jira',
            'business intelligence', 'tableau', 'power bi', 'excel',
            'project management', 'workflow design', 'analytics', 'scrum',
            'use cases', 'gap analysis', 'solution design'
        ]
    },

    # ===== PRODUCT & PROJECT MANAGEMENT =====
    'product_manager': {
        'required': [
            'product management', 'product strategy', 'roadmap', 'stakeholder management',
            'user stories', 'agile', 'requirements', 'prioritization'
        ],
        'preferred': [
            'scrum', 'product analytics', 'a/b testing', 'user research',
            'data-driven', 'kpi', 'go-to-market', 'mvp', 'backlog',
            'product vision', 'wireframing', 'jira', 'sql', 'metrics',
            'feature definition', 'cross-functional', 'product lifecycle'
        ]
    },
    'technical_product_manager': {
        'required': [
            'product management', 'technical', 'api', 'architecture',
            'roadmap', 'agile', 'engineering', 'stakeholder management'
        ],
        'preferred': [
            'sql', 'system design', 'microservices', 'cloud', 'data modeling',
            'technical specifications', 'rest', 'integration', 'scalability',
            'platform', 'developer tools', 'sdk', 'technical requirements',
            'backend', 'infrastructure', 'performance'
        ]
    },
    'project_manager': {
        'required': [
            'project management', 'planning', 'scheduling', 'stakeholder management',
            'risk management', 'budget', 'team coordination', 'pmp'
        ],
        'preferred': [
            'agile', 'scrum', 'waterfall', 'jira', 'microsoft project',
            'resource management', 'project planning', 'status reporting',
            'change management', 'quality management', 'vendor management',
            'project charter', 'gantt chart', 'critical path', 'prince2'
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
