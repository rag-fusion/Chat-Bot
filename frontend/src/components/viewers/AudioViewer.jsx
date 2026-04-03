import { useEffect, useRef } from "react";

export default function AudioViewer({ url, startTime, endTime, transcript }) {
  const audioRef = useRef(null);

  // When citation changes, jump to that timestamp and play
  useEffect(() => {
    const audio = audioRef.current;
    if (!audio || startTime == null) return;

    audio.currentTime = startTime;

    // Small delay needed for some browsers to accept currentTime before play
    setTimeout(() => {
      audio.play().catch(() => {
        // Autoplay blocked — user needs to press play manually
        // Audio is already seeked to correct position
      });
    }, 100);
  }, [url, startTime]);

  return (
    <div className="audio-viewer">
      <audio
        ref={audioRef}
        src={url}
        controls
        style={{ width: "100%", marginBottom: 12 }}
      />
      <div className="timestamp-badge">
        ⏱ {startTime != null ? `${startTime}s` : "—"}
        {endTime != null ? ` → ${endTime}s` : ""}
      </div>
      <div className="transcript-box">
        <strong>Cited transcript:</strong>
        <p>{transcript}</p>
      </div>
    </div>
  );
}
