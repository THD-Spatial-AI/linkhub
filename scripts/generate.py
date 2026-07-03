#!/usr/bin/env python3
"""
Generate landing pages from page.json configuration files.

Usage:
    python3 scripts/generate.py

Output:
    _site/             — directory ready for GitHub Pages deployment
    _site/index.html   — hub page listing all events
    _site/{slug}/      — one subdirectory per page.json found under events/
"""

import json
import re
import shutil
from html import escape
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "_site"
EVENTS_DIR = ROOT / "events"

_LOGO_DIR = ROOT / "docs" / "assets" / "gh-logo"


def _clean_svg(filename: str) -> str:
    """Load an SVG and strip Inkscape/Sodipodi metadata for safe inline embedding."""
    text = (_LOGO_DIR / filename).read_text(encoding="utf-8")
    text = re.sub(r'<\?xml[^?]*\?>\n?', '', text)
    text = re.sub(r'\s*<sodipodi:namedview\b[^>]*/>\n?', '', text, flags=re.DOTALL)
    text = re.sub(r'\s+xmlns:(inkscape|sodipodi|svg)="[^"]*"', '', text)
    text = re.sub(r'\s+inkscape:[a-zA-Z:-]+=(?:"[^"]*")', '', text)
    text = re.sub(r'\s+sodipodi:[a-zA-Z:-]+=(?:"[^"]*")', '', text)
    # Remove explicit dimensions from root <svg> so CSS can control sizing
    def _strip_dims(m: re.Match) -> str:
        s = re.sub(r'\s+width="[^"]*"', '', m.group())
        return re.sub(r'\s+height="[^"]*"', '', s)
    text = re.sub(r'<svg\b[^>]*>', _strip_dims, text, count=1)
    return text.strip()


_LOGO_LIGHT = _clean_svg("spatialai-lockup-blue.svg")
_LOGO_DARK  = _clean_svg("spatialai-lockup-blue-dark.svg")
_LOGO_HTML  = (
    '    <div class="org-logo">\n'
    f'      <div class="logo-light">{_LOGO_LIGHT}</div>\n'
    f'      <div class="logo-dark">{_LOGO_DARK}</div>\n'
    '    </div>\n'
)

# ── Icon library ──────────────────────────────────────────────────────────────
# Inner SVG path data for 24×24 stroke icons (Feather icon style).
# The outer <svg> wrapper and stroke styles are added by icon_svg().
ICONS: dict[str, str] = {
    "globe": (
        '<circle cx="12" cy="12" r="9"/>'
        '<path d="M12 3a14.5 14.5 0 0 1 0 18M12 3a14.5 14.5 0 0 0 0 18M3 12h18"/>'
    ),
    "code": (
        '<polyline points="16 18 22 12 16 6"/>'
        '<polyline points="8 6 2 12 8 18"/>'
    ),
    "table": (
        '<rect x="3" y="3" width="18" height="18" rx="2"/>'
        '<path d="M3 9h18M3 15h18M9 3v18"/>'
    ),
    "document": (
        '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>'
        '<polyline points="14 2 14 8 20 8"/>'
    ),
    "github": (
        '<path d="M9 19c-5 1.5-5-2.5-7-3m14 6v-3.87a3.37 3.37 0 0 0-.94-2.61'
        'c3.14-.35 6.44-1.54 6.44-7A5.44 5.44 0 0 0 20 4.77 5.07 5.07 0 0 0 19.91 1'
        'S18.73.65 16 2.48a13.38 13.38 0 0 0-7 0C6.27.65 5.09 1 5.09 1'
        'A5.07 5.07 0 0 0 5 4.77a5.44 5.44 0 0 0-1.5 3.78c0 5.42 3.3 6.61 6.44 7'
        'A3.37 3.37 0 0 0 9 18.13V22"/>'
    ),
    "data": (
        '<ellipse cx="12" cy="5" rx="9" ry="3"/>'
        '<path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"/>'
        '<path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"/>'
    ),
    "tool": (
        '<path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77'
        'a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91'
        'a6 6 0 0 1 7.94-7.94l-3.76 3.76z"/>'
    ),
    "link": (
        '<path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/>'
        '<path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/>'
    ),
    "envelope": (
        '<rect x="2" y="4" width="20" height="16" rx="2"/>'
        '<path d="m22 6-10 7L2 6"/>'
    ),
    "linkedin": (
        '<path d="M16 8a6 6 0 0 1 6 6v7h-4v-7a2 2 0 0 0-2-2 2 2 0 0 0-2 2v7h-4v-7a6 6 0 0 1 6-6z"/>'
        '<rect x="2" y="9" width="4" height="12"/>'
        '<circle cx="4" cy="4" r="2"/>'
    ),
    "phone": (
        '<path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6'
        ' 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72c.13.96.36 1.9.7 2.81'
        'a2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45'
        'c.91.34 1.85.57 2.81.7A2 2 0 0 1 22 16.92z"/>'
    ),
    "orcid": (
        '<circle cx="12" cy="12" r="9"/>'
        '<line x1="8.5" y1="8" x2="8.5" y2="16"/>'
        '<circle cx="8.5" cy="6" r="0.6" fill="currentColor" stroke="none"/>'
        '<path d="M12 8h1.5a4 4 0 0 1 0 8H12z"/>'
    ),
    "gitlab": (
        '<path d="M12 21 3 9l3-7h2l1 4 3 3 3-3 1-4h2l3 7z"/>'
    ),
    "paper": (
        '<path d="M12 20h9"/>'
        '<path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"/>'
    ),
    "map": (
        '<polygon points="1 6 1 22 8 18 16 22 23 18 23 2 16 6 8 2 1 6"/>'
        '<line x1="8" y1="2" x2="8" y2="18"/>'
        '<line x1="16" y1="6" x2="16" y2="22"/>'
    ),
}


