#!/usr/bin/env bash
set -euo pipefail
docker compose up -d dns-primary dns-secondary client
docker network connect --ip 172.28.0.10 infractl-bind9_labnet infractl-dns-primary 2>/dev/null || true
echo "Recovery attempted. Run make verify."
