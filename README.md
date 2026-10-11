# infractl

Personal infrastructure documentation. Published at https://prmctl.github.io/infractl/.

## Local preview

```bash
python -m pip install -r requirements.txt
python -m mkdocs serve
```

## Deployment

Push the contents of this directory to the repository root on `master` or `main`.
Set **Settings → Pages → Build and deployment → Source** to **GitHub Actions**.

The workflow builds the `docs/` directory with MkDocs and deploys `site/`.
