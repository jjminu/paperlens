import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api/client.js";
import Loading from "../components/Loading.jsx";

function formatDate(iso) {
  if (!iso) return "";
  const d = new Date(iso);
  if (isNaN(d)) return iso;
  return d.toLocaleString("ko-KR", {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export default function HistoryPage() {
  const [papers, setPapers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    api
      .listPapers()
      .then(setPapers)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  return (
    <>
      <div className="hero">
        <h1>요약 기록</h1>
        <p>지금까지 요약한 논문 목록입니다.</p>
      </div>

      <div className="panel">
        {loading && <Loading text="목록을 불러오는 중…" />}
        {error && <div className="alert alert-error">❌ {error}</div>}

        {!loading && !error && papers.length === 0 && (
          <div className="empty">
            아직 저장된 요약이 없습니다.
            <br />
            <Link to="/">첫 논문을 요약해보세요 →</Link>
          </div>
        )}

        {papers.map((p) => (
          <div className="paper-item" key={p.id}>
            <div>
              <h3>{p.title}</h3>
              <div className="meta">
                {[p.journal, p.pub_year, p.pmid ? `PMID ${p.pmid}` : null]
                  .filter(Boolean)
                  .join(" · ")}
                {p.journal || p.pub_year || p.pmid ? " · " : ""}
                {formatDate(p.created_at)}
              </div>
            </div>
            <Link to={`/papers/${p.id}`} className="btn btn-ghost">
              자세히 보기
            </Link>
          </div>
        ))}
      </div>
    </>
  );
}