def icon_svg(name: str) -> str:
    paths = ICONS.get(name, ICONS["link"])
    return f'<svg viewBox="0 0 24 24" aria-hidden="true">{paths}</svg>'


# ── Shared stylesheet ─────────────────────────────────────────────────────────
# Embedded verbatim in every generated page. No external resources.
CSS = """\
    :root {
      --navy:         #1B3A6B;
      --amber:        #F59E0B;
      --bg:           #f0f4f8;
      --surface:      #ffffff;
      --border:       #d1dce8;
      --text:         #1B3A6B;
      --text-muted:   #4a6080;
      --shadow:       0 2px 8px rgba(27,58,107,0.08);
      --shadow-hover: 0 6px 20px rgba(27,58,107,0.16);
      --radius:       12px;
    }
    @media (prefers-color-scheme: dark) {
      :root {
        --bg:           #0b1628;
        --surface:      #132040;
        --border:       #1e3358;
        --text:         #e8eef7;
        --text-muted:   #7fa0c8;
        --shadow:       0 2px 8px rgba(0,0,0,0.3);
        --shadow-hover: 0 6px 20px rgba(0,0,0,0.45);
      }
    }
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
                   Helvetica, Arial, sans-serif;
      background: var(--bg);
      color: var(--text);
      min-height: 100dvh;
      display: flex;
      flex-direction: column;
      align-items: center;
      padding: 2.5rem 1rem 2rem;
    }
    main {
      width: 100%;
      max-width: 560px;
      display: flex;
      flex-direction: column;
      gap: 1rem;
      flex: 1;
    }
    header { margin-bottom: 0.75rem; }
    .badge {
      display: inline-block;
      font-size: 0.72rem;
      font-weight: 600;
      letter-spacing: 0.08em;
      text-transform: uppercase;
      color: var(--amber);
      background: color-mix(in srgb, var(--amber) 12%, transparent);
      border: 1px solid color-mix(in srgb, var(--amber) 30%, transparent);
      border-radius: 20px;
      padding: 0.25em 0.75em;
      margin-bottom: 0.9rem;
    }
    h1 {
      font-size: clamp(1.45rem, 5vw, 1.85rem);
      font-weight: 700;
      line-height: 1.25;
      color: var(--text);
      margin-bottom: 0.5rem;
    }
    h1 .x { color: var(--amber); }
    .subtitle { font-size: 0.93rem; color: var(--text-muted); line-height: 1.55; max-width: 46ch; }
    .card {
      display: flex;
      align-items: center;
      gap: 1rem;
      background: var(--surface);
      border: 1.5px solid var(--border);
      border-radius: var(--radius);
      padding: 1.1rem 1.25rem;
      text-decoration: none;
      color: inherit;
      box-shadow: var(--shadow);
      transition: box-shadow 0.18s ease, border-color 0.18s ease, transform 0.18s ease;
    }
    .card:hover, .card:focus-visible {
      border-color: var(--amber);
      box-shadow: var(--shadow-hover);
      transform: translateY(-2px);
      outline: none;
    }
    .card:focus-visible { outline: 2px solid var(--amber); outline-offset: 2px; }
    .card-icon {
      flex-shrink: 0;
      width: 44px;
      height: 44px;
      border-radius: 10px;
      background: color-mix(in srgb, var(--navy) 8%, transparent);
      display: flex;
      align-items: center;
      justify-content: center;
    }
    @media (prefers-color-scheme: dark) {
      .card-icon { background: color-mix(in srgb, var(--amber) 10%, transparent); }
    }
    .card-icon svg {
      width: 22px;
      height: 22px;
      stroke: var(--navy);
      fill: none;
      stroke-width: 1.75;
      stroke-linecap: round;
      stroke-linejoin: round;
    }
    @media (prefers-color-scheme: dark) { .card-icon svg { stroke: var(--amber); } }
    .card-body { flex: 1; min-width: 0; }
    .card-title { font-size: 0.97rem; font-weight: 600; color: var(--text); margin-bottom: 0.2rem; }
    .card-desc { font-size: 0.82rem; color: var(--text-muted); line-height: 1.45; }
    .card-arrow {
      flex-shrink: 0;
      color: var(--border);
      font-size: 1.2rem;
      line-height: 1;
      transition: color 0.18s ease, transform 0.18s ease;
    }
    .card:hover .card-arrow,
    .card:focus-visible .card-arrow { color: var(--amber); transform: translateX(3px); }
    .section-label {
      font-size: 0.72rem;
      font-weight: 600;
      letter-spacing: 0.09em;
      text-transform: uppercase;
      color: var(--text-muted);
      padding: 0.5rem 0 0.1rem;
    }
    .contact-row {
      display: flex;
      flex-wrap: wrap;
      gap: 0.6rem;
      margin-bottom: 0.25rem;
    }
    .contact-chip {
      display: flex;
      align-items: center;
      justify-content: center;
      width: 44px;
      height: 44px;
      border-radius: 50%;
      background: var(--surface);
      border: 1.5px solid var(--border);
      box-shadow: var(--shadow);
      text-decoration: none;
      transition: box-shadow 0.18s ease, border-color 0.18s ease, transform 0.18s ease;
    }
    .contact-chip:hover, .contact-chip:focus-visible {
      border-color: var(--amber);
      box-shadow: var(--shadow-hover);
      transform: translateY(-2px);
      outline: none;
    }
    .contact-chip svg {
      width: 20px;
      height: 20px;
      stroke: var(--navy);
      fill: none;
      stroke-width: 1.75;
      stroke-linecap: round;
      stroke-linejoin: round;
    }
    @media (prefers-color-scheme: dark) { .contact-chip svg { stroke: var(--amber); } }
    .pub-card { align-items: flex-start; }
    .pub-title-link { text-decoration: none; color: inherit; }
    .pub-title-link:hover .card-title { color: var(--amber); }
    .pub-abstract {
      font-size: 0.82rem;
      color: var(--text-muted);
      line-height: 1.5;
      margin-top: 0.4rem;
    }
    .pub-doi {
      display: inline-flex;
      align-items: center;
      gap: 0.3rem;
      font-size: 0.72rem;
      font-weight: 600;
      letter-spacing: 0.03em;
      color: var(--amber);
      text-decoration: none;
      margin-top: 0.6rem;
    }
    .pub-doi:hover { text-decoration: underline; }
    footer {
      width: 100%;
      max-width: 560px;
      margin-top: 2.25rem;
      border-top: 1px solid var(--border);
      padding-top: 1.25rem;
      display: flex;
      flex-direction: column;
      gap: 0.25rem;
    }
    .footer-label {
      font-size: 0.7rem;
      font-weight: 600;
      letter-spacing: 0.08em;
      text-transform: uppercase;
      color: var(--amber);
      margin-bottom: 0.35rem;
    }
    .institution { font-size: 0.82rem; color: var(--text-muted); line-height: 1.45; }
    .institution strong { color: var(--text); font-weight: 600; }
    .org-logo { margin-bottom: 1.25rem; }
    .org-logo svg { height: 44px; width: auto; display: block; }
    .logo-dark { display: none; }
    @media (prefers-color-scheme: dark) {
      .logo-light { display: none; }
      .logo-dark { display: block; }
    }
"""

