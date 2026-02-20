#!/usr/bin/env python3
"""
Build corpus database from raw corpus files.

This script:
1. Extracts skills from skills_it.txt
2. Extracts role mappings from normlized_classes.txt
3. Generates basic skill synonyms from the corpus
4. Saves everything as JSON files in data/corpus/

Usage:
    python3 scripts/build_corpus_database.py
"""
import json
import logging
import sys
from collections import defaultdict
from pathlib import Path

# Add parent directory to path to import corpus_parser
sys.path.insert(0, str(Path(__file__).parent))

from corpus_parser import extract_skills_database, extract_role_mappings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def generate_skill_synonyms(skills_db: dict) -> dict:
    """
    Generate basic synonyms from corpus skills.

    This creates simple variations like:
    - javascript -> js
    - c++ -> cpp, cplusplus
    - typescript -> ts

    Args:
        skills_db: Skills database with frequencies

    Returns:
        Dictionary mapping skill -> list of synonyms
    """
    synonyms = {}

    # Common abbreviation patterns
    abbreviation_map = {
        'javascript': ['js'],
        'typescript': ['ts'],
        'c++': ['cpp', 'cplusplus'],
        'c#': ['csharp', 'c-sharp'],
        'node.js': ['nodejs', 'node'],
        'react.js': ['react', 'reactjs'],
        'vue.js': ['vue', 'vuejs'],
        'angular.js': ['angular', 'angularjs'],
        'python': ['py'],
        'postgresql': ['postgres', 'psql'],
        'mongodb': ['mongo'],
        'kubernetes': ['k8s'],
        'docker': ['containerization'],
        'aws': ['amazon web services'],
        'gcp': ['google cloud platform'],
        'azure': ['microsoft azure'],
    }

    # Add predefined mappings
    for skill, skill_synonyms in abbreviation_map.items():
        if skill in skills_db:
            synonyms[skill] = skill_synonyms

    logger.info(f"Generated {len(synonyms)} skill synonym mappings")

    return synonyms


def main():
    """Main execution function."""
    # Define paths
    backend_dir = Path(__file__).parent.parent
    corpus_source_dir = backend_dir / 'data' / 'corpus_source'
    corpus_output_dir = backend_dir / 'data' / 'corpus'

    skills_file = corpus_source_dir / 'skills_it.txt'
    roles_file = corpus_source_dir / 'normlized_classes.txt'

    # Verify input files exist
    if not skills_file.exists():
        logger.error(f"Skills file not found: {skills_file}")
        sys.exit(1)

    if not roles_file.exists():
        logger.error(f"Roles file not found: {roles_file}")
        sys.exit(1)

    # Create output directory if it doesn't exist
    corpus_output_dir.mkdir(parents=True, exist_ok=True)

    logger.info("=" * 60)
    logger.info("BUILDING CORPUS DATABASE")
    logger.info("=" * 60)

    # Step 1: Extract skills database
    logger.info("\n[1/3] Extracting skills database...")
    skills_db = extract_skills_database(skills_file)

    # Save skills database
    skills_output = corpus_output_dir / 'skills_database.json'
    with open(skills_output, 'w', encoding='utf-8') as f:
        json.dump(skills_db, f, indent=2, ensure_ascii=False)

    logger.info(f"Saved {len(skills_db)} skills to {skills_output}")

    # Step 2: Extract role mappings
    logger.info("\n[2/3] Extracting role mappings...")
    role_mappings = extract_role_mappings(roles_file)

    # Save role mappings
    roles_output = corpus_output_dir / 'role_mappings.json'
    with open(roles_output, 'w', encoding='utf-8') as f:
        json.dump(role_mappings, f, indent=2, ensure_ascii=False)

    logger.info(f"Saved {len(role_mappings)} role mappings to {roles_output}")

    # Step 3: Generate skill synonyms
    logger.info("\n[3/3] Generating skill synonyms...")
    skill_synonyms = generate_skill_synonyms(skills_db)

    # Save skill synonyms
    synonyms_output = corpus_output_dir / 'skill_synonyms_corpus.json'
    with open(synonyms_output, 'w', encoding='utf-8') as f:
        json.dump(skill_synonyms, f, indent=2, ensure_ascii=False)

    logger.info(f"Saved {len(skill_synonyms)} synonym mappings to {synonyms_output}")

    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("BUILD COMPLETE")
    logger.info("=" * 60)
    logger.info(f"Skills extracted: {len(skills_db):,}")
    logger.info(f"Role mappings: {len(role_mappings):,}")
    logger.info(f"Synonym mappings: {len(skill_synonyms):,}")
    logger.info(f"\nOutput directory: {corpus_output_dir}")
    logger.info("=" * 60)


if __name__ == '__main__':
    main()
