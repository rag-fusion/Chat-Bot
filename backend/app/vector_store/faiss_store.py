import json
import numpy as np
import faiss
from pathlib import Path
from app.config import EMBED_DIM, get_session_dir

class FaissStore:
    def __init__(self, chat_id: str):
        self.chat_id     = chat_id
        self.session_dir = get_session_dir(chat_id)
        self.index_path  = self.session_dir / "index.faiss"
        self.meta_path   = self.session_dir / "metadata.json"

        # IndexFlatIP = cosine similarity (after L2 normalization)
        # IndexIDMap2 = stable integer IDs (required for citations)
        self._index    = faiss.IndexIDMap2(faiss.IndexFlatIP(EMBED_DIM))
        self._metadata: dict[int, dict] = {}

        if self.index_path.exists() and self.meta_path.exists():
            self._load()

    def add(self, embeddings: np.ndarray, metadata_list: list[dict]) -> list[int]:
        """Add vectors. Returns list of assigned vector_ids."""
        assert embeddings.shape[0] == len(metadata_list)

        start_id = (max(self._metadata.keys(), default=-1) + 1)
        ids = np.arange(start_id, start_id + len(embeddings), dtype=np.int64)

        self._index.add_with_ids(embeddings, ids)

        for vid, meta in zip(ids.tolist(), metadata_list):
            meta["vector_id"] = vid
            self._metadata[vid] = meta

        self._save()
        return ids.tolist()

    def search(self, query_vec: np.ndarray, k: int = 5, threshold: float = 0.25) -> list[dict]:
        """Search. Returns top-k results above threshold, sorted by score."""
        if self._index.ntotal == 0:
            return []

        q = query_vec.reshape(1, -1).astype(np.float32)
        actual_k = min(k, self._index.ntotal)
        scores, ids = self._index.search(q, actual_k)

        results = []
        for score, vid in zip(scores[0], ids[0]):
            if vid == -1:
                continue
            if float(score) < threshold:
                continue
            meta = dict(self._metadata[int(vid)])
            meta["score"] = float(score)
            results.append(meta)

        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def get_by_id(self, vector_id: int) -> dict | None:
        return self._metadata.get(vector_id)

    def _save(self):
        faiss.write_index(self._index, str(self.index_path))
        with open(self.meta_path, "w") as f:
            json.dump({str(k): v for k, v in self._metadata.items()}, f, indent=2)

    def _load(self):
        self._index = faiss.read_index(str(self.index_path))
        with open(self.meta_path, "r") as f:
            raw = json.load(f)
        self._metadata = {int(k): v for k, v in raw.items()}


# In-process cache — avoids reloading FAISS on every request
_stores: dict[str, FaissStore] = {}

def get_store(chat_id: str) -> FaissStore:
    if chat_id not in _stores:
        _stores[chat_id] = FaissStore(chat_id)
    return _stores[chat_id]
