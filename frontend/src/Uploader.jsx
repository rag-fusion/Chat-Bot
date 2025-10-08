import { useCallback, useState } from "react";
import { UploadZone, FilePreview } from "./components/ui/upload-zone";
import { AlertCircle, CheckCircle2, Loader2 } from "lucide-react";

const ACCEPTED_FILES = [
  // Documents
  "application/pdf",
  "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
  // Images
  "image/jpeg",
  "image/png",
  "image/webp",
  // Audio
  "audio/mpeg",
  "audio/wav",
  "audio/ogg",
].join(",");

export default function Uploader({ onUploaded }) {
  const [dragOver, setDragOver] = useState(false);
  const [status, setStatus] = useState("");
  const [files, setFiles] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState("");

  const onDrop = useCallback(async (e) => {
    e.preventDefault();
    setDragOver(false);
    const droppedFiles = Array.from(e.dataTransfer.files || []);
    if (!droppedFiles.length) return;
    handleFiles(droppedFiles);
  }, []);

  const handleFiles = async (newFiles) => {
    const validFiles = newFiles.filter((f) =>
      ACCEPTED_FILES.split(",").some((type) =>
        f.type.match(new RegExp(type.replace("*", ".*")))
      )
    );

    if (validFiles.length < newFiles.length) {
      setError(
        "Some files were skipped. Only PDF, DOCX, images, and audio files are supported."
      );
    }

    setFiles((prev) => [...prev, ...validFiles]);
    await uploadMany(validFiles);
  };

  const upload = async (file) => {
    setUploading(true);
    setError("");
    setStatus(`Uploading ${file.name}...`);

    try {
      const form = new FormData();
      form.append("file", file);
      const res = await fetch("http://localhost:8000/ingest", {
        method: "POST",
        body: form,
      });
      const data = await res.json();
      setStatus(`Indexed ${data.vectors_indexed} vectors from ${data.file}`);
      onUploaded?.(data);
    } catch (e) {
      setError("Failed to upload file. Please try again.");
      setFiles((prev) => prev.filter((f) => f !== file));
    } finally {
      setUploading(false);
    }
  };

  const uploadMany = async (filesToUpload) => {
    if (!filesToUpload.length) return;
    if (filesToUpload.length === 1) {
      return upload(filesToUpload[0]);
    }

    setUploading(true);
    setError("");
    setStatus(`Uploading ${filesToUpload.length} files...`);

    try {
      const form = new FormData();
      filesToUpload.forEach((f) => form.append("files", f));
      const res = await fetch("http://localhost:8000/ingest/batch", {
        method: "POST",
        body: form,
      });
      const data = await res.json();
      setStatus(
        `Indexed ${data.vectors_indexed} vectors from ${
          data.files?.length || 0
        } files`
      );
      onUploaded?.(data);
    } catch (e) {
      setError("Failed to upload files. Please try again.");
      setFiles((prev) => prev.filter((f) => !filesToUpload.includes(f)));
    } finally {
      setUploading(false);
    }
  };

  const removeFile = (file) => {
    setFiles((prev) => prev.filter((f) => f !== file));
  };

  return (
    <div className="space-y-4">
      {/* Drop Zone */}
      <div
        onDragOver={(e) => {
          e.preventDefault();
          setDragOver(true);
        }}
        onDragLeave={() => setDragOver(false)}
        onDrop={onDrop}
      >
        <UploadZone
          onFilesSelected={handleFiles}
          accept={ACCEPTED_FILES}
          multiple={true}
          title="Drop your files here"
          subtitle="Support for PDF, DOCX, images and audio files"
          isDragOver={dragOver}
        />
      </div>

      {/* Status Messages */}
      {(error || status || uploading) && (
        <div className="flex items-center gap-2 text-sm p-3 rounded-lg border bg-card">
          {error ? (
            <AlertCircle className="w-4 h-4 text-destructive shrink-0" />
          ) : uploading ? (
            <Loader2 className="w-4 h-4 text-muted-foreground animate-spin shrink-0" />
          ) : (
            <CheckCircle2 className="w-4 h-4 text-green-500 shrink-0" />
          )}
          <p className={error ? "text-destructive" : "text-muted-foreground"}>
            {error || status}
          </p>
        </div>
      )}

      {/* File List */}
      {files.length > 0 && (
        <div className="space-y-2">
          {files.map((file, idx) => (
            <FilePreview
              key={`${file.name}-${idx}`}
              file={file}
              onDelete={removeFile}
            />
          ))}
        </div>
      )}
    </div>
  );
}
