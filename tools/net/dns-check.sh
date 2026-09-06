#!/usr/bin/env bash
set -euo pipefail
name="${1:-example.com}"
dig "$name"
dig +trace "$name"
