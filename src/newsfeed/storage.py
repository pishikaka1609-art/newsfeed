from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Any


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def append_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        return
    ensure_parent(path)
    with path.open("a", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def read_jsonl(path: Path, limit: int | None = None) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    if limit is not None:
        return rows[-limit:]
    return rows


def read_state(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"model_calls": {}}
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def write_state(path: Path, state: dict[str, Any]) -> None:
    ensure_parent(path)
    with path.open("w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def get_daily_calls(state: dict[str, Any], day: date) -> int:
    return int(state.get("model_calls", {}).get(day.isoformat(), 0))


def bump_daily_calls(state: dict[str, Any], day: date) -> None:
    model_calls = state.setdefault("model_calls", {})
    model_calls[day.isoformat()] = int(model_calls.get(day.isoformat(), 0)) + 1
