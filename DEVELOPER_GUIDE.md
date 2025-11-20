# Image Understanding Pipeline - Developer Quick Reference

## Quick Diagnosis Checklist

If image queries aren't working, run through this checklist:

### 1. Image Embedding Generation

```python
from app.embeddings import embed_image
import numpy as np

# Test an image
embedding = embed_image("path/to/image.png")

# Check these:
assert embedding.shape == (1, 512), f"Shape wrong: {embedding.shape}"
assert embedding.dtype == np.float32, f"Dtype wrong: {embedding.dtype}"
norm = np.linalg.norm(embedding[0])
assert 0.95 < norm <= 1.05, f"Norm wrong: {norm}"
assert not np.allclose(embedding, 0), "Embedding is all zeros!"
print("✓ Image embedding generation working")
```

### 2. OCR Text Extraction

```python
from app.ingestion.image_processor import detect_text_in_image

# Test OCR
text = detect_text_in_image("path/to/image.png")
if text:
    print(f"✓ OCR extracted {len(text)} chars: {text[:50]}...")
else:
    print("⚠ No OCR text. Is pytesseract installed?")
    print("   Install: pip install pytesseract")
```

### 3. Image Chunk Creation

```python
from app.ingestion.image_processor import image_to_embedding

chunks = image_to_embedding("path/to/image.png", "image.png")
chunk = chunks[0]

# Verify content
assert chunk.file_type == "image"
assert "Image:" in chunk.content
assert chunk.width > 0
assert chunk.height > 0
print(f"✓ Chunk content: {chunk.content[:80]}...")
```

### 4. Vector Store Status

```python
from app.vector_store import get_store

store = get_store()
status = store.status()
print(f"Total vectors: {status['vectors']}")
print(f"File count: {status['files']}")
print(f"Modalities: {status['modalities']}")
print(f"Dimension: {status['dimension']}")

# Should show:
# - vectors > 0
# - 'image' in modalities
# - dimension == 512
```

### 5. Image Retrieval Test

```python
from app.embeddings import embed_text
from app.vector_store import get_store

query_text = "image text you're looking for"
query_emb = embed_text(query_text)

store = get_store()
results = store.search(query_emb, top_k=5)

for result in results:
    print(f"File: {result['file_name']}")
    print(f"Score: {result['score']:.3f}")
    print(f"Content: {result['content'][:60]}...")
    print()

# Should show:
# - Image filenames in results
# - Scores > 0.7
# - Content includes OCR text
```

### 6. Prompt Formatting Test

```python
from app.llm.prompts import build_prompt, build_multimodal_prompt

sources = [
    {
        'file_name': 'screenshot.png',
        'file_type': 'image',
        'modality': 'image',
        'content': 'Image: screenshot.png | OCR Text: storage info'
    }
]

prompt = build_prompt("test query", sources)
print(prompt)
# Should contain: [1], screenshot.png, (IMAGE) or similar label

multimodal_prompt = build_multimodal_prompt("test query", sources)
print(multimodal_prompt)
# Should contain: "IMAGE SOURCES", "[1]", "screenshot.png"
```

---

## Common Issues & Fixes

### Issue: "CUDA operation attempted" Error

**Symptom:**

```
RuntimeError: Could not run 'aten::empty_strided' with arguments from the 'CUDA' backend
```

**Fix:** Already handled! But if still seeing it:

```bash
# Clear CUDA environment
export CUDA_VISIBLE_DEVICES=""

# Or in Python:
import os
os.environ['CUDA_VISIBLE_DEVICES'] = ''
```

### Issue: "No OCR Text Extracted"

**Symptom:**

```
Image: screenshot.png | Dimensions: 1920x1080 pixels
(No OCR text)
```

**Solution:**

```bash
# Install pytesseract
pip install pytesseract

# Install Tesseract binary
# Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki
# Linux: sudo apt-get install tesseract-ocr
# macOS: brew install tesseract
```

### Issue: Image Embedding Shape is (512,) not (1, 512)

**Symptom:**

```
AssertionError: Expected shape (1, 512), got (512,)
```

**Fix:** This is now prevented by assertions in `embed_image()`. If you see it:

1. Update backend/app/embeddings/generate.py (should be fixed)
2. Run: `python test_image_understanding.py`

### Issue: Images Not Appearing in Results

**Diagnosis:**

```python
# 1. Check if images are indexed
store = get_store()
print(f"Total vectors: {store.index.ntotal}")

# 2. Check if modalities are correct
status = store.status()
print(f"Modalities: {status['modalities']}")  # Should include 'image'

# 3. Check image metadata in store
for vector_id, meta in list(store.metadata.items())[:5]:
    if meta.get('modality') == 'image':
        print(f"Image: {meta['file_name']}")
        print(f"Content: {meta['content'][:80]}")
```

### Issue: Vector Dimension Mismatch

**Error:**

```
ValueError: Embedding dimension mismatch: got 384, expected 512
```

**Solution:**

```bash
# You have old 384-dim embeddings
# Back up and clear the old index
cp backend/storage/faiss.index backend/storage/faiss.index.backup
rm backend/storage/faiss.index
rm backend/storage/metadata.json

# Re-index your files
# (Images will be re-embedded with 512-dim CLIP)
```

