interface Props {
  text: string;
  isStreaming: boolean;
}

export default function StreamingText({ text, isStreaming }: Props) {
  return (
    <span>
      {text}
      {isStreaming && (
        <span style={{
          display: "inline-block", width: "2px", height: "14px",
          background: "#0ea5e9", marginLeft: "2px",
          animation: "blink 1s step-end infinite"
        }} />
      )}
      <style>{`@keyframes blink { 0%,100%{opacity:1} 50%{opacity:0} }`}</style>
    </span>
  );
}
