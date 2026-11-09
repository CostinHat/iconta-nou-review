#!/bin/sh
# 6.1–6.3 din comanda 17.5-C0, pe P; ieșirile în docs/dovezi/17_5_C0/
cd ~/iconta_lot17_5c0 || exit 1
D=docs/dovezi/17_5_C0
PY=./venv/bin/python
{ echo "== 6.1 stare înainte"; date -Is; git rev-parse HEAD; $PY scripts/lacat_test.py stare; (ss -ltn | grep ":8019 ") || echo "8019: liber"; echo "status: [$(git status --porcelain --untracked-files=no)]"; } > $D/stare_inainte.txt 2>&1
{ echo "== 6.2"; /usr/bin/time -f "durata %e s" $PY -m pytest -q -p no:cacheprovider core/test_plasa_modificabile_17_5_C0.py; } > $D/teste_noi_P.txt 2>&1

{ echo "== 6.3 core/test_s2_salariu_de_la.py pe P"; /usr/bin/time -f "durata %e s" $PY -m pytest -q -p no:cacheprovider core/test_s2_salariu_de_la.py; } > $D/s2_P.txt 2>&1
for f in e2e_pilot_x09 e2e_lot12_verif e2e_pilot_luna; do
  sh scripts/baza_test.sh restaureaza > $D/restaureaza_$f.txt 2>&1
  { date -Is; /usr/bin/time -f "durata %e s" $PY scripts/e2e_poarta.py --arbore --doar=$f.py /tmp/e2e_17_5_C0_$f; } > $D/$f.txt 2>&1
done
echo GATA > $D/pasi_6_gata.flag
