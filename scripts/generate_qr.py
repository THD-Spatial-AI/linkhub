#!/usr/bin/env python3
"""
Generate QR codes for all event pages.

Reads every events/*/page.json and writes qr.png and qr.svg.

Default output: source event folder (e.g. events/egu-2026/qr.png) — suitable for
committing to the repository so presenters can download directly from GitHub.

Pass --site-dir _site to write into the built site instead (used by deploy.yml).

Both files use the navy colour (#1B3A6B) matching the landing page design.
Error correction is set to HIGH (H) so the QR code remains scannable even
if part of it is obscured or damaged on a printed poster.

Usage:
    # Write to source event folders (default):
    python3 scripts/generate_qr.py \\
        --site-url https://thd-spatial-ai.github.io/linkhub

    # Write into _site/ for deployment:
    python3 scripts/generate_qr.py \\
        --site-url https://thd-spatial-ai.github.io/linkhub \\
        --site-dir _site
"""

import argparse
import json
from io import BytesIO
from pathlib import Path

try:
    import qrcode
    import qrcode.constants
    import qrcode.image.svg
except ImportError:
    raise SystemExit(
        "Missing dependency.\n"
        "Install with:  pip install \"qrcode[pil]\"\n"
        "           or: pip install -r requirements.txt"
    )

ROOT       = Path(__file__).resolve().parent.parent
EVENTS_DIR = ROOT / "events"

_COLOR = "#1B3A6B"  # navy — matches the landing page palette


def _make_png(url: str, path: Path) -> None:
    qr = qrcode.QRCode(
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=15,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color=_COLOR, back_color="white")
    img.save(path)


def _make_svg(url: str, path: Path) -> None:
    qr = qrcode.QRCode(
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        image_factory=qrcode.image.svg.SvgPathImage,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image()
    buf = BytesIO()
    img.save(buf)
    svg = buf.getvalue().decode("utf-8")
    svg = svg.replace('fill="#000000"', f'fill="{_COLOR}"')
    path.write_text(svg, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate QR codes for all event pages.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--site-url",
        default="https://thd-spatial-ai.github.io/linkhub",
        metavar="URL",
        help="GitHub Pages base URL without a trailing slash.",
    )
    parser.add_argument(
        "--site-dir",
        default=None,
        metavar="DIR",
        help="Write QR codes to DIR/{slug}/ instead of the source event folder.",
    )
    args = parser.parse_args()
    site_url = args.site_url.rstrip("/")
    site_dir = Path(args.site_dir) if args.site_dir else None

    if site_dir and not site_dir.exists():
        raise SystemExit(
            f"Error: {site_dir}/ does not exist.\n"
            "Run generate.py first:  python3 scripts/generate.py"
        )

    count = 0
    for page_json in sorted(EVENTS_DIR.glob("*/page.json")):
        slug = page_json.parent.name
        if slug.startswith(("_", ".")):
            continue

        url = f"{site_url}/{slug}/"
        if site_dir:
            out_dir = site_dir / slug
            out_dir.mkdir(exist_ok=True)
        else:
            out_dir = page_json.parent  # source event folder

        _make_png(url, out_dir / "qr.png")
        _make_svg(url, out_dir / "qr.svg")
        print(f"  {out_dir / 'qr.png'}  {out_dir / 'qr.svg'}  →  {url}")
        count += 1

    if count == 0:
        print("No event pages found.")
    else:
        print(f"\nDone. {count} QR code(s) generated.")


if __name__ == "__main__":
    main()