# ── HTML helpers ──────────────────────────────────────────────────────────────

def _title_html(raw: str) -> str:
    """Wrap × with an amber-coloured span for visual accent."""
    return escape(raw).replace("×", '<span class="x">×</span>')


def _card_html(link: dict) -> str:
    url   = escape(link["url"])
    title = escape(link["title"])
    desc  = escape(link.get("description", ""))
    icon  = icon_svg(link.get("icon", "link"))
    return (
        f'    <a class="card" href="{url}" target="_blank" rel="noopener noreferrer">\n'
        f'      <div class="card-icon">{icon}</div>\n'
        f'      <div class="card-body">\n'
        f'        <div class="card-title">{title}</div>\n'
        f'        <div class="card-desc">{desc}</div>\n'
        f'      </div>\n'
        f'      <span class="card-arrow" aria-hidden="true">&#x203A;</span>\n'
        f'    </a>\n'
    )


_REPO_ICON_HOSTS = {
    "github.com": "github",
    "gitlab.com": "gitlab",
}


def _detect_repo_icon(url: str) -> str:
    """Infer a source-code hosting icon from the URL's hostname."""
    host = urlparse(url).netloc.lower()
    for suffix, name in _REPO_ICON_HOSTS.items():
        if host == suffix or host.endswith("." + suffix):
            return name
    return "link"


