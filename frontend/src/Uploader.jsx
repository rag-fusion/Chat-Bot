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
      
      if (!res.ok) {
        let errorMessage = "Failed to upload file. Please try again.";
        try {
          const errorData = await res.json();
          errorMessage = errorData.detail || errorData.message || errorMessage;
        } catch {
          errorMessage = `Upload failed: ${res.status} ${res.statusText}`;
        }
        throw new Error(errorMessage);
      }
      
      const data = await res.json();
      setStatus(`Indexed ${data.vectors_indexed} vectors from ${data.file}`);
      onUploaded?.(data);
    } catch (e) {
      const errorMsg = e.message || "Failed to upload file. Please try again.";
      setError(errorMsg);
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

    // Upload files sequentially since batch endpoint doesn't exist
    setUploading(true);
    setError("");
    let successCount = 0;
    let failCount = 0;
    const failedFiles = [];

    for (let i = 0; i < filesToUpload.length; i++) {
      const file = filesToUpload[i];
      setStatus(`Uploading ${file.name} (${i + 1}/${filesToUpload.length})...`);

      try {
        const form = new FormData();
        form.append("file", file);
        const res = await fetch("http://localhost:8000/ingest", {
          method: "POST",
          body: form,
        });

        if (!res.ok) {
          let errorMessage = `Failed to upload ${file.name}`;
          try {
            const errorData = await res.json();
            errorMessage = errorData.detail || errorData.message || errorMessage;
          } catch {
            errorMessage = `${file.name}: ${res.status} ${res.statusText}`;
          }
          throw new Error(errorMessage);
        }

        const data = await res.json();
        successCount++;
        onUploaded?.(data);
      } catch (e) {
        failCount++;
        failedFiles.push(file);
        const errorMsg = e.message || `Failed to upload ${file.name}`;
        setError(`${errorMsg}${failCount > 1 ? ` (${failCount} failed)` : ""}`);
      }
    }

    // Update status with final results
    if (failCount === 0) {
      setStatus(`Successfully uploaded ${successCount} file${successCount > 1 ? "s" : ""}`);
      setError("");
    } else if (successCount > 0) {
      setStatus(`Uploaded ${successCount} file${successCount > 1 ? "s" : ""}, ${failCount} failed`);
    } else {
      setError(`Failed to upload all ${filesToUpload.length} file${filesToUpload.length > 1 ? "s" : ""}`);
    }

    // Remove failed files from the list
    if (failedFiles.length > 0) {
      setFiles((prev) => prev.filter((f) => !failedFiles.includes(f)));
    }

    setUploading(false);
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
