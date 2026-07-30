import { useRef, useState } from "react";
import { X, FileText, Loader } from "lucide-react";
import { uploadPDF, getIndexStatus } from "../api/client";

interface Props {
  onClose: () => void;
  onSuccess: (status: any) => void;
}

export default function UploadModal({ onClose, onSuccess }: Props) {
  const [isUploading, setIsUploading] = useState(false);
  const [message, setMessage] = useState("");
  const [progress, setProgress] = useState(0);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setIsUploading(true);
    setProgress(0);
    setMessage("⏳ Uploading PDF to server...");

    // Simulate progress while waiting
    const progressInterval = setInterval(() => {
      setProgress((prev) => {
        if (prev >= 90) return prev;
        return prev + 2;
      });
    }, 3000);

    // Update messages over time so user knows it's working
    const msg1 = setTimeout(() => setMessage("⚙️ Extracting text from PDF..."), 5000);
    const msg2 = setTimeout(() => setMessage("🧠 Creating embeddings (this takes 1-3 mins on free tier)..."), 15000);
    const msg3 = setTimeout(() => setMessage("📊 Building FAISS index..."), 60000);
    const msg4 = setTimeout(() => setMessage("🔄 Almost done, finalizing index..."), 120000);

    try {
      const result = await uploadPDF(file);
      const status = await getIndexStatus();
      clearInterval(progressInterval);
      clearTimeout(msg1);
      clearTimeout(msg2);
      clearTimeout(msg3);
      clearTimeout(msg4);
      setProgress(100);
      setMessage(`✅ Ingested "${result.filename}" — ${result.chunks_created} chunks created!`);
      onSuccess(status);
    } catch (err: any) {
      clearInterval(progressInterval);
      clearTimeout(msg1);
      clearTimeout(msg2);
      clearTimeout(msg3);
      clearTimeout(msg4);

      if (err.code === "ECONNABORTED" || err.message?.includes("timeout")) {
        setMessage("⏳ Still processing on server — PDF may have ingested. Wait 2 mins then ask a question to verify!");
      } else {
        setMessage("❌ Upload failed. Try a smaller PDF or check backend.");
      }
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div style={{
      position: "fixed", inset: 0, background: "rgba(0,0,0,0.7)",
      display: "flex", alignItems: "center", justifyContent: "center", zIndex: 50
    }}>
      <div style={{
        background: "#1e293b", border: "1px solid #334155",
        borderRadius: "16px", padding: "24px", width: "420px"
      }}>
        {/* Header */}
        <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "20px" }}>
          <h2 style={{ fontSize: "16px", fontWeight: 600, color: "#f1f5f9" }}>
            Upload Medical PDF
          </h2>
          <button
            onClick={onClose}
            disabled={isUploading}
            style={{ background: "none", border: "none", color: "#64748b", cursor: isUploading ? "not-allowed" : "pointer" }}
          >
            <X size={18} />
          </button>
        </div>

        {/* Drop zone */}
        <div
          onClick={() => !isUploading && fileInputRef.current?.click()}
          style={{
            border: `2px dashed ${isUploading ? "#0ea5e9" : "#334155"}`,
            borderRadius: "12px", padding: "32px", textAlign: "center",
            cursor: isUploading ? "not-allowed" : "pointer", color: "#64748b",
            background: isUploading ? "rgba(14,165,233,0.05)" : "transparent",
            transition: "all 0.3s"
          }}
        >
          {isUploading ? (
            <Loader size={32} style={{ margin: "0 auto 8px", color: "#0ea5e9", animation: "spin 1s linear infinite" }} />
          ) : (
            <FileText size={32} style={{ margin: "0 auto 8px" }} />
          )}
          <p style={{ fontSize: "14px" }}>
            {isUploading ? "Processing..." : "Click to select a PDF file"}
          </p>
          <p style={{ fontSize: "12px", marginTop: "4px" }}>
            {isUploading ? "Do not close this window" : "Max 50MB · Medical PDFs recommended"}
          </p>
        </div>

        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf"
          onChange={handleUpload}
          style={{ display: "none" }}
        />

        {/* Progress bar */}
        {isUploading && (
          <div style={{ marginTop: "16px" }}>
            <div style={{
              background: "#0f172a", borderRadius: "8px",
              height: "6px", overflow: "hidden"
            }}>
              <div style={{
                height: "100%", borderRadius: "8px",
                background: "linear-gradient(90deg, #0ea5e9, #10b981)",
                width: `${progress}%`,
                transition: "width 0.5s ease"
              }} />
            </div>
            <p style={{ fontSize: "11px", color: "#64748b", marginTop: "4px", textAlign: "right" }}>
              {progress}%
            </p>
          </div>
        )}

        {/* Message */}
        {message && (
          <p style={{
            marginTop: "12px", fontSize: "13px", lineHeight: "1.5",
            color: message.includes("✅") ? "#10b981" :
                   message.includes("⏳") ? "#f59e0b" :
                   message.includes("❌") ? "#ef4444" : "#94a3b8"
          }}>
            {message}
          </p>
        )}

        {/* Warning */}
        {isUploading && (
          <div style={{
            marginTop: "12px", padding: "10px 12px", borderRadius: "8px",
            background: "rgba(245,158,11,0.1)", border: "1px solid rgba(245,158,11,0.2)"
          }}>
            <p style={{ fontSize: "12px", color: "#f59e0b", margin: 0 }}>
              ⚠️ Free tier processing takes 1-3 minutes. Please keep this window open!
            </p>
          </div>
        )}

        {/* Spinner animation */}
        <style>{`
          @keyframes spin {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
          }
        `}</style>
      </div>
    </div>
  );
}
