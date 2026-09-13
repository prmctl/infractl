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


## URL compatibility

The site uses relative internal URLs, so the same static artifact works at:

```text
http://localhost:8000/
https://prmctl.github.io/infractl/
https://infractl.prmctl.me/
```

No runtime `<base>` element is required.

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

## Nested sidebar navigation

The left navigation is a recursive collapsible tree. Each item can have `children`, and children can have their own `children`, so there is no fixed two-level limit.

A recommended content hierarchy for technology posts is:

```text
docs/
└── labs/
    └── web-servers/
        └── nginx/
            ├── README.md
            ├── architecture.md
            ├── reverse-proxy.md
            ├── tls.md
            └── troubleshooting.md
```

The matching navigation shape in `site/assets/app.js` is:

```js
{
  label: "Web Servers",
  href: "labs/web-servers/",
  children: [
    {
      label: "Nginx",
      href: "labs/web-servers/nginx/",
      children: [
        { label: "Architecture", href: "labs/web-servers/nginx/architecture/" },
        { label: "Reverse Proxy", href: "labs/web-servers/nginx/reverse-proxy/" },
        { label: "TLS", href: "labs/web-servers/nginx/tls/" }
      ]
    }
  ]
}
```

Folders with children are shown as dropdowns. The branch containing the current page opens automatically, and manually opened branches are remembered in the browser.