def _contact_chip_html(link: dict) -> str:
    url   = escape(link["url"])
    title = escape(link.get("title", ""))
    icon  = icon_svg(link.get("icon", "link"))
    return (
        f'    <a class="contact-chip" href="{url}" target="_blank" rel="noopener noreferrer" '
        f'title="{title}" aria-label="{title}">\n'
        f'      {icon}\n'
        f'    </a>\n'
    )


def _publication_card_html(link: dict) -> str:
    url      = escape(link["url"])
    title    = escape(link["title"])
    desc     = escape(link.get("description", ""))
    abstract = escape(link.get("abstract", ""))
    doi      = link.get("doi", "").strip()
    icon     = icon_svg(link.get("icon", "paper"))

    abstract_html = f'        <p class="pub-abstract">{abstract}</p>\n' if abstract else ""
    doi_html = ""
    if doi:
        doi_url = escape(f"https://doi.org/{doi}")
        doi_html = (
            f'        <a class="pub-doi" href="{doi_url}" target="_blank" rel="noopener noreferrer">'
            f'DOI: {escape(doi)}</a>\n'
        )

    return (
        f'    <div class="card pub-card">\n'
        f'      <div class="card-icon">{icon}</div>\n'
        f'      <div class="card-body">\n'
        f'        <a class="pub-title-link" href="{url}" target="_blank" rel="noopener noreferrer">\n'
        f'          <div class="card-title">{title}</div>\n'
        f'        </a>\n'
        f'        <div class="card-desc">{desc}</div>\n'
        + abstract_html
        + doi_html +
        f'      </div>\n'
        f'    </div>\n'
    )


def _institution_html(inst: dict) -> str:
    name = escape(inst.get("name", ""))
    unit = escape(inst.get("unit", ""))
    return f'    <p class="institution"><strong>{name}</strong><br>{unit}</p>\n'


def _page_shell(title_tag: str, og_title: str, og_desc: str, body: str) -> str:
    """Wrap body content in the full HTML shell with embedded CSS."""
    head = (
        "<!DOCTYPE html>\n"
        '<html lang="en">\n'
        "<head>\n"
        '  <meta charset="UTF-8">\n'
        '  <meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
        f'  <meta name="description" content="{og_desc}">\n'
        f'  <meta property="og:title" content="{og_title}">\n'
        f'  <meta property="og:description" content="{og_desc}">\n'
        '  <meta property="og:type" content="website">\n'
        f'  <title>{title_tag}</title>\n'
        "  <style>\n"
    )
    return head + CSS + "  </style>\n</head>\n<body>\n" + body + "</body>\n</html>\n"


# ── Page renderers ─────────────────────────────────────────────────────────────

