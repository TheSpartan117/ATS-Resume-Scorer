"""
Process O*NET bulk data files into role-specific keyword lists.
Maps O*NET occupation codes to our role taxonomy.
"""

import json
import csv
from pathlib import Path
from collections import defaultdict

# O*NET code mappings to our roles
# Note: Using codes that have detailed skills/knowledge data in O*NET database
ONET_ROLE_MAPPING = {
    "software_engineer": "15-1251.00",  # Computer Programmers (closest match with data)
    "data_scientist": "15-2051.01",     # Business Intelligence Analysts (Data Scientists variant)
    "devops_engineer": "15-1244.00",    # Network and Computer Systems Administrators
    "product_manager": "11-3021.00",    # Computer and Information Systems Managers
    "ux_designer": "27-1024.00",        # Graphic Designers
    "ui_designer": "27-1024.00",        # Graphic Designers
    "product_designer": "27-1024.00",   # Graphic Designers
    "marketing_manager": "11-2021.00",  # Marketing Managers
    "sales_manager": "11-2022.00",      # Sales Managers
    "business_analyst": "13-1111.00",   # Management Analysts
    "operations_manager": "11-1021.00", # General and Operations Managers
    "financial_analyst": "13-2052.00",  # Personal Financial Advisors (closest match with data)
    "accountant": "13-2011.00",         # Accountants and Auditors
    "hr_manager": "11-3121.00",         # Human Resources Managers
    "recruiter": "13-1071.00",          # Human Resources Specialists
    "customer_success_manager": "11-2022.00",  # Sales Managers (customer-facing)
    "corporate_lawyer": "23-1011.00",   # Lawyers
    "content_writer": "27-3043.00",     # Writers and Authors
    "qa_engineer": "15-1253.00",        # Software Quality Assurance Analysts
    "data_engineer": "15-1243.00",      # Database Architects
    "project_manager": "15-1299.09",    # Information Technology Project Managers
}

def read_onet_file(filename):
    """Read O*NET tab-separated file"""
    data_dir = Path(__file__).parent.parent / "data" / "onet_raw"
    file_path = data_dir / filename

    rows = []
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            rows.append(row)

    return rows

def process_onet_to_role_keywords():
    """Extract skills and knowledge for each role from O*NET data"""

    print("Processing O*NET data...")

    # Read O*NET files
    skills_data = read_onet_file("Skills.txt")
    knowledge_data = read_onet_file("Knowledge.txt")

    keywords_by_role = {}

    for role_id, onet_code in ONET_ROLE_MAPPING.items():
        print(f"Processing {role_id} (O*NET: {onet_code})...")

        # Extract skills for this occupation
        role_skills = []
        seen_skills = set()
        for row in skills_data:
            if row.get('O*NET-SOC Code') == onet_code:
                skill_name = row.get('Element Name', '').strip().lower()
                if skill_name and skill_name not in seen_skills:
                    role_skills.append(skill_name)
                    seen_skills.add(skill_name)

        # Extract knowledge areas
        role_knowledge = []
        seen_knowledge = set()
        for row in knowledge_data:
            if row.get('O*NET-SOC Code') == onet_code:
                knowledge_name = row.get('Element Name', '').strip().lower()
                if knowledge_name and knowledge_name not in seen_knowledge:
                    role_knowledge.append(knowledge_name)
                    seen_knowledge.add(knowledge_name)

        keywords_by_role[role_id] = {
            "onet_code": onet_code,
            "core_skills": role_skills,
            "knowledge_areas": role_knowledge,
            "total_keywords": len(role_skills) + len(role_knowledge)
        }

        print(f"  ✓ {len(role_skills)} skills, {len(role_knowledge)} knowledge areas")

    # Save to JSON
    output_path = Path(__file__).parent.parent / "data" / "keywords" / "onet_skills.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w') as f:
        json.dump(keywords_by_role, f, indent=2)

    print(f"\n✓ Processed {len(keywords_by_role)} roles from O*NET")
    print(f"✓ Saved to {output_path}")

    return output_path

if __name__ == "__main__":
    process_onet_to_role_keywords()
