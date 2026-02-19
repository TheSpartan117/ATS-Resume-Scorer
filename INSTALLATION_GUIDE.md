# Installation Guide for Grammar Checking Fix

## Quick Start

### Step 1: Install the new dependency

```bash
cd /Users/sabuj.mondal/ats-resume-scorer/backend
pip install pyspellchecker==0.8.1
```

### Step 2: Verify installation

```bash
python -c "from spellchecker import SpellChecker; print('✓ pyspellchecker installed successfully')"
```

### Step 3: Run the test script

```bash
cd /Users/sabuj.mondal/ats-resume-scorer/backend
python test_grammar_fix.py
```

Expected output:
```
============================================================
Grammar Checking Implementation Test
============================================================
Testing typo detection...

Found X grammar issues:
  - [typo] Software Engineer at Company A: Possible spelling error 'Develped' - Suggestion: 'developed'
  - [typo] Software Engineer at Company A: Possible spelling error 'continous' - Suggestion: 'continuous'

Typo issues found: 2
✓ Test PASSED: Typos detected successfully


Testing basic grammar checks...
...
✓ Test PASSED: Grammar errors detected successfully


Testing graceful fallback...
...
✓ Test PASSED: Graceful fallback works (returns empty list)

============================================================
Test Results Summary
============================================================
Typo Detection: ✓ PASSED
Basic Grammar: ✓ PASSED
Graceful Fallback: ✓ PASSED

============================================================
ALL TESTS PASSED ✓
```

### Step 4: Run the official test suite

```bash
pytest backend/tests/test_red_flags_validator.py::test_typo_detection -v
```

Expected output:
```
test_typo_detection PASSED
```

## Troubleshooting

### Issue: Import Error for SpellChecker

**Error**: `ImportError: No module named 'spellchecker'`

**Solution**:
```bash
pip install pyspellchecker==0.8.1
```

### Issue: Test fails with no typos detected

**Problem**: The spell checker might not be initialized properly.

**Solution**:
1. Check if pyspellchecker is installed: `pip list | grep pyspellchecker`
2. Reinstall if needed: `pip uninstall pyspellchecker && pip install pyspellchecker==0.8.1`
3. Clear any Python cache: `find . -type d -name __pycache__ -exec rm -rf {} +`

### Issue: Old LanguageTool still being used

**Problem**: LanguageTool dependency still installed.

**Solution**:
```bash
pip uninstall language-tool-python
pip install pyspellchecker==0.8.1
```

## Verification Checklist

- [ ] pyspellchecker installed: `pip list | grep pyspellchecker`
- [ ] LanguageTool removed: `pip list | grep language-tool` (should be empty)
- [ ] Test script passes: `python backend/test_grammar_fix.py`
- [ ] Official test passes: `pytest backend/tests/test_red_flags_validator.py::test_typo_detection -v`
- [ ] API still works with existing resumes

## Rollback (if needed)

If you need to rollback to LanguageTool:

```bash
pip uninstall pyspellchecker
pip install language-tool-python==2.7.1
```

Then revert the changes in:
- `backend/requirements.txt`
- `backend/services/red_flags_validator.py`

## Next Steps

After successful installation:

1. Test with real resumes in your application
2. Monitor for any false positives in typo detection
3. Adjust technical terms whitelist if needed (in `_check_spelling()` method)
4. Consider adding more grammar patterns if needed (in `_check_basic_grammar()` method)

## Support

For issues or questions:
- Check the implementation guide: `GRAMMAR_CHECK_IMPLEMENTATION.md`
- Review the code: `backend/services/red_flags_validator.py`
- Run debug script: `python backend/test_grammar_fix.py`
