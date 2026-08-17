Citeste CLAUDE.md §2.2 (structura raportului) si §2.3 (lant, siguranta, limba - pct.11 poarta verde vizuala) + ARHITECT.md "FORMA COMENZII" (7 puncte), apoi acest PREDARE_LANT.md, inainte de a incepe.

# PREDARE LANT — audit vizual tenant_005 (Constructii Profit Trim SRL / P2, cabinet 1968); TOATE straturile de migrare PARCURSE

## REPORNIRE (comanda exacta, gata de dat)
Auditul vizual al straturilor de migrare tenant_005 e TERMINAT (toate parcurse cap-coada cu Playwright, captura
PRIVITA + axe/mobil). Continua cu FRONTURILE RAMASE de mai jos, in aceeasi metoda (Regula 13+14): captura privita +
axe-core + mobil pe fiecare ecran atins, REPARAND ce gasesti, cu gard RED-probat per defect. DS inainte de cod UI.
DUPA editare static/js: venv/bin/python versioneaza_assets.py --scrie INAINTE de commit. Commit pe iconta_nou =
poarta pre-commit (~9min) + post-commit publica origin/main + backup + restart automat. Probe Playwright: helper
frontend_test/w_auth (tenant_005 id=4840); scripturi + CSV-uri de test in ~/probe_t005 (pe server).

## STRATURI DE MIGRARE — TOATE PARCURSE (nimic ramas aici)
Vector fiscal, Solduri initiale, Solduri parteneri, Salariati, Asociati, Mijloace fixe, Istoric declaratii, Plan de
conturi, Articole — toate parcurse (import->preview cu blocaje provocate->salvare->registru numarat in DB). Design
bun peste tot (preview per-rand, erori care numesc campul+randul, buton dezactivat). Date de test importate in
tenant_005: solduri(4 conturi echilibrat 22000), parteneri(2), asociati(2, cote 100%), mijloace(1), istoric(D300),
plan(4428.01 analitic) — seed de audit, se pot sterge.

## FRONTURI RAMASE (in ordine sugerata)
- **CLUSTER A11Y (recomandat urmatorul)** — pe TOATE ecranele atinse (Vector + cele 5 import) axe da 14-15 noduri
  color-contrast (serious), ~11-17 tinte <44px, 2 info livrata EXCLUSIV prin `title` (pierduta pe touch, Pixel 5).
  Pre-existent, APP-WIDE. E un cluster dedicat (CSS + componenta comuna .vf-opt/.mig-*). Vezi GARZI "REZIDUU a11y".
- **Field-level error marking** — eroarea de la formulare (ex. Vector) NU marcheaza campul vinovat cu contur (cutie
  generica jos; mesajul il numeste). Pattern app-wide (Regula 14 pct.4). Cluster separat.
- **FRONT D - declaratii**: D112 (VERIFICA la sursa daca art.60 pct.5 constructii CAEN 4321 e in vigoare 2026
  inainte de a decide daca lipsa scutirii e defect; azi impozit 266.61/CASS 500 = NEscutit), D101/D205 anuale,
  Bilant S1005 (blocat CORECT de reg.com. lipsa). Wizard pas 3 (coada) neatins pe nicio declaratie.
- **FRONT E (mic)** - editarea nume/CNP/data_angajare/norma salariat din UI (azi doar IBAN/COR/incetare/salariu).

## FOUR-WAY (de confirmat de urmatoarea tura)
HEAD = origin/main = backup/lant-2026-08-17 (remote) = 368325e. Comituri aceasta tura: 58fd46e (diacritice mesaje
validatori import), 368325e (plan conturi - adaugare cont reparata), + acest PREDARE. Anterior aceeasi zi: 53ca370
(mesaje user-facing fara nume intern de camp), 3a3b3f2 (vector per-firma reflecta vectorul salvat). Poarta verde pe
fiecare (2284->2285 passed, verificator TOTAL 0). RUNNING confirmat BEHAVIORAL: adaugarea de cont Plan conturi
intoarce acum 200 (era 422), contul apare in registru. Sentinele PUSH absente.

## LIVRAT aceasta tura (clustere 6+7)
6. **Diacritice pe mesajele validatorilor de import** (58fd46e, DS v2.37). 21 mesaje afisate fara diacritice
   (solduri/parteneri/asociati/istoric/articole/salariati/retete/mijloace + generalizare e-Factura), reparate;
   scapasera gardului fiindca sunt in raise brut/det+=/f-string/avertismente.append. Gard test_diacritice_afisate
   extins: 14 triggere + scanare INTEGRALA a validatorilor de import (exclude _gaseste_col + SQL). RED-probat.
7. **Plan de conturi: adaugarea de cont reparata** (368325e, DS v2.38). PlanContIn era definit DUPA handler (4798 vs
   1719); cu future annotations FastAPI trata `date` ca query -> orice adaugare 422. Mutat inainte de handler. Gard
   test_rute_model_body (niciun param BaseModel clasificat ca query). RED-probat. Reziduu: frontendul arata generic
   "eroare" la 422 (api.post) - dupa fix nu se mai atinge pe input valid.
