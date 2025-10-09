# Offline Multimodal RAG System

A fully offline Retrieval-Augmented Generation (RAG) system that supports multiple modalities including PDF, DOCX, images, and audio files. All processing happens locally without requiring internet connectivity.

## Features

- **Fully Offline**: No internet connection required after initial setup
- **Multimodal Support**: PDF, DOCX, images, and audio files
- **Local LLM Integration**: Supports GPT4All, Llama.cpp, and Mistral
- **Cross-Modal Search**: Find related content across different file types
- **Dual Interface**: Both Gradio web UI and FastAPI backend
- **Docker Support**: Easy deployment with Docker containers
- **Citation Support**: Proper source attribution and linking

## Quick Start

### Option 1: Docker (Recommended)

1. **Download the release**:

   ```bash
   # Download from GitHub Releases
   wget https://github.com/your-repo/offline-multimodal-rag/releases/latest/download/offline-multimodal-rag-0.1.0.tar.gz
   ```

2. **Load and run**:

   ```bash
   docker load < offline-multimodal-rag-0.1.0.tar.gz
   docker run -p 7860:7860 offline-multimodal-rag:0.1.0
   ```

3. **Access the interface**:
   Open http://localhost:7860 in your browser

### Option 2: Native Installation

1. **Clone the repository**:

   ```bash
   git clone https://github.com/your-repo/offline-multimodal-rag.git
   cd offline-multimodal-rag
   ```

2. **Install dependencies**:

   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. **Run the application**:

   ```bash
   # Gradio interface (default)
   python main.py --interface gradio --port 7860

   # FastAPI backend only
   python main.py --interface fastapi --port 8000
   ```

## System Requirements

- **Minimum**: 8GB RAM, 20GB disk space
- **Recommended**: 16GB RAM, 50GB disk space, GPU for faster inference
- **OS**: Windows, macOS, or Linux
- **Python**: 3.11+ (for native installation)
- **Docker**: Latest version (for Docker installation)

## Architecture

The system is organized into modular components:

```
app/
├── ingestion/          # Document processing (PDF, DOCX, images, audio)
├── embeddings/         # Embedding generation (text and image)
├── vector_store/       # FAISS vector database
├── retriever/          # Search and reranking
├── llm/               # Local LLM adapters
├── ui/                # Gradio web interface
└── utils/             # Cross-modal linking and citations
```

## Configuration

Edit `backend/config.yaml` to configure the system:

```yaml
model_backend: llama_cpp # options: gpt4all | llama_cpp | mistral
model_path: ./models/mistral-7b-instruct-v0.2.Q4_K_M.gguf
top_k: 5
max_tokens: 512
temperature: 0.2
```

## Usage

### Web Interface (Gradio)

1. **Upload Documents**: Use the upload tab to add PDF, DOCX, images, or audio files
2. **Ask Questions**: Use the query tab to ask questions about your documents
3. **View Sources**: See citations and source references for each answer

### API Interface (FastAPI)

```python
import requests

# Upload a document
with open("document.pdf", "rb") as f:
    response = requests.post("http://localhost:8000/ingest", files={"file": f})

# Query the system
response = requests.post("http://localhost:8000/query",
                        json={"query": "What is the main topic?"})
result = response.json()
print(result["answer"])
```

### Command Line Interface

```bash
# Ingest all files from a directory
python scripts/ingest_all.py --data-dir ./documents --index ./storage/faiss.index

# Run tests
python -m pytest tests/ -v
```

## Supported File Types

- **Documents**: PDF, DOCX, TXT, MD
- **Images**: PNG, JPG, JPEG, GIF, BMP, WEBP
- **Audio**: MP3, WAV, M4A, FLAC, OGG

## Model Requirements

### Text Embeddings

- **Default**: `sentence-transformers/all-MiniLM-L6-v2` (384 dimensions)
- **Offline**: Download model files locally and set `TEXT_MODEL_PATH` environment variable

### Image Embeddings

- **Default**: OpenCLIP ViT-B-32
- **Offline**: Download model weights and set `CLIP_MODEL_PATH` environment variable

### LLM Models

- **GPT4All**: Download from [GPT4All](https://gpt4all.io/)
- **Llama.cpp**: Download GGUF format models
- **Mistral**: Use provided Mistral-7B model or download others

## Development

### Project Structure

```
offline-multimodal-rag/
├── backend/
│   ├── app/                 # Main application code
│   ├── scripts/            # Build and utility scripts
│   ├── tests/              # Test suite
│   ├── requirements.txt    # Python dependencies
│   └── config.yaml         # Configuration file
├── frontend/               # React frontend (optional)
├── .github/workflows/      # CI/CD workflows
└── main.py                # Entry point
```

### Running Tests

```bash
cd backend
python -m pytest tests/ -v
```

### Building Docker Image

```bash
cd backend
docker build -t offline-multimodal-rag:latest -f scripts/docker/Dockerfile .
```

### Creating Release

```bash
cd backend
chmod +x scripts/build_release.sh
./scripts/build_release.sh 0.1.0
```

## Troubleshooting

### Common Issues

1. **Out of Memory**: Reduce model size or increase system RAM
2. **Slow Inference**: Use GPU acceleration with `--gpus all` in Docker
3. **Import Errors**: Ensure all dependencies are installed correctly
4. **Model Download**: Set offline environment variables for local models

### Environment Variables

```bash
# Offline mode
export TRANSFORMERS_OFFLINE=1
export HF_HUB_OFFLINE=1

# Model paths
export TEXT_MODEL_PATH=/path/to/local/text/model
export CLIP_MODEL_PATH=/path/to/local/clip/model

# Whisper (for audio)
export WHISPER_CPP_BIN=/path/to/whisper/main
export WHISPER_CPP_MODEL=/path/to/whisper/model.bin
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [FAISS](https://github.com/facebookresearch/faiss) for vector search
- [Sentence Transformers](https://www.sbert.net/) for text embeddings
- [OpenCLIP](https://github.com/mlfoundations/open_clip) for image embeddings
- [Gradio](https://gradio.app/) for the web interface
- [FastAPI](https://fastapi.tiangolo.com/) for the API backend

## Support

For issues and questions:

- Create an issue on GitHub
- Check the troubleshooting section
- Review the test suite for usage examples
