17.5-Q5 pct.8.5 — rularea dedicată a testului arhitectului (e.1, e.2, e.4, e.5) pe P Q5 7a5dce04 (produsul = C2 Q3 fb5208ee pe bloburi).
Copia iconta_test restaurată (scripts/baza_test.sh restaureaza, 82 s) din iconta_test-20261104-171456, apoi:
  D=$(mktemp -d "$HOME/probe_Q5.XXXXXXXX")   # /home/costin/probe_Q5.MccJNBzo
  PYTEST_ADDOPTS="--junitxml=$D/ferestre.xml" ./venv/bin/python scripts/e2e_poarta.py --doar=e2e_ferestre_17_5_Q5.py "$D/capturi"
rc=0, «1 passed in 18.70s». Cititorul (logica dovada_baza.sh:338–339, numărarea rândurilor «VERDICT <id> pica|trece» din ieșirea pytest): cititor.txt —
e.1 trece=1, e.2 trece=1, e.4 trece=1, e.5 trece=1, nicio «pica». Pe E (REAL Q5): toate patru pică.
Cifrele Bancă (masuri.json, cifre_banca_stoc.txt): 11 ID-uri în API (1–11) = 11 rânduri în #bk-lucru, din care 2 în #bk-deoparte (7, 10); secțiunile exclusive 9 contate + 2 ignorate;
11 «Contează», 0 principale, 0 active (snapshotul nu are linie eligibilă; martor activ: 0); un singur principal «Importă extras», în bară.
Martorul de Stocuri: #s-desc «Descarcă gestiunea lunii» activ, secundar (fond alb, contur gri), Luna 10/2026; un singur principal «+ NIR nou», în bară.
Solduri inițiale (C236): cursor «default» pe toate cele 7 noduri, aspect identic în repaus și la hover, F1 și F7, la 1366×768 și 603×590 (8 capturi pereche).
