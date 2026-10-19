#!/usr/bin/env bash
set -euo pipefail
[ "$(id -u)" -eq 0 ] || { echo 'Run as root' >&2; exit 1; }
DOMAIN=api.example.com
CERT="/etc/letsencrypt/live/$DOMAIN/fullchain.pem"
KEY="/etc/letsencrypt/live/$DOMAIN/privkey.pem"
BOOT=/etc/nginx/sites-enabled/00-bootstrap-api.conf
ACTIVE=/etc/nginx/sites-enabled/api.example.com.conf
[ -s "$CERT" ] && [ -s "$KEY" ] || { echo 'Certificate/key missing' >&2; exit 1; }
[ ! -e "$ACTIVE" ] && [ ! -L "$ACTIVE" ] || { echo 'HTTPS site already enabled' >&2; exit 1; }
[ -L "$BOOT" ] || { echo 'Expected bootstrap symlink is missing' >&2; exit 1; }
rm "$BOOT"
ln -s ../sites-available/production/api.example.com.conf "$ACTIVE"
if nginx -t; then
    if systemctl reload nginx; then
        echo 'HTTPS enabled; port 80 challenge remains available for renewal.'
        exit 0
    fi
fi
rm -f "$ACTIVE"
ln -s ../sites-available/00-bootstrap-api.conf "$BOOT"
nginx -t || true
systemctl reload nginx || true
echo 'Activation failed; restored HTTP bootstrap. Check Nginx logs.' >&2
exit 1
