from __future__ import annotations

import json
import re
import shutil
from html import escape
from pathlib import Path

try:
    import mistune
except ImportError as exc:
    raise SystemExit("Missing dependency: mistune. Run: pip install -r requirements.txt") from exc

ROOT = Path(__file__).resolve().parent
DOCS = ROOT / "docs"
SITE = ROOT / "site"
ASSETS = SITE / "assets"

SECTION_META = {
    "labs": ("Labs · Break & Learn", "blue"),
    "templates": ("Templates · Copy & Use", "green"),
    "runbooks": ("Runbooks · Incident Guides", "purple"),
    "field-notes": ("Field Notes · Real World", "purple"),
    "tools": ("Tools · Utilities", "cyan"),
}

ICON_MAP = {
    "labs": "labs", "templates": "template", "runbooks": "runbook",
    "field-notes": "note", "tools": "tools", "dns": "dns",
    "web-servers": "server", "databases": "db", "kubernetes": "k8s",
    "networking": "net", "storage": "storage", "observability": "observe",
    "linux-system": "terminal", "system": "terminal", "security": "security",
}

ACRONYMS = {"dns": "DNS", "nginx": "Nginx", "bind9": "BIND9", "coredns": "CoreDNS", "tls": "TLS", "api": "API", "ssh": "SSH"}


def pretty_name(name: str) -> str:
    key = name.lower().replace("_", "-")
    if key in ACRONYMS:
        return ACRONYMS[key]
    return " ".join(ACRONYMS.get(p, p.capitalize()) for p in re.split(r"[-_]+", name) if p)


def first_heading(path: Path) -> str | None:
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return None
    m = re.search(r"^#\s+(.+?)\s*$", text, re.M)
    return m.group(1).strip() if m else None


def href_for_md(md: Path) -> str:
    rel = md.relative_to(DOCS)
    if rel.name.lower() == "readme.md":
        parent = rel.parent.as_posix()
        return "" if parent == "." else f"{parent}/"
    return f"{rel.with_suffix('').as_posix()}/"


def file_node(md: Path, section_color: str) -> dict:
    slug = md.stem
    return {
        "label": first_heading(md) or pretty_name(slug),
        "href": href_for_md(md),
        "icon": ICON_MAP.get(slug.lower(), "note"),
        "color": section_color,
    }


def dir_node(directory: Path, section_color: str) -> dict:
    readme = directory / "README.md"
    label = pretty_name(directory.name)

    node = {
        "label": label,
        "href": href_for_md(readme) if readme.exists() else f"{directory.relative_to(DOCS).as_posix()}/",
        "icon": ICON_MAP.get(directory.name.lower(), "tools"),
        "color": section_color,
    }

    children: list[dict] = []
    # Directories first, then Markdown posts. README is represented by the folder link itself.
    for child_dir in sorted((p for p in directory.iterdir() if p.is_dir() and not p.name.startswith(".")), key=lambda p: p.name.lower()):
        children.append(dir_node(child_dir, section_color))
    for md in sorted((p for p in directory.glob("*.md") if p.name.lower() != "readme.md"), key=lambda p: p.name.lower()):
        children.append(file_node(md, section_color))
    if children:
        node["children"] = children
    return node


def build_navigation() -> list[dict]:
    nav: list[dict] = [
        {"label": "Getting Started", "href": "", "icon": "tools", "color": "cyan"}
    ]
    for section, (group, color) in SECTION_META.items():
        d = DOCS / section
        if not d.exists():
            continue
        items: list[dict] = []
        readme = d / "README.md"
        if readme.exists():
            items.append({"label": "Overview" if section != "field-notes" else "Latest Posts", "href": href_for_md(readme), "icon": ICON_MAP.get(section, "note"), "color": color})
        for child_dir in sorted((p for p in d.iterdir() if p.is_dir() and not p.name.startswith(".")), key=lambda p: p.name.lower()):
            items.append(dir_node(child_dir, color))
        for md in sorted((p for p in d.glob("*.md") if p.name.lower() != "readme.md"), key=lambda p: p.name.lower()):
            items.append(file_node(md, color))
        nav.append({"group": group, "items": items})
    return nav


def depth_prefix(href: str) -> str:
    depth = len([p for p in href.strip("/").split("/") if p])
    return "../" * depth


def breadcrumb(href: str) -> str:
    parts = [pretty_name(p) for p in href.strip("/").split("/") if p]
    return "  ›  ".join(parts)


def render_markdown(md: Path) -> str:
    text = md.read_text(encoding="utf-8")
    renderer = mistune.HTMLRenderer(escape=False)
    markdown = mistune.create_markdown(renderer=renderer, plugins=["strikethrough", "table", "task_lists", "url"])
    return markdown(text)


