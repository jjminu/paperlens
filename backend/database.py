"""SQLite 데이터베이스 연결 및 세션 관리 (SQLAlchemy)."""
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from config import settings

SQLALCHEMY_DATABASE_URL = f"sqlite:///{settings.DB_PATH}"

# check_same_thread=False : FastAPI의 멀티스레드 환경에서 SQLite를 쓰기 위함
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """FastAPI 의존성: 요청마다 DB 세션을 만들고 끝나면 닫는다."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """앱 시작 시 테이블을 생성한다."""
    # models를 import 해야 Base.metadata에 테이블이 등록된다.
    import models  # noqa: F401

    Base.metadata.create_all(bind=engine)
