#!/bin/sh
# baza_test.sh — snapshot și restaurare ale bazei de TEST (comanda 16.0, pct.2b + completarea 2, pct.G).
#   baza_test.sh salveaza     pg_dump -Fc al bazei iconta_test în ~/backups_test/iconta_test.dump
#   baza_test.sh restaureaza  pg_restore --clean --if-exists în iconta_test
# REFUZ MECANIC (pct.G): numele bazei se citește din conexiunea efectivă (SELECT current_database()); orice nume diferit de iconta_test = refuz,
# înainte de orice scriere. Conexiunea vine numai din ~/.iconta/test.env (rolul de test nu are CONNECT pe producție).
#   baza_test.sh stare        amprenta stării: hash pe date (toate schemele), valorile secvențelor, inventarul fișierelor generate (pct.C)
# Restaurarea: baza, apoi golirea directorului generat al serverului 8019 (E2E_TEMP, implicit /tmp/e2e_poarta) și a cozilor, apoi lucrătorul de
# recalculare sincron (core.firma_rezumat, 723). Detalii în scripts/baza_test_README.md.
set -u
ACTIUNE="${1:-}"
case "$ACTIUNE" in salveaza|restaureaza|stare|verifica) ;; *) echo "[baza_test] folosire: baza_test.sh salveaza|restaureaza|stare|verifica"; exit 2 ;; esac
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
TEMP="${E2E_TEMP:-/tmp/e2e_poarta}"
Q() { psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d iconta_test -Atq -c "$1"; }
if [ "$ACTIUNE" = verifica ]; then
    # precondițiile scenariului F017 (comanda 16.0, pct.2d + N), pe firma F1 (schema copiei: tenant_9049); rulează după fiecare restaurare și după testul 10 al lanțului
    SCH="${F1_SCHEMA:-tenant_9049}"; RC=0
    chk() { R=$(Q "$2"); if [ "$R" = "$3" ]; then echo "[verifica] OK    $1 ($R)"; else echo "[verifica] PICĂ  $1: găsit '$R', așteptat '$3'"; RC=1; fi; }
    chk "F1A nr. 15, 500,00 lei, 24.10.2026, neîncasată (fără chitanță anulabilă pe ea)" "SELECT count(*) FROM $SCH.facturi f WHERE f.numar='F1A15' AND f.total=500 AND f.data_emitere='2026-10-24' AND f.tert_cui='410001005' AND NOT EXISTS (SELECT 1 FROM $SCH.chitante c WHERE c.factura_id=f.id AND NOT c.anulata)" 1
    chk "Client Test SRL (410001005) sold preluat 2000,00 la 31.08.2026" "SELECT count(*) FROM $SCH.solduri_parteneri WHERE cui='410001005' AND sold_debitor=2000 AND data_referinta='2026-08-31'" 1
    chk "F1 fără serie de chitanță" "SELECT coalesce(nullif(serie_chitanta,''),'-') FROM $SCH.firma_profil LIMIT 1" "-"
    echo "[verifica] luna 10/2026: $(Q "SELECT coalesce(string_agg(DISTINCT 'blocată '||an||'/'||luna, ','), 'nicio perioadă blocată') FROM $SCH.perioade_blocate WHERE an=2026 AND luna IN (10,11)" 2>&1 | head -1)"
    exit $RC
fi
if [ "$ACTIUNE" = stare ]; then
    # hash pe date, independent de ordinea fizică a rândurilor: pe fiecare tabel, count + md5 al rândurilor sortate. Excluse: tabelele de bătăi/metrici,
    # care se schimbă singure la fiecare recalculare (cron_batai, metrici_sanatate) — vezi README
    psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d iconta_test -At -q <<'SQL' | sort
SELECT format($f$SELECT %L, count(*), coalesce(md5(string_agg(x::text, '|' ORDER BY x::text)), '') FROM %I.%I x$f$, table_schema || '.' || table_name, table_schema, table_name)
FROM information_schema.tables
WHERE table_type = 'BASE TABLE' AND (table_schema = 'public' OR table_schema LIKE 'tenant\_%')
  AND table_name NOT IN ('cron_batai', 'metrici_sanatate')
ORDER BY 1 \gexec
SQL
    psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d iconta_test -Atc "select schemaname||'.'||sequencename||'='||coalesce(last_value::text,'null') from pg_sequences where schemaname='public' or schemaname like 'tenant_%' order by 1" | sha256sum | sed 's/^/secvente /; s/ -$//'
    echo "fisiere $( [ -d "$TEMP" ] && find "$TEMP" -type f | sort | sha256sum | cut -d' ' -f1 || echo absent )"
    exit 0
fi
if [ "$ACTIUNE" = salveaza ]; then
    pg_dump -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d iconta_test -Fc -f "$DIR/iconta_test.dump" || exit 1
    echo "[baza_test] salvat $DIR/iconta_test.dump sha256=$(sha256sum "$DIR/iconta_test.dump" | cut -d' ' -f1) in $(( $(date +%s) - T0 ))s"
else
    [ -f "$DIR/iconta_test.dump" ] || { echo "[baza_test] REFUZ: lipsește snapshotul $DIR/iconta_test.dump"; exit 1; }
    # conexiunile deschise la iconta_test (serverul de lucru 8019, lucrători) se termină întâi; serverul 8019 își reface pool-ul singur la prima cerere (README)
    Q "SELECT count(pg_terminate_backend(pid)) FROM pg_stat_activity WHERE datname='iconta_test' AND pid <> pg_backend_pid()" > /dev/null
    pg_restore -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d iconta_test --clean --if-exists --no-owner "$DIR/iconta_test.dump" || exit 1
    # directorul generat al serverului de lucru + cozile, apoi recalcularea sincronă a rezumatelor firmelor (723)
    rm -rf "$TEMP"
    psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d iconta_test -q -c "TRUNCATE public.declaratii_coada, public.declaratii_in_asteptare, public.inregistrari_in_asteptare, public.login_esecuri, public.reset_parola_token, public.tokene_activare, public.telefon_coduri" || exit 1
    ( cd "$(dirname "$0")/.." && "${PYTHON:-./venv/bin/python}" -m core.firma_rezumat > "${TMPDIR:-/tmp}/baza_test_recalcul.log" 2>&1 ) || echo "[baza_test] AVERTISMENT: recalcularea a ieșit cu eroare (vezi ${TMPDIR:-/tmp}/baza_test_recalcul.log)"
    echo "[baza_test] restaurat în $(( $(date +%s) - T0 ))s"
fi
