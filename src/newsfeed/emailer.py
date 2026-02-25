from __future__ import annotations

import email
import imaplib
import smtplib
from email.header import decode_header
from email.message import EmailMessage
from email.utils import parsedate_to_datetime
from typing import Any


def send_digest_email(cfg: Any, must_read: str, page_url: str, md_path: str) -> None:
    msg = EmailMessage()
    msg["Subject"] = "NEWSFEED Digest"
    msg["From"] = cfg.mail_from
    msg["To"] = cfg.mail_to
    msg.set_content(
        (
            f"Must-read summary (<=300 chars):\n{must_read}\n\n"
            f"Detailed web page: {page_url}\n"
            f"Detailed markdown: {md_path}\n\n"
            f"Reply with subject prefix {cfg.feedback_subject_prefix} to submit feedback.\n"
            "Template:\n"
            "keep: xxx\n"
            "drop: xxx\n"
            "reason: xxx\n"
            "Chinese template is also supported:\n"
            "\u4FDD\u7559: xxx\n"
            "\u5220\u9664: xxx\n"
            "\u539F\u56E0: xxx\n"
        ),
        charset="utf-8",
    )

    with smtplib.SMTP(cfg.smtp_host, cfg.smtp_port, timeout=30) as s:
        s.starttls()
        s.login(cfg.smtp_user, cfg.smtp_pass)
        s.send_message(msg)


def _decode_subject(raw: str) -> str:
    parts = decode_header(raw)
    out = []
    for text, enc in parts:
        if isinstance(text, bytes):
            out.append(text.decode(enc or "utf-8", errors="ignore"))
        else:
            out.append(text)
    return "".join(out)


def fetch_feedback_emails(cfg: Any, limit: int = 30) -> list[dict[str, str]]:
    results: list[dict[str, str]] = []
    with imaplib.IMAP4_SSL(cfg.imap_host, cfg.imap_port) as m:
        m.login(cfg.imap_user, cfg.imap_pass)
        m.select("INBOX")
        typ, data = m.search(None, f'(SUBJECT "{cfg.feedback_subject_prefix}")')
        if typ != "OK":
            return results
        ids = data[0].split()[-limit:]
        for i in ids:
            typ2, msg_data = m.fetch(i, "(RFC822)")
            if typ2 != "OK":
                continue
            raw = msg_data[0][1]
            msg = email.message_from_bytes(raw)
            subject = _decode_subject(msg.get("Subject", ""))
            dt = parsedate_to_datetime(msg.get("Date"))
            body = ""
            if msg.is_multipart():
                for part in msg.walk():
                    ctype = part.get_content_type()
                    if ctype == "text/plain":
                        body = part.get_payload(decode=True).decode(
                            part.get_content_charset() or "utf-8", errors="ignore"
                        )
                        break
            else:
                body = msg.get_payload(decode=True).decode(msg.get_content_charset() or "utf-8", errors="ignore")
            results.append({"subject": subject, "body": body.strip(), "date": dt.isoformat()})
    return results

