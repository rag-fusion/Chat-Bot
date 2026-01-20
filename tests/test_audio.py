import os
from backend.app.ingestion.audio_transcriber import transcribe_audio


def test_transcribe_sanity():
    # Create a small temporary wav file
    import wave, struct
    tmp = os.path.join(os.path.dirname(__file__), 'tmp_test_silent.wav')
    with wave.open(tmp, 'w') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(16000)
        frames = (struct.pack('<h', 0) for _ in range(16000))
        wf.writeframes(b''.join(frames))

    chunks = transcribe_audio(tmp, 'tmp_test_silent.wav')
    assert isinstance(chunks, list)
    assert len(chunks) >= 1
    # Each chunk should have content and file_type audio
    for c in chunks:
        assert hasattr(c, 'content')
        assert c.file_type == 'audio'

    os.remove(tmp)
