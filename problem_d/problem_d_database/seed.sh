#!/usr/bin/env bash
set -euo pipefail

DB_PATH="${1:-$(pwd)/northwind_signal.sqlite}"

sqlite3 "$DB_PATH" < "$(dirname "$0")/schema.sql"
sqlite3 "$DB_PATH" < "$(dirname "$0")/seed.sql"

echo "Seeded $DB_PATH"
