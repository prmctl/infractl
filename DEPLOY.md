# Deploy to GitHub Pages

This repository uses **MkDocs Material**, not the hosted GitBook service.

1. Push the files in this archive to the **root** of `prmctl/infractl` on `master` (or `main`).
2. Remove any old or duplicate Pages workflows that still call `python build.py`.
3. In GitHub repository Settings → Pages → Build and deployment, select **GitHub Actions**.
4. Open Actions → Publish documentation and check the build and deploy jobs.
5. Visit https://prmctl.github.io/infractl/ after a successful deployment.

To test locally:

```sh
python -m pip install -r requirements.txt
python -m mkdocs serve
```

The output directory is `_site`, configured in `mkdocs.yml` and in the Pages workflow. The repository's source templates and labs remain in their original folders; the site is generated from `docs/`.
