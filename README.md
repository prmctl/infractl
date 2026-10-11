# infractl

A straightforward infrastructure knowledge base, published on GitHub Pages using [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/).

## Sections

- Templates
- Laboratories (including field notes and runbooks)
- Common Commands

## Local development

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
mkdocs serve
```

## Publish

1. Push this repository to GitHub (`main` or `master`).
2. Go to **Settings → Pages → Build and deployment** and select **GitHub Actions**.
3. Push a Markdown change; the workflow builds and deploys the site.
4. The site is served at `https://USERNAME.github.io/REPO/` unless a custom domain is configured.

The docs are original Markdown files. No AI-generated filler or fabricated lab results have been added.

GitBook's modern hosted service cannot be directly deployed to GitHub Pages. This uses a maintained static documentation generator instead.
