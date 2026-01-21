import { Send, Plus, X } from "lucide-react";
import { useEffect, useRef, useState } from "react";
import Uploader from "./Uploader";
import { API_BASE_URL } from "../config";

function CitationNumber({ number, onClick }) {
  return (
    <button
      onClick={onClick}
      className="inline-flex h-5 w-5 items-center justify-center rounded-full bg-gray-500 text-[10px] font-medium text-white hover:bg-gray-600 transition-colors"
    >
      {number}
    </button>
  );
}

function ChatMessage({ role, content, sources = [], onOpenSource }) {
  const isUser = role === "user";
  const isSystem = role === "system";
  const hasSourceCitations = sources && sources.length > 0;

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
        <div className="flex-shrink-0">
          {isUser ? (
            <div className="h-8 w-8 rounded-full bg-purple-500 flex items-center justify-center text-white font-semibold">
              U
            </div>
          ) : (
            <div className="h-8 w-8 rounded-full bg-green-500 flex items-center justify-center text-white shadow-sm">
              <svg
                width="20"
                height="20"
                viewBox="0 0 24 24"
                fill="none"
                xmlns="http://www.w3.org/2000/svg"
              >
                <path
                  d="M12 2L2 7L12 12L22 7L12 2Z"
                  fill="currentColor"
                  opacity="0.4"
                />
                <path
                  d="M2 17L12 22L22 17V12L12 17L2 12V17Z"
                  fill="currentColor"
                />
              </svg>
            </div>
          )}
        </div>

        <div className="flex flex-col gap-2 flex-1">
          <div>
            <p className="whitespace-pre-wrap text-gray-900 leading-7">
              {content}
              {hasSourceCitations && (
                <span className="ml-2 space-x-1">
                  {sources.map((source, i) => (
                    <CitationNumber
                      key={i}
                      number={i + 1}
                      onClick={() => {
                        // Prefer direct URL when available for instant open
                        if (source?.url) {
                          window.open(
                            source.url.startsWith("http")
                              ? source.url
                              : `${API_BASE_URL}${source.url}`,
// ...
                            "_blank"
                          );
                        } else {
                          onOpenSource?.(source);
                        }
                      }}
                    />
                  ))}
                </span>
              )}
            </p>
          </div>

          {hasSourceCitations && (
            <div className="flex flex-wrap gap-2 text-xs text-gray-500">
              {sources.map((source, i) => (
                <button
                  key={i}
                  onClick={() => onOpenSource?.(source)}
                  className="hover:text-gray-700 hover:underline"
                >
                  [{i + 1}] {source.file_name || source.title || source.file}
                </button>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default function ChatUI({
  messages,
  onSend,
  isTyping = false,
  onUploadComplete,
  isDarkMode = false,
}) {
  const [input, setInput] = useState("");
  const [showUploader, setShowUploader] = useState(false);
  const [isFocused, setIsFocused] = useState(false);
  const scrollRef = useRef(null);
  const inputRef = useRef(null);

  const MAX_CHARS = 4000;
  const charCount = input.length;
  const isNearLimit = charCount > MAX_CHARS * 0.8;
  const isOverLimit = charCount > MAX_CHARS;

  // Submit handler for text input
  const submit = (e) => {
    e.preventDefault();
    if (!input.trim() || isOverLimit) return;
    onSend(input.trim());
    setInput("");
    // Re-focus input after sending
    setTimeout(() => inputRef.current?.focus(), 100);
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
      inputRef.current.style.height =
        Math.min(inputRef.current.scrollHeight, 200) + "px";
    }
  }, [input]);

  // Dynamic placeholder based on context
  const getPlaceholder = () => {
    if (isTyping) return "Wait for response...";
    return "Ask anything";
  };

  const Typing = () => (
    <div
      className={`w-full border-b ${
        isDarkMode
          ? "bg-gray-800 border-gray-700"
          : "bg-gray-50 border-gray-100"
      }`}
    >
      <div className="flex gap-4 p-6 md:gap-6 md:max-w-3xl lg:max-w-[40rem] xl:max-w-[48rem] mx-auto">
        <div className="h-8 w-8 rounded-full bg-green-500 flex items-center justify-center text-white shadow-sm">
          <svg
            width="20"
            height="20"
            viewBox="0 0 24 24"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
            className="animate-pulse"
          >
            <path
              d="M12 2L2 7L12 12L22 7L12 2Z"
              fill="currentColor"
              opacity="0.4"
            />
            <path d="M2 17L12 22L22 17V12L12 17L2 12V17Z" fill="currentColor" />
          </svg>
        </div>
        <div className="flex items-center gap-1">
          <span
            className={`w-2 h-2 rounded-full animate-bounce ${
              isDarkMode ? "bg-gray-500" : "bg-gray-400"
            }`}
            style={{ animationDelay: "0ms" }}
          ></span>
          <span
            className={`w-2 h-2 rounded-full animate-bounce ${
              isDarkMode ? "bg-gray-500" : "bg-gray-400"
            }`}
            style={{ animationDelay: "150ms" }}
          ></span>
          <span
            className={`w-2 h-2 rounded-full animate-bounce ${
              isDarkMode ? "bg-gray-500" : "bg-gray-400"
            }`}
            style={{ animationDelay: "300ms" }}
          ></span>
        </div>
      </div>
    </div>
  );

  return (
    <div
      className={`flex h-full flex-col overflow-hidden ${
        isDarkMode ? "bg-gray-900" : "bg-white"
      }`}
    >
      {/* Message List */}
      <div ref={scrollRef} className="flex-1 overflow-y-auto w-full">
        {messages.length === 0 && (
          <div
            className={`flex flex-col items-center justify-center h-full text-center px-4 ${
              isDarkMode ? "bg-gray-900" : "bg-white"
            }`}
          >
             {/* Welcome message removed as requested */}
          </div>
        )}

        <div className="flex flex-col pb-32">
          {messages.map((msg, i) => (
            <ChatMessage key={i} {...msg} />
          ))}
          {isTyping && <Typing />}
        </div>
      </div>

      {/* Upload Modal */}
      {showUploader && (
        <div className="absolute inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div
            className={`rounded-2xl shadow-2xl w-full max-w-2xl max-h-[80vh] overflow-y-auto ${
              isDarkMode ? "bg-gray-800" : "bg-white"
            }`}
          >
            <div
              className={`sticky top-0 border-b p-4 flex items-center justify-between rounded-t-2xl ${
                isDarkMode
                  ? "bg-gray-800 border-gray-700"
                  : "bg-white border-gray-200"
              }`}
            >
              <h3
                className={`text-lg font-semibold ${
                  isDarkMode ? "text-gray-100" : "text-gray-900"
                }`}
              >
                Upload Documents
              </h3>
              <button
                onClick={() => setShowUploader(false)}
                className={`p-2 rounded-lg transition-colors ${
                  isDarkMode ? "hover:bg-gray-700" : "hover:bg-gray-100"
                }`}
              >
                <X
                  className={`w-5 h-5 ${
                    isDarkMode ? "text-gray-400" : "text-gray-500"
                  }`}
                />
              </button>
            </div>
            <div className="p-6">
              <Uploader
                onUploaded={(data) => {
                  if (onUploadComplete) onUploadComplete(data);
                  setShowUploader(false);
                }}
              />
            </div>
          </div>
        </div>
      )}

      {/* Input Form */}
      <div
        className={`absolute bottom-0 left-0 w-full bg-gradient-to-t pt-10 pb-6 px-4 ${
          isDarkMode
            ? "from-gray-900 via-gray-900 to-transparent"
            : "from-white via-white to-transparent"
        }`}
      >
        <div className="max-w-3xl lg:max-w-[40rem] xl:max-w-[48rem] mx-auto">
          <form
            onSubmit={submit}
            className={`relative flex items-center w-full rounded-full transition-all duration-300 py-3 px-4 ${
              isFocused
                ? "bg-[#2f2f2f] ring-1 ring-gray-600"
                : "bg-[#2f2f2f] hover:bg-[#3f3f3f]"
            }`}
          >
            <button
              type="button"
              onClick={() => setShowUploader(true)}
              className={`p-2 ml-1 rounded-lg transition-all duration-200 transform hover:scale-110 mr-2 ${
                isDarkMode
                  ? "text-gray-400 hover:bg-gray-700 hover:text-green-400"
                  : "text-gray-400 hover:bg-gray-100 hover:text-green-500"
              }`}
              title="Upload documents"
              disabled={isTyping}
            >
              <Plus className="w-5 h-5" />
            </button>
            <textarea
              ref={inputRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onFocus={() => setIsFocused(true)}
              onBlur={() => setIsFocused(false)}
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault();
                  submit(e);
                }
              }}
              placeholder={getPlaceholder()}
              disabled={isTyping}
              className={`w-full max-h-[200px] pr-24 bg-transparent border-none focus:ring-0 focus:outline-none outline-none resize-none text-base transition-all duration-200 text-gray-200 placeholder-gray-400 ${
                isTyping ? "text-gray-500 cursor-not-allowed" : ""
              } ${isOverLimit ? "text-red-500" : ""}`}
              rows={1}
            />
            <div className="absolute right-3 bottom-3 flex items-center gap-2">
              {/* Character Counter */}
              {charCount > 0 && (
                <div
                  className={`text-xs font-medium transition-all duration-200 ${
                    isOverLimit
                      ? "text-red-500 animate-pulse"
                      : isNearLimit
                      ? "text-orange-500"
                      : "text-gray-400"
                  }`}
                >
                  {charCount}/{MAX_CHARS}
                </div>
              )}


              <button
                type="submit"
                disabled={!input.trim() || isTyping || isOverLimit}
                className={`p-2 rounded-lg transition-all duration-200 transform ${
                  !input.trim() || isTyping || isOverLimit
                    ? "bg-gray-300 text-gray-500 cursor-not-allowed scale-95"
                    : "bg-green-500 text-white hover:bg-green-600 hover:scale-110 shadow-md hover:shadow-lg"
                }`}
              >
                <Send
                  className={`w-5 h-5 transition-transform duration-200 ${
                    input.trim() && !isTyping && !isOverLimit
                      ? "translate-x-0"
                      : ""
                  }`}
                />
              </button>
            </div>
          </form>
          <div className="text-center mt-3 flex items-center justify-center gap-2">
            <p className="text-xs text-gray-400">
              AI can make mistakes. Consider checking important information.
            </p>
            {/* Status indicator */}
            {isTyping && (
              <span className="inline-flex items-center gap-1 text-xs text-green-500 font-medium">
                <span className="w-1.5 h-1.5 bg-green-500 rounded-full animate-pulse"></span>
                Thinking...
              </span>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
