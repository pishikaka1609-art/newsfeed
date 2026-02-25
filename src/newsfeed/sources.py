from __future__ import annotations

import re
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from typing import Any
from urllib.parse import urlparse

import feedparser
import requests
from bs4 import BeautifulSoup

from .models import NewsItem

UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
)


def _clean_html(text: str) -> str:
    if not text:
        return ""
    soup = BeautifulSoup(text, "lxml")
    return " ".join(soup.get_text(" ").split())


def _parse_time(entry: Any) -> datetime | None:
    for key in ("published", "updated"):
        raw = getattr(entry, key, None) or entry.get(key)
        if raw:
            try:
                dt = parsedate_to_datetime(raw)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                return dt
            except Exception:
                pass
    return None


def _extract_entities(text: str, entities: list[str]) -> list[str]:
    matched = []
    for e in entities:
        if e and e in text:
            matched.append(e)
    return matched


def _source_kind(url: str) -> str:
    host = (urlparse(url).hostname or "").lower()
    if any(x in host for x in ["gov.cn", "sec.gov", "hkexnews.hk", "szse.cn", "sse.com.cn"]):
        return "primary_disclosure"
    return "media_transfer"


def fetch_items(sources_cfg: dict[str, Any], days_back: int = 3) -> list[NewsItem]:
    all_entities = sources_cfg.get("entities", {}).get("core_clients", []) + sources_cfg.get("entities", {}).get("watchlist", [])
    cutoff = datetime.now(timezone.utc) - timedelta(days=days_back)
    items: list[NewsItem] = []
    for src in sources_cfg.get("sources", []):
        if src.get("type") != "rss":
            continue
        url = src["url"]
        try:
            parsed = feedparser.parse(url, request_headers={"User-Agent": UA})
        except Exception:
            continue
        for entry in parsed.entries:
            link = entry.get("link", "").strip()
            title = entry.get("title", "").strip()
            summary = _clean_html(entry.get("summary", ""))
            if not link or not title:
                continue
            dt = _parse_time(entry)
            if dt and dt < cutoff:
                continue
            full_text = f"{title} {summary}"
            entities = _extract_entities(full_text, all_entities)
            items.append(
                NewsItem(
                    source_name=src["name"],
                    source_tier=src.get("tier", "media"),
                    title=title,
                    url=link,
                    published_at=dt,
                    summary=summary[:700],
                    tags=src.get("tags", []),
                    entities=entities,
                    source_kind=_source_kind(link),
                    is_earnings=bool(re.search(r"财报|业绩|季度|年度|earnings|results", full_text, re.I)),
                )
            )
    return dedupe_items(items)


def dedupe_items(items: list[NewsItem]) -> list[NewsItem]:
    seen = set()
    out = []
    for it in items:
        key = (it.title.strip().lower(), it.url.split("?")[0])
        if key in seen:
            continue
        seen.add(key)
        out.append(it)
    return out


def check_url_alive(url: str, timeout: int = 10) -> bool:
    try:
        resp = requests.get(url, timeout=timeout, headers={"User-Agent": UA})
        return 200 <= resp.status_code < 400
    except Exception:
        return False

