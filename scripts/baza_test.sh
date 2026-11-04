#!/bin/sh
# baza_test.sh — snapshot și restaurare ale bazei de TEST (comanda 16.0, pct.2b + completarea 2, pct.G).
#   baza_test.sh salveaza     pg_dump -Fc al bazei iconta_test în ~/backups_test/iconta_test.dump
#   baza_test.sh restaureaza  pg_restore --clean --if-exists în iconta_test
# REFUZ MECANIC (pct.G): numele bazei se citește din conexiunea efectivă (SELECT current_database()); orice nume diferit de iconta_test = refuz,
# înainte de orice scriere. Conexiunea vine numai din ~/.iconta/test.env (rolul de test nu are CONNECT pe producție).
# NEFĂCUT încă (așteaptă decizia pe copia producției): directoarele cabinetului de test, golirea cozilor, lucrătorul de recalculare (723).
set -u
ACTIUNE="${1:-}"
case "$ACTIUNE" in salveaza|restaureaza) ;; *) echo "[baza_test] folosire: baza_test.sh salveaza|restaureaza"; exit 2 ;; esac
ENV_FILE="${BAZA_TEST_ENV:-$HOME/.iconta/test.env}"
set -a; . "$ENV_FILE"; set +a
export PGPASSWORD="$DB_PASSWORD"
BAZA=$(psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -Atc "SELECT current_database()" 2>/dev/null)
if [ "$BAZA" != "iconta_test" ]; then
    echo "[baza_test] REFUZ: baza conexiunii este '${BAZA:-necunoscută (conectare eșuată)}', nu iconta_test."
    exit 1
fi
DIR="${BAZA_TEST_DIR:-$HOME/backups_test}"
mkdir -p "$DIR"
T0=$(date +%s)
if [ "$ACTIUNE" = salveaza ]; then
    pg_dump -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d iconta_test -Fc -f "$DIR/iconta_test.dump" || exit 1
    echo "[baza_test] salvat $DIR/iconta_test.dump sha256=$(sha256sum "$DIR/iconta_test.dump" | cut -d' ' -f1) in $(( $(date +%s) - T0 ))s"
else
    [ -f "$DIR/iconta_test.dump" ] || { echo "[baza_test] REFUZ: lipsește snapshotul $DIR/iconta_test.dump"; exit 1; }
    pg_restore -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d iconta_test --clean --if-exists --no-owner "$DIR/iconta_test.dump" || exit 1
    echo "[baza_test] restaurat în $(( $(date +%s) - T0 ))s"
fi
