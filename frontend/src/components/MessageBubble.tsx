import ReactMarkdown from "react-markdown";
import { FileText } from "lucide-react";
import type { ChatMessage } from "../hooks/useStreamingChat";

interface Props {
  message: ChatMessage;
}

export default function MessageBubble({ message }: Props) {
  if (message.role === "user") {
    return (
      <div style={{ display: "flex", justifyContent: "flex-end", marginBottom: "20px" }}>
        <div style={{
          background: "#0ea5e9", color: "white", padding: "12px 16px",
          borderRadius: "16px 16px 4px 16px", fontSize: "14px",
          maxWidth: "600px", lineHeight: "1.5"
        }}>
          {message.content}
        </div>
      </div>
    );
  }

  return (
    <div style={{ display: "flex", justifyContent: "flex-start", marginBottom: "20px" }}>
      <div style={{
        background: "#1e293b", border: "1px solid #334155",
        borderRadius: "16px 16px 16px 4px", overflow: "hidden", maxWidth: "680px"
      }}>
        {message.sources && message.sources.length > 0 && (
          <div style={{ padding: "10px 16px 8px", borderBottom: "1px solid #334155" }}>
            <div style={{ fontSize: "11px", color: "#64748b", marginBottom: "6px", display: "flex", alignItems: "center", gap: "4px" }}>
              <FileText size={11} /> Sources
            </div>
            <div style={{ display: "flex", flexWrap: "wrap", gap: "6px" }}>
              {message.sources.map((s, j) => (
                <span key={j} style={{
                  fontSize: "11px", padding: "2px 8px", borderRadius: "4px",
                  background: "#0f172a", color: "#94a3b8", border: "1px solid #334155"
                }}>
                  📄 {s.source} · p.{s.page_num}
                </span>
              ))}
            </div>
          </div>
        )}
        <div style={{ padding: "12px 16px", fontSize: "14px", lineHeight: "1.6", color: "#e2e8f0" }}>
          {message.content ? (
            <ReactMarkdown>{message.content}</ReactMarkdown>
          ) : (
            <div style={{ color: "#64748b", fontSize: "13px" }}>Thinking...</div>
          )}
        </div>
      </div>
    </div>
  );
}
