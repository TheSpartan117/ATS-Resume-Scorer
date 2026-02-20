#!/usr/bin/env python3
"""
Download and cache AI models for offline use
"""
import os

def download_sentence_transformer():
    """Download sentence-transformers model"""
    print("Downloading sentence-transformers model...")
    try:
        from sentence_transformers import SentenceTransformer

        # This will download and cache the model
        model = SentenceTransformer('all-MiniLM-L6-v2')
        print(f"✅ Successfully downloaded model to cache")
        print(f"   Cache location: {model._model_card_vars.get('model_name', 'unknown')}")
        return True
    except Exception as e:
        print(f"❌ Failed to download model: {e}")
        return False

def download_keybert_model():
    """KeyBERT uses the sentence-transformer model, so no separate download needed"""
    print("✅ KeyBERT will use the same model as sentence-transformers")
    return True

if __name__ == "__main__":
    print("=" * 60)
    print("AI MODEL DOWNLOAD")
    print("=" * 60)
    print()

    results = []
    results.append(download_sentence_transformer())
    results.append(download_keybert_model())

    print()
    print("=" * 60)
    if all(results):
        print("✅ ALL MODELS DOWNLOADED SUCCESSFULLY")
    else:
        print("⚠️  SOME MODELS FAILED TO DOWNLOAD")
        print("   You may need to check your internet connection")
