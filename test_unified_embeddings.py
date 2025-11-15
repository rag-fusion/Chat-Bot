"""Test unified 512-dim embeddings."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.embeddings import embed_text, embed_image
from app.vector_store import get_store
import numpy as np

def test_embeddings():
    """Test unified embedding dimensions."""
    print("Testing unified 512-dim embeddings...")
    print("=" * 60)
    
    # Test 1: Text embedding dimension
    print("\n1. Testing text embedding dimension...")
    try:
        text_emb = embed_text("test text")
        assert text_emb.shape == (1, 512), f"Expected (1, 512), got {text_emb.shape}"
        print(f"   ✓ Text embedding shape: {text_emb.shape} (expected: (1, 512))")
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False
    
    # Test 2: Store dimension
    print("\n2. Testing store dimension...")
    try:
        store = get_store()
        assert store.dimension == 512, f"Expected 512, got {store.dimension}"
        print(f"   ✓ Store dimension: {store.dimension} (expected: 512)")
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False
    
    # Test 3: Cross-modal compatibility (if index has data)
    print("\n3. Testing cross-modal compatibility...")
    try:
        store = get_store()
        if store.index.ntotal > 0:
            results = store.search(text_emb, top_k=5)
            print(f"   ✓ Cross-modal search returned {len(results)} results")
            modalities = set(r.get('modality', r.get('file_type', 'unknown')) for r in results)
            print(f"   ✓ Retrieved modalities: {modalities}")
        else:
            print("   ⚠ No indexed data - ingest some files first to test cross-modal retrieval")
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("✅ All tests passed!")
    return True

if __name__ == "__main__":
    success = test_embeddings()
    sys.exit(0 if success else 1)

