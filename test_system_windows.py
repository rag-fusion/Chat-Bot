#!/usr/bin/env python3
"""
Simple test script to verify the system works.
"""

import sys
import os
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

def test_imports():
    """Test that all modules can be imported."""
    print("Testing imports...")
    
    try:
        from app.ingestion import extract_any, Chunk
        print("[OK] Ingestion module imported")
    except Exception as e:
        print(f"[FAIL] Ingestion module failed: {e}")
        return False
    
    try:
        from app.embeddings import embed_text, embed_image
        print("[OK] Embeddings module imported")
    except Exception as e:
        print(f"[FAIL] Embeddings module failed: {e}")
        return False
    
    try:
        from app.vector_store import get_store
        print("[OK] Vector store module imported")
    except Exception as e:
        print(f"[FAIL] Vector store module failed: {e}")
        return False
    
    try:
        from app.retriever import get_retriever
        print("[OK] Retriever module imported")
    except Exception as e:
        print(f"[FAIL] Retriever module failed: {e}")
        return False
    
    try:
        from app.llm import build_adapter, load_config
        print("[OK] LLM module imported")
    except Exception as e:
        print(f"[FAIL] LLM module failed: {e}")
        return False
    
    try:
        from app.utils import create_citations
        print("[OK] Utils module imported")
    except Exception as e:
        print(f"[FAIL] Utils module failed: {e}")
        return False
    
    try:
        from app.ui import GradioApp
        print("[OK] UI module imported")
    except Exception as e:
        print(f"[FAIL] UI module failed: {e}")
        return False
    
    return True


def test_basic_functionality():
    """Test basic functionality."""
    print("\nTesting basic functionality...")
    
    try:
        from app.embeddings import embed_text
        from app.vector_store import get_store
        
        # Test text embedding
        embedding = embed_text("test text")
        print(f"[OK] Text embedding generated: {embedding.shape}")
        
        # Test vector store
        store = get_store()
        status = store.status()
        print(f"[OK] Vector store status: {status}")
        
        return True
        
    except Exception as e:
        print(f"[FAIL] Basic functionality test failed: {e}")
        return False


def test_config_loading():
    """Test configuration loading."""
    print("\nTesting configuration...")
    
    try:
        from app.llm import load_config
        
        config_path = Path(__file__).parent / "backend" / "config.yaml"
        if config_path.exists():
            config = load_config(str(config_path))
            print(f"[OK] Configuration loaded: {config}")
        else:
            print("[WARN] Configuration file not found, using defaults")
            config = load_config("")
            print(f"[OK] Default configuration: {config}")
        
        return True
        
    except Exception as e:
        print(f"[FAIL] Configuration test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("Offline Multimodal RAG - System Test")
    print("=" * 40)
    
    tests = [
        test_imports,
        test_basic_functionality,
        test_config_loading
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 40)
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("[SUCCESS] All tests passed! System is ready to use.")
        return 0
    else:
        print("[ERROR] Some tests failed. Check the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
