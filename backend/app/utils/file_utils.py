"""
File utility functions.
"""

from __future__ import annotations

import os
import time
from typing import Dict, Any, Optional
from datetime import datetime


def get_file_metadata(filepath: str) -> Dict[str, Any]:
    """Get metadata for a file."""
    if not os.path.exists(filepath):
        return {}
    
    stat = os.stat(filepath)
    
    return {
        'filepath': filepath,
        'filename': os.path.basename(filepath),
        'size': stat.st_size,
        'created': datetime.fromtimestamp(stat.st_ctime).isoformat(),
        'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
        'extension': os.path.splitext(filepath)[1].lower()
    }


def format_timestamp(seconds: float) -> str:
    """Format timestamp in seconds to readable format."""
    if seconds is None:
        return ""
    
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    else:
        return f"{minutes:02d}:{secs:02d}"


def validate_file_path(filepath: str) -> bool:
    """Validate if file path exists and is accessible."""
    try:
        return os.path.exists(filepath) and os.path.isfile(filepath)
    except Exception:
        return False


def get_safe_filename(filename: str) -> str:
    """Get a safe filename by removing/replacing invalid characters."""
    import re
    # Remove or replace invalid characters
    safe_name = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # Remove leading/trailing spaces and dots
    safe_name = safe_name.strip(' .')
    return safe_name


def ensure_directory(path: str) -> None:
    """Ensure directory exists."""
    os.makedirs(path, exist_ok=True)


def get_file_type_from_extension(filename: str) -> str:
    """Get file type from extension."""
    ext = os.path.splitext(filename)[1].lower()
    
    type_mapping = {
        '.pdf': 'pdf',
        '.docx': 'docx',
        '.doc': 'docx',
        '.txt': 'text',
        '.md': 'text',
        '.png': 'image',
        '.jpg': 'image',
        '.jpeg': 'image',
        '.gif': 'image',
        '.bmp': 'image',
        '.webp': 'image',
        '.mp3': 'audio',
        '.wav': 'audio',
        '.m4a': 'audio',
        '.flac': 'audio',
        '.ogg': 'audio',
        '.mp4': 'video',
        '.avi': 'video',
        '.mov': 'video'
    }
    
    return type_mapping.get(ext, 'unknown')
