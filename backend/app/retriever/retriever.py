from app.embedder.embedder import embed_single
from app.vector_store.faiss_store import get_store
from app.config import TOP_K, SIMILARITY_THRESHOLD


def retrieve(chat_id: str, query: str, k: int = TOP_K) -> list[dict]:
    store = get_store(chat_id)
    query_vec = embed_single(query)
    return store.search(query_vec, k=k, threshold=SIMILARITY_THRESHOLD)


def build_context(chunks: list[dict]) -> tuple[str, dict]:
    """
    Returns:
      context_str  — numbered text block for LLM prompt
      citation_map — {citation_number: vector_id}
    """
    lines = []
    citation_map = {}

    for i, chunk in enumerate(chunks, start=1):
        citation_map[i] = chunk["vector_id"]
        m = chunk.get("modality", "?")

        if m in ("pdf", "docx"):
            header = f"[{i}] file={chunk['file_name']} page={chunk.get('page','N/A')} type={m}"
        elif m == "audio":
            header = f"[{i}] file={chunk['file_name']} time={chunk.get('start_time',0)}s–{chunk.get('end_time',0)}s type=audio"
        elif m == "image":
            header = f"[{i}] file={chunk['file_name']} type=image"
        else:
            header = f"[{i}] file={chunk['file_name']}"

        lines.append(f"{header}\n{chunk['text']}")

    return "\n\n".join(lines), citation_map
