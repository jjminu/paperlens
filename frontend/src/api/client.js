// 백엔드 API 호출 래퍼.
const BASE = import.meta.env.VITE_API_BASE || "/api";

async function request(path, options = {}) {
  let resp;
  try {
    resp = await fetch(`${BASE}${path}`, {
      headers: { "Content-Type": "application/json" },
      ...options,
    });
  } catch (e) {
    // 네트워크 / 서버 다운
    throw new Error("백엔드 서버에 연결할 수 없습니다. 서버가 실행 중인지 확인해주세요.");
  }

  let data = null;
  const text = await resp.text();
  if (text) {
    try {
      data = JSON.parse(text);
    } catch {
      data = null;
    }
  }

  if (!resp.ok) {
    const detail = data?.detail || `요청 실패 (HTTP ${resp.status})`;
    throw new Error(typeof detail === "string" ? detail : JSON.stringify(detail));
  }
  return data;
}

export const api = {
  // 초록 직접 요약
  summarize: (title, abstract) =>
    request("/summarize", {
      method: "POST",
      body: JSON.stringify({ title, abstract }),
    }),

  // PMID로 PubMed 정보 + 요약
  summarizePubmed: (pmid) =>
    request(`/summarize/pubmed/${encodeURIComponent(pmid)}`, { method: "POST" }),

  // PMID 정보만 조회 (미리보기)
  getPubmed: (pmid) => request(`/pubmed/${encodeURIComponent(pmid)}`),

  // 저장된 목록
  listPapers: () => request("/papers"),

  // 상세
  getPaper: (id) => request(`/papers/${id}`),
};
