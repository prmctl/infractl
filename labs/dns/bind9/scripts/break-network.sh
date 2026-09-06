#!/usr/bin/env bash
set -euo pipefail
docker network disconnect infractl-bind9_labnet infractl-dns-primary || true
echo "Primary is still alive but disconnected from the lab network."
