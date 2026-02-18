"""
Synonym database for intelligent keyword matching.

This module provides a comprehensive mapping of related terms to enable
better keyword matching in ATS resume scoring. It supports both direct
lookup (main keyword -> synonyms) and reverse lookup (synonym -> main keyword).
"""

from typing import List, Set


# Synonym database organized by category
SYNONYM_DATABASE = {
    # Programming Languages
    "python": ["py", "python3", "python2", "cpython"],
    "javascript": ["js", "es6", "es2015", "ecmascript", "node.js", "nodejs"],
    "java": ["jdk", "jvm", "java se", "java ee"],
    "c++": ["cpp", "c plus plus"],
    "c#": ["csharp", "c sharp", ".net"],
    "golang": ["go", "go lang"],
    "typescript": ["ts"],
    "ruby": ["rb", "ruby on rails", "rails"],
    "php": ["php5", "php7", "php8"],
    "swift": ["swift ui", "swiftui"],
    "kotlin": ["kt"],
    "rust": ["rs"],
    "scala": ["sc"],
    "r": ["r language", "r programming"],
    "perl": ["pl"],
    "shell": ["bash", "sh", "zsh", "shell script", "shell scripting"],

    # Cloud Platforms
    "aws": ["amazon web services", "amazon aws"],
    "azure": ["microsoft azure", "azure cloud"],
    "gcp": ["google cloud platform", "google cloud", "gcloud"],
    "ibm cloud": ["ibm bluemix", "bluemix"],
    "oracle cloud": ["oci", "oracle cloud infrastructure"],

    # AWS Services
    "ec2": ["elastic compute cloud", "amazon ec2"],
    "s3": ["simple storage service", "amazon s3"],
    "lambda": ["aws lambda", "serverless lambda"],
    "rds": ["relational database service", "amazon rds"],
    "dynamodb": ["dynamo db", "amazon dynamodb"],
    "cloudformation": ["cloud formation", "cfn"],
    "eks": ["elastic kubernetes service"],
    "ecs": ["elastic container service"],

    # DevOps & CI/CD Tools
    "kubernetes": ["k8s", "kube"],
    "docker": ["containerization", "containers"],
    "terraform": ["tf", "infrastructure as code", "iac"],
    "jenkins": ["jenkins ci", "jenkins cd"],
    "gitlab": ["gitlab ci", "gitlab ci/cd"],
    "github actions": ["github action", "gh actions"],
    "circleci": ["circle ci"],
    "travis ci": ["travis"],
    "ansible": ["ansible playbook", "ansible automation"],
    "puppet": ["puppet labs"],
    "chef": ["chef automation"],
    "vagrant": ["vagrant box"],

    # Version Control
    "git": ["version control", "source control", "github", "gitlab", "bitbucket"],
    "svn": ["subversion", "apache subversion"],
    "mercurial": ["hg"],

    # Databases - SQL
    "postgresql": ["postgres", "psql", "pg"],
    "mysql": ["my sql", "mysql server"],
    "sql server": ["mssql", "microsoft sql server", "ms sql"],
    "oracle": ["oracle database", "oracle db"],
    "sqlite": ["sqlite3"],
    "mariadb": ["maria db"],

    # Databases - NoSQL
    "mongodb": ["mongo", "mongo db"],
    "redis": ["redis cache"],
    "cassandra": ["apache cassandra"],
    "couchdb": ["couch db", "apache couchdb"],
    "elasticsearch": ["elastic search", "es"],
    "neo4j": ["neo4j graph database"],

    # Web Frameworks
    "react": ["reactjs", "react.js", "react js"],
    "angular": ["angularjs", "angular.js"],
    "vue": ["vuejs", "vue.js"],
    "django": ["django rest framework", "drf"],
    "flask": ["flask api"],
    "express": ["expressjs", "express.js"],
    "spring": ["spring boot", "spring framework"],
    "laravel": ["laravel framework"],

    # Mobile Development
    "android": ["android development", "android sdk"],
    "ios": ["ios development", "iphone development"],
    "react native": ["react-native"],
    "flutter": ["flutter sdk"],

    # Testing & Quality Assurance
    "selenium": ["selenium webdriver"],
    "junit": ["j unit"],
    "pytest": ["py test"],
    "jest": ["jest testing"],
    "mocha": ["mocha testing"],
    "cypress": ["cypress.io"],
    "test driven development": ["tdd"],
    "behavior driven development": ["bdd"],

    # Data Science & Machine Learning
    "machine learning": ["ml", "ml engineering"],
    "deep learning": ["dl", "neural networks"],
    "natural language processing": ["nlp"],
    "computer vision": ["cv", "image processing"],
    "artificial intelligence": ["ai"],
    "data science": ["ds"],
    "tensorflow": ["tf", "tensor flow"],
    "pytorch": ["torch"],
    "scikit-learn": ["sklearn", "scikit learn"],
    "pandas": ["pd"],
    "numpy": ["np"],
    "matplotlib": ["mpl"],
    "jupyter": ["jupyter notebook", "jupyter lab"],

    # Methodologies & Practices
    "agile": ["agile methodology", "agile development", "scrum"],
    "scrum": ["scrum master", "scrum methodology"],
    "kanban": ["kanban board"],
    "ci/cd": ["continuous integration", "continuous deployment", "continuous delivery"],
    "microservices": ["micro services", "microservice architecture"],
    "rest api": ["restful api", "rest", "restful"],
    "graphql": ["graph ql"],
    "soap": ["soap api"],
    "api": ["application programming interface"],
    "sdk": ["software development kit"],

    # Project Management & Collaboration
    "jira": ["jira software", "atlassian jira"],
    "confluence": ["atlassian confluence"],
    "slack": ["slack communication"],
    "trello": ["trello board"],
    "asana": ["asana project management"],

    # Action Verbs - Leadership
    "managed": ["led", "directed", "oversaw", "supervised", "coordinated"],
    "developed": ["built", "created", "designed", "engineered", "implemented"],
    "improved": ["enhanced", "optimized", "streamlined", "upgraded", "refined"],
    "reduced": ["decreased", "minimized", "lowered", "cut", "diminished"],
    "increased": ["boosted", "raised", "grew", "expanded", "amplified"],
    "launched": ["released", "deployed", "shipped", "initiated", "introduced"],
    "achieved": ["accomplished", "attained", "delivered", "completed", "executed"],
    "collaborated": ["partnered", "cooperated", "worked with", "teamed up"],
    "analyzed": ["examined", "evaluated", "assessed", "investigated", "studied"],
    "established": ["founded", "instituted", "created", "set up", "formed"],

    # Action Verbs - Technical
    "architected": ["designed architecture", "designed system"],
    "debugged": ["troubleshot", "diagnosed", "fixed bugs"],
    "refactored": ["restructured", "reorganized code"],
    "automated": ["scripted", "streamlined automation"],
    "integrated": ["connected", "interfaced", "linked"],
    "migrated": ["transferred", "moved", "ported"],
    "scaled": ["expanded capacity", "increased scalability"],
    "monitored": ["tracked", "observed", "watched"],
    "documented": ["recorded", "catalogued", "wrote documentation"],

    # Soft Skills
    "leadership": ["team leadership", "leading teams"],
    "communication": ["verbal communication", "written communication"],
    "problem solving": ["problem-solving", "analytical thinking"],
    "teamwork": ["team collaboration", "team player"],
    "time management": ["organization", "prioritization"],
    "adaptability": ["flexibility", "versatile"],
    "critical thinking": ["analytical skills"],
    "mentoring": ["coaching", "training", "mentorship"],

    # Roles & Titles
    "software engineer": ["software developer", "developer", "programmer"],
    "senior software engineer": ["senior developer", "senior programmer"],
    "data scientist": ["ml engineer", "data analyst"],
    "product manager": ["pm", "product owner"],
    "project manager": ["program manager"],
    "devops engineer": ["sre", "site reliability engineer", "platform engineer"],
    "full stack developer": ["fullstack developer", "full-stack developer"],
    "frontend developer": ["front-end developer", "front end developer", "ui developer"],
    "backend developer": ["back-end developer", "back end developer"],
    "qa engineer": ["quality assurance engineer", "test engineer", "sdet"],
    "data engineer": ["etl developer", "data pipeline engineer"],

    # Security
    "security": ["cybersecurity", "information security", "infosec"],
    "authentication": ["auth", "authorization"],
    "oauth": ["oauth2", "oauth 2.0"],
    "jwt": ["json web token", "json web tokens"],
    "ssl": ["tls", "ssl/tls", "https"],
    "encryption": ["cryptography", "crypto"],

    # Networking
    "http": ["https", "http protocol"],
    "tcp/ip": ["tcp", "ip", "networking"],
    "dns": ["domain name system"],
    "load balancing": ["load balancer", "lb"],
    "cdn": ["content delivery network"],

    # Monitoring & Logging
    "prometheus": ["prometheus monitoring"],
    "grafana": ["grafana dashboard"],
    "datadog": ["data dog"],
    "new relic": ["newrelic"],
    "splunk": ["splunk enterprise"],
    "elk": ["elasticsearch logstash kibana", "elk stack"],

    # Big Data
    "hadoop": ["apache hadoop"],
    "spark": ["apache spark", "pyspark"],
    "kafka": ["apache kafka"],
    "airflow": ["apache airflow"],
    "flink": ["apache flink"],

    # Business & Analytics
    "kpi": ["key performance indicator", "metrics"],
    "roi": ["return on investment"],
    "b2b": ["business to business"],
    "b2c": ["business to consumer"],
    "saas": ["software as a service"],
    "paas": ["platform as a service"],
    "iaas": ["infrastructure as a service"],
}


