import { useState, useRef, useEffect } from "react";
import { MoreHorizontal, Pencil, Trash2, Check, X } from "lucide-react";

export default function ChatHistoryItem({ chat, isActive, onClick, onRename, onDelete, isDarkMode }) {
  const [isRenaming, setIsRenaming] = useState(false);
  const [newTitle, setNewTitle] = useState(chat.title);
  const [showMenu, setShowMenu] = useState(false);
  const inputRef = useRef(null);
  const menuRef = useRef(null);

  useEffect(() => {
    if (isRenaming && inputRef.current) {
      inputRef.current.focus();
      inputRef.current.select();
    }
  }, [isRenaming]);

  // Close menu when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (menuRef.current && !menuRef.current.contains(event.target)) {
        setShowMenu(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const handleSaveRename = () => {
    if (newTitle.trim() && newTitle !== chat.title) {
      onRename(newTitle.trim());
    }
    setIsRenaming(false);
    setShowMenu(false);
  };

  const handleCancelRename = () => {
    setNewTitle(chat.title);
    setIsRenaming(false);
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter") {
      handleSaveRename();
    } else if (e.key === "Escape") {
      handleCancelRename();
    }
  };

  const handleDelete = () => {
    if (confirm(`Delete "${chat.title}"?`)) {
      onDelete();
    }
    setShowMenu(false);
  };

  return (
    <div
      className={`group relative flex items-center gap-2 px-3 py-2.5 rounded-lg cursor-pointer transition-colors ${
        isActive
          ? isDarkMode
            ? "bg-gray-700 text-white"
            : "bg-gray-200 text-gray-900"
          : isDarkMode
          ? "hover:bg-gray-750 text-gray-300 hover:text-white"
          : "hover:bg-gray-100 text-gray-700 hover:text-gray-900"
      }`}
    >
      {isRenaming ? (
        <div className="flex-1 flex items-center gap-2">
          <input
            ref={inputRef}
            type="text"
            value={newTitle}
            onChange={(e) => setNewTitle(e.target.value)}
            onKeyDown={handleKeyDown}
            onBlur={handleSaveRename}
            className={`flex-1 px-2 py-1 text-sm rounded outline-none ${
              isDarkMode
                ? "bg-gray-600 text-white border border-gray-500"
                : "bg-white text-gray-900 border border-gray-300"
            }`}
          />
          <button
            onClick={handleSaveRename}
            className="p-1 hover:bg-gray-600 rounded"
          >
            <Check className="w-4 h-4" />
          </button>
          <button
            onClick={handleCancelRename}
            className="p-1 hover:bg-gray-600 rounded"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      ) : (
        <>
          <div
            onClick={onClick}
            className="flex-1 truncate text-sm"
            title={chat.title}
          >
            {chat.title}
          </div>
          <div className="relative" ref={menuRef}>
            <button
              onClick={(e) => {
                e.stopPropagation();
                setShowMenu(!showMenu);
              }}
              className={`opacity-0 group-hover:opacity-100 p-1 rounded-md transition-opacity ${
                isDarkMode ? "hover:bg-gray-600" : "hover:bg-gray-200"
              }`}
            >
              <MoreHorizontal className="w-4 h-4" />
            </button>
            {showMenu && (
              <div
                className={`absolute right-0 top-8 min-w-[160px] rounded-lg shadow-lg border z-50 ${
                  isDarkMode
                    ? "bg-gray-800 border-gray-700"
                    : "bg-white border-gray-200"
                }`}
              >
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    setIsRenaming(true);
                    setShowMenu(false);
                  }}
                  className={`w-full text-left px-4 py-2 text-sm flex items-center gap-2 ${
                    isDarkMode
                      ? "hover:bg-gray-700 text-gray-200"
                      : "hover:bg-gray-50 text-gray-700"
                  }`}
                >
                  <Pencil className="w-4 h-4" />
                  Rename
                </button>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    handleDelete();
                  }}
                  className={`w-full text-left px-4 py-2 text-sm flex items-center gap-2 text-red-500 ${
                    isDarkMode ? "hover:bg-gray-700" : "hover:bg-gray-50"
                  }`}
                >
                  <Trash2 className="w-4 h-4" />
                  Delete
                </button>
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
}
