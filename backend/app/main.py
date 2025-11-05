import os
from typing import List

from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, RedirectResponse, PlainTextResponse

from .ingestion import extract_any
from .embeddings import embed_text, embed_image, get_text_model, get_clip
from .vector_store import get_store
from .retriever import get_retriever
from .llm import build_adapter, load_config, generate_answer
from .utils import create_citations
import faiss
import numpy as np

app = FastAPI(title="RAG Offline Chatbot Backend", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup_init():
    """Preload models and mount storage for faster first use."""
    # Mount storage once at startup
    storage_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "storage"))
    os.makedirs(storage_dir, exist_ok=True)
    if not any(getattr(r, "path", None) == "/storage" for r in app.router.routes):
        app.mount("/storage", StaticFiles(directory=storage_dir), name="storage")
    # Also expose files under a stable /files route for direct linking
    if not any(getattr(r, "path", None) == "/files" for r in app.router.routes):
        app.mount("/files", StaticFiles(directory=storage_dir), name="files")

    # Preload embedding models (text + clip) to avoid first-request delays
    try:
        get_text_model()
    except Exception as e:
        print(f"[startup] Warning: text model preload failed: {e}")
    try:
        get_clip()
    except Exception as e:
        print(f"[startup] Warning: CLIP model preload failed: {e}")

    # Initialize global store and retriever
    try:
        _ = get_store()
        _ = get_retriever()
    except Exception as e:
        print(f"[startup] Warning: store/retriever init failed: {e}")

    # Preload LLM adapter
    try:
        cfg_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "config.yaml"))
        config = load_config(cfg_path)
        global _llm_adapter
        _llm_adapter = build_adapter(config)
    except Exception as e:
        print(f"[startup] Warning: LLM adapter preload failed: {e}")


@app.get("/")
def root():
    """Root endpoint with API information."""
    return {
        "message": "RAG Offline Chatbot API",
        "version": "0.1.0",
        "endpoints": {
            "health": "/health",
            "upload": "/ingest",
            "query": "/query",
            "search": "/search/similarity",
            "status": "/status",
            "docs": "/docs"
        },
        "frontend": "http://localhost:5173"
    }


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/ingest")
async def ingest(file: UploadFile = File(...)):
    storage_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "storage"))
    os.makedirs(storage_dir, exist_ok=True)
    # storage is mounted on startup; ensure dir exists
    if not file.filename:
        raise HTTPException(status_code=400, detail="Missing filename")
    dest_path = os.path.join(storage_dir, file.filename)
    data = await file.read()
    with open(dest_path, "wb") as f:
        f.write(data)

    # Extract chunks using new ingestion module
    chunks = extract_any(dest_path, file.filename, file.content_type or "")
    
    # Generate embeddings and store using new vector store
    store = get_store()
    items = []
    
    for chunk in chunks:
        if chunk.file_type == 'image':
            embedding = embed_image(chunk.filepath)
        else:
            embedding = embed_text(chunk.content)
        
        items.append({
            'embedding': embedding[0],  # Remove batch dimension
            'metadata': {
                'content': chunk.content,
                'file_name': chunk.file_name,
                'file_type': chunk.file_type,
                'page_number': chunk.page_number,
                'timestamp': chunk.timestamp,
                'filepath': chunk.filepath,
                'width': getattr(chunk, 'width', None),
                'height': getattr(chunk, 'height', None),
                'bbox': getattr(chunk, 'bbox', None),
                'char_start': getattr(chunk, 'char_start', None),
                'char_end': getattr(chunk, 'char_end', None),
                'modality': chunk.file_type
            }
        })
    
    vectors_added = store.upsert(items)
    return {"chunks_added": len(chunks), "vectors_indexed": vectors_added, "file": file.filename}


@app.post("/api/chat")
async def chat(query: dict):
    user_message = query.get("message", "")
    return {"answer": f"Echo: {user_message}", "sources": []}


