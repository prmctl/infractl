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

## Dual URL support

The static site is base-path aware and supports both:

```text
https://prmctl.github.io/infractl/
https://infractl.prmctl.me/
```

On `prmctl.github.io`, assets resolve under `/infractl/`. On the custom domain and local preview, assets resolve from `/`.

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
