"""
LinkedIn Skills Scraper - MOCK DATA VERSION

IMPORTANT: This script generates MOCK data instead of actual LinkedIn scraping.
This approach avoids authentication requirements and provides realistic skill data
for the ATS resume scorer system.

The mock data includes modern tech terms that O*NET might not have (Kubernetes,
Terraform, GraphQL, Next.js, React, TypeScript, etc.) based on industry trends
and common job postings.

Run once during setup to generate backend/data/keywords/linkedin_skills.json
"""

import json
from pathlib import Path
from typing import Dict, List


# The 7 roles we're generating skills for
ROLES = [
    "Software Engineer",
    "Data Scientist",
    "DevOps Engineer",
    "Product Manager",
    "UX Designer",
    "Data Engineer",
    "QA Engineer"
]


def generate_mock_linkedin_skills() -> Dict[str, List[str]]:
    """
    Generate realistic mock skills data for each role.
    Returns 50-100 skills per role with modern tech terms.

    Returns:
        Dict mapping role name to list of skills (lowercase)
    """

    skills_data = {
        "Software Engineer": [
            # Programming Languages
            "python", "javascript", "java", "typescript", "c++", "c#", "go",
            "rust", "ruby", "php", "kotlin", "swift", "scala",

            # Frontend
            "react", "angular", "vue.js", "next.js", "svelte", "html", "css",
            "sass", "less", "webpack", "vite", "redux", "react native",
            "flutter", "electron", "tailwind css", "bootstrap", "material-ui",

            # Backend
            "node.js", "express.js", "django", "flask", "fastapi", "spring boot",
            "asp.net", ".net core", "laravel", "rails",

            # Databases
            "sql", "postgresql", "mysql", "mongodb", "redis", "elasticsearch",
            "cassandra", "dynamodb", "sqlite", "mariadb",

            # Cloud & DevOps
            "aws", "azure", "gcp", "docker", "kubernetes", "ci/cd", "jenkins",
            "terraform", "ansible", "github actions", "gitlab ci",

            # APIs & Protocols
            "rest api", "graphql", "grpc", "websockets", "microservices",
            "oauth", "jwt", "api design",

            # Tools & Practices
            "git", "agile", "scrum", "tdd", "unit testing", "integration testing",
            "code review", "debugging", "performance optimization",
            "security best practices", "design patterns", "algorithms",
            "data structures", "system design", "object-oriented programming",
            "functional programming", "linux", "bash", "vim"
        ],

        "Data Scientist": [
            # Programming
            "python", "r", "sql", "java", "scala", "julia",

            # ML/AI Frameworks
            "machine learning", "deep learning", "tensorflow", "pytorch",
            "keras", "scikit-learn", "xgboost", "lightgbm", "catboost",

            # Data Tools
            "pandas", "numpy", "scipy", "matplotlib", "seaborn", "plotly",
            "jupyter", "spyder", "anaconda",

            # Big Data
            "spark", "hadoop", "hive", "pig", "kafka", "airflow", "databricks",

            # Statistics & Math
            "statistics", "probability", "linear algebra", "calculus",
            "hypothesis testing", "regression analysis", "time series",
            "bayesian methods", "a/b testing",

            # ML Techniques
            "supervised learning", "unsupervised learning", "reinforcement learning",
            "neural networks", "computer vision", "nlp", "natural language processing",
            "transformers", "bert", "gpt", "classification", "clustering",
            "dimensionality reduction", "feature engineering", "model evaluation",
            "cross-validation", "ensemble methods", "random forest", "gradient boosting",

            # Databases
            "postgresql", "mysql", "mongodb", "redis", "bigquery", "snowflake",
            "redshift",

            # Cloud
            "aws", "azure", "gcp", "sagemaker", "ml ops",

            # Visualization
            "tableau", "power bi", "looker", "data visualization",
            "dashboard design",

            # Domain Knowledge
            "predictive modeling", "data mining", "data wrangling",
            "statistical analysis", "experimental design", "causal inference",
            "business intelligence", "data storytelling"
        ],

        "DevOps Engineer": [
            # Core DevOps
            "ci/cd", "continuous integration", "continuous deployment",
            "infrastructure as code", "automation", "configuration management",

            # Containers & Orchestration
            "docker", "kubernetes", "helm", "docker compose", "containerd",
            "podman", "eks", "aks", "gke", "openshift",

            # Cloud Platforms
            "aws", "azure", "gcp", "cloud architecture", "cloud migration",
            "ec2", "s3", "lambda", "cloudformation", "cloud watch",

            # Infrastructure as Code
            "terraform", "ansible", "puppet", "chef",
            "pulumi", "arm templates",

            # CI/CD Tools
            "jenkins", "gitlab ci", "github actions", "circleci", "travis ci",
            "bamboo", "teamcity", "spinnaker", "argo cd",

            # Monitoring & Logging
            "prometheus", "grafana", "elk stack", "elasticsearch", "logstash",
            "kibana", "datadog", "new relic", "splunk", "nagios", "zabbix",

            # Scripting
            "bash", "python", "powershell", "shell scripting", "groovy",

            # Version Control
            "git", "github", "gitlab", "bitbucket", "git workflow",

            # Networking
            "networking", "load balancing", "dns", "tcp/ip", "http/https",
            "vpn", "firewall", "nginx", "apache", "haproxy",

            # Security
            "security best practices", "vulnerability scanning", "secrets management",
            "vault", "ssl/tls", "iam", "rbac",

            # Operating Systems
            "linux", "ubuntu", "centos", "red hat", "windows server",

            # Databases
            "postgresql", "mysql", "mongodb", "redis", "database administration",

            # Methodologies
            "agile", "scrum", "devops culture", "sre", "incident management",
            "disaster recovery", "high availability", "scalability"
        ],

        "Product Manager": [
            # Core PM Skills
            "product management", "product strategy", "product roadmap",
            "product lifecycle", "product vision", "go-to-market strategy",

            # User Research
            "user research", "customer interviews", "user personas", "user stories",
            "jobs to be done", "customer journey mapping", "empathy mapping",

            # Design & UX
            "user experience", "wireframing", "prototyping", "figma", "sketch",
            "invision", "design thinking", "user testing", "usability testing",

            # Analytics
            "data analysis", "metrics", "kpis", "google analytics", "mixpanel",
            "amplitude", "a/b testing", "cohort analysis", "funnel analysis",
            "product analytics",

            # Technical
            "sql", "api understanding", "technical documentation", "system design",
            "software development lifecycle", "agile", "scrum", "jira", "confluence",

            # Business
            "business strategy", "market research", "competitive analysis",
            "business case development", "roi analysis", "pricing strategy",
            "business model", "revenue strategy",

            # Stakeholder Management
            "stakeholder management", "communication", "presentation skills",
            "executive communication", "cross-functional collaboration",
            "team leadership", "influence without authority",

            # Prioritization
            "prioritization", "backlog management", "feature prioritization",
            "value vs effort", "impact mapping", "okrs", "objectives and key results",

            # Development Process
            "requirements gathering", "user acceptance testing", "release planning",
            "sprint planning", "product backlog", "acceptance criteria",

            # Market Understanding
            "market trends", "industry knowledge", "customer needs", "problem solving",
            "innovation", "product-market fit", "mvp", "minimum viable product",

            # Tools
            "productboard", "aha!", "asana", "monday.com", "notion", "miro",
            "microsoft excel", "powerpoint", "google slides"
        ],

        "UX Designer": [
            # Core UX
            "user experience design", "user interface design", "ux research",
            "interaction design", "information architecture", "usability",

            # Design Tools
            "figma", "sketch", "adobe xd", "invision", "framer", "principle",
            "protopie", "zeplin", "abstract",

            # Adobe Suite
            "adobe photoshop", "adobe illustrator", "adobe after effects",

            # Research Methods
            "user research", "usability testing", "user interviews",
            "surveys", "card sorting", "tree testing", "contextual inquiry",
            "ethnographic research", "diary studies",

            # Design Process
            "design thinking", "human-centered design", "user-centered design",
            "design sprint", "iterative design", "rapid prototyping",

            # Artifacts
            "wireframing", "prototyping", "mockups", "user flows", "journey maps",
            "personas", "empathy maps", "storyboards", "site maps",
            "design systems", "style guides", "pattern libraries",

            # Testing
            "a/b testing", "multivariate testing", "heuristic evaluation",
            "cognitive walkthrough", "eye tracking", "heat maps",

            # Front-end Knowledge
            "html", "css", "responsive design", "mobile design", "web design",
            "ios design", "android design", "material design", "human interface guidelines",

            # Accessibility
            "accessibility", "wcag", "inclusive design", "universal design",
            "screen readers", "keyboard navigation",

            # Visual Design
            "visual design", "typography", "color theory", "layout", "grid systems",
            "iconography", "illustration",

            # Collaboration
            "cross-functional collaboration", "stakeholder management",
            "design critique", "design presentation", "design documentation",

            # Methodologies
            "agile", "scrum", "lean ux", "design ops",

            # Analytics
            "google analytics", "hotjar", "fullstory", "user analytics",
            "conversion rate optimization"
        ],

        "Data Engineer": [
            # Programming
            "python", "java", "scala", "sql", "pyspark", "go", "r",

            # Big Data
            "spark", "hadoop", "hive", "pig", "mapreduce", "hdfs", "yarn",

            # Data Warehousing
            "data warehouse", "snowflake", "redshift", "bigquery", "synapse",
            "dimensional modeling", "star schema",

            # Databases
            "postgresql", "mysql", "mongodb", "cassandra", "redis", "dynamodb",
            "elasticsearch", "neo4j", "graph databases", "columnar databases",

            # ETL/ELT
            "etl", "elt", "data pipelines", "airflow", "luigi", "prefect",
            "dagster", "data integration", "data transformation",

            # Stream Processing
            "kafka", "kinesis", "flink", "storm", "spark streaming",
            "real-time processing", "event streaming",

            # Cloud Data Services
            "aws", "azure", "gcp", "s3", "glue", "emr", "athena", "data factory",
            "cloud storage", "cloud functions", "lambda",

            # Data Modeling
            "data modeling", "data architecture", "database design",
            "schema design", "normalization", "denormalization",

            # Infrastructure as Code
            "terraform", "cloudformation", "docker", "kubernetes",

            # Orchestration
            "workflow orchestration", "job scheduling", "cron", "data lineage",

            # Data Quality
            "data quality", "data validation", "data profiling", "data cleansing",
            "data governance", "data catalog", "metadata management",

            # APIs
            "rest api", "api development", "api integration", "webhooks",

            # Version Control
            "git", "github", "gitlab", "version control",

            # Performance
            "query optimization", "performance tuning", "indexing",
            "partitioning", "sharding"
        ],

        "QA Engineer": [
            # Testing Types
            "manual testing", "automated testing", "functional testing",
            "regression testing", "integration testing", "system testing",
            "smoke testing", "sanity testing", "exploratory testing",
            "acceptance testing", "end-to-end testing",

            # Test Automation
            "test automation", "selenium", "cypress", "playwright", "puppeteer",
            "webdriverio", "appium", "testcafe",

            # Programming
            "python", "java", "javascript", "typescript", "c#",

            # Testing Frameworks
            "pytest", "junit", "testng", "jest", "mocha", "jasmine", "cucumber",
            "robot framework", "behave",

            # Performance Testing
            "performance testing", "load testing", "stress testing", "jmeter",
            "gatling", "locust", "k6",

            # API Testing
            "api testing", "rest api", "postman", "soap ui", "rest assured",
            "graphql testing",

            # Mobile Testing
            "mobile testing", "ios testing", "android testing",
            "espresso", "xcuitest",

            # CI/CD
            "ci/cd", "jenkins", "github actions", "gitlab ci", "circleci",
            "continuous testing",

            # Test Management
            "test planning", "test strategy", "test cases", "test scenarios",
            "test documentation", "test reports", "defect tracking",
            "jira", "testrail", "zephyr", "xray",

            # Methodologies
            "agile", "scrum", "bdd", "tdd",

            # Security Testing
            "security testing", "penetration testing", "vulnerability assessment",
            "owasp", "burp suite",

            # Database Testing
            "database testing", "sql", "data validation", "data integrity",

            # Tools
            "git", "docker", "bash", "chrome devtools", "browser devtools",

            # Cross-browser Testing
            "cross-browser testing", "browserstack", "sauce labs",

            # Accessibility Testing
            "accessibility testing", "wcag",

            # Skills
            "debugging", "troubleshooting", "root cause analysis", "attention to detail",
            "analytical thinking", "problem solving", "communication",
            "documentation", "test data management"
        ]
    }

    return skills_data