---

## Performance Optimization Tips

### For Large Image Collections

```python
# Batch process image embeddings
from app.embeddings import embed_image
import concurrent.futures

image_paths = ["img1.png", "img2.png", ..., "img1000.png"]

# Use ThreadPoolExecutor for I/O-bound OCR operations
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
    embeddings = list(executor.map(embed_image, image_paths))

# But note: CLIP embedding is CPU-bound, so parallel execution
# may not speed it up much
```

### For Faster Retrieval

```python
# Limit search to just images if that's all you need
from app.retriever import get_retriever

retriever = get_retriever()

# Search only image modality
results = retriever.retrieve(query, top_k=5, modality_filter='image')
```

### For Memory Efficiency

```python
# CLIP model takes ~500MB
# OCR add-ons minimal
# Main bottleneck: FAISS index + metadata

# Keep the store lightweight:
store = get_store()
print(f"Metadata size (approx): {len(store.metadata)} entries")

# Delete old entries if needed:
# (Careful: FAISS doesn't support deletion, need to rebuild)
```

---

## Integration Points

### For Frontend Developers

When displaying retrieved images:

```javascript
// In ChatUI.jsx or ResultItem.jsx
const result = {
  file_name: "screenshot.png",
  modality: "image",
  content: "Image: screenshot.png | OCR Text: ...",
  filepath: "/files/screenshot.png",
};

// Display as image
if (result.modality === "image") {
  return <img src={result.filepath} alt={result.file_name} />;
}

// Extract OCR for preview text
const ocrMatch = result.content.match(/OCR Text: (.*?)(?:\||$)/);
const ocrText = ocrMatch ? ocrMatch[1] : "No text extracted";
```

### For API Users

```bash
# Upload an image
curl -X POST http://localhost:8000/ingest \
  -F "file=@screenshot.png"

# Query
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "what is visible in the screenshots?"}'

# Response will include image results with OCR in content field
```

---

## Testing Commands

```bash
# Run all image understanding tests
python test_image_understanding.py

# Expected: 6/6 tests PASSED

# Run unified embeddings tests
python test_unified_embeddings.py

# Expected: 3/3 tests PASSED

# Run full system test
python test_final_system.py

# Expected: 8/8 tests PASSED

# Quick embedding test
python -c "
from app.embeddings import embed_image
import numpy as np
emb = embed_image('backend/storage/Screenshot 2025-11-06 233326.png')
print(f'Shape: {emb.shape}')
print(f'Norm: {np.linalg.norm(emb[0]):.4f}')
print('✓ Embedding works!')
"
```

---

## Key Files & Their Roles

```
backend/app/
├── ingestion/
│   └── image_processor.py          ← OCR extraction, chunk creation
├── embeddings/
│   └── generate.py                 ← CLIP embedding generation
├── vector_store/
│   └── faiss_store.py              ← Metadata storage + retrieval
├── llm/
│   └── prompts.py                  ← Prompt formatting with OCR
└── main.py                         ← API endpoint, ingestion pipeline

tests/
├── test_image_understanding.py     ← Image-specific tests (NEW)
├── test_unified_embeddings.py      ← Embedding consistency tests
└── test_final_system.py            ← End-to-end tests

docs/
├── DEBUG_IMAGE_FIXES.md            ← This fix summary
└── BEFORE_AFTER_EXAMPLES.md        ← Real-world examples
```

---

## Performance Benchmarks

```
Operation                    Time (CPU)    Notes
────────────────────────────────────────────────
Load CLIP model               ~2 seconds   One-time, then cached
Embed image (512-dim)         ~200-300ms   Per image
Extract OCR text              ~50-100ms    If pytesseract available
Index image (store)           ~10ms        Upsert to FAISS
Search image query            <5ms         FAISS vector search
Generate LLM prompt           ~1ms         String formatting
```

---

## Debugging Tips

### Enable verbose logging

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Then run your code, you'll see detailed logs
```

### Inspect stored metadata

```python
from app.vector_store import get_store
import json

store = get_store()

# Find image entries
for vid, meta in store.metadata.items():
    if meta.get('modality') == 'image':
        print(f"Vector {vid}: {json.dumps(meta, indent=2)}")
```

### Test specific components

```python
# Test just the embedding
from app.embeddings import embed_image
emb = embed_image('test.png')

# Test just the OCR
from app.ingestion.image_processor import detect_text_in_image
text = detect_text_in_image('test.png')

# Test just retrieval
from app.vector_store import get_store
results = get_store().search(emb, top_k=1)
```

---

## When to Re-index

Re-index images when:

- ❌ You make changes to image_processor.py
- ❌ You make changes to embed_image() function
- ❌ You update the CLIP model
- ❌ You change embedding dimension (384 → 512)
- ✅ You add new images (automatic on upload)
- ✅ You install pytesseract (old images stay as-is, new ones get OCR)

To re-index:

```bash
# Backup current index
cp backend/storage/faiss.index backend/storage/faiss.index.backup

# Delete old index
rm backend/storage/faiss.index backend/storage/metadata.json

# Upload your images again - they'll be re-indexed automatically
```

---

**Last Updated: November 16, 2025**
**Status: ✅ All image understanding fixes implemented and tested**
