"""PaperLens — FastAPI 백엔드 진입점.

AI 논문 요약 API:
  POST /summarize               초록 직접 입력 → AI 요약
  GET  /pubmed/{pmid}           PMID로 PubMed 논문 정보 조회
  POST /summarize/pubmed/{pmid} PMID → PubMed 정보 가져온 뒤 AI 요약 + 저장
  GET  /papers                  저장된 요약 목록
  GET  /papers/{paper_id}       저장된 요약 상세
"""
from __future__ import annotations

import json

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

import models
from config import settings
from database import get_db, init_db
from schemas import (
    Entity,
    PaperDetail,
    PaperListItem,
    PubMedArticle,
    SummarizeRequest,
    SummarizeResponse,
    Summary,
)
from services.ai_service import AIServiceError, summarize_abstract
from services.ner_service import extract_entities
from services.pubmed_service import PubMedError, PubMedNotFound, fetch_pubmed_article

app = FastAPI(
    title="PaperLens API",
    description="AI-powered research paper insight tool",
    version="1.0.0",
)

# ── CORS ──
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    init_db()


# ── 헬퍼: 논문 + 요약을 DB에 저장 ──
def _save_paper(
    db: Session,
    *,
    title: str,
    abstract: str,
    summary: Summary,
    entities: list[Entity] | None = None,
    pmid: str | None = None,
    authors: list[str] | None = None,
    journal: str | None = None,
    pub_year: str | None = None,
) -> models.Paper:
    paper = models.Paper(
        title=title,
        pmid=pmid,
        authors=", ".join(authors) if authors else None,
        journal=journal,
        pub_year=pub_year,
        abstract=abstract,
        summary_json=summary.model_dump_json(),
        entities_json=json.dumps([e.model_dump() for e in (entities or [])]),
    )
    db.add(paper)
    db.commit()
    db.refresh(paper)
    return paper


def _paper_to_detail(paper: models.Paper) -> PaperDetail:
    entities = []
    if paper.entities_json:
        try:
            entities = [Entity(**e) for e in json.loads(paper.entities_json)]
        except Exception:
            entities = []
    return PaperDetail(
        id=paper.id,
        title=paper.title,
        pmid=paper.pmid,
        authors=paper.authors,
        journal=paper.journal,
        pub_year=paper.pub_year,
        abstract=paper.abstract,
        summary=Summary(**json.loads(paper.summary_json)),
        entities=entities,
        created_at=paper.created_at,
    )


# ── 헬스 체크 ──
@app.get("/health")
def health():
    return {
        "status": "ok",
        "has_openai_key": settings.has_openai_key,
        "has_hf_token": settings.has_hf_token,
    }


# ── 1) 초록 직접 입력 → 요약 ──
@app.post("/summarize", response_model=SummarizeResponse)
def summarize(req: SummarizeRequest, db: Session = Depends(get_db)):
    abstract = (req.abstract or "").strip()
    if not abstract:
        raise HTTPException(status_code=400, detail="초록을 입력해주세요.")

    try:
        summary, used_mock = summarize_abstract(req.title or "제목 없음", abstract)
    except AIServiceError as e:
        raise HTTPException(status_code=422, detail=str(e))

    # 생의학 개체 추출 (실패해도 요약은 반환)
    entities = extract_entities(abstract)

    paper = _save_paper(
        db,
        title=req.title or "제목 없음",
        abstract=abstract,
        summary=summary,
        entities=entities,
    )

    return SummarizeResponse(
        summary=summary,
        abstract=abstract,
        entities=entities,
        paper_id=paper.id,
        used_mock=used_mock,
    )


# ── 2) PMID → PubMed 정보 조회 ──
@app.get("/pubmed/{pmid}", response_model=PubMedArticle)
def get_pubmed(pmid: str):
    try:
        article = fetch_pubmed_article(pmid)
    except PubMedNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PubMedError as e:
        raise HTTPException(status_code=502, detail=str(e))
    return article


# ── 3) PMID → 정보 조회 + AI 요약 + 저장 ──
@app.post("/summarize/pubmed/{pmid}", response_model=SummarizeResponse)
def summarize_pubmed(pmid: str, db: Session = Depends(get_db)):
    try:
        article = fetch_pubmed_article(pmid)
    except PubMedNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PubMedError as e:
        raise HTTPException(status_code=502, detail=str(e))

    if not article.abstract:
        raise HTTPException(
            status_code=422,
            detail=f"PMID {pmid} 논문에서 초록을 찾을 수 없습니다.",
        )

    try:
        summary, used_mock = summarize_abstract(article.title, article.abstract)
    except AIServiceError as e:
        raise HTTPException(status_code=422, detail=str(e))

    entities = extract_entities(article.abstract)

    paper = _save_paper(
        db,
        title=article.title,
        abstract=article.abstract,
        summary=summary,
        entities=entities,
        pmid=article.pmid,
        authors=article.authors,
        journal=article.journal,
        pub_year=article.pub_year,
    )

    return SummarizeResponse(
        summary=summary,
        abstract=article.abstract,
        entities=entities,
        paper_id=paper.id,
        used_mock=used_mock,
    )


# ── 4) 저장된 요약 목록 ──
@app.get("/papers", response_model=list[PaperListItem])
def list_papers(db: Session = Depends(get_db)):
    papers = db.query(models.Paper).order_by(models.Paper.created_at.desc()).all()
    return papers


# ── 5) 저장된 요약 상세 ──
@app.get("/papers/{paper_id}", response_model=PaperDetail)
def get_paper(paper_id: int, db: Session = Depends(get_db)):
    paper = db.query(models.Paper).filter(models.Paper.id == paper_id).first()
    if paper is None:
        raise HTTPException(status_code=404, detail="해당 논문을 찾을 수 없습니다.")
    return _paper_to_detail(paper)
