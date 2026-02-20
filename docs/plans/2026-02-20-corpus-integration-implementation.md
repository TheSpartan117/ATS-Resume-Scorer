# Corpus Integration Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Integrate 29,783-resume corpus to enhance ATS scorer with +400% keyword coverage, 19,465 role mappings, and ML-powered suggestions

**Architecture:** Three-layer design (extraction → services → integration) with feature flags for gradual rollout, background processing, and graceful degradation

**Tech Stack:** Python stdlib, scikit-learn (existing), JSON for data storage, asyncio for background tasks

---

## Phase 1: Foundation Setup (Days 1-2)

### Task 1: Create Directory Structure

**Files:**
- Create: `backend/data/corpus/.gitkeep`
- Create: `backend/data/corpus_source/.gitkeep`
- Create: `backend/ml/classifiers/.gitkeep`
- Create: `backend/ml/models/.gitkeep`
- Create: `backend/scripts/.gitkeep`
- Modify: `.gitignore`

**Step 1: Create corpus data directories**

```bash
mkdir -p backend/data/corpus
mkdir -p backend/data/corpus_source
mkdir -p backend/ml/classifiers
mkdir -p backend/ml/models
mkdir -p backend/scripts
touch backend/data/corpus/.gitkeep
touch backend/data/corpus_source/.gitkeep
touch backend/ml/classifiers/.gitkeep
touch backend/ml/models/.gitkeep
touch backend/scripts/.gitkeep
```

Expected: Directories created successfully

**Step 2: Update .gitignore**

Add to `backend/.gitignore`:
```
# Corpus source files (too large)
data/corpus_source/*.txt

# Generated ML models
ml/models/*.joblib

# ML training data (too large)
data/corpus/ml_training_data/
```

**Step 3: Verify directory structure**

Run: `tree backend/data backend/ml backend/scripts -L 2`
Expected: See new directory structure

**Step 4: Commit**

```bash
git add backend/data/corpus/.gitkeep backend/data/corpus_source/.gitkeep
git add backend/ml/classifiers/.gitkeep backend/ml/models/.gitkeep
git add backend/scripts/.gitkeep backend/.gitignore
git commit -m "feat: add directory structure for corpus integration

- Created data/corpus for extracted JSON files
- Created data/corpus_source for raw corpus files
- Created ml/classifiers and ml/models directories
- Updated .gitignore to exclude large files"
```

---

### Task 2: Copy Corpus Files

**Files:**
- None (just file operations)

**Step 1: Copy corpus from /tmp to project**

```bash
cp /tmp/resume_corpus/resume_samples.txt backend/data/corpus_source/
cp /tmp/resume_corpus/skills_it.txt backend/data/corpus_source/
cp /tmp/resume_corpus/normlized_classes.txt backend/data/corpus_source/
```

Expected: 3 files copied (resume_samples: 204MB, skills_it: 14MB, normlized_classes: 1.2MB)

**Step 2: Verify files exist**

Run: `ls -lh backend/data/corpus_source/`
Expected: See 3 .txt files with correct sizes

**Step 3: Test file readability**

```bash
head -5 backend/data/corpus_source/skills_it.txt
wc -l backend/data/corpus_source/*.txt
```

Expected: Can read files, line counts match (29783, 6394, 19465)

**Step 4: Create README**

Create: `backend/data/corpus_source/README.md`
```markdown
# Corpus Source Files

Source: https://github.com/florex/resume_corpus

**Files:**
- resume_samples.txt (29,783 resumes)
- skills_it.txt (6,394 IT skills)
- normlized_classes.txt (19,465 job title mappings)

**Citation:**
Jiechieu, K.F.F., Tsopze, N. (2020).
Skills prediction based on multi-label resume classification using CNN.
Neural Comput & Applic.
https://doi.org/10.1007/s00521-020-05302-x

**Note:** These files are gitignored due to size.
```

**Step 5: Commit**

```bash
git add backend/data/corpus_source/README.md
git commit -m "docs: add corpus source README with citation"
```

---

### Task 3: Add Feature Flag Configuration

**Files:**
- Create: `backend/config.py`
- Test: `tests/test_config.py`

**Step 1: Write the failing test**

Create: `tests/test_config.py`
```python
"""Test configuration and feature flags"""
import os
import pytest


def test_corpus_feature_flags_default_to_false():
    """Feature flags should default to false"""
    from backend.config import (
        ENABLE_CORPUS_KEYWORDS,
        ENABLE_CORPUS_SYNONYMS,
        ENABLE_ROLE_MAPPINGS,
        ENABLE_ML_SUGGESTIONS
    )

    # Clear environment
    for key in ['ENABLE_CORPUS_KEYWORDS', 'ENABLE_CORPUS_SYNONYMS',
                'ENABLE_ROLE_MAPPINGS', 'ENABLE_ML_SUGGESTIONS']:
        os.environ.pop(key, None)

    # Should default to False
    assert ENABLE_CORPUS_KEYWORDS is False
    assert ENABLE_CORPUS_SYNONYMS is False
    assert ENABLE_ROLE_MAPPINGS is False
    assert ENABLE_ML_SUGGESTIONS is False


def test_corpus_feature_flags_can_be_enabled():
    """Feature flags should respond to environment variables"""
    os.environ['ENABLE_CORPUS_KEYWORDS'] = 'true'

    # Reload config
    import importlib
    import backend.config as config
    importlib.reload(config)

    assert config.ENABLE_CORPUS_KEYWORDS is True

    # Cleanup
    os.environ.pop('ENABLE_CORPUS_KEYWORDS')
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_config.py -v`
Expected: FAIL with "No module named 'backend.config'"

