Audio Integration - Debug Report

Summary of changes

- Implemented offline transcription pipeline in `backend/app/ingestion/audio_transcriber.py`.
- Ensured audio transcript segments carry `start_ts`/`end_ts` and `timestamp` metadata.
- Persisted start/end timestamps to FAISS metadata in `backend/app/vector_store/faiss_store.py`.
- Ingestion pipeline (`/ingest` in `backend/app/main.py`) now includes start/end timestamps when upserting vectors.
- Query endpoint now formats audio citations using timestamp fragments (`#timestamp=MM:SS`).
- Added test script and unit test to exercise pipeline and validate chunk generation.

Known issues / notes

- The transcription code tries multiple local backends: `whisper` (openai) first, then `faster-whisper`.
- If neither backend is installed or a model isn't present, the pipeline will insert a placeholder chunk stating that transcription is unavailable. This allows indexing to proceed without failing.
- For production-grade ASR, install `faster-whisper` with a quantized model placed in `models/whisper` for efficient CPU inference.

Suggested next steps (optional)

- Add a background task queue to perform transcription asynchronously for large files.
- Expose an authenticated endpoint to return audio playback with `start`/`end` query params to support direct playback from the UI.
- Add richer tests with a real short spoken sample and ensure transcripts match expected phrases.
