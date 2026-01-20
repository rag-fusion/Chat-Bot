"""
Migration script to convert existing 384-dim indices to 512-dim CLIP embeddings.

WARNING: This requires re-indexing all documents. The script will:
1. Backup existing index and metadata
2. Extract all content from metadata
3. Re-embed using CLIP (512-dim)
4. Create new index

Usage:
    python scripts/migrate_to_clip.py
"""

import os
import sys
import shutil
import json
from pathlib import Path

# Add backend directory to path
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend'))
sys.path.insert(0, backend_dir)

from app.vector_store import FAISSStore
from app.embeddings import embed_text, embed_image
from app.index_store import connect_db

def migrate_index():
    """Migrate existing 384-dim index to 512-dim CLIP embeddings."""
    
    storage_dir = os.path.join(backend_dir, "storage")
    index_path = os.path.join(storage_dir, "faiss.index")
    metadata_path = os.path.join(storage_dir, "metadata.json")
    db_path = os.path.join(storage_dir, "metadata.db")
    
    # Check if old index exists
    if not os.path.exists(index_path):
        print("No existing index found. Nothing to migrate.")
        return
    
    # Backup existing files
    print("Creating backups...")
    backup_dir = os.path.join(storage_dir, "backup_384dim")
    os.makedirs(backup_dir, exist_ok=True)
    
    if os.path.exists(index_path):
        shutil.copy2(index_path, os.path.join(backup_dir, "faiss.index.backup"))
    if os.path.exists(metadata_path):
        shutil.copy2(metadata_path, os.path.join(backup_dir, "metadata.json.backup"))
    if os.path.exists(db_path):
        shutil.copy2(db_path, os.path.join(backup_dir, "metadata.db.backup"))
    
    print("✓ Backups created in storage/backup_384dim/")
    
    # Load existing metadata
    print("\nLoading existing metadata...")
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("SELECT vector_id, content, file_name, file_type, page_number, timestamp, filepath, width, height, bbox FROM vectors ORDER BY vector_id")
    rows = cur.fetchall()
    conn.close()
    
    if not rows:
        print("No data to migrate.")
        return
    
    print(f"Found {len(rows)} vectors to migrate")
    
    # Create new 512-dim store
    print("\nCreating new 512-dim index...")
    new_store = FAISSStore(dimension=512, storage_dir=storage_dir)
    
    # Re-embed and index
    print("Re-embedding content with CLIP (512-dim)...")
    items = []
    processed = 0
    
    for row in rows:
        vector_id, content, file_name, file_type, page_number, timestamp, filepath, width, height, bbox = row
        
        # Determine embedding method based on file type
        if file_type == 'image' and filepath and os.path.exists(filepath):
            try:
                embedding = embed_image(filepath)
            except Exception as e:
                print(f"  Warning: Could not embed image {filepath}: {e}")
                # Fallback to text embedding of content
                embedding = embed_text(content or f"Image: {file_name}")
        else:
            # Text, audio, or other - use text embedding
            embedding = embed_text(content or "")
        
        items.append({
            'embedding': embedding[0],  # Remove batch dimension
            'metadata': {
                'content': content,
                'file_name': file_name,
                'file_type': file_type,
                'page_number': page_number,
                'timestamp': timestamp,
                'filepath': filepath,
                'width': width,
                'height': height,
                'bbox': bbox,
                'modality': file_type
            }
        })
        
        processed += 1
        if processed % 100 == 0:
            print(f"  Processed {processed}/{len(rows)} vectors...")
    
    # Add to new index
    print(f"\nAdding {len(items)} vectors to new index...")
    added = new_store.upsert(items)
    print(f"✓ Successfully migrated {added} vectors to 512-dim index")
    
    # Verify
    status = new_store.status()
    print(f"\nMigration complete!")
    print(f"  - Vectors: {status['vectors']}")
    print(f"  - Dimension: {status['dimension']}")
    print(f"  - Files: {status['files']}")
    print(f"  - Modalities: {status['modalities']}")
    
    print("\n⚠️  Old index files have been backed up.")
    print("   You can delete them after verifying the migration worked correctly.")

if __name__ == "__main__":
    print("=" * 60)
    print("Migration: 384-dim → 512-dim CLIP Embeddings")
    print("=" * 60)
    print("\nThis will re-index all your documents using CLIP embeddings.")
    print("Make sure you have enough disk space and time.")
    print("\nPress Ctrl+C to cancel, or Enter to continue...")
    try:
        input()
    except KeyboardInterrupt:
        print("\nMigration cancelled.")
        sys.exit(0)
    
    migrate_index()
