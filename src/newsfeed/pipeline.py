from __future__ import annotations

from dataclasses import asdict
from datetime import datetime
from zoneinfo import ZoneInfo

from .config import load_config
from .emailer import fetch_feedback_emails, send_digest_email
from .feedback import build_preferences, parse_feedback
from .filtering import score_item, strict_filter
from .report import write_reports
from .sources import fetch_items
from .storage import append_jsonl, read_jsonl, read_state, write_state
from .summarizer import llm_summary


def run_digest(page_url: str) -> dict[str, str]:
    cfg = load_config()
    state = read_state(cfg.state_path)
    now = datetime.now(ZoneInfo(cfg.tz))
    day = now.date()

    prefs = build_preferences(read_jsonl(cfg.feedback_store, limit=120))
    state["preferences"] = prefs

    items = fetch_items(cfg.sources_cfg)
    scored = [score_item(i, cfg.sources_cfg, prefs=prefs) for i in items]
    kept, filtered = strict_filter(scored)

    must_read, detail = llm_summary(cfg, state, kept, day)
    md_path, _ = write_reports(
        report_dir=cfg.report_dir,
        pages_dir=cfg.pages_dir,
        must_read=must_read,
        detail=detail,
        items=kept[:15],
        filtered=filtered[:60],
        tz=cfg.tz,
    )

    append_jsonl(cfg.item_store, [x.to_json() for x in kept])
    append_jsonl(cfg.filtered_store, [x.to_json() for x in filtered])
    write_state(cfg.state_path, state)

    send_digest_email(cfg, must_read=must_read, page_url=page_url, md_path=str(md_path))
    return {"must_read": must_read, "md_path": str(md_path)}


def run_feedback_pull() -> int:
    cfg = load_config()
    emails = fetch_feedback_emails(cfg)
    rows = []
    for m in emails:
        parsed = parse_feedback(m["body"])
        parsed["subject"] = m["subject"]
        parsed["date"] = m["date"]
        rows.append(parsed)
    append_jsonl(cfg.feedback_store, rows)

    state = read_state(cfg.state_path)
    state["preferences"] = build_preferences(read_jsonl(cfg.feedback_store, limit=120))
    write_state(cfg.state_path, state)
    return len(rows)
