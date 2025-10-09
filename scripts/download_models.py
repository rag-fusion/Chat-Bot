#!/usr/bin/env python3
"""
Model Download Script for RAG Offline Chatbot
Downloads all required models to the organized directory structure.
"""

import os
import sys
from pathlib import Path

def download_text_embeddings():
    """Download text embedding model."""
    print("📥 Downloading text embeddings model...")
    try:
        from sentence_transformers import SentenceTransformer
        
        model_path = Path("backend/models/embeddings/all-MiniLM-L6-v2")
        model_path.mkdir(parents=True, exist_ok=True)
        
        model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
        model.save(str(model_path))
        print(f"✅ Text embeddings saved to: {model_path}")
        return True
    except Exception as e:
        print(f"❌ Failed to download text embeddings: {e}")
        return False

def download_clip_model():
    """Download CLIP model for image embeddings."""
    print("📥 Downloading CLIP model...")
    try:
        import clip
        
        model_path = Path("backend/models/clip")
        model_path.mkdir(parents=True, exist_ok=True)
        
        model, preprocess = clip.load('ViT-B/32', download_root=str(model_path))
        print(f"✅ CLIP model saved to: {model_path}")
        return True
    except Exception as e:
        print(f"❌ Failed to download CLIP model: {e}")
        return False

def download_whisper_model():
    """Download Whisper model for audio processing."""
    print("📥 Downloading Whisper model...")
    try:
        import whisper
        
        model_path = Path("backend/models/whisper")
        model_path.mkdir(parents=True, exist_ok=True)
        
        model = whisper.load_model('small', download_root=str(model_path))
        print(f"✅ Whisper model saved to: {model_path}")
        return True
    except Exception as e:
        print(f"❌ Failed to download Whisper model: {e}")
        return False

def main():
    """Main function to download all models."""
    print("🚀 Starting model downloads...")
    print("=" * 50)
    
    # Create base models directory
    Path("backend/models").mkdir(parents=True, exist_ok=True)
    
    success_count = 0
    total_models = 3
    
    # Download models
    if download_text_embeddings():
        success_count += 1
    
    if download_clip_model():
        success_count += 1
    
    if download_whisper_model():
        success_count += 1
    
    print("=" * 50)
    print(f"📊 Download Summary: {success_count}/{total_models} models downloaded successfully")
    
    if success_count == total_models:
        print("🎉 All models downloaded successfully!")
        print("\n📁 Your models directory structure:")
        print("backend/models/")
        print("├── llm/")
        print("│   └── mistral-7b-instruct-v0.2.Q4_K_M.gguf")
        print("├── embeddings/")
        print("│   └── all-MiniLM-L6-v2/")
        print("├── clip/")
        print("│   └── clip-vit-base-patch32/")
        print("└── whisper/")
        print("    └── whisper-small/")
    else:
        print("⚠️  Some models failed to download. Check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
