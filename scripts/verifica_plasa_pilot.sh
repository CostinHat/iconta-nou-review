#!/bin/sh
# verifica_plasa_pilot.sh — pasul porții care refuză când o poziție pilot „ok” nu are test în hartă (15.1-E7, pct.5); vezi verifica_plasa_pilot.py
ROOT=$(git rev-parse --show-toplevel) || exit 1
cd "$ROOT" || exit 1
PY=./venv/bin/python
[ -x "$PY" ] || PY=python3
exec "$PY" scripts/verifica_plasa_pilot.py
