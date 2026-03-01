"""
Pre-load ML models and start LanguageTool JVM during Render build.

Run this as part of the Render Build Command:
  pip install -r requirements.txt && python backend/preload_models.py && alembic upgrade head

What this does:
1. Downloads sentence-transformers model 'all-MiniLM-L6-v2' (~80 MB) into
   HuggingFace local cache — loads in ~1-2s at runtime instead of 4+ minutes.
2. Starts a LanguageTool JVM to download its JAR (~200 MB) and verify it works.
   The JVM cache is preserved so subsequent startups are fast.
"""

import sys


def preload_sentence_transformer():
    print("Pre-loading sentence-transformers model 'all-MiniLM-L6-v2'...")
    try:
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer('all-MiniLM-L6-v2')
        _ = model.encode("test", show_progress_bar=False)
        print("✓ sentence-transformers model loaded and verified")
    except Exception as e:
        print(f"✗ Failed to pre-load sentence-transformers model: {e}")
        sys.exit(1)


def preload_language_tool():
    """
    Attempt to pre-load LanguageTool.  Non-fatal: if Java is unavailable in
    the build environment the app falls back to pyspellchecker at runtime.
    """
    print("Pre-loading LanguageTool (downloads JAR and starts JVM)...")
    try:
        import language_tool_python
        tool = language_tool_python.LanguageTool('en-US')
        # Quick smoke-test
        matches = tool.check("This are a test.")
        tool.close()
        print(f"✓ LanguageTool loaded and verified ({len(matches)} test matches found)")
    except Exception as e:
        print(f"⚠ LanguageTool not available ({e}) — grammar checking will use fallback at runtime")


if __name__ == "__main__":
    preload_sentence_transformer()
    preload_language_tool()
    print("\nPre-load complete.")
