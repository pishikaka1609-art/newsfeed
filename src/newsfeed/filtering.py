from __future__ import annotations

import re
from datetime import datetime
from typing import Any

from .models import FilteredItem, NewsItem
from .sources import check_url_alive


LOW_SIGNAL_PATTERNS = [
    "lottery",
    "livestream replay",
    "ad",
    "promo list",
    "\u62BD\u5956",
    "\u5E7F\u544A",
]

GROWTH_PATTERN = r"growth|acquisition|activation|retention|conversion|\u62C9\u65B0|\u589E\u957F|\u4FC3\u6D3B|\u7559\u5B58|\u8F6C\u5316"
BRAND_PATTERN = r"incident|outage|penalty|complaint|controversy|\u8206\u60C5|\u4E8B\u6545|\u5904\u7F5A|\u6295\u8BC9|\u4E89\u8BAE|\u5B95\u673A"
MACRO_PATTERN = r"holiday|spring travel|summer travel|passenger|\u8282\u5047\u65E5|\u6625\u8FD0|\u6691\u8FD0|\u5BA2\u6D41"
COMP_PATTERN = r"launch|release|partnership|subsidy|discount|price|\u4E0A\u7EBF|\u53D1\u5E03|\u5408\u4F5C|\u8865\u8D34|\u964D\u4EF7|\u63D0\u4EF7"
COST_PATTERN = r"ad spend|CAC|ROI|commission|traffic cost|\u6295\u653E|\u4F63\u91D1|\u6D41\u91CF\u6210\u672C"
REG_PATTERN = r"regulation|compliance|policy|guideline|\u76D1\u7BA1|\u5408\u89C4|\u6761\u4F8B|\u529E\u6CD5"
MIN_IMPORTANCE_SCORE = 0.35


def score_item(item: NewsItem, cfg: dict[str, Any], prefs: dict[str, list[str]] | None = None) -> NewsItem:
    text = f"{item.title} {item.summary}"
    weights = cfg.get("priority_weights", {})
    score = 0.0
    reasons: list[str] = []

    if re.search(GROWTH_PATTERN, text, re.I):
        score += float(weights.get("growth_impact", 1.0))
        reasons.append("growth impact")
    if re.search(BRAND_PATTERN, text, re.I):
        score += float(weights.get("brand_risk", 0.9))
        reasons.append("brand risk")
    if item.is_earnings:
        score += float(weights.get("earnings_signal", 0.8))
        reasons.append("earnings signal")
    if re.search(MACRO_PATTERN, text, re.I):
        score += float(weights.get("macro_trend", 0.7))
        reasons.append("macro trend")
    if re.search(COMP_PATTERN, text, re.I):
        score += float(weights.get("competition", 0.6))
        reasons.append("competition move")
    if re.search(COST_PATTERN, text, re.I):
        score += float(weights.get("channel_cost", 0.5))
        reasons.append("channel cost signal")
    if re.search(REG_PATTERN, text, re.I):
        score += float(weights.get("compliance", 0.4))
        reasons.append("compliance/policy signal")

    if item.entities:
        score += 0.2
    if item.source_kind == "primary_disclosure":
        score += 0.4
        reasons.append("primary disclosure")

    prefs = prefs or {"keep_terms": [], "drop_terms": []}
    for term in prefs.get("keep_terms", []):
        if term and term in text:
            score += 0.2
            reasons.append(f"feedback keep: {term}")
            break
    for term in prefs.get("drop_terms", []):
        if term and term in text:
            score -= 0.25
            reasons.append(f"feedback drop: {term}")
            break

    item.score = round(score, 3)
    item.reasons = reasons
    return item


def strict_filter(items: list[NewsItem], min_score: float = MIN_IMPORTANCE_SCORE) -> tuple[list[NewsItem], list[FilteredItem]]:
    kept: list[NewsItem] = []
    filtered: list[FilteredItem] = []
    for it in items:
        reason = None
        lowered = f"{it.title} {it.summary}".lower()
        if not it.url.startswith("http"):
            reason = "missing traceable source url"
        elif any(pat.lower() in lowered for pat in LOW_SIGNAL_PATTERNS):
            reason = "low signal content"
        elif it.score < min_score:
            reason = "importance score too low"
        else:
            alive = check_url_alive(it.url)
            # Network instability should not wipe out the whole digest.
            # Keep strong items even if instant reachability check fails.
            if (not alive) and it.score < (min_score + 0.25):
                reason = "source link unreachable and low score"

        if reason:
            filtered.append(
                FilteredItem(
                    title=it.title,
                    url=it.url,
                    source_name=it.source_name,
                    reason=reason,
                    filtered_at=datetime.utcnow(),
                )
            )
            continue
        kept.append(it)
    kept.sort(key=lambda x: (x.score, x.published_at or datetime.min), reverse=True)
    return kept, filtered
