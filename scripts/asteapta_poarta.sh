#!/bin/sh
# asteapta_poarta.sh <lot> [secunde_max, implicit 540] [--dupa=<ISO cu fus orar>] — așteptarea porții (17.5-U, U.3): iese când jurnalul arată rezultatul și nu se
# potrivește singură (fără pgrep/ps pe linii de comandă). Logica și ieșirile (0 verde, 1 rosu, 2 uz, 3 oprit, 4 infra, 5 intrerupt, 6 nepornita, 7 eroare de unealtă,
# 9 in_curs) sunt în scripts/asteapta_poarta.py; argumentele le citește numai scripts/argumente_script.py.
RAD="$(cd "$(dirname "$0")/.." && pwd)"
PY="$RAD/venv/bin/python"; [ -x "$PY" ] || PY=python3
exec "$PY" "$RAD/scripts/asteapta_poarta.py" "$@"