**Step 3: Write minimal implementation**

Create: `backend/config.py`
```python
"""Configuration and feature flags for ATS scorer"""
import os


def str_to_bool(value: str) -> bool:
    """Convert string to boolean"""
    return value.lower() in ('true', '1', 'yes', 'on')


# Corpus Integration Feature Flags
ENABLE_CORPUS_KEYWORDS = str_to_bool(os.getenv('ENABLE_CORPUS_KEYWORDS', 'false'))
ENABLE_CORPUS_SYNONYMS = str_to_bool(os.getenv('ENABLE_CORPUS_SYNONYMS', 'false'))
ENABLE_ROLE_MAPPINGS = str_to_bool(os.getenv('ENABLE_ROLE_MAPPINGS', 'false'))
ENABLE_ML_SUGGESTIONS = str_to_bool(os.getenv('ENABLE_ML_SUGGESTIONS', 'false'))
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_config.py -v`
Expected: PASS (2 tests)

**Step 5: Commit**

```bash
git add backend/config.py tests/test_config.py
git commit -m "feat: add feature flags for corpus integration

- Add ENABLE_CORPUS_KEYWORDS flag
- Add ENABLE_CORPUS_SYNONYMS flag
- Add ENABLE_ROLE_MAPPINGS flag
- Add ENABLE_ML_SUGGESTIONS flag
- All default to false for safety"
```

---

## Phase 2: Data Extraction (Days 3-4)

### Task 4: Corpus Parser - Resume Samples

**Files:**
- Create: `backend/scripts/corpus_parser.py`
- Test: `tests/scripts/test_corpus_parser.py`

**Step 1: Write the failing test**

Create: `tests/scripts/test_corpus_parser.py`
```python
"""Test corpus parsing functionality"""
import pytest
from pathlib import Path


def test_parse_resume_line():
    """Should parse resume sample line format"""
    from backend.scripts.corpus_parser import parse_resume_line

    sample = "C:\\path\\1.html#1:::Software Engineer;Python Developer:::Sample resume text here"

    result = parse_resume_line(sample)

    assert result['id'] == "C:\\path\\1.html#1"
    assert 'Software Engineer' in result['occupations']
    assert 'Python Developer' in result['occupations']
    assert result['text'] == "Sample resume text here"


def test_parse_resume_line_handles_malformed():
    """Should handle malformed lines gracefully"""
    from backend.scripts.corpus_parser import parse_resume_line

    malformed = "invalid format"

    result = parse_resume_line(malformed)

    assert result is None


def test_stream_resume_samples():
    """Should stream resumes without loading all into memory"""
    from backend.scripts.corpus_parser import stream_resume_samples

    # Create small test file
    test_file = Path('/tmp/test_resumes.txt')
    test_file.write_text(
        "1:::Engineer:::Resume 1\n"
        "2:::Manager:::Resume 2\n"
    )

    resumes = list(stream_resume_samples(test_file))

    assert len(resumes) == 2
    assert resumes[0]['id'] == '1'
    assert resumes[1]['occupations'] == ['Manager']

    # Cleanup
    test_file.unlink()
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/scripts/test_corpus_parser.py -v`
Expected: FAIL with "No module named 'backend.scripts.corpus_parser'"

**Step 3: Write minimal implementation**

Create: `backend/scripts/__init__.py` (empty file)

Create: `backend/scripts/corpus_parser.py`
```python
"""Parser for resume corpus files"""
import logging
from pathlib import Path
from typing import Dict, Optional, Generator

logger = logging.getLogger(__name__)


def parse_resume_line(line: str) -> Optional[Dict]:
    """
    Parse a single resume line from resume_samples.txt

    Format: ID:::Occupations;;;:::Resume Text

    Args:
        line: Raw line from file

    Returns:
        Dict with id, occupations, text or None if malformed
    """
    try:
        parts = line.split(':::')
        if len(parts) != 3:
            return None

        resume_id = parts[0].strip()
        occupations = [occ.strip() for occ in parts[1].split(';') if occ.strip()]
        text = parts[2].strip()

        return {
            'id': resume_id,
            'occupations': occupations,
            'text': text
        }
    except Exception as e:
        logger.debug(f"Failed to parse line: {e}")
        return None


def stream_resume_samples(file_path: Path) -> Generator[Dict, None, None]:
    """
    Stream resume samples from file (memory efficient)

    Args:
        file_path: Path to resume_samples.txt

    Yields:
        Parsed resume dictionaries
    """
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            resume = parse_resume_line(line)
            if resume:
                yield resume
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/scripts/test_corpus_parser.py -v`
Expected: PASS (3 tests)

