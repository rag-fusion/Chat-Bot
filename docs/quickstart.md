# Quick Start Guide

Get up and running with the Offline Multimodal RAG system in minutes.

## Prerequisites

- **Docker** (recommended) or **Python 3.11+**
- **8GB RAM** minimum, 16GB recommended
- **20GB disk space** for models and data

## Option 1: Docker (Easiest)

### Step 1: Download and Load

```bash
# Download the latest release
wget https://github.com/your-repo/offline-multimodal-rag/releases/latest/download/offline-multimodal-rag-0.1.0.tar.gz

# Load the Docker image
docker load < offline-multimodal-rag-0.1.0.tar.gz
```

### Step 2: Run the Application

```bash
# Basic run
docker run -p 7860:7860 offline-multimodal-rag:0.1.0

# With GPU support (if available)
docker run --gpus all -p 7860:7860 offline-multimodal-rag:0.1.0

# With persistent storage
docker run -p 7860:7860 -v $(pwd)/data:/app/storage offline-multimodal-rag:0.1.0
```

### Step 3: Access the Interface

Open your browser to: http://localhost:7860

## Option 2: Native Installation

### Step 1: Clone and Install

```bash
git clone https://github.com/your-repo/offline-multimodal-rag.git
cd offline-multimodal-rag/backend
pip install -r requirements.txt
```

### Step 2: Run the Application

```bash
# Gradio interface (recommended for beginners)
python main.py --interface gradio --port 7860

# FastAPI backend only
python main.py --interface fastapi --port 8000
```

### Step 3: Access the Interface

- **Gradio**: http://localhost:7860
- **FastAPI**: http://localhost:8000/docs

## First Steps

### 1. Upload Documents

1. Go to the **Upload & Ingest** tab
2. Click **Upload Document**
3. Select your files (PDF, DOCX, images, audio)
4. Click **Ingest Document**
5. Wait for processing to complete

### 2. Ask Questions

1. Go to the **Query** tab
2. Type your question in the text box
3. Adjust the number of sources if needed
4. Click **Ask Question**
5. View the answer and sources

### 3. Check Status

1. Go to the **Status** tab
2. Click **Refresh Status**
3. View system information and statistics

## Example Workflow

### Upload a PDF Document

```bash
# Using the API
curl -X POST "http://localhost:8000/ingest" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@document.pdf"
```

### Ask a Question

```bash
# Using the API
curl -X POST "http://localhost:8000/query" \
     -H "Content-Type: application/json" \
     -d '{"query": "What is the main topic of the document?"}'
```

### Check System Status

```bash
# Using the API
curl http://localhost:8000/status
```

## Configuration

### Basic Configuration

Edit `backend/config.yaml`:

```yaml
model_backend: llama_cpp # or gpt4all, mistral
model_path: ./models/mistral-7b-instruct-v0.2.Q4_K_M.gguf
top_k: 5
max_tokens: 512
temperature: 0.2
```

### Environment Variables

```bash
# For offline mode
export TRANSFORMERS_OFFLINE=1
export HF_HUB_OFFLINE=1

# For custom model paths
export TEXT_MODEL_PATH=/path/to/local/text/model
export CLIP_MODEL_PATH=/path/to/local/clip/model
```

## Common Use Cases

### 1. Document Q&A

Upload PDFs and ask questions about their content.

### 2. Image Search

Upload images and find similar content across your collection.

### 3. Audio Transcription

Upload audio files and search through transcripts.

### 4. Cross-Modal Search

Find related content across different file types.

## Troubleshooting

### Common Issues

1. **Out of Memory**: Reduce model size or increase RAM
2. **Slow Performance**: Use GPU acceleration or smaller models
3. **Import Errors**: Check Python version and dependencies
4. **File Upload Fails**: Check file size and format support

### Getting Help

1. Check the [Troubleshooting Guide](docs/troubleshooting.md)
2. Review the [Full Documentation](README.md)
3. Create an issue on GitHub

## Next Steps

- Explore the [API Documentation](http://localhost:8000/docs)
- Try the [Command Line Tools](scripts/)
- Customize the [Configuration](backend/config.yaml)
- Read the [Development Guide](README.md#development)

## Performance Tips

- Use GPU acceleration for faster inference
- Pre-process large documents
- Use appropriate chunk sizes for your content
- Monitor system resources during processing
