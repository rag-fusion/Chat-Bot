import { useRef } from "react";

const MODALITY_ICONS = {
  pdf:   "📄",
  docx:  "📝",
  image: "🖼️",
  audio: "🎵",
};

/**
 * Drag & drop OR click-to-upload.
 * Calls onUpload(file) when a file is selected.
 */
export default function FileUpload({ onUpload, disabled }) {
  const inputRef = useRef(null);

  function handleDrop(e) {
    e.preventDefault();
    if (disabled) return;
    const file = e.dataTransfer.files[0];
    if (file) onUpload(file);
  }

  function handleChange(e) {
    const file = e.target.files[0];
    if (file) {
      onUpload(file);
      e.target.value = ""; // Reset so same file can be re-uploaded
    }
  }

  return (
    <div
      className={`drop-zone ${disabled ? "disabled" : ""}`}
      onDragOver={(e) => e.preventDefault()}
      onDrop={handleDrop}
      onClick={() => !disabled && inputRef.current?.click()}
    >
      <input
        ref={inputRef}
        type="file"
        accept=".pdf,.docx,.doc,.png,.jpg,.jpeg,.bmp,.tiff,.mp3,.wav,.m4a,.ogg,.flac"
        onChange={handleChange}
        style={{ display: "none" }}
      />
      <div className="drop-zone-content">
        <span className="drop-icon">📎</span>
        <span>{disabled ? "Uploading..." : "Drop file here or click to upload"}</span>
        <span className="drop-hint">PDF · DOCX · Images · Audio</span>
      </div>
    </div>
  );
}
