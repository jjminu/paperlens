# 🔬 PaperLens

**AI-powered research paper insight tool**

PubMed 논문 초록을 입력하면 AI가 **연구 배경 · 목적 · 방법 · 결과 · 한계점 · 쉬운 한국어 요약 · 핵심 키워드 · 중요성 · 후속 연구 아이디어**로 구조화해 정리해주는 Bio-AI 학습/연구 보조 웹 애플리케이션입니다.

단순 챗봇이 아니라, **Bio 전공자가 AI를 연구·학습 도구로 활용하는 워크플로**를 보여주는 포트폴리오용 풀스택 프로젝트입니다.

---

## ✨ 주요 기능

| 기능 | 설명 |
| --- | --- |
| 📝 초록 직접 요약 | 논문 초록을 붙여넣으면 AI가 9개 항목으로 구조화 요약 |
| 🔎 PMID 자동 요약 | PMID 입력 → PubMed에서 제목·저자·저널·연도·초록을 가져와 자동 요약 |
| 🇰🇷 한국어 + 원어 병기 | 전문 용어는 `세포 사멸(apoptosis)`처럼 영어 원어를 괄호로 병기 |
| 💾 결과 저장 | 모든 요약을 SQLite에 자동 저장 |
| 🗂️ 기록 페이지 | 저장된 요약 목록 조회 및 상세 보기 |
| 🛡️ MOCK 모드 | OpenAI 키가 없어도 예시 응답으로 전체 흐름 동작 |

AI는 다음 역할을 부여받습니다:

> "너는 생명과학, 의학, 약학 논문을 쉽게 설명해주는 연구 보조 AI다. (…) 초록에 없는 내용은 추측하지 말고, 불확실한 부분은 '초록만으로는 확인하기 어렵다'고 말해야 한다."

출력은 항상 **파싱 가능한 JSON**으로 반환됩니다.

---

## 🧱 기술 스택

- **Frontend**: React 18 + Vite, React Router
- **Backend**: FastAPI, Uvicorn
- **AI**: OpenAI API (OpenAI-compatible API도 지원, `OPENAI_BASE_URL`)
- **Database**: SQLite + SQLAlchemy
- **External API**: NCBI Entrez (PubMed E-utilities)
- **Styling**: 순수 CSS (커스텀 디자인 토큰)

```
bio ai 프로젝트/
├── backend/
│   ├── main.py              # FastAPI 앱 / 라우트
│   ├── config.py            # .env 로딩 / 설정
│   ├── database.py          # SQLAlchemy 엔진 / 세션
│   ├── models.py            # Paper ORM 모델
│   ├── schemas.py           # Pydantic 스키마
│   ├── services/
│   │   ├── ai_service.py    # OpenAI 호출 + MOCK 폴백
│   │   └── pubmed_service.py# PubMed efetch 조회/파싱
│   ├── requirements.txt
│   └── .env.example
└── frontend/
    ├── src/
    │   ├── pages/           # HomePage, HistoryPage, PaperDetailPage
    │   ├── components/      # Navbar, SummaryCard, Loading
    │   ├── api/client.js    # 백엔드 호출 래퍼
    │   └── styles/index.css
    ├── package.json
    └── .env.example
```

---

## 🚀 실행 방법

### 0) 사전 준비

- **Python 3.9+** (확인: `python3 --version`)
- **Node.js 18+** + npm — 설치돼 있지 않다면:
  - macOS(Homebrew): `brew install node`
  - 또는 공식 설치 프로그램: <https://nodejs.org> (LTS 버전)
  - 확인: `node -v && npm -v`

### 1) 백엔드 실행

```bash
cd backend
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env              # 필요 시 OPENAI_API_KEY 입력
uvicorn main:app --reload --port 8000
```

- API 문서(Swagger): <http://localhost:8000/docs>
- `OPENAI_API_KEY`가 비어 있으면 **MOCK 요약**이 반환됩니다(앱 흐름은 정상 동작).

### 2) 프론트엔드 실행 (새 터미널)

```bash
cd frontend
cp .env.example .env
npm install
npm run dev
```

- 접속: <http://localhost:5173>
- Vite 개발 프록시가 `/api/*` 요청을 `http://localhost:8000`으로 전달합니다.

### 3) 인터넷에 배포하기

Vercel(프론트) + Render(백엔드) 무료 배포 전체 과정은 **[DEPLOY.md](DEPLOY.md)** 를 참고하세요.

---

## 🔑 환경변수 설정

### backend/.env

