#!/usr/bin/env bash
set -euo pipefail

python scripts/db_sync.py "$1"
