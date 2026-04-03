import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from app.config import EMBED_MODEL_NAME

_model = None

def get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        print(f"[Embedder] Loading model {EMBED_MODEL_NAME}...")
        _model = SentenceTransformer(EMBED_MODEL_NAME)
        print("[Embedder] Model ready.")
    return _model

def embed_texts(texts: list[str]) -> np.ndarray:
    model = get_model()
    embeddings = model.encode(
        texts,
        convert_to_numpy=True,
        show_progress_bar=False,
        batch_size=32
    )
    embeddings = embeddings.astype(np.float32)
    faiss.normalize_L2(embeddings)
    return embeddings

def embed_single(text: str) -> np.ndarray:
    return embed_texts([text])[0]
