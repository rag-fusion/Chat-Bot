import os
import pytest
import numpy as np
from backend.app.vector_store import FAISSStore

def test_similarity_flow(tmp_path):
    # Build a tiny index for test
    store = FAISSStore(dimension=512, storage_dir=str(tmp_path))
    texts = ["solar panel efficiency", "wind turbine", "battery storage"]
    
    # Mock embeddings (512 dim)
    embs = np.random.rand(3, 512).astype(np.float32)
    items = []
    for i, text in enumerate(texts):
        items.append({
            'embedding': embs[i],
            'metadata': {
                'content': text,
                'file_name': 'test.txt',
                'modality': 'text',
                'file_id': f'test-{i}',
                'chunk_index': 0
            }
        })
    
    added = store.upsert(items, session_id="test_session")
    assert added == 3

    # simple check: search
    res = store.search(embs[0], top_k=3, session_id="test_session")
    assert len(res) > 0
    assert res[0]["page_content"] == texts[0]
