from __future__ import annotations

import json
from datetime import date
from typing import Any

from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_fixed

from .models import NewsItem
from .storage import bump_daily_calls, get_daily_calls


def _rule_summary(items: list[NewsItem], max_chars: int = 300) -> str:
    if not items:
        return "No high-confidence items passed strict source rules today."
    text = "; ".join([f"{it.title} ({it.source_name})" for it in items[:3]])
    return text[:max_chars]


@retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
def _chat(client: OpenAI, model: str, prompt: str, max_output_tokens: int) -> str:
    rsp = client.chat.completions.create(
        model=model,
        temperature=0.2,
        max_tokens=max_output_tokens,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a strict analyst. Use only provided facts. "
                    "Do not invent details. Output Chinese text with optional English entity names."
                ),
            },
            {"role": "user", "content": prompt},
        ],
    )
    return (rsp.choices[0].message.content or "").strip()


def llm_summary(
    cfg: Any,
    state: dict[str, Any],
    items: list[NewsItem],
    day: date,
) -> tuple[str, str]:
    if not cfg.openai_api_key:
        return _rule_summary(items, 300), _rule_summary(items, 2000)

    calls = get_daily_calls(state, day)
    if calls >= cfg.openai_daily_call_limit:
        return _rule_summary(items, 300), _rule_summary(items, 2000)

    client = OpenAI(api_key=cfg.openai_api_key, base_url=cfg.openai_base_url)
    compact_payload = [
        {
            "title": it.title,
            "summary": it.summary,
            "url": it.url,
            "source_kind": it.source_kind,
            "source_name": it.source_name,
            "is_earnings": it.is_earnings,
            "score": it.score,
            "reasons": it.reasons,
            "entities": it.entities,
        }
        for it in items[:12]
    ]
    payload = json.dumps(compact_payload, ensure_ascii=False)

    must_read_prompt = (
        "Create a Chinese must-read summary under 300 Chinese characters. "
        "Prioritize growth impact, brand risk, and earnings signals. "
        "No assumptions.\n"
        f"Input: {payload}"
    )
    detail_prompt = (
        "Create a detailed Chinese brief with sections: Key Points, Important Details, "
        "Earnings Interpretation if available, Risk Notes. "
        "Every statement should include source URL in brackets. No fabrication.\n"
        f"Input: {payload}"
    )

    must_read = _chat(client, cfg.openai_model, must_read_prompt, cfg.openai_max_output_tokens)
    bump_daily_calls(state, day)
    detail = _chat(client, cfg.openai_model, detail_prompt, cfg.openai_max_output_tokens)
    bump_daily_calls(state, day)
    return must_read[:300], detail

