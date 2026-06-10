"""SQLAlchemy ORM 모델 정의."""
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Integer, String, Text

from database import Base


class Paper(Base):
    """요약된 논문 한 편을 나타내는 테이블."""

    __tablename__ = "papers"

    id = Column(Integer, primary_key=True, index=True)

    # 논문 메타데이터
    title = Column(String, nullable=False)
    pmid = Column(String, nullable=True, index=True)
    authors = Column(String, nullable=True)       # "홍길동, 김철수" 형태로 저장
    journal = Column(String, nullable=True)
    pub_year = Column(String, nullable=True)
    abstract = Column(Text, nullable=False)        # 원문 초록

    # AI 요약 결과 (JSON 문자열로 저장)
    summary_json = Column(Text, nullable=False)

    # 생의학 NER 개체 목록 (JSON 문자열로 저장)
    entities_json = Column(Text, nullable=True)

    # 생성 날짜 (UTC)
    created_at = Column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )
