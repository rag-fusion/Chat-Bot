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
    Transcribe audio using Whisper model.
    Returns (full_transcript, segments).
    segments is a list of tuples (start_ms, end_ms, text).
    """
    try:
        import whisper
        import torch
        import numpy as np
        
        # Force CPU mode for consistency
        device = "cpu"
        
        # Load model with absolute path
        model_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "models", "whisper"))
        model = whisper.load_model("base", download_root=model_path, device=device)
        
        # Transcribe audio
        result = model.transcribe(path, language=None)
        
        # Extract transcript and segments
        transcript = result.get("text", "").strip()
        segments = []
        
        # Process segments if available
        for seg in result.get("segments", []):
            text = seg.get("text", "").strip()
            if text:
                start = seg.get("start", 0)
                end = seg.get("end", 0)
                segments.append((start, end, text))
                
        return transcript, segments
    except Exception as e:
        print(f"Error transcribing audio: {str(e)}")
        pass
    return "", []


def transcribe_audio(path: str, file_name: str) -> List[Chunk]:
    """Transcribe audio file and create chunks with timestamps."""
    transcript, segments = transcribe_audio_with_whisper_cpp(path)
    chunks: List[Chunk] = []
    
    if not transcript or transcript.strip() == "":
        # If transcription failed, return empty list
        return chunks
    
    # Split transcript into chunks
    split_chunks = _split_text(transcript)
    
    # Map chunks to segments for timestamp assignment
    segment_idx = 0
    char_pos = 0
    
    for i, ch in enumerate(split_chunks):
        # Find corresponding segment for this chunk
        chunk_start = char_pos
        chunk_end = char_pos + len(ch)
        
        # Find segment that contains this chunk
        timestamp_str = None
        for seg_start, seg_end, seg_text in segments:
            seg_char_start = sum(len(seg[2]) + 1 for seg in segments[:segments.index((seg_start, seg_end, seg_text))])
            seg_char_end = seg_char_start + len(seg_text)
            
            if chunk_start >= seg_char_start and chunk_start < seg_char_end:
                # Format timestamp as "HH:MM:SS" or "MM:SS"
                if seg_start is not None and seg_end is not None:
                    start_sec = seg_start / 1000.0
                    end_sec = seg_end / 1000.0
                    hours = int(start_sec // 3600)
                    minutes = int((start_sec % 3600) // 60)
                    seconds = int(start_sec % 60)
                    if hours > 0:
                        timestamp_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
                    else:
                        timestamp_str = f"{minutes:02d}:{seconds:02d}"
                break
        
        c = Chunk(
            content=ch, 
            file_name=file_name, 
            file_type="audio", 
            filepath=path,
            timestamp=timestamp_str  # Store timestamp in Chunk
        )
        # Also store segments for reference
        setattr(c, "segments", segments)
        chunks.append(c)
        
        char_pos = chunk_end
    
    return chunks
