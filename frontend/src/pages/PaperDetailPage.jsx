import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { api } from "../api/client.js";
import SummaryCard from "../components/SummaryCard.jsx";
import Loading from "../components/Loading.jsx";

export default function PaperDetailPage() {
  const { id } = useParams();
  const [paper, setPaper] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    api
      .getPaper(id)
      .then(setPaper)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, [id]);

  return (
    <>
      <Link to="/history" className="back-link">
        ← 기록으로 돌아가기
      </Link>

      {loading && (
        <div className="panel">
          <Loading text="불러오는 중…" />
        </div>
      )}
      {error && <div className="alert alert-error">❌ {error}</div>}

      {paper && (
        <>
          <div className="panel">
            <h2 style={{ marginTop: 0 }}>{paper.title}</h2>
            {paper.authors && <div className="detail-meta">👥 {paper.authors}</div>}
            <div className="detail-meta">
              {[
                paper.journal,
                paper.pub_year,
                paper.pmid ? `PMID ${paper.pmid}` : null,
              ]
                .filter(Boolean)
                .join(" · ")}
            </div>
            <details style={{ marginTop: 14 }}>
              <summary style={{ cursor: "pointer", fontWeight: 600 }}>
                원문 초록 보기
              </summary>
              <div className="abstract-box" style={{ marginTop: 10 }}>
                {paper.abstract}
              </div>
            </details>
          </div>

          <SummaryCard title="AI 요약" summary={paper.summary} />
        </>
      )}
    </>
  );
}