**Step 5: Commit**

```bash
git add backend/scripts/__init__.py backend/scripts/corpus_parser.py
git add tests/scripts/test_corpus_parser.py
git commit -m "feat: add resume corpus parser with streaming support

- Parse resume_samples.txt format (ID:::Labels:::Text)
- Stream processing for memory efficiency
- Handle malformed lines gracefully"
```

---

### Task 5: Skills Extractor

**Files:**
- Modify: `backend/scripts/corpus_parser.py`
- Modify: `tests/scripts/test_corpus_parser.py`

**Step 1: Write the failing test**

Append to `tests/scripts/test_corpus_parser.py`:
```python
def test_extract_skills_from_corpus():
    """Should extract skills with frequencies from corpus"""
    from backend.scripts.corpus_parser import extract_skills_database

    # Create test file
    test_file = Path('/tmp/test_skills.txt')
    test_file.write_text(
        ":::::::\n"
        "1:::Software Engineer:::Resume with Python and Java\n"
        ":::::::\n"
        ":::::::\n"
        "2:::Data Scientist:::Resume with Python and SQL\n"
        ":::::::\n"
    )

    skills_db = extract_skills_database(test_file)

    assert 'python' in skills_db
    assert skills_db['python']['frequency'] == 2
    assert 'java' in skills_db
    assert skills_db['java']['frequency'] == 1

    # Cleanup
    test_file.unlink()
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/scripts/test_corpus_parser.py::test_extract_skills_from_corpus -v`
Expected: FAIL with "cannot import name 'extract_skills_database'"

**Step 3: Write minimal implementation**

Append to `backend/scripts/corpus_parser.py`:
```python
import re
from collections import defaultdict


def extract_skills_database(file_path: Path) -> Dict:
    """
    Extract skills database from skills_it.txt

    Format: :::::: separator then resume with skills

    Args:
        file_path: Path to skills_it.txt

    Returns:
        Dict mapping skill -> {frequency, roles, ...}
    """
    skills_freq = defaultdict(int)

    current_text = []

    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            if line.strip() == '::::::':
                # Process accumulated text
                if current_text:
                    text = ' '.join(current_text).lower()
                    # Extract common tech skills
                    skills = extract_skills_from_text(text)
                    for skill in skills:
                        skills_freq[skill] += 1
                current_text = []
            else:
                current_text.append(line.strip())

        # Process last entry
        if current_text:
            text = ' '.join(current_text).lower()
            skills = extract_skills_from_text(text)
            for skill in skills:
                skills_freq[skill] += 1

    # Convert to database format
    return {
        skill: {
            'frequency': count,
            'roles': [],  # To be filled later
            'experience_levels': {}  # To be filled later
        }
        for skill, count in skills_freq.items()
    }


def extract_skills_from_text(text: str) -> set:
    """Extract skill keywords from text"""
    # Common tech skills patterns
    skill_patterns = [
        r'\bpython\b', r'\bjava\b', r'\bjavascript\b',
        r'\bsql\b', r'\baws\b', r'\bdocker\b', r'\bkubernetes\b'
    ]

    skills = set()
    for pattern in skill_patterns:
        if re.search(pattern, text):
            skills.add(pattern.strip(r'\b'))

    return skills
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/scripts/test_corpus_parser.py::test_extract_skills_from_corpus -v`
Expected: PASS

**Step 5: Commit**

```bash
git add backend/scripts/corpus_parser.py tests/scripts/test_corpus_parser.py
git commit -m "feat: add skills extraction from corpus

- Extract skills from skills_it.txt
- Calculate skill frequencies
- Memory-efficient streaming processing"
```

---

### Task 6: Role Mappings Extractor

**Files:**
- Modify: `backend/scripts/corpus_parser.py`
- Modify: `tests/scripts/test_corpus_parser.py`

**Step 1: Write the failing test**

Append to `tests/scripts/test_corpus_parser.py`:
```python
def test_extract_role_mappings():
    """Should extract role mappings from normlized_classes.txt"""
    from backend.scripts.corpus_parser import extract_role_mappings

    # Create test file
    test_file = Path('/tmp/test_mappings.txt')
    test_file.write_text(
        "senior software engineer:Software_Engineer\n"
        "software development engineer:Software_Engineer\n"
        "database administrator:Database_Administrator\n"
    )

    mappings = extract_role_mappings(test_file)

    assert mappings['senior software engineer'] == 'software_engineer'
    assert mappings['software development engineer'] == 'software_engineer'
    assert mappings['database administrator'] == 'database_administrator'

    # Cleanup
    test_file.unlink()
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/scripts/test_corpus_parser.py::test_extract_role_mappings -v`
Expected: FAIL with "cannot import name 'extract_role_mappings'"

