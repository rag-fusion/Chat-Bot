## RAG Offline Chatbot

Fully offline Retrieval-Augmented Generation (RAG) with text, image, and audio support. Runs locally with a simple UI (Gradio) and a FastAPI backend. Optional React frontend included.

### What you get
- **Offline-first**: after setup, no internet needed
- **Multimodal**: PDF/DOCX/TXT/MD, images, audio
- **Local models**: sentence-transformers, CLIP, Whisper, and a local LLM (GGUF)
- **Two ways to use**: Web UI or REST API

---

### 1) Fork & clone

```bash
git fork <this repo>  # on GitHub, then
git clone https://github.com/<your-username>/rag-offline-chatbot.git
cd rag-offline-chatbot
```

### 2) Requirements
- Python 3.11+
- Node.js 18+ (only if using the React frontend)
- Windows, macOS, or Linux

### 3) Setup (Backend)

Windows PowerShell:
```powershell
python -m venv .venv
.\.venv\Scripts\Activate
pip install -r backend\requirements.txt
```

macOS/Linux:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
```

Optional: download models automatically (first run needs internet):
```bash
python scripts/download_models.py
```

The default config is in `backend/config.yaml`:
```yaml
model_backend: llama_cpp
model_path: ./models/llm/mistral-7b-instruct-v0.2.Q4_K_M.gguf
top_k: 5
max_tokens: 512
temperature: 0.2
```
Place your GGUF LLM at `backend/models/llm/` or update `model_path`.

### 4) Run

Gradio UI (recommended for first run):
```bash
python main.py --interface gradio --port 7860
```
Open `http://localhost:7860`.

FastAPI API server:
```bash
python main.py --interface fastapi --port 8000
```
Docs at `http://localhost:8000/docs`.

Frontend (optional React app):
```bash
cd frontend
npm install
npm run dev
# open http://localhost:5173
```

### 5) Docker (optional)

Using Compose (backend + vite preview):
```bash
docker compose up --build
# Backend on 8000, frontend on 5173
```
Model folders on the host are mounted from `./backend/models`.

---

### Use it

- Web UI: upload files, then ask a question
- REST API examples:

Upload a file:
```bash
curl -F "file=@document.pdf" http://localhost:8000/ingest
```

Ask a question:
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query":"What is the main topic?"}'
```

Rebuild index (if metadata present):
```bash
curl -X POST http://localhost:8000/index/rebuild
```

Status:
```bash
curl http://localhost:8000/status
```

---

### Project structure (short)
```
backend/
  app/              # API, ingestion, embeddings, retriever, vector store
  models/           # llm/, embeddings/, clip/, whisper/
  storage/          # faiss index + metadata
  config.yaml
frontend/           # optional React UI (vite)
main.py             # entrypoint (gradio or fastapi)
cli.py              # interactive CLI
```

### Troubleshooting
- "FAISS not found" on Windows: ensure `faiss-cpu` installed from `requirements.txt` inside venv
- Torch/CPU slow: try a smaller GGUF or enable CUDA if available
- Port already in use: change `--port` or stop the conflicting app
- No answers: check you ingested files and that `backend/storage` is writable
- Model not found: verify `backend/config.yaml` `model_path`

### Contributing
1. Fork → create branch → commit
2. Run tests: `pytest -v` (inside venv)
3. Open a PR

### License
MIT — see `LICENSE`
