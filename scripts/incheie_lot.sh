#!/bin/sh
# incheie_lot.sh — SINGURA încheiere a unei comenzi (comanda 16.1-C3, pct.4): scrie ~/ghid_incoming/OPRIT_<nr>.txt, fișierul-semnal pe care coada îl citește (nu ecranul).
#   incheie_lot.sh <nr> <stare> [<sha>|-] [<motiv>]     stare = publicat | nepublicat; motivul (o propoziție) ajunge în alerta către Costin
# Rândul scris: „OPRIT — gata: <nr> <stare> <sha|-> <ora ISO>”. Apelat de publica_lot.sh la sfârșit (publicat sau STOP) și de orice oprire cu „OPRIT — gata: <nr> nepublicat”.
# Regula (CLAUDE.md): Code nu scrie fișierul de mână și nu scrie «OPRIT — gata» înainte de a-l apela. OPRIT_DIR mută directorul numai în calibrări.
# Alerta (17.2-A): după scrierea fișierului, pentru un lot cu număr de forma NN.M[-X], scripts/alerta_whatsapp.py (cu OPRIT_DIR setat, numai dacă ALERTA_CMD e setată);
# ieșirea ei nu schimbă codul de ieșire de aici. ALERTA_TIMEOUT_S = bugetul alertei (implicit 90 s: Meta 2×15 s plus email 2×15 s, cu marjă).
NR="${1:-}"; STARE="${2:-}"; SHA="${3:--}"; MOTIV="${4:-}"
printf '%s' "$NR" | grep -Eq '^[0-9A-Za-z][0-9A-Za-z.-]*$' || { echo "[incheie_lot] REFUZ: număr de lot invalid: '$NR'"; exit 2; }
case "$STARE" in publicat|nepublicat) ;; *) echo "[incheie_lot] REFUZ: stare '$STARE' (publicat | nepublicat)"; exit 2 ;; esac
DIR="${OPRIT_DIR:-$HOME/ghid_incoming}"
[ -d "$DIR" ] || { echo "[incheie_lot] REFUZ: lipsește $DIR"; exit 1; }
F="$DIR/OPRIT_$NR.txt"
T="$F.tmp.$$"
printf 'OPRIT — gata: %s %s %s %s\n' "$NR" "$STARE" "$SHA" "$(date -Is)" > "$T" && mv "$T" "$F" || { rm -f "$T"; echo "[incheie_lot] REFUZ: scrierea a eșuat"; exit 1; }
echo "[incheie_lot] $F: $(cat "$F")"
if printf '%s' "$NR" | grep -Eq '^[0-9]+\.[0-9]+(-[A-Z][0-9]*)?$' && { [ -z "${OPRIT_DIR:-}" ] || [ -n "${ALERTA_CMD:-}" ]; }; then
  RAD="$(cd "$(dirname "$0")/.." && pwd)"
  if [ -n "${ALERTA_CMD:-}" ]; then CMD="$ALERTA_CMD"
  elif [ -x "$RAD/venv/bin/python" ]; then CMD="$RAD/venv/bin/python $RAD/scripts/alerta_whatsapp.py"
  else CMD="python3 $RAD/scripts/alerta_whatsapp.py"; fi
  # shellcheck disable=SC2086 — comanda alertei are cuvinte separate (interpretor + script)
  timeout "${ALERTA_TIMEOUT_S:-90}" $CMD lot "$NR" "$STARE" "$SHA" "$MOTIV" || true
fi
exit 0