def page_shell(title: str, href: str, body: str) -> str:
    p = depth_prefix(href)
    crumb = breadcrumb(href)
    return f'''<!doctype html><html lang="en" data-theme="dark"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{escape(title)} · infractl</title><link rel="icon" href="{p}assets/logo.svg"><link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500;600;700&display=swap" rel="stylesheet"><link rel="stylesheet" href="{p}assets/style.css"></head><body>
<header class="top">
<a class="brand" href="{p}"><img src="{p}assets/logo.svg"><div>infractl<small>by prmctl</small></div></a>
<nav class="nav">
<a href="{p}labs/"><svg class="icon-svg blue"><use href="{p}assets/icons.svg#labs"></use></svg><span>Labs<em>Break & Learn</em></span></a>
<a href="{p}templates/"><svg class="icon-svg green"><use href="{p}assets/icons.svg#template"></use></svg><span>Templates<em>Production Ready</em></span></a>
<a href="{p}runbooks/"><svg class="icon-svg purple"><use href="{p}assets/icons.svg#runbook"></use></svg><span>Runbooks<em>Incident Guides</em></span></a>
<a href="{p}field-notes/"><svg class="icon-svg purple"><use href="{p}assets/icons.svg#note"></use></svg><span>Field Notes<em>Real World</em></span></a>
<a href="{p}tools/"><svg class="icon-svg cyan"><use href="{p}assets/icons.svg#tools"></use></svg><span>Tools<em>Utilities</em></span></a>
</nav>
<div class="toptools"><button id="menu-toggle" class="iconbtn mobile">☰</button><div class="search">⌕ <input placeholder="Search documentation..."></div><button id="theme-toggle" class="iconbtn" aria-label="Toggle theme">◐</button><a class="iconbtn" href="https://github.com/prmctl/infractl" aria-label="GitHub"><svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor"><path d="M12 .7a11.3 11.3 0 0 0-3.6 22c.6.1.8-.3.8-.6v-2.2c-3.3.7-4-1.4-4-1.4-.5-1.4-1.3-1.8-1.3-1.8-1.1-.8.1-.8.1-.8 1.2.1 1.9 1.3 1.9 1.3 1.1 1.9 2.9 1.4 3.6 1.1.1-.8.4-1.4.8-1.7-2.7-.3-5.5-1.4-5.5-6a4.7 4.7 0 0 1 1.2-3.3 4.4 4.4 0 0 1 .1-3.2s1-.3 3.5 1.3a12 12 0 0 1 6.3 0c2.4-1.6 3.5-1.3 3.5-1.3a4.4 4.4 0 0 1 .1 3.2 4.7 4.7 0 0 1 1.2 3.3c0 4.7-2.8 5.7-5.5 6 .4.4.8 1.1.8 2.2v3.2c0 .3.2.7.8.6A11.3 11.3 0 0 0 12 .7z"/></svg></a></div>
</header>
<div class="layout"><aside class="sidebar"></aside><main class="main"><article class="doc"><div class="crumb">{escape(crumb)}</div>{body}</article></main>
<aside class="rightbar"><div class="box"><div class="rbrand"><img src="{p}assets/logo.svg"><div><h3>infractl</h3><p style="margin:0">by prmctl</p></div></div><p>Open source knowledge base for infrastructure engineers.</p><ul class="list"><li>● Hands-on labs</li><li>● Production templates</li><li>● Incident runbooks</li><li>● Real-world experience</li></ul><a class="star" href="https://github.com/prmctl/infractl">★ Star on GitHub</a></div></aside></div>
<script src="{p}assets/navigation.js"></script><script src="{p}assets/app.js"></script></body></html>'''


def output_path(md: Path) -> Path:
    rel = md.relative_to(DOCS)
    if rel.name.lower() == "readme.md":
        return SITE / rel.parent / "index.html"
    return SITE / rel.with_suffix("") / "index.html"


def ensure_home_scripts() -> None:
    index = SITE / "index.html"
    if not index.exists():
        return
    text = index.read_text(encoding="utf-8")
    # Existing home keeps its custom layout, but its sidebar is replaced dynamically.
    if 'assets/navigation.js' not in text:
        text = text.replace('<script src="assets/app.js"></script>', '<script src="assets/navigation.js"></script><script src="assets/app.js"></script>')
    index.write_text(text, encoding="utf-8")


def main() -> None:
    nav = build_navigation()
    ASSETS.mkdir(parents=True, exist_ok=True)
    (ASSETS / "navigation.js").write_text("window.INFRACTL_NAV = " + json.dumps(nav, ensure_ascii=False, indent=2) + ";\n", encoding="utf-8")

    for md in DOCS.rglob("*.md"):
        if md.name == "SUMMARY.md" or md == DOCS / "README.md":
            continue
        href = href_for_md(md)
        title = first_heading(md) or pretty_name(md.parent.name if md.name.lower() == "readme.md" else md.stem)
        out = output_path(md)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(page_shell(title, href, render_markdown(md)), encoding="utf-8")

    ensure_home_scripts()
    print(f"infractl: built {sum(1 for p in DOCS.rglob('*.md') if p.name != 'SUMMARY.md') - 1} documentation pages")


if __name__ == "__main__":
    main()
