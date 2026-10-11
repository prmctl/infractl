
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parent
DOCS = ROOT / "docs"

SECTIONS = (
    ("Common Commands", "commands"),
    ("Laboratories", "laboratories"),
    ("Templates", "template-library"),
)


def label(name):
    return name.replace("-", " ").replace("_", " ").title()


def walk(folder):
    index = folder / "index.md"

    if not index.exists():
        index.write_text(
            f"# {label(folder.name)}\n\n",
            encoding="utf-8",
        )

    children = [
        index.relative_to(DOCS).as_posix()
    ]

    directories = sorted(
        (
            p for p in folder.iterdir()
            if p.is_dir() and not p.name.startswith(".")
        ),
        key=lambda p: p.name.lower(),
    )

    for directory in directories:
        children.append({
            label(directory.name): walk(directory)
        })

    pages = sorted(
        folder.glob("*.md"),
        key=lambda p: p.name.lower(),
    )

    for page in pages:
        if page.name != "index.md":
            children.append({
                label(page.stem):
                page.relative_to(DOCS).as_posix()
            })

    return children


def main():
    config_path = ROOT / "mkdocs.yml"

    config = yaml.safe_load(
        config_path.read_text(encoding="utf-8")
    )

    config["nav"] = [
        {"Home": "index.md"}
    ]

    for title, directory in SECTIONS:
        folder = DOCS / directory

        folder.mkdir(
            parents=True,
            exist_ok=True,
        )

        config["nav"].append({
            title: walk(folder)
        })

    output = ROOT / "mkdocs.generated.yml"

    output.write_text(
        yaml.safe_dump(
            config,
            allow_unicode=True,
            sort_keys=False,
        ),
        encoding="utf-8",
    )

    print("Generated navigation:")
    for item in config["nav"]:
        print(" -", next(iter(item)))


if __name__ == "__main__":
    main()