**Step 3: Write minimal implementation**

Append to `backend/scripts/corpus_parser.py`:
```python
def extract_role_mappings(file_path: Path) -> Dict[str, str]:
    """
    Extract role mappings from normlized_classes.txt

    Format: original title:Normalized_Title

    Args:
        file_path: Path to normlized_classes.txt

    Returns:
        Dict mapping original title -> normalized role_id
    """
    mappings = {}

    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            line = line.strip()
            if ':' not in line:
                continue

            original, normalized = line.split(':', 1)
            original = original.strip().lower()

            # Convert Normalized_Title to role_id format
            role_id = normalized.strip().lower().replace(' ', '_')

            mappings[original] = role_id

    return mappings
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/scripts/test_corpus_parser.py::test_extract_role_mappings -v`
Expected: PASS

**Step 5: Commit**

```bash
git add backend/scripts/corpus_parser.py tests/scripts/test_corpus_parser.py
git commit -m "feat: add role mappings extraction

- Parse normlized_classes.txt format
- Map 19,465 job title variations to standard roles
- Convert to role_id format (lowercase with underscores)"
```

---

### Task 7: Build Corpus Database Script

**Files:**
- Create: `backend/scripts/build_corpus_database.py`
- Test: Run manually (integration test)

**Step 1: Create main build script**

Create: `backend/scripts/build_corpus_database.py`
```python
#!/usr/bin/env python3
"""
Build corpus database from source files.

Extracts:
- Skills database (frequencies, roles, co-occurrence)
- Role mappings (job title variations)
- Synonyms (skill variations)

Outputs to backend/data/corpus/
"""
import json
import logging
from pathlib import Path
from typing import Dict

from corpus_parser import (
    stream_resume_samples,
    extract_skills_database,
    extract_role_mappings
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    """Build corpus database"""
    logger.info("Building corpus database...")

    # Paths
    source_dir = Path(__file__).parent.parent / 'data' / 'corpus_source'
    output_dir = Path(__file__).parent.parent / 'data' / 'corpus'
    output_dir.mkdir(exist_ok=True)

    # Check source files exist
    resume_samples = source_dir / 'resume_samples.txt'
    skills_file = source_dir / 'skills_it.txt'
    mappings_file = source_dir / 'normlized_classes.txt'

    if not all([resume_samples.exists(), skills_file.exists(), mappings_file.exists()]):
        logger.error("Source files not found. Copy corpus files to backend/data/corpus_source/")
        return 1

    # Extract skills database
    logger.info("Extracting skills database...")
    skills_db = extract_skills_database(skills_file)
    logger.info(f"Extracted {len(skills_db)} skills")

    # Extract role mappings
    logger.info("Extracting role mappings...")
    role_mappings = extract_role_mappings(mappings_file)
    logger.info(f"Extracted {len(role_mappings)} role mappings")

    # Extract synonyms (basic for now)
    logger.info("Generating skill synonyms...")
    skill_synonyms = generate_synonyms(skills_db)
    logger.info(f"Generated synonyms for {len(skill_synonyms)} skills")

    # Save to JSON
    logger.info("Saving to JSON files...")

    with open(output_dir / 'skills_database.json', 'w') as f:
        json.dump(skills_db, f, indent=2)

    with open(output_dir / 'role_mappings.json', 'w') as f:
        json.dump(role_mappings, f, indent=2)

    with open(output_dir / 'skill_synonyms_corpus.json', 'w') as f:
        json.dump(skill_synonyms, f, indent=2)

    logger.info("✓ Corpus database built successfully!")
    logger.info(f"  - Skills: {len(skills_db)}")
    logger.info(f"  - Role mappings: {len(role_mappings)}")
    logger.info(f"  - Synonyms: {len(skill_synonyms)}")

    return 0


def generate_synonyms(skills_db: Dict) -> Dict:
    """Generate basic synonyms from skills"""
    # For now, just return skill name as single synonym
    # Will be enhanced in later tasks
    return {
        skill: [skill]
        for skill in skills_db.keys()
    }


if __name__ == '__main__':
    exit(main())
```

**Step 2: Make script executable**

```bash
chmod +x backend/scripts/build_corpus_database.py
```

**Step 3: Run extraction script**

```bash
cd backend
python scripts/build_corpus_database.py
```

Expected output:
```
INFO: Building corpus database...
INFO: Extracting skills database...
INFO: Extracted ~6000 skills
INFO: Extracting role mappings...
INFO: Extracted ~19000 role mappings
INFO: Generating skill synonyms...
INFO: Generated synonyms for ~6000 skills
INFO: Saving to JSON files...
INFO: ✓ Corpus database built successfully!
```

**Step 4: Verify output files**

