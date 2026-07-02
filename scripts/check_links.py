#!/usr/bin/env python3
"""
Check all links in page.json files and verify published GitHub Pages are accessible.

For each event slug:
  - Fetches the published GitHub Pages URL and verifies it returns HTML content.
  - Fetches every URL listed in the links array and checks for HTTP 200.

Broken links are printed and summarised. The script always exits 0 so it never
blocks the deploy workflow — issues are visible as workflow output only.

Usage:
    python3 scripts/check_links.py
"""

import json
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

SITE_URL = "https://thd-spatial-ai.github.io/linkhub"
ROOT = Path(__file__).resolve().parent.parent
EVENTS_DIR = ROOT / "events"

_HEADERS = {"User-Agent": "LinkHub-LinkChecker/1.0"}
_TIMEOUT = 15


def _fetch(url: str) -> tuple[int, str]:
    """Return (status_code, content_type). On error return (0, error_message)."""
    try:
        req = urllib.request.Request(url, headers=_HEADERS)
        with urllib.request.urlopen(req, timeout=_TIMEOUT) as resp:
            content_type = resp.headers.get("Content-Type", "")
            return resp.status, content_type
    except urllib.error.HTTPError as e:
        return e.code, ""
    except Exception as e:
        return 0, str(e)


def check_url(url: str, label: str, require_html: bool = False) -> bool:
    status, content_type = _fetch(url)
    if status == 200:
        if require_html and "text/html" not in content_type:
            print(f"  WARN  {label}: responded 200 but content-type is '{content_type}'")
            print(f"        {url}")
            return False
        print(f"  OK    {label}")
        return True
    elif status == 0:
        print(f"  FAIL  {label}: connection error — {content_type}")
    else:
        print(f"  FAIL  {label}: HTTP {status}")
    print(f"        {url}")
    return False


def main() -> None:
    issues: list[str] = []

    for page_json in sorted(EVENTS_DIR.glob("*/page.json")):
        slug = page_json.parent.name
        if slug.startswith(("_", ".")):
            continue

        with open(page_json, encoding="utf-8") as f:
            config = json.load(f)

        print(f"\n[{slug}]")

        page_url = f"{SITE_URL}/{slug}/"
        if not check_url(page_url, f"GitHub Pages: {page_url}", require_html=True):
            issues.append(f"{slug}: published page not accessible — {page_url}")

        for link in config.get("links", []):
            url = link.get("url", "").strip()
            title = link.get("title", url)
            if not url:
                continue
            time.sleep(0.3)  # avoid hammering external servers
            if not check_url(url, title):
                issues.append(f"{slug}/{title} — {url}")

    print(f"\n{'=' * 60}")
    if issues:
        print(f"BROKEN OR INACCESSIBLE LINKS ({len(issues)} issue(s)):")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("All links OK.")

    sys.exit(0)


if __name__ == "__main__":
    main()
