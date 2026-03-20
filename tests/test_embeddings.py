import numpy as np
from backend.app.embeddings import embed_texts


def test_embed_texts_shape():
  embs = embed_texts(["hello world", "renewable energy"])
  assert isinstance(embs, np.ndarray)
  assert embs.shape[0] == 2
  # MiniLM-L6-v2 is 512 dims
  assert embs.shape[1] == 512


