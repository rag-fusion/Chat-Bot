import { useEffect, useState } from "react";
import { API_BASE_URL } from "./config";
import ChatUI from "./components/ChatUI";
import ContextViewer from "./components/ContextViewer";
import SourceModal from "./components/SourceModal";
import { Auth } from "./components/Auth";
import { Sheet, SheetContent, SheetTrigger } from "./components/ui/sheet";
import { Menu, X, Database, LogOut } from "lucide-react";

function App() {
  const [token, setToken] = useState(localStorage.getItem("token") || null);
  const [user, setUser] = useState(JSON.parse(localStorage.getItem("user") || "null"));
  
  const [messages, setMessages] = useState([]);
  const [isTyping, setIsTyping] = useState(false);
  const [results, setResults] = useState([]);
  const [modalItem, setModalItem] = useState(null);
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const [showSidebar, setShowSidebar] = useState(true);
  const [indexedDocs, setIndexedDocs] = useState(0);
  const [isDarkMode, setIsDarkMode] = useState(true);

  // Real Chat History
  const [chatHistory, setChatHistory] = useState([]);
  const [currentChatId, setCurrentChatId] = useState(null);

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

  // Fetch history on load/login
  useEffect(() => {
    if (token) {
        fetchHistory();
    }
  }, [token]);

  const handleLogin = (data) => {
      setToken(data.access_token);
      setUser(data.user);
      localStorage.setItem("token", data.access_token);
      localStorage.setItem("user", JSON.stringify(data.user));
  };

  const handleLogout = () => {
      setToken(null);
      setUser(null);
      localStorage.removeItem("token");
      localStorage.removeItem("user");
      setMessages([]);
      setChatHistory([]);
  };

  const fetchHistory = async () => {
      try {
          const res = await fetch(`${API_BASE_URL}/api/history`, {
              headers: { 'Authorization': `Bearer ${token}` }
          });
          
          if (res.status === 401) {
              handleLogout();
              return;
          }

          if (res.ok) {
              const data = await res.json();
              // data is list of {id, title, updated_at...}
              // Map to UI format if needed, but backend probably returns compatible dicts
              // Backend returns: [{id: str, title: str, updated_at: iso}, ...]
              // UI expects: {id, title, date}
              const formatted = data.map(c => ({
                  id: c.chat_id || c.id || c._id,
                  title: c.title,
                  date: new Date(c.updated_at).toLocaleDateString()
              }));
              setChatHistory(formatted);
          }
      } catch (e) {
          console.error("Failed to fetch history", e);
      }
  };

  const startNewChat = () => {
      setMessages([]);
      setResults([]);
      setCurrentChatId(null);
  };

  const loadChat = async (chatId) => {
      try {
          const res = await fetch(`${API_BASE_URL}/api/chat/${chatId}`, {
              headers: { 'Authorization': `Bearer ${token}` }
          });
          if (res.ok) {
              const chat = await res.json();
              setCurrentChatId(chatId);
              // Transform messages if needed. Backend: {messages: [{role, content, sources...}]}
              setMessages(chat.messages || []);
              
              // Maybe set results from last message?
              const lastMsg = chat.messages && chat.messages.length > 0 ? chat.messages[chat.messages.length - 1] : null;
              if (lastMsg && lastMsg.sources) {
                  setResults(lastMsg.sources);
              } else {
                  setResults([]);
              }
              
              // Close mobile drawer if open
          } else if (res.status === 401) {
              handleLogout();
          }
      } catch (e) {
          console.error("Failed to load chat", e);
      }
  };

  const handleSend = async (text) => {
    setMessages((prev) => [...prev, { role: "user", content: text }]);
    setIsTyping(true);

    let activeChatId = currentChatId;

    try {
      // Create chat if not exists
      if (!activeChatId) {
          const chatRes = await fetch(`${API_BASE_URL}/api/chat/new`, {
              method: "POST",
              headers: { 
                  "Content-Type": "application/json",
                  "Authorization": `Bearer ${token}`
              },
              body: JSON.stringify({ title: text.substring(0, 30) + "..." })
          });

          if (chatRes.status === 401) {
              handleLogout();
              setIsTyping(false);
              return;
          }

          if (chatRes.ok) {
              const chatData = await chatRes.json();
              activeChatId = chatData.chat_id || chatData.insert_id; // Check backend return
              // Backend returns result of insert_one? No, ChatHistory.create_chat returns {chat_id: str, ...} usually?
              // Let's assume backend returns {chat_id: ...} or similar.
              // Logic check: create_chat returns `str(result.inserted_id)` usually?
              // Let's assume it returns {id: ...} or just ID string.
              // Wait, previous grep showed `return await ChatHistory.create_chat`.
              // I need to be sure what `create_chat` returns.
              // Assuming it returns a dict with `id` or `chat_id`.
              // If it returns simple string (id), then `chatData` is the string if response is not json dict?
              // FastAPI returns JSON.
              // Let's assume dict.
              if (typeof chatData === 'string') activeChatId = chatData;
              else activeChatId = chatData.chat_id || chatData.id || chatData._id;
              
              setCurrentChatId(activeChatId);
              fetchHistory(); // Refresh list to show new chat
          }
      }

      const payload = { query: text };
      if (activeChatId) payload.chat_id = activeChatId;

      const res = await fetch(`${API_BASE_URL}/query`, {
        method: "POST",
        headers: { 
            "Content-Type": "application/json",
            "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify(payload),
      });

      if (res.status === 401) {
          handleLogout();
          setIsTyping(false);
          return;
      }

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

      if (data.sources) {
        setResults(data.sources);
      }
      
      // If chat was just created, maybe update title?
      // Backend does it. We should refresh history to see title.
      if (!currentChatId && activeChatId) {
          fetchHistory();
      }

    } catch (e) {
      console.error(e);
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: isOnline
            ? "Sorry, I couldn't connect to the server."
            : "You're offline.",
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
        content: `Successfully indexed: ${data.file || "document"}`,
      },
    ]);
  };

  if (!token) {
      return <Auth onLogin={handleLogin} />;
  }

  return (
    <div className={`flex h-screen w-full overflow-hidden ${isDarkMode ? "bg-gray-900" : "bg-white"}`}>
      {/* Mobile Navigation */}
      <div className="lg:hidden fixed top-4 left-4 z-50">
        <Sheet>
          <SheetTrigger asChild>
            <button className={`p-2 rounded-md ${isDarkMode ? "bg-gray-800 text-gray-300" : "bg-gray-100 text-gray-700"}`}>
              <Menu className="w-5 h-5" />
            </button>
          </SheetTrigger>
          <SheetContent side="left" className={`w-[280px] p-0 border-r ${isDarkMode ? "bg-gray-800 border-gray-700 text-gray-100" : "bg-white border-gray-200 text-gray-900"}`}>
            <div className="p-3 flex-1 overflow-y-auto flex flex-col h-full">
              <button onClick={startNewChat} className={`w-full flex items-center justify-center gap-2 px-4 py-3 rounded-lg border mb-4 ${isDarkMode ? "border-gray-600 hover:bg-gray-700" : "border-gray-300 hover:bg-gray-100"}`}>
                <span className="text-lg">+</span> New Chat
              </button>
              
              <div className="mb-6 flex-1">
                  <div className="text-xs font-semibold mb-2 px-2 opacity-70">Chat History</div>
                  <div className="space-y-1">
                      {chatHistory.map((chat) => (
                          <div key={chat.id} onClick={() => loadChat(chat.id)} className={`px-3 py-2 rounded-lg cursor-pointer truncate ${isDarkMode ? "hover:bg-gray-700" : "hover:bg-gray-100"} ${currentChatId === chat.id ? "bg-blue-100 dark:bg-blue-900" : ""}`}>
                              {chat.title}
                          </div>
                      ))}
                  </div>
              </div>

               {/* User Area */}
               <div className={`border-t pt-3 ${isDarkMode ? "border-gray-700" : "border-gray-200"}`}>
                <div className="flex items-center justify-between px-3 py-2">
                   <div className="flex items-center gap-3">
                        <div className="w-8 h-8 rounded-full bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center text-white font-bold">
                            {user?.full_name?.[0] || user?.email?.[0] || "U"}
                        </div>
                        <div className="text-sm font-medium truncate max-w-[120px]">
                            {user?.full_name || "User"}
                        </div>
                   </div>
                   <button onClick={handleLogout} className="text-red-500 hover:text-red-700"><LogOut className="w-4 h-4"/></button>
                </div>
              </div>
            </div>
          </SheetContent>
        </Sheet>
      </div>

      {/* Sidebar (Desktop) */}
      <aside className={`${showSidebar ? "w-[260px]" : "w-0"} hidden lg:flex flex-col transition-all duration-300 border-r ${isDarkMode ? "bg-gray-800 border-gray-700 text-gray-100" : "bg-white border-gray-200 text-gray-900"}`}>
        <div className="p-3 flex-1 overflow-y-auto flex flex-col">
          <button onClick={startNewChat} className={`w-full flex items-center justify-center gap-2 px-4 py-3 rounded-lg border mb-6 ${isDarkMode ? "border-gray-600 hover:bg-gray-700" : "border-gray-300 hover:bg-gray-100"}`}>
            <span className="text-lg">+</span> New Chat
          </button>
          
          <div className="mb-6 flex-1">
            <div className="text-xs font-semibold mb-3 px-2 opacity-70">Chat History</div>
            <div className="space-y-1">
              {chatHistory.map((chat) => (
                <div key={chat.id} onClick={() => loadChat(chat.id)} className={`px-3 py-2 rounded-lg cursor-pointer truncate text-sm ${isDarkMode ? "hover:bg-gray-700" : "hover:bg-gray-100"} ${currentChatId === chat.id ? "bg-blue-50 dark:bg-blue-900/50" : ""}`}>
                  {chat.title}
                </div>
              ))}
            </div>
          </div>

          <div className="px-2 mb-4">
             <div className="text-xs font-semibold mb-2 opacity-70">Database Stats</div>
             <div className={`text-sm flex items-center gap-2 px-3 py-2 rounded-lg ${isDarkMode ? "bg-gray-700 text-gray-400" : "bg-gray-100 text-gray-600"}`}>
               <Database className="w-4 h-4" /> {indexedDocs} indexed
             </div>
          </div>
        </div>

        {/* User Area at bottom */}
        <div className={`p-3 border-t ${isDarkMode ? "border-gray-700" : "border-gray-200"}`}>
           <div className="flex items-center justify-between px-3 py-2">
               <div className="flex items-center gap-3 overflow-hidden">
                    <div className="w-8 h-8 rounded-full bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center text-white font-bold shrink-0">
                        {user?.full_name?.[0] || user?.email?.[0] || "U"}
                    </div>
                    <div className="text-sm font-medium truncate">
                        {user?.full_name || "User"}
                    </div>
               </div>
               <button onClick={handleLogout} title="Logout" className="text-red-500 hover:text-red-700"><LogOut className="w-4 h-4"/></button>
           </div>
        </div>
      </aside>

      {/* Main Content Area */}
      <main className={`flex-1 flex flex-col h-full relative min-w-0 ${isDarkMode ? "bg-gray-900" : "bg-white"}`}>
        <header className={`h-14 flex items-center justify-between px-6 border-b ${isDarkMode ? "border-gray-700 bg-gray-800" : "border-gray-200 bg-white"}`}>
          <div className="flex items-center gap-3">
            <button onClick={() => setShowSidebar(!showSidebar)} className={`hidden lg:block p-2 rounded-lg ${isDarkMode ? "text-gray-400 hover:bg-gray-700" : "text-gray-600 hover:bg-gray-100"}`}>
              {showSidebar ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </button>
            <h1 className={`text-lg font-semibold ${isDarkMode ? "text-gray-100" : "text-gray-900"}`}>Local AI Assistant</h1>
          </div>
          <div className="flex items-center gap-4">
            <button onClick={() => setIsDarkMode(!isDarkMode)} className={`px-3 py-1.5 rounded-full text-sm ${isDarkMode ? "bg-gray-700 text-yellow-400" : "bg-gray-100 text-gray-700"}`} title="Toggle dark mode">{isDarkMode ? "☀️" : "🌙"}</button>
            <div className={`px-3 py-1.5 rounded-full text-xs font-medium ${isOnline ? "bg-green-100 text-green-700" : "bg-gray-100 text-gray-600"}`}>
              {isOnline ? "● Online" : "○ Offline"}
            </div>
          </div>
        </header>

        <div className={`flex-1 overflow-hidden relative ${isDarkMode ? "bg-gray-900" : "bg-white"}`}>
          <ChatUI messages={messages} onSend={handleSend} isTyping={isTyping} onUploadComplete={handleUploadComplete} isDarkMode={isDarkMode} />
        </div>
      </main>

      {/* Right Sidebar */}
      {results.length > 0 && (
        <aside className={`w-80 border-l hidden xl:flex flex-col ${isDarkMode ? "border-gray-700 bg-gray-800" : "border-gray-200 bg-white"}`}>
          <div className={`p-4 border-b font-semibold flex items-center justify-between ${isDarkMode ? "border-gray-700" : "border-gray-200"}`}>
            <span className={isDarkMode ? "text-gray-100" : "text-gray-900"}>Sources</span>
            <span className={`text-xs px-2 py-1 rounded-full font-medium ${isDarkMode ? "bg-gray-700 text-gray-300" : "bg-gray-100 text-gray-600"}`}>{results.length}</span>
          </div>
          <div className="flex-1 overflow-y-auto p-4">
            <ContextViewer results={results} onOpen={setModalItem} isDarkMode={isDarkMode} />
          </div>
        </aside>
      )}

      <SourceModal item={modalItem} onClose={() => setModalItem(null)} />
    </div>
  );
}

export default App;
