
"""Generate a complete MkDocs navigation and folder landing pages."""
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parent
DOCS = ROOT / "docs"
SECTIONS = (("Common Commands", "commands"), ("Laboratories", "laboratories"), ("Templates", "templates"))

def label(value):
    return value.replace("-", " ").replace("_", " ").title()

def walk(folder):
    index = folder / "index.md"
    if not index.exists():
        # Never overwrite authored pages; only create missing landing pages.
        index.write_text("# " + label(folder.name) + "\n\nPages in this section are listed in the sidebar.\n", encoding="utf-8")
    children = [index.relative_to(DOCS).as_posix()]
    for sub in sorted((p for p in folder.iterdir() if p.is_dir() and not p.name.startswith(".")), key=lambda p: p.name.lower()):
        if any(sub.rglob("*.md")):
            children.append({label(sub.name): walk(sub)})
    for page in sorted(folder.glob("*.md"), key=lambda p: p.name.lower()):
        if page.name != "index.md":
            children.append({label(page.stem): page.relative_to(DOCS).as_posix()})
    return children

def main():
    config = yaml.safe_load((ROOT / "mkdocs.yml").read_text(encoding="utf-8"))
    # MkDocs Material's navigation.indexes turns the first index page into
    # the clickable section title (rather than a separate Overview link).
    config["nav"] = [{"Home": "index.md"}]
    for title, directory in SECTIONS:
        folder = DOCS / directory
        folder.mkdir(parents=True, exist_ok=True)
        config["nav"].append({title: walk(folder)})
    output = ROOT / "mkdocs.generated.yml"
    output.write_text(yaml.safe_dump(config, allow_unicode=True, sort_keys=False), encoding="utf-8")
    print("Sidebar sections:", [next(iter(x)) for x in config["nav"]])

if __name__ == "__main__":
    main()
