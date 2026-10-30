#!/bin/sh
# poarta_completa.sh — RULAREA COMPLETĂ (comanda 15.G, 30.10.2026): tot pytest + toată plasa e2e, FĂRĂ marcajul de sărire
# (POARTA_SARE=0: rulează și testele din scripts/poarta_sare.txt / poarta_forma.txt), informativ, fără să scrie vreun verdict.
# Pornește NUMAI dacă există ~/ghid_incoming/cheie_poarta_completa_<lot>.txt, creată de arhitect printr-o comandă (o singură dată pe
# lot, înainte de ultima publicare). Argument: <lot>. Șterge cheia la pornire, scrie rezultatul în
# ~/ghid_incoming/poarta_completa_<lot>.txt, refuză orice pornire fără cheie. Code NU o rulează în timpul comenzilor și NU creează cheia.
LOT="$1"
DIR=${GHID_INCOMING:-$HOME/ghid_incoming}
if [ -z "$LOT" ]; then echo "[poarta completa] REFUZ: lipseste lotul (sh scripts/poarta_completa.sh <lot>)."; exit 1; fi
CHEIE="$DIR/cheie_poarta_completa_$LOT.txt"
if [ ! -f "$CHEIE" ]; then
    echo "[poarta completa] REFUZ: nu exista $CHEIE — cheia o creeaza numai comanda arhitectului."
    exit 1
fi
rm -f "$CHEIE"
ROOT=$(git rev-parse --show-toplevel) || exit 1
cd "$ROOT" || exit 1
PY=./venv/bin/python
[ -x "$PY" ] || PY=python3
REZ="$DIR/poarta_completa_$LOT.txt"
export POARTA_SARE=0
J=${POARTA_JURNALE:-/tmp}
T0=$(date +%s)
{
    echo "poarta completa, lotul $LOT, commit $(git rev-parse HEAD), $(date -Is), POARTA_SARE=0"
    "$PY" -m pytest -q -n "${POARTA_PROCESE:-3}" --dist loadfile > "$J/completa_pytest.log" 2>&1
    echo "pytest exit $? · $(tail -1 "$J/completa_pytest.log") · $(( $(date +%s) - T0 ))s"
    grep -E "^(FAILED|ERROR) " "$J/completa_pytest.log" | head -200
    T1=$(date +%s)
    "$PY" scripts/e2e_poarta.py "$J/completa_e2e_capturi" > "$J/completa_e2e.log" 2>&1
    echo "plasa e2e exit $? · $(tail -1 "$J/completa_e2e.log") · $(( $(date +%s) - T1 ))s"
    grep -E "^(FAILED|ERROR) " "$J/completa_e2e.log" | head -200
    echo "total $(( $(date +%s) - T0 ))s — informativ, nu blocheaza nimic"
} > "$REZ" 2>&1
cat "$REZ"
exit 0
