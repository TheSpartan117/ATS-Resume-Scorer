# Resume Corpus Integration - Design Document

**Date**: 2026-02-20
**Status**: Approved
**Approach**: Comprehensive Enhancement (Option C)

---

## Executive Summary

Integrate the 29,783-resume corpus from https://github.com/florex/resume_corpus into the existing ATS scorer system to provide:

- **Enhanced keyword matching**: 6,394 IT skills → +400% keyword coverage per role
- **Comprehensive role mapping**: 19,465 job title variations → handle any job title
- **Advanced synonym matching**: +400% synonym coverage per keyword
- **ML-powered suggestions**: Auto-detect experience level and suggest roles
- **Large-scale validation**: Test suite with 1000+ real resumes

**Key Constraint**: Zero cost, zero breaking changes, gradual rollout with feature flags

---

## 1. Architecture Overview

### Three-Layer Design

**Layer 1: Data Extraction & Processing** (One-time, runs in background)
- Parse corpus files: resume_samples.txt, skills_it.txt, normlized_classes.txt
- Extract structured data: skills with frequencies, role mappings, synonyms
- Generate ML training datasets
- Train classifiers: experience level and role prediction
- Output: JSON files in `backend/data/corpus/`

**Layer 2: Enhanced Intelligence Services** (Runtime)
- `CorpusSkillsDatabase`: Serve skill data with frequency and context
- `RoleMappingService`: Map any job title variation to standard roles
- `CorpusSynonymEngine`: Extended synonym matching
- `ExperienceLevelClassifier`: ML-based level prediction (75-80% accuracy)
- `RoleClassifier`: ML-based role suggestions (70-75% accuracy)

**Layer 3: Integration Points** (Updates to existing code)
- `role_taxonomy.py`: Add hybrid keyword retrieval (manual + corpus)
- `keyword_extractor.py`: Enhanced synonym matching
- `scorer_v2.py`: Optional ML suggestions in scoring
- `api/upload.py`: ML predictions in API response
- New test suite: Validate against 1000 corpus resumes

### Design Principles

1. **Backward Compatible**: Existing code continues to work unchanged
2. **Gradual Adoption**: Features enabled via feature flags
3. **Zero Dependencies**: Uses only Python stdlib + existing packages (scikit-learn)
4. **Zero Cost**: No external services, all runs locally
5. **Graceful Degradation**: Falls back to manual data if corpus unavailable

---

## 2. Data Flow

### Startup Flow

```
Backend Startup
    ↓
Check if corpus data exists
    ├─ NO → Launch background extraction (~60s)
    │        System uses manual data (works normally)
    │        When complete: hot-reload enhanced data
    │
    └─ YES → Load corpus JSON files (0.5s)
             System ready with enhanced features
```

**Key Points:**
- Backend starts in 0.5 seconds (no waiting)
- Existing features work immediately
- Enhanced features activate after 60 seconds (first run only)
- Progress logged to console

### Scoring Flow

```
User uploads CV → Parse resume → Call scorer.score()
    ↓
Check: Is corpus available?
    ├─ YES → Enhanced Mode
    │         - Get hybrid keywords (manual + corpus)
    │         - Match with enhanced synonyms
    │         - Add ML suggestions
    │
    └─ NO → Fallback Mode
            - Use manual keywords
            - Use base synonyms
            - No ML suggestions
    ↓
Return score result
```

### Background Extraction Flow

```
Step 1: Parse Resume Samples (20s)
  - Read resume_samples.txt (204 MB, 29,783 resumes)
  - Extract: ID, labels, text
  - Progress: 0-30%

Step 2: Extract Skills Database (15s)
  - Parse skills_it.txt (6,394 skills)
  - Count frequencies across resumes
  - Map skills to roles
  - Build co-occurrence matrix
  - Progress: 30-50%

Step 3: Process Role Mappings (10s)
  - Parse normlized_classes.txt (19,465 mappings)
  - Handle multi-role mappings
  - Progress: 50-70%

Step 4: Extract Synonyms (5s)
  - Identify skill variations
  - Merge with manual synonyms
  - Progress: 70-80%

Step 5: Prepare ML Training Data (10s)
  - Extract features from resumes
  - Label with ground truth
  - Split train/val/test (70/15/15)
  - Progress: 80-90%

Step 6: Train ML Models (5s)
  - Train ExperienceLevelClassifier
  - Train RoleClassifier
  - Validate on test set
  - Progress: 90-98%

Step 7: Save Outputs (2s)
  - Write JSON files (~3.4 MB total)
  - Save ML models (~7 MB total)
  - Progress: 98-100%

Total Time: ~60 seconds (one-time)
```

---

## 3. Component Details

### 3.1 Data Files (Layer 1 Output)

**Location**: `backend/data/corpus/`

**Files Generated:**