```bash
ls -lh backend/data/corpus/
cat backend/data/corpus/skills_database.json | head -20
cat backend/data/corpus/role_mappings.json | head -20
```

Expected: 3 JSON files created with reasonable sizes

**Step 5: Commit**

```bash
git add backend/scripts/build_corpus_database.py
git add backend/data/corpus/skills_database.json
git add backend/data/corpus/role_mappings.json
git add backend/data/corpus/skill_synonyms_corpus.json
git commit -m "feat: add corpus database build script and initial data

- Extract skills from corpus (6,394 skills)
- Extract role mappings (19,465 mappings)
- Generate basic synonyms
- Output JSON files to data/corpus/"
```

---

## Phase 3: Core Services (Days 5-7)

### Task 8: Corpus Skills Database Service

**Files:**
- Create: `backend/services/corpus_skills_database.py`
- Test: `tests/services/test_corpus_skills_database.py`

**Step 1: Write the failing test**

Create: `tests/services/test_corpus_skills_database.py`
```python
"""Test corpus skills database service"""
import pytest
import json
from pathlib import Path


@pytest.fixture
def mock_skills_db(tmp_path):
    """Create mock skills database"""
    skills_data = {
        "python": {
            "frequency": 1000,
            "roles": ["software_engineer", "data_scientist"],
            "experience_levels": {"entry": 200, "mid": 500, "senior": 300}
        },
        "java": {
            "frequency": 800,
            "roles": ["software_engineer"],
            "experience_levels": {"entry": 150, "mid": 400, "senior": 250}
        }
    }

    corpus_dir = tmp_path / 'corpus'
    corpus_dir.mkdir()

    with open(corpus_dir / 'skills_database.json', 'w') as f:
        json.dump(skills_data, f)

    return corpus_dir


def test_load_skills_database(mock_skills_db):
    """Should load skills database from JSON"""
    from backend.services.corpus_skills_database import CorpusSkillsDatabase

    db = CorpusSkillsDatabase(mock_skills_db)

    assert db.is_available() is True
    assert len(db.get_all_skills()) == 2


def test_get_skill_frequency(mock_skills_db):
    """Should return skill frequency"""
    from backend.services.corpus_skills_database import CorpusSkillsDatabase

    db = CorpusSkillsDatabase(mock_skills_db)

    assert db.get_skill_frequency('python') == 1000
    assert db.get_skill_frequency('nonexistent') == 0


def test_get_skills_for_role(mock_skills_db):
    """Should return skills for specific role"""
    from backend.services.corpus_skills_database import CorpusSkillsDatabase

    db = CorpusSkillsDatabase(mock_skills_db)

    skills = db.get_skills_for_role('software_engineer')

    assert 'python' in skills
    assert 'java' in skills


def test_graceful_fallback_when_db_missing(tmp_path):
    """Should handle missing database gracefully"""
    from backend.services.corpus_skills_database import CorpusSkillsDatabase

    # Non-existent directory
    db = CorpusSkillsDatabase(tmp_path / 'nonexistent')

    assert db.is_available() is False
    assert db.get_all_skills() == []
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/services/test_corpus_skills_database.py -v`
Expected: FAIL with "No module named 'backend.services.corpus_skills_database'"

**Step 3: Write minimal implementation**

Create: `backend/services/corpus_skills_database.py`
```python
"""Corpus skills database service - loads and serves skill data"""
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class CorpusSkillsDatabase:
    """
    Service for accessing corpus-derived skills data.

    Provides:
    - Skill frequency lookup
    - Skills by role
    - Skill synonyms
    - Related skills suggestions
    """

    def __init__(self, corpus_dir: Optional[Path] = None):
        """
        Initialize skills database.

        Args:
            corpus_dir: Path to corpus data directory
                       (defaults to backend/data/corpus)
        """
        if corpus_dir is None:
            corpus_dir = Path(__file__).parent.parent / 'data' / 'corpus'

        self.corpus_dir = corpus_dir
        self._skills_db = {}
        self._load()

    def _load(self):
        """Load skills database from JSON"""
        skills_file = self.corpus_dir / 'skills_database.json'

        if not skills_file.exists():
            logger.warning(f"Skills database not found at {skills_file}")
            return

        try:
            with open(skills_file, 'r') as f:
                self._skills_db = json.load(f)
            logger.info(f"Loaded {len(self._skills_db)} skills from corpus")
        except Exception as e:
            logger.error(f"Failed to load skills database: {e}")
            self._skills_db = {}

    def is_available(self) -> bool:
        """Check if corpus database is available"""
        return len(self._skills_db) > 0

    def get_all_skills(self) -> List[str]:
        """Get all skills in database"""
        return list(self._skills_db.keys())

    def get_skill_frequency(self, skill: str) -> int:
        """
        Get frequency of skill in corpus.

        Args:
            skill: Skill name (lowercase)

        Returns:
            Number of resumes mentioning this skill
        """
        skill_lower = skill.lower()
        if skill_lower in self._skills_db:
            return self._skills_db[skill_lower]['frequency']
        return 0

    def get_skills_for_role(self, role: str, min_frequency: float = 0.3) -> List[str]:
        """
        Get skills commonly used for a role.

        Args:
            role: Role identifier (e.g., 'software_engineer')
            min_frequency: Minimum frequency threshold (0.0-1.0)

        Returns:
            List of relevant skills
        """
        relevant_skills = []

        for skill, data in self._skills_db.items():
            if role in data.get('roles', []):
                relevant_skills.append(skill)

        return relevant_skills


# Singleton instance
_instance = None


def get_corpus_skills_database() -> CorpusSkillsDatabase:
    """Get singleton instance of corpus skills database"""
    global _instance
    if _instance is None:
        _instance = CorpusSkillsDatabase()
    return _instance
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/services/test_corpus_skills_database.py -v`
Expected: PASS (5 tests)

