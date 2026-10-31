#!/bin/sh
# inainte_de_commit.sh — regula 15.1 (31.10.2026): înainte de orice commit se rulează verificatorul de design și pytest-ul țintit pe fișierele
# atinse (de la ultima publicare, plus ce e necomis); poarta (`poarta_lot.sh`) pornește numai dacă amândouă sunt verzi. Nu primește fișiere în argv
# (lista atinselor vine numai din git). Ieșire: 0 = ambele verzi (se poate comite și porni poarta), 1 = cel puțin una roșie.
ROOT=$(git rev-parse --show-toplevel) || exit 1
cd "$ROOT" || exit 1
[ -n "$1" ] && { echo "[inainte de commit] REFUZ: scriptul nu are argumente (primit: $1)."; exit 1; }
PY=./venv/bin/python
[ -x "$PY" ] || PY=python3
J=${POARTA_JURNALE:-/tmp}
"$PY" verificator_conformitate.py > "$J/inainte_verificator.log" 2>&1
TOT=$(grep -i "TOTAL" "$J/inainte_verificator.log")
echo "[inainte de commit] verificator de design: $TOT"
case "$TOT" in *"TOTAL: 0"*) ;; *) echo "[inainte de commit] ROSU: verificator (vezi $J/inainte_verificator.log)"; exit 1 ;; esac
"$PY" - "$J/inainte_pytest_fisiere.txt" <<'PYE' || exit 1
import os, subprocess, sys
sys.path.insert(0, os.path.join(os.getcwd(), "scripts"))
import perimetru as P, poarta_scurta as S, poarta_sare
def git(*a): return subprocess.run(["git", *a], capture_output=True, text=True).stdout.split("\n")
baza = subprocess.run(["git", "merge-base", "HEAD", "main"], capture_output=True, text=True).stdout.strip() or "HEAD"
atinse = sorted({f for f in git("diff", "--name-only", baza) + git("ls-files", "-o", "--exclude-standard") if f})
teste = S.selectie(atinse, "direct")[0]
teste = [t for t in teste if os.path.isfile(t) and not poarta_sare.sare_fisier(os.path.join(P.RAD, t))]
open(sys.argv[1], "w").write("\n".join(teste) + "\n")
print("[inainte de commit] %d fisiere atinse, %d fisiere pytest" % (len(atinse), len(teste)))
PYE
if [ -s "$J/inainte_pytest_fisiere.txt" ] && [ "$(grep -c . "$J/inainte_pytest_fisiere.txt")" -gt 0 ]; then
    xargs "$PY" -m pytest -q -n "${POARTA_PROCESE:-3}" --dist loadfile < "$J/inainte_pytest_fisiere.txt" > "$J/inainte_pytest.log" 2>&1
    RC=$?
    tail -1 "$J/inainte_pytest.log"
    [ "$RC" -ne 0 ] && { echo "[inainte de commit] ROSU: pytest pe fisierele atinse (vezi $J/inainte_pytest.log)"; exit 1; }
fi
echo "[inainte de commit] VERDE: verificator si pytest tintit; se poate comite si porni poarta."
