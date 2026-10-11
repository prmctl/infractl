# Deploy to GitHub Pages

This archive contains the **entire repository content**. Extract it and copy all files, including the hidden `.github` directory, to the **root** of `prmctl/infractl` (not into a nested folder).

1. Replace the old repository files with these files. **Remove old `.github/workflows/*.yml` files** so only `.github/workflows/pages.yml` remains.
2. Push to `master` (or `main`).
3. On GitHub, open **Settings → Pages → Build and deployment → Source: GitHub Actions**.
4. Check **Actions → Deploy documentation to GitHub Pages** for a green build and deploy.
5. Open https://prmctl.github.io/infractl/

The workflow installs `requirements.txt`, runs `python -m mkdocs build --clean`, uploads `_site`, then deploys to Pages. It does not call `build.py`.

To preview locally after installing dependencies: `python -m mkdocs serve`.
