"""
Pre-load ML models during Render build so they are cached before the first request.

Run this as part of the Render Build Command:
  pip install -r requirements.txt && python backend/preload_models.py && alembic upgrade head

The sentence-transformers model (~80 MB) is downloaded once here and stored in
HuggingFace's local cache (~/.cache/huggingface/hub/).  At runtime, loading from
cache takes ~1-2 seconds instead of 4+ minutes.
"""

import sys

def preload_sentence_transformer():
    print("Pre-loading sentence-transformers model 'all-MiniLM-L6-v2'...")
    try:
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer('all-MiniLM-L6-v2')
        # Run a quick smoke-test to confirm the model works
        _ = model.encode("test", show_progress_bar=False)
        print("✓ sentence-transformers model loaded and verified")
    except Exception as e:
        print(f"✗ Failed to pre-load sentence-transformers model: {e}")
        sys.exit(1)


if __name__ == "__main__":
    preload_sentence_transformer()
    print("All models pre-loaded successfully.")
