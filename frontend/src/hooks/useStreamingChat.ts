import { useState, useCallback } from "react";
import type { ChatMessage, Source } from "../api/client";

const BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export function useStreamingChat() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isStreaming, setIsStreaming] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const sendMessage = useCallback(async (query: string) => {
    setError(null);

    const userMsg: ChatMessage = {
      role: "user",
      content: query,
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, userMsg]);

    const assistantMsg: ChatMessage = {
      role: "assistant",
      content: "",
      sources: [],
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, assistantMsg]);
    setIsStreaming(true);

    try {
      const response = await fetch(`${BASE_URL}/api/v1/chat/stream`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          query,
          conversation_history: messages.slice(-6).map((m) => ({
            role: m.role,
            content: m.content,
          })),
          stream: true,
        }),
      });


      const reader = response.body?.getReader();
      const decoder = new TextDecoder();

      while (reader) {
        const { done, value } = await reader.read();
        if (done) break;
        const text = decoder.decode(value);
        const lines = text.split("\n");
        for (const line of lines) {
          if (line.startsWith("data: ")) {
            try {
              const data = JSON.parse(line.slice(6));
              if (data.type === "sources") {
                setMessages((prev) => {
                  const updated = [...prev];
                  updated[updated.length - 1] = { ...updated[updated.length - 1], sources: data.sources };
                  return updated;
                });
              } else if (data.type === "token") {
                setMessages((prev) => {
                  const updated = [...prev];
                  updated[updated.length - 1] = { ...updated[updated.length - 1], content: updated[updated.length - 1].content + data.content };
                  return updated;
                });
              }
            } catch (_e) {}
          }
        }
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown error");
      setMessages((prev) => {
        const updated = [...prev];
        updated[updated.length - 1] = { ...updated[updated.length - 1], content: "Sorry, something went wrong." };
        return updated;
      });
    } finally {
      setIsStreaming(false);
    }
  }, [messages]);

  return { messages, isStreaming, error, sendMessage };
}
