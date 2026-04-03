const BASE = "http://localhost:8000";

/**
 * Upload a file to a chat session.
 * Returns { file_name, file_id, modality, chunks_indexed }
 */
export async function uploadFile(chatId, file) {
  const form = new FormData();
  form.append("file", file);
  form.append("chat_id", chatId);

  const res = await fetch(`${BASE}/upload`, { method: "POST", body: form });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `Upload failed (${res.status})`);
  }
  return res.json();
}

/**
 * Ask a question in a chat session.
 * Returns { answer, citations, citation_map }
 */
export async function sendQuery(chatId, question) {
  const res = await fetch(`${BASE}/query`, {
    method:  "POST",
    headers: { "Content-Type": "application/json" },
    body:    JSON.stringify({ chat_id: chatId, question }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `Query failed (${res.status})`);
  }
  return res.json();
}

/**
 * Fetch metadata for a specific vector_id (for citation viewer).
 */
export async function getChunkSource(chatId, vectorId) {
  const res = await fetch(`${BASE}/viewer/${chatId}/${vectorId}`);
  if (!res.ok) throw new Error("Source not found");
  return res.json();
}

/**
 * Get URL to serve the original file.
 */
export function getFileUrl(chatId, filename) {
  return `${BASE}/file/${chatId}/${encodeURIComponent(filename)}`;
}
