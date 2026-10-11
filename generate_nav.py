"""Generate deterministic MkDocs sidebar from nested Markdown directories."""
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parent
DOCS = ROOT / "docs"
SECTIONS = (("Common Commands", "commands"), ("Laboratories", "laboratories"), ("Templates", "templates"))

def label(name):
    return name.replace("-", " ").replace("_", " ").title()

def walk(folder):
    result = []
    index = folder / "index.md"
    if index.is_file():
        result.append({"Overview": index.relative_to(DOCS).as_posix()})
    for sub in sorted((p for p in folder.iterdir() if p.is_dir() and not p.name.startswith(".")), key=lambda p: p.name.lower()):
        children = walk(sub)
        if children:
            result.append({label(sub.name): children})
    for f in sorted(folder.glob("*.md"), key=lambda p: p.name.lower()):
        if f.name != "index.md":
            result.append({label(f.stem): f.relative_to(DOCS).as_posix()})
    return result

def main():
    cfg = yaml.safe_load((ROOT / "mkdocs.yml").read_text(encoding="utf-8"))
    nav = [{"Home": "index.md"}]
    for title, dirname in SECTIONS:
        folder = DOCS / dirname
        folder.mkdir(parents=True, exist_ok=True)
        if not (folder / "index.md").exists():
            (folder / "index.md").write_text("# " + title + "\n", encoding="utf-8")
        nav.append({title: walk(folder)})
    cfg["nav"] = nav
    output = ROOT / "mkdocs.generated.yml"
    output.write_text(yaml.safe_dump(cfg, allow_unicode=True, sort_keys=False), encoding="utf-8")
    print("Generated sidebar:", [list(item)[0] for item in nav])
    assert len(nav) == 4

if __name__ == "__main__":
    main()
