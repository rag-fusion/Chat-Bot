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

### Text Embeddings

```bash
# Download all-MiniLM-L6-v2
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2').save('./models/embeddings/all-MiniLM-L6-v2')"
```

### Image Embeddings

```bash
# Download CLIP model
python -c "import clip; clip.load('ViT-B/32', download_root='./models/clip')"
```

### Audio Processing

```bash
# Download Whisper model
python -c "import whisper; whisper.load_model('small', download_root='./models/whisper')"
```

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
