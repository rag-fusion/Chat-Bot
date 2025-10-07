import { useEffect, useState } from "react";
import ChatUI from "./ChatUI"; // Changed import from ChatWindow to ChatUI
import Uploader from "./Uploader";
import ResultItem from "./ResultItem";
import SourceModal from "./SourceModal";

function App() {
  const [messages, setMessages] = useState([]);
  const [isTyping, setIsTyping] = useState(false);
  const [results, setResults] = useState([]);
  const [modalItem, setModalItem] = useState(null);
  const [dark, setDark] = useState(() => {
    if (typeof window === "undefined") return false;
    const saved = localStorage.getItem("theme-dark");
    return saved ? JSON.parse(saved) : false;
  });

  useEffect(() => {
    document.documentElement.classList.toggle("dark", dark);
    localStorage.setItem("theme-dark", JSON.stringify(dark));
  }, [dark]);

  const handleSend = async (text) => {
    // The payload is now just the input text from ChatUI
    setMessages((prev) => [...prev, { role: "user", content: text }]);
    setIsTyping(true);
    try {
      const res = await fetch("http://localhost:8000/query", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: text }),
      });
      const data = await res.json();
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: data.answer,
          sources: data.sources,
          onOpenSource: setModalItem,
        },
      ]);
    } catch (e) {
      console.error(e);
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: "Sorry, I encountered an error." },
      ]);
    }
    setIsTyping(false);
  };

  const doSearch = async (query) => {
    if (!query || !query.trim()) {
      setResults([]);
      return;
    }
    const res = await fetch("http://localhost:8000/search/similarity", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query, k: 8 }),
    });
    const data = await res.json();
    setResults(data.results || []);
  };

  return (
    <div className="min-h-screen bg-gray-50 text-gray-900 transition-colors duration-300 dark:bg-neutral-950 dark:text-neutral-100">
      <main className="max-w-4xl mx-auto p-4 sm:p-6 md:p-8 space-y-8">
        <header className="flex items-center justify-between">
          <h1 className="text-2xl sm:text-3xl font-bold bg-gradient-to-r from-violet-600 to-fuchsia-500 text-transparent bg-clip-text">
            RAG Offline Chatbot
          </h1>
          <button
            onClick={() => setDark((d) => !d)}
            className="rounded-full border px-4 py-2 text-sm font-medium shadow-sm bg-white/60 backdrop-blur-sm hover:shadow-md transition-shadow dark:bg-neutral-900 dark:border-neutral-700"
            aria-label="Toggle theme"
          >
            {dark ? "Light ☀️" : "Dark 🌙"}
          </button>
        </header>

        <Uploader onUploaded={() => doSearch(null)} />

        {/* --- THIS IS THE KEY CHANGE --- */}
        <ChatUI
          messages={messages}
          onSend={handleSend} // Prop name changed from onQuery to onSend
          isTyping={isTyping}
        />
        {/* ----------------------------- */}

        {results.length > 0 && (
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {results.map((r, i) => (
              <ResultItem key={i} item={r} onOpen={setModalItem} />
            ))}
          </div>
        )}
      </main>
      {modalItem && (
        <SourceModal item={modalItem} onClose={() => setModalItem(null)} />
      )}
    </div>
  );
}

export default App;