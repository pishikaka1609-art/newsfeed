from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml
from dotenv import load_dotenv


@dataclass
class AppConfig:
    openai_api_key: str
    openai_base_url: str
    openai_model: str
    openai_daily_call_limit: int
    openai_max_output_tokens: int
    smtp_host: str
    smtp_port: int
    smtp_user: str
    smtp_pass: str
    mail_from: str
    mail_to: str
    imap_host: str
    imap_port: int
    imap_user: str
    imap_pass: str
    feedback_subject_prefix: str
    state_path: Path
    feedback_store: Path
    filtered_store: Path
    item_store: Path
    report_dir: Path
    pages_dir: Path
    tz: str
    sources_cfg: dict[str, Any]


def _must(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise ValueError(f"Missing env var: {name}")
    return value


def load_config() -> AppConfig:
    load_dotenv()
    with Path("config/sources.yaml").open("r", encoding="utf-8") as f:
        sources_cfg = yaml.safe_load(f)
    return AppConfig(
        openai_api_key=os.getenv("OPENAI_API_KEY", "").strip(),
        openai_base_url=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1").strip(),
        openai_model=os.getenv("OPENAI_MODEL", "gpt-4o-mini").strip(),
        openai_daily_call_limit=int(os.getenv("OPENAI_DAILY_CALL_LIMIT", "10")),
        openai_max_output_tokens=int(os.getenv("OPENAI_MAX_OUTPUT_TOKENS", "800")),
        smtp_host=_must("SMTP_HOST"),
        smtp_port=int(os.getenv("SMTP_PORT", "587")),
        smtp_user=_must("SMTP_USER"),
        smtp_pass=_must("SMTP_PASS"),
        mail_from=_must("MAIL_FROM"),
        mail_to=_must("MAIL_TO"),
        imap_host=_must("IMAP_HOST"),
        imap_port=int(os.getenv("IMAP_PORT", "993")),
        imap_user=_must("IMAP_USER"),
        imap_pass=_must("IMAP_PASS"),
        feedback_subject_prefix=os.getenv("FEEDBACK_SUBJECT_PREFIX", "[NEWSFEED-FEEDBACK]").strip(),
        state_path=Path(os.getenv("STATE_PATH", "data/state.json")),
        feedback_store=Path(os.getenv("FEEDBACK_STORE", "data/feedback.jsonl")),
        filtered_store=Path(os.getenv("FILTERED_STORE", "data/filtered_items.jsonl")),
        item_store=Path(os.getenv("ITEM_STORE", "data/items.jsonl")),
        report_dir=Path(os.getenv("REPORT_DIR", "reports")),
        pages_dir=Path(os.getenv("PAGES_DIR", "docs")),
        tz=os.getenv("TZ", "Asia/Shanghai"),
        sources_cfg=sources_cfg,
    )