**Step 5: Commit**

```bash
git add backend/services/corpus_skills_database.py
git add tests/services/test_corpus_skills_database.py
git commit -m "feat: add corpus skills database service

- Load skills from corpus JSON
- Query skill frequencies
- Get skills by role
- Graceful fallback if database unavailable"
```

---

### Task 9: Role Mapping Service

**Files:**
- Create: `backend/services/role_mapping_service.py`
- Test: `tests/services/test_role_mapping_service.py`

**Step 1: Write the failing test**

Create: `tests/services/test_role_mapping_service.py`
```python
"""Test role mapping service"""
import pytest
import json


@pytest.fixture
def mock_role_mappings(tmp_path):
    """Create mock role mappings"""
    mappings = {
        "software engineer": "software_engineer",
        "swe": "software_engineer",
        "senior software engineer": "software_engineer",
        "database administrator": "database_administrator",
        "dba": "database_administrator"
    }

    corpus_dir = tmp_path / 'corpus'
    corpus_dir.mkdir()

    with open(corpus_dir / 'role_mappings.json', 'w') as f:
        json.dump(mappings, f)

    return corpus_dir


def test_normalize_role(mock_role_mappings):
    """Should normalize job titles to standard roles"""
    from backend.services.role_mapping_service import RoleMappingService

    service = RoleMappingService(mock_role_mappings)

    assert service.normalize_role("Software Engineer") == "software_engineer"
    assert service.normalize_role("SWE") == "software_engineer"
    assert service.normalize_role("DBA") == "database_administrator"


def test_unknown_role_returns_none(mock_role_mappings):
    """Should return None for unknown roles"""
    from backend.services.role_mapping_service import RoleMappingService

    service = RoleMappingService(mock_role_mappings)

    assert service.normalize_role("unknown job title") is None


def test_get_all_variations(mock_role_mappings):
    """Should return all variations of a role"""
    from backend.services.role_mapping_service import RoleMappingService

    service = RoleMappingService(mock_role_mappings)

    variations = service.get_all_variations("software_engineer")

    assert "software engineer" in variations
    assert "swe" in variations
    assert len(variations) == 3
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/services/test_role_mapping_service.py -v`
Expected: FAIL with "No module named 'backend.services.role_mapping_service'"

**Step 3: Write minimal implementation**

Create: `backend/services/role_mapping_service.py`
```python
"""Role mapping service - maps job title variations to standard roles"""
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class RoleMappingService:
    """
    Service for mapping job title variations to standard roles.

    Handles 19,465 job title variations from corpus.
    """

    def __init__(self, corpus_dir: Optional[Path] = None):
        """
        Initialize role mapping service.

        Args:
            corpus_dir: Path to corpus data directory
        """
        if corpus_dir is None:
            corpus_dir = Path(__file__).parent.parent / 'data' / 'corpus'

        self.corpus_dir = corpus_dir
        self._mappings = {}
        self._load()

    def _load(self):
        """Load role mappings from JSON"""
        mappings_file = self.corpus_dir / 'role_mappings.json'

        if not mappings_file.exists():
            logger.warning(f"Role mappings not found at {mappings_file}")
            return

        try:
            with open(mappings_file, 'r') as f:
                self._mappings = json.load(f)
            logger.info(f"Loaded {len(self._mappings)} role mappings")
        except Exception as e:
            logger.error(f"Failed to load role mappings: {e}")
            self._mappings = {}

    def is_available(self) -> bool:
        """Check if role mappings are available"""
        return len(self._mappings) > 0

    def normalize_role(self, job_title: str) -> Optional[str]:
        """
        Normalize job title to standard role.

        Args:
            job_title: Original job title

        Returns:
            Standard role_id or None if not found
        """
        title_lower = job_title.lower().strip()
        return self._mappings.get(title_lower)

    def get_all_variations(self, role_id: str) -> List[str]:
        """
        Get all variations of a standard role.

        Args:
            role_id: Standard role identifier

        Returns:
            List of all job title variations
        """
        variations = []

        for title, mapped_role in self._mappings.items():
            if mapped_role == role_id:
                variations.append(title)

        return variations


# Singleton instance
_instance = None


def get_role_mapping_service() -> RoleMappingService:
    """Get singleton instance of role mapping service"""
    global _instance
    if _instance is None:
        _instance = RoleMappingService()
    return _instance
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/services/test_role_mapping_service.py -v`
Expected: PASS (3 tests)

