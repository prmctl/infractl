#!/usr/bin/env bash
set -euo pipefail
docker compose ps
docker compose exec -T client dig @172.28.0.10 infractl.test SOA +short
docker compose exec -T client dig @172.28.0.11 infractl.test SOA +short
