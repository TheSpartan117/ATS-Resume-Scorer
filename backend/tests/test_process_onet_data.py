"""
Tests for process_onet_data.py script
"""

import json
import pytest
from pathlib import Path
import sys

# Add scripts directory to path
scripts_dir = Path(__file__).parent.parent / "scripts"
sys.path.insert(0, str(scripts_dir))

from process_onet_data import (
    read_onet_file,
    process_onet_to_role_keywords,
    ONET_ROLE_MAPPING
)


class TestOnetRoleMapping:
    """Test O*NET role mappings"""

    def test_mapping_has_21_roles(self):
        """Should have exactly 21 roles defined"""
        assert len(ONET_ROLE_MAPPING) == 21

    def test_all_roles_have_valid_onet_codes(self):
        """All O*NET codes should follow XX-XXXX.XX format"""
        for role_id, onet_code in ONET_ROLE_MAPPING.items():
            assert isinstance(onet_code, str)
            assert len(onet_code) == 10  # e.g., "15-1252.00"
            assert onet_code[2] == '-'
            assert onet_code[7] == '.'

    def test_expected_roles_exist(self):
        """Should include key roles from requirements"""
        expected_roles = [
            "software_engineer",
            "data_scientist",
            "devops_engineer",
            "product_manager",
            "ux_designer",
            "marketing_manager",
            "qa_engineer",
            "data_engineer"
        ]
        for role in expected_roles:
            assert role in ONET_ROLE_MAPPING


class TestReadOnetFile:
    """Test O*NET file reading"""

    def test_reads_skills_file(self):
        """Should successfully read Skills.txt file"""
        data = read_onet_file("Skills.txt")
        assert isinstance(data, list)
        assert len(data) > 0

    def test_reads_knowledge_file(self):
        """Should successfully read Knowledge.txt file"""
        data = read_onet_file("Knowledge.txt")
        assert isinstance(data, list)
        assert len(data) > 0

    def test_file_has_expected_columns(self):
        """Data should have required O*NET columns"""
        data = read_onet_file("Skills.txt")
        first_row = data[0]
        assert 'O*NET-SOC Code' in first_row
        assert 'Element Name' in first_row

    def test_finds_software_developer_code(self):
        """Should find data for Computer Programmers (15-1251.00)"""
        skills_data = read_onet_file("Skills.txt")
        swe_code = ONET_ROLE_MAPPING["software_engineer"]

        swe_skills = [row for row in skills_data if row.get('O*NET-SOC Code') == swe_code]
        assert len(swe_skills) > 0, f"No skills found for {swe_code}"


