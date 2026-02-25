from __future__ import annotations

from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from jinja2 import Template

from .models import FilteredItem, NewsItem

HTML_TEMPLATE = """<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{{ title }}</title>
<style>
body{font-family:"Noto Sans SC","PingFang SC","Microsoft YaHei",sans-serif;margin:0;background:linear-gradient(180deg,#f7fbff,#eef5ec);color:#13232f}
.wrap{max-width:900px;margin:32px auto;padding:0 16px}
.card{background:#fff;border-radius:14px;padding:18px 20px;box-shadow:0 8px 24px rgba(0,0,0,.06);margin-bottom:16px}
h1{margin:0 0 12px;font-size:28px} h2{margin:0 0 8px;font-size:20px}
a{color:#0b5ea8;text-decoration:none} a:hover{text-decoration:underline}
small{color:#5b6b77}
li{margin:8px 0}
</style></head><body>
<div class="wrap">
<div class="card"><h1>{{ title }}</h1><p>{{ must_read }}</p><small>Generated: {{ generated }}</small></div>
<div class="card"><h2>Detailed Brief</h2><p style="white-space:pre-wrap">{{ detail }}</p></div>
<div class="card"><h2>Top Items</h2><ol>{% for i in items %}<li><a href="{{ i.url }}">{{ i.title }}</a> ({{ i.source_name }}, {{ i.source_kind }}, score={{ i.score }})</li>{% endfor %}</ol></div>
<div class="card"><h2>Filtered Log</h2><ul>{% for f in filtered %}<li>{{ f.title }} - {{ f.reason }} <a href="{{ f.url }}">source</a></li>{% endfor %}</ul></div>
</div></body></html>"""


def build_markdown(
    day_label: str,
    must_read: str,
    detail: str,
    items: list[NewsItem],
    filtered: list[FilteredItem],
) -> str:
    lines = [
        f"# NEWSFEED Digest - {day_label}",
        "",
        "## Must Read (<=300 chars)",
        must_read,
        "",
        "## Detailed Brief",
        detail,
        "",
        "## Top Items",
    ]
    for i, it in enumerate(items, 1):
        lines.append(
            f"{i}. [{it.title}]({it.url}) | source={it.source_name} | kind={it.source_kind} | score={it.score} | reasons={';'.join(it.reasons)}"
        )
    lines += ["", "## Filtered Log"]
    for i, it in enumerate(filtered, 1):
        lines.append(f"{i}. {it.title} | reason={it.reason} | url={it.url}")
    return "\n".join(lines)


def write_reports(
    report_dir: Path,
    pages_dir: Path,
    must_read: str,
    detail: str,
    items: list[NewsItem],
    filtered: list[FilteredItem],
    tz: str,
) -> tuple[Path, Path]:
    now = datetime.now(ZoneInfo(tz))
    day_label = now.strftime("%Y-%m-%d")
    report_dir.mkdir(parents=True, exist_ok=True)
    pages_dir.mkdir(parents=True, exist_ok=True)

    md = build_markdown(day_label, must_read, detail, items, filtered)
    md_path = report_dir / f"digest-{day_label}.md"
    md_path.write_text(md, encoding="utf-8")

    html = Template(HTML_TEMPLATE).render(
        title=f"NEWSFEED Industry Digest - {day_label}",
        must_read=must_read,
        detail=detail,
        items=items,
        filtered=filtered,
        generated=now.strftime("%Y-%m-%d %H:%M %Z"),
    )
    html_path = pages_dir / "index.html"
    html_path.write_text(html, encoding="utf-8")

    return md_path, html_path

