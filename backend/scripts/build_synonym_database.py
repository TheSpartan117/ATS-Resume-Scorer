#!/usr/bin/env python3
"""
Build Synonym Database

Creates a comprehensive mapping of technology terms to their variations and synonyms.
This enables flexible keyword matching - e.g., "Python3" matches "Python", "ReactJS" matches "React".

Output: backend/data/synonyms/skill_synonyms.json
"""

import json
from pathlib import Path


def build_synonym_database():
    """Build comprehensive synonym mappings for 70+ technology terms."""

    synonyms = {
        # Programming Languages
        "Python": ["python", "python3", "py", "cpython", "python2", "python 3"],
        "JavaScript": ["javascript", "js", "ecmascript", "es6", "es2015", "es2020", "vanilla js"],
        "Java": ["java", "java8", "java11", "java17", "jdk", "java se"],
        "TypeScript": ["typescript", "ts", "type script"],
        "C++": ["c++", "cpp", "c plus plus", "cplusplus"],
        "C#": ["c#", "csharp", "c sharp", ".net", "dotnet"],
        "Ruby": ["ruby", "rb", "ruby on rails", "ror"],
        "Go": ["go", "golang", "go lang"],
        "Rust": ["rust", "rust lang"],
        "PHP": ["php", "php7", "php8", "hypertext preprocessor"],
        "Swift": ["swift", "swift 5", "swiftui"],
        "Kotlin": ["kotlin", "kt"],
        "R": ["r", "r programming", "r language"],
        "Scala": ["scala", "scala lang"],
        "Perl": ["perl", "perl5"],
        "Shell": ["shell", "bash", "sh", "shell script", "shell scripting"],
        "SQL": ["sql", "structured query language", "t-sql", "pl/sql"],

        # Frontend Frameworks & Libraries
        "React": ["react", "reactjs", "react.js", "react js", "react native"],
        "Angular": ["angular", "angularjs", "angular.js", "angular 2+", "ng"],
        "Vue": ["vue", "vuejs", "vue.js", "vue js"],
        "Next.js": ["next.js", "nextjs", "next", "next js"],
        "Svelte": ["svelte", "sveltejs", "svelte.js"],
        "jQuery": ["jquery", "jquery ui"],

        # Backend Frameworks
        "Node.js": ["node.js", "nodejs", "node", "node js"],
        "Express": ["express", "expressjs", "express.js", "express js"],
        "Django": ["django", "django rest framework", "drf"],
        "Flask": ["flask", "flask rest", "flask-restful"],
        "FastAPI": ["fastapi", "fast api"],
        "Spring": ["spring", "spring boot", "spring framework", "springframework"],
        "Ruby on Rails": ["ruby on rails", "rails", "ror", "ruby-on-rails"],
        "Laravel": ["laravel", "laravel framework"],
        "ASP.NET": ["asp.net", "aspnet", "asp .net", "asp net"],

        # Cloud Platforms
        "AWS": ["aws", "amazon web services", "amazon aws"],
        "Azure": ["azure", "microsoft azure", "azure cloud"],
        "GCP": ["gcp", "google cloud", "google cloud platform", "gcloud"],
        "Heroku": ["heroku", "heroku cloud"],
        "DigitalOcean": ["digitalocean", "digital ocean", "do"],

        # AWS Services
        "EC2": ["ec2", "elastic compute cloud", "aws ec2"],
        "S3": ["s3", "simple storage service", "aws s3"],
        "Lambda": ["lambda", "aws lambda", "lambda functions"],
        "RDS": ["rds", "relational database service", "aws rds"],
        "DynamoDB": ["dynamodb", "dynamo db", "aws dynamodb"],
        "CloudFormation": ["cloudformation", "cloud formation", "cfn"],
        "ECS": ["ecs", "elastic container service", "aws ecs"],
        "EKS": ["eks", "elastic kubernetes service", "aws eks"],

        # DevOps & Containers
        "Docker": ["docker", "docker container", "docker compose", "dockerfile"],
        "Kubernetes": ["kubernetes", "k8s", "k-8-s", "kube"],
        "Jenkins": ["jenkins", "jenkins ci", "jenkins ci/cd"],
        "GitLab CI": ["gitlab ci", "gitlab-ci", "gitlab ci/cd", "gitlab pipeline"],
        "GitHub Actions": ["github actions", "github action", "gh actions"],
        "CircleCI": ["circleci", "circle ci"],
        "Terraform": ["terraform", "tf", "terraform iac"],
        "Ansible": ["ansible", "ansible automation"],
        "Chef": ["chef", "chef automation"],
        "Puppet": ["puppet", "puppet automation"],

        # Databases
        "PostgreSQL": ["postgresql", "postgres", "psql", "pg"],
        "MySQL": ["mysql", "my sql"],
        "MongoDB": ["mongodb", "mongo", "mongo db"],
        "Redis": ["redis", "redis cache"],
        "Elasticsearch": ["elasticsearch", "elastic search", "es", "elk"],
        "Cassandra": ["cassandra", "apache cassandra"],
        "Oracle": ["oracle", "oracle db", "oracle database"],
        "SQLite": ["sqlite", "sqlite3"],
        "MariaDB": ["mariadb", "maria db"],

        # Testing Frameworks
        "Jest": ["jest", "jestjs", "jest testing"],
        "Pytest": ["pytest", "py.test", "pytest framework"],
        "JUnit": ["junit", "junit5", "junit 5"],
        "Selenium": ["selenium", "selenium webdriver"],
        "Cypress": ["cypress", "cypress.io", "cypress testing"],
        "Mocha": ["mocha", "mochajs", "mocha.js"],
        "TestNG": ["testng", "test ng"],

        # Version Control
        "Git": ["git", "git version control", "git scm"],
        "GitHub": ["github", "git hub"],
        "GitLab": ["gitlab", "git lab"],
        "Bitbucket": ["bitbucket", "bit bucket"],

        # Methodologies
        "Agile": ["agile", "agile methodology", "agile development"],
        "Scrum": ["scrum", "scrum methodology"],
        "Kanban": ["kanban", "kanban board"],
        "CI/CD": ["ci/cd", "ci cd", "continuous integration", "continuous deployment"],
        "TDD": ["tdd", "test driven development", "test-driven development"],
        "Microservices": ["microservices", "micro services", "microservice architecture"],

        # Data Science & ML
        "TensorFlow": ["tensorflow", "tensor flow", "tf"],
        "PyTorch": ["pytorch", "torch"],
        "Pandas": ["pandas", "pandas library"],
        "NumPy": ["numpy", "numerical python"],
        "scikit-learn": ["scikit-learn", "sklearn", "scikit learn"],
    }

    return synonyms


def save_synonym_database(synonyms, output_path):
    """Save synonym database to JSON file."""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(synonyms, f, indent=2, ensure_ascii=False)

    return output_path


def main():
    """Main execution function."""
    print("Building synonym database...")

    # Build synonyms
    synonyms = build_synonym_database()

    # Calculate statistics
    primary_terms = len(synonyms)
    total_variations = sum(len(variations) for variations in synonyms.values())

    # Save to file
    output_path = Path(__file__).parent.parent / "data" / "synonyms" / "skill_synonyms.json"
    save_synonym_database(synonyms, output_path)

    # Report success
    print(f"✓ Built synonym database with {primary_terms} primary terms")
    print(f"✓ Saved to {output_path}")
    print(f"✓ Total variations: {total_variations}")

    return 0


if __name__ == "__main__":
    exit(main())
