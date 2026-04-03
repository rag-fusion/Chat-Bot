from pathlib import Path
import whisper
from app.config import WHISPER_MODEL

_whisper_model = None


def get_whisper():
    global _whisper_model
    if _whisper_model is None:
        print(f"[Whisper] Loading model '{WHISPER_MODEL}'...")
        _whisper_model = whisper.load_model(WHISPER_MODEL)
        print("[Whisper] Model ready.")
    return _whisper_model


def ingest_audio(file_path: Path) -> list[dict]:
    """
    Transcribe audio with Whisper.
    Groups segments into 30-second windows with 5-second overlap.
    Each chunk stores start_time and end_time in seconds.
    """
    model = get_whisper()
    result = model.transcribe(str(file_path), verbose=False)
    segments = result.get("segments", [])

    if not segments:
        return []

    WINDOW = 30.0   # seconds per chunk
    OVERLAP = 5.0   # seconds overlap between chunks

    chunks = []
    chunk_index = 0
    window_start = segments[0]["start"]
    window_segs = []

    for seg in segments:
        if seg["start"] < window_start + WINDOW:
            window_segs.append(seg)
        else:
            if window_segs:
                text = " ".join(s["text"].strip() for s in window_segs)
                chunks.append({
                    "chunk_index": chunk_index,
                    "text": text.strip(),
                    "start_time": round(window_segs[0]["start"], 2),
                    "end_time":   round(window_segs[-1]["end"], 2),
                    "modality":   "audio",
                    "page":       None,
                    "image_path": None,
                })
                chunk_index += 1
                window_start = window_segs[-1]["end"] - OVERLAP
                window_segs = [s for s in window_segs if s["end"] > window_start]
            else:
                window_start = seg["start"]
                window_segs = []
            window_segs.append(seg)

    # Flush last window
    if window_segs:
        text = " ".join(s["text"].strip() for s in window_segs)
        chunks.append({
            "chunk_index": chunk_index,
            "text": text.strip(),
            "start_time": round(window_segs[0]["start"], 2),
            "end_time":   round(window_segs[-1]["end"], 2),
            "modality":   "audio",
            "page":       None,
            "image_path": None,
        })

    return chunks
