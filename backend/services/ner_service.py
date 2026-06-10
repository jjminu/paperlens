"""생의학 개체명 인식(NER) 서비스.

HuggingFace Inference API에 올라간 생의학 NER 트랜스포머 모델을 호출해
초록 텍스트에서 유전자/단백질/질병/약물/해부학 등 개체를 추출한다.

모델: d4data/biomedical-ner-all (PubMedBERT 계열, token-classification)
- 토큰(HF_TOKEN)이 없으면 NER을 건너뛴다(빈 리스트 반환). 요약 기능 자체는 정상 동작.
- 모델 콜드스타트(503)는 wait_for_model 옵션 + 재시도로 처리한다.
"""
from __future__ import annotations

import time
from typing import List

import httpx

from config import settings
from schemas import Entity

HF_API_BASE = "https://api-inference.huggingface.co/models/"

# 모델이 내보내는 세부 라벨(수십 종)을 UI에서 쓸 6개 그룹으로 묶는다.
# key는 라벨을 대문자화한 부분 문자열, value는 그룹명.
_GROUP_RULES = [
    ("GENE", "gene"),
    ("PROTEIN", "gene"),
    ("DISEASE", "disease"),
    ("DISORDER", "disease"),
    ("SIGN", "disease"),
    ("SYMPTOM", "disease"),
    ("CANCER", "disease"),
    ("MEDICATION", "chemical"),
    ("DRUG", "chemical"),
    ("CHEMICAL", "chemical"),
    ("DOSAGE", "chemical"),
    ("BIOLOGICAL_STRUCTURE", "anatomy"),
    ("ANATOMY", "anatomy"),
    ("ORGAN", "anatomy"),
    ("TISSUE", "anatomy"),
    ("CELL", "anatomy"),
    ("ORGANISM", "species"),
    ("SPECIES", "species"),
    ("BACTERIA", "species"),
    ("VIRUS", "species"),
]


def _to_group(raw_label: str) -> str:
    """모델의 세부 라벨을 6개 그룹(gene/disease/chemical/anatomy/species/other) 중 하나로."""
    up = (raw_label or "").upper()
    for needle, group in _GROUP_RULES:
        if needle in up:
            return group
    return "other"


def _call_hf(text: str) -> list[dict]:
    """HF Inference API 호출 (콜드스타트 재시도 포함)."""
    url = HF_API_BASE + settings.HF_NER_MODEL
    headers = {"Authorization": f"Bearer {settings.HF_TOKEN}"}
    payload = {
        "inputs": text,
        # 그룹 단위로 묶어서 반환 + 모델이 깨어날 때까지 대기
        "parameters": {"aggregation_strategy": "simple"},
        "options": {"wait_for_model": True},
    }

    last_err = None
    with httpx.Client(timeout=45.0) as client:
        for attempt in range(3):
            try:
                resp = client.post(url, headers=headers, json=payload)
            except httpx.RequestError as e:
                last_err = e
                time.sleep(2)
                continue

            if resp.status_code == 503:
                # 모델 로딩 중. 잠시 후 재시도.
                time.sleep(3)
                continue
            if resp.status_code == 200:
                return resp.json()
            # 그 외 오류는 NER을 포기(요약은 살림)
            last_err = httpx.HTTPStatusError(
                f"HF status {resp.status_code}", request=resp.request, response=resp
            )
            break

    if last_err:
        # 조용히 실패 처리: 호출부에서 빈 리스트로 대체
        raise last_err
    return []


def extract_entities(text: str) -> List[Entity]:
    """텍스트에서 생의학 개체를 추출한다.

    토큰이 없거나 호출에 실패하면 빈 리스트를 반환한다(요약 흐름은 유지).
    """
    text = (text or "").strip()
    if not text or not settings.HF_TOKEN:
        return []

    try:
        raw = _call_hf(text)
    except Exception:
        return []

    if not isinstance(raw, list):
        return []

    entities: list[Entity] = []
    for item in raw:
        try:
            word = (item.get("word") or "").strip()
            start = item.get("start")
            end = item.get("end")
            if not word or start is None or end is None:
                continue
            entities.append(
                Entity(
                    text=word,
                    label=item.get("entity_group") or item.get("entity") or "other",
                    group=_to_group(item.get("entity_group") or item.get("entity") or ""),
                    start=int(start),
                    end=int(end),
                    score=float(item.get("score") or 0.0),
                )
            )
        except Exception:
            continue

    # 위치 순으로 정렬하고, 겹치는 개체는 앞선 것만 남긴다.
    entities.sort(key=lambda e: (e.start, -(e.end - e.start)))
    deduped: list[Entity] = []
    last_end = -1
    for e in entities:
        if e.start >= last_end:
            deduped.append(e)
            last_end = e.end
    return deduped
