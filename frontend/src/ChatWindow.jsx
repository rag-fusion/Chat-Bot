import { useState } from "react";

export default function ChatWindow({ onQuery, messages, isTyping }) {
  const [input, setInput] = useState("");

  const submit = async (e) => {
    e.preventDefault();
    const text = input.trim();
    if (!text) return;
    setInput("");
    await onQuery(text);
  };

 return (
  <div className="relative flex h-full flex-col rounded-2xl border bg-white/90 dark:bg-neutral-900/80 backdrop-blur shadow-sm">
    {/* Messages area */}
    <div className="flex-1 overflow-y-auto px-4 py-4 space-y-4">
      {messages.length === 0 && (
        <div className="mt-10 text-center text-sm text-muted-foreground">
          <p className="font-medium">Chat with your documents</p>
          <p className="text-xs">Ask anything about the files you&apos;ve uploaded…</p>
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
              <div className="mr-2 mt-1 flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-emerald-600 text-xs font-semibold text-white">
                AI
              </div>
            )}

            <div className="max-w-[80%] space-y-1">
              {/* Message bubble */}
              <div
                className={`inline-block rounded-2xl px-4 py-2 text-sm leading-relaxed ${
                  isUser
                    ? "bg-blue-600 text-white rounded-br-sm"
                    : "bg-gray-100 text-gray-900 dark:bg-neutral-800 dark:text-neutral-50 rounded-bl-sm"
                }`}
              >
                {m.content}
              </div>

              {/* Sources (sirf assistant ke niche) */}
              {!isUser && m.sources && m.sources.length > 0 && (
                <div className="flex flex-wrap gap-1 text-xs text-gray-600 dark:text-gray-400">
                  {m.sources.map((s, i) => (
                    <button
                      key={i}
                      onClick={() => m.onOpenSource?.(s)}
                      className="rounded-full border px-2 py-0.5 hover:bg-gray-100 dark:hover:bg-neutral-700"
                    >
                      [{i + 1}] {s.file_name}
                    </button>
                  ))}
                </div>
              )}
            </div>

            {/* User avatar */}
            {isUser && (
              <div className="ml-2 mt-1 flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-gray-200 text-xs font-semibold text-gray-800 dark:bg-neutral-700 dark:text-neutral-200">
                You
              </div>
            )}
          </div>
        );
      })}

      {/* Typing indicator */}
      {isTyping && (
        <div className="flex items-center justify-start gap-2 text-sm text-gray-500">
          <div className="mr-1 flex h-7 w-7 items-center justify-center rounded-full bg-emerald-600 text-xs font-semibold text-white">
            AI
          </div>
          <div className="flex items-center gap-1 rounded-2xl bg-gray-100 px-3 py-2 text-xs dark:bg-neutral-800">
            <span className="h-1.5 w-1.5 rounded-full bg-gray-500 animate-bounce" />
            <span className="h-1.5 w-1.5 rounded-full bg-gray-500 animate-bounce [animation-delay:0.15s]" />
            <span className="h-1.5 w-1.5 rounded-full bg-gray-500 animate-bounce [animation-delay:0.3s]" />
          </div>
        </div>
      )}
    </div>

    {/* Input area – bottom, ChatGPT style */}
    <form
      onSubmit={submit}
      className="border-t bg-gradient-to-t from-background via-background/80 to-background/40 px-3 py-3"
    >
      <div className="flex items-end gap-2 rounded-xl border bg-white/90 px-3 py-2 dark:bg-neutral-900/80">
        <textarea
          className="max-h-32 min-h-[40px] w-full resize-none bg-transparent text-sm outline-none"
          placeholder="Message your assistant..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
        />
        <button
          type="submit"
          disabled={!input.trim()}
          className="inline-flex h-9 w-9 items-center justify-center rounded-lg bg-gradient-to-r from-violet-500 to-fuchsia-500 text-[11px] font-medium text-white shadow-sm disabled:cursor-not-allowed disabled:opacity-50"
        >
          Send
        </button>
      </div>
      <p className="mt-1 px-1 text-[11px] text-muted-foreground">
        AI can make mistakes. Check important information.
      </p>
    </form>
  </div>
);

}
