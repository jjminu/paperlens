"""환경변수 로딩 및 앱 설정.

.env 파일을 읽어 애플리케이션 전역에서 사용하는 설정값을 제공한다.
"""
import os

from dotenv import load_dotenv

# backend/.env 파일을 로드한다.
load_dotenv()


class Settings:
    # OpenAI / OpenAI-compatible
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "").strip()
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini").strip()
    OPENAI_BASE_URL: str = os.getenv("OPENAI_BASE_URL", "").strip()

    # NCBI Entrez (PubMed)
    NCBI_EMAIL: str = os.getenv("NCBI_EMAIL", "").strip()
    NCBI_API_KEY: str = os.getenv("NCBI_API_KEY", "").strip()

    # CORS
    CORS_ORIGINS: list[str] = [
        o.strip()
        for o in os.getenv(
            "CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173"
        ).split(",")
        if o.strip()
    ]

    # DB 파일 위치 (backend/paperlens.db)
    DB_PATH: str = os.path.join(os.path.dirname(__file__), "paperlens.db")

    @property
    def has_openai_key(self) -> bool:
        return bool(self.OPENAI_API_KEY)


settings = Settings()
