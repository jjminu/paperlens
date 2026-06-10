"""AI 요약 서비스.

OpenAI(또는 OpenAI-compatible) API를 호출해 논문 초록을 구조화 요약한다.
API 키가 없으면 mock 요약을 반환하여 키 없이도 앱이 동작하도록 한다.
"""
import json
from typing import Tuple

from config import settings
from schemas import Summary

# 초록이 너무 짧으면 의미있는 요약이 어렵다.
MIN_ABSTRACT_LENGTH = 40


class AIServiceError(Exception):
    """AI 요약 생성 중 발생하는 오류."""


# ── 시스템 프롬프트 (역할 부여) ──
SYSTEM_PROMPT = (
    "너는 생명과학, 의학, 약학 논문을 쉽게 설명해주는 연구 보조 AI다. "
    "사용자가 제공한 논문 초록을 바탕으로 연구 배경, 목적, 방법, 결과, 한계점, "
    "쉬운 한국어 요약, 핵심 키워드, 중요성, 후속 연구 아이디어를 구조화해서 "
    "설명해야 한다. 초록에 없는 내용은 추측하지 말고, 불확실한 부분은 "
    "'초록만으로는 확인하기 어렵다'고 말해야 한다. "
    "모든 출력은 한국어로 작성하되, 전문 용어는 영어 원어를 괄호 안에 함께 표기한다. "
    "예: 세포 사멸(apoptosis), 유전자 발현(gene expression)."
)

# AI가 반드시 따라야 하는 JSON 스키마 안내
JSON_INSTRUCTION = (
    "반드시 아래 키를 가진 JSON 객체만 출력해라. 추가 설명이나 마크다운 코드블록은 쓰지 마라.\n"
    "{\n"
    '  "background": "연구 배경",\n'
    '  "objective": "연구 목적",\n'
    '  "methods": "연구 방법",\n'
    '  "results": "주요 결과",\n'
    '  "limitations": "연구의 한계점",\n'
    '  "simple_korean_summary": "비전공자도 이해할 수 있는 쉬운 한국어 요약",\n'
    '  "keywords": ["키워드1", "키워드2", "키워드3", "키워드4", "키워드5"],\n'
    '  "importance": "이 논문이 중요한 이유",\n'
    '  "future_research": "후속 연구 아이디어"\n'
    "}"
)


def _build_user_prompt(title: str, abstract: str) -> str:
    return (
        f"논문 제목: {title}\n\n"
        f"논문 초록:\n{abstract}\n\n"
        f"{JSON_INSTRUCTION}"
    )


def _mock_summary(title: str, abstract: str) -> Summary:
    """OpenAI 키가 없을 때 사용하는 가짜 요약 (앱 흐름 확인용)."""
    snippet = abstract.strip().replace("\n", " ")
    snippet = (snippet[:120] + "…") if len(snippet) > 120 else snippet
    return Summary(
        background=(
            "[MOCK 응답] OpenAI API 키가 설정되지 않아 예시 요약을 표시합니다. "
            "실제 요약을 보려면 backend/.env 에 OPENAI_API_KEY 를 입력하세요."
        ),
        objective="[MOCK] 이 논문의 연구 목적이 여기에 한국어로 정리됩니다.",
        methods="[MOCK] 사용된 연구 방법(method)이 여기에 정리됩니다.",
        results=f"[MOCK] 입력한 초록 일부: “{snippet}”",
        limitations="초록만으로는 확인하기 어렵다. (MOCK)",
        simple_korean_summary=(
            f"[MOCK] '{title}' 논문을 쉬운 한국어로 풀어 설명한 내용이 여기에 표시됩니다."
        ),
        keywords=["mock", "예시", "키워드", "테스트", "데모"],
        importance="[MOCK] 이 논문이 왜 중요한지에 대한 설명이 여기에 표시됩니다.",
        future_research="[MOCK] 후속 연구 아이디어(future research)가 여기에 제안됩니다.",
    )


def _call_openai(title: str, abstract: str) -> Summary:
    """실제 OpenAI API 호출."""
    # 지연 import: 키가 없을 때 굳이 SDK를 불러오지 않기 위함
    from openai import OpenAI

    client_kwargs = {"api_key": settings.OPENAI_API_KEY}
    if settings.OPENAI_BASE_URL:
        client_kwargs["base_url"] = settings.OPENAI_BASE_URL

    client = OpenAI(**client_kwargs)

    try:
        completion = client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": _build_user_prompt(title, abstract)},
            ],
            response_format={"type": "json_object"},
            temperature=0.3,
        )
    except Exception as e:  # 네트워크/인증/쿼터 등 모든 호출 실패
        raise AIServiceError(f"AI API 호출에 실패했습니다: {e}") from e

    raw = completion.choices[0].message.content or ""
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        raise AIServiceError("AI 응답을 JSON으로 파싱하지 못했습니다.") from e

    # keywords가 문자열로 올 경우 방어적으로 리스트화
    if isinstance(data.get("keywords"), str):
        data["keywords"] = [k.strip() for k in data["keywords"].split(",") if k.strip()]

    try:
        return Summary(**data)
    except Exception as e:
        raise AIServiceError(f"AI 응답 형식이 올바르지 않습니다: {e}") from e


def summarize_abstract(title: str, abstract: str) -> Tuple[Summary, bool]:
    """초록을 요약한다.

    Returns:
        (Summary, used_mock) 튜플. used_mock 은 mock 응답 여부.

    Raises:
        AIServiceError: 초록이 너무 짧거나 AI 호출이 실패한 경우.
    """
    abstract = (abstract or "").strip()
    if len(abstract) < MIN_ABSTRACT_LENGTH:
        raise AIServiceError(
            f"초록이 너무 짧습니다. 최소 {MIN_ABSTRACT_LENGTH}자 이상 입력해주세요."
        )

    title = (title or "제목 없음").strip()

    if not settings.has_openai_key:
        return _mock_summary(title, abstract), True

    return _call_openai(title, abstract), False
