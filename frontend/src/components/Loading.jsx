export default function Loading({ text = "처리 중입니다…" }) {
  return (
    <div className="loading">
      <div className="spinner" />
      <span>{text}</span>
    </div>
  );
}
