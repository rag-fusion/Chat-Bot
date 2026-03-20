import { useEffect, useRef, useState } from "react";
import WaveSurfer from "wavesurfer.js";
import * as pdfjsLib from "pdfjs-dist";
import { FileAudio, FileText, Image as ImageIcon } from "lucide-react";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from "./ui/dialog";
import { API_BASE_URL } from "../config";

pdfjsLib.GlobalWorkerOptions.workerSrc = `https://unpkg.com/pdfjs-dist@${pdfjsLib.version}/build/pdf.worker.min.mjs`;

/**
 * Build file URL using session-scoped path: /api/files/{session_id}/{file_name}
 */
function getFileUrl(item) {
  if (item?.session_id && item?.file_name) {
    return `${API_BASE_URL}/api/files/${item.session_id}/${encodeURIComponent(item.file_name)}`;
  }
  // Legacy fallback
  const name = item?.file_name || item?.file || item?.title || "";
  if (name) return `${API_BASE_URL}/api/files/${encodeURIComponent(name)}`;
  return "";
}

function AudioPlayer({ url, timestamp }) {
  const audioRef = useRef(null);
  const waveRef = useRef(null);

  useEffect(() => {
    if (!url || waveRef.current) return;

    const ws = WaveSurfer.create({
      container: "#wave",
      waveColor: "hsl(var(--primary))",
      progressColor: "hsl(var(--primary) / 0.5)",
      height: 80,
      cursorWidth: 2,
      cursorColor: "hsl(var(--primary))",
      normalize: true,
      minimap: true,
      barWidth: 2,
      barGap: 1,
    });
    waveRef.current = ws;
    ws.load(url);

    if (timestamp) {
      const [s0] = String(timestamp).split("-");
      const startSec = parseFloat(s0) / 100.0;
      ws.on("ready", () => ws.setTime(startSec));
    }

    return () => {
      ws.destroy();
      waveRef.current = null;
    };
  }, [url, timestamp]);

  return (
    <div className="space-y-4">
      <div id="wave" className="rounded-lg border bg-muted/50 p-4" />
      <div className="flex items-center gap-2">
        <button
          onClick={() => waveRef.current?.playPause()}
          className="inline-flex items-center justify-center rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 border border-input bg-background hover:bg-accent hover:text-accent-foreground h-10 px-4 py-2"
        >
          Play/Pause
        </button>
      </div>
    </div>
  );
}

function PdfViewer({ url, pageNumber = 1 }) {
  const [loading, setLoading] = useState(true);
  const [failed, setFailed] = useState(false);
  const canvasRef = useRef(null);

  useEffect(() => {
    if (!url || !canvasRef.current) return;

    (async () => {
      try {
        const pdf = await pdfjsLib.getDocument(url).promise;
        const page = await pdf.getPage(pageNumber);
        const canvas = canvasRef.current;
        const ctx = canvas.getContext("2d");

        const viewport = page.getViewport({ scale: 1 });
        const maxWidth = 600;
        const scale = maxWidth / viewport.width;
        const scaledViewport = page.getViewport({ scale });

        canvas.width = scaledViewport.width;
        canvas.height = scaledViewport.height;

        await page.render({
          canvasContext: ctx,
          viewport: scaledViewport,
        }).promise;
      } catch (error) {
        console.error("Error rendering PDF:", error);
        setFailed(true);
      } finally {
        setLoading(false);
      }
    })();
  }, [url, pageNumber]);

  return (
    <div className="flex min-h-[300px] items-center justify-center rounded-lg border bg-muted/50">
      {loading ? (
        <div className="flex items-center gap-2 text-muted-foreground">
          <div className="h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent" />
          <span>Loading PDF...</span>
        </div>
      ) : failed ? (
        <div className="w-full p-4 text-center text-sm text-muted-foreground">
          <p>PDF preview failed. You can open the file directly:</p>
          <a href={url} target="_blank" rel="noreferrer" className="text-primary underline">Open PDF</a>
        </div>
      ) : (
        <canvas ref={canvasRef} className="max-h-[70vh] rounded" />
      )}
    </div>
  );
}

export default function SourceModal({ item, onClose }) {
  const [viewerData, setViewerData] = useState(null);
  const [loading, setLoading] = useState(false);

  // Fetch full citation context from viewer API when item has vector_id + session_id
  useEffect(() => {
    if (!item) {
      setViewerData(null);
      return;
    }

    if (item.vector_id != null && item.session_id) {
      setLoading(true);
      const token = localStorage.getItem("token");
      fetch(`${API_BASE_URL}/api/viewer/${item.session_id}/${item.vector_id}`, {
        headers: { "Authorization": `Bearer ${token}` }
      })
        .then((res) => (res.ok ? res.json() : null))
        .then((data) => {
          setViewerData(data);
        })
        .catch((e) => {
          console.error("Viewer fetch error:", e);
          setViewerData(null);
        })
        .finally(() => setLoading(false));
    } else {
      setViewerData(null);
    }
  }, [item]);

  if (!item) return null;

  // Merge viewer data with item for display
  const displayItem = viewerData
    ? { ...item, text: viewerData.text, file_name: viewerData.file_name, page_number: viewerData.page_number, modality: viewerData.modality }
    : item;

  const fileUrl = getFileUrl(displayItem);
  const modality = displayItem.modality || "text";
  const pageNum = displayItem.page_number || displayItem.page || 1;
  const displayText = displayItem.text || displayItem.snippet || "";

  return (
    <Dialog open={true} onOpenChange={() => onClose()}>
      <DialogContent className="max-w-2xl">
        <DialogHeader className="flex-row items-center gap-3">
          <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-muted">
            {modality === "audio" ? (
              <FileAudio className="h-5 w-5 text-primary" />
            ) : modality === "image" ? (
              <ImageIcon className="h-5 w-5 text-primary" />
            ) : (
              <FileText className="h-5 w-5 text-primary" />
            )}
          </div>
          <div className="flex-1">
            <DialogTitle className="text-xl">
              {displayItem.file_name || displayItem.file || "Source"}
            </DialogTitle>
            <DialogDescription>
              Source preview and extracted content
            </DialogDescription>
            {modality !== "image" && (
              <p className="mt-1 text-sm text-muted-foreground">
                {modality === "audio"
                  ? displayItem.transcript
                  : `Page ${pageNum}`}
              </p>
            )}
          </div>
        </DialogHeader>

        <div className="mt-4">
          {loading ? (
            <div className="flex items-center justify-center p-8 text-muted-foreground">
              <div className="h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent mr-2" />
              Loading source...
            </div>
          ) : modality === "audio" ? (
            <AudioPlayer url={fileUrl} timestamp={displayItem.timestamp} />
          ) : modality === "image" ? (
            <img
              src={fileUrl}
              alt={displayItem.caption || "Source image"}
              className="max-h-[70vh] w-full rounded-lg object-contain"
            />
          ) : fileUrl.toLowerCase().includes(".pdf") ? (
            <div className="space-y-4">
              <PdfViewer url={fileUrl} pageNumber={pageNum} />
              {displayText && (
                <div className="rounded-lg border bg-muted p-4">
                  <p className="text-xs font-medium text-muted-foreground mb-2">Extracted Text:</p>
                  <pre className="whitespace-pre-wrap text-sm">{displayText}</pre>
                </div>
              )}
            </div>
          ) : (
            <div className="rounded-lg border bg-muted p-4">
              <pre className="whitespace-pre-wrap text-sm">{displayText || "No text available."}</pre>
            </div>
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
}
