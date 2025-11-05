"""
File serving utilities for uploaded documents.
"""

import os
import shutil
from pathlib import Path

UPLOADS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "storage", "uploads")

def init_upload_dir():
    """Initialize uploads directory."""
    os.makedirs(UPLOADS_DIR, exist_ok=True)

def save_uploaded_file(temp_path: str, original_filename: str) -> str:
    """
    Save an uploaded file to the uploads directory.
    Returns the relative path to the file.
    """
    init_upload_dir()
    
    # Create safe filename
    safe_filename = Path(original_filename).name
    dest_path = os.path.join(UPLOADS_DIR, safe_filename)
    
    # If file exists, add number suffix
    counter = 1
    while os.path.exists(dest_path):
        name, ext = os.path.splitext(safe_filename)
        dest_path = os.path.join(UPLOADS_DIR, f"{name}_{counter}{ext}")
        counter += 1
    
    # Copy file to uploads directory
    shutil.copy2(temp_path, dest_path)
    
    # Return relative path
    return os.path.relpath(dest_path, UPLOADS_DIR)

def get_file_path(relative_path: str) -> str:
    """Get absolute path for a relative upload path."""
    return os.path.join(UPLOADS_DIR, relative_path)