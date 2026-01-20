"""Audio transcription using local ASR (whisper/faster-whisper if available).

This module tries to transcribe audio offline using locally installed Whisper
or faster-whisper backends. If neither is available, it will return an empty
transcript and the ingestion pipeline will surface an appropriate message.
"""

from __future__ import annotations

import os
from typing import List, Tuple
from .base import Chunk, _split_text


def _format_timestamp(seconds: float) -> str:
    """Format seconds as HH:MM:SS or MM:SS string."""
    try:
        seconds = float(seconds)
    except Exception:
        return ""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    return f"{minutes:02d}:{secs:02d}"


def transcribe_audio_with_whisper(path: str) -> Tuple[str, List[Tuple[float, float, str]]]:
    """Transcribe audio using available local Whisper implementation.

    Returns (full_transcript, segments) where segments is a list of
    (start_seconds, end_seconds, text).
    """
    # Try openai/whisper first
    try:
        import whisper
        print(f"[Audio] Loading openai-whisper model 'base'...")
        model = whisper.load_model("base", device="cpu")
        print(f"[Audio] Transcribing {path}...")
        result = model.transcribe(path)
        transcript = result.get("text", "").strip()
        segments = []
        for seg in result.get("segments", []):
            start = seg.get("start", 0.0)
            end = seg.get("end", 0.0)
            text = seg.get("text", "").strip()
            if text:
                segments.append((float(start), float(end), text))
        print(f"[Audio] Transcription complete. Length: {len(transcript)} chars.")
        return transcript, segments
    except ImportError:
        print("[Audio] openai-whisper not installed.")
    except Exception as e:
        print(f"[Audio] openai-whisper failed: {e}")

    # Try faster-whisper if installed (it often works well offline)
    try:
        from faster_whisper import WhisperModel
        print(f"[Audio] Loading faster-whisper model...")
        model_size = "small"
        model_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "models", "whisper"))
        model = WhisperModel(model_dir, device="cpu", compute_type="int8_float16")
        segments_iter, info = model.transcribe(path, beam_size=5)
        transcript_parts = []
        segments = []
        for segment in segments_iter:
            start = float(segment.start)
            end = float(segment.end)
            text = segment.text.strip()
            if text:
                transcript_parts.append(text)
                segments.append((start, end, text))
        return " ".join(transcript_parts), segments
    except ImportError:
        print("[Audio] faster-whisper not installed.")
    except Exception as e:
        print(f"[Audio] faster-whisper failed: {e}")

    # If no local ASR available, return empty results (ingestion will handle fallback)
    print("[Audio] No ASR backend available or all failed.")
    return "", []


def transcribe_audio(path: str, file_name: str) -> List[Chunk]:
    """Transcribe audio file and return a list of Chunk objects with timestamps.

    Each chunk will have attributes:
      - content: transcript text
      - file_name, file_type='audio', filepath
      - start_ts (float seconds), end_ts (float seconds)
      - timestamp (formatted start time string)
    """
    transcript, segments = transcribe_audio_with_whisper(path)
    chunks: List[Chunk] = []

    if not segments:
        # If ASR failed, create a single placeholder chunk to surface the file
        placeholder = Chunk(
            content="[Transcription unavailable: please install a local ASR model (whisper or faster-whisper)]",
            file_name=file_name,
            file_type="audio",
            filepath=path,
            timestamp=None
        )
        setattr(placeholder, "start_ts", None)
        setattr(placeholder, "end_ts", None)
        chunks.append(placeholder)
        return chunks

    # For each segment returned by ASR, split further if needed and assign timestamps
    for seg_start, seg_end, seg_text in segments:
        seg_text = (seg_text or "").strip()
        if not seg_text:
            continue

        # Split long segment text into subchunks while preserving approximate timestamps
        subchunks = _split_text(seg_text, min_size=100, max_size=400)
        if not subchunks:
            subchunks = [seg_text]

        total_chars = sum(len(s) for s in subchunks)
        if total_chars == 0:
            continue

        # Distribute timestamp range proportionally across subchunks
        seg_duration = max(0.0, float(seg_end) - float(seg_start))
        char_cursor = 0
        for sub in subchunks:
            proportion = len(sub) / total_chars
            start_offset = (char_cursor / total_chars) * seg_duration
            end_offset = ((char_cursor + len(sub)) / total_chars) * seg_duration
            start_ts = float(seg_start) + start_offset
            end_ts = float(seg_start) + end_offset

            ts_str = _format_timestamp(start_ts)

            c = Chunk(
                content=sub,
                file_name=file_name,
                file_type="audio",
                filepath=path,
                timestamp=ts_str
            )
            setattr(c, "start_ts", start_ts)
            setattr(c, "end_ts", end_ts)
            setattr(c, "char_start", None)
            setattr(c, "char_end", None)
            chunks.append(c)

            char_cursor += len(sub)

    return chunks