| 변수 | 필수 | 설명 |
| --- | --- | --- |
| `OPENAI_API_KEY` | 권장 | 비우면 MOCK 모드로 동작 |
| `OPENAI_MODEL` | 선택 | 기본 `gpt-4o-mini` |
| `OPENAI_BASE_URL` | 선택 | OpenAI-compatible 엔드포인트(예: Together, Groq) |
| `NCBI_EMAIL` | 선택 | PubMed 안정성 향상(권장) |
| `NCBI_API_KEY` | 선택 | NCBI rate limit 상향 |
| `CORS_ORIGINS` | 선택 | 허용 오리진(기본 localhost:5173) |

> ⚠️ API 키는 절대 코드/깃에 커밋하지 마세요. `.env`는 `.gitignore`에 포함돼 있습니다.

### frontend/.env

| 변수 | 설명 |
| --- | --- |
| `VITE_API_BASE` | 백엔드 주소(기본 `/api`, Vite 프록시 사용) |

---

## 📡 API 엔드포인트

| 메서드 | 경로 | 설명 |
| --- | --- | --- |
| `POST` | `/summarize` | 초록 직접 입력 → AI 요약 + 저장 |
| `GET` | `/pubmed/{pmid}` | PMID로 PubMed 논문 정보 조회 |
| `POST` | `/summarize/pubmed/{pmid}` | PMID 정보 조회 → AI 요약 + 저장 |
| `GET` | `/papers` | 저장된 요약 목록 |
| `GET` | `/papers/{paper_id}` | 저장된 요약 상세 |
| `GET` | `/health` | 헬스 체크 (키 설정 여부 포함) |

**요청 예시** — `POST /summarize`

```json
{ "title": "논문 제목", "abstract": "논문 초록 …" }
```

**응답 예시**

```json
{
  "summary": {
    "background": "...",
    "objective": "...",
    "methods": "...",
    "results": "...",
    "limitations": "...",
    "simple_korean_summary": "...",
    "keywords": ["...", "..."],
    "importance": "...",
    "future_research": "..."
  },
  "paper_id": 1,
  "used_mock": false
}
```

빠른 테스트:

```bash
curl -X POST http://localhost:8000/summarize \
  -H "Content-Type: application/json" \
  -d '{"title":"Test","abstract":"This study investigates the role of p53 in apoptosis and gene expression in cancer cells."}'

# PMID로 요약 (실제 PubMed 논문)
curl -X POST http://localhost:8000/summarize/pubmed/33301246
```

---

## 🧯 예외 처리

다음 상황을 사용자 친화적 메시지로 처리합니다.

- 초록이 너무 짧을 때 (`최소 40자`)
- 빈 입력 제출
- PMID 형식 오류 / 존재하지 않는 PMID (404)
- PubMed에 초록이 없는 논문
- AI API 호출/파싱 실패
- 백엔드 미실행·네트워크 오류 (프론트에서 안내)

---

## 🧭 개발 단계 (MVP → 확장)

1. ✅ 초록 직접 입력 → AI 요약
2. ✅ PMID 입력 → PubMed 정보 가져오기
3. ✅ 요약 결과 DB 저장
4. ✅ 저장 기록 페이지 + 상세 페이지
5. ✅ UI 정리 및 README 작성

---

## 🔮 향후 개선 아이디어

- DOI / PubMed 링크 / 논문 제목 검색 입력 방식 추가
- 요약 결과 PDF·Markdown 내보내기
- 여러 논문 비교 요약 / 리뷰 초안 생성
- 사용자 인증 + 개인별 라이브러리
- 요약 품질 평가(LLM-as-judge) 및 근거 문장 하이라이트
- 벡터 DB 기반 유사 논문 추천
- 배포(예: Render/Fly.io + Vercel)

---

## 💼 포트폴리오용 설명

> **PaperLens**는 PubMed 논문 초록을 AI로 분석하여 연구 배경·방법·결과·한계점 등 9개 항목으로 구조화하는 풀스택 웹 애플리케이션입니다. Bio 전공 도메인 지식과 **FastAPI 기반 백엔드**, **React 기반 프론트엔드**, **LLM API 활용 능력**, 그리고 **외부 과학 API(NCBI Entrez) 연동**을 결합한 프로젝트입니다.

**면접/리뷰에서 강조할 포인트**

- **도메인 + 기술 융합**: 생명과학 논문 구조에 대한 이해를 프롬프트 설계와 출력 스키마에 반영
- **신뢰성 있는 프롬프트 설계**: "초록에 없는 내용은 추측 금지" 등 환각(hallucination) 억제 규칙과 JSON 강제 출력
- **견고한 백엔드 설계**: 서비스 레이어 분리(`ai_service`, `pubmed_service`), Pydantic 스키마 검증, 계층별 예외 처리
- **실제 외부 API 연동**: NCBI E-utilities XML 파싱
- **개발자 경험**: API 키 없이도 동작하는 MOCK 모드로 데모/온보딩 용이
- **보안 기본기**: API 키를 `.env`로 분리하고 깃 추적 제외

---

*Made for a Bio × AI portfolio.*
