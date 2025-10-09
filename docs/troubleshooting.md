# Troubleshooting Guide

This document covers common issues and solutions for the Offline Multimodal RAG system.

## Installation Issues

### Docker Installation Problems

**Problem**: Docker build fails with dependency errors

```
Solution:
1. Ensure Docker is up to date
2. Clear Docker cache: docker system prune -a
3. Try building with --no-cache: docker build --no-cache -t offline-multimodal-rag .
```

**Problem**: Docker container runs but app doesn't start

```
Solution:
1. Check logs: docker logs <container_id>
2. Verify Python path: docker run --rm <image> python -c "import sys; print(sys.path)"
3. Check file permissions in container
```

### Python Installation Problems

**Problem**: Import errors after pip install

```
Solution:
1. Verify Python version: python --version (should be 3.11+)
2. Use virtual environment: python -m venv venv && source venv/bin/activate
3. Reinstall dependencies: pip install --force-reinstall -r requirements.txt
```

**Problem**: CUDA/PyTorch installation issues

```
Solution:
1. Install CPU-only version: pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
2. For GPU: pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

## Runtime Issues

### Memory Problems

**Problem**: Out of memory errors during inference

```
Solutions:
1. Reduce model size in config.yaml
2. Lower max_tokens parameter
3. Use smaller embedding models
4. Increase system RAM or use swap space
```

**Problem**: FAISS index too large

```
Solutions:
1. Use smaller chunk sizes
2. Implement index compression
3. Use disk-based FAISS indices
4. Split large documents into smaller files
```

### Model Loading Issues

**Problem**: Models fail to load

```
Solutions:
1. Check model file paths in config.yaml
2. Verify model file integrity
3. Ensure sufficient disk space
4. Check file permissions
```

**Problem**: Embedding models download on every run

```
Solutions:
1. Set offline environment variables:
   export TRANSFORMERS_OFFLINE=1
   export HF_HUB_OFFLINE=1
2. Download models manually and set local paths
3. Use local model cache directory
```

### Performance Issues

**Problem**: Slow inference

```
Solutions:
1. Use GPU acceleration (add --gpus all to docker run)
2. Reduce model size
3. Use quantization (Q4_K_M, Q8_0)
4. Increase batch sizes for embeddings
```

**Problem**: Slow file ingestion

```
Solutions:
1. Process files in parallel
2. Use faster storage (SSD)
3. Optimize chunk sizes
4. Use multiprocessing for large files
```

## File Processing Issues

### PDF Processing

**Problem**: PDF extraction fails

```
Solutions:
1. Install PyMuPDF: pip install PyMuPDF
2. Check PDF file integrity
3. Try different PDF libraries (pdfplumber, pymupdf)
4. Convert PDF to images if text extraction fails
```

**Problem**: PDF with images not processed

```
Solutions:
1. Enable OCR: pip install pytesseract
2. Use image extraction for PDF pages
3. Convert PDF to images first
```

### Audio Processing

**Problem**: Audio transcription fails

```
Solutions:
1. Install whisper.cpp: ./scripts/setup_whisper_cpp.sh
2. Check audio file format support
3. Install ffmpeg for audio conversion
4. Use alternative transcription libraries
```

**Problem**: Audio files too large

```
Solutions:
1. Split audio into smaller segments
2. Use streaming transcription
3. Compress audio files
4. Use lower quality audio
```

### Image Processing

**Problem**: Image embedding fails

```
Solutions:
1. Check image file format support
2. Install Pillow: pip install Pillow
3. Verify image file integrity
4. Use alternative image processing libraries
```

## API Issues

### FastAPI Problems

**Problem**: API endpoints not responding

```
Solutions:
1. Check server logs for errors
2. Verify port availability
3. Check CORS configuration
4. Test with curl: curl http://localhost:8000/health
```

**Problem**: File upload fails

```
Solutions:
1. Check file size limits
2. Verify file permissions
3. Check multipart form handling
4. Test with smaller files first
```

### Gradio Problems

**Problem**: Gradio interface not loading

```
Solutions:
1. Check port conflicts
2. Verify Gradio installation
3. Check browser compatibility
4. Try different port: --port 7861
```

## Database Issues

### FAISS Index Problems

**Problem**: Index corruption

```
Solutions:
1. Rebuild index: POST /index/rebuild
2. Delete corrupted index files
3. Restore from backup
4. Re-ingest all documents
```

**Problem**: Dimension mismatch

```
Solutions:
1. Check embedding model consistency
2. Rebuild index with correct dimensions
3. Verify model configuration
4. Use consistent embedding models
```

### SQLite Database Issues

**Problem**: Database locked

```
Solutions:
1. Check for concurrent access
2. Close all connections properly
3. Use connection pooling
4. Check file permissions
```

## Network Issues

### Offline Mode Problems

**Problem**: Still trying to access internet

```
Solutions:
1. Set environment variables:
   export TRANSFORMERS_OFFLINE=1
   export HF_HUB_OFFLINE=1
2. Use local model paths
3. Disable network interfaces
4. Use air-gapped environment
```

## Configuration Issues

### Config File Problems

**Problem**: Config not loading

```
Solutions:
1. Check YAML syntax
2. Verify file path
3. Check file permissions
4. Use absolute paths
```

**Problem**: Model paths incorrect

```
Solutions:
1. Use absolute paths
2. Check file existence
3. Verify file permissions
4. Test model loading separately
```

## Debugging Tips

### Enable Debug Logging

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Test Individual Components

```bash
# Test embeddings
python -c "from app.embeddings import embed_text; print(embed_text('test'))"

# Test vector store
python -c "from app.vector_store import get_store; print(get_store().status())"

# Test LLM adapter
python -c "from app.llm import build_adapter; adapter = build_adapter({'model_backend': 'mistral'}); print(adapter.generate('test'))"
```

### Check System Resources

```bash
# Memory usage
free -h

# Disk space
df -h

# GPU usage (if available)
nvidia-smi
```

## Getting Help

1. Check this troubleshooting guide first
2. Review the test suite for usage examples
3. Check GitHub issues for similar problems
4. Create a new issue with:
   - System information (OS, Python version, etc.)
   - Error messages and logs
   - Steps to reproduce the issue
   - Configuration files (sanitized)

## Performance Optimization

### For Large Document Collections

1. Use smaller chunk sizes (200-300 characters)
2. Implement document filtering
3. Use hierarchical indexing
4. Consider document clustering

### For Real-time Applications

1. Pre-compute embeddings
2. Use caching layers
3. Implement connection pooling
4. Use async processing

### For Resource-Constrained Systems

1. Use quantized models
2. Implement model pruning
3. Use CPU-only inference
4. Reduce batch sizes
