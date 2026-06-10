// 원문 초록을 보여주면서, 생의학 NER 모델이 찾은 개체를 색으로 하이라이트한다.

// 그룹 → 표시 정보 (색상은 CSS 변수/클래스로 처리)
const GROUP_META = {
  gene: { label: "유전자·단백질", cls: "ent-gene" },
  disease: { label: "질병·증상", cls: "ent-disease" },
  chemical: { label: "약물·화학물질", cls: "ent-chemical" },
  anatomy: { label: "해부·구조", cls: "ent-anatomy" },
  species: { label: "생물종", cls: "ent-species" },
  other: { label: "기타", cls: "ent-other" },
};

function groupMeta(group) {
  return GROUP_META[group] || GROUP_META.other;
}

// 초록 텍스트를 개체 위치(start/end)에 따라 일반 텍스트 + <mark> 조각으로 나눈다.
function buildSegments(text, entities) {
  if (!entities || entities.length === 0) return [{ text, ent: null }];

  // 위치순 정렬 + 겹침 제거 (백엔드가 이미 처리하지만 방어적으로 한 번 더)
  const sorted = [...entities]
    .filter((e) => Number.isInteger(e.start) && Number.isInteger(e.end) && e.end > e.start)
    .sort((a, b) => a.start - b.start);

  const segments = [];
  let cursor = 0;
  let lastEnd = -1;

  for (const e of sorted) {
    if (e.start < lastEnd) continue; // 겹치면 건너뜀
    if (e.start > cursor) {
      segments.push({ text: text.slice(cursor, e.start), ent: null });
    }
    segments.push({ text: text.slice(e.start, e.end), ent: e });
    cursor = e.end;
    lastEnd = e.end;
  }
  if (cursor < text.length) {
    segments.push({ text: text.slice(cursor), ent: null });
  }
  return segments;
}

export default function HighlightedAbstract({ abstract, entities }) {
  if (!abstract) return null;

  const segments = buildSegments(abstract, entities);

  // 실제로 등장한 그룹만 범례에 표시
  const presentGroups = [...new Set((entities || []).map((e) => e.group))];

  return (
    <div className="ner-block">
      <h3>
        <span className="icon">🧬</span>
        생의학 개체 분석 (AI NER)
      </h3>

      {presentGroups.length > 0 ? (
        <div className="ner-legend">
          {presentGroups.map((g) => (
            <span className={`chip ${groupMeta(g).cls}`} key={g}>
              {groupMeta(g).label}
            </span>
          ))}
        </div>
      ) : (
        <p className="hint" style={{ marginTop: 0 }}>
          이 초록에서 인식된 생의학 개체가 없거나, NER 모델이 아직 연결되지 않았어요.
        </p>
      )}

      <p className="ner-text">
        {segments.map((seg, i) =>
          seg.ent ? (
            <mark
              key={i}
              className={`ent ${groupMeta(seg.ent.group).cls}`}
              title={`${seg.ent.label} (${(seg.ent.score * 100).toFixed(0)}%)`}
            >
              {seg.text}
            </mark>
          ) : (
            <span key={i}>{seg.text}</span>
          )
        )}
      </p>
    </div>
  );
}
