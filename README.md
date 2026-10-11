# infractl

Three sections: **Common Commands**, **Laboratories**, **Templates**.

Add Markdown files in arbitrarily nested folders inside `docs/commands`, `docs/laboratories`, or `docs/templates`. Sidebar navigation is regenerated automatically during each deployment.

## Local preview

```bash
python -m pip install -r requirements.txt
python generate_nav.py
python -m mkdocs serve -f mkdocs.generated.yml
```

## GitHub Pages

Push all files, including `.github/workflows/pages.yml`, to `master`. Set **Settings → Pages → Source: GitHub Actions**.

The custom domain is `infractl.prmctl.me`. The theme supports dark and light modes.

Deployment note: the workflow no longer assumes a particular HTML output path for each section; MkDocs is the source of truth.
