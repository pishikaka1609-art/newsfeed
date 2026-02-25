from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Any


@dataclass
class NewsItem:
    source_name: str
    source_tier: str
    title: str
    url: str
    published_at: datetime | None
    summary: str
    tags: list[str] = field(default_factory=list)
    entities: list[str] = field(default_factory=list)
    score: float = 0.0
    reasons: list[str] = field(default_factory=list)
    is_earnings: bool = False
    source_kind: str = "media_transfer"

    def to_json(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["published_at"] = self.published_at.isoformat() if self.published_at else None
        return payload


@dataclass
class FilteredItem:
    title: str
    url: str
    source_name: str
    reason: str
    filtered_at: datetime

    def to_json(self) -> dict[str, Any]:
        return {
            "title": self.title,
            "url": self.url,
            "source_name": self.source_name,
            "reason": self.reason,
            "filtered_at": self.filtered_at.isoformat(),
        }

