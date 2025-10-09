import os
from typing import List

from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles
from fastapi.responses import JSONResponse

from .ingestion import extract_any
from .embeddings import embed_text, embed_image
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
    # mount static if not mounted yet
    if not any(r.path == "/storage" for r in app.router.routes):
        app.mount("/storage", StaticFiles(directory=storage_dir), name="storage")
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
    # Placeholder: perform retrieval + generation
    user_message = query.get("message", "")
    return {"answer": f"Echo: {user_message}", "sources": []}


@app.post("/query")
def query(payload: dict):
    try:
        q = payload.get("query", "")
        if not q:
            raise HTTPException(status_code=400, detail="Missing query")
        
        # Use new retriever and LLM modules
        retriever = get_retriever()
        results = retriever.retrieve(q, top_k=5)
        
        if not results:
            return {"answer": "I don't have any relevant information to answer this question.", "sources": []}
        
        # Load LLM adapter
        cfg_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "config.yaml"))
        config = load_config(cfg_path)
        adapter = build_adapter(config)
        
        # Generate answer
        answer = generate_answer(q, results, adapter)
        
        # Create citations
        citations = create_citations(results)
        
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


