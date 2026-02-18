"""
Merge O*NET, LinkedIn, and existing role_taxonomy.py into comprehensive role_keywords.json.
Expands from 7 keywords per role/level to 50-100.
"""

import json
import re
from pathlib import Path
from collections import defaultdict

# Experience levels
EXPERIENCE_LEVELS = ["entry", "mid", "senior", "lead", "executive"]

# All 22 roles
ALL_ROLES = [
    "software_engineer", "data_scientist", "devops_engineer",
    "product_manager", "technical_product_manager",
    "ux_designer", "ui_designer", "product_designer",
    "marketing_manager", "sales_manager", "business_analyst",
    "operations_manager", "financial_analyst", "accountant",
    "hr_manager", "recruiter", "customer_success_manager",
    "corporate_lawyer", "content_writer",
    "qa_engineer", "data_engineer", "project_manager"
]

# Fallback roles for roles without external data
ROLE_FALLBACKS = {
    "technical_product_manager": "product_manager",
    "ui_designer": "ux_designer",
    "product_designer": "ux_designer"
}


def load_existing_taxonomy():
    """Extract keywords from existing role_taxonomy.py"""
    taxonomy_path = Path(__file__).parent.parent / "services" / "role_taxonomy.py"

    with open(taxonomy_path, 'r') as f:
        content = f.read()

    # Extract typical_keywords dict from ROLE_DEFINITIONS
    keywords_by_role_level = defaultdict(lambda: defaultdict(list))

    # Split content into role blocks
    # Pattern: find "role_id": { ... } blocks
    role_blocks = re.finditer(
        r'"(\w+)":\s*\{[^}]*?"typical_keywords":\s*\{(.*?)\},\s*"action_verbs":',
        content,
        re.DOTALL
    )

    for match in role_blocks:
        role_id = match.group(1)
        typical_keywords_section = match.group(2)

        # Extract each level's keywords
        level_pattern = r'ExperienceLevel\.(\w+):\s*\[(.*?)\]'
        for level_match in re.finditer(level_pattern, typical_keywords_section):
            level = level_match.group(1).lower()
            keywords_str = level_match.group(2)

            # Extract quoted keywords
            keywords = re.findall(r'"([^"]+)"', keywords_str)
            keywords_by_role_level[role_id][level] = [kw.lower() for kw in keywords]

    return keywords_by_role_level


def merge_keyword_sources():
    """Combine O*NET, LinkedIn, and existing taxonomy into final database"""

    print("Merging keyword sources...")

    # Load all sources
    data_dir = Path(__file__).parent.parent / "data" / "keywords"

    with open(data_dir / "onet_skills.json", 'r') as f:
        onet_data = json.load(f)

    with open(data_dir / "linkedin_skills.json", 'r') as f:
        linkedin_data = json.load(f)

    existing_keywords = load_existing_taxonomy()

    # Merge per role/level
    merged = {}

    for role_id in ALL_ROLES:
        for level in EXPERIENCE_LEVELS:
            keywords = set()

            # Determine which role to use for external data (use fallback if needed)
            data_role = ROLE_FALLBACKS.get(role_id, role_id)

            # Add O*NET core skills (if available)
            if data_role in onet_data:
                # Add core skills
                core_skills = onet_data[data_role].get('core_skills', [])
                keywords.update([skill.lower() for skill in core_skills])

                # Add knowledge areas
                knowledge_areas = onet_data[data_role].get('knowledge_areas', [])
                keywords.update([area.lower() for area in knowledge_areas])

            # Add LinkedIn trending skills (if available)
            if data_role in linkedin_data:
                trending_skills = linkedin_data[data_role].get('trending_skills', [])
                keywords.update([skill.lower() for skill in trending_skills])

            # Add existing custom keywords from taxonomy (use actual role_id, not fallback)
            if role_id in existing_keywords and level in existing_keywords[role_id]:
                keywords.update([kw.lower() for kw in existing_keywords[role_id][level]])

            # Add level-specific variations
            if level == "entry":
                keywords.update(["learning", "training", "mentorship", "junior", "intern", "graduate"])
            elif level in ["senior", "lead", "executive"]:
                keywords.update(["leadership", "strategy", "architecture", "mentoring", "team management"])

            # Convert to sorted list
            merged[f"{role_id}_{level}"] = sorted(list(keywords))

    # Save final merged data
    output_path = data_dir / "role_keywords.json"

    with open(output_path, 'w') as f:
        json.dump(merged, f, indent=2)

    # Print statistics
    print("\n✓ Keyword Merge Complete")
    print(f"✓ Saved to {output_path}")
    print("\nKeyword counts per role/level:")

    keyword_counts = []
    for role_level, keywords in sorted(merged.items()):
        count = len(keywords)
        keyword_counts.append(count)
        print(f"  {role_level:40} {count:3} keywords")

    total_keywords = sum(keyword_counts)
    avg_keywords = total_keywords / len(merged)
    min_keywords = min(keyword_counts)
    max_keywords = max(keyword_counts)

    print(f"\n✓ Total role/level combinations: {len(merged)}")
    print(f"✓ Total keywords: {total_keywords}")
    print(f"✓ Average per role/level: {avg_keywords:.1f}")
    print(f"✓ Min keywords: {min_keywords}")
    print(f"✓ Max keywords: {max_keywords}")
    print(f"✓ Target range: 50-100 keywords per role/level")

    # Check if target achieved
    below_50 = sum(1 for count in keyword_counts if count < 50)
    if below_50 > 0:
        print(f"⚠ Warning: {below_50} role/level combinations have <50 keywords")
    else:
        print("✓ Target achieved: All role/level combinations have 50+ keywords")

    return output_path


if __name__ == "__main__":
    merge_keyword_sources()
