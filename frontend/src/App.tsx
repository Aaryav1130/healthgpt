import { useState, useRef, useEffect } from "react";
import { useStreamingChat } from "./hooks/useStreamingChat";
import { uploadPDF, getIndexStatus } from "./api/client";
import ReactMarkdown from "react-markdown";
import { Send, Upload, FileText, Brain, AlertCircle, CheckCircle } from "lucide-react";

export default function App() {
  const { messages, isStreaming, error, sendMessage } = useStreamingChat();
  const [input, setInput] = useState("");
  const [isUploading, setIsUploading] = useState(false);
  const [indexStatus, setIndexStatus] = useState<any>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  useEffect(() => {
    getIndexStatus().then(setIndexStatus).catch(() => {});
  }, []);

  const handleSend = () => {
    if (!input.trim() || isStreaming) return;
    sendMessage(input.trim());
    setInput("");
  };

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setIsUploading(true);
    try {
      const result = await uploadPDF(file);
      const status = await getIndexStatus();
      setIndexStatus(status);
      alert(`✅ Ingested "${result.filename}" — ${result.chunks_created} chunks created`);
    } catch (err) {
      alert("❌ Upload failed.");
    } finally {
      setIsUploading(false);
      e.target.value = "";
    }
  };

  return (
    <div style={{ minHeight: "100vh", background: "#0f172a", color: "#f1f5f9", display: "flex", flexDirection: "column", fontFamily: "system-ui, sans-serif" }}>
      {/* Header */}
      <header style={{ borderBottom: "1px solid #1e293b", padding: "16px 24px", display: "flex", alignItems: "center", justifyContent: "space-between", background: "#0f172a", position: "sticky", top: 0, zIndex: 10 }}>
        <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
          <div style={{ width: "36px", height: "36px", borderRadius: "10px", background: "#0ea5e9", display: "flex", alignItems: "center", justifyContent: "center" }}>
            <Brain size={20} color="white" />
          </div>
          <div>
            <div style={{ fontWeight: 600, fontSize: "16px" }}>HealthGPT</div>
            <div style={{ fontSize: "11px", color: "#94a3b8" }}>Medical RAG Assistant · Llama 3.2 + FAISS</div>
          </div>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
          {indexStatus && (
            <div style={{ display: "flex", alignItems: "center", gap: "6px", fontSize: "12px", color: "#94a3b8" }}>
              {indexStatus.index_loaded
                ? <CheckCircle size={14} color="#10b981" />
                : <AlertCircle size={14} color="#f59e0b" />}
              {indexStatus.total_chunks} chunks indexed
            </div>
          )}
          <button
            onClick={() => fileInputRef.current?.click()}
            disabled={isUploading}
            style={{ display: "flex", alignItems: "center", gap: "8px", padding: "8px 16px", borderRadius: "8px", background: "#0ea5e9", color: "white", border: "none", cursor: "pointer", fontSize: "13px", fontWeight: 500 }}
          >
            <Upload size={14} />
            {isUploading ? "Uploading..." : "Upload PDF"}
          </button>
          <input ref={fileInputRef} type="file" accept=".pdf" onChange={handleUpload} style={{ display: "none" }} />
        </div>
      </header>

      {/* Messages */}
      <main style={{ flex: 1, overflowY: "auto", padding: "24px 16px", maxWidth: "800px", margin: "0 auto", width: "100%" }}>
        {messages.length === 0 && (
          <div style={{ display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", minHeight: "400px", gap: "16px", textAlign: "center" }}>
            <div style={{ width: "64px", height: "64px", borderRadius: "16px", background: "rgba(14,165,233,0.1)", border: "1px solid rgba(14,165,233,0.2)", display: "flex", alignItems: "center", justifyContent: "center" }}>
              <Brain size={32} color="#0ea5e9" />
            </div>
            <h2 style={{ fontSize: "20px", fontWeight: 600, color: "#e2e8f0" }}>Ask a Medical Question</h2>
            <p style={{ color: "#64748b", fontSize: "14px", maxWidth: "360px" }}>Upload medical PDFs first, then ask questions. HealthGPT uses hybrid search + reranking to find relevant context.</p>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "8px", marginTop: "8px" }}>
              {["What are symptoms of hypertension?", "Explain diabetes management.", "What causes pneumonia?", "Describe treatment for anemia."].map((q) => (
                <button key={q} onClick={() => sendMessage(q)}
                  style={{ fontSize: "12px", padding: "10px 14px", borderRadius: "8px", border: "1px solid #1e293b", background: "transparent", color: "#94a3b8", cursor: "pointer", textAlign: "left" }}>
                  {q}
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((msg, i) => (
          <div key={i} style={{ marginBottom: "24px", display: "flex", justifyContent: msg.role === "user" ? "flex-end" : "flex-start" }}>
            <div style={{ maxWidth: "680px" }}>
              {msg.role === "user" ? (
                <div style={{ background: "#0ea5e9", color: "white", padding: "12px 16px", borderRadius: "16px 16px 4px 16px", fontSize: "14px" }}>
                  {msg.content}
                </div>
              ) : (
                <div style={{ background: "#1e293b", border: "1px solid #334155", borderRadius: "16px 16px 16px 4px", overflow: "hidden" }}>
                  {msg.sources && msg.sources.length > 0 && (
                    <div style={{ padding: "12px 16px 8px", borderBottom: "1px solid #334155" }}>
                      <div style={{ fontSize: "11px", color: "#64748b", marginBottom: "6px", display: "flex", alignItems: "center", gap: "4px" }}>
                        <FileText size={11} /> Sources
                      </div>
                      <div style={{ display: "flex", flexWrap: "wrap", gap: "6px" }}>
                        {msg.sources.map((s, j) => (
                          <span key={j} style={{ fontSize: "11px", padding: "2px 8px", borderRadius: "4px", background: "#0f172a", color: "#94a3b8", border: "1px solid #334155" }}>
                            📄 {s.source} · p.{s.page_num}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                  <div style={{ padding: "12px 16px", fontSize: "14px", lineHeight: "1.6", color: "#e2e8f0" }}>
                    {msg.content ? (
                      <ReactMarkdown>{msg.content}</ReactMarkdown>
                    ) : (
                      <div style={{ display: "flex", alignItems: "center", gap: "8px", color: "#64748b" }}>
                        <span style={{ fontSize: "12px" }}>Thinking...</span>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </main>

      {/* Input */}
      <div style={{ borderTop: "1px solid #1e293b", background: "#0f172a", padding: "16px" }}>
        <div style={{ maxWidth: "800px", margin: "0 auto", display: "flex", gap: "12px", alignItems: "flex-end" }}>
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); handleSend(); } }}
            placeholder="Ask a medical question... (Enter to send)"
            rows={1}
            style={{ flex: 1, resize: "none", background: "#1e293b", border: "1px solid #334155", borderRadius: "12px", padding: "12px 16px", fontSize: "14px", color: "#f1f5f9", outline: "none" }}
          />
          <button
            onClick={handleSend}
            disabled={!input.trim() || isStreaming}
            style={{ width: "44px", height: "44px", borderRadius: "12px", background: "#0ea5e9", border: "none", cursor: "pointer", display: "flex", alignItems: "center", justifyContent: "center", opacity: (!input.trim() || isStreaming) ? 0.4 : 1 }}
          >
            <Send size={16} color="white" />
          </button>
        </div>
        {error && <p style={{ color: "#ef4444", fontSize: "12px", marginTop: "8px", maxWidth: "800px", margin: "8px auto 0" }}>{error}</p>}
      </div>
    </div>
  );
}