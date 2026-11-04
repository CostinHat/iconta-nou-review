#!/bin/sh
# jurnal_verificator.sh — jurnalul verificării pe pas (comanda 16.1, pct.3). Sursa rândurilor e scripts/verifica_pas.py (verdictul vine din comparația JSON-ului
# ecranului cu așteptarea pasului); acest script e controlul încrucișat, nu sursa: refuză un rând fără captură existentă cu mtime în intervalul declarat.
#   jurnal_verificator.sh incepe <lot>            începutul parcurgerii (faza „verificator” din .lot_jurnal.log); id-ul rămâne în <git-common-dir>/verificator_<lot>.id
#   jurnal_verificator.sh pas <lot> <pas> <acțiune> <json-url> <așteptare-json> [pagina]   un pas: rulează verifica_pas.py, apoi controlul încrucișat
#   jurnal_verificator.sh incheie <lot>           sfârșitul parcurgerii
#   jurnal_verificator.sh controleaza <csv>       controlul încrucișat pe un CSV existent (ieșire 1 + numele rândului la prima abatere)
ROOT=$(git rev-parse --show-toplevel) || exit 1
cd "$ROOT" || exit 1
PY=./venv/bin/python; [ -x "$PY" ] || PY=python3
COMUN=$(git rev-parse --path-format=absolute --git-common-dir)
controleaza() {
    "$PY" - "$1" <<'PYE'
import csv, datetime, os, sys
rad = os.getcwd()
rc = 0
for r in csv.DictReader(open(sys.argv[1], encoding="utf-8")):
    cap = r["captura"] if os.path.isabs(r["captura"]) else os.path.join(rad, r["captura"])
    if r["verdict"] == "neexecutat":
        continue
    if not os.path.exists(cap):
        print("REFUZ: rândul %s fără captură existentă (%s)" % (r["pas"], r["captura"])); rc = 1; continue
    t = datetime.datetime.fromtimestamp(os.path.getmtime(cap)).astimezone()
    a, b = datetime.datetime.fromisoformat(r["inceput"]), datetime.datetime.fromisoformat(r["sfarsit"])
    if not (a - datetime.timedelta(seconds=1) <= t <= b + datetime.timedelta(seconds=1)):
        print("REFUZ: rândul %s: captura are mtime %s, în afara intervalului %s – %s" % (r["pas"], t.isoformat(timespec="seconds"), r["inceput"], r["sfarsit"])); rc = 1
sys.exit(rc)
PYE
}
case "$1" in
    incepe) ID=$("$PY" scripts/jurnal_lot.py inceput "$2" verificator) && echo "$ID" > "$COMUN/verificator_$2.id" ;;
    pas)
        LOT="$2"; PAS="$3"; ACT="$4"; URL="$5"; AST="$6"; PAG="${7:-/}"
        CSV=${JURNAL_VERIFICARE_CSV:-docs/dovezi/$(echo "$LOT" | tr . _)/jurnal_verificare.csv}
        "$PY" scripts/verifica_pas.py --lot "$LOT" --pas "$PAS" --actiune "$ACT" --json-url "$URL" --asteptare "$AST" --pagina "$PAG" --csv "$CSV"
        RC=$?
        controleaza "$CSV" || exit 1
        exit $RC ;;
    incheie) ID=$(cat "$COMUN/verificator_$2.id" 2>/dev/null) && "$PY" scripts/jurnal_lot.py sfarsit "$2" verificator "$ID" parcurs ;;
    controleaza) controleaza "$2" ;;
    *) echo "folosire: jurnal_verificator.sh incepe|pas|incheie|controleaza …"; exit 2 ;;
esac