1. **skills_database.json** (~500 KB)
   ```json
   {
     "python": {
       "frequency": 2847,
       "roles": ["software_engineer", "data_scientist"],
       "experience_levels": {"entry": 450, "mid": 1200, "senior": 1197},
       "co_occurring_skills": ["django", "flask", "pandas"]
     }
   }
   ```

2. **role_mappings.json** (~1.2 MB)
   ```json
   {
     "database administrator": "database_administrator",
     "dba": "database_administrator",
     "oracle production dba": "database_administrator"
   }
   ```

3. **skill_synonyms_corpus.json** (~1.7 MB)
   ```json
   {
     "javascript": ["javascript", "js", "node.js", "nodejs", "ecmascript"],
     "kubernetes": ["kubernetes", "k8s", "kube"]
   }
   ```

4. **ml_training_data/** (~25 MB, not committed to git)
   - experience_classifier_data.json
   - role_classifier_data.json

5. **ml/models/** (~7 MB)
   - experience_classifier.joblib
   - role_classifier.joblib

### 3.2 Runtime Services (Layer 2)

**CorpusSkillsDatabase** (`backend/services/corpus_skills_database.py`)
```python
class CorpusSkillsDatabase:
    def get_skill_frequency(skill: str) -> int
    def get_skills_for_role(role: str, min_frequency: float = 0.3) -> List[str]
    def get_skill_synonyms(skill: str) -> List[str]
    def suggest_related_skills(skills: List[str], top_n: int = 10) -> List[str]
```

**RoleMappingService** (`backend/services/role_mapping_service.py`)
```python
class RoleMappingService:
    def normalize_role(job_title: str) -> str
    def get_all_variations(role: str) -> List[str]
    def suggest_role(resume_text: str) -> List[Tuple[str, float]]
```

**ML Classifiers** (`backend/ml/classifiers/`)
```python
class ExperienceLevelClassifier:
    def predict_level(resume_data: ResumeData) -> Tuple[str, float]
    def explain_prediction(resume_data: ResumeData) -> Dict

class RoleClassifier:
    def predict_roles(resume_data: ResumeData) -> List[Tuple[str, float]]
    def get_top_role(resume_data: ResumeData) -> str
```

### 3.3 Integration Points (Layer 3)

**role_taxonomy.py** - Add hybrid keyword function:
```python
def get_role_scoring_data_enhanced(role_id: str, level: ExperienceLevel) -> Dict:
    """Merges manual + corpus keywords"""
    base_data = ROLE_DEFINITIONS.get(role_id)

    try:
        corpus_keywords = get_corpus_keywords(role_id, level)
        base_data['typical_keywords'][level] = merge_keywords(
            base_data['typical_keywords'][level],  # Manual (priority)
            corpus_keywords                         # Corpus (comprehensive)
        )
    except ImportError:
        pass  # Use manual data

    return base_data
```

**keyword_extractor.py** - Enhanced synonym matching:
```python
def match_with_synonyms(keyword: str, text: str) -> bool:
    """Enhanced with corpus synonyms"""
    base_synonyms = get_all_synonyms(keyword)

    try:
        corpus_synonyms = get_corpus_synonyms(keyword)
        all_synonyms = list(set(base_synonyms + corpus_synonyms))
    except ImportError:
        all_synonyms = base_synonyms

    return any(syn in text.lower() for syn in all_synonyms)
```

**scorer_v2.py** - ML suggestions:
```python
class AdaptiveScorer:
    def suggest_experience_level(resume_data) -> Optional[Tuple[str, float]]
    def suggest_best_roles(resume_data, top_n=3) -> List[Tuple[str, float]]
```

**api/upload.py** - Add ML to response:
```python
response = {
    ...existing fields...,
    "ml_suggestions": {
        "experience_level": ("senior", 0.85),  # or null
        "alternative_roles": [("data_scientist", 0.67), ...]
    }
}
```

---

## 4. Error Handling

### Fallback Strategy

```
Corpus Features (Best)
  ↓ (if available)
Partial Corpus (Some Enhancement)
  ↓ (if extraction partial)
Manual Data Only (Current Behavior)
```

**Philosophy**: Never break, always degrade gracefully

### Error Scenarios

**1. Corpus Files Not Found**
- Log: "Corpus files not found, using manual data"
- Impact: System works normally with manual data
- Resolution: User can clone corpus repo if desired

**2. Extraction Fails Mid-Process**
- Log error and reason
- Clean up partial files
- Continue with manual data
- Don't retry automatically

**3. ML Training Fails**
- Log warning
- Continue without ML features
- Core features (keywords, synonyms) still work

**4. JSON Files Corrupted**
- Detect corruption on load
- Delete corrupted files
- Trigger re-extraction
- Use manual data meanwhile

**5. Memory Issues**
- Stream-process large files (don't load all into memory)
- Peak memory: ~50 MB vs 204 MB
- Skip invalid data, continue with rest

---

## 5. Feature Flags

**Configuration** (`backend/config.py`):
```python
ENABLE_CORPUS_KEYWORDS = os.getenv('ENABLE_CORPUS_KEYWORDS', 'false') == 'true'
ENABLE_CORPUS_SYNONYMS = os.getenv('ENABLE_CORPUS_SYNONYMS', 'false') == 'true'
ENABLE_ROLE_MAPPINGS = os.getenv('ENABLE_ROLE_MAPPINGS', 'false') == 'true'
ENABLE_ML_SUGGESTIONS = os.getenv('ENABLE_ML_SUGGESTIONS', 'false') == 'true'
```

**Purpose**:
- Enable features incrementally
- Easy rollback if issues
- A/B testing capability
- Production safety

---

## 6. Testing Strategy

### Test Suite Structure

```
tests/
├── test_corpus_extraction.py        # Extraction logic
├── test_corpus_services.py          # Runtime services
├── test_ml_classifiers.py           # ML models
└── test_corpus_validation.py        # 1000 resume validation
```

### Validation Metrics

**Target Improvements:**
- Keyword matching: 90%+ (up from 60%)
- Role mapping: 95%+ (handles 19,465 variations)
- Experience classifier: 75-80% accuracy
- Role classifier: 70-75% accuracy
- Score consistency: ±5 points variance

**Performance Benchmarks:**
- Startup time: <1 second (with cached corpus)
- Query time: <0.1ms (JSON lookup)
- ML prediction: <10ms per resume
- Memory overhead: +10 MB total

---

## 7. Deployment Strategy

### Phased Rollout (14 days)

**Phase 1-2 (Days 1-4): Foundation & Extraction**
- Set up directory structure
- Copy corpus files to project
- Build extraction scripts
- Run extraction once
- Generate all JSON files
- Commit to git (with Git LFS)

**Phase 3 (Days 5-7): Core Services**
- Implement CorpusSkillsDatabase
- Implement RoleMappingService
- Implement CorpusSynonymEngine
- Add lazy loading
- Write unit tests
- **All features disabled** (flags off)

**Phase 4-5 (Days 8-11): Integration & ML**
- Update role_taxonomy.py
- Update keyword_extractor.py
- Update scorer_v2.py
- Update api/upload.py
- Train ML models
- Write integration tests
- **All features still disabled**

**Phase 6 (Day 12): Validation**
- Run 1000 resume validation
- Compare features ON vs OFF
- Verify improvements
- Confirm no regressions

**Phase 7 (Days 13-14): Gradual Rollout**
- Day 13 AM: Enable synonyms → monitor 4 hours
- Day 13 PM: Enable keywords → monitor 4 hours
- Day 14 AM: Enable role mappings → monitor 4 hours
- Day 14 PM: Enable ML → monitor 4 hours

### Rollback Plan

```bash
# Immediate rollback (30 seconds)
ENABLE_CORPUS_KEYWORDS=false
ENABLE_CORPUS_SYNONYMS=false
ENABLE_ROLE_MAPPINGS=false
ENABLE_ML_SUGGESTIONS=false

# Restart backend
# System reverts to manual data (proven stable)
```

---

## 8. Success Metrics

### Quantitative Metrics

**Keyword Coverage:**
- Before: ~30-50 keywords per role
- After: ~200-300 keywords per role
- Target: +400% increase

**Synonym Matching:**
- Before: ~100 synonyms per keyword
- After: ~500 synonyms per keyword
- Target: +400% increase

**Role Recognition:**
- Before: 23 roles, limited variations
- After: 23 roles + 19,465 variations
- Target: 95%+ mapping success

**Score Accuracy:**
- Before: Wide variance, some inflated
- After: Tighter distribution, more realistic
- Target: 60-75 mean on corpus validation

**ML Predictions:**
- Experience level: 75-80% accuracy
- Role suggestions: 70-75% accuracy

### Qualitative Metrics

- User can enter any job title (not just predefined 23)
- Better keyword matching reduces false negatives
- ML suggestions help users discover better roles
- More realistic scores build user trust

---

## 9. Resource Requirements

### Storage

```
backend/data/corpus_source/     # Raw corpus files (gitignored)
├── resume_samples.txt          204 MB
├── skills_it.txt               14 MB
└── normlized_classes.txt       1.2 MB

backend/data/corpus/            # Generated JSON (committed with Git LFS)
├── skills_database.json        500 KB
├── role_mappings.json          1.2 MB
└── skill_synonyms_corpus.json  1.7 MB

backend/ml/models/              # Trained models (gitignored)
├── experience_classifier.joblib 2 MB
└── role_classifier.joblib      5 MB

Total committed to git: ~3.4 MB (compressed to ~800 KB)
Total on disk: ~230 MB
```

### Runtime Resources

- **Memory**: +10 MB (3.4 MB data + 7 MB models loaded on-demand)
- **Startup time**: +0.5s (JSON loading) or +60s (first extraction)
- **CPU**: Low (one-time extraction, fast JSON lookups)
- **Disk I/O**: Minimal (JSON cached in memory)

### Development Time

- Phase 1-2: 4 days (foundation + extraction)
- Phase 3: 3 days (core services)
- Phase 4-5: 4 days (integration + ML)
- Phase 6: 1 day (validation)
- Phase 7: 2 days (rollout)
- **Total: 14 days**

---

## 10. Risks & Mitigations

### Risk 1: Corpus Data Quality

**Risk**: Resume corpus may have errors, spam, or low-quality data

**Mitigation**:
- Frequency thresholds (only use skills appearing in 30%+ of resumes)
- Manual review of top 100 most frequent skills
- Hybrid approach keeps manual keywords as foundation
- Easy to adjust or disable via feature flags

### Risk 2: Breaking Changes

**Risk**: Integration might break existing functionality

**Mitigation**:
- Feature flags allow instant rollback
- Comprehensive test suite (1000+ resumes)
- Backward compatibility enforced
- All existing functions unchanged
- Gradual rollout (one feature at a time)

### Risk 3: Performance Degradation

**Risk**: Additional data might slow down system

**Mitigation**:
- JSON files cached in memory (fast lookups)
- Lazy loading for ML models
- Benchmarks confirm <1ms query time
- Startup time minimal (+0.5s)

### Risk 4: ML Model Inaccuracy

**Risk**: ML predictions might be wrong or misleading

**Mitigation**:
- Show confidence scores (user can judge)
- Frame as "suggestions" not "requirements"
- Can disable ML via feature flag
- Target 75-80% accuracy (better than nothing)
- Core scoring doesn't depend on ML

### Risk 5: Memory Issues

**Risk**: Large corpus files might cause memory problems

**Mitigation**:
- Stream processing (don't load 204 MB into memory)
- Peak memory: 50 MB during extraction
- Runtime memory: 10 MB total
- Extraction runs in background (doesn't block startup)

---

## 11. Future Enhancements

### Phase 8+ (Post-Launch)

**Enhancement 1: Continuous Learning**
- Periodically retrain ML models with new data
- Update skill frequencies as technologies evolve
- Track which keywords are trending

**Enhancement 2: Custom Corpus**
- Allow users to upload their own resume corpus
- Build company-specific keyword databases
- Train ML models on company data

**Enhancement 3: Advanced Analytics**
- Skill gap analysis (what skills are missing)
- Career path suggestions
- Salary predictions based on skills

**Enhancement 4: Real-time Updates**
- Auto-update corpus from job sites
- Track emerging skills and roles
- Adaptive keyword database

---

## 12. Dependencies & Licenses

### External Dependencies

**Corpus Repository:**
- Source: https://github.com/florex/resume_corpus
- License: Open source, requires citation
- Citation: Jiechieu, K.F.F., Tsopze, N. (2020). Skills prediction based on multi-label resume classification using CNN with model predictions explanation. Neural Comput & Applic. https://doi.org/10.1007/s00521-020-05302-x

**Python Packages** (already in requirements):
- scikit-learn (ML models)
- json (data loading)
- All standard library

**New Dependencies**: NONE

---

## 13. Documentation Requirements

### User-Facing Documentation

1. Update README with corpus integration features
2. Document new ML suggestion fields in API response
3. Add examples showing enhanced keyword matching
4. Explain how role mapping works

### Developer Documentation

1. Document corpus extraction process
2. Explain hybrid keyword merge logic
3. ML model training instructions
4. Feature flag usage guide
5. Troubleshooting guide

### Code Documentation

1. Docstrings for all new functions
2. Type hints throughout
3. Inline comments for complex logic
4. Architecture diagram in docs/

---

## 14. Acceptance Criteria

### Must Have (Phase 1-6)

- [x] Design approved
- [ ] Corpus data extracted and validated
- [ ] Core services implemented and tested
- [ ] Integration complete with feature flags
- [ ] ML models trained with 75%+ accuracy
- [ ] 1000 resume validation passes
- [ ] All tests pass (100% coverage for new code)
- [ ] Documentation complete

### Should Have (Phase 7)

- [ ] Gradual rollout completed successfully
- [ ] No production incidents
- [ ] Metrics show improvements
- [ ] User feedback positive

### Nice to Have (Future)

- [ ] Custom corpus upload
- [ ] Real-time updates
- [ ] Advanced analytics

---

## 15. Sign-off

**Design Approved By**: User
**Date**: 2026-02-20
**Next Step**: Create implementation plan using writing-plans skill

---

**End of Design Document**
