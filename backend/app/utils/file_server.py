"""
File serving utilities for uploaded documents.
Supports both legacy global uploads and session-scoped file storage.
"""

import os
from pathlib import Path

STORAGE_DIR = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)), "..", "storage"))
UPLOADS_DIR = os.path.join(STORAGE_DIR, "uploads")


def init_upload_dir():
    """Initialize uploads directory."""
    os.makedirs(UPLOADS_DIR, exist_ok=True)


def get_file_path(relative_path: str) -> str:
    """Get absolute path for a relative upload path (legacy)."""
    return os.path.join(UPLOADS_DIR, relative_path)


def get_session_file_path(session_id: str, file_name: str) -> str:
    """Get absolute path for a session-scoped file."""
    safe_name = Path(file_name).name
    return os.path.join(STORAGE_DIR, "sessions", session_id, "files", safe_name)