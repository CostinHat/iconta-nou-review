#!/bin/sh
# poarta_lot.sh — POARTA LOTULUI, la inchiderea lui, inaintea publicarii pe productie: rularea COMPLETA (implicit) sau cea COMPUSA
# (`--compus`), dupa o rulare completa rosie.
#
# [15.10.2026, comanda Costin, verbatim in DECIZII „Poarta o dată pe lot”] „Poarta completă: o singură dată pe lot, la închiderea
# lotului, înainte de publicarea pe producție.” Intre comenzi: numai `scripts/poarta_scurta.py`.
# [23.10.2026, CLAUDE.md §5; DECIZII 23.10.2026 „Comanda 12.1”] „La închiderea lotului, poarta completă rulează o singură dată
# (scripts/poarta_lot.sh). Un test care a trecut deja pe exact același commit nu se mai rulează a doua oară. Dacă poarta pică: se repară
# cauza, apoi se rulează testele căzute și tot ce depinde de reparație. Poarta completă se reia numai dacă reparația a atins piese
# folosite în mai multe locuri sau dacă perimetrul ei nu e sigur. Verdictul pentru commitul reparat se compune din rularea completă
# anterioară plus rerularea țintită.”
#
# RULAREA COMPLETA (fara argumente): pe ramura lotului (worktree), cu arborele CURAT (HEAD = commitul lotului; pytest citeste arborele,
# deci verdictul e despre commit), ruleaza `scripts/githooks/poarta-suita` (prospetime, pytest, verificator, cifre F1–F5, plasa e2e —
# toate, si dupa una rosie; inregistrarea in `<git-common-dir>/poarta_rulari/<sha>.json`) si scrie verdictul in
# `<git-common-dir>/poarta_verdicte.log`:   VERDE|ROSU <sha complet> <ramura> <data>
# RULAREA COMPUSA (`--compus`): X = ultima rulare COMPLETA ROSIE de pe ramura (randul cu patru campuri); `scripts/poarta_scurta.py
# --compus=X` reruleaza testele cazute in X + perimetrul reparatiei (`git diff X`), e2e-ul cazut + cel derivat, prospetimea, verificatorul
# si cifrele F1–F5, sau REFUZA (cod 2, niciun verdict) cand compunerea nu e sigura — atunci se ruleaza poarta completa. Verdictul:
#                                    VERDE|ROSU <sha complet> <ramura> <data> compus:<X>
# `scripts/githooks/reference-transaction` muta `main` numai la un SHA cu `VERDE <sha>` aici (complet sau compus; CLAUDE.md §6).
# REFUZA, in ambele moduri: pe `main` / fara ramura; arbore murdar (modificari sau fisiere noi); un SHA deja VERDE (nimic de aflat); un
# SHA deja ROSU (regula 3d, comanda Costin 11.2, 22.10.2026: pe rosu se repara codul — commit nou — si se ruleaza din nou, pana la verde;
# fara limita de rulari). Compusul, in plus: fara rulare completa ROSIE pe ramura. Completa: ~70 de minute, in fundal.
# Gard: core/test_poarta_lot.py (depozit temporar) + core/test_poarta_ordine.py (singurul care cheama `poarta-suita`).
MOD=completa
case "$1" in
    "") ;;
    --compus) MOD=compus ;;
    *) echo "[poarta lot] REFUZ: argument necunoscut ${1} (singurul admis: --compus)."; exit 1 ;;
esac
ROOT=$(git rev-parse --show-toplevel) || exit 1
cd "$ROOT" || exit 1
COMUN=$(git rev-parse --path-format=absolute --git-common-dir) || exit 1
JV="$COMUN/poarta_verdicte.log"
RAM=$(git symbolic-ref --short HEAD 2>/dev/null)
if [ -z "$RAM" ] || [ "$RAM" = "main" ]; then
    echo "[poarta lot] REFUZ: poarta lotului ruleaza pe ramura lotului, nu pe main / HEAD detasat (acum: ${RAM:-detasat})."
    exit 1
fi
MURDAR=$(git status --porcelain --untracked-files=normal)
if [ -n "$MURDAR" ]; then
    echo "[poarta lot] REFUZ: arborele nu e curat — poarta judeca COMMITUL lotului; comite tot ce intra in lot, intai:"
    echo "$MURDAR" | head -20 | sed 's/^/    /'
    exit 1
fi
SHA=$(git rev-parse HEAD)
if grep -q "^VERDE $SHA " "$JV" 2>/dev/null; then
    echo "[poarta lot] REFUZ: $SHA are deja poarta VERDE — o a doua rulare pe acelasi commit nu afla nimic nou."
    exit 1
fi
if grep -q "^ROSU $SHA " "$JV" 2>/dev/null; then
    echo "[poarta lot] REFUZ: $SHA are deja poarta ROSIE — regula 3d (comanda Costin 11.2): pe rosu se REPARA CODUL (commit nou) si se ruleaza din nou; aceeasi rulare pe acelasi commit nu repara nimic (si ar trece un test instabil pe noroc)."
    exit 1
fi
N=$(awk -v r="$RAM" '$3 == r' "$JV" 2>/dev/null | wc -l)
T0=$(date +%s)
if [ "$MOD" = "compus" ]; then
    X=$(awk -v r="$RAM" '$1 == "ROSU" && $3 == r && NF == 4 { x = $2 } END { print x }' "$JV" 2>/dev/null)
    if [ -z "$X" ]; then
        echo "[poarta lot] REFUZ: --compus cere o rulare COMPLETA ROSIE anterioara pe $RAM — nu exista; ruleaza poarta completa (sh scripts/poarta_lot.sh)."
        exit 1
    fi
    PY=./venv/bin/python
    [ -x "$PY" ] || PY=python3
    echo "[poarta lot] rularea $((N + 1)) pe $RAM, commit $SHA: COMPUSA din rularea completa rosie a lui $X"
    "$PY" scripts/poarta_scurta.py --compus="$X"
    RC=$?
    case "$RC" in
        0|1) ;;
        *) echo "[poarta lot] compusul n-a dat verdict (exit $RC) — niciun rand scris; ruleaza poarta completa (sh scripts/poarta_lot.sh)."
           exit "$RC" ;;
    esac
    SUFIX=" compus:$X"
else
    echo "[poarta lot] rularea $((N + 1)) pe $RAM, commit $SHA (regula 3d: pana la verde, fara limita de rulari)"
    sh scripts/githooks/poarta-suita
    RC=$?
    SUFIX=""
fi
if [ "$(git rev-parse HEAD)" != "$SHA" ]; then
    echo "[poarta lot] HEAD s-a mutat cat a rulat poarta — verdictul nu mai e despre $SHA."
    RC=1
fi
if [ "$RC" -eq 0 ]; then V=VERDE; else V=ROSU; fi
echo "$V $SHA $RAM $(date -Is)$SUFIX" >> "$JV"
echo "[poarta lot] $V $SHA ($RAM${SUFIX}) -> $JV · durata $(( $(date +%s) - T0 ))s"
exit $RC
