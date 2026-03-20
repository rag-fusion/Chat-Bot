import sys
import os
import shutil
import numpy as np
import pytest

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)


from backend.app.vector_store import get_store, FAISSStore

def test_session_isolation():
    print("\n--- Testing Session Isolation ---")
    

    store = FAISSStore(dimension=512, storage_dir="./test_storage")
    
    # 1. Add Data to Session A
    print("Adding data to Session A...")
    item_a = {
        'embedding': np.random.rand(512).astype(np.float32),
        'metadata': {
            'content': 'Secret of Session A', 
            'file_name': 'doc_a.txt', 
            'modality': 'text',
            'file_id': 'file-a-001',
            'chunk_index': 0
        }
    }
    store.upsert([item_a], session_id="session_A")
    
    # 2. Add Data to Session B
    print("Adding data to Session B...")
    item_b = {
        'embedding': np.random.rand(512).astype(np.float32),
        'metadata': {
            'content': 'Secret of Session B', 
            'file_name': 'doc_b.txt', 
            'modality': 'text',
            'file_id': 'file-b-001',
            'chunk_index': 0
        }
    }
    store.upsert([item_b], session_id="session_B")
    
    # 3. Search in Session A (Should find A, not B)
    print("Searching in Session A...")
    results_a = store.search(item_a['embedding'], top_k=5, session_id="session_A")
    found_content_a = [r['page_content'] for r in results_a]
    print(f"Results A: {found_content_a}")
    
    assert 'Secret of Session A' in found_content_a
    assert 'Secret of Session B' not in found_content_a
    print("✅ Session A isolation passed.")
    
    # 4. Search in Session B (Should find B, not A)
    print("Searching in Session B...")
    results_b = store.search(item_b['embedding'], top_k=5, session_id="session_B")
    found_content_b = [r['page_content'] for r in results_b]
    print(f"Results B: {found_content_b}")
    
    assert 'Secret of Session B' in found_content_b
    assert 'Secret of Session A' not in found_content_b
    print("✅ Session B isolation passed.")
    
    # 5. Verify enriched metadata
    meta_a = results_a[0]
    assert meta_a.get('session_id') == 'session_A'
    assert meta_a.get('file_id') == 'file-a-001'
    assert meta_a.get('chunk_index') == 0
    print("✅ Enriched metadata passed.")
    
    # Cleanup
    if os.path.exists("./test_storage"):
        shutil.rmtree("./test_storage")

def test_persistence_reload():
    print("\n--- Testing Persistence Reload ---")
    

    store_dir = "./test_storage_persist"
    if os.path.exists(store_dir):
        shutil.rmtree(store_dir)
        
    store1 = FAISSStore(dimension=512, storage_dir=store_dir)
    
    # Add data
    print("Adding data to Session Persistent...")
    emb = np.random.rand(512).astype(np.float32)
    item = {
        'embedding': emb,
        'metadata': {
            'content': 'Persistent Content', 
            'file_name': 'persist.txt', 
            'modality': 'text',
            'file_id': 'file-persist-001',
            'chunk_index': 0
        }
    }
    store1.upsert([item], session_id="session_P")
    
    # Get ID
    results1 = store1.search(emb, top_k=1, session_id="session_P")
    original_id = results1[0]['vector_id']
    print(f"Original ID: {original_id}")
    
    # Simulate App Restart (New Store Instance)

    from backend.app.vector_store.faiss_store import _active_sessions
    _active_sessions.clear()
    
    print("Simulating Restart...")
    store2 = FAISSStore(dimension=512, storage_dir=store_dir)
    
    # Search again
    results2 = store2.search(emb, top_k=1, session_id="session_P")
    
    assert len(results2) > 0
    assert results2[0]['page_content'] == 'Persistent Content'
    assert results2[0]['vector_id'] == original_id
    assert results2[0]['session_id'] == 'session_P'
    print(f"Reloaded ID: {results2[0]['vector_id']}")
    print("✅ Persistence reload passed.")
    
    # Cleanup
    if os.path.exists(store_dir):
        shutil.rmtree(store_dir)

def test_citation_metadata():
    print("\n--- Testing Metadata Retrieval for Viewer ---")

    store_dir = "./test_storage_meta"
    if os.path.exists(store_dir):
        shutil.rmtree(store_dir)
    
    store = FAISSStore(dimension=512, storage_dir=store_dir)
    
    item = {
        'embedding': np.random.rand(512).astype(np.float32),
        'metadata': {
            'content': 'Viewer Content', 
            'file_name': 'view.txt', 
            'modality': 'text', 
            'page_number': 42,
            'file_id': 'file-view-001',
            'chunk_index': 3
        }
    }
    store.upsert([item], session_id="session_view")
    
    # Search to get ID
    results = store.search(item['embedding'], top_k=1, session_id="session_view")
    vid = results[0]['vector_id']
    
    # Retrieve by ID (as viewer endpoint would)
    meta = store.get_metadata(session_id="session_view", vector_id=vid)
    
    assert meta is not None
    assert meta['page_content'] == 'Viewer Content'
    assert meta['page_number'] == 42
    assert meta['file_id'] == 'file-view-001'
    assert meta['chunk_index'] == 3
    assert meta['session_id'] == 'session_view'
    print("✅ Metadata retrieval via ID passed.")
    
    # Cleanup
    if os.path.exists(store_dir):
        shutil.rmtree(store_dir)

def test_session_files_dir():
    print("\n--- Testing Session Files Directory ---")
    store_dir = "./test_storage_files"
    if os.path.exists(store_dir):
        shutil.rmtree(store_dir)
    
    store = FAISSStore(dimension=512, storage_dir=store_dir)
    files_dir = store.get_session_files_dir("test_session")
    
    assert os.path.exists(files_dir)
    assert "test_session" in files_dir
    assert files_dir.endswith("files")
    print(f"Files dir: {files_dir}")
    print("✅ Session files directory passed.")
    
    # Cleanup
    if os.path.exists(store_dir):
        shutil.rmtree(store_dir)

if __name__ == "__main__":
    try:
        test_session_isolation()
        test_persistence_reload()
        test_citation_metadata()
        test_session_files_dir()
        print("\n🎉 ALL TESTS PASSED!")
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
