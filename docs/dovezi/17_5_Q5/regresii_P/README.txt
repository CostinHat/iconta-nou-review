17.5-Q5 pct.8 — diagnosticul țintit al celor două regresii ale porții 1 Q3, pe P Q5 7a5dce04 (produsul = C2 Q3 fb5208ee pe bloburi; arbore curat, status gol).
Identitățile modulelor în exportul Git al lui P (SHA-256 = manifestul publicat pe E Q2):
  frontend_test/e2e/e2e_pilot_luna.py 6da296d150c336d2c367b3481afe05b34387cea5da69eaa6e923edc7b31d2c59
  frontend_test/e2e/e2e_pilot_x09.py  11bfa9c059b5362a82506dbe807a759ca6e4b8875be734df50cf7d376c491fc3
Copia iconta_test restaurată cu scripts/baza_test.sh restaureaza (81 s) din iconta_test-20261104-171456 (054cd769…), apoi:
  D=$(mktemp -d "$HOME/probe_Q5.XXXXXXXX")   # /home/costin/probe_Q5.3tgiG6gd
  PYTEST_ADDOPTS="--junitxml=$D/regresii.xml" ./venv/bin/python scripts/e2e_poarta.py --doar=./e2e_pilot_luna.py --doar=./e2e_pilot_x09.py "$D/capturi"
rc=0; «41 passed in 318.08s». În XML: e2e_pilot_luna.test_pilot_39_deblocarea_lunii_cu_motiv o apariție, trecută (5,092 s);
e2e_pilot_x09.test_pilot_X09 o apariție, trecută (58,090 s). Niciun alt eșec.
Martorul pasului 39 (capturile testului): fara_motiv (luna 09/2026 blocată, refuz fără motiv) → deblocata (deschisă cu motiv) → blocata_din_nou.
Martorul X09: testul nu scrie capturi (docstring, rândul 7); verdictul e aserțiunea pe 603×590 și 1366×768 (un loc de derulare, zona ≥ 40% la ≤ 700 px, nimic ieșit).
Notă: capturile pasului 39 sunt ale testului (patron.captura), luate imediat după acțiune; «fara_motiv» prinde fereastra deblocării în tranziție peste pagina de început — martorul pasului e aserțiunea testului, capturile sunt anexă.
