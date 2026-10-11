# infractl · GitBook-style Infrastructure Handbook

A beautiful, fast, static documentation site built from Markdown, with automatic GitHub Pages deployment. The three primary collections are **Templates**, **Laboratories**, and **Common Commands**. Existing field notes, tools, runnable labs, and runbooks are preserved.

## Run locally

```bash
python3 -m pip install -r requirements.txt
python3 build.py
python3 serve.py
```

Open `http://localhost:8000`.

## Publish on GitHub Pages

1. Create a GitHub repository (e.g. `infractl`) and push **the contents of this directory** to its `main` or `master` branch.
2. Go to **Settings → Pages → Build and deployment** and choose **GitHub Actions**.
3. Push a change or manually run **Actions → Deploy infractl → Run workflow**.
4. Open `https://YOUR-USERNAME.github.io/REPOSITORY/` (or your configured custom domain).

The workflow builds Markdown into static pages and deploys `site/`. No GitBook paid account or backend is needed; this is a **GitBook-inspired site**, not the proprietary GitBook platform.

## Add a page

Create `docs/commands/linux/my-command.md` with a `# Title` heading, then commit and push. The sidebar is generated automatically by `build.py`.

## Content locations

- `docs/templates/` — reusable examples
- `docs/lab/` — guided labs
- `docs/commands/` — operational commands
- `docs/field-notes/` — experiences
- `labs/` — runnable exercises
- `runbooks/` — incident guides
- `site/assets/` — theme, JavaScript, icons

> Check examples for credentials or private infrastructure data before making the repository public.
