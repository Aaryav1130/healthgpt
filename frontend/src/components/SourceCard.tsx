import type { Source } from "../hooks/useStreamingChat";

interface Props {
  source: Source;
  index: number;
}

export default function SourceCard({ source, index }: Props) {
  return (
    <div style={{
      padding: "10px 12px", borderRadius: "8px",
      background: "#0f172a", border: "1px solid #334155",
      fontSize: "12px"
    }}>
      <div style={{ color: "#0ea5e9", fontWeight: 600, marginBottom: "4px" }}>
        [{index + 1}] {source.source} — Page {source.page_num}
      </div>
      <div style={{ color: "#94a3b8", lineHeight: "1.5" }}>
        {source.text.slice(0, 150)}...
      </div>
      {source.rerank_score !== null && (
        <div style={{ color: "#475569", fontSize: "11px", marginTop: "4px" }}>
          Score: {source.rerank_score?.toFixed(3)}
        </div>
      )}
    </div>
  );
}
