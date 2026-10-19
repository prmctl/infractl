#!/usr/bin/env bash
set -euo pipefail
[ "$(id -u)" -eq 0 ] || { echo 'Run as root' >&2; exit 1; }
command -v certbot >/dev/null || { echo 'Install certbot first' >&2; exit 1; }
install -d -m 755 /etc/letsencrypt/renewal-hooks/deploy
install -m 755 "$(dirname "$0")/reload-nginx-after-renewal.sh" /etc/letsencrypt/renewal-hooks/deploy/reload-nginx.sh
echo 'Renewal deploy hook installed.'
