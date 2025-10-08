import { Mic, Send, Loader2 } from "lucide-react";
import { useEffect, useRef, useState } from "react";

function CitationNumber({ number, onClick }) {
  return (
    <button
      onClick={onClick}
      className="inline-flex h-4 w-4 items-center justify-center rounded-full bg-primary text-[10px] font-medium text-primary-foreground hover:bg-primary/90"
    >
      {number}
    </button>
  );
}

function ChatMessage({ role, content, sources = [], onOpenSource }) {
  const isUser = role === "user";
  const hasSourceCitations = sources && sources.length > 0;

  return (
    <div
      className={`group flex items-start gap-3 ${
        isUser ? "justify-end" : "justify-start"
      }`}
    >
      {!isUser && (
        <div className="h-8 w-8 overflow-hidden rounded-full bg-gradient-to-br from-violet-500 to-fuchsia-500 ring-2 ring-background">
          <div className="flex h-full w-full items-center justify-center text-white font-semibold">
            A
          </div>
        </div>
      )}
      <div className="flex flex-col gap-1">
        <div
          className={`max-w-[85%] rounded-2xl px-4 py-2.5 shadow-sm transition-colors ${
            isUser
              ? "bg-primary text-primary-foreground"
              : "bg-muted text-foreground"
          }`}
        >
          <p className="whitespace-pre-wrap text-sm leading-relaxed">
            {content}
            {hasSourceCitations && (
              <span className="ml-1 space-x-1">
                {sources.map((source, i) => (
                  <CitationNumber
                    key={i}
                    number={i + 1}
                    onClick={() => onOpenSource?.(source)}
                  />
                ))}
              </span>
            )}
          </p>
        </div>
        {hasSourceCitations && (
          <div
            className="invisible flex gap-2 px-4 text-xs text-muted-foreground group-hover:visible"
            aria-label="Click numbers above to view sources"
          >
            {sources.map((source, i) => (
              <button
                key={i}
                onClick={() => onOpenSource?.(source)}
                className="hover:text-foreground"
              >
                [{i + 1}] {source.title || source.file}
              </button>
            ))}
          </div>
        )}
      </div>
      {isUser && (
        <div className="h-8 w-8 overflow-hidden rounded-full bg-primary ring-2 ring-background">
          <div className="flex h-full w-full items-center justify-center text-primary-foreground font-semibold">
            U
          </div>
        </div>
      )}
    </div>
  );
}

export default function ChatUI({ messages, onSend, isTyping = false }) {
  const [input, setInput] = useState("");
  const [isRecording, setIsRecording] = useState(false);
  const scrollRef = useRef(null);
  const inputRef = useRef(null);

  // Submit handler for text input
  const submit = (e) => {
    e.preventDefault();
    if (!input.trim()) return;
    onSend(input.trim());
    setInput("");
  };

  // Handle voice input (placeholder)
  const toggleVoiceInput = () => {
    // TODO: Implement voice recording
    setIsRecording(!isRecording);
  };

  // Auto-scroll to bottom
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTo({
        top: scrollRef.current.scrollHeight,
        behavior: "smooth",
      });
    }
  }, [messages, isTyping]);

  // Auto-grow input field
  useEffect(() => {
    if (inputRef.current) {
      inputRef.current.style.height = "auto";
      inputRef.current.style.height = inputRef.current.scrollHeight + "px";
    }
  }, [input]);

  return (
    <div className="flex h-full flex-col overflow-hidden rounded-lg bg-card text-card-foreground">
      {/* Message List */}
      <div
        ref={scrollRef}
        className="flex-1 space-y-4 overflow-y-auto p-4 scroll-smooth"
      >
        {messages.map((msg, i) => (
          <ChatMessage key={i} {...msg} />
        ))}
        {isTyping && (
          <div className="flex items-center gap-2 text-muted-foreground">
            <Loader2 className="h-4 w-4 animate-spin" />
            <span className="text-sm">AI is thinking...</span>
          </div>
        )}
      </div>

      {/* Input Form */}
      <form onSubmit={submit} className="border-t p-4">
        <div className="flex gap-2">
          <div className="relative flex-1">
            <textarea
              ref={inputRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault();
                  submit(e);
                }
              }}
              placeholder="Type a message..."
              className="min-h-[44px] w-full resize-none rounded-md border bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
              style={{ maxHeight: "200px" }}
            />
          </div>
          <button
            type="button"
            onClick={toggleVoiceInput}
            className={`inline-flex h-11 w-11 items-center justify-center whitespace-nowrap rounded-md ring-offset-background transition-colors hover:bg-muted focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 ${
              isRecording ? "bg-red-500 text-white hover:bg-red-600" : ""
            }`}
          >
            <Mic className="h-5 w-5" />
          </button>
          <button
            type="submit"
            disabled={!input.trim()}
            className="inline-flex h-11 w-11 items-center justify-center whitespace-nowrap rounded-md bg-primary text-primary-foreground ring-offset-background transition-colors hover:bg-primary/90 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50"
          >
            <Send className="h-5 w-5" />
          </button>
        </div>
      </form>
    </div>
  );
}
