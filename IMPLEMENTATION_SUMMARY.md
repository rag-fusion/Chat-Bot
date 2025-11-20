Audio Modality Implementation Summary

What was added

- Offline audio transcription support using local Whisper or faster-whisper when available.
- `backend/app/ingestion/audio_transcriber.py`: transcripts audio into timestamped chunks.
- Chunks include `start_ts` and `end_ts` (seconds) and a human-readable `timestamp` (MM:SS or HH:MM:SS).
- Audio transcript chunks are embedded using the existing `embed_text()` (CLIP text encoder, 512-d) so audio lives in the same FAISS index as text and images.
- FAISS metadata now persists `start_ts` and `end_ts` for each vector.
- Ingestion (`/ingest`) pipeline stores start/end timestamps in vector metadata so audio citations can be timestamped.
- Added `backend/scripts/test_audio_pipeline.py` to exercise the full pipeline locally.
- Added `tests/test_audio.py` unit test.

How it works (high level)

1. Upload or place an audio file into `storage/`.
2. `transcribe_audio()` calls a local ASR (openai/whisper or faster-whisper) and returns segments.
3. Each segment is optionally split and assigned proportional start/end times.
4. Transcript segments are embedded with `embed_text()` and upserted into FAISS with metadata including `start_ts` and `end_ts`.
5. Queries use the unified `embed_text()` to search the same 512-d space and return audio hits alongside text/images.
6. Citations include timestamped fragment URLs like `/files/{file_name}#timestamp=00:01:23`.

How to test locally

1. Run the quick script (it generates a short silent WAV and runs through ingestion):

```bash
python backend/scripts/test_audio_pipeline.py
```

2. Run unit tests (requires pytest):

```bash
pytest tests/test_audio.py -q
```

Notes

- To get real transcripts, install `whisper` or `faster-whisper` and place a downloaded model under `models/whisper` or let the package download models locally.
- The script gracefully handles missing ASR backends by creating a placeholder chunk so indexing still works.
