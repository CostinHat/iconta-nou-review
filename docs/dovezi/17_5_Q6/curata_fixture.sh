#!/bin/sh
# 17.5-Q6 — scoaterea firmei create de pregateste_fixture_17_5_Q6.py (schema ei ține funcțiile publice, iar pg_restore --clean nu o poate șterge),
# prin funcția oficială a plasei (frontend_test/e2e/curatenie.py::scoate), apoi restaurarea oficială; totul sub lacătul oficial, cu 8019 oprit.
# Uz: sh docs/dovezi/17_5_Q6/curata_fixture.sh <tenant_id> <schema>
set -u
cd "$(git rev-parse --show-toplevel)" || exit 1
PY=./venv/bin/python
$PY scripts/lacat_test.py ia $$ curata_fixture_17_5_Q6 || exit 90
export LACAT_TEST_PID="${LACAT_TEST_PID:-$$}"
$PY scripts/verificator_design.py opreste
set -a; . ~/.iconta/test.env; set +a
PYTHONPATH=frontend_test/e2e:. $PY -c "
import sys; sys.path.insert(0,'frontend_test/e2e')
from conftest import _db; import curatenie
db=_db()
with db.get_conn() as c, c.cursor() as cur:
    cur.execute('SELECT current_database()'); assert cur.fetchone()[0]=='iconta_test'
curatenie.scoate(db, [(int(sys.argv[1]), sys.argv[2])]); print('scoasa', sys.argv[1], sys.argv[2])
" "$1" "$2" || exit 91
sh scripts/baza_test.sh restaureaza
