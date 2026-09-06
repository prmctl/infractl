# infractl

> Infrastructure for a more resilient tomorrow.

`infractl` is an open-source practical infrastructure knowledge base by `prmctl`.

It combines:

- **Labs** — build, break, troubleshoot, recover.
- **Templates** — reusable production-minded configuration.
- **Runbooks** — incident procedures for real operations.
- **Field Notes** — engineering notes and lessons.
- **Tools** — small operational helpers.

## Local preview

Use the included server so the correct web root is always used:

```bash
python3 serve.py
```

or:

```bash
make serve
```

Open:

```text
http://localhost:8000
```

## GitHub Pages + custom domain

Target:

```text
https://infractl.prmctl.me
```

Push the repository to:

```text
https://github.com/prmctl/infractl
```

The included GitHub Action deploys from `master`.

GitHub:

```text
Settings -> Pages -> Source -> GitHub Actions
Settings -> Pages -> Custom domain -> infractl.prmctl.me
```

Cloudflare:

```text
Type: CNAME
Name: infractl
Target: prmctl.github.io
Proxy: DNS only
```

No VPS or separate web server is required.
