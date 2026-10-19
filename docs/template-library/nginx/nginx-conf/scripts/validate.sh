#!/usr/bin/env bash
set -euo pipefail
nginx -t
nginx -T >/dev/null
printf 'Nginx configuration syntax OK. Test routes, certificates, and backend reachability separately.\n'
