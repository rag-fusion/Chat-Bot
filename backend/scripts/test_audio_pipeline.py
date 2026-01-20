"""End-to-end test script for the audio ingestion pipeline.

This script is intended to be runnable locally. It:
 - Creates a short synthetic WAV file in storage
 - Calls the ingestion/transcription pipeline directly
 - Embeds transcript segments using the unified embed_text()
 - Indexes embeddings in FAISS
 - Performs a simple search to verify vectors are searchable

The script is tolerant of missing ASR backends: if no local ASR is available,
the pipeline will insert a placeholder chunk and indexing will still succeed.
"""

import os
import wave
import struct
import tempfile
import numpy as np

from backend.app.ingestion.audio_transcriber import transcribe_audio
from backend.app.embeddings.generate import embed_text
from backend.app.vector_store.faiss_store import get_store, upsert, search


def generate_silent_wav(path: str, duration_sec: float = 1.0, rate: int = 16000):
    n_samples = int(duration_sec * rate)
    amplitude = 0
    with wave.open(path, 'w') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(rate)
        frames = (struct.pack('<h', 0) for _ in range(n_samples))
        wf.writeframes(b''.join(frames))


def main():
    storage_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'storage'))
    os.makedirs(storage_dir, exist_ok=True)
    wav_path = os.path.join(storage_dir, 'test_silent.wav')
    generate_silent_wav(wav_path, duration_sec=1.0)

    print(f"Generated test WAV: {wav_path}")

    chunks = transcribe_audio(wav_path, 'test_silent.wav')
    print(f"Transcription produced {len(chunks)} chunk(s)")
    for c in chunks:
        print('---')
        print('content:', c.content)
        print('timestamp:', getattr(c, 'timestamp', None))
        print('start_ts:', getattr(c, 'start_ts', None))
        print('end_ts:', getattr(c, 'end_ts', None))

    # Embed and index
    store = get_store()
    items = []
    for c in chunks:
        emb = embed_text(c.content)
        if emb.ndim == 2:
            emb = emb[0]
        items.append({
            'embedding': emb,
            'metadata': {
                'content': c.content,
                'file_name': c.file_name,
                'file_type': c.file_type,
                'timestamp': getattr(c, 'timestamp', None),
                'start_ts': getattr(c, 'start_ts', None),
                'end_ts': getattr(c, 'end_ts', None),
                'filepath': c.filepath,
                'modality': 'audio'
            }
        })

    upsert(items)
    print('Indexed items:', len(items))

    # Simple search for "transcription" to see if placeholder appears
    q = 'transcription'
    q_emb = embed_text(q)
    results = store.search(q_emb, top_k=5)
    print('Search results:', results[:3])


if __name__ == '__main__':
    main()
