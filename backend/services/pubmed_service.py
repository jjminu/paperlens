"""PubMed (NCBI Entrez) 서비스.

PMID로 논문 메타데이터와 초록을 가져온다.
NCBI E-utilities의 efetch 엔드포인트(XML)를 사용한다.
"""
import xml.etree.ElementTree as ET

import httpx

from config import settings
from schemas import PubMedArticle

EFETCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"


class PubMedError(Exception):
    """PubMed 조회 중 발생하는 오류."""


class PubMedNotFound(PubMedError):
    """해당 PMID의 논문을 찾을 수 없음."""


def _build_params(pmid: str) -> dict:
    params = {"db": "pubmed", "id": pmid, "retmode": "xml"}
    # 이메일/키가 있으면 NCBI 권장 정책에 따라 함께 전송
    if settings.NCBI_EMAIL:
        params["email"] = settings.NCBI_EMAIL
        params["tool"] = "PaperLens"
    if settings.NCBI_API_KEY:
        params["api_key"] = settings.NCBI_API_KEY
    return params


def _text(el) -> str:
    """엘리먼트 내부의 모든 텍스트를 이어붙인다 (자식 태그 포함)."""
    if el is None:
        return ""
    return "".join(el.itertext()).strip()


def _parse_article(root: ET.Element, pmid: str) -> PubMedArticle:
    article = root.find(".//PubmedArticle")
    if article is None:
        raise PubMedNotFound(f"PMID {pmid} 에 해당하는 논문을 찾을 수 없습니다.")

    # 제목
    title = _text(article.find(".//ArticleTitle")) or "제목 없음"

    # 초록 (라벨이 붙은 여러 섹션일 수 있음)
    abstract_parts = []
    for ab in article.findall(".//Abstract/AbstractText"):
        label = ab.get("Label")
        content = _text(ab)
        if not content:
            continue
        abstract_parts.append(f"{label}: {content}" if label else content)
    abstract = "\n".join(abstract_parts).strip() or None

    # 저자
    authors = []
    for author in article.findall(".//AuthorList/Author"):
        last = _text(author.find("LastName"))
        fore = _text(author.find("ForeName"))
        collective = _text(author.find("CollectiveName"))
        if last or fore:
            authors.append(" ".join(p for p in [fore, last] if p))
        elif collective:
            authors.append(collective)

    # 저널명
    journal = (
        _text(article.find(".//Journal/Title"))
        or _text(article.find(".//Journal/ISOAbbreviation"))
        or None
    )

    # 발행연도
    pub_year = (
        _text(article.find(".//Journal/JournalIssue/PubDate/Year"))
        or _text(article.find(".//Journal/JournalIssue/PubDate/MedlineDate"))[:4]
        or None
    )

    return PubMedArticle(
        pmid=pmid,
        title=title,
        authors=authors,
        journal=journal,
        pub_year=pub_year,
        abstract=abstract,
    )


def fetch_pubmed_article(pmid: str) -> PubMedArticle:
    """PMID로 PubMed에서 논문 정보를 가져온다.

    Raises:
        PubMedNotFound: 논문이 존재하지 않는 경우.
        PubMedError: 네트워크 오류 등.
    """
    pmid = (pmid or "").strip()
    if not pmid.isdigit():
        raise PubMedError("PMID는 숫자여야 합니다.")

    try:
        with httpx.Client(timeout=15.0) as client:
            resp = client.get(EFETCH_URL, params=_build_params(pmid))
            resp.raise_for_status()
    except httpx.HTTPStatusError as e:
        raise PubMedError(f"PubMed 서버 오류 (status {e.response.status_code}).") from e
    except httpx.RequestError as e:
        raise PubMedError(
            "PubMed에 연결할 수 없습니다. 인터넷 연결을 확인해주세요."
        ) from e

    try:
        root = ET.fromstring(resp.content)
    except ET.ParseError as e:
        raise PubMedError("PubMed 응답을 해석하지 못했습니다.") from e

    return _parse_article(root, pmid)
