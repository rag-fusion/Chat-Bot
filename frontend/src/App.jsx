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

function App() {
  const [messages, setMessages] = useState([]);
  const [isTyping, setIsTyping] = useState(false);
  const [results, setResults] = useState([]);
  const [modalItem, setModalItem] = useState(null);
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const [dark, setDark] = useState(() => {
    if (typeof window === "undefined") return false;
    const saved = localStorage.getItem("theme-dark");
    return saved ? JSON.parse(saved) : false;
  });

  // Monitor online/offline status
  useEffect(() => {
    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);

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
    <div className="flex min-h-screen flex-col bg-background">
      <Header dark={dark} setDark={setDark} isOnline={isOnline} />

      {/* Mobile Navigation */}
      <div className="fixed bottom-4 left-4 right-4 flex items-center justify-center gap-2 lg:hidden">
        <Sheet>
          <SheetTrigger asChild>
            <button className="inline-flex h-10 items-center justify-center rounded-md bg-primary px-4 text-sm font-medium text-primary-foreground ring-offset-background transition-colors hover:bg-primary/90 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2">
              Upload Files
            </button>
          </SheetTrigger>
          <SheetContent side="left">
            <SheetHeader>
              <SheetTitle>Upload Files</SheetTitle>
            </SheetHeader>
            <div className="mt-4">
              <Uploader onUploaded={() => doSearch(null)} />
            </div>
          </SheetContent>
        </Sheet>

        <Sheet>
          <SheetTrigger asChild>
            <button className="inline-flex h-10 items-center justify-center rounded-md bg-primary px-4 text-sm font-medium text-primary-foreground ring-offset-background transition-colors hover:bg-primary/90 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2">
              View Context
            </button>
          </SheetTrigger>
          <SheetContent>
            <SheetHeader>
              <SheetTitle>Retrieved Context</SheetTitle>
            </SheetHeader>
            <div className="mt-4">
              <ContextViewer results={results} onOpen={setModalItem} />
            </div>
          </SheetContent>
        </Sheet>
      </div>

      <div className="container mx-auto flex flex-1 gap-4 p-4">
        {/* Left Panel - File Upload */}
        <aside className="hidden lg:flex w-72 flex-col gap-4">
          <div className="rounded-lg border bg-card text-card-foreground shadow-sm">
            <div className="p-6">
              <h3 className="text-lg font-semibold mb-4">Upload Files</h3>
              <Uploader onUploaded={() => doSearch(null)} />
            </div>
          </div>
        </aside>

        {/* Center Panel - Chat Interface */}
        <div className="flex-1 flex flex-col min-w-0">
          <div className="rounded-lg border bg-card text-card-foreground shadow-sm h-full">
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
        <aside className="hidden lg:flex w-80 flex-col gap-4">
          <div className="rounded-lg border bg-card text-card-foreground shadow-sm">
            <div className="p-6">
              <h3 className="text-lg font-semibold mb-4">Retrieved Context</h3>
              <ContextViewer results={results} onOpen={setModalItem} />
            </div>
          </div>
        </aside>
      </div>

      {modalItem && (
        <SourceModal item={modalItem} onClose={() => setModalItem(null)} />
      )}
    </div>
  );
}

export default App;
