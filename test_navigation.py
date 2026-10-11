
from pathlib import Path
import yaml
import generate_nav


def main():
    generate_nav.main()

    config = yaml.safe_load(
        Path("mkdocs.generated.yml").read_text(
            encoding="utf-8"
        )
    )

    nav = config["nav"]

    expected = [
        "Home",
        "Common Commands",
        "Laboratories",
        "Templates",
    ]

    actual = [
        next(iter(item))
        for item in nav
    ]

    assert actual == expected, (
        f"Navigation mismatch: {actual}"
    )

    sections = {
        "Common Commands": "commands",
        "Laboratories": "laboratories",
        "Templates": "template-library",
    }

    for title, directory in sections.items():
        section = next(
            item[title]
            for item in nav
            if title in item
        )

        assert section[0] == f"{directory}/index.md"

    print("Navigation checks passed")


if __name__ == "__main__":
    main()
