#!/bin/sh
# porneste_8019.sh — singura cale de pornire a serverului de lucru (port 8019), comanda 16.0 pct.2b. Mediul serverului de lucru = ~/.iconta/test.env
# (DATABASE_URL / DB_NAME ale bazei de TEST). REFUZ dacă baza din mediu sau baza conexiunii efective nu e `iconta_test`: verificarea e aici, nu în codul aplicației.
ROOT=$(git rev-parse --show-toplevel) || exit 1
cd "$ROOT" || exit 1
ENV_FILE="${BAZA_TEST_ENV:-$HOME/.iconta/test.env}"
set -a; . "$ENV_FILE"; set +a
[ "${DB_NAME:-}" = "iconta_test" ] || { echo "[porneste_8019] REFUZ: DB_NAME din $ENV_FILE este '${DB_NAME:-}', nu iconta_test."; exit 1; }
BAZA=$(PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -Atc "SELECT current_database()" 2>/dev/null)
[ "$BAZA" = "iconta_test" ] || { echo "[porneste_8019] REFUZ: baza conexiunii efective este '${BAZA:-necunoscută}', nu iconta_test."; exit 1; }
PY=./venv/bin/python; [ -x "$PY" ] || PY=python3
exec "$PY" scripts/verificator_design.py porneste
