from pathlib import Path
root = Path(__file__).resolve().parent
required = [
    "site/index.html",
    "site/assets/style.css",
    "site/assets/app.js",
    "site/assets/navigation.js",
    "site/assets/logo.svg",
    "site/CNAME",
    ".github/workflows/pages.yml",
    "labs/dns/bind9/docker-compose.yml",
    "templates/web-servers/nginx/nginx.conf",
    "runbooks/dns/dns-resolution-failure.md",
    "site/labs/web-servers/nginx/index.html",
    "site/labs/web-servers/nginx/architecture/index.html",
]
for rel in required:
    p = root / rel
    assert p.exists(), f"missing: {rel}"
assert (root / "site/CNAME").read_text().strip() == "infractl.prmctl.me"
nav = (root / "site/assets/navigation.js").read_text(encoding="utf-8")
assert 'labs/web-servers/nginx/' in nav
assert 'labs/web-servers/nginx/architecture/' in nav
print("infractl: OK")
