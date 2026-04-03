import { useState } from "react";
import { getChunkSource, getFileUrl } from "../api/client";
import PdfViewer   from "./viewers/PdfViewer";
import AudioViewer from "./viewers/AudioViewer";
import ImageViewer from "./viewers/ImageViewer";

/**
 * Renders citation chips.
 * When clicked, fetches source metadata and opens the right viewer.
 */
export default function CitationPanel({ citations, chatId }) {
  const [activeSource, setActiveSource]   = useState(null);
  const [loadingId,    setLoadingId]      = useState(null);
  const [error,        setError]          = useState(null);

  if (!citations || citations.length === 0) return null;

  async function handleClick(citation) {
    if (loadingId === citation.vector_id) return;
    setError(null);
    setLoadingId(citation.vector_id);
    try {
      const source = await getChunkSource(chatId, citation.vector_id);
      setActiveSource(source);
    } catch (e) {
      setError("Could not load source: " + e.message);
    } finally {
      setLoadingId(null);
    }
  }

  const renderViewer = () => {
    if (!activeSource) return null;
    const url = getFileUrl(chatId, activeSource.file_name);

    switch (activeSource.modality) {
      case "pdf":
      case "docx":
        return <PdfViewer url={url} page={activeSource.page || 1} />;
      case "audio":
        return (
          <AudioViewer
            url={url}
            startTime={activeSource.start_time}
            endTime={activeSource.end_time}
            transcript={activeSource.text}
          />
        );
      case "image":
        return <ImageViewer url={url} chunkText={activeSource.text} />;
      default:
        return <p>Unknown modality: {activeSource.modality}</p>;
    }
  };

  return (
    <div className="citation-panel">
      <div className="citation-chips">
        {citations.map((c) => (
          <button
            key={c.vector_id}
            className={`citation-chip ${loadingId === c.vector_id ? "loading" : ""} ${activeSource?.vector_id === c.vector_id ? "active" : ""}`}
            onClick={() => handleClick(c)}
            disabled={loadingId === c.vector_id}
            title={c.text_preview}
          >
            [{c.number}] {c.file_name}
            {c.modality === "pdf" && c.page ? ` · p.${c.page}` : ""}
            {c.modality === "audio" && c.start_time != null ? ` · ${c.start_time}s` : ""}
            {c.modality === "image" ? " · image" : ""}
            {loadingId === c.vector_id ? " ..." : ""}
          </button>
        ))}
      </div>
      {error && <p className="error-text">{error}</p>}
      {activeSource && (
        <div className="source-viewer-box">
          <div className="source-header">
            <span>📄 {activeSource.file_name}</span>
            <button onClick={() => setActiveSource(null)} className="close-btn">✕</button>
          </div>
          {renderViewer()}
        </div>
      )}
    </div>
  );
}
