import { useRef, useState } from "react";
import { Upload, X, FileText } from "lucide-react";
import { uploadPDF, getIndexStatus } from "../api/client";

interface Props {
  onClose: () => void;
  onSuccess: (status: any) => void;
}

export default function UploadModal({ onClose, onSuccess }: Props) {
  const [isUploading, setIsUploading] = useState(false);
  const [message, setMessage] = useState("");
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setIsUploading(true);
    setMessage("Uploading and ingesting PDF...");
    try {
      const result = await uploadPDF(file);
      const status = await getIndexStatus();
      setMessage(`✅ Ingested "${result.filename}" — ${result.chunks_created} chunks created`);
      onSuccess(status);
    } catch {
      setMessage("❌ Upload failed. Make sure backend is running.");
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
        borderRadius: "16px", padding: "24px", width: "400px"
      }}>
        <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "20px" }}>
          <h2 style={{ fontSize: "16px", fontWeight: 600, color: "#f1f5f9" }}>Upload Medical PDF</h2>
          <button onClick={onClose} style={{ background: "none", border: "none", color: "#64748b", cursor: "pointer" }}>
            <X size={18} />
          </button>
        </div>
        <div
          onClick={() => fileInputRef.current?.click()}
          style={{
            border: "2px dashed #334155", borderRadius: "12px",
            padding: "32px", textAlign: "center", cursor: "pointer",
            color: "#64748b"
          }}
        >
          <FileText size={32} style={{ margin: "0 auto 8px" }} />
          <p style={{ fontSize: "14px" }}>Click to select a PDF file</p>
          <p style={{ fontSize: "12px", marginTop: "4px" }}>Max 50MB</p>
        </div>
        <input ref={fileInputRef} type="file" accept=".pdf" onChange={handleUpload} style={{ display: "none" }} />
        {message && (
          <p style={{ marginTop: "12px", fontSize: "13px", color: message.includes("✅") ? "#10b981" : "#ef4444" }}>
            {message}
          </p>
        )}
        {isUploading && (
          <p style={{ marginTop: "8px", fontSize: "12px", color: "#94a3b8" }}>
            Processing chunks and building FAISS index...
          </p>
        )}
      </div>
    </div>
  );
}
