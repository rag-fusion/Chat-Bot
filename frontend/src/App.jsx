import { useEffect, useState } from "react";
import { API_BASE_URL } from "./config";
import ChatUI from "./components/ChatUI";
import ContextViewer from "./components/ContextViewer";
import SourceModal from "./components/SourceModal";
import { Sheet, SheetContent, SheetTrigger } from "./components/ui/sheet";
import { Menu, X, Database } from "lucide-react";

function App() {
  const [messages, setMessages] = useState([]);
  const [isTyping, setIsTyping] = useState(false);
  const [results, setResults] = useState([]);
  const [modalItem, setModalItem] = useState(null);
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const [showSidebar, setShowSidebar] = useState(true);
  const [indexedDocs, setIndexedDocs] = useState(0);
  const [isDarkMode, setIsDarkMode] = useState(true);

  // Static chat history for demo
  const [chatHistory] = useState([
    { id: 1, title: "What is RAG?", date: "Today" },
    { id: 2, title: "Document analysis help", date: "Yesterday" },
    { id: 3, title: "Audio transcription query", date: "Nov 20" },
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
          content:
            "You're offline. Don't worry, you can still query your uploaded documents!",
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
      const res = await fetch(`${API_BASE_URL}/query`, {
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
        content: `Successfully indexed: ${
          data.file || "document"
        }\nVectors indexed: ${data.vectors_indexed || 0}`,
      },
    ]);
  };

  return (
    <div
      className={`flex h-screen w-full overflow-hidden ${
        isDarkMode ? "bg-gray-900" : "bg-white"
      }`}
    >
      {/* Mobile Navigation */}
      <div className="lg:hidden fixed top-4 left-4 z-50">
        <Sheet>
          <SheetTrigger asChild>
            <button
              className={`p-2 rounded-md transition-colors ${
                isDarkMode
                  ? "bg-gray-800 text-gray-300 hover:bg-gray-700"
                  : "bg-gray-100 text-gray-700 hover:bg-gray-200"
              }`}
            >
              <Menu className="w-5 h-5" />
            </button>
          </SheetTrigger>
          <SheetContent
            side="left"
            className={`w-[280px] p-0 border-r ${
              isDarkMode
                ? "bg-gray-800 border-gray-700 text-gray-100"
                : "bg-white border-gray-200 text-gray-900"
            }`}
          >
            <div className="p-3 flex-1 overflow-y-auto flex flex-col h-full">
              <button
                onClick={() => {
                  setMessages([]);
                  setResults([]);
                }}
                className={`w-full flex items-center justify-center gap-2 px-4 py-3 rounded-lg border transition-all text-sm font-medium mb-4 ${
                  isDarkMode
                    ? "border-gray-600 hover:bg-gray-700 text-gray-100"
                    : "border-gray-300 hover:bg-gray-100 text-gray-900"
                }`}
              >
                <span className="text-lg">+</span> New Chat
              </button>

              <div className="mb-6 flex-1">
                <div
                  className={`text-xs font-semibold mb-2 px-2 ${
                    isDarkMode ? "text-gray-500" : "text-gray-600"
                  }`}
                >
                  Chat History
                </div>
                <div className="space-y-1">
                  {chatHistory.map((chat) => (
                    <div
                      key={chat.id}
                      className={`px-3 py-2 rounded-lg cursor-pointer transition-colors ${
                        isDarkMode ? "hover:bg-gray-700" : "hover:bg-gray-100"
                      }`}
                    >
                      <div
                        className={`text-sm truncate ${
                          isDarkMode ? "text-gray-100" : "text-gray-900"
                        }`}
                      >
                        {chat.title}
                      </div>
                      <div
                        className={`text-xs ${
                          isDarkMode ? "text-gray-500" : "text-gray-600"
                        }`}
                      >
                        {chat.date}
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              <div className="px-2 mb-4">
                <div
                  className={`text-xs font-semibold mb-2 ${
                    isDarkMode ? "text-gray-500" : "text-gray-600"
                  }`}
                >
                  Database Stats
                </div>
                <div
                  className={`text-sm flex items-center gap-2 px-3 py-2 rounded-lg ${
                    isDarkMode
                      ? "bg-gray-700 text-gray-400"
                      : "bg-gray-100 text-gray-600"
                  }`}
                >
                  <Database className="w-4 h-4" />
                  {indexedDocs} indexed
                </div>
              </div>

              {/* User Area */}
              <div
                className={`border-t pt-3 ${
                  isDarkMode ? "border-gray-700" : "border-gray-200"
                }`}
              >
                <div
                  className={`flex items-center gap-3 px-3 py-2 rounded-lg cursor-pointer transition-colors ${
                    isDarkMode ? "hover:bg-gray-700" : "hover:bg-gray-100"
                  }`}
                >
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
        } hidden lg:flex flex-col transition-all duration-300 ease-in-out overflow-hidden border-r ${
          isDarkMode
            ? "bg-gray-800 text-gray-100 border-gray-700"
            : "bg-white text-gray-900 border-gray-200"
        }`}
      >
        <div className="p-3 flex-1 overflow-y-auto flex flex-col">
          <button
            onClick={() => {
              setMessages([]);
              setResults([]);
            }}
            className={`w-full flex items-center justify-center gap-2 px-4 py-3 rounded-lg border transition-all text-sm font-medium mb-6 ${
              isDarkMode
                ? "border-gray-600 hover:bg-gray-700 text-gray-100"
                : "border-gray-300 hover:bg-gray-100 text-gray-900"
            }`}
          >
            <span className="text-lg">+</span> New Chat
          </button>

          <div className="mb-6 flex-1">
            <div
              className={`text-xs font-semibold mb-3 px-2 ${
                isDarkMode ? "text-gray-500" : "text-gray-600"
              }`}
            >
              Chat History
            </div>
            <div className="space-y-1">
              {chatHistory.map((chat) => (
                <div
                  key={chat.id}
                  className={`px-3 py-2 rounded-lg cursor-pointer transition-colors group ${
                    isDarkMode ? "hover:bg-gray-700" : "hover:bg-gray-100"
                  }`}
                >
                  <div
                    className={`text-sm truncate ${
                      isDarkMode ? "text-gray-100" : "text-gray-900"
                    }`}
                  >
                    {chat.title}
                  </div>
                  <div
                    className={`text-xs ${
                      isDarkMode ? "text-gray-500" : "text-gray-600"
                    }`}
                  >
                    {chat.date}
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="px-2 mb-4">
            <div
              className={`text-xs font-semibold mb-2 ${
                isDarkMode ? "text-gray-500" : "text-gray-600"
              }`}
            >
              Database Stats
            </div>
            <div
              className={`text-sm flex items-center gap-2 px-3 py-2 rounded-lg ${
                isDarkMode
                  ? "bg-gray-700 text-gray-400"
                  : "bg-gray-100 text-gray-600"
              }`}
            >
              <Database className="w-4 h-4" />
              {indexedDocs} indexed
            </div>
          </div>
        </div>

        {/* User Area at bottom */}
        <div
          className={`p-3 border-t ${
            isDarkMode ? "border-gray-700" : "border-gray-200"
          }`}
        >
          <div
            className={`flex items-center gap-3 px-3 py-2 rounded-lg cursor-pointer transition-colors ${
              isDarkMode ? "hover:bg-gray-700" : "hover:bg-gray-100"
            }`}
          >
            <div className="w-8 h-8 rounded-full bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center text-white font-semibold text-sm">
              U
            </div>
            <div
              className={`text-sm font-medium ${
                isDarkMode ? "text-gray-100" : "text-gray-900"
              }`}
            >
              User
            </div>
          </div>
        </div>
      </aside>

      {/* Main Content Area */}
      <main
        className={`flex-1 flex flex-col h-full relative min-w-0 ${
          isDarkMode ? "bg-gray-900" : "bg-white"
        }`}
      >
        {/* Top Navbar */}
        <header
          className={`h-14 flex items-center justify-between px-6 border-b ${
            isDarkMode
              ? "border-gray-700 bg-gray-800"
              : "border-gray-200 bg-white"
          }`}
        >
          <div className="flex items-center gap-3">
            <button
              onClick={() => setShowSidebar(!showSidebar)}
              className={`hidden lg:block p-2 rounded-lg transition-colors ${
                isDarkMode
                  ? "text-gray-400 hover:bg-gray-700"
                  : "text-gray-600 hover:bg-gray-100"
              }`}
            >
              {showSidebar ? (
                <X className="w-5 h-5" />
              ) : (
                <Menu className="w-5 h-5" />
              )}
            </button>
            <h1
              className={`text-lg font-semibold ${
                isDarkMode ? "text-gray-100" : "text-gray-900"
              }`}
            >
              Local AI Assistant
            </h1>
          </div>
          <div className="flex items-center gap-4">
            <button
              onClick={() => setIsDarkMode(!isDarkMode)}
              className={`px-3 py-1.5 rounded-full text-sm transition-colors ${
                isDarkMode
                  ? "bg-gray-700 text-yellow-400 hover:bg-gray-600"
                  : "bg-gray-100 text-gray-700 hover:bg-gray-200"
              }`}
              title="Toggle dark mode"
            >
              {isDarkMode ? "☀️" : "🌙"}
            </button>
            <div
              className={`px-3 py-1.5 rounded-full text-xs font-medium ${
                isOnline
                  ? "bg-green-100 text-green-700"
                  : "bg-gray-100 text-gray-600"
              }`}
            >
              {isOnline ? "● Online" : "○ Offline"}
            </div>
          </div>
        </header>

        {/* Chat Area */}
        <div
          className={`flex-1 overflow-hidden relative ${
            isDarkMode ? "bg-gray-900" : "bg-white"
          }`}
        >
          <ChatUI
            messages={messages}
            onSend={handleSend}
            isTyping={isTyping}
            onUploadComplete={handleUploadComplete}
            isDarkMode={isDarkMode}
          />
        </div>
      </main>

      {/* Right Sidebar (Context) - Desktop only */}
      {results.length > 0 && (
        <aside
          className={`w-80 border-l hidden xl:flex flex-col ${
            isDarkMode
              ? "border-gray-700 bg-gray-800"
              : "border-gray-200 bg-white"
          }`}
        >
          <div
            className={`p-4 border-b font-semibold flex items-center justify-between ${
              isDarkMode ? "border-gray-700" : "border-gray-200"
            }`}
          >
            <span className={isDarkMode ? "text-gray-100" : "text-gray-900"}>
              Sources
            </span>
            <span
              className={`text-xs px-2 py-1 rounded-full font-medium ${
                isDarkMode
                  ? "bg-gray-700 text-gray-300"
                  : "bg-gray-100 text-gray-600"
              }`}
            >
              {results.length}
            </span>
          </div>
          <div className="flex-1 overflow-y-auto p-4">
            <ContextViewer
              results={results}
              onOpen={setModalItem}
              isDarkMode={isDarkMode}
            />
          </div>
        </aside>
      )}

      <SourceModal item={modalItem} onClose={() => setModalItem(null)} />
    </div>
  );
}

export default App;
