import { useEffect, useRef, useState } from "react";
import { Mic } from "lucide-react";

export default function ChatUI({ messages, onSend, isTyping = false }) {
  const [input, setInput] = useState("");
  const scrollRef = useRef(null);

  // Submit handler
  const submit = (e) => {
    e.preventDefault();
    if (!input.trim()) return;
    onSend(input.trim());
    setInput("");
  };

  // Auto-scroll to bottom on new messages
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, isTyping]);

  const Message = ({ role, content }) => {
    const isUser = role === "user";
    const isSystem = role === "system";
    
    if (isSystem) {
        return (
            <div className="flex justify-center my-4 px-4">
                <span className="text-xs text-gray-500 bg-gray-50 px-4 py-2 rounded-full border border-gray-200">
                    {content}
                </span>
            </div>
        );
    }

    return (
      <div
        className={`w-full ${
          isUser ? "bg-white" : "bg-gray-50"
        } border-b border-gray-100`}
      >
        <div className="flex gap-4 p-6 text-base md:gap-6 md:max-w-3xl lg:max-w-[40rem] xl:max-w-[48rem] mx-auto">
          <div className="flex-shrink-0 flex flex-col relative items-end">
            {isUser ? (
              <div className="h-8 w-8 rounded-full bg-purple-500 flex items-center justify-center text-white font-semibold">
                U
              </div>
            ) : (
              <div className="h-8 w-8 rounded-full bg-green-500 flex items-center justify-center text-white shadow-sm">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M12 2L2 7L12 12L22 7L12 2Z" fill="currentColor" opacity="0.4"/>
                  <path d="M2 17L12 22L22 17V12L12 17L2 12V17Z" fill="currentColor"/>
                </svg>
              </div>
            )}
          </div>
          
          <div className="relative flex-1 overflow-hidden">
              <div className="prose prose-gray max-w-none break-words">
                  <p className="whitespace-pre-wrap text-gray-900 leading-7">{content}</p>
              </div>
          </div>
        </div>
      </div>
    );
  };

  const Typing = () => (
    <div className="w-full bg-gray-50 border-b border-gray-100">
      <div className="flex gap-4 p-6 md:gap-6 md:max-w-3xl lg:max-w-[40rem] xl:max-w-[48rem] mx-auto">
          <div className="h-8 w-8 rounded-full bg-green-500 flex items-center justify-center text-white shadow-sm">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" className="animate-pulse">
                <path d="M12 2L2 7L12 12L22 7L12 2Z" fill="currentColor" opacity="0.4"/>
                <path d="M2 17L12 22L22 17V12L12 17L2 12V17Z" fill="currentColor"/>
              </svg>
          </div>
          <div className="flex items-center gap-1">
              <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: "0ms" }}></span>
              <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: "150ms" }}></span>
              <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: "300ms" }}></span>
          </div>
      </div>
    </div>
  );

  return (
    <div className="flex flex-col h-full relative">
      {/* Messages Area */}
      <div
        ref={scrollRef}
        className="flex-1 overflow-y-auto w-full"
      >
        {messages.length === 0 && (
          <div className="flex flex-col items-center justify-center h-full text-center px-4">
            <div className="h-16 w-16 rounded-full bg-gradient-to-br from-purple-500 to-pink-500 shadow-lg flex items-center justify-center mb-6">
                 <svg width="32" height="32" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" className="text-white">
                    <path d="M12 2L2 7L12 12L22 7L12 2Z" fill="currentColor" opacity="0.6"/>
                    <path d="M2 17L12 22L22 17V12L12 17L2 12V17Z" fill="currentColor"/>
                 </svg>
            </div>
            <h2 className="text-3xl font-semibold mb-2 text-gray-900">How can I help you today?</h2>
            <p className="text-gray-500 text-sm">Ask me anything about your documents</p>
          </div>
          <p className="text-base font-medium">Chat with your documents</p>
          <p className="mt-1 text-xs sm:text-sm text-muted-foreground">
            Ask questions, summarize, or explore any file you&apos;ve uploaded.
          </p>
        </div>
      )}

        <div className="flex flex-col pb-32">
            {messages.map((m, idx) => (
            <Message key={idx} role={m.role} content={m.content} />
            ))}
            {isTyping && <Typing />}
        </div>
      </div>

      {/* Input Area */}
      <div className="absolute bottom-0 left-0 w-full bg-gradient-to-t from-white via-white to-transparent pt-10 pb-6 px-4">
        <div className="max-w-3xl lg:max-w-[40rem] xl:max-w-[48rem] mx-auto">
            <form onSubmit={submit} className="relative flex items-center w-full px-4 py-3 bg-white border border-gray-300 rounded-2xl shadow-lg hover:shadow-xl transition-shadow focus-within:border-gray-400">
                <input
                    className="w-full max-h-[200px] pr-24 bg-transparent border-none focus:ring-0 resize-none outline-none text-base text-gray-900 placeholder-gray-400"
                    placeholder="Send a message..."
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                />
                <div className="absolute right-3 flex items-center gap-2">
                  <button
                      type="button"
                      className="p-2 rounded-lg text-gray-400 hover:bg-gray-100 transition-colors"
                      title="Voice input (placeholder)"
                  >
                      <Mic className="w-5 h-5" />
                  </button>
                  <button
                      type="submit"
                      disabled={!input.trim() || isTyping}
                      className="p-2 rounded-lg bg-green-500 text-white disabled:bg-gray-300 disabled:cursor-not-allowed hover:bg-green-600 transition-colors"
                  >
                      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                          <path d="M2.01 21L23 12L2.01 3L2 10L17 12L2 14L2.01 21Z" fill="currentColor"/>
                      </svg>
                  </button>
                </div>
            </form>
            <div className="text-center mt-3">
                <p className="text-xs text-gray-400">
                    AI can make mistakes. Consider checking important information.
                </p>
            </div>
        </div>
      </div>
    </div>
  </div>
);

}