def render_landing_page(config: dict, slug: str) -> str:
    event    = config.get("event", "")
    raw_title = config.get("title", "Untitled")
    subtitle = config.get("subtitle", "")
    institutions = config.get("institutions", [])

    # Group links by category, preserving insertion order
    categories: dict[str, list] = {}
    for link in config.get("links", []):
        categories.setdefault(link.get("category", "Links"), []).append(link)

    cards = ""
    for cat, cat_links in categories.items():
        cards += f'    <div class="section-label">{escape(cat)}</div>\n'

        contact_links = [l for l in cat_links if l.get("type") == "contact"]
        other_links   = [l for l in cat_links if l.get("type") != "contact"]

        if contact_links:
            cards += '    <div class="contact-row">\n'
            for link in contact_links:
                cards += _contact_chip_html(link)
            cards += '    </div>\n'

        for link in other_links:
            link_type = link.get("type")
            if link_type == "publication":
                cards += _publication_card_html(link)
            elif link_type == "repo" and "icon" not in link:
                cards += _card_html({**link, "icon": _detect_repo_icon(link["url"])})
            else:
                cards += _card_html(link)

    inst_html = "".join(_institution_html(i) for i in institutions)

    body = (
        "  <main>\n"
        "    <header>\n"
        + _LOGO_HTML +
        f'      <div class="badge">{escape(event)}</div>\n'
        f'      <h1>{_title_html(raw_title)}</h1>\n'
        f'      <p class="subtitle">{escape(subtitle)}</p>\n'
        "    </header>\n"
        + cards +
        "  </main>\n"
        "  <footer>\n"
        '    <div class="footer-label">Research institutions</div>\n'
        + inst_html +
        "  </footer>\n"
    )

    og_title  = escape(f"{raw_title} — {event}")
    og_desc   = escape(subtitle)
    title_tag = f"{escape(raw_title)} — {escape(event)}"
    return _page_shell(title_tag, og_title, og_desc, body)


def render_hub(pages: list[tuple[str, dict]]) -> str:
    cards = ""
    for slug, config in pages:
        event    = config.get("event", slug)
        raw_title = config.get("title", "Untitled")
        subtitle = config.get("subtitle", "")
        short    = subtitle[:90] + ("…" if len(subtitle) > 90 else "")
        desc_html = (
            f"<strong>{escape(event)}</strong> — {escape(short)}"
            if short else escape(event)
        )
        cards += (
            f'    <a class="card" href="{slug}/">\n'
            f'      <div class="card-icon">{icon_svg("link")}</div>\n'
            f'      <div class="card-body">\n'
            f'        <div class="card-title">{_title_html(raw_title)}</div>\n'
            f'        <div class="card-desc">{desc_html}</div>\n'
            f'      </div>\n'
            f'      <span class="card-arrow" aria-hidden="true">&#x203A;</span>\n'
            f'    </a>\n'
        )

    body = (
        "  <main>\n"
        "    <header>\n"
        + _LOGO_HTML +
        '      <div class="badge">THD Spatial AI</div>\n'
        '      <h1>Link Hub</h1>\n'
        '      <p class="subtitle">Landing pages for conferences, events, and research projects.</p>\n'
        "    </header>\n"
        '    <div class="section-label">All pages</div>\n'
        + cards +
        "  </main>\n"
        "  <footer>\n"
        '    <div class="footer-label">Research group</div>\n'
        '    <p class="institution"><strong>BigGeoData &amp; Spatial AI</strong>'
        "<br>Technische Hochschule Deggendorf (THD)</p>\n"
        "  </footer>\n"
    )

    og = "THD Spatial AI — Link Hub"
    og_desc = "Landing pages for conferences, events, and research projects."
    return _page_shell(escape(og), escape(og), escape(og_desc), body)


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    if SITE.exists():
        shutil.rmtree(SITE)
    SITE.mkdir()

    pages: list[tuple[str, dict]] = []

    for page_json in sorted(EVENTS_DIR.glob("*/page.json")):
        slug = page_json.parent.name
        if slug.startswith(("_", ".")):
            continue

        with open(page_json, encoding="utf-8") as f:
            config = json.load(f)

        pages.append((slug, config))
        out_dir = SITE / slug
        out_dir.mkdir()
        (out_dir / "index.html").write_text(render_landing_page(config, slug), encoding="utf-8")
        print(f"  generated  {slug}/index.html")

    (SITE / "index.html").write_text(render_hub(pages), encoding="utf-8")
    print(f"  generated  index.html  ({len(pages)} page(s) listed)")


if __name__ == "__main__":
    print(f"Output → {SITE}")
    main()
    print("Done.")
