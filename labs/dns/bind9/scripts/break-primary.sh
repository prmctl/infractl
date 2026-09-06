#!/usr/bin/env bash
set -euo pipefail
docker compose stop dns-primary
echo "Primary stopped. Investigate before recovery."
