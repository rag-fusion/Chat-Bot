export default function ImageViewer({ url, chunkText }) {
  return (
    <div className="image-viewer">
      <img
        src={url}
        alt="Source image"
        style={{ maxWidth: "100%", borderRadius: 8, display: "block" }}
      />
      {chunkText && (
        <div className="transcript-box" style={{ marginTop: 12 }}>
          <strong>OCR text from image:</strong>
          <p>{chunkText}</p>
        </div>
      )}
    </div>
  );
}
