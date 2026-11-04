# verde-prin-pass.sh — funcția comună a hook-urilor reference-transaction și pre-push (comanda 16.1-C2, pct.0); se încarcă cu `. "$(dirname "$0")/verde-prin-pass.sh"`.
# verde_pe_head <sha> <poarta_verdicte.log> <publica_verdicte.log>: întoarce 0 dacă poarta are VERDE pe <sha> SAU dacă există PASS pe <sha> care numește un C cu VERDE,
# iar `scripts/publica_lot.py --verifica C <sha> <lot>` (aceeași funcție ca în C1: C strămoș al lui <sha>, diff-ul atinge numai dovezile și registrele) dă PASS.
# Fără PASS pe <sha> nu se acceptă nimic în afară de VERDE exact pe <sha> (și aceasta rămâne necesară în hook-uri ca al doilea gard, după cererea PASS).
verde_pe_head() {
    _SHA="$1"; _JV="$2"; _JP="$3"
    grep -q "^VERDE $_SHA " "$_JV" 2>/dev/null && return 0
    _LINIE=$(grep "^PASS $_SHA " "$_JP" 2>/dev/null | tail -n 1)
    [ -n "$_LINIE" ] || return 1
    _C=$(printf '%s\n' "$_LINIE" | sed -n 's/.* C=\([0-9a-f]\{40\}\).*/\1/p')
    _LOT=$(printf '%s\n' "$_LINIE" | cut -d' ' -f3)
    [ -n "$_C" ] && [ -n "$_LOT" ] || return 1
    grep -q "^VERDE $_C .* completa " "$_JV" 2>/dev/null || return 1
    _SCR="$(cd "$(dirname "$0")/.." && pwd)/publica_lot.py"
    [ -f "$_SCR" ] || return 1
    python3 "$_SCR" --verifica "$_C" "$_SHA" "$_LOT" >&2
}
