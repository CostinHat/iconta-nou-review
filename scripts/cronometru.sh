#!/bin/sh
# cronometru.sh <lot> <faza> -- <comanda…> — rulează comanda și scrie în .lot_jurnal.log începutul și sfârșitul fazei (comanda 16.1, pct.2), pentru orice rulare
# care nu trece prin pytest. Ieșirea comenzii e a scriptului. Un proces omorât în timpul rulării apare în jurnal ca „intrerupt”.
AICI=$(cd "$(dirname "$0")" && pwd)
PY=$AICI/../venv/bin/python; [ -x "$PY" ] || PY=python3
LOT="$1"; FAZA="$2"; shift 2
[ "$1" = "--" ] && shift
[ -n "$LOT" ] && [ -n "$FAZA" ] && [ "$#" -gt 0 ] || { echo "folosire: cronometru.sh <lot> <faza> -- <comanda…>"; exit 2; }
ID=$("$PY" "$AICI/jurnal_lot.py" inceput "$LOT" "$FAZA" "comanda=$1")
LOT_CRONOMETRAT=1 "$@"
RC=$?
if [ "$RC" -eq 0 ]; then R=verde; else R=rosu_$RC; fi
"$PY" "$AICI/jurnal_lot.py" sfarsit "$LOT" "$FAZA" "$ID" "$R"
exit $RC
