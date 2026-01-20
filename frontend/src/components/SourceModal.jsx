import { useEffect, useRef, useState } from "react";
import WaveSurfer from "wavesurfer.js";
import * as pdfjsLib from "pdfjs-dist";
import { FileAudio, FileText, Image as ImageIcon } from "lucide-react";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from "./ui/dialog";

pdfjsLib.GlobalWorkerOptions.workerSrc = `https://unpkg.com/pdfjs-dist@${pdfjsLib.version}/build/pdf.worker.min.mjs`;

function getFileUrl(item) {
  // Prefer direct /files URL (potentially with #page anchor) for pdf.js
  if (item?.url) {
    return item.url.startsWith("http")
      ? item.url
      : `http://localhost:8000${item.url}`;
  }
  // Fallback to stable /files by filename
  const name = item.file || item.title || (item.filepath ? item.filepath.split(/[\\/]/).pop() : "");
  if (name) return `http://localhost:8000/files/${encodeURIComponent(name)}`;
  // Fallback to raw storage path if available
  if (item.filepath) {
    const tail = item.filepath.split(/storage[\\/]/i)[1] || item.filepath.split(/[\\/]/).pop() || "";
    return `http://localhost:8000/storage/${tail}`;
  }
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

        // Calculate scale to fit within modal while maintaining aspect ratio
        const viewport = page.getViewport({ scale: 1 });
        const maxWidth = 600; // Maximum width in modal
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
  if (!item) return null;

  const fileUrl = getFileUrl(item);

  return (
    <Dialog open={true} onOpenChange={() => onClose()}>
      <DialogContent className="max-w-2xl">
        <DialogHeader className="flex-row items-center gap-3">
          <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-muted">
            {item.type === "audio" ? (
              <FileAudio className="h-5 w-5 text-primary" />
            ) : item.type === "image" ? (
              <ImageIcon className="h-5 w-5 text-primary" />
            ) : (
              <FileText className="h-5 w-5 text-primary" />
            )}
          </div>
          <div className="flex-1">
            <DialogTitle className="text-xl">
              {item.title || item.file}
            </DialogTitle>
            <DialogDescription>
              Source preview and extracted content
            </DialogDescription>
            {item.type !== "image" && (
              <p className="mt-1 text-sm text-muted-foreground">
                {item.type === "audio"
                  ? item.transcript
                  : `Page ${item.page || 1}`}
              </p>
            )}
          </div>
        </DialogHeader>

        <div className="mt-4">
          {item.type === "audio" ? (
            <AudioPlayer url={fileUrl} timestamp={item.timestamp} />
          ) : item.type === "image" ? (
            <img
              src={fileUrl}
              alt={item.caption || "Source image"}
              className="max-h-[70vh] w-full rounded-lg object-contain"
            />
          ) : item.type === "pdf" ? (
            <PdfViewer url={fileUrl} pageNumber={item.page || 1} />
          ) : (
            <TextFallback url={fileUrl} initialText={item.text} />
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
}

function TextFallback({ url, initialText }) {
  const [text, setText] = useState(initialText || "");
  useEffect(() => {
    if (!text && url) {
      (async () => {
        try {
          const res = await fetch(url);
          if (res.ok) {
            const t = await res.text();
            setText(t);
          }
        } catch (e) {
          // ignore
        }
      })();
    }
  }, [url, text]);
  return (
    <div className="rounded-lg border bg-muted p-4">
      <pre className="whitespace-pre-wrap text-sm">{text || "No text available."}</pre>
    </div>
  );
}
