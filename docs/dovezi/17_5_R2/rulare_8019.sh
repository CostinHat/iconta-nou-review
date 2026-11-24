#!/bin/sh
# 17.5-R2 — o rulare de probă pe iconta_test:8019 sub lacătul oficial (scripts/lacat_test.py), cu portul eliberat înainte și, la cerere,
# baza restaurată înainte și după (scripts/baza_test.sh restaureaza, cu 8019 oprit). Rulatorul e cel nativ: scripts/e2e_poarta.py
# (indexul git al arborelui din care se cheamă). Uz:
#   sh docs/dovezi/17_5_R2/rulare_8019.sh [--restaureaza] <iesire> [argumente e2e_poarta.py...]
# Ieșirea: codul lui e2e_poarta.py (pytest); 90 = lacăt refuzat; 91 = restaurare eșuată.
set -u
REST=0
[ "${1:-}" = "--restaureaza" ] && { REST=1; shift; }
IES="$1"; shift
RAD=$(git rev-parse --show-toplevel)
cd "$RAD" || exit 92
PY=./venv/bin/python
$PY scripts/lacat_test.py ia $$ rulare_8019_17_5_R2 || exit 90
export LACAT_TEST_PID="${LACAT_TEST_PID:-$$}"
mkdir -p "$IES"
{ echo "# inceput $(date -Iseconds) commit $(git rev-parse HEAD) index $(git write-tree)"; } > "$IES/rulare.meta"
$PY scripts/verificator_design.py opreste > "$IES/opreste_inainte.out" 2>&1
if [ "$REST" = 1 ]; then
    sh scripts/baza_test.sh restaureaza > "$IES/restaurare_inainte.out" 2>&1 || { echo "restaurare inainte esuata" >> "$IES/rulare.meta"; exit 91; }
fi
RC=0
$PY scripts/e2e_poarta.py "$@" "$IES/capturi" > "$IES/e2e.out" 2>&1 || RC=$?
echo "$RC" > "$IES/rc.txt"
$PY scripts/verificator_design.py opreste > "$IES/opreste_dupa.out" 2>&1
if [ "$REST" = 1 ]; then
    sh scripts/baza_test.sh restaureaza > "$IES/restaurare_dupa.out" 2>&1 || echo "restaurare dupa esuata" >> "$IES/rulare.meta"
fi
echo "# sfarsit $(date -Iseconds) rc=$RC" >> "$IES/rulare.meta"
exit "$RC"
