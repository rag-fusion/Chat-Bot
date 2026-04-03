import { useState } from "react";
import { v4 as uuidv4 } from "uuid";

/**
 * Creates or retrieves a chat_id for this browser session.
 * chat_id is stored in sessionStorage so it resets on new tab.
 */
export function useChatId() {
  const [chatId] = useState(() => {
    const existing = sessionStorage.getItem("rag_chat_id");
    if (existing) return existing;
    const newId = uuidv4();
    sessionStorage.setItem("rag_chat_id", newId);
    return newId;
  });
  return chatId;
}
