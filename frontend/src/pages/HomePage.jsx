import { useState } from "react";
import { api } from "../api/client.js";
import SummaryCard from "../components/SummaryCard.jsx";
import Loading from "../components/Loading.jsx";

export default function HomePage() {
  const [mode, setMode] = useState("abstract"); // "abstract" | "pmid"

  // 초록 입력 모드 상태
  const [title, setTitle] = useState("");
  const [abstract, setAbstract] = useState("");

  // PMID 입력 모드 상태
  const [pmid, setPmid] = useState("");

  // 공통 상태
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState(null); // { title, summary, used_mock }

  async function handleAbstractSubmit(e) {
    e.preventDefault();
    setError("");
    if (!abstract.trim()) {
      setError("초록을 입력해주세요.");
      return;
    }
    setLoading(true);
    setResult(null);
    try {
      const data = await api.summarize(title.trim() || "제목 없음", abstract.trim());
      setResult({
        title: title.trim() || "제목 없음",
        summary: data.summary,
        used_mock: data.used_mock,
        abstract: data.abstract,
        entities: data.entities,
      });
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  async function handlePmidSubmit(e) {
    e.preventDefault();
    setError("");
    const cleaned = pmid.trim();
    if (!cleaned) {
      setError("PMID를 입력해주세요.");
      return;
    }
    if (!/^\d+$/.test(cleaned)) {
      setError("PMID는 숫자만 입력 가능합니다. (예: 33301246)");
      return;
    }
    setLoading(true);
    setResult(null);
    try {
      const data = await api.summarizePubmed(cleaned);
      setResult({
        title: `PMID ${cleaned}`,
        summary: data.summary,
        used_mock: data.used_mock,
        abstract: data.abstract,
        entities: data.entities,
      });
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <>
      <div className="hero">
        <h1>Bio Paper Summarizer</h1>
        <p>
          PubMed 논문 초록을 AI가 연구 배경, 방법, 결과, 한계점으로 정리해주는
          Bio-AI 학습 도구
        </p>
      </div>

      <div className="panel">
        <div className="tabs">
          <button
            className={`tab ${mode === "abstract" ? "active" : ""}`}
            onClick={() => {
              setMode("abstract");
              setError("");
            }}
          >
            📝 초록 직접 입력
          </button>
          <button
            className={`tab ${mode === "pmid" ? "active" : ""}`}
            onClick={() => {
              setMode("pmid");
              setError("");
            }}
          >
            🔎 PMID 입력
          </button>
        </div>

        {mode === "abstract" ? (
          <form onSubmit={handleAbstractSubmit}>
            <div className="field">
              <label htmlFor="title">논문 제목 (선택)</label>
              <input
                id="title"
                type="text"
                placeholder="예: The role of p53 in apoptosis"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
              />
            </div>
            <div className="field">
              <label htmlFor="abstract">논문 초록 *</label>
              <textarea
                id="abstract"
                rows={9}
                placeholder="요약할 논문 초록(abstract)을 붙여넣으세요."
                value={abstract}
                onChange={(e) => setAbstract(e.target.value)}
              />
              <div className="hint">영어/한국어 초록 모두 가능합니다.</div>
            </div>
            <button className="btn btn-block" type="submit" disabled={loading}>
              {loading ? "요약 중…" : "논문 요약하기"}
            </button>
          </form>
        ) : (
          <form onSubmit={handlePmidSubmit}>
            <div className="field">
              <label htmlFor="pmid">PubMed PMID *</label>
              <input
                id="pmid"
                type="text"
                placeholder="예: 33301246"
                value={pmid}
                onChange={(e) => setPmid(e.target.value)}
              />
              <div className="hint">
                PMID를 입력하면 PubMed에서 제목·저자·초록을 가져와 자동으로
                요약합니다.
              </div>
            </div>
            <button className="btn btn-block" type="submit" disabled={loading}>
              {loading ? "가져오는 중…" : "PubMed에서 가져와 요약하기"}
            </button>
          </form>
        )}
      </div>

      {loading && (
        <div className="panel">
          <Loading text="AI가 논문을 분석하고 있습니다…" />
        </div>
      )}

      {error && <div className="alert alert-error">❌ {error}</div>}

      {result && (
        <SummaryCard
          title={result.title}
          summary={result.summary}
          usedMock={result.used_mock}
          abstract={result.abstract}
          entities={result.entities}
        />
      )}
    </>
  );
}