@app.post("/query")
def query(payload: dict):
    try:
        q = payload.get("query", "")
        if not q:
            raise HTTPException(status_code=400, detail="Missing query")
        
        # Use retriever and global LLM adapter
        retriever = get_retriever()
        results = retriever.retrieve(q, top_k=5)
        
        if not results:
            return {"answer": "I don't have any relevant information to answer this question.", "sources": []}
        
        # Reuse preloaded adapter if available
        global _llm_adapter
        if _llm_adapter is None:
            cfg_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "config.yaml"))
            config = load_config(cfg_path)
            _llm_adapter = build_adapter(config)
        adapter = _llm_adapter
        
        # Generate answer
        answer = generate_answer(q, results, adapter)
        
        # Create citations (include direct URL under /files, with #page for PDFs)
        citations = []
        for idx, r in enumerate(results, start=1):
            file_name = r.get("file_name")
            file_type = r.get("modality", r.get("file_type", "text"))
            page_num = r.get("page_number")
            base_path = f"/files/{file_name}" if file_name else None
            if base_path and file_type == "pdf" and page_num:
                url = f"{base_path}#page={page_num}"
            else:
                url = base_path or None

            citations.append({
                # New minimal schema for fast linking
                "id": idx,
                "source": file_name,
                "page": page_num,
                "url": url,
                # Backward/compat fields used by UI components
                "title": file_name,
                "file": file_name,
                "type": file_type,
                "timestamp": r.get("timestamp"),
                "filepath": r.get("filepath"),
                "text": r.get("content", ""),
                "score": r.get("score", 0.0),
            })
        
        return {"answer": answer, "sources": citations}
        
    except HTTPException:
        # re-raise FastAPI HTTP errors as-is
        raise
    except Exception as e:
        # surface underlying backend errors to the client to aid debugging
        raise HTTPException(status_code=500, detail=f"Query failed: {e}")


@app.get("/status")
def status():
    store = get_store()
    return store.status()


@app.get("/source/{filename}")
def get_source(filename: str, request: Request):
    """Serve source content or redirect to file under storage.

    - If a text sidecar exists (e.g., extracted .txt), return it as plain text.
    - Otherwise redirect to raw file under /storage for frontend rendering (PDF/image/audio).
    """
    storage_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "storage"))
    file_path = os.path.join(storage_dir, filename)

    # Prefer a sidecar extracted text if available
    txt_path = file_path + ".txt"
    if os.path.exists(txt_path):
        try:
            with open(txt_path, "r", encoding="utf-8", errors="ignore") as f:
                return PlainTextResponse(f.read())
        except Exception:
            pass

    # Fallbacks to locate the file robustly
    # 1) Exact name
    if os.path.exists(file_path):
        return RedirectResponse(url=str(request.base_url) + f"storage/{filename}")

    # 2) Case-insensitive match within storage directory
    try:
        for entry in os.listdir(storage_dir):
            if entry.lower() == filename.lower():
                return RedirectResponse(url=str(request.base_url) + f"storage/{entry}")
    except Exception:
        pass

    # 3) Lookup by metadata.json (match file_name and use its stored filepath)
    try:
        import json
        metadata_path = os.path.join(storage_dir, "metadata.json")
        if os.path.exists(metadata_path):
            with open(metadata_path, "r", encoding="utf-8", errors="ignore") as f:
                metadata = json.load(f)
            # Find entries where file_name matches
            candidates = [v for v in metadata.values() if v.get("file_name", "").lower() == filename.lower()]
            if candidates:
                # Prefer an existing file on disk by its basename
                base = os.path.basename(candidates[0].get("filepath", ""))
                if base:
                    candidate_path = os.path.join(storage_dir, base)
                    if os.path.exists(candidate_path):
                        return RedirectResponse(url=str(request.base_url) + f"storage/{base}")
            # As a last resort, aggregate text content for this filename and return as plain text
            texts = [v.get("content", "") for v in metadata.values() if v.get("file_name", "").lower() == filename.lower()]
            if texts:
                combined = "\n\n---\n\n".join(t for t in texts if t)
                if combined.strip():
                    return PlainTextResponse(combined)
    except Exception:
        pass

    raise HTTPException(status_code=404, detail="Source not found")


@app.post("/index/rebuild")
def rebuild():
    store = get_store()
    store.rebuild_from_metadata()
    return store.status()




@app.post("/search/similarity")
async def similarity(request: Request, mode: str = "text", file: UploadFile | None = None):
    k = 5
    query_emb = None
    store = get_store()
    
    if store.index.ntotal == 0:
        return {"results": []}

    # Parse JSON body
    body = await request.json()
    
    if mode == "text":
        query = body.get("query", "")
        k = int(body.get("k", 5))
        if not query:
            raise HTTPException(status_code=400, detail="Missing query")
        query_emb = embed_text(query)
    elif mode == "image":
        if file is None:
            raise HTTPException(status_code=400, detail="Missing image file")
        data = await file.read()
        tmp_path = os.path.join(os.path.dirname(__file__), "..", "storage", f"_query_{file.filename}")
        os.makedirs(os.path.dirname(tmp_path), exist_ok=True)
        with open(tmp_path, "wb") as f:
            f.write(data)
        query_emb = embed_image(os.path.abspath(tmp_path))
        try:
            os.remove(tmp_path)
        except Exception:
            pass
        k = int(body.get("k", 5))
    else:
        # cross-modal defaults to text embedding of query string
        query = body.get("query", "")
        k = int(body.get("k", 5))
        if not query:
            raise HTTPException(status_code=400, detail="Missing query for cross mode")
        query_emb = embed_text(query)

    results = store.search(query_emb, k)
    return {"results": results}


