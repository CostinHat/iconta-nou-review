# lacat_test.sh — se încarcă cu `. "$(dirname "$0")/lacat_test.sh"` de scripturile care ating iconta_test sau serverul 8019 (comanda 16.1-C3, pct.2); apoi `lacat_test_ia [director-scripturi]`.
# Ia lacătul pe numele shell-ului scriptului ($$) prin scripts/lacat_test.py; refuzul iese din script (exit 1). Exportă LACAT_TEST_PID=$$ ca scripturile pornite de acesta să fie reentrante.
lacat_test_ia() {
    _LT_DIR="$(cd "${1:-$(dirname "$0")}" && pwd)"   # directorul cu lacat_test.py: implicit cel al scriptului care a încărcat biblioteca
    _LT_PY=python3
    "$_LT_PY" "$_LT_DIR/lacat_test.py" ia "$$" "$(basename "$0")" || exit 1
    [ -n "${LACAT_TEST_PID:-}" ] && [ "$LACAT_TEST_PID" != "$$" ] && return 0   # reentrant: deținătorul rămâne cel care a pornit lanțul
    export LACAT_TEST_PID=$$
}