def get_all_synonyms(keyword: str) -> List[str]:
    """
    Get all synonyms for a given keyword.

    Supports both direct lookup (main keyword -> synonyms) and
    reverse lookup (synonym -> main keyword).

    Args:
        keyword: The keyword to look up (case-insensitive)

    Returns:
        List of all synonyms including the keyword itself

    Examples:
        >>> get_all_synonyms("python")
        ['python', 'py', 'python3', 'python2', 'cpython']

        >>> get_all_synonyms("k8s")  # Reverse lookup
        ['k8s', 'kubernetes', 'kube']
    """
    keyword_lower = keyword.lower().strip()
    result_set: Set[str] = {keyword_lower}

    # Direct lookup: keyword is a main entry
    if keyword_lower in SYNONYM_DATABASE:
        result_set.update(SYNONYM_DATABASE[keyword_lower])

    # Reverse lookup: keyword is a synonym
    for main_keyword, synonyms in SYNONYM_DATABASE.items():
        if keyword_lower in synonyms:
            result_set.add(main_keyword)
            result_set.update(synonyms)
            break  # Found it, no need to continue

    return sorted(list(result_set))


def expand_keywords(keywords: List[str]) -> List[str]:
    """
    Expand a list of keywords to include all their synonyms.

    Args:
        keywords: List of keywords to expand

    Returns:
        Deduplicated list of all keywords and their synonyms

    Examples:
        >>> expand_keywords(["python", "aws"])
        ['amazon aws', 'amazon web services', 'aws', 'cpython', 'py',
         'python', 'python2', 'python3']
    """
    expanded_set: Set[str] = set()

    for keyword in keywords:
        synonyms = get_all_synonyms(keyword)
        expanded_set.update(synonyms)

    return sorted(list(expanded_set))
