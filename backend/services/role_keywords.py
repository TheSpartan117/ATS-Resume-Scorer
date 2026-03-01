"""
Role-specific keywords for ATS scoring - EXPANDED VERSION.

Significantly expanded keyword lists for better coverage:
- Required: 15-20 core essential skills
- Preferred: 30-40 advanced/specialized skills

Updated: March 1, 2026
"""

ROLE_KEYWORDS = {
    # ===== FINANCE & ACCOUNTING =====
    'accountant': {
        'required': [
            # Core accounting
            'accounting', 'gaap', 'financial reporting', 'reconciliation',
            'general ledger', 'accounts payable', 'accounts receivable',
            'journal entries', 'month-end close', 'financial statements',
            # Tools & skills
            'excel', 'accounting software', 'bookkeeping', 'ledger',
            'balance sheet', 'income statement'
        ],
        'preferred': [
            # Software
            'quickbooks', 'sap', 'erp', 'oracle financials', 'netsuite',
            'xero', 'sage', 'peachtree', 'microsoft dynamics',
            # Skills
            'audit', 'tax', 'tax preparation', 'variance analysis',
            'budgeting', 'forecasting', 'sox compliance', 'internal controls',
            'cost accounting', 'ifrs', 'fixed assets', 'accruals',
            'prepayments', 'depreciation', 'amortization', 'cash flow',
            'financial analysis', 'ratio analysis', 'account reconciliation',
            'payroll', 'payroll processing', 'accounts management',
            'financial reporting', 'monthly close', 'quarterly close',
            'annual close', 'cpa', 'certified public accountant'
        ]
    },
    'financial_analyst': {
        'required': [
            'financial analysis', 'financial modeling', 'excel', 'forecasting',
            'budgeting', 'financial reporting', 'data analysis', 'valuation',
            'financial planning', 'modeling', 'variance analysis', 'kpi',
            'financial statements', 'reporting', 'analytics'
        ],
        'preferred': [
            # Analysis
            'fp&a', 'financial planning and analysis', 'dcf', 'discounted cash flow',
            'valuation modeling', 'merger modeling', 'lbo', 'leveraged buyout',
            'investment analysis', 'roi analysis', 'sensitivity analysis',
            'scenario analysis', 'what-if analysis', 'business case analysis',
            # Tools
            'sql', 'tableau', 'power bi', 'bloomberg', 'capital iq',
            'factset', 'refinitiv', 'python', 'r', 'vba', 'macros',
            # Skills
            'kpi tracking', 'dashboard', 'metrics', 'strategic planning',
            'financial planning', 'business intelligence', 'powerpoint',
            'presentations', 'board reporting', 'management reporting',
            'cost analysis', 'profitability analysis', 'pricing analysis'
        ]
    },

    # ===== HR & LEGAL =====
    'hr_manager': {
        'required': [
            'human resources', 'hr', 'recruitment', 'employee relations',
            'talent management', 'performance management', 'hris',
            'hr policy', 'compensation', 'benefits', 'hr strategy',
            'talent acquisition', 'onboarding', 'employee engagement',
            'hr compliance'
        ],
        'preferred': [
            # Systems
            'workday', 'successfactors', 'adp', 'bamboohr', 'namely',
            'ultipro', 'peoplesoft', 'oracle hcm', 'sap hr',
            # Skills
            'benefits administration', 'compensation planning', 'salary benchmarking',
            'job evaluation', 'succession planning', 'workforce planning',
            'organizational development', 'organizational design', 'change management',
            'training', 'learning and development', 'l&d', 'training programs',
            'employee development', 'career development', 'performance reviews',
            'performance appraisal', 'talent review', '9-box', 'talent assessment',
            # Legal/compliance
            'labor relations', 'employment law', 'hr law', 'compliance',
            'diversity', 'inclusion', 'dei', 'diversity equity inclusion',
            'retention', 'employee retention', 'engagement surveys',
            'exit interviews', 'terminations', 'disciplinary actions'
        ]
    },
    'recruiter': {
        'required': [
            'recruiting', 'recruitment', 'talent acquisition', 'sourcing',
            'screening', 'interviewing', 'applicant tracking', 'ats',
            'linkedin', 'linkedin recruiter', 'candidate sourcing',
            'candidate screening', 'job posting', 'hiring'
        ],
        'preferred': [
            # Sourcing
            'boolean search', 'x-ray search', 'talent sourcing', 'passive sourcing',
            'active sourcing', 'social recruiting', 'sourcing strategies',
            # Process
            'candidate experience', 'employer branding', 'recruitment marketing',
            'talent branding', 'pipeline management', 'talent pool',
            'candidate relationship management', 'crm',
            # Tools
            'greenhouse', 'lever', 'workday recruiting', 'taleo', 'icims',
            'jobvite', 'smartrecruiters', 'bullhorn', 'indeed', 'glassdoor',
            # Skills
            'diversity hiring', 'inclusive hiring', 'negotiation',
            'offer negotiation', 'salary negotiation', 'onboarding',
            'new hire onboarding', 'recruitment metrics', 'time to hire',
            'cost per hire', 'quality of hire', 'sourcing metrics',
            'interview techniques', 'behavioral interviewing',
            'competency-based interviewing', 'reference checks',
            'background checks'
        ]
    },
    'corporate_lawyer': {
        'required': [
            'legal', 'law', 'attorney', 'counsel', 'contracts',
            'compliance', 'corporate law', 'litigation', 'legal counsel',
            'due diligence', 'legal research', 'legal analysis',
            'contract negotiation', 'contract drafting'
        ],
        'preferred': [
            # Practice areas
            'mergers', 'acquisitions', 'm&a', 'mergers and acquisitions',
            'corporate governance', 'securities law', 'securities',
            'intellectual property', 'ip', 'patents', 'trademarks',
            'employment law', 'labor law', 'regulatory compliance',
            'commercial law', 'corporate transactions', 'finance law',
            'banking law', 'real estate law', 'tax law',
            # Tools & research
            'westlaw', 'lexisnexis', 'legal research platforms',
            'contract management', 'document management',
            # Skills
            'risk management', 'legal risk', 'risk assessment',
            'legal opinions', 'memoranda', 'legal writing',
            'litigation management', 'dispute resolution',
            'arbitration', 'mediation', 'negotiation',
            'corporate filings', 'sec filings', 'regulatory filings',
            'board meetings', 'corporate secretary'
        ]
    },

    # ===== SALES & MARKETING =====
    'sales_manager': {
        'required': [
            'sales', 'sales management', 'revenue', 'quota', 'pipeline',
            'crm', 'salesforce', 'account management', 'forecasting',
            'business development', 'sales strategy', 'team management',
            'sales leadership', 'territory management'
        ],
        'preferred': [
            # Strategy & process
            'sales operations', 'sales enablement', 'sales training',
            'sales coaching', 'sales process', 'sales methodology',
            'consultative selling', 'solution selling', 'value selling',
            'challenger sale', 'spin selling', 'sandler', 'miller heiman',
            # Tools & platforms
            'hubspot', 'hubspot crm', 'zoho crm', 'pipedrive',
            'microsoft dynamics', 'sales navigator', 'outreach',
            'salesloft', 'gong', 'chorus',
            # Skills & metrics
            'negotiation', 'closing', 'deal closing', 'contract negotiation',
            'performance metrics', 'kpi tracking', 'sales kpis',
            'win rate', 'conversion rate', 'sales cycle',
            'lead generation', 'prospecting', 'cold calling',
            'b2b sales', 'b2c sales', 'enterprise sales', 'saas sales',
            'channel sales', 'partner sales', 'inside sales',
            'outside sales', 'field sales', 'account planning',
            'strategic account management', 'key accounts'
        ]
    },
    'marketing_manager': {
        'required': [
            'marketing', 'digital marketing', 'campaigns', 'campaign management',
            'content marketing', 'seo', 'social media', 'google analytics',
            'marketing strategy', 'marketing automation', 'email marketing',
            'brand management', 'lead generation'
        ],
        'preferred': [
            # Digital channels
            'sem', 'ppc', 'pay per click', 'google ads', 'facebook ads',
            'linkedin ads', 'display advertising', 'programmatic',
            'retargeting', 'remarketing', 'affiliate marketing',
            # Tools & platforms
            'hubspot', 'marketo', 'pardot', 'eloqua', 'mailchimp',
            'constant contact', 'hootsuite', 'sprout social', 'buffer',
            'google tag manager', 'google analytics 4', 'ga4',
            'adobe analytics', 'mixpanel', 'amplitude',
            # Content & creative
            'content strategy', 'content creation', 'copywriting',
            'creative direction', 'design', 'brand strategy',
            'brand positioning', 'messaging', 'value proposition',
            # Analytics & optimization
            'marketing analytics', 'roi', 'roas', 'attribution',
            'marketing attribution', 'multi-touch attribution',
            'conversion optimization', 'cro', 'a/b testing',
            'multivariate testing', 'landing pages', 'funnel optimization',
            # Operations
            'marketing operations', 'martech', 'marketing technology',
            'budget management', 'vendor management', 'agency management',
            'cms', 'wordpress', 'drupal'
        ]
    },

    # ===== OPERATIONS & CUSTOMER SUCCESS =====
    'operations_manager': {
        'required': [
            'operations', 'operations management', 'process improvement',
            'project management', 'team management', 'operations strategy',
            'efficiency', 'productivity', 'kpi tracking', 'process optimization',
            'workflow optimization', 'operational excellence'
        ],
        'preferred': [
            # Supply chain & logistics
            'supply chain', 'supply chain management', 'logistics',
            'inventory', 'inventory management', 'warehouse management',
            'distribution', 'fulfillment', 'procurement', 'vendor management',
            'supplier management', 'purchasing',
            # Methodologies
            'lean', 'lean manufacturing', 'lean principles', 'six sigma',
            'lean six sigma', 'green belt', 'black belt', 'kaizen',
            'continuous improvement', 'process mapping', 'value stream mapping',
            # Tools & systems
            'erp', 'sap', 'oracle', 'netsuite', 'microsoft dynamics',
            'wms', 'tms', 'oms', 'project management', 'ms project',
            # Skills
            'quality control', 'quality assurance', 'quality management',
            'cost reduction', 'cost optimization', 'capacity planning',
            'resource planning', 'production planning', 'scheduling',
            'change management', 'sop', 'standard operating procedures',
            'process documentation', 'metrics tracking', 'dashboards',
            'business analysis', 'root cause analysis', 'problem solving'
        ]
    },
    'customer_success_manager': {
        'required': [
            'customer success', 'customer retention', 'account management',
            'customer satisfaction', 'onboarding', 'customer onboarding',
            'crm', 'renewals', 'customer engagement', 'relationship management',
            'customer experience', 'account health'
        ],
        'preferred': [
            # Strategy & metrics
            'churn reduction', 'churn management', 'retention rate',
            'nps', 'net promoter score', 'csat', 'customer satisfaction score',
            'customer health score', 'engagement metrics', 'adoption metrics',
            'usage metrics', 'success metrics',
            # Growth
            'upselling', 'cross-selling', 'expansion', 'expansion revenue',
            'account expansion', 'customer advocacy', 'customer references',
            'case studies', 'testimonials', 'customer marketing',
            # Tools & platforms
            'gainsight', 'totango', 'planhat', 'salesforce', 'zendesk',
            'intercom', 'drift', 'helpscout', 'freshdesk',
            # Process & skills
            'product adoption', 'user adoption', 'feature adoption',
            'escalation management', 'issue resolution', 'customer feedback',
            'voice of customer', 'voc', 'customer insights',
            'customer journey', 'journey mapping', 'touchpoints',
            'qbr', 'quarterly business review', 'executive business review',
            'ebr', 'success planning', 'account planning',
            'stakeholder management', 'executive relationships'
        ]
    },

    # ===== CONTENT & DESIGN =====
    'content_writer': {
        'required': [
            'content writing', 'writing', 'copywriting', 'content strategy',
            'seo', 'seo writing', 'editing', 'proofreading', 'research',
            'cms', 'blogging', 'content creation', 'storytelling'
        ],
        'preferred': [
            # Content types
            'content marketing', 'blog posts', 'articles', 'white papers',
            'case studies', 'ebooks', 'guides', 'landing pages',
            'web content', 'website copy', 'product descriptions',
            'email copy', 'email campaigns', 'social media content',
            'video scripts', 'podcast scripts',
            # Tools & platforms
            'wordpress', 'contentful', 'hubspot', 'drupal', 'medium',
            'grammarly', 'hemingway', 'yoast', 'surfer seo',
            'clearscope', 'semrush', 'ahrefs',
            # Skills
            'content planning', 'content calendar', 'editorial calendar',
            'content strategy development', 'audience targeting',
            'buyer personas', 'tone of voice', 'brand voice',
            'style guide', 'ap style', 'chicago style',
            'keyword research', 'search intent', 'content optimization',
            'content performance', 'analytics', 'engagement metrics',
            'conversion copywriting', 'persuasive writing',
            'technical writing', 'ux writing', 'microcopy'
        ]
    },
    'product_designer': {
        'required': [
            'product design', 'ux', 'ui', 'user experience', 'user interface',
            'figma', 'user research', 'wireframing', 'prototyping',
            'design systems', 'user testing', 'interaction design',
            'visual design'
        ],
        'preferred': [
            # Tools
            'sketch', 'adobe xd', 'invision', 'framer', 'principle',
            'protopie', 'axure', 'balsamiq', 'miro', 'figjam',
            'zeplin', 'abstract', 'maze', 'optimal workshop',
            # Research & strategy
            'user flows', 'user journeys', 'journey mapping',
            'design thinking', 'design sprint', 'double diamond',
            'usability testing', 'user interviews', 'personas',
            'user personas', 'empathy mapping', 'customer journey',
            'information architecture', 'ia', 'card sorting',
            'tree testing', 'heuristic evaluation',
            # Design skills
            'a/b testing', 'multivariate testing', 'accessibility',
            'wcag', 'inclusive design', 'responsive design',
            'mobile design', 'web design', 'design handoff',
            'developer collaboration', 'design documentation',
            'design specs', 'redlining', 'design qa',
            # Process
            'agile', 'scrum', 'lean ux', 'atomic design',
            'component library', 'pattern library', 'design tokens',
            'design ops', 'design process', 'design critique'
        ]
    },
    'ui_designer': {
        'required': [
            'ui design', 'user interface', 'user interface design',
            'figma', 'visual design', 'design systems', 'prototyping',
            'html', 'css', 'responsive design', 'mobile design',
            'web design', 'interface design'
        ],
        'preferred': [
            # Tools & software
            'sketch', 'adobe xd', 'photoshop', 'illustrator',
            'after effects', 'principle', 'framer', 'invision',
            # Technical skills
            'javascript', 'react', 'vue', 'angular', 'sass', 'less',
            'tailwind', 'bootstrap', 'material design', 'ant design',
            # Design skills
            'typography', 'type design', 'color theory', 'color systems',
            'layout design', 'grid systems', 'spacing systems',
            'iconography', 'icon design', 'illustration',
            'animation', 'micro-interactions', 'motion design',
            'interaction design', 'interface animation',
            # Systems & process
            'design tokens', 'design system architecture',
            'component library', 'atomic design', 'accessibility',
            'wcag compliance', 'aria', 'usability', 'responsive',
            'mobile-first', 'adaptive design', 'cross-browser',
            'browser compatibility', 'design handoff', 'zeplin',
            'design specs', 'style guide', 'brand guidelines',
            'design qa', 'visual qa'
        ]
    },
    'ux_designer': {
        'required': [
            'ux design', 'user experience', 'user experience design',
            'user research', 'figma', 'wireframing', 'prototyping',
            'usability testing', 'user flows', 'information architecture',
            'interaction design', 'user-centered design'
        ],
        'preferred': [
            # Tools
            'sketch', 'adobe xd', 'axure', 'balsamiq', 'miro',
            'mural', 'optimal workshop', 'maze', 'usertesting',
            'lookback', 'hotjar', 'fullstory', 'google analytics',
            # Research methods
            'personas', 'user personas', 'journey mapping',
            'customer journey mapping', 'empathy mapping',
            'service blueprints', 'stakeholder mapping',
            'user interviews', 'contextual inquiry', 'ethnographic research',
            'diary studies', 'field studies', 'surveys',
            'questionnaires', 'card sorting', 'tree testing',
            'first click testing', 'heuristic evaluation',
            'cognitive walkthrough', 'expert review',
            # Strategy & process
            'design thinking', 'design sprint', 'lean ux',
            'agile ux', 'jobs to be done', 'jtbd',
            'problem framing', 'opportunity mapping',
            # Analysis & testing
            'a/b testing', 'multivariate testing', 'usability metrics',
            'quantitative research', 'qualitative research',
            'analytics', 'user behavior', 'heat maps',
            'session recordings', 'accessibility', 'wcag',
            'inclusive design', 'universal design'
        ]
    },

    # ===== TECH ROLES =====
    'software_engineer': {
        'required': [
            'programming', 'software development', 'software engineering',
            'coding', 'algorithms', 'data structures', 'git', 'version control',
            'api', 'rest', 'testing', 'debugging', 'code review',
            'software design', 'system design'
        ],
        'preferred': [
            # Languages
            'python', 'java', 'javascript', 'typescript', 'c++', 'c#',
            'go', 'golang', 'rust', 'kotlin', 'swift', 'ruby', 'php',
            'scala', 'r', 'matlab',
            # Frameworks & libraries
            'react', 'angular', 'vue', 'node', 'nodejs', 'express',
            'django', 'flask', 'spring', 'spring boot', '.net', 'asp.net',
            # Infrastructure & DevOps
            'docker', 'kubernetes', 'k8s', 'aws', 'azure', 'gcp',
            'terraform', 'ansible', 'jenkins', 'ci/cd', 'github actions',
            'gitlab ci', 'circleci',
            # Databases
            'sql', 'postgresql', 'mysql', 'mongodb', 'redis', 'elasticsearch',
            'cassandra', 'dynamodb', 'oracle', 'sql server',
            # Architecture & patterns
            'microservices', 'rest api', 'graphql', 'grpc',
            'event-driven', 'message queues', 'kafka', 'rabbitmq',
            'design patterns', 'solid principles', 'clean code',
            'tdd', 'test-driven development', 'bdd',
            # Tools & practices
            'linux', 'unix', 'bash', 'shell scripting', 'agile', 'scrum',
            'jira', 'confluence', 'code quality', 'code coverage',
            'unit testing', 'integration testing', 'performance testing'
        ]
    },
    'data_scientist': {
        'required': [
            'data science', 'machine learning', 'ml', 'python',
            'data analysis', 'statistics', 'statistical analysis',
            'sql', 'data visualization', 'modeling', 'analytics',
            'predictive modeling', 'data mining'
        ],
        'preferred': [
            # ML/DL
            'deep learning', 'neural networks', 'nlp', 'natural language processing',
            'computer vision', 'cv', 'image recognition', 'recommendation systems',
            'time series', 'forecasting', 'classification', 'regression',
            'clustering', 'dimensionality reduction', 'feature engineering',
            # Tools & frameworks
            'tensorflow', 'keras', 'pytorch', 'scikit-learn', 'sklearn',
            'xgboost', 'lightgbm', 'catboost', 'h2o',
            # Python libraries
            'pandas', 'numpy', 'matplotlib', 'seaborn', 'plotly',
            'scipy', 'statsmodels', 'jupyter', 'jupyter notebook',
            # Big data & cloud
            'spark', 'pyspark', 'hadoop', 'hive', 'pig',
            'aws', 'sagemaker', 'azure ml', 'google cloud ai',
            # Visualization
            'tableau', 'power bi', 'looker', 'data studio',
            # Other languages & tools
            'r', 'r studio', 'sas', 'matlab',
            # Techniques
            'a/b testing', 'hypothesis testing', 'bayesian statistics',
            'causal inference', 'experimental design'
        ]
    },
    'data_engineer': {
        'required': [
            'data engineering', 'etl', 'elt', 'sql', 'python',
            'data pipeline', 'data pipelines', 'data warehousing',
            'database', 'big data', 'data modeling', 'data architecture',
            'data integration'
        ],
        'preferred': [
            # Big data
            'spark', 'apache spark', 'pyspark', 'hadoop',
            'hive', 'presto', 'impala', 'pig',
            # Streaming
            'kafka', 'apache kafka', 'kinesis', 'pubsub',
            'stream processing', 'real-time processing', 'flink',
            # Orchestration & workflow
            'airflow', 'apache airflow', 'dagster', 'prefect',
            'luigi', 'oozie', 'azkaban',
            # Cloud platforms
            'aws', 'redshift', 'emr', 'glue', 'lambda',
            'azure', 'synapse', 'data factory', 'databricks',
            'gcp', 'bigquery', 'dataflow', 'dataproc',
            # Warehouses & lakes
            'snowflake', 'redshift', 'bigquery', 'synapse',
            'data lake', 'delta lake', 'iceberg',
            # Tools & frameworks
            'dbt', 'dataform', 'fivetran', 'stitch', 'talend',
            'scala', 'java', 'docker', 'kubernetes',
            # Databases
            'postgresql', 'mysql', 'mongodb', 'cassandra',
            'elasticsearch', 'dynamodb', 'cosmos db',
            # Skills
            'data quality', 'data governance', 'data catalog',
            'metadata management', 'data lineage', 'schema design',
            'dimensional modeling', 'star schema', 'snowflake schema',
            'slowly changing dimensions', 'scd'
        ]
    },
    'devops_engineer': {
        'required': [
            'devops', 'ci/cd', 'continuous integration', 'continuous deployment',
            'docker', 'kubernetes', 'aws', 'linux', 'automation',
            'infrastructure', 'infrastructure as code', 'iac',
            'cloud', 'scripting'
        ],
        'preferred': [
            # Cloud platforms
            'aws', 'ec2', 's3', 'lambda', 'ecs', 'eks', 'cloudformation',
            'azure', 'azure devops', 'arm templates',
            'gcp', 'google cloud', 'compute engine', 'gke',
            # IaC & configuration
            'terraform', 'terragrunt', 'ansible', 'chef', 'puppet',
            'cloudformation', 'arm', 'bicep', 'pulumi',
            # CI/CD
            'jenkins', 'gitlab ci', 'github actions', 'circleci',
            'travis ci', 'bamboo', 'teamcity', 'azure pipelines',
            'codebuild', 'codepipeline',
            # Containers & orchestration
            'docker', 'docker-compose', 'dockerfile', 'kubernetes', 'k8s',
            'helm', 'kustomize', 'istio', 'linkerd', 'argo cd',
            'flux', 'rancher', 'openshift',
            # Monitoring & logging
            'prometheus', 'grafana', 'elk', 'elasticsearch', 'logstash',
            'kibana', 'splunk', 'datadog', 'new relic', 'cloudwatch',
            'stackdriver', 'pagerduty', 'opsgenie',
            # Languages & scripting
            'python', 'bash', 'shell scripting', 'powershell', 'go',
            # Networking & security
            'networking', 'vpc', 'load balancing', 'dns', 'ssl', 'tls',
            'security', 'iam', 'secrets management', 'vault', 'kms',
            # Practices
            'sre', 'site reliability engineering', 'high availability',
            'disaster recovery', 'backup', 'monitoring', 'observability'
        ]
    },
    'qa_engineer': {
        'required': [
            'qa', 'quality assurance', 'testing', 'test automation',
            'automated testing', 'test cases', 'test plans', 'bug tracking',
            'manual testing', 'test planning', 'test strategy',
            'quality control'
        ],
        'preferred': [
            # Automation tools
            'selenium', 'selenium webdriver', 'appium', 'cypress',
            'playwright', 'testcafe', 'puppeteer', 'webdriverio',
            'robot framework', 'cucumber', 'testng', 'junit', 'pytest',
            # Programming
            'python', 'java', 'javascript', 'typescript', 'c#',
            # Testing types
            'api testing', 'rest api testing', 'postman', 'rest assured',
            'soapui', 'regression testing', 'smoke testing',
            'integration testing', 'end-to-end testing', 'e2e',
            'performance testing', 'load testing', 'stress testing',
            'security testing', 'penetration testing', 'mobile testing',
            'cross-browser testing', 'accessibility testing',
            # Tools & platforms
            'jira', 'testray', 'testrail', 'zephyr', 'xray',
            'browserstack', 'sauce labs', 'lambdatest',
            # Performance
            'jmeter', 'gatling', 'locust', 'k6', 'blazemeter',
            # CI/CD
            'jenkins', 'github actions', 'gitlab ci', 'ci/cd',
            'docker', 'continuous testing',
            # Methodologies
            'agile', 'scrum', 'waterfall', 'tdd', 'test-driven development',
            'bdd', 'behavior-driven development', 'shift-left testing',
            # Skills
            'sql', 'database testing', 'test automation framework',
            'page object model', 'pom', 'data-driven testing',
            'keyword-driven testing', 'test coverage', 'defect management',
            'test metrics', 'quality metrics'
        ]
    },
    'business_analyst': {
        'required': [
            'business analysis', 'requirements gathering', 'requirements analysis',
            'documentation', 'stakeholder management', 'sql', 'data analysis',
            'agile', 'business requirements', 'functional requirements',
            'process analysis', 'process improvement'
        ],
        'preferred': [
            # Documentation
            'user stories', 'use cases', 'business requirements document',
            'brd', 'functional requirements document', 'frd',
            'software requirements specification', 'srs',
            'process flows', 'workflow diagrams', 'wireframes',
            'mockups', 'prototypes',
            # Tools
            'jira', 'confluence', 'azure devops', 'visio',
            'lucidchart', 'draw.io', 'miro', 'figma', 'axure',
            # Analysis & modeling
            'process modeling', 'data modeling', 'gap analysis',
            'impact analysis', 'feasibility analysis', 'cost-benefit analysis',
            'swot analysis', 'as-is to-be', 'current state future state',
            # Data & reporting
            'sql', 'tableau', 'power bi', 'excel', 'advanced excel',
            'pivot tables', 'vlookup', 'macros', 'vba',
            'business intelligence', 'data visualization', 'dashboards',
            'kpi', 'metrics', 'reporting',
            # Methodologies
            'agile', 'scrum', 'kanban', 'waterfall', 'lean',
            'six sigma', 'babok', 'uml', 'bpmn',
            # Skills
            'elicitation', 'requirements elicitation', 'workshops',
            'facilitation', 'change management', 'user acceptance testing',
            'uat', 'test cases', 'solution design', 'system design',
            'vendor management', 'project management'
        ]
    },

    # ===== PRODUCT & PROJECT MANAGEMENT =====
    'product_manager': {
        'required': [
            'product management', 'product strategy', 'roadmap',
            'product roadmap', 'stakeholder management', 'user stories',
            'agile', 'requirements', 'prioritization', 'product planning',
            'product development', 'product lifecycle'
        ],
        'preferred': [
            # Agile & methodologies
            'scrum', 'kanban', 'safe', 'lean', 'product backlog',
            'sprint planning', 'story mapping', 'impact mapping',
            # Analytics & metrics
            'product analytics', 'metrics', 'kpi', 'okr',
            'product metrics', 'user metrics', 'engagement metrics',
            'retention metrics', 'cohort analysis', 'funnel analysis',
            'a/b testing', 'experimentation', 'hypothesis testing',
            # Research
            'user research', 'customer research', 'market research',
            'competitive analysis', 'competitor analysis', 'user interviews',
            'surveys', 'user testing', 'usability testing',
            # Tools
            'jira', 'productboard', 'aha', 'pivotal tracker',
            'asana', 'trello', 'confluence', 'miro', 'figma',
            'google analytics', 'mixpanel', 'amplitude', 'heap',
            # Technical
            'sql', 'api', 'rest api', 'technical documentation',
            'system architecture', 'database', 'wireframing',
            # Strategy
            'product vision', 'product strategy', 'go-to-market', 'gtm',
            'product launch', 'launch planning', 'mvp', 'minimum viable product',
            'product-market fit', 'value proposition', 'positioning',
            'pricing', 'pricing strategy', 'prd', 'product requirements document',
            'feature definition', 'feature prioritization',
            'cross-functional', 'cross-functional leadership',
            'engineering collaboration', 'design collaboration'
        ]
    },
    'technical_product_manager': {
        'required': [
            'product management', 'technical product management',
            'technical', 'api', 'architecture', 'system architecture',
            'roadmap', 'agile', 'engineering', 'stakeholder management',
            'technical requirements', 'system design'
        ],
        'preferred': [
            # Technical skills
            'sql', 'python', 'rest api', 'graphql', 'grpc',
            'microservices', 'distributed systems', 'cloud',
            'aws', 'azure', 'gcp', 'system design', 'data modeling',
            'database design', 'schema design', 'api design',
            'technical specifications', 'technical documentation',
            # Architecture
            'software architecture', 'solution architecture',
            'integration', 'integrations', 'third-party integrations',
            'webhooks', 'event-driven architecture', 'scalability',
            'performance', 'reliability', 'security',
            # Platform & infrastructure
            'platform', 'platform development', 'developer tools',
            'sdk', 'developer experience', 'dx', 'api documentation',
            'backend', 'infrastructure', 'devops', 'ci/cd',
            # Tools & practices
            'jira', 'confluence', 'github', 'gitlab',
            'postman', 'swagger', 'openapi', 'technical roadmap',
            'technical debt', 'code review', 'sprint planning',
            # Strategy
            'technical strategy', 'engineering strategy',
            'build vs buy', 'technical feasibility', 'capacity planning',
            'resource planning', 'engineering metrics', 'velocity',
            'technical requirements', 'api strategy', 'data strategy'
        ]
    },
    'project_manager': {
        'required': [
            'project management', 'planning', 'project planning',
            'scheduling', 'stakeholder management', 'risk management',
            'budget', 'budget management', 'team coordination',
            'pmp', 'project coordination', 'project execution',
            'project delivery'
        ],
        'preferred': [
            # Methodologies
            'agile', 'scrum', 'kanban', 'waterfall', 'hybrid',
            'safe', 'prince2', 'pmi', 'pmbok', 'lean',
            # Tools
            'jira', 'microsoft project', 'ms project', 'smartsheet',
            'asana', 'monday.com', 'trello', 'basecamp', 'wrike',
            'confluence', 'sharepoint', 'excel', 'powerpoint',
            # Planning & scheduling
            'resource management', 'resource allocation', 'capacity planning',
            'project scheduling', 'timeline management', 'milestone tracking',
            'critical path', 'critical path method', 'cpm',
            'gantt chart', 'pert', 'network diagram',
            # Management skills
            'status reporting', 'executive reporting', 'stakeholder communication',
            'change management', 'scope management', 'time management',
            'cost management', 'quality management', 'procurement management',
            'issue management', 'risk mitigation', 'dependency management',
            # Project artifacts
            'project charter', 'project plan', 'work breakdown structure',
            'wbs', 'risk register', 'raid log', 'status reports',
            'project dashboard', 'project metrics', 'kpi tracking',
            # Certifications & standards
            'pmp certified', 'capm', 'csm', 'certified scrum master',
            'prince2 certified', 'agile certified', 'pmi-acp',
            # Skills
            'vendor management', 'contract management', 'negotiation',
            'team leadership', 'conflict resolution', 'problem solving',
            'decision making', 'lessons learned', 'post-mortem'
        ]
    },
}

def get_role_keywords(role_id: str):
    """Get keywords for a specific role."""
    return ROLE_KEYWORDS.get(role_id)

def get_all_roles():
    """Get list of all available role IDs."""
    return list(ROLE_KEYWORDS.keys())
