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
  <div className="relative flex h-full flex-col overflow-hidden rounded-2xl border bg-background/95 shadow-lg dark:bg-neutral-900/90 dark:border-neutral-800">
    {/* Messages area */}
    <div
      ref={scrollRef}
      className="relative flex-1 px-4 sm:px-6 py-4 space-y-4 h-[60vh] min-h-[400px] max-h-[700px] overflow-y-auto"
    >
      {messages.length === 0 && (
        <div className="flex h-full flex-col items-center justify-center text-center text-gray-500 dark:text-gray-400">
          <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-gray-900 text-sm font-semibold text-white dark:bg-neutral-700">
            AI
          </div>
          <p className="text-base font-medium">Chat with your documents</p>
          <p className="mt-1 text-xs sm:text-sm text-muted-foreground">
            Ask questions, summarize, or explore any file you&apos;ve uploaded.
          </p>
        </div>
      )}

      {messages.map((m, idx) => {
        const isUser = m.role === "user";

        return (
          <div
            key={idx}
            className={`flex w-full ${isUser ? "justify-end" : "justify-start"}`}
          >
            {/* Assistant avatar */}
            {!isUser && (
              <div className="mr-2 mt-1 flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-emerald-600 text-xs font-semibold text-white">
                AI
              </div>
            )}

            <div className="max-w-[80%] space-y-1">
              <div
                className={`inline-block rounded-2xl px-4 py-2 text-sm leading-relaxed ${
                  isUser
                    ? "bg-blue-600 text-white rounded-br-sm"
                    : "bg-gray-100 text-gray-900 dark:bg-neutral-800 dark:text-neutral-50 rounded-bl-sm"
                }`}
              >
                {m.content}
              </div>
            </div>

            {/* User avatar */}
            {isUser && (
              <div className="ml-2 mt-1 flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-gray-200 text-xs font-semibold text-gray-800 dark:bg-neutral-700 dark:text-neutral-200">
                You
              </div>
            )}
          </div>
        );
      })}

      {/* Typing indicator (assistant) */}
      {isTyping && (
        <div className="flex items-center justify-start gap-3">
          <div className="mr-2 mt-1 flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-emerald-600 text-xs font-semibold text-white">
            AI
          </div>
          <div className="rounded-2xl bg-gray-100 px-4 py-2 text-sm dark:bg-neutral-800">
            <Typing />
          </div>
        </div>
      )}
    </div>

    {/* Input area – bottom, ChatGPT style */}
    <div className="border-t bg-background/95 p-3 dark:bg-neutral-900/95 dark:border-neutral-800">
      <form onSubmit={submit} className="relative">
        <div className="flex items-end gap-2 rounded-xl border bg-white/90 px-3 py-2 dark:bg-neutral-900/80">
          <textarea
            className="max-h-32 min-h-[40px] w-full resize-none bg-transparent text-sm outline-none"
            placeholder="Message your assistant..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
          />
          <button
            type="submit"
            disabled={!input.trim() || isTyping}
            className="inline-flex h-9 w-9 items-center justify-center rounded-lg bg-gradient-to-r from-violet-500 to-fuchsia-500 text-[11px] font-medium text-white shadow-sm disabled:cursor-not-allowed disabled:opacity-50"
            aria-label="Send message"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="18"
              height="18"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <path d="M5 12h14" />
              <path d="m12 5 7 7-7 7" />
            </svg>
          </button>
        </div>
        <p className="mt-1 px-1 text-[11px] text-muted-foreground">
          AI can make mistakes. Consider checking important information.
        </p>
      </form>
    </div>
  </div>
);

}