def main() -> Path:
    """
    Generate mock LinkedIn skills data and save to JSON file.

    Returns:
        Path to saved JSON file
    """
    print("Generating mock LinkedIn skills data...")
    print("(Using mock data to avoid authentication requirements)")

    # Generate skills
    skills_data = generate_mock_linkedin_skills()

    # Verify we have all roles
    for role in ROLES:
        assert role in skills_data, f"Missing role: {role}"
        skill_count = len(skills_data[role])
        print(f"  {role}: {skill_count} skills")

        # Verify skill count is in range
        if not (50 <= skill_count <= 100):
            print(f"    WARNING: {role} has {skill_count} skills (expected 50-100)")

    # Save to JSON
    output_path = Path(__file__).parent.parent / "data" / "keywords" / "linkedin_skills.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w') as f:
        json.dump(skills_data, f, indent=2)

    print(f"\n✓ Generated mock LinkedIn skills for {len(skills_data)} roles")
    print(f"✓ Saved to {output_path}")
    print(f"✓ Total skills generated: {sum(len(skills) for skills in skills_data.values())}")
    print("\nNote: This is MOCK data, not actual LinkedIn scraping.")
    print("Includes modern tech terms: Kubernetes, Terraform, GraphQL, Next.js, React, TypeScript, etc.")

    return output_path


if __name__ == "__main__":
    main()