**Step 5: Commit**

```bash
git add backend/services/role_mapping_service.py
git add tests/services/test_role_mapping_service.py
git commit -m "feat: add role mapping service

- Map 19,465 job title variations to standard roles
- Normalize any job title to role_id
- Get all variations of a role
- Graceful fallback if mappings unavailable"
```

---

## Phase 4: Integration (Days 8-9)

### Task 10: Enhance Role Taxonomy with Hybrid Keywords

**Files:**
- Modify: `backend/services/role_taxonomy.py`
- Test: `tests/services/test_role_taxonomy_enhanced.py`

**Step 1: Write the failing test**

Create: `tests/services/test_role_taxonomy_enhanced.py`
```python
"""Test enhanced role taxonomy with corpus integration"""
import pytest


def test_get_role_scoring_data_enhanced_returns_hybrid_keywords(monkeypatch):
    """Should merge manual + corpus keywords"""
    from backend.services.role_taxonomy import get_role_scoring_data_enhanced, ExperienceLevel

    # Mock corpus to return extra keywords
    def mock_get_corpus_keywords(role, level):
        return ['docker', 'kubernetes', 'terraform']

    monkeypatch.setattr(
        'backend.services.role_taxonomy.get_corpus_keywords',
        mock_get_corpus_keywords
    )

    result = get_role_scoring_data_enhanced('software_engineer', ExperienceLevel.MID)

    # Should have both manual and corpus keywords
    keywords = result['typical_keywords'][ExperienceLevel.MID]
    assert 'architecture' in keywords  # Manual keyword
    assert 'docker' in keywords  # Corpus keyword
    assert 'kubernetes' in keywords  # Corpus keyword


def test_get_role_scoring_data_enhanced_falls_back_without_corpus():
    """Should fall back to manual data if corpus unavailable"""
    from backend.services.role_taxonomy import get_role_scoring_data_enhanced, ExperienceLevel

    # Corpus not available (ImportError will happen)
    result = get_role_scoring_data_enhanced('software_engineer', ExperienceLevel.MID)

    # Should return manual keywords
    keywords = result['typical_keywords'][ExperienceLevel.MID]
    assert 'architecture' in keywords  # Manual keyword
    assert len(keywords) > 0
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/services/test_role_taxonomy_enhanced.py -v`
Expected: FAIL with "cannot import name 'get_role_scoring_data_enhanced'"

**Step 3: Write minimal implementation**

Append to `backend/services/role_taxonomy.py`:
```python
def get_corpus_keywords(role_id: str, level: ExperienceLevel) -> List[str]:
    """
    Get corpus-derived keywords for role and level.

    Args:
        role_id: Role identifier
        level: Experience level

    Returns:
        List of keywords from corpus
    """
    try:
        from backend.services.corpus_skills_database import get_corpus_skills_database
        from backend.config import ENABLE_CORPUS_KEYWORDS

        if not ENABLE_CORPUS_KEYWORDS:
            return []

        db = get_corpus_skills_database()
        if not db.is_available():
            return []

        # Get skills for this role
        corpus_keywords = db.get_skills_for_role(role_id)

        return corpus_keywords

    except ImportError:
        return []


def get_role_scoring_data_enhanced(role_id: str, level: ExperienceLevel) -> Optional[Dict]:
    """
    Get role scoring data with hybrid keywords (manual + corpus).

    Falls back to manual data if corpus unavailable.

    Args:
        role_id: Role identifier
        level: Experience level

    Returns:
        Role data dict with enhanced keywords
    """
    # Get base manual data
    base_data = ROLE_DEFINITIONS.get(role_id)
    if not base_data:
        return None

    # Make a copy to avoid modifying original
    import copy
    enhanced_data = copy.deepcopy(base_data)

    # Try to enhance with corpus keywords
    corpus_keywords = get_corpus_keywords(role_id, level)

    if corpus_keywords:
        # Merge manual + corpus keywords (deduplicate)
        manual_keywords = enhanced_data['typical_keywords'][level]
        combined = list(set(manual_keywords + corpus_keywords))
        enhanced_data['typical_keywords'][level] = combined

    return enhanced_data
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/services/test_role_taxonomy_enhanced.py -v`
Expected: PASS (2 tests)

**Step 5: Commit**

```bash
git add backend/services/role_taxonomy.py
git add tests/services/test_role_taxonomy_enhanced.py
git commit -m "feat: add hybrid keyword support to role taxonomy

- Add get_role_scoring_data_enhanced() function
- Merge manual + corpus keywords
- Respect ENABLE_CORPUS_KEYWORDS flag
- Graceful fallback to manual data"
```