class TestProcessOnetToRoleKeywords:
    """Test O*NET data processing"""

    def test_creates_output_file(self):
        """Should create onet_skills.json file"""
        output_path = process_onet_to_role_keywords()
        assert output_path.exists()

    def test_output_has_all_roles(self):
        """Output should contain all 21 roles"""
        output_path = Path(__file__).parent.parent / "data" / "keywords" / "onet_skills.json"

        with open(output_path, 'r') as f:
            data = json.load(f)

        assert len(data) == 21

        for role_id in ONET_ROLE_MAPPING.keys():
            assert role_id in data

    def test_role_structure_is_valid(self):
        """Each role should have required fields"""
        output_path = Path(__file__).parent.parent / "data" / "keywords" / "onet_skills.json"

        with open(output_path, 'r') as f:
            data = json.load(f)

        for role_id, role_data in data.items():
            assert "onet_code" in role_data
            assert "core_skills" in role_data
            assert "knowledge_areas" in role_data
            assert "total_keywords" in role_data

            assert isinstance(role_data["core_skills"], list)
            assert isinstance(role_data["knowledge_areas"], list)
            assert isinstance(role_data["total_keywords"], int)

    def test_software_engineer_has_skills(self):
        """Software engineer role should have skills and knowledge"""
        output_path = Path(__file__).parent.parent / "data" / "keywords" / "onet_skills.json"

        with open(output_path, 'r') as f:
            data = json.load(f)

        swe_data = data["software_engineer"]

        assert swe_data["onet_code"] == "15-1251.00"
        assert len(swe_data["core_skills"]) > 0
        assert len(swe_data["knowledge_areas"]) > 0
        assert swe_data["total_keywords"] == len(swe_data["core_skills"]) + len(swe_data["knowledge_areas"])

    def test_skills_are_lowercase(self):
        """All skills should be lowercase"""
        output_path = Path(__file__).parent.parent / "data" / "keywords" / "onet_skills.json"

        with open(output_path, 'r') as f:
            data = json.load(f)

        for role_id, role_data in data.items():
            for skill in role_data["core_skills"]:
                assert skill == skill.lower(), f"Skill '{skill}' in {role_id} is not lowercase"

            for knowledge in role_data["knowledge_areas"]:
                assert knowledge == knowledge.lower(), f"Knowledge '{knowledge}' in {role_id} is not lowercase"

    def test_total_keywords_is_accurate(self):
        """total_keywords should equal sum of skills and knowledge"""
        output_path = Path(__file__).parent.parent / "data" / "keywords" / "onet_skills.json"

        with open(output_path, 'r') as f:
            data = json.load(f)

        for role_id, role_data in data.items():
            expected_total = len(role_data["core_skills"]) + len(role_data["knowledge_areas"])
            assert role_data["total_keywords"] == expected_total

    def test_onet_provides_baseline_keywords(self):
        """O*NET provides standardized baseline skills and knowledge for all roles"""
        output_path = Path(__file__).parent.parent / "data" / "keywords" / "onet_skills.json"

        with open(output_path, 'r') as f:
            data = json.load(f)

        # O*NET uses standardized 35 skills and 33 knowledge areas across all occupations
        # This provides a baseline that will be augmented with LinkedIn skills for differentiation
        for role_id, role_data in data.items():
            # All roles should have the standard O*NET skill set
            assert len(role_data["core_skills"]) == 35, f"{role_id} should have 35 O*NET skills"
            assert len(role_data["knowledge_areas"]) == 33, f"{role_id} should have 33 O*NET knowledge areas"

            # Verify they contain expected baseline skills
            skills_str = " ".join(role_data["core_skills"])
            assert "critical thinking" in skills_str
            assert "active learning" in skills_str

    def test_common_technical_skills_in_tech_roles(self):
        """Tech roles should have programming-related skills"""
        output_path = Path(__file__).parent.parent / "data" / "keywords" / "onet_skills.json"

        with open(output_path, 'r') as f:
            data = json.load(f)

        tech_roles = ["software_engineer", "data_scientist", "data_engineer"]

        for role in tech_roles:
            all_keywords = data[role]["core_skills"] + data[role]["knowledge_areas"]
            all_keywords_str = " ".join(all_keywords).lower()

            # Should have some programming/computer-related terms
            has_tech_keyword = any(term in all_keywords_str for term in
                                   ["programming", "computer", "software", "mathematics", "analysis"])
            assert has_tech_keyword, f"{role} should have technical keywords"

    def test_no_empty_skill_lists(self):
        """No role should have empty skills or knowledge"""
        output_path = Path(__file__).parent.parent / "data" / "keywords" / "onet_skills.json"

        with open(output_path, 'r') as f:
            data = json.load(f)

        for role_id, role_data in data.items():
            assert len(role_data["core_skills"]) > 0, f"{role_id} has no core_skills"
            assert len(role_data["knowledge_areas"]) > 0, f"{role_id} has no knowledge_areas"


class TestDataQuality:
    """Test data quality and consistency"""

    def test_output_is_valid_json(self):
        """Output file should be valid JSON"""
        output_path = Path(__file__).parent.parent / "data" / "keywords" / "onet_skills.json"

        with open(output_path, 'r') as f:
            data = json.load(f)

        assert isinstance(data, dict)

    def test_no_duplicate_skills_within_role(self):
        """Each role should not have duplicate skills"""
        output_path = Path(__file__).parent.parent / "data" / "keywords" / "onet_skills.json"

        with open(output_path, 'r') as f:
            data = json.load(f)

        for role_id, role_data in data.items():
            skills = role_data["core_skills"]
            assert len(skills) == len(set(skills)), f"{role_id} has duplicate skills"

            knowledge = role_data["knowledge_areas"]
            assert len(knowledge) == len(set(knowledge)), f"{role_id} has duplicate knowledge"

    def test_designer_roles_share_same_code(self):
        """UX, UI, and Product Designer should share the same O*NET code"""
        output_path = Path(__file__).parent.parent / "data" / "keywords" / "onet_skills.json"

        with open(output_path, 'r') as f:
            data = json.load(f)

        ux_code = data["ux_designer"]["onet_code"]
        ui_code = data["ui_designer"]["onet_code"]
        pd_code = data["product_designer"]["onet_code"]

        assert ux_code == ui_code == pd_code == "27-1024.00"
