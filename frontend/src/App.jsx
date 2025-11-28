import { useEffect, useState } from "react";
import ChatUI from "./components/ChatUI";
import ContextViewer from "./components/ContextViewer";
import SourceModal from "./components/SourceModal";
import {
  Sheet,
  SheetContent,
  SheetTrigger,
} from "./components/ui/sheet";
import { Menu, X, Database } from "lucide-react";

function App() {
  const [messages, setMessages] = useState([]);
  const [isTyping, setIsTyping] = useState(false);
  const [results, setResults] = useState([]);
  const [modalItem, setModalItem] = useState(null);
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const [showSidebar, setShowSidebar] = useState(true);
  const [indexedDocs, setIndexedDocs] = useState(0);

  // Static chat history for demo
  const [chatHistory] = useState([
    { id: 1, title: "What is RAG?", date: "Today" },
    { id: 2, title: "Document analysis help", date: "Yesterday" },
    { id: 3, title: "Audio transcription query", date: "Nov 20" }
  ]);

  // Monitor online/offline status
  useEffect(() => {
    const handleOnline = () => {
      setIsOnline(true);
      setMessages((prev) => [
        ...prev,
        {
          role: "system",
          content: "Connection restored. You're back online!",
        },
      ]);
    };

    const handleOffline = () => {
      setIsOnline(false);
      setMessages((prev) => [
        ...prev,
        {
          role: "system",
          content: "You're offline. Don't worry, you can still query your uploaded documents!",
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

  // Welcome message on first load

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
            ? "Sorry, I couldn't connect to the server. Please check if the backend is running."
            : "You're offline. Make sure your documents are already indexed to query them.",
        },
      ]);
    }
    setIsTyping(false);
  };

  const handleUploadComplete = (data) => {
    setIndexedDocs((prev) => prev + 1);
    setMessages((prev) => [
      ...prev,
      {
        role: "system",
        content: `Successfully indexed: ${data.file || "document"}\nVectors indexed: ${data.vectors_indexed || 0}`,
      },
    ]);
  };

  return (
    <div className="flex h-screen w-full overflow-hidden bg-white">
      {/* Mobile Navigation */}
      <div className="lg:hidden fixed top-4 left-4 z-50">
        <Sheet>
          <SheetTrigger asChild>
            <button className="p-2 rounded-md bg-gray-100 text-gray-700 hover:bg-gray-200 transition-colors">
              <Menu className="w-5 h-5" />
            </button>
          </SheetTrigger>
          <SheetContent side="left" className="w-[280px] p-0 bg-gray-900 border-r border-gray-700 text-gray-100">
            <div className="p-3 flex-1 overflow-y-auto flex flex-col h-full">
              <button 
                onClick={() => {
                  setMessages([]);
                  setResults([]);
                }}
                className="w-full flex items-center justify-center gap-2 px-4 py-3 rounded-lg border border-gray-600 hover:bg-gray-800 transition-all text-sm font-medium mb-4"
              >
                <span className="text-lg">+</span> New Chat
              </button>
              
              <div className="mb-6 flex-1">
                <div className="text-xs font-semibold text-gray-500 mb-2 px-2">Chat History</div>
                <div className="space-y-1">
                  {chatHistory.map((chat) => (
                    <div key={chat.id} className="px-3 py-2 rounded-lg hover:bg-gray-800 cursor-pointer transition-colors">
                      <div className="text-sm truncate">{chat.title}</div>
                      <div className="text-xs text-gray-500">{chat.date}</div>
                    </div>
                  ))}
                </div>
              </div>

              <div className="px-2 mb-4">
                <div className="text-xs font-semibold text-gray-500 mb-2">Database Stats</div>
                <div className="text-sm text-gray-400 flex items-center gap-2 bg-gray-800 px-3 py-2 rounded-lg">
                  <Database className="w-4 h-4" />
                  {indexedDocs} indexed
                </div>
              </div>

              {/* User Area */}
              <div className="border-t border-gray-700 pt-3">
                <div className="flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-gray-800 cursor-pointer transition-colors">
                  <div className="w-8 h-8 rounded-full bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center text-white font-semibold text-sm">
                    U
                  </div>
                  <div className="text-sm font-medium">User</div>
                </div>
              </div>
            </div>
          </SheetContent>
        </Sheet>
      </div>

      {/* Sidebar (Desktop) */}
      <aside
        className={`${
          showSidebar ? "w-[260px]" : "w-0"
        } hidden lg:flex flex-col bg-gray-900 text-gray-100 transition-all duration-300 ease-in-out overflow-hidden border-r border-gray-700`}
      >
        <div className="p-3 flex-1 overflow-y-auto flex flex-col">
          <button 
            onClick={() => {
              setMessages([]);
              setResults([]);
            }}
            className="w-full flex items-center justify-center gap-2 px-4 py-3 rounded-lg border border-gray-600 hover:bg-gray-800 transition-all text-sm font-medium mb-6"
          >
            <span className="text-lg">+</span> New Chat
          </button>

          <div className="mb-6 flex-1">
             <div className="text-xs font-semibold text-gray-500 mb-3 px-2">Chat History</div>
             <div className="space-y-1">
               {chatHistory.map((chat) => (
                 <div 
                   key={chat.id} 
                   className="px-3 py-2 rounded-lg hover:bg-gray-800 cursor-pointer transition-colors group"
                 >
                   <div className="text-sm truncate">{chat.title}</div>
                   <div className="text-xs text-gray-500">{chat.date}</div>
                 </div>
               ))}
             </div>
          </div>

          <div className="px-2 mb-4">
             <div className="text-xs font-semibold text-gray-500 mb-2">Database Stats</div>
             <div className="text-sm text-gray-400 flex items-center gap-2 bg-gray-800 px-3 py-2 rounded-lg">
                <Database className="w-4 h-4" />
                {indexedDocs} indexed
             </div>
          </div>
        </div>

        {/* User Area at bottom */}
        <div className="p-3 border-t border-gray-700">
           <div className="flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-gray-800 cursor-pointer transition-colors">
              <div className="w-8 h-8 rounded-full bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center text-white font-semibold text-sm">
                 U
              </div>
              <div className="text-sm font-medium">User</div>
           </div>
        </div>
      </aside>

      {/* Main Content Area */}
      <main className="flex-1 flex flex-col h-full relative min-w-0 bg-white">
        {/* Top Navbar */}
        <header className="h-14 flex items-center justify-between px-6 border-b border-gray-200 bg-white">
           <div className="flex items-center gap-3">
             <button
               onClick={() => setShowSidebar(!showSidebar)}
               className="hidden lg:block p-2 rounded-lg text-gray-600 hover:bg-gray-100 transition-colors"
             >
               {showSidebar ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
             </button>
             <h1 className="text-lg font-semibold text-gray-900">Local AI Assistant</h1>
           </div>
           <div className="flex items-center gap-2">
              <div className={`px-3 py-1.5 rounded-full text-xs font-medium ${isOnline ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-600'}`}>
                {isOnline ? '● Online' : '○ Offline'}
              </div>
           </div>
        </header>

        {/* Chat Area */}
        <div className="flex-1 overflow-hidden relative bg-white">
          <ChatUI
            messages={messages}
            onSend={handleSend}
            isTyping={isTyping}
            onUploadComplete={handleUploadComplete}
          />
        </div>
      </main>

      {/* Right Sidebar (Context) - Desktop only */}
      {results.length > 0 && (
        <aside className="w-80 border-l border-gray-200 bg-white hidden xl:flex flex-col">
           <div className="p-4 border-b border-gray-200 font-semibold flex items-center justify-between">
              <span className="text-gray-900">Sources</span>
              <span className="text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded-full font-medium">{results.length}</span>
           </div>
           <div className="flex-1 overflow-y-auto p-4">
              <ContextViewer results={results} onOpen={setModalItem} />
           </div>
        </aside>
      )}

      {modalItem && (
        <SourceModal item={modalItem} onClose={() => setModalItem(null)} />
      )}
    </div>
  );
}

export default App;