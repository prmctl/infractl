#!/usr/bin/env bash
set -euo pipefail
[ "$(id -u)" -eq 0 ] || { echo 'Run as root'; exit 1; }
command -v nginx >/dev/null || { echo 'Install nginx first'; exit 1; }
[ -d /etc/nginx ] || { echo '/etc/nginx missing'; exit 1; }
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SRC="$SCRIPT_DIR/../nginx"
BACKUP="/root/nginx-backup-$(date +%Y%m%d-%H%M%S)"
cp -a /etc/nginx "$BACKUP"
echo "Backup: $BACKUP"
# Replace managed config; leave installed dynamic module files intact.
install -d /etc/nginx/{conf.d,maps,upstreams,snippets,sites-available,sites-enabled,ssl} /var/www/letsencrypt
cp "$SRC/nginx.conf" /etc/nginx/nginx.conf
for d in conf.d maps upstreams snippets sites-available; do
 rm -rf "/etc/nginx/$d"
 cp -a "$SRC/$d" "/etc/nginx/$d"
done
find /etc/nginx/sites-enabled -mindepth 1 -maxdepth 1 -exec rm -f {} +
ln -s ../sites-available/00-default-reject.conf /etc/nginx/sites-enabled/00-default-reject.conf
ln -s ../sites-available/00-bootstrap-api.conf /etc/nginx/sites-enabled/00-bootstrap-api.conf
if ! nginx -t; then
 echo "nginx -t failed. Restore from $BACKUP before reloading." >&2
 exit 1
fi
systemctl reload nginx || systemctl restart nginx
echo 'HTTP bootstrap active. Read README before activating HTTPS.'
