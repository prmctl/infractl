# Deployment

1. Extract the ZIP and copy **all contents**, including `.github`, to the repository root (not a nested folder).
2. Remove old files in `.github/workflows/` from the repository; only `pages.yml` should remain.
3. Commit and push to `master`.
4. In GitHub **Settings → Pages**, select **GitHub Actions** as Source.
5. Check the **Actions** tab. Both `build` and `deploy` must pass.
6. Visit https://prmctl.github.io/infractl/.

The build uses `python -m mkdocs build --clean` and uploads `site/`. It never invokes `build.py`.
