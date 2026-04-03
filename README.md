# 🧠 Multimodal RAG Offline Chatbot

A fully **offline**, **privacy-first** Retrieval-Augmented Generation (RAG) chatbot that can ingest and reason over **PDFs, Word documents, images, and audio files** — all running locally on your machine without sending data to any external API.

---

## ✨ Features

- 📄 **Multi-format Ingestion** — Upload PDFs, DOCX, images (PNG/JPG/BMP/TIFF), and audio files (MP3/WAV/M4A/OGG/FLAC)
- 🔍 **Semantic Search** — Chunks documents and embeds them using `sentence-transformers` for vector similarity search with FAISS
- 🤖 **Local LLM Inference** — Uses [Ollama](https://ollama.com/) with `mistral:7b` (or any compatible model) — no internet required
- 🗣️ **Audio Transcription** — Transcribes audio files locally using OpenAI Whisper
- 🖼️ **OCR for Images** — Extracts text from images using Tesseract OCR
- 💬 **Session-based Chat** — Each chat session is isolated with its own document context
- 📑 **Source Citations** — Answers include citations with references to source documents
- 🌐 **React Frontend** — Clean, responsive UI built with React + Vite

---

## 🏗️ Architecture

```
rag-offline-chatbot/
├── backend/
│   ├── app/
│   │   ├── main.py           # FastAPI entrypoint
│   │   ├── config.py         # Model & storage configuration
│   │   ├── embedder/         # Sentence-transformer embedding logic
│   │   ├── ingestion/        # PDF, DOCX, image, audio ingestors
│   │   ├── retriever/        # FAISS vector store retrieval
│   │   ├── vector_store/     # Index management
│   │   ├── rag/              # RAG pipeline (context + LLM query)
│   │   └── routes/           # API routes (upload, query, viewer)
│   ├── storage/              # Per-session file & index storage
│   └── requirements.txt
└── frontend/
    ├── src/
    │   ├── App.jsx            # Main chat UI
    │   ├── api/               # Axios API client
    │   ├── components/        # FileUpload, CitationPanel, viewers
    │   └── hooks/             # useChatId (session management)
    ├── index.html
    └── vite.config.js
```

---

## 🛠️ Tech Stack

| Layer        | Technology                                      |
|--------------|-------------------------------------------------|
| **Frontend** | React 18, Vite 5, react-pdf                     |
| **Backend**  | FastAPI, Uvicorn, Python 3.10+                  |
| **Embeddings** | `sentence-transformers/all-MiniLM-L6-v2`      |
| **Vector DB** | FAISS (CPU)                                    |
| **LLM**      | Ollama (`mistral:7b` or any local model)        |
| **OCR**      | Tesseract via `pytesseract`                     |
| **Audio STT**| OpenAI Whisper (`base` model, runs locally)     |
| **PDF Parse**| `pdfplumber`                                    |
| **DOCX Parse**| `python-docx`                                  |

---

## 📋 Prerequisites

Make sure the following are installed on your machine:

- **Python 3.10+**
- **Node.js 18+** and **npm**
- **[Ollama](https://ollama.com/)** — for local LLM inference
- **[Tesseract OCR](https://github.com/tesseract-ocr/tesseract)** — for image text extraction  
  > Windows: Download installer from [UB Mannheim](https://github.com/UB-Mannheim/tesseract/wiki) and ensure `tesseract` is in your PATH.

---

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/rag-offline-chatbot.git
cd rag-offline-chatbot
```

### 2. Pull the LLM Model via Ollama

```bash
ollama pull mistral:7b
```

> Make sure Ollama is running: `ollama serve`

---

### 3. Backend Setup

```bash
cd backend

# Create and activate virtual environment
python -m venv venv

# Windows
.\venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start the FastAPI server
uvicorn app.main:app --reload --port 8000
```
<!-- run backend must run in terminal both command together -->
.\venv\Scripts\activate
uvicorn app.main:app --reload --port 8000


The API will be available at: `http://localhost:8000`  
Interactive docs: `http://localhost:8000/docs`

---

### 4. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start the dev server
npm run dev
```

The app will be available at: `http://localhost:5173`

---

## 📡 API Endpoints

| Method | Endpoint              | Description                          |
|--------|-----------------------|--------------------------------------|
| `GET`  | `/health`             | Health check                         |
| `POST` | `/upload`             | Upload a file and ingest it into RAG |
| `POST` | `/query`              | Ask a question against ingested docs |
| `GET`  | `/viewer/{chat_id}/{filename}` | Serve original uploaded files |

---

## ⚙️ Configuration

Key settings are in `backend/app/config.py`:

| Setting               | Default                              | Description                        |
|-----------------------|--------------------------------------|------------------------------------|
| `EMBED_MODEL_NAME`    | `all-MiniLM-L6-v2`                   | Sentence-transformer model         |
| `OLLAMA_MODEL`        | `mistral:7b`                         | Local LLM via Ollama               |
| `OLLAMA_BASE_URL`     | `http://localhost:11434`             | Ollama server URL                  |
| `CHUNK_SIZE`          | `400`                                | Token chunk size for splitting     |
| `CHUNK_OVERLAP`       | `80`                                 | Overlap between chunks             |
| `TOP_K`               | `5`                                  | Number of context chunks retrieved |
| `SIMILARITY_THRESHOLD`| `0.25`                               | Minimum similarity score to use    |
| `WHISPER_MODEL`       | `base`                               | Whisper model size for audio STT   |

---

## 📁 Supported File Types

| Type    | Extensions                              |
|---------|-----------------------------------------|
| PDF     | `.pdf`                                  |
| Word    | `.docx`, `.doc`                         |
| Image   | `.png`, `.jpg`, `.jpeg`, `.bmp`, `.tiff`|
| Audio   | `.mp3`, `.wav`, `.m4a`, `.ogg`, `.flac` |

---

## 🔒 Privacy

All processing happens **100% locally**:
- No data is sent to OpenAI, Google, or any external service
- LLM inference via Ollama (local)
- Embeddings via Sentence-Transformers (local)
- Speech-to-text via Whisper (local)
- OCR via Tesseract (local)

---

## 🤝 Contributing

Contributions are welcome! Please open an issue or submit a pull request.

---

## 📄 License

This project is open-source and available under the [MIT License](LICENSE).


Ensure your system dependencies are installed via tesseract-ocr and ffmpeg.

Start the backend: cd backend -> pip install -r requirements.txt -> uvicorn app.main:app --reload --port 8000.

Start the frontend: cd frontend -> npm install -> npm run dev.

Run your local Ollama server in a separate terminal: ollama pull mistral:7b, followed by ollama serve.