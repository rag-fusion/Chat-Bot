import httpx
from app.retriever.retriever import retrieve, build_context
from app.config import OLLAMA_BASE_URL, OLLAMA_MODEL

SYSTEM_PROMPT = """You are a precise document assistant.

STRICT RULES — follow every one:
1. Answer ONLY from the provided context below.
2. If the answer is NOT in the context, respond exactly: "I could not find this information in the uploaded documents."
3. Do NOT guess. Do NOT use outside knowledge. Do NOT infer.
4. Cite every fact using [1], [2], etc. matching the context numbers.
5. Include ONLY citation numbers you actually used.
6. Keep answers factual and concise."""


def ask(chat_id: str, question: str) -> dict:
    chunks = retrieve(chat_id, question)

    if not chunks:
        return {
            "answer": "No relevant content found. Please upload your documents first.",
            "citations": [],
            "citation_map": {}
        }

    context, citation_map = build_context(chunks)

    prompt = f"""Context:
{context}

Question: {question}

Answer (cite with [1],[2] etc.):"""

    try:
        resp = httpx.post(
            f"{OLLAMA_BASE_URL}/api/chat",
            json={
                "model": OLLAMA_MODEL,
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user",   "content": prompt}
                ],
                "stream": False
            },
            timeout=120.0
        )
        resp.raise_for_status()
        answer = resp.json()["message"]["content"].strip()
    except Exception as e:
        return {
            "answer": f"LLM error: {str(e)}. Is Ollama running? Run: ollama serve",
            "citations": [],
            "citation_map": {}
        }

    # Only include citations that actually appear in the answer text
    used_citations = []
    for num, vid in citation_map.items():
        if f"[{num}]" in answer:
            chunk = next((c for c in chunks if c["vector_id"] == vid), None)
            if chunk:
                used_citations.append({
                    "number":       num,
                    "vector_id":    vid,
                    "file_name":    chunk["file_name"],
                    "modality":     chunk["modality"],
                    "page":         chunk.get("page"),
                    "start_time":   chunk.get("start_time"),
                    "end_time":     chunk.get("end_time"),
                    "text_preview": chunk["text"][:200],
                })

    return {
        "answer": answer,
        "citations": used_citations,
        "citation_map": citation_map
    }
