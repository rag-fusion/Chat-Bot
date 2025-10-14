import { useEffect, useState } from "react";
import ChatUI from "./components/ChatUI";
import Uploader from "./Uploader";
import ContextViewer from "./components/ContextViewer";
import SourceModal from "./components/SourceModal";
import Header from "./components/Header";
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from "./components/ui/sheet";
import { Menu, X, FileText, Database } from "lucide-react";

function App() {
  const [messages, setMessages] = useState([]);
  const [isTyping, setIsTyping] = useState(false);
  const [results, setResults] = useState([]);
  const [modalItem, setModalItem] = useState(null);
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const [showSidebar, setShowSidebar] = useState(true);
  const [indexedDocs, setIndexedDocs] = useState(0);
  const [dark, setDark] = useState(() => {
    if (typeof window === "undefined") return false;
    const saved = localStorage.getItem("theme-dark");
    return saved ? JSON.parse(saved) : false;
  });

  // Monitor online/offline status
  useEffect(() => {
    const handleOnline = () => {
      setIsOnline(true);
      setMessages((prev) => [
        ...prev,
        {
          role: "system",
          content: "✅ Connection restored. You're back online!",
        },
      ]);
    };

    const handleOffline = () => {
      setIsOnline(false);
      setMessages((prev) => [
        ...prev,
        {
          role: "system",
          content: "📴 You're offline. Don't worry, you can still query your uploaded documents!",
        },
      ]);
    };

    window.addEventListener("online", handleOnline);
    window.addEventListener("offline", handleOffline);

    return () => {
      window.removeEventListener("online", handleOnline);
      window.removeEventListener("offline", handleOffline);
    };
  }, []);

  useEffect(() => {
    document.documentElement.classList.toggle("dark", dark);
    localStorage.setItem("theme-dark", JSON.stringify(dark));
  }, [dark]);

  // Welcome message on first load
  useEffect(() => {
    if (messages.length === 0) {
      setMessages([
        {
          role: "assistant",
          content:
            "👋 Welcome to your Offline RAG Assistant!\n\nI can help you:\n• 📄 Query PDF documents\n• 🖼️ Analyze images\n• 🎵 Search audio transcripts\n• 📝 Search through text files\n\nUpload your documents to get started!",
        },
      ]);
    }
  }, []);

  const handleSend = async (text) => {
    setMessages((prev) => [...prev, { role: "user", content: text }]);
    setIsTyping(true);

    try {
      const res = await fetch("http://localhost:8000/query", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: text }),
      });

      if (!res.ok) throw new Error("Query failed");

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

      // Update context viewer with retrieved documents
      if (data.sources) {
        setResults(data.sources);
      }
    } catch (e) {
      console.error(e);
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: isOnline
            ? "❌ Sorry, I couldn't connect to the server. Please check if the backend is running."
            : "📴 You're offline. Make sure your documents are already indexed to query them.",
        },
      ]);
    }
    setIsTyping(false);
  };

  const doSearch = async (query) => {
    if (!query || !query.trim()) {
      setResults([]);
      return;
    }
    try {
      const res = await fetch("http://localhost:8000/search/similarity", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query, k: 8 }),
      });
      const data = await res.json();
      setResults(data.results || []);
    } catch (e) {
      console.error("Search failed:", e);
    }
  };

  const handleUploadComplete = (data) => {
    setIndexedDocs((prev) => prev + 1);
    setMessages((prev) => [
      ...prev,
      {
        role: "system",
        content: `✅ Successfully indexed: ${data.file || "document"}\n📊 Vectors indexed: ${data.vectors_indexed || 0}`,
      },
    ]);
  };

  return (
    <div className="flex min-h-screen flex-col bg-background">
      <Header dark={dark} setDark={setDark} isOnline={isOnline} />

      {/* Offline Banner */}
      {!isOnline && (
        <div className="bg-amber-500/10 border-b border-amber-500/20 px-4 py-2">
          <p className="text-sm text-center text-amber-700 dark:text-amber-400">
            🔌 Offline Mode Active - You can query already indexed documents
          </p>
        </div>
      )}

      {/* Mobile Navigation */}
      <div className="fixed bottom-4 left-4 right-4 flex items-center justify-center gap-2 lg:hidden z-50">
        <Sheet>
          <SheetTrigger asChild>
            <button className="flex-1 inline-flex h-12 items-center justify-center rounded-xl bg-primary px-6 text-sm font-medium text-primary-foreground shadow-lg hover:bg-primary/90 transition-all">
              <FileText className="w-4 h-4 mr-2" />
              Upload Files
            </button>
          </SheetTrigger>
          <SheetContent side="left" className="w-[300px] sm:w-[400px]">
            <SheetHeader>
              <SheetTitle>Upload Documents</SheetTitle>
            </SheetHeader>
            <div className="mt-6">
              <Uploader onUploaded={handleUploadComplete} />
            </div>
          </SheetContent>
        </Sheet>

        <Sheet>
          <SheetTrigger asChild>
            <button className="flex-1 inline-flex h-12 items-center justify-center rounded-xl bg-primary px-6 text-sm font-medium text-primary-foreground shadow-lg hover:bg-primary/90 transition-all">
              <Database className="w-4 h-4 mr-2" />
              Context
            </button>
          </SheetTrigger>
          <SheetContent className="w-[300px] sm:w-[400px]">
            <SheetHeader>
              <SheetTitle>Retrieved Context</SheetTitle>
            </SheetHeader>
            <div className="mt-6">
              <ContextViewer results={results} onOpen={setModalItem} />
            </div>
          </SheetContent>
        </Sheet>
      </div>

      <div className="container mx-auto flex flex-1 gap-4 p-4 pb-24 lg:pb-4">
        {/* Left Panel - File Upload */}
        <aside
          className={`hidden lg:flex w-80 flex-col gap-4 transition-all duration-300 ${
            showSidebar ? "" : "-ml-80 opacity-0"
          }`}
        >
          <div className="rounded-xl border bg-card text-card-foreground shadow-lg overflow-hidden">
            <div className="bg-gradient-to-r from-violet-500 to-fuchsia-500 p-4">
              <h3 className="text-lg font-bold text-white flex items-center gap-2">
                <FileText className="w-5 h-5" />
                Document Library
              </h3>
              <p className="text-xs text-white/80 mt-1">
                {indexedDocs} document(s) indexed
              </p>
            </div>
            <div className="p-6">
              <Uploader onUploaded={handleUploadComplete} />
            </div>
          </div>
        </aside>

        {/* Center Panel - Chat Interface */}
        <div className="flex-1 flex flex-col min-w-0">
          <div className="rounded-xl border bg-card text-card-foreground shadow-lg h-full overflow-hidden">
            <div className="p-6 h-full">
              <ChatUI
                messages={messages}
                onSend={handleSend}
                isTyping={isTyping}
              />
            </div>
          </div>
        </div>

        {/* Right Panel - Context Viewer */}
        <aside
          className={`hidden lg:flex w-80 flex-col gap-4 transition-all duration-300 ${
            showSidebar ? "" : "-mr-80 opacity-0"
          }`}
        >
          <div className="rounded-xl border bg-card text-card-foreground shadow-lg overflow-hidden">
            <div className="bg-gradient-to-r from-blue-500 to-cyan-500 p-4">
              <h3 className="text-lg font-bold text-white flex items-center gap-2">
                <Database className="w-5 h-5" />
                Retrieved Context
              </h3>
              <p className="text-xs text-white/80 mt-1">
                {results.length} result(s) found
              </p>
            </div>
            <div className="p-6 max-h-[calc(100vh-12rem)] overflow-y-auto">
              <ContextViewer results={results} onOpen={setModalItem} />
            </div>
          </div>
        </aside>
      </div>

      {/* Toggle Sidebar Button */}
      <button
        onClick={() => setShowSidebar(!showSidebar)}
        className="hidden lg:flex fixed top-20 right-4 z-50 w-10 h-10 items-center justify-center rounded-full bg-primary text-primary-foreground shadow-lg hover:scale-110 transition-transform"
      >
        {showSidebar ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
      </button>

      {modalItem && (
        <SourceModal item={modalItem} onClose={() => setModalItem(null)} />
      )}
    </div>
  );
}

export default App;