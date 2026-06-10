"""Pydantic 스키마 (요청/응답 모델)."""
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


# ── 생의학 개체(NER) ──
class Entity(BaseModel):
    text: str = Field(..., description="개체 텍스트")
    label: str = Field(..., description="모델이 부여한 세부 라벨")
    group: str = Field(..., description="UI용 그룹: gene/disease/chemical/anatomy/species/other")
    start: int = Field(..., description="원문 내 시작 인덱스")
    end: int = Field(..., description="원문 내 끝 인덱스")
    score: float = Field(default=0.0, description="신뢰도")


# ── AI 요약 결과 구조 ──
class Summary(BaseModel):
    background: str = Field(..., description="연구 배경")
    objective: str = Field(..., description="연구 목적")
    methods: str = Field(..., description="연구 방법")
    results: str = Field(..., description="주요 결과")
    limitations: str = Field(..., description="연구의 한계점")
    simple_korean_summary: str = Field(..., description="쉬운 한국어 요약")
    keywords: List[str] = Field(default_factory=list, description="핵심 키워드 5개")
    importance: str = Field(..., description="이 논문이 중요한 이유")
    future_research: str = Field(..., description="후속 연구 아이디어")


# ── /summarize 요청 ──
class SummarizeRequest(BaseModel):
    title: Optional[str] = Field(default="제목 없음", description="논문 제목")
    abstract: str = Field(..., min_length=1, description="논문 초록")


# ── /summarize 응답 ──
class SummarizeResponse(BaseModel):
    summary: Summary
    # 하이라이트용: 분석에 사용된 원문 초록 + 추출된 개체 목록
    abstract: str = ""
    entities: List[Entity] = Field(default_factory=list)
    # 저장된 경우 paper id를 함께 반환
    paper_id: Optional[int] = None
    used_mock: bool = False  # API 키가 없어 mock 요약을 썼는지 여부


# ── PubMed 메타데이터 ──
class PubMedArticle(BaseModel):
    pmid: str
    title: str
    authors: List[str] = Field(default_factory=list)
    journal: Optional[str] = None
    pub_year: Optional[str] = None
    abstract: Optional[str] = None


# ── 저장된 논문 목록 항목 ──
class PaperListItem(BaseModel):
    id: int
    title: str
    journal: Optional[str] = None
    pub_year: Optional[str] = None
    pmid: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# ── 저장된 논문 상세 ──
class PaperDetail(BaseModel):
    id: int
    title: str
    pmid: Optional[str] = None
    authors: Optional[str] = None
    journal: Optional[str] = None
    pub_year: Optional[str] = None
    abstract: str
    summary: Summary
    entities: List[Entity] = Field(default_factory=list)
    created_at: datetime
