#!/usr/bin/env python3
"""
Ingest all files from a directory into the RAG system.
"""

import argparse
import os
import sys
from pathlib import Path
from typing import List

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.ingestion import extract_any
from app.embeddings import embed_text, embed_image
from app.vector_store import get_store


def ingest_directory(data_dir: str, index_path: str = None) -> None:
    """Ingest all supported files from a directory."""
    data_path = Path(data_dir)
    if not data_path.exists():
        print(f"Error: Directory {data_dir} does not exist")
        return
    
    store = get_store()
    supported_extensions = {'.pdf', '.docx', '.txt', '.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp', '.mp3', '.wav', '.m4a', '.flac', '.ogg'}
    
    files_processed = 0
    chunks_added = 0
    
    print(f"Scanning directory: {data_dir}")
    
    for file_path in data_path.rglob('*'):
        if file_path.is_file() and file_path.suffix.lower() in supported_extensions:
            print(f"Processing: {file_path}")
            
            try:
                # Extract content
                chunks = extract_any(str(file_path), file_path.name, "")
                
                if not chunks:
                    print(f"  No content extracted from {file_path.name}")
                    continue
                
                # Generate embeddings and store
                items = []
                for chunk in chunks:
                    if chunk.file_type == 'image':
                        embedding = embed_image(chunk.filepath)
                    else:
                        embedding = embed_text(chunk.content)
                    
                    items.append({
                        'embedding': embedding[0],  # Remove batch dimension
                        'metadata': {
                            'content': chunk.content,
                            'file_name': chunk.file_name,
                            'file_type': chunk.file_type,
                            'page_number': chunk.page_number,
                            'timestamp': chunk.timestamp,
                            'filepath': chunk.filepath,
                            'width': getattr(chunk, 'width', None),
                            'height': getattr(chunk, 'height', None),
                            'bbox': getattr(chunk, 'bbox', None),
                            'char_start': getattr(chunk, 'char_start', None),
                            'char_end': getattr(chunk, 'char_end', None),
                            'modality': chunk.file_type
                        }
                    })
                
                # Store in vector database
                added = store.upsert(items)
                chunks_added += added
                files_processed += 1
                
                print(f"  Added {added} chunks from {file_path.name}")
                
            except Exception as e:
                print(f"  Error processing {file_path.name}: {e}")
    
    print(f"\nIngestion complete!")
    print(f"Files processed: {files_processed}")
    print(f"Total chunks added: {chunks_added}")
    
    # Save index if specified
    if index_path:
        store.persist(index_path)
        print(f"Index saved to: {index_path}")


def main():
    parser = argparse.ArgumentParser(description='Ingest files into the RAG system')
    parser.add_argument('--data-dir', required=True, help='Directory containing files to ingest')
    parser.add_argument('--index', help='Path to save the FAISS index')
    
    args = parser.parse_args()
    
    ingest_directory(args.data_dir, args.index)


if __name__ == '__main__':
    main()
