import { useState, useRef, useEffect } from "react";
import { LogOut, Settings, Sun, Moon } from "lucide-react";
import { API_BASE_URL } from "../config";

export default function UserMenu({ user, onLogout, isDarkMode, onToggleTheme, onEditProfile }) {
  const [isOpen, setIsOpen] = useState(false);
  const menuRef = useRef(null);

  useEffect(() => {
    function handleClickOutside(event) {
      if (menuRef.current && !menuRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  return (
    <div className="relative" ref={menuRef}>
      <button 
        onClick={() => setIsOpen(!isOpen)}
        className={`w-full flex items-center justify-between px-3 py-2 rounded-lg transition-colors cursor-pointer ${
          isOpen 
            ? (isDarkMode ? "bg-gray-800" : "bg-gray-100") 
            : (isDarkMode ? "hover:bg-gray-800" : "hover:bg-gray-100")
        }`}
        title="User Menu"
      >
        <div className="flex items-center gap-3 overflow-hidden text-left">
          <div className="w-8 h-8 rounded-full bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center text-white font-bold shrink-0 overflow-hidden">
             {user?.avatar_url ? (
               <img src={`${API_BASE_URL}${user.avatar_url}`} alt="Avatar" className="w-full h-full object-cover" />
             ) : (
                user?.full_name?.[0] || user?.email?.[0] || "U"
             )}
          </div>
          <div className="flex flex-col overflow-hidden">
             <span className={`text-sm font-medium truncate ${isDarkMode ? "text-gray-200" : "text-gray-900"}`}>
                {user?.full_name || "User"}
             </span>
             {user?.email && (
                 <span className={`text-xs truncate ${isDarkMode ? "text-gray-400" : "text-gray-500"}`}>
                    {user.email}
                 </span>
             )}
          </div>
        </div>
      </button>

      {isOpen && (
        <div className={`absolute bottom-full left-0 w-full mb-2 min-w-[200px] rounded-lg shadow-lg border overflow-hidden z-50 ${
          isDarkMode ? "bg-gray-800 border-gray-700 text-gray-200" : "bg-white border-gray-200 text-gray-700"
        }`}>
           <div className={`px-4 py-2 border-b text-xs uppercase font-semibold tracking-wider ${isDarkMode ? "border-gray-700 text-gray-500" : "border-gray-200 text-gray-400"}`}>
              Account
           </div>
           
           <div 
              onClick={() => { setIsOpen(false); onEditProfile(); }}
              className={`px-4 py-2 text-sm border-b cursor-pointer transition-colors ${isDarkMode ? "border-gray-700 hover:bg-gray-700" : "border-gray-200 hover:bg-gray-50"}`}
           >
              <p className="font-medium truncate">{user?.full_name || "User"}</p>
              <p className="text-xs opacity-70 truncate">{user?.email}</p>
           </div>


           <button onClick={() => setIsOpen(false)} className={`w-full text-left px-4 py-2 text-sm flex items-center gap-2 ${isDarkMode ? "hover:bg-gray-700" : "hover:bg-gray-50"}`}>
              <Settings className="w-4 h-4" /> Settings
           </button>
           <button onClick={() => { setIsOpen(false); onToggleTheme(); }} className={`w-full text-left px-4 py-2 text-sm flex items-center gap-2 ${isDarkMode ? "hover:bg-gray-700" : "hover:bg-gray-50"}`}>
              {isDarkMode ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />} 
              {isDarkMode ? "Light Mode" : "Dark Mode"}
           </button>
           <button onClick={() => { setIsOpen(false); onLogout(); }} className={`w-full text-left px-4 py-2 text-sm flex items-center gap-2 text-red-500 ${isDarkMode ? "hover:bg-gray-700" : "hover:bg-gray-50"}`}>
              <LogOut className="w-4 h-4" /> Logout
           </button>
        </div>
      )}
    </div>
  );
}
