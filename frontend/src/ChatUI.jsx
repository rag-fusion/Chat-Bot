import { useEffect, useRef, useState } from "react";

export default function ChatUI({ messages, onSend, isTyping = false }) {
  const [input, setInput] = useState("");
  const scrollRef = useRef(null);

  // Simplified submit handler for text-only input
  const submit = (e) => {
    e.preventDefault();
    if (!input.trim()) return;
    onSend(input.trim());
    setInput("");
  };

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, isTyping]);

  const Message = ({ role, content }) => {
    const isUser = role === "user";
    return (
      <div
        className={`flex items-start gap-3 ${
          isUser ? "justify-end" : "justify-start"
        }`}
      >
        {!isUser && (
          <div className="h-8 w-8 rounded-full bg-gradient-to-br from-violet-500 to-fuchsia-500 flex items-center justify-center text-white shrink-0 shadow-sm">
            A
          </div>
        )}
        <div
          className={
            isUser
              ? "max-w-[80%] sm:max-w-[75%] md:max-w-[70%] rounded-2xl px-4 py-2.5 bg-blue-600 text-white shadow-md animate-in fade-in slide-in-from-right-2 duration-200"
              : "max-w-[80%] sm:max-w-[75%] md:max-w-[70%] rounded-2xl px-4 py-2.5 bg-white/70 backdrop-blur ring-1 ring-gray-200 shadow-sm animate-in fade-in slide-in-from-left-2 duration-200 dark:bg-neutral-800/70 dark:ring-neutral-700"
          }
        >
          <p className="whitespace-pre-wrap leading-relaxed">{content}</p>
        </div>
        {isUser && (
          <div className="h-8 w-8 rounded-full bg-blue-600 text-white flex items-center justify-center shrink-0 shadow-sm">
            U
          </div>
        )}
      </div>
    );
  };

  const Typing = () => (
    <div className="flex items-center gap-2 text-gray-500">
      <span
        className="h-2 w-2 rounded-full bg-gray-400 animate-bounce"
        style={{ animationDelay: "0ms" }}
      />
      <span
        className="h-2 w-2 rounded-full bg-gray-400 animate-bounce"
        style={{ animationDelay: "150ms" }}
      />
      <span
        className="h-2 w-2 rounded-full bg-gray-400 animate-bounce"
        style={{ animationDelay: "300ms" }}
      />
    </div>
  );

  return (
    <div className="relative overflow-hidden rounded-2xl border bg-gradient-to-b from-gray-50 to-white shadow-lg dark:from-neutral-900/80 dark:to-neutral-900 dark:border-neutral-800">
      <div
        className="absolute inset-0 pointer-events-none opacity-60"
        style={{
          background:
            "radial-gradient(600px circle at 0% 0%, rgba(139,92,246,0.08), transparent 40%), radial-gradient(600px circle at 100% 0%, rgba(236,72,153,0.06), transparent 40%)",
        }}
      />
      
      {/* Set a fixed height and enable scrolling */}
      <div
        ref={scrollRef}
        className="relative p-4 sm:p-6 space-y-4 h-[60vh] min-h-[400px] max-h-[700px] overflow-y-auto"
      >
        {messages.length === 0 && (
          <div className="text-center text-gray-500 py-8 dark:text-gray-400 flex flex-col items-center justify-center h-full">
            <div className="mx-auto h-14 w-14 rounded-full bg-gradient-to-br from-violet-500 to-fuchsia-500 text-white flex items-center justify-center shadow-lg mb-4 animate-[float_6s_ease-in-out_infinite]">
              A
            </div>
            <p className="text-lg font-medium">Chat with your Documents</p>
            <p className="text-sm">
              Upload files using the box above to get started.
            </p>
          </div>
        )}

        {messages.map((m, idx) => (
          <Message key={idx} role={m.role} content={m.content} />
        ))}

        {isTyping && (
          <div className="flex items-center gap-3">
            <div className="h-8 w-8 rounded-full bg-gradient-to-br from-violet-500 to-fuchsia-500 flex items-center justify-center text-white shrink-0 shadow-sm">
              A
            </div>
            <div className="rounded-2xl px-4 py-2 bg-white/70 backdrop-blur ring-1 ring-gray-200 shadow-sm dark:bg-neutral-800/60 dark:ring-neutral-700">
              <Typing />
            </div>
          </div>
        )}
      </div>

      <div className="p-3 border-t bg-white/50 dark:bg-neutral-900/50 dark:border-neutral-800">
        <form onSubmit={submit} className="relative">
          <input
            className="w-full bg-gray-100 dark:bg-neutral-800 rounded-lg py-3 px-5 pr-16 outline-none focus:ring-2 focus:ring-violet-500"
            placeholder="Ask anything about your documents..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
          />
          <button
            type="submit"
            className="absolute right-2.5 top-1/2 -translate-y-1/2 p-2 rounded-full bg-gradient-to-r from-violet-500 to-fuchsia-500 text-white shadow transition-transform hover:scale-105 active:scale-95 disabled:opacity-50"
            disabled={!input.trim() || isTyping}
            aria-label="Send message"
          >
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M5 12h14"/><path d="m12 5 7 7-7 7"/></svg>
          </button>
        </form>
      </div>
    </div>
  );
}