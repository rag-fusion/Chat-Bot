import { useState, useEffect, useRef } from "react";
import { Send, Mic } from "lucide-react";

export default function ChatWindow({ onQuery, messages, isTyping }) {
  const [input, setInput] = useState("");
  const scrollRef = useRef(null);
  const inputRef = useRef(null);

  const submit = async (e) => {
    e.preventDefault();
    const text = input.trim();
    if (!text) return;
    setInput("");
    await onQuery(text);
  };

  // Auto-scroll to bottom on new messages
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, isTyping]);

  // Auto-grow textarea
  useEffect(() => {
    if (inputRef.current) {
      inputRef.current.style.height = "auto";
      inputRef.current.style.height = Math.min(inputRef.current.scrollHeight, 150) + "px";
    }
  }, [input]);

  const Message = ({ role, content, sources = [], onOpenSource }) => {
    const isUser = role === "user";
    const isSystem = role === "system";
    
    if (isSystem) {
      return (
        <div className="flex justify-center my-3">
          <span className="text-xs text-gray-500 bg-gray-50 px-3 py-1.5 rounded-full border border-gray-200">
            {content}
          </span>
        </div>
      );
    }

    return (
      <div className={`flex gap-3 mb-4 ${isUser ? "justify-end" : "justify-start"}`}>
        {!isUser && (
          <div className="flex-shrink-0 h-8 w-8 rounded-full bg-green-500 flex items-center justify-center text-white shadow-sm">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M12 2L2 7L12 12L22 7L12 2Z" fill="currentColor" opacity="0.4"/>
              <path d="M2 17L12 22L22 17V12L12 17L2 12V17Z" fill="currentColor"/>
            </svg>
          </div>
        )}
        
        <div className="flex flex-col gap-1 max-w-[75%]">
          <div
            className={`rounded-2xl px-4 py-2.5 shadow-sm ${
              isUser
                ? "bg-purple-500 text-white"
                : "bg-gray-100 text-gray-900"
            }`}
          >
            <p className="text-sm leading-relaxed whitespace-pre-wrap">{content}</p>
          </div>
          
          {sources && sources.length > 0 && (
            <div className="flex flex-wrap gap-1 px-2">
              {sources.map((s, i) => (
                <button
                  key={i}
                  onClick={() => onOpenSource?.(s)}
                  className="text-xs text-gray-500 hover:text-gray-700 hover:underline"
                >
                  [{i + 1}] {s.file_name || s.file}
                </button>
              ))}
            </div>
          )}
        </div>

        {isUser && (
          <div className="flex-shrink-0 h-8 w-8 rounded-full bg-purple-500 flex items-center justify-center text-white font-semibold text-sm shadow-sm">
            U
          </div>
        )}
      </div>
    );
  };

  const Typing = () => (
    <div className="flex gap-3 mb-4">
      <div className="h-8 w-8 rounded-full bg-green-500 flex items-center justify-center text-white shadow-sm">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" className="animate-pulse">
          <path d="M12 2L2 7L12 12L22 7L12 2Z" fill="currentColor" opacity="0.4"/>
          <path d="M2 17L12 22L22 17V12L12 17L2 12V17Z" fill="currentColor"/>
        </svg>
      </div>
      <div className="flex items-center gap-1 bg-gray-100 rounded-2xl px-4 py-3">
        <span className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: "0ms" }}></span>
        <span className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: "150ms" }}></span>
        <span className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: "300ms" }}></span>
      </div>
    </div>
  );

  return (
    <div className="relative rounded-2xl border border-gray-200 bg-white shadow-lg overflow-hidden flex flex-col h-full max-h-[600px]">
      {/* Messages Area */}
      <div 
        ref={scrollRef}
        className="flex-1 overflow-y-auto p-4 space-y-2"
      >
        {messages.length === 0 && (
          <div className="flex flex-col items-center justify-center h-full text-center px-4">
            <div className="h-14 w-14 rounded-full bg-gradient-to-br from-purple-500 to-pink-500 shadow-md flex items-center justify-center mb-4">
              <svg width="28" height="28" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" className="text-white">
                <path d="M12 2L2 7L12 12L22 7L12 2Z" fill="currentColor" opacity="0.6"/>
                <path d="M2 17L12 22L22 17V12L12 17L2 12V17Z" fill="currentColor"/>
              </svg>
            </div>
            <h3 className="text-xl font-semibold mb-1 text-gray-900">Start a conversation</h3>
            <p className="text-gray-500 text-sm">Ask me anything!</p>
          </div>
        )}

        {messages.map((m, idx) => (
          <Message key={idx} {...m} />
        ))}
        
        {isTyping && <Typing />}
      </div>

      {/* Input Form */}
      <form
        onSubmit={submit}
        className="border-t border-gray-200 bg-gray-50 p-3"
      >
        <div className="flex items-end gap-2 bg-white border border-gray-300 rounded-xl px-3 py-2 focus-within:border-gray-400 transition-colors shadow-sm">
          <textarea
            ref={inputRef}
            className="flex-1 bg-transparent resize-none outline-none text-sm text-gray-900 placeholder-gray-400 max-h-[150px]"
            placeholder="Ask a question..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                submit(e);
              }
            }}
            rows={1}
          />
          <div className="flex items-center gap-1">
            <button
              type="button"
              onClick={() => alert("Voice input coming soon!")}
              className="p-1.5 rounded-lg text-gray-400 hover:bg-gray-100 transition-colors"
              title="Voice input"
            >
              <Mic className="w-4 h-4" />
            </button>
            <button
              type="submit"
              disabled={!input.trim() || isTyping}
              className="p-1.5 rounded-lg bg-green-500 text-white hover:bg-green-600 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
              title="Send message"
            >
              <Send className="w-4 h-4" />
            </button>
          </div>
        </div>
        <p className="text-xs text-gray-400 text-center mt-2">
          Press Enter to send, Shift+Enter for new line
        </p>
      </form>
    </div>
  );
}
