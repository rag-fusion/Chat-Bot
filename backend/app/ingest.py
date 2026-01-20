import os
from typing import List, Optional
from fastapi import UploadFile, HTTPException

from .ingestion import extract_any
from .ingestion.base import Chunk
from .embeddings import embed_text, embed_image
from .vector_store import get_store

async def process_and_ingest_file(file: UploadFile, storage_dir: str) -> dict:
    """
    Process an uploaded file, extract content, generate embeddings, and store them.
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="Missing filename")
    
    dest_path = os.path.join(storage_dir, file.filename)
    data = await file.read()
    
    if not data:
        raise HTTPException(status_code=400, detail="Empty file uploaded")
    
    # Save file to disk
    with open(dest_path, "wb") as f:
        f.write(data)

    # Extract chunks
    try:
        chunks = extract_any(dest_path, file.filename, file.content_type or "")
    except Exception as e:
        raise HTTPException(
            status_code=422, 
            detail=f"Failed to extract content from file: {str(e)}"
        )
    
    # Handle audio transcription placeholder if needed
    if not chunks:
        audio_exts = ('.mp3', '.wav', '.m4a', '.flac', '.ogg')
        if file.filename.lower().endswith(audio_exts):
            placeholder = Chunk(
                content="[Transcription unavailable: install a local ASR model (whisper or faster-whisper) to enable transcripts]",
                file_name=file.filename,
                file_type="audio",
                filepath=dest_path,
                timestamp=None
            )
            setattr(placeholder, 'start_ts', None)
            setattr(placeholder, 'end_ts', None)
            chunks = [placeholder]
        else:
            raise HTTPException(
                status_code=422,
                detail=f"No content could be extracted from {file.filename}. The file may be corrupted or in an unsupported format."
            )
    
    # Generate embeddings and store
    try:
        store = get_store()
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to initialize vector store: {str(e)}"
        )
    
    items = []
    text_chunks = []
    image_chunks = []
    
    for i, chunk in enumerate(chunks):
        if chunk.file_type == 'image':
            image_chunks.append((i, chunk))
        else:
            text_chunks.append((i, chunk))
    
    # Batch process text embeddings
    if text_chunks:
        try:
            text_contents = [chunk.content for _, chunk in text_chunks]
            text_embeddings = embed_text(text_contents)
            
            for idx, (orig_idx, chunk) in enumerate(text_chunks):
                embedding = text_embeddings[idx] if text_embeddings.ndim == 2 else text_embeddings
                if embedding.ndim == 2:
                    embedding = embedding[0]
                
                items.append({
                    'embedding': embedding,
                    'metadata': _build_metadata(chunk)
                })
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to generate text embeddings: {str(e)}"
            )
    
    # Process image embeddings
    for orig_idx, chunk in image_chunks:
        try:
            embedding = embed_image(chunk.filepath)
            if embedding.ndim == 2:
                embedding = embedding[0]
            
            items.append({
                'embedding': embedding,
                'metadata': _build_metadata(chunk)
            })
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to generate image embedding for {chunk.file_name}: {str(e)}"
            )
    
    try:
        vectors_added = store.upsert(items)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to store vectors in database: {str(e)}"
        )
    
    return {"chunks_added": len(chunks), "vectors_indexed": vectors_added, "file": file.filename}


def _build_metadata(chunk: Chunk) -> dict:
    """Helper to construct metadata dictionary from a Chunk."""
    return {
        'content': chunk.content,
        'file_name': chunk.file_name,
        'file_type': chunk.file_type,
        'page_number': chunk.page_number,
        'timestamp': chunk.timestamp,
        'start_ts': getattr(chunk, 'start_ts', None),
        'end_ts': getattr(chunk, 'end_ts', None),
        'filepath': chunk.filepath,
        'width': getattr(chunk, 'width', None),
        'height': getattr(chunk, 'height', None),
        'bbox': getattr(chunk, 'bbox', None),
        'char_start': getattr(chunk, 'char_start', None),
        'char_end': getattr(chunk, 'char_end', None),
        'modality': chunk.file_type
    }


