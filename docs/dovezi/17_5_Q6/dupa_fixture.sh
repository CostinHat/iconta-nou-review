#!/bin/sh
# 17.5-Q6 — după o rulare care a pregătit fixture-ul: restaurarea oficială (readuce tabelele publice, dar nu poate șterge schema firmei de probă,
# care ține funcțiile publice), apoi scoaterea schemei orfane (curata_fixture.sh: curatenie.scoate + restaurarea oficială). Sub lacătul oficial.
# Uz: sh docs/dovezi/17_5_Q6/dupa_fixture.sh <tenant_id> <schema>
set -u
cd "$(git rev-parse --show-toplevel)" || exit 1
./venv/bin/python scripts/lacat_test.py ia $$ dupa_fixture_17_5_Q6 || exit 90
export LACAT_TEST_PID="${LACAT_TEST_PID:-$$}"
./venv/bin/python scripts/verificator_design.py opreste
sh scripts/baza_test.sh restaureaza > /dev/null 2>&1 || echo "[dupa_fixture] prima restaurare a lăsat schema $2 (așteptat)"
sh docs/dovezi/17_5_Q6/curata_fixture.sh "$1" "$2"
