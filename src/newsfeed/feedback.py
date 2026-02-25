from __future__ import annotations

import re
from datetime import datetime


def parse_feedback(body: str) -> dict[str, str]:
    keep = _capture(body, r"(?:保留|keep)[:：]\s*(.+)")
    drop = _capture(body, r"(?:删除|drop)[:：]\s*(.+)")
    reason = _capture(body, r"(?:原因|reason)[:：]\s*(.+)")
    if keep or drop or reason:
        return {
            "mode": "template",
            "keep": keep,
            "drop": drop,
            "reason": reason,
            "raw": body,
            "parsed_at": datetime.utcnow().isoformat(),
        }
    return {
        "mode": "freeform",
        "keep": "",
        "drop": "",
        "reason": "",
        "raw": body,
        "parsed_at": datetime.utcnow().isoformat(),
    }


def _capture(text: str, pat: str) -> str:
    m = re.search(pat, text, re.I)
    return m.group(1).strip() if m else ""


def build_preferences(rows: list[dict[str, str]], limit: int = 100) -> dict[str, list[str]]:
    keeps: list[str] = []
    drops: list[str] = []
    for r in rows[-limit:]:
        k = (r.get("keep") or "").strip()
        d = (r.get("drop") or "").strip()
        if k:
            keeps.extend([x.strip() for x in re.split(r"[，,;；/]", k) if x.strip()])
        if d:
            drops.extend([x.strip() for x in re.split(r"[，,;；/]", d) if x.strip()])
    return {"keep_terms": keeps[-30:], "drop_terms": drops[-30:]}
