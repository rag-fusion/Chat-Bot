import { useCallback, useState } from "react";

export default function Uploader({ onUploaded }) {
  const [dragOver, setDragOver] = useState(false);
  const [status, setStatus] = useState("");

  const onDrop = useCallback(async (e) => {
    e.preventDefault();
    setDragOver(false);
    const files = Array.from(e.dataTransfer.files || []);
    if (!files.length) return;
    await uploadMany(files);
  }, []);

  const upload = async (file) => {
    setStatus(`Uploading ${file.name}...`);
    const form = new FormData();
    form.append("file", file);
    const res = await fetch("http://localhost:8000/ingest", {
      method: "POST",
      body: form,
    });
    const data = await res.json();
    setStatus(`Indexed ${data.vectors_indexed} vectors from ${data.file}`);
    onUploaded?.(data);
  };

  const uploadMany = async (files) => {
    if (!files.length) return;
    if (files.length === 1) {
      return upload(files[0]);
    }
    setStatus(`Uploading ${files.length} files...`);
    const form = new FormData();
    files.forEach((f) => form.append("files", f));
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
  };

  return (
    <div
      onDragOver={(e) => {
        e.preventDefault();
        setDragOver(true);
      }}
      onDragLeave={() => setDragOver(false)}
      onDrop={onDrop}
      className={
        "rounded-xl border-2 border-dashed p-6 text-center transition-colors " +
        (dragOver
          ? "bg-violet-50 border-violet-400 dark:bg-violet-900/30 dark:border-violet-500"
          : "bg-white dark:bg-neutral-900 border-gray-300 dark:border-neutral-700")
      }
    >
      <p className="text-sm text-gray-600 dark:text-gray-400">
        Drag & drop documents here or
      </p>
      <label className="inline-block mt-3 cursor-pointer rounded-lg px-4 py-2 bg-violet-600 text-white font-medium shadow-sm transition-transform hover:scale-[1.02] active:scale-[0.98]">
        Browse Files
        <input
          type="file"
          className="hidden"
          multiple
          onChange={(e) => {
            const files = Array.from(e.target.files || []);
            if (files.length) uploadMany(files);
          }}
        />
      </label>
      {status && <div className="mt-3 text-sm text-gray-500 dark:text-gray-400">{status}</div>}
    </div>
  );
}