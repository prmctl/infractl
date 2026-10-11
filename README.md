# infractl

Minimal documentation with **Common Commands**, **Laboratories**, and **Templates**.

## Publish

Push the entire contents of this directory (including `.github/`) to the root of `prmctl/infractl` on `master`. In repository Settings → Pages, select **GitHub Actions**.

## Add content

Add Markdown files or nested directories inside `docs/commands`, `docs/laboratories`, or `docs/templates`. Navigation discovers them automatically. `.pages` files control section names and top-level order.

## Run locally

```bash
python -m pip install -r requirements.txt
python -m mkdocs serve
```

Theme toggle is provided by Material for MkDocs and persists between pages. Custom domain: `infractl.prmctl.me`.
