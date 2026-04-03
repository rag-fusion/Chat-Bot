import { useState, useRef, useEffect } from "react";
import { useChatId }     from "./hooks/useChatId";
import { uploadFile, sendQuery } from "./api/client";
import FileUpload        from "./components/FileUpload";
import CitationPanel     from "./components/CitationPanel";
import "./App.css";

const MODALITY_ICONS = { pdf: "📄", docx: "📝", image: "🖼️", audio: "🎵" };

export default function App() {
  const chatId                      = useChatId();
  const [messages, setMessages]     = useState([]);
  const [input, setInput]           = useState("");
  const [uploading, setUploading]   = useState(false);
  const [querying, setQuerying]     = useState(false);
  const messagesEndRef               = useRef(null);

  // Auto-scroll to bottom when new message arrives
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // ── UPLOAD ──────────────────────────────────────────────────────────
  async function handleUpload(file) {
    setUploading(true);

    // Immediately show "uploading" message in chat
    const tempId = Date.now();
    setMessages(prev => [...prev, {
      id:      tempId,
      type:    "file-uploading",
      name:    file.name,
      size:    file.size,
    }]);

    try {
      const result = await uploadFile(chatId, file);

      // Replace temp message with success
      setMessages(prev => prev.map(m =>
        m.id === tempId
          ? {
              id:       tempId,
              type:     "file-done",
              name:     result.file_name,
              modality: result.modality,
              chunks:   result.chunks_indexed,
            }
          : m
      ));
    } catch (err) {
      setMessages(prev => prev.map(m =>
        m.id === tempId
          ? { id: tempId, type: "file-error", name: file.name, error: err.message }
          : m
      ));
    } finally {
      setUploading(false);
    }
  }

  // ── QUERY ───────────────────────────────────────────────────────────
  async function handleSend() {
    const q = input.trim();
    if (!q || querying) return;

    // Add user message
    setMessages(prev => [...prev, { id: Date.now(), type: "user", text: q }]);
    setInput("");  // Clear input immediately after send

    setQuerying(true);
    const thinkingId = Date.now() + 1;
    setMessages(prev => [...prev, { id: thinkingId, type: "thinking" }]);

    try {
      const result = await sendQuery(chatId, q);

      // Replace thinking bubble with real answer
      setMessages(prev => prev.map(m =>
        m.id === thinkingId
          ? {
              id:        thinkingId,
              type:      "answer",
              text:      result.answer,
              citations: result.citations || [],
            }
          : m
      ));
    } catch (err) {
      setMessages(prev => prev.map(m =>
        m.id === thinkingId
          ? { id: thinkingId, type: "error", text: "Error: " + err.message }
          : m
      ));
    } finally {
      setQuerying(false);
    }
  }

  function handleKeyDown(e) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  }

  // ── RENDER MESSAGE ───────────────────────────────────────────────────
  function renderMessage(msg) {
    switch (msg.type) {
      case "file-uploading":
        return (
          <div key={msg.id} className="msg msg-file">
            <span className="file-icon">📎</span>
            <div className="file-info">
              <span className="file-name">{msg.name}</span>
              <span className="file-status uploading">Uploading & indexing...</span>
            </div>
          </div>
        );

      case "file-done":
        return (
          <div key={msg.id} className="msg msg-file success">
            <span className="file-icon">{MODALITY_ICONS[msg.modality] || "📎"}</span>
            <div className="file-info">
              <span className="file-name">{msg.name}</span>
              <span className="file-status success">
                ✓ Indexed — {msg.chunks} chunks
              </span>
            </div>
          </div>
        );

      case "file-error":
        return (
          <div key={msg.id} className="msg msg-file error">
            <span className="file-icon">❌</span>
            <div className="file-info">
              <span className="file-name">{msg.name}</span>
              <span className="file-status error">{msg.error}</span>
            </div>
          </div>
        );

      case "user":
        return (
          <div key={msg.id} className="msg msg-user">
            <p>{msg.text}</p>
          </div>
        );

      case "thinking":
        return (
          <div key={msg.id} className="msg msg-bot thinking">
            <span className="dot" /><span className="dot" /><span className="dot" />
          </div>
        );

      case "answer":
        return (
          <div key={msg.id} className="msg msg-bot">
            <p className="answer-text">{msg.text}</p>
            <CitationPanel citations={msg.citations} chatId={chatId} />
          </div>
        );

      case "error":
        return (
          <div key={msg.id} className="msg msg-bot error-msg">
            <p>{msg.text}</p>
          </div>
        );

      default:
        return null;
    }
  }

  // ── FULL RENDER ──────────────────────────────────────────────────────
  return (
    <div className="app">
      <header className="app-header">
        <h1>🧠 Multimodal RAG</h1>
        <span className="session-id">Session: {chatId.slice(0, 8)}…</span>
      </header>

      <main className="chat-area">
        {messages.length === 0 && (
          <div className="empty-state">
            <p>Upload a file above, then ask questions about it.</p>
            <p className="hint">Supports PDF · DOCX · Images · Audio</p>
          </div>
        )}
        {messages.map(renderMessage)}
        <div ref={messagesEndRef} />
      </main>

      <footer className="chat-footer">
        <FileUpload onUpload={handleUpload} disabled={uploading} />
        <div className="input-row">
          <textarea
            className="chat-input"
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask a question about your documents…"
            rows={2}
            disabled={querying}
          />
          <button
            className="send-btn"
            onClick={handleSend}
            disabled={!input.trim() || querying}
          >
            {querying ? "…" : "Send"}
          </button>
        </div>
      </footer>
    </div>
  );
}
