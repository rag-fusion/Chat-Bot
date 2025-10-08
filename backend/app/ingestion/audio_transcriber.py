"""
Audio transcription using Whisper.
"""

from __future__ import annotations

import os
import subprocess
import tempfile
from typing import List, Tuple
from .base import Chunk, _split_text


def transcribe_audio_with_whisper_cpp(path: str) -> Tuple[str, List[Tuple[float, float, str]]]:
    """
    Invoke local whisper.cpp binary and return (full_transcript, segments).
    segments is a list of tuples (start_ms, end_ms, text).
    """
    binary = os.getenv("WHISPER_CPP_BIN", "./models/whisper/main")
    model = os.getenv("WHISPER_CPP_MODEL", "./models/whisper/ggml-base.en.bin")
    try:
        with tempfile.TemporaryDirectory() as td:
            out_prefix = os.path.join(td, "out")
            out_json = out_prefix + ".json"
            cmd = [binary, "-m", model, "-f", path, "-oj", "-of", out_prefix]
            subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if os.path.exists(out_json):
                import json
                data = json.load(open(out_json, "r", encoding="utf-8"))
                parts = []
                segments = []
                for seg in data.get("segments", []):
                    text = (seg.get("text") or "").strip()
                    if not text:
                        continue
                    parts.append(text)
                    segments.append((seg.get("t0"), seg.get("t1"), text))
                return " ".join(parts), segments
    except Exception:
        pass
    return "", []


def transcribe_audio(path: str, file_name: str) -> List[Chunk]:
    """Transcribe audio file and create chunks with timestamps."""
    transcript, segments = transcribe_audio_with_whisper_cpp(path)
    chunks: List[Chunk] = []
    
    # Split transcript into chunks
    split_chunks = _split_text(transcript)
    for i, ch in enumerate(split_chunks):
        c = Chunk(
            content=ch, 
            file_name=file_name, 
            file_type="audio", 
            filepath=path
        )
        # Store segments for timestamp information
        setattr(c, "segments", segments)
        chunks.append(c)
    
    return chunks
