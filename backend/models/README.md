# Backend Models Directory Structure

This directory contains all the AI models used by the RAG system, organized by type:

## Directory Structure

```
backend/models/
├── llm/                    # Large Language Models
│   └── mistral-7b-instruct-v0.2.Q4_K_M.gguf
├── embeddings/             # Text Embedding Models
│   └── all-MiniLM-L6-v2/
├── clip/                   # Image Embedding Models
│   └── ViT-B-32.pt
└── whisper/               # Audio Processing Models
    └── small.pt
```

## Model Types

### LLM (Large Language Models)

- **Purpose**: Generate responses to user queries
- **Current Model**: Mistral-7B-Instruct-v0.2 (Q4_K_M quantization)
- **Format**: GGUF files
- **Location**: `models/llm/`

### Embeddings (Text)

- **Purpose**: Convert text to vector embeddings for similarity search
- **Current Model**: all-MiniLM-L6-v2
- **Format**: Hugging Face transformers format
- **Location**: `models/embeddings/`

### CLIP (Image Embeddings)

- **Purpose**: Convert images to vector embeddings for multimodal search
- **Current Model**: CLIP ViT-B-32
- **Format**: Hugging Face transformers format
- **Location**: `models/clip/`

### Whisper (Audio Processing)

- **Purpose**: Transcribe audio files to text
- **Current Model**: whisper-small
- **Format**: Hugging Face transformers format
- **Location**: `models/whisper/`

## Adding New Models

1. **Download the model** to the appropriate subdirectory
2. **Update configuration** in `backend/config.yaml`
3. **Restart the application** to load the new model

## Model Downloads

### 1. Text Embeddings (all-MiniLM-L6-v2)

**Purpose**: Convert text to 384-dimensional vectors for similarity search

**Download Options**:

**Option A - Automatic (Recommended)**:
```bash
python scripts/download_models.py
```

**Option B - Manual Python**:
```bash
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2').save('./models/embeddings/all-MiniLM-L6-v2')"
```

**Option C - Direct Download**:
- **Hugging Face**: https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2
- **Size**: ~90MB
- **Files needed**: All files from the repository

### 2. Image Embeddings (CLIP ViT-B-32)

**Purpose**: Convert images to 512-dimensional vectors for multimodal search

**Download Options**:

**Option A - Automatic (Recommended)**:
```bash
python scripts/download_models.py
```

**Option B - Manual Python**:
```bash
python -c "import clip; clip.load('ViT-B/32', download_root='./models/clip')"
```

**Option C - Direct Download**:
- **Hugging Face**: https://huggingface.co/openai/clip-vit-base-patch32
- **Size**: ~580MB
- **Files needed**: `pytorch_model.bin` and `config.json`

### 3. Audio Processing (Whisper Small)

**Purpose**: Transcribe audio files (MP3, WAV, etc.) to text

**Download Options**:

**Option A - Automatic (Recommended)**:
```bash
python scripts/download_models.py
```

**Option B - Manual Python**:
```bash
python -c "import whisper; whisper.load_model('small', download_root='./models/whisper')"
```

**Option C - Direct Download**:
- **Hugging Face**: https://huggingface.co/openai/whisper-small
- **Size**: ~244MB
- **Files needed**: `pytorch_model.bin` and `config.json`

### 4. Large Language Model (Mistral-7B-Instruct)

**Purpose**: Generate responses to user queries using local LLM

**Download Options**:

**Option A - Direct Download (Recommended)**:
- **Hugging Face**: https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF
- **File**: `mistral-7b-instruct-v0.2.Q4_K_M.gguf`
- **Size**: ~4.1GB
- **Place in**: `backend/models/llm/`

**Option B - Alternative Models**:
- **Llama 2 7B**: https://huggingface.co/TheBloke/Llama-2-7B-Chat-GGUF
- **CodeLlama 7B**: https://huggingface.co/TheBloke/CodeLlama-7B-Instruct-GGUF
- **Phi-3 Mini**: https://huggingface.co/microsoft/Phi-3-mini-4k-instruct-gguf

**Option C - Using wget/curl**:
```bash
# Create directory
mkdir -p backend/models/llm

# Download Mistral (4.1GB)
wget https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF/resolve/main/mistral-7b-instruct-v0.2.Q4_K_M.gguf -O backend/models/llm/mistral-7b-instruct-v0.2.Q4_K_M.gguf
```

### Quick Setup (All Models)

**One-command setup** (requires internet):
```bash
# Download all models automatically
python scripts/download_models.py

# Download LLM manually (4.1GB)
wget https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF/resolve/main/mistral-7b-instruct-v0.2.Q4_K_M.gguf -O backend/models/llm/mistral-7b-instruct-v0.2.Q4_K_M.gguf
```

**Total disk space needed**: ~5GB

## Configuration

Update `backend/config.yaml` to point to your models:

```yaml
model_backend: llama_cpp
model_path: ./models/llm/your-model.gguf
```

## Environment Variables

For offline usage, set these environment variables:

```bash
export TRANSFORMERS_OFFLINE=1
export HF_HUB_OFFLINE=1
export TEXT_MODEL_PATH=./backend/models/embeddings/all-MiniLM-L6-v2
export CLIP_MODEL_PATH=./backend/models/clip/ViT-B-32.pt
export WHISPER_CPP_MODEL=./backend/models/whisper/small.pt
```
