from __future__ import annotations

import argparse
import os

from .pipeline import run_digest, run_feedback_pull


def main() -> None:
    parser = argparse.ArgumentParser(description="NEWSFEED automation")
    sub = parser.add_subparsers(dest="cmd", required=True)
    run_cmd = sub.add_parser("run", help="run digest pipeline")
    run_cmd.add_argument("--page-url", default=os.getenv("PAGES_URL", ""))
    sub.add_parser("pull-feedback", help="pull feedback emails via IMAP")
    args = parser.parse_args()

    if args.cmd == "run":
        if not args.page_url:
            owner = os.getenv("GITHUB_REPOSITORY_OWNER", "owner")
            repo = os.getenv("GITHUB_REPOSITORY", "repo/repo").split("/")[-1]
            args.page_url = f"https://{owner}.github.io/{repo}/"
        result = run_digest(page_url=args.page_url)
        print(f"digest_ok md={result['md_path']}")
    elif args.cmd == "pull-feedback":
        count = run_feedback_pull()
        print(f"feedback_rows={count}")


if __name__ == "__main__":
    main()