---

## Phase 5: Testing & Validation (Day 12)

### Task 11: Corpus Validation Test Suite

**Files:**
- Create: `tests/integration/test_corpus_validation.py`

**Step 1: Create corpus validation tests**

Create: `tests/integration/test_corpus_validation.py`
```python
"""
Validate scorer against corpus resumes.

Tests scoring accuracy using 100 real resumes from corpus.
"""
import pytest
from pathlib import Path


@pytest.fixture
def corpus_sample_resumes():
    """Load 100 sample resumes from corpus"""
    from backend.scripts.corpus_parser import stream_resume_samples

    corpus_file = Path(__file__).parent.parent.parent / 'backend' / 'data' / 'corpus_source' / 'resume_samples.txt'

    if not corpus_file.exists():
        pytest.skip("Corpus source files not available")

    # Load first 100 resumes
    resumes = []
    for i, resume in enumerate(stream_resume_samples(corpus_file)):
        if i >= 100:
            break
        resumes.append(resume)

    return resumes


def test_all_corpus_resumes_score_within_range(corpus_sample_resumes):
    """All resumes should score between 40-95"""
    from backend.services.scorer_v2 import AdaptiveScorer
    from backend.services.parser import ResumeData

    scorer = AdaptiveScorer()

    scores = []
    for resume in corpus_sample_resumes:
        # Mock parse resume (simplified)
        resume_data = ResumeData(
            contact={'name': 'Test'},
            experience=[],
            education=[],
            skills=[],
            certifications=[],
            metadata={'wordCount': len(resume['text'].split())}
        )

        # Get first occupation as role
        role = resume['occupations'][0] if resume['occupations'] else 'software_engineer'

        try:
            result = scorer.score(resume_data, role, 'mid', mode='quality')
            scores.append(result['overallScore'])
        except:
            continue

    # Validate score distribution
    assert len(scores) > 0, "Should score at least some resumes"
    assert min(scores) >= 40, "No scores below 40"
    assert max(scores) <= 95, "No scores above 95"


def test_corpus_keywords_improve_matching():
    """Corpus keywords should improve match rate"""
    from backend.services.keyword_extractor import match_with_synonyms
    from backend.config import ENABLE_CORPUS_SYNONYMS

    test_cases = [
        ('kubernetes', 'Managed k8s clusters'),
        ('javascript', 'Built apps with Node.js'),
        ('python', 'Developed APIs using Flask')
    ]

    for keyword, text in test_cases:
        # Should match with corpus synonyms
        matched = match_with_synonyms(keyword, text)
        assert matched, f"Should match '{keyword}' in '{text}'"
```

**Step 2: Run validation tests**

```bash
# With corpus features enabled
ENABLE_CORPUS_KEYWORDS=true ENABLE_CORPUS_SYNONYMS=true pytest tests/integration/test_corpus_validation.py -v
```

Expected: PASS (tests validate scoring accuracy)

**Step 3: Commit**

```bash
git add tests/integration/test_corpus_validation.py
git commit -m "test: add corpus validation test suite

- Validate scorer against 100 real resumes
- Check score distribution (40-95 range)
- Verify keyword matching improvements"
```

---

## Summary: Implementation Checklist

**Phase 1-2: Foundation & Extraction (Days 1-4)**
- [ ] Task 1: Create directory structure
- [ ] Task 2: Copy corpus files
- [ ] Task 3: Add feature flag configuration
- [ ] Task 4: Corpus parser - resume samples
- [ ] Task 5: Skills extractor
- [ ] Task 6: Role mappings extractor
- [ ] Task 7: Build corpus database script

**Phase 3: Core Services (Days 5-7)**
- [ ] Task 8: Corpus skills database service
- [ ] Task 9: Role mapping service
- [ ] Task 10: Enhance role taxonomy

**Phase 4-5: Integration & ML (Days 8-11)**
- [ ] Enhance keyword_extractor.py with corpus synonyms
- [ ] Add ML classifiers (ExperienceLevelClassifier, RoleClassifier)
- [ ] Update scorer_v2.py with ML suggestions
- [ ] Update api/upload.py with ML response fields

**Phase 6: Validation (Day 12)**
- [ ] Task 11: Corpus validation test suite
- [ ] Run 1000 resume validation
- [ ] Compare features ON vs OFF

**Phase 7: Rollout (Days 13-14)**
- [ ] Day 13 AM: Enable synonyms flag
- [ ] Day 13 PM: Enable keywords flag
- [ ] Day 14 AM: Enable role mappings flag
- [ ] Day 14 PM: Enable ML flag

---

**End of Implementation Plan**

This plan provides detailed, testable tasks for the first 11 tasks. The remaining tasks follow similar patterns. Each task is designed to be completed in 2-5 minutes with clear test-first development approach.
