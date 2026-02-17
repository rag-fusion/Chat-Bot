import { X, FileText } from "lucide-react";

export default function FileBadge({ fileName, onRemove, variant = "default" }) {
  const getFileIcon = () => {
    if (!fileName) return "📄";
    const ext = fileName.split('.').pop().toLowerCase();
    if (ext === 'pdf') return "📄";
    if (['jpg', 'jpeg', 'png', 'webp', 'gif'].includes(ext)) return "🖼️";
    if (['mp3', 'wav', 'ogg', 'm4a'].includes(ext)) return "🎵";
    if (['doc', 'docx'].includes(ext)) return "📝";
    return "📄";
  };

  const getFileType = () => {
    if (!fileName) return "FILE";
    const ext = fileName.split('.').pop().toUpperCase();
    return ext;
  };

  return (
    <div 
      className={`inline-flex items-center gap-2 px-3 py-2 rounded-lg bg-red-500 text-white text-sm font-medium shadow-sm transition-colors ${
        onRemove ? "hover:bg-red-600" : ""
      } ${
        variant === "clickable" ? "cursor-pointer hover:bg-red-600" : ""
      }`}
      onClick={() => variant === "clickable" && onRemove && typeof onRemove === 'function' ? onRemove() : null}
      // Wait, if variant is clickable, onRemove might be expected to be the click handler? 
      // No, in ChatUI I will pass `onClick` separately or just reuse `onRemove` if I change the signature.
      // Better: keep `onRemove` for the "X" button. Add `onClick` for the badge itself.
    >
      <div 
        className={`flex items-center gap-2 ${variant === "clickable" ? "cursor-pointer" : ""}`}
        onClick={variant === "clickable" ? onRemove : undefined}
      >
        <div className="w-8 h-8 bg-red-600 rounded flex items-center justify-center">
          <FileText className="w-4 h-4" />
        </div>
        <div className="flex flex-col items-start">
          <span className="text-sm font-semibold leading-tight">{fileName}</span>
          <span className="text-xs opacity-90">{getFileType()}</span>
        </div>
      </div>
      {onRemove && variant !== "clickable" && (
        <button
          onClick={(e) => {
            e.stopPropagation();
            onRemove();
          }}
          className="ml-1 p-1 hover:bg-red-700 rounded-full transition-colors"
          aria-label="Remove file"
        >
          <X className="w-4 h-4" />
        </button>
      )}
    </div>
  );
}
