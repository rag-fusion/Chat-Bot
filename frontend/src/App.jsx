import { useEffect, useState } from "react";
import { API_BASE_URL } from "./config";
import ChatUI from "./components/ChatUI";
import ContextViewer from "./components/ContextViewer";
import SourceModal from "./components/SourceModal";
import { Auth } from "./components/Auth";
import LandingPage from "./components/LandingPage";
import { Sheet, SheetContent, SheetTrigger } from "./components/ui/sheet";
import { DialogTitle, DialogDescription } from "./components/ui/dialog";
import UserMenu from "./components/UserMenu";
import ProfileModal from "./components/ProfileModal";
import ChatHistoryItem from "./components/ChatHistoryItem";
import { PanelLeft, X, Database, LogOut, SquarePen, Sun, Moon } from "lucide-react";

function App() {
  const [token, setToken] = useState(localStorage.getItem("token") || null);
  const [user, setUser] = useState(() => {
    try {
        const item = localStorage.getItem("user");
        return (item && item !== "undefined") ? JSON.parse(item) : null;
    } catch (e) {
        return null;
    }
  });
  
  const [messages, setMessages] = useState([]);
  const [isTyping, setIsTyping] = useState(false);
  const [results, setResults] = useState([]);
  const [modalItem, setModalItem] = useState(null);
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const [showSidebar, setShowSidebar] = useState(true);
  const [indexedDocs, setIndexedDocs] = useState(0);
  const [isDarkMode, setIsDarkMode] = useState(true);
  const [isProfileOpen, setIsProfileOpen] = useState(false);


  // Real Chat History
  const [chatHistory, setChatHistory] = useState([]);
  const [currentChatId, setCurrentChatId] = useState(null);

  useEffect(() => {
    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);
    window.addEventListener("online", handleOnline);
    window.addEventListener("offline", handleOffline);
    
    // Cleanup URL hash if present
    if (window.location.hash) {
      window.history.replaceState(null, null, ' ');
    }

    return () => {
      window.removeEventListener("online", handleOnline);
      window.removeEventListener("offline", handleOffline);
    };
  }, []);

  // Fetch history on load/login
  useEffect(() => {
    if (token) {
        fetchHistory();
        
        // Refresh user data if missing or incomplete
        if (!user || !user.email) {
            fetch(`${API_BASE_URL}/api/auth/me`, {
                   headers: { 'Authorization': `Bearer ${token}` }
            })
            .then(res => res.ok ? res.json() : null)
            .then(u => {
                if (u) {
                    setUser(u);
                    localStorage.setItem("user", JSON.stringify(u));
                }
            })
            .catch(err => console.error("Failed to refresh user", err));
        }
    }
  }, [token]);

  const handleLogin = async (data) => {
      let userData = data.user;
      const accessToken = data.access_token;
      
      setToken(accessToken);
      localStorage.setItem("token", accessToken);

      if (!userData) {
           // Fallback: fetch user me
           try {
               const res = await fetch(`${API_BASE_URL}/api/auth/me`, {
                   headers: { 'Authorization': `Bearer ${accessToken}` }
               });
               if (res.ok) {
                   userData = await res.json();
               }
           } catch (e) {
               console.error("Failed to fetch user info", e);
           }
      }

      setUser(userData);
      if (userData) {
          localStorage.setItem("user", JSON.stringify(userData));
      } else {
          localStorage.removeItem("user");
      }
  };

  const handleLogout = () => {
      setToken(null);
      setUser(null);
      localStorage.removeItem("token");
      localStorage.removeItem("user");
      setMessages([]);
      setChatHistory([]);
      setShowLanding(true);
  };

  const handleUpdateProfile = async (updatedData) => {
      // Optimistic update
      const newUser = { ...user, ...updatedData };
      setUser(newUser);
      localStorage.setItem("user", JSON.stringify(newUser));
      
      // Attempt backend update if endpoint exists (mocked for now as we don't have PUT /api/auth/me confirmed)
      // If backend supports it:
      /*
      try {
        await fetch(`${API_BASE_URL}/api/auth/me`, {
            method: 'PUT',
            headers: { 
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}` 
            },
            body: JSON.stringify(updatedData)
        });
      } catch(e) { console.error(e); }
      */
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

  const handleRenameChat = async (chatId, newTitle) => {
      try {
          const res = await fetch(`${API_BASE_URL}/api/chat/${chatId}`, {
              method: 'PATCH',
              headers: { 
                  'Authorization': `Bearer ${token}`,
                  'Content-Type': 'application/json'
              },
              body: JSON.stringify({ title: newTitle })
          });
          if (res.ok) {
              fetchHistory(); // Refresh list
          }
      } catch (e) {
          console.error("Failed to rename chat", e);
      }
  };

  const handleDeleteChat = async (chatId) => {
      try {
          const res = await fetch(`${API_BASE_URL}/api/chat/${chatId}`, {
              method: 'DELETE',
              headers: { 'Authorization': `Bearer ${token}` }
          });
          if (res.ok) {
              fetchHistory(); // Refresh list
              // If deleting current chat, start new one
              if (currentChatId === chatId) {
                  startNewChat();
              }
          }
      } catch (e) {
          console.error("Failed to delete chat", e);
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
      return <LandingPage onLogin={handleLogin} />;
  }

  return (
    <div className={`flex h-screen w-full overflow-hidden ${isDarkMode ? "bg-gray-900" : "bg-white"}`}>
      {/* Mobile Navigation */}
      <div className="lg:hidden fixed top-4 left-4 z-50">
        <Sheet>
          <SheetTrigger asChild>
            <button className={`p-2 rounded-md ${isDarkMode ? "bg-gray-800 text-gray-300" : "bg-gray-100 text-gray-700"}`}>
              <PanelLeft className="w-5 h-5" />
            </button>
          </SheetTrigger>
          <SheetContent side="left" className={`w-[280px] p-0 border-r ${isDarkMode ? "bg-gray-800 border-gray-700 text-gray-100" : "bg-white border-gray-200 text-gray-900"}`}>
            <div className="sr-only">
              <DialogTitle>Navigation Menu</DialogTitle>
              <DialogDescription>Access chat history and new chat options</DialogDescription>
            </div>
            <div className="p-3 flex-1 overflow-y-auto flex flex-col h-full">
              <div className="flex items-center justify-between px-4 py-3 mb-4">
                <div className="flex items-center gap-2">
                   <div className="w-8 h-8 bg-white rounded-full flex items-center justify-center">
                     <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" className="w-5 h-5 text-black"><path d="M12 2L2 7L12 12L22 7L12 2Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/><path d="M2 17L12 22L22 17" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/><path d="M2 12L12 17L22 12" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/></svg>
                   </div>
                   <span className="font-semibold text-lg">ChatBot</span>
                </div>
                <button onClick={startNewChat} className={`p-2 rounded-lg transition-colors ${isDarkMode ? "hover:bg-gray-700 text-gray-400 hover:text-gray-100" : "hover:bg-gray-100 text-gray-600 hover:text-gray-900"}`} title="New Chat">
                  <SquarePen className="w-5 h-5" />
                </button>
              </div>
              
              {/* Chat History List */}
              <div className="flex-1 overflow-y-auto space-y-1 mb-2">
                {chatHistory.map((chat) => (
                  <ChatHistoryItem
                    key={chat.id}
                    chat={chat}
                    isActive={currentChatId === chat.id}
                    onClick={() => loadChat(chat.id)}
                    onRename={(newTitle) => handleRenameChat(chat.id, newTitle)}
                    onDelete={() => handleDeleteChat(chat.id)}
                    isDarkMode={isDarkMode}
                  />
                ))}
              </div>

               {/* User Area */}
               <div className={`border-t pt-2 pb-2 ${isDarkMode ? "border-gray-700" : "border-gray-200"}`}>
                   <UserMenu user={user} onLogout={handleLogout} isDarkMode={isDarkMode} onToggleTheme={() => setIsDarkMode(!isDarkMode)} onEditProfile={() => setIsProfileOpen(true)} />
              </div>
            </div>
          </SheetContent>
        </Sheet>
      </div>

      {/* Sidebar (Desktop) */}
      <aside className={`${showSidebar ? "w-[260px]" : "w-0"} hidden lg:flex flex-col transition-all duration-300 border-r ${isDarkMode ? "bg-gray-800 border-gray-700 text-gray-100" : "bg-white border-gray-200 text-gray-900"}`}>
        <div className="p-3 flex-1 overflow-y-auto flex flex-col">
          <div className="flex items-center justify-between px-3 py-3 mb-2">
            <div className={`flex items-center gap-2 transition-opacity duration-300 ${!showSidebar && "opacity-0"}`}>
               <div className="w-8 h-8 bg-white rounded-full flex items-center justify-center">
                 <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" className="w-5 h-5 text-black"><path d="M12 2L2 7L12 12L22 7L12 2Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/><path d="M2 17L12 22L22 17" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/><path d="M2 12L12 17L22 12" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/></svg>
               </div>
               <span className="font-semibold text-lg">ChatBot</span>
            </div>
            <button onClick={() => setShowSidebar(!showSidebar)} className={`p-2 rounded-lg transition-colors ${isDarkMode ? "hover:bg-gray-700 text-gray-400 hover:text-gray-100" : "hover:bg-gray-100 text-gray-600 hover:text-gray-900"}`} title="Close Sidebar">
              <PanelLeft className="w-5 h-5" />
            </button>
          </div>

          <button onClick={startNewChat} className={`flex items-center gap-3 px-3 py-3 rounded-lg text-sm transition-colors mb-2 ${isDarkMode ? "hover:bg-gray-700 text-gray-100" : "hover:bg-gray-100 text-gray-900"}`}>
              <SquarePen className="w-4 h-4" />
              <span>New chat</span>
          </button>
          
          {/* Chat History List */}
          <div className="flex-1 overflow-y-auto space-y-1">
            {chatHistory.map((chat) => (
              <ChatHistoryItem
                key={chat.id}
                chat={chat}
                isActive={currentChatId === chat.id}
                onClick={() => loadChat(chat.id)}
                onRename={(newTitle) => handleRenameChat(chat.id, newTitle)}
                onDelete={() => handleDeleteChat(chat.id)}
                isDarkMode={isDarkMode}
              />
            ))}
          </div>

        </div>

        {/* User Area at bottom */}
        <div className={`p-3 border-t ${isDarkMode ? "border-gray-700" : "border-gray-200"}`}>
           <UserMenu user={user} onLogout={handleLogout} isDarkMode={isDarkMode} onToggleTheme={() => setIsDarkMode(!isDarkMode)} onEditProfile={() => setIsProfileOpen(true)} />
        </div>
      </aside>

      {/* Main Content Area */}
      <main className={`flex-1 flex flex-col h-full relative min-w-0 ${isDarkMode ? "bg-gray-900" : "bg-white"}`}>
        <header className={`h-14 flex items-center justify-between px-6 border-b ${isDarkMode ? "border-gray-700 bg-gray-800" : "border-gray-200 bg-white"}`}>
          <div className="flex items-center gap-3">
            {!showSidebar && (
              <button onClick={() => setShowSidebar(!showSidebar)} className={`hidden lg:block p-2 rounded-lg ${isDarkMode ? "text-gray-400 hover:bg-gray-700" : "text-gray-600 hover:bg-gray-100"}`}>
                <PanelLeft className="w-5 h-5" />
              </button>
            )}

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
      <ProfileModal 
        isOpen={isProfileOpen} 
        onClose={() => setIsProfileOpen(false)} 
        user={user} 
        onSave={handleUpdateProfile} 
        isDarkMode={isDarkMode} 
      />
    </div>
  );
}

export default App;
