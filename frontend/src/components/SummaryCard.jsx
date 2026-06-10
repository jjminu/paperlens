import HighlightedAbstract from "./HighlightedAbstract.jsx";

// AI 요약 결과를 항목별 카드로 보여준다.
const SECTIONS = [
  { key: "background", label: "연구 배경", icon: "📚" },
  { key: "objective", label: "연구 목적", icon: "🎯" },
  { key: "methods", label: "연구 방법", icon: "🧪" },
  { key: "results", label: "주요 결과", icon: "📊" },
  { key: "limitations", label: "연구의 한계점", icon: "⚠️" },
  { key: "simple_korean_summary", label: "쉬운 한국어 요약", icon: "💡" },
  { key: "importance", label: "이 논문이 중요한 이유", icon: "⭐" },
  { key: "future_research", label: "후속 연구 아이디어", icon: "🚀" },
];

export default function SummaryCard({ title, summary, usedMock, abstract, entities }) {
  if (!summary) return null;

  return (
    <div className="panel">
      <div className="summary-head">
        <h2>{title || "요약 결과"}</h2>
      </div>

      {usedMock && (
        <div className="alert alert-warn">
          ⚠️ OpenAI API 키가 없어 <b>예시(MOCK) 요약</b>이 표시됩니다. 실제 요약을
          보려면 <code>backend/.env</code> 에 <code>OPENAI_API_KEY</code> 를 설정하세요.
        </div>
      )}

      {abstract && (
        <div className="summary-section">
          <HighlightedAbstract abstract={abstract} entities={entities} />
        </div>
      )}

      {SECTIONS.map(({ key, label, icon }) => (
        <div className="summary-section" key={key}>
          <h3>
            <span className="icon">{icon}</span>
            {label}
          </h3>
          <p>{summary[key]}</p>
        </div>
      ))}

      <div className="summary-section">
        <h3>
          <span className="icon">🏷️</span>
          핵심 키워드
        </h3>
        <div className="keywords">
          {(summary.keywords || []).map((kw, i) => (
            <span className="chip" key={i}>
              {kw}
            </span>
          ))}
        </div>
      </div>
    </div>
  );
}
