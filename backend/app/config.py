from pathlib import Path

BASE_DIR     = Path(__file__).parent.parent
STORAGE_DIR  = BASE_DIR / "storage" / "sessions"

EMBED_MODEL_NAME     = "sentence-transformers/all-MiniLM-L6-v2"
WHISPER_MODEL        = "base"
OLLAMA_BASE_URL      = "http://localhost:11434"
OLLAMA_MODEL         = "mistral:7b"

EMBED_DIM            = 384
CHUNK_SIZE           = 400
CHUNK_OVERLAP        = 80
TOP_K                = 5
SIMILARITY_THRESHOLD = 0.25

SUPPORTED_EXTENSIONS = {
    ".pdf":  "pdf",
    ".docx": "docx",
    ".doc":  "docx",
    ".png":  "image",
    ".jpg":  "image",
    ".jpeg": "image",
    ".bmp":  "image",
    ".tiff": "image",
    ".mp3":  "audio",
    ".wav":  "audio",
    ".m4a":  "audio",
    ".ogg":  "audio",
    ".flac": "audio",
}

def get_session_dir(chat_id: str) -> Path:
    path = STORAGE_DIR / chat_id
    path.mkdir(parents=True, exist_ok=True)
    return path

def get_files_dir(chat_id: str) -> Path:
    path = get_session_dir(chat_id) / "files"
    path.mkdir(parents=True, exist_ok=True)
    return path
