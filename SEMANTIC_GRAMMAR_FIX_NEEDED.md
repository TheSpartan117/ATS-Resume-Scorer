# Semantic Matching & Grammar Checking - Fix Required

**Date**: March 1, 2026
**Status**: ❌ NOT WORKING - Network connectivity issues
**Priority**: HIGH

---

## 🔴 CRITICAL ISSUES

### 1. Semantic Keyword Matching - NOT WORKING ❌

**Problem**: Connection to HuggingFace model hub failing
**Model**: `all-MiniLM-L6-v2` (sentence-transformers)
**Error**: `Connection reset by peer (Error 54)`

**Current Behavior**:
- ✅ System is functional (falls back to exact matching)
- ❌ Semantic matching unavailable
- ❌ Synonym detection disabled
- ❌ Abbreviation matching disabled

**Impact**:
- Lower scores for resumes with synonyms/variations
- Example: "ML" won't match "machine learning"
- Example: "stakeholders" won't match "stakeholder"
- Estimated: **-2 to -4 points per resume**

---

### 2. Grammar Checking - NOT WORKING ❌

**Problem**: Connection to LanguageTool API failing
**Service**: `language-tool-python`
**Error**: `Connection aborted, ConnectionResetError(54)`

**Current Behavior**:
- ❌ Grammar checking disabled
- ❌ Spelling errors not detected
- ❌ P4.1 (Grammar & Spelling) parameter may fail

**Impact**:
- Grammar/spelling parameter (10 points) not functioning
- Users won't get feedback on language quality
- Estimated: **-5 to -10 points per resume**

---

## 🔍 Root Cause Analysis

### Network Connectivity Issues

Both services require external connections:

1. **HuggingFace Hub**: `https://huggingface.co`
   - Downloads model files (~80MB)
   - Requires stable internet connection
   - Model caches locally after first download

2. **LanguageTool**: Remote API endpoint
   - Checks grammar in real-time
   - Requires internet per request
   - No local caching available

### Error Details

```
'(ProtocolError('Connection aborted.', ConnectionResetError(54,
'Connection reset by peer')), ...)'

Retry attempts: 5/5 failed
Status: Unable to establish connection
```

**Possible Causes**:
- Network firewall blocking HuggingFace
- VPN or proxy interference
- ISP connection issues
- HuggingFace service temporarily down
- Rate limiting or IP blocking

---

## ✅ SOLUTIONS

### Solution 1: Fix Network Connection (PREFERRED)

**Try these steps in order:**

#### A. Check Basic Connectivity
```bash
# Test connection to HuggingFace
curl -I https://huggingface.co

# If this fails, network issue confirmed
```

#### B. Try Different Network
- Switch to mobile hotspot
- Try from different WiFi
- Disable VPN if active
- Connect from work/university network

#### C. Use Proxy/Mirror
```bash
# Set HuggingFace mirror
export HF_ENDPOINT=https://hf-mirror.com

# Retry model download
python3 backend/download_models.py
```

#### D. Download with Retry Logic
```bash
# Manual download with better retry
pip install --upgrade huggingface-hub
huggingface-cli download sentence-transformers/all-MiniLM-L6-v2
```

---

### Solution 2: Use Local LanguageTool Server (ALTERNATIVE)

Instead of remote API, run LanguageTool locally:

```bash
# Download LanguageTool server
wget https://languagetool.org/download/LanguageTool-stable.zip
unzip LanguageTool-stable.zip
cd LanguageTool-*

# Start local server
java -cp languagetool-server.jar org.languagetool.server.HTTPServer --port 8081

# Update code to use local server
```

**Code Change Required**:
```python
# In grammar checking code
tool = language_tool_python.LanguageTool('en-US',
                                         remote_server='http://localhost:8081')
```

---

### Solution 3: Pre-download Models (WORKAROUND)

Download model on machine with good connection, then transfer:

#### Step 1: Download on different machine
```bash
# On machine with good internet
pip install sentence-transformers
python3 -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"
```

#### Step 2: Copy cache to target machine
```bash
# Find cache location
echo ~/.cache/huggingface/
echo ~/.cache/torch/sentence_transformers/

# Copy to USB/cloud
tar -czf model_cache.tar.gz ~/.cache/huggingface/ ~/.cache/torch/

# On target machine
cd ~
tar -xzf model_cache.tar.gz
```

---

### Solution 4: Use Alternative Models (FALLBACK)

If HuggingFace remains inaccessible, use alternative semantic matching:

#### Option A: spaCy (Smaller, Simpler)
```bash
pip install spacy
python3 -m spacy download en_core_web_md

# Modify semantic_matcher.py to use spaCy instead
```

#### Option B: Gensim Word2Vec (Lightweight)
```bash
pip install gensim
# Use pre-trained word2vec models (smaller download)
```

#### Option C: Fuzzy Matching (No External Deps)
```bash
pip install fuzzywuzzy python-levenshtein
# Use string similarity instead of semantic similarity
# Not as accurate, but works offline
```

---

## 📊 Expected Improvements Once Fixed

### Semantic Matching Restored:

**Before (Exact matching only)**:
```
Resume: "I have experience with ML and AI"
Looking for: "machine learning", "artificial intelligence"
Match: 0/2 keywords ❌
```

**After (Semantic matching)**:
```
Resume: "I have experience with ML and AI"
Looking for: "machine learning", "artificial intelligence"
Match: 2/2 keywords (0.85 similarity) ✅
Improvement: +2 to +4 points per resume
```

### Grammar Checking Restored:

**Current**: Grammar errors ignored
**After Fix**: Proper error detection

Example resume errors:
- "I has five years experience" → Detected: Subject-verb disagreement
- "experiance in python" → Detected: Spelling error
- "Working on multiple project" → Detected: Singular/plural error

Impact: Accurate P4.1 scoring (8 points for grammar)

---

## 🧪 Testing & Verification

Once network issues resolved:

### Test Semantic Matching:
```bash
python3 -c "
from backend.services.hybrid_keyword_matcher import get_hybrid_matcher
matcher = get_hybrid_matcher()
score = matcher.match_keyword('python', 'experienced with Python programming')
print(f'Semantic match score: {score}')
print(f'Model loaded: {matcher._model is not None}')
# Expected: score > 0.8, Model loaded: True
"
```

### Test Grammar Checking:
```bash
python3 -c "
import language_tool_python
tool = language_tool_python.LanguageTool('en-US')
text = 'I has five years experiance.'
matches = tool.check(text)
print(f'Errors found: {len(matches)}')
for match in matches:
    print(f'  - {match.message}')
# Expected: 2-3 errors detected
"
```

---

## 📝 Temporary Workarounds (Current State)

### What's Working:
✅ **Exact keyword matching** - System continues to function
✅ **All other scoring parameters** - 18/21 parameters working
✅ **Core functionality** - Resumes can still be scored

### What's Missing:
❌ **Semantic similarity** - Synonym/variation matching
❌ **Grammar checking** - Language quality assessment
❌ **Estimated -7 to -14 points** lost per resume

### Fallback Behavior:
- Keyword matching uses strict string matching
- Grammar parameter may return 0 or skip
- No errors thrown, system gracefully degrades

---

## 🔧 Implementation Priority

1. **Immediate** (Today):
   - ✅ Document issue (this file)
   - ✅ Expand keywords to compensate for exact matching
   - Try network troubleshooting

2. **Short-term** (This week):
   - Fix network connectivity
   - Download models successfully
   - Test both features working

3. **Medium-term** (If network unfixable):
   - Implement local LanguageTool server
   - Consider alternative semantic matching
   - Add offline fallback models

4. **Long-term** (Future enhancement):
   - Bundle models with application
   - Implement auto-retry with exponential backoff
   - Add health checks for external services
   - Create admin dashboard showing service status

---

## 📋 Files Affected

```
backend/services/hybrid_keyword_matcher.py     # Semantic matching
backend/services/semantic_matcher.py           # Semantic similarity core
backend/services/parameters/p4_1_grammar.py    # Grammar checking
backend/download_models.py                     # Model download script
```

---

## 🎯 Success Criteria

System considered "fully operational" when:

✅ Semantic matching working:
- Model loads successfully
- Similarity scores > 0.7 for synonyms
- Abbreviations detected (ML = machine learning)

✅ Grammar checking working:
- LanguageTool connects
- Errors detected accurately
- P4.1 parameter scores correctly

✅ Full scoring accuracy:
- All 21 parameters operational
- Scores match expected benchmarks
- No degraded functionality

---

## 📞 Support Resources

### HuggingFace Support:
- Forum: https://discuss.huggingface.co/
- Discord: https://discord.gg/huggingface
- GitHub: https://github.com/huggingface/transformers/issues

### LanguageTool Support:
- Forum: https://forum.languagetool.org/
- GitHub: https://github.com/languagetool-org/languagetool/issues

### Network Debugging:
```bash
# Test DNS resolution
nslookup huggingface.co

# Test HTTP connection
curl -v https://huggingface.co

# Check proxy settings
env | grep -i proxy

# Test with different DNS
dig @8.8.8.8 huggingface.co
```

---

## ⚠️ Important Notes

1. **System is NOT broken** - it continues to function with fallback
2. **Scores are lower** than they should be due to missing features
3. **User experience degraded** - less accurate feedback
4. **Fix is straightforward** once network access restored
5. **No code changes needed** if network fixed (just download models)

---

**Status**: DOCUMENTED - Awaiting network fix
**Next Action**: Attempt network troubleshooting and model download
**Owner**: System Administrator / DevOps
**Updated**: March 1, 2026
