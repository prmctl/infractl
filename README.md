# infractl

Minimal MkDocs documentation for GitHub Pages.

## Structure

- `docs/commands/` — common commands
- `docs/laboratories/` — labs
- `docs/templates/` — templates

Create any number of nested folders and `.md` files under these directories. The sidebar is generated automatically because `mkdocs.yml` intentionally has no `nav` section. Add an `index.md` to each folder if you want a landing page.

## Local preview

```bash
python -m pip install -r requirements.txt
python -m mkdocs serve
```

## Publish

1. Copy **all files**, including hidden `.github/`, to the repository root. Remove obsolete workflows under `.github/workflows/`.
2. Push to `master` or `main`.
3. In repository Settings → Pages, select **GitHub Actions** as the build source.
4. Check the **Publish documentation** workflow under Actions.

Custom domain `infractl.prmctl.me` is set in `docs/CNAME` and `mkdocs.yml`. In Settings → Pages, configure that same domain and point its DNS CNAME record to `prmctl.github.io`. If you prefer the default GitHub Pages URL, remove `docs/CNAME` and set `site_url` to `https://prmctl.github.io/infractl/`.
