#!/bin/sh
# poarta_lot.sh — POARTA COMPLETA, o singura data pe lot, la inchiderea lui, inaintea publicarii pe productie.
#
# [15.10.2026, comanda Costin, verbatim in DECIZII „Poarta o dată pe lot”] „Poarta completă: o singură dată pe lot, la închiderea
# lotului, înainte de publicarea pe producție. Lotul se închide doar când o comandă îți spune explicit „Lotul X e complet”. [...]
# Maximum două rulări complete pe lot; dacă a doua pică, te oprești și raportezi.” Intre comenzi: numai `scripts/poarta_scurta.py`.
#
# Ce face: pe ramura lotului (worktree), cu arborele CURAT (HEAD = commitul lotului; pytest citeste arborele, deci verdictul e despre
# commit), ruleaza `scripts/githooks/poarta-suita` (prospetime, pytest, verificator, cifre F1–F5, plasa e2e) si scrie verdictul in
# `<git-common-dir>/poarta_verdicte.log`:   VERDE|ROSU <sha complet> <ramura> <data>
# `scripts/githooks/reference-transaction` muta `main` numai la un SHA cu `VERDE <sha>` aici (plus aprobarea scrisa a lui Costin).
# REFUZA: pe `main` / fara ramura; arbore murdar (modificari sau fisiere noi); un SHA deja VERDE (nimic de aflat); a TREIA rulare pe
# aceeasi ramura (maximum doua pe lot — la a doua rosie: oprire si raport, nu o a treia). Rulat in fundal (~70 de minute).
# Gard: core/test_poarta_lot.py (depozit temporar) + core/test_poarta_ordine.py (singurul care cheama `poarta-suita`).
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
N=$(awk -v r="$RAM" '$3 == r' "$JV" 2>/dev/null | wc -l)
if [ "$N" -ge 2 ]; then
    echo "[poarta lot] REFUZ: lotul $RAM are deja $N rulari complete (maximum doua pe lot). Oprire si raport (decizia Costin 15.10.2026)."
    awk -v r="$RAM" '$3 == r' "$JV" | sed 's/^/    /'
    exit 1
fi
echo "[poarta lot] rularea $((N + 1)) din maximum 2 pe $RAM, commit $SHA"
sh scripts/githooks/poarta-suita
RC=$?
if [ "$(git rev-parse HEAD)" != "$SHA" ]; then
    echo "[poarta lot] HEAD s-a mutat cat a rulat poarta — verdictul nu mai e despre $SHA."
    RC=1
fi
if [ "$RC" -eq 0 ]; then V=VERDE; else V=ROSU; fi
echo "$V $SHA $RAM $(date -Is)" >> "$JV"
echo "[poarta lot] $V $SHA ($RAM) -> $JV"
exit $RC
