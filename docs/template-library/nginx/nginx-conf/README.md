# Nginx Company Production Gateway — deployment template

## Scope
Debian/Ubuntu, packaged Nginx >= 1.25.1 (for `http2 on`), systemd, four backend services listening on localhost ports 3001–3004, and `api.example.com`. `app.example.com` and staging are *disabled examples*. This is a starting template, **not** a guarantee of production readiness.

## Included
Permanent HTTP-01 challenge path on port 80, HTTPS port 443 production virtual host, TLS 1.2/1.3, rate limits, connection limits, request size, timeouts, security headers, upstream keepalive, WebSocket, JSON access logs, gzip, static caching example, logrotate example, default HTTP reject, validation and rollout scripts.

## Before installing
1. Change **every** `example.com` domain to real DNS names in site files and scripts. Search: `grep -R 'example.com' .`.
2. Change `127.0.0.1:3001`–`:3004` in upstreams to real backend addresses; make sure services are running. For Docker containers, use reachable container networking, not localhost unless appropriate.
3. Review route prefix behavior: `proxy_pass http://auth_service;` preserves `/auth/` prefix. To strip it, use `proxy_pass http://auth_service/;` intentionally.
4. Check Nginx version (`nginx -v`); this template uses `http2 on` and needs Nginx 1.25.1+. If older, adapt HTTP/2 syntax.
5. **Back up existing configuration**. Installer replaces nginx.conf, conf.d, maps, upstreams, snippets, sites-available and sites-enabled. Do not use installer on a shared server without change review.
6. Check host firewall allows TCP 80 and 443; DNS A/AAAA records point to the server. Do not expose backend ports publicly.
7. Review rate limits against real traffic, especially shared NAT/mobile networks. Auth default 5 requests/minute per IP may be too strict for some routes.

## Deploy (replace domains first)
```bash
sudo apt-get update && sudo apt-get install -y nginx certbot
sudo bash scripts/install.sh
# Ensure DNS is correct and port 80 reachable
sudo certbot certonly --webroot -w /var/www/letsencrypt -d api.example.com
sudo bash scripts/enable-api-https.sh
sudo bash scripts/install-renewal-hook.sh
sudo certbot renew --dry-run
sudo bash scripts/validate.sh
curl -I https://api.example.com/healthz
```
The permanent `/etc/nginx/snippets/letsencrypt.conf` is included by every example HTTP server, so renewal requires no temporary config edits. The hook installer sets up reload after a successful renewal. Check that `certbot.timer` (or the distro equivalent) is enabled; test with `sudo certbot renew --dry-run`.

## Important caveats
- TLS cannot work without a real certificate; the HTTPS virtual host is intentionally **not enabled** by install.sh until cert issuance succeeds.
- `healthz` checks Nginx, not backend health. Protect detailed status endpoints; use separate synthetic checks for each backend.
- HTTP default server rejects unknown Host. HTTPS default rejection is commented out for version/compatibility; enable `ssl_reject_handshake on` after verifying support and testing SNI behavior.
- Only trust forwarded client IP headers when a trusted load balancer/CDN is configured using exact `set_real_ip_from` CIDRs and `real_ip_header`. Never trust arbitrary client-provided X-Forwarded-For.
- Nginx rate limits are per source IP, not per account. Pair with app-level abuse controls, WAF/CDN when appropriate, and proper auth.
- No shared API caching is enabled: do not cache authenticated/payment responses without explicit policy.
- `proxy_next_upstream_tries 1` prevents automatic multiple upstream attempts; ensure payment operations are idempotent at application level.
- HSTS is enabled for the API hostname only (no includeSubDomains); confirm HTTPS availability before public rollout.
- HTTP/3, OCSP, Brotli, active health checks, distributed rate limits and advanced WAF are not included; they depend on modules, topology and requirements.
- The optional logrotate sample may conflict with your distro's existing `/etc/logrotate.d/nginx`; adapt the existing rule rather than installing both.
- Review permissions, SELinux/AppArmor, container networking, DNS, and OS-level file descriptor limits for your host.
- After each change: `sudo nginx -t && sudo systemctl reload nginx`. Validate with integration and load tests, not syntax check alone.

## Layout
`nginx/` mirrors `/etc/nginx/`; `sites-enabled/` is created by installer. Snippets are included only in compatible contexts. `ssl/` is reserved; Let's Encrypt certs are stored under `/etc/letsencrypt/live/`.

## Files changed for permanent ACME Webroot
- `nginx/snippets/letsencrypt.conf` (new): HTTP-01 challenge path
- `nginx/sites-available/00-bootstrap-api.conf`: first-issuance HTTP server
- `nginx/sites-available/production/api.example.com.conf`: permanent challenge on port 80 plus HTTPS 443
- `nginx/sites-available/production/app.example.com.conf`: same pattern for app
- `nginx/sites-available/staging/staging.example.com.conf`: same pattern for staging
- `scripts/enable-api-https.sh`: safer activation with rollback on failure
- `scripts/install-renewal-hook.sh` and `scripts/reload-nginx-after-renewal.sh` (new)

**Critical:** This package contains placeholder domain names and backend IP/ports. Edit them before running the installer. `install.sh` replaces existing Nginx configuration; use a staging VM and review the script first. For HTTP-01, TCP/80 must be publicly reachable and DNS must point to this host. TLS certificate files must exist before enabling the HTTPS site.
