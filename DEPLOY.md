# Deployment

This repository uses MkDocs Material and GitHub Actions.

1. Place all files in the repository root, including `.github/workflows/pages.yml`.
2. Push to `master` (or `main`).
3. In GitHub, set Settings > Pages > Build and deployment > Source to GitHub Actions.
4. Confirm the `Deploy documentation` workflow has successful build and deploy jobs.

Site URL: https://prmctl.github.io/infractl/

For a custom domain, configure it in GitHub Pages Settings and update `site_url` in `mkdocs.yml`. DNS and custom domain configuration are separate from the build.

To install from this archive: extract it beside your local repository, `cd` into your repository, and run `bash ../install-infractl.sh` (adjust the relative path if necessary).
