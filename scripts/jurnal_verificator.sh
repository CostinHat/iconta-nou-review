#!/bin/sh
# jurnal_verificator.sh — controlul încrucișat al jurnalului verificării pe pas (comanda 16.1, pct.3; rescris în 16.3, pct.2). Sursa rândurilor e scripts/verifica_pas.py (verdictul vine din comparația stării paginii
# cu așteptarea pasului, prin parcursul lansat de scripts/lanseaza_verificator.py); acest script e controlul încrucișat, nu sursa. Controlul nu mai judecă după mtime-ul capturii (capturile comise primesc mtime-ul
# checkout-ului): judecă după cheia (lot, parcurgere, pas, sha, verificator), existența capturii și marcajul oracolului; rândurile loturilor scutite (publica_lot.py::LOTURI_FARA_MARCAJ) numai după existența capturii.
# Subcomanda `pas` s-a scos (C212): oracolul se apelează prin parcurs.
#   jurnal_verificator.sh incepe <lot>            începutul parcurgerii (faza „verificator” din .lot_jurnal.log); id-ul rămâne în <git-common-dir>/verificator_<lot>.id
#   jurnal_verificator.sh incheie <lot>           sfârșitul parcurgerii
#   jurnal_verificator.sh controleaza <csv>       controlul încrucișat pe un CSV existent (ieșire 1 + numele rândului la prima abatere)
ROOT=$(git rev-parse --show-toplevel) || exit 1
cd "$ROOT" || exit 1
PY=./venv/bin/python; [ -x "$PY" ] || PY=python3
COMUN=$(git rev-parse --path-format=absolute --git-common-dir)
case "$1" in
    incepe) ID=$("$PY" scripts/jurnal_lot.py inceput "$2" verificator) && echo "$ID" > "$COMUN/verificator_$2.id" ;;
    incheie) ID=$(cat "$COMUN/verificator_$2.id" 2>/dev/null) && "$PY" scripts/jurnal_lot.py sfarsit "$2" verificator "$ID" parcurs ;;
    controleaza) [ -n "$2" ] || { echo "folosire: jurnal_verificator.sh incepe|incheie|controleaza …"; exit 2; }; "$PY" scripts/publica_lot.py --controleaza "$2" ;;
    *) echo "folosire: jurnal_verificator.sh incepe|incheie|controleaza …"; exit 2 ;;
esac
