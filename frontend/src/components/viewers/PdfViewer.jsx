import { useState } from "react";
import { Document, Page, pdfjs } from "react-pdf";
import "react-pdf/dist/Page/AnnotationLayer.css";
import "react-pdf/dist/Page/TextLayer.css";

// Required: tell react-pdf where to find the worker
pdfjs.GlobalWorkerOptions.workerSrc = `https://unpkg.com/pdfjs-dist@${pdfjs.version}/build/pdf.worker.min.js`;

export default function PdfViewer({ url, page = 1 }) {
  const [numPages, setNumPages] = useState(null);
  const [currentPage, setCurrentPage] = useState(page);
  const [error, setError] = useState(null);

  function onLoadSuccess({ numPages }) {
    setNumPages(numPages);
    setCurrentPage(page); // Jump to cited page
  }

  if (error) {
    return <div className="viewer-error">Failed to load PDF: {error}</div>;
  }

  return (
    <div className="pdf-viewer">
      <div className="pdf-controls">
        <button
          disabled={currentPage <= 1}
          onClick={() => setCurrentPage(p => p - 1)}
        >
          ← Prev
        </button>
        <span>Page {currentPage} of {numPages || "?"}</span>
        <button
          disabled={currentPage >= (numPages || 1)}
          onClick={() => setCurrentPage(p => p + 1)}
        >
          Next →
        </button>
      </div>
      <Document
        file={url}
        onLoadSuccess={onLoadSuccess}
        onLoadError={(e) => setError(e.message)}
      >
        <Page
          pageNumber={currentPage}
          width={500}
          renderAnnotationLayer={true}
          renderTextLayer={true}
        />
      </Document>
    </div>
  );
}
