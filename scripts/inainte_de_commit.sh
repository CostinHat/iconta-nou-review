#!/bin/sh
# inainte_de_commit.sh — hook-ul pre-commit, partea rapidă (comanda 15.1-E7, pct.4): verificatorul de design, sintaxa fișierelor atinse și testul
# registrului de deficiențe; în total sub 2 minute. Pytest-ul țintit și plasa e2e rulează o singură dată, în poarta de publicare (`poarta_lot.sh`):
# o poartă per lot, nu una per commit (E5 a plătit 7 commituri × ~18 min). Nu primește argumente (lista atinselor vine numai din git).
# Ieșire: 0 = verde (se poate comite), 1 = roșu.
ROOT=$(git rev-parse --show-toplevel) || exit 1
cd "$ROOT" || exit 1
[ -n "$1" ] && { echo "[inainte de commit] REFUZ: scriptul nu are argumente (primit: $1)."; exit 1; }
PY=./venv/bin/python
[ -x "$PY" ] || PY=python3
J=${POARTA_JURNALE:-/tmp}
T0=$(date +%s)
# 1. sintaxa fișierelor atinse (în index): JS cu `node --check` (module), Python cu py_compile
git diff --cached --name-only --diff-filter=ACM > "$J/inainte_atinse.txt"
for f in $(grep -E '\.js$' "$J/inainte_atinse.txt"); do
    cp "$f" "$J/inainte_sintaxa.mjs" && node --check "$J/inainte_sintaxa.mjs" > "$J/inainte_sintaxa.log" 2>&1 || { cat "$J/inainte_sintaxa.log"; echo "[inainte de commit] ROSU: sintaxa $f"; exit 1; }
done
for f in $(grep -E '\.py$' "$J/inainte_atinse.txt"); do
    "$PY" -m py_compile "$f" || { echo "[inainte de commit] ROSU: sintaxa $f"; exit 1; }
done
echo "[inainte de commit] sintaxa: $(grep -cE '\.(js|py)$' "$J/inainte_atinse.txt") fisiere"
# 2. testul registrului de deficiențe
"$PY" -m pytest -q core/test_deficiente.py > "$J/inainte_registru.log" 2>&1 || { tail -15 "$J/inainte_registru.log"; echo "[inainte de commit] ROSU: registrul de deficiente (vezi $J/inainte_registru.log)"; exit 1; }
echo "[inainte de commit] registrul: $(tail -1 "$J/inainte_registru.log")"
# 3. verificatorul de design
"$PY" verificator_conformitate.py > "$J/inainte_verificator.log" 2>&1
TOT=$(grep -i "TOTAL" "$J/inainte_verificator.log")
echo "[inainte de commit] verificator de design: $TOT"
case "$TOT" in *"TOTAL: 0"*) ;; *) echo "[inainte de commit] ROSU: verificator (vezi $J/inainte_verificator.log)"; exit 1 ;; esac
echo "[inainte de commit] VERDE in $(( $(date +%s) - T0 )) s: sintaxa, registrul si verificatorul de design; pytest tintit si plasa e2e ruleaza in poarta."
