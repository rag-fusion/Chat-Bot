import { File, FileImage, FileText, FileAudio } from "lucide-react";

const getFileIcon = (type) => {
  if (type.startsWith("image/")) return FileImage;
  if (type.startsWith("audio/")) return FileAudio;
  if (
    type === "application/pdf" ||
    type ===
      "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
  )
    return FileText;
  return File;
};

export function UploadZone({
  onFilesSelected,
  accept = "*",
  multiple = true,
  title = "Drop files here",
  subtitle = "or click to select",
  className = "",
  isDragOver = false,
}) {
  return (
    <div
      className={`relative rounded-lg border-2 border-dashed transition-colors duration-200 ease-in-out ${
        isDragOver
          ? "border-primary bg-primary/5"
          : "border-muted-foreground/25 hover:border-primary/50"
      } ${className}`}
    >
      <input
        type="file"
        className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
        onChange={(e) => {
          const files = Array.from(e.target.files || []);
          onFilesSelected(files);
          e.target.value = ""; // Reset input
        }}
        accept={accept}
        multiple={multiple}
      />
      <div className="flex flex-col items-center justify-center p-6 text-center">
        <div className="flex items-center justify-center w-12 h-12 mb-4 rounded-full bg-muted">
          <File className="w-6 h-6 text-muted-foreground" />
        </div>
        <p className="text-sm font-medium">{title}</p>
        <p className="mt-1 text-xs text-muted-foreground">{subtitle}</p>
      </div>
    </div>
  );
}

export function FilePreview({ file, onDelete }) {
  const Icon = getFileIcon(file.type);

  return (
    <div className="flex items-center gap-3 p-3 rounded-lg border bg-card text-card-foreground">
      <div className="flex items-center justify-center w-10 h-10 rounded-lg bg-muted">
        <Icon className="w-5 h-5 text-muted-foreground" />
      </div>
      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium truncate">{file.name}</p>
        <p className="text-xs text-muted-foreground">
          {(file.size / 1024 / 1024).toFixed(2)} MB
        </p>
      </div>
      <button
        onClick={() => onDelete(file)}
        className="p-2 text-muted-foreground hover:text-destructive transition-colors"
        aria-label="Remove file"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 24 24"
          strokeWidth={1.5}
          stroke="currentColor"
          className="w-5 h-5"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            d="M6 18L18 6M6 6l12 12"
          />
        </svg>
      </button>
    </div>
  );
}
