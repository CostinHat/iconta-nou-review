Citeste CLAUDE.md §2.2 (structura raportului) si §2.3 (lant, siguranta, limba), si ARHITECT.md "FORMA COMENZII" (forma comenzii primite - 7 puncte), inainte de a incepe.

# PREDARE_LANT — STARE CURENTA

Se SUPRASCRIE la fiecare publicare (al 5-lea pas, CLAUDE.md §2.3 pct.10). NU e jurnal - jurnalul e ISTORIC.md.
Ritual pornire: `ssh iconta 'cd ~/iconta_nou && git log -1 && git status --porcelain'`.

## (a) Four-way de la ultima executie
Ultimul commit de COD: (vezi git HEAD). App pe 127.0.0.1:8010. Four-way se confirma dupa restart
(start-time > commit-time). Ramura backup: backup/lant-2026-08-11.

## (b) Fronturi deschise
0. **CAMPANIE "CERTIFICARE-COMPORTAMENT" (Costin, 11.08) — IN CURS.** Certifica pentru fiecare din cele 201
   ca FACE ce spune (comportament exercitat pe 4163, NU cod citit) + are cale de acces in UI + ecranul respecta
   DS pe pagina RANDATA in browser. Raport UNIC la final (NU pe traseu). Constrangere: doar 4163; 1968 NEATINS;
   ZERO-BASE (rezultat gol/zero = eroare pana la proba contrara).
   PROGRES:
   - **CLUSTER 1 (import migrare) CERTIFICAT + REPARAT** (commit 38dbb06): clasa "accepta orice fisier si declara
     succes" reparata pe TOATA familia (asociati/istoric/mijloace/salariati/solduri; retete/articole aveau deja
     checkul). Proba comportamentala: feed gunoi pe /incarca -> era HTTP 200 total=0, acum 400. Gard
     core/test_import_migrare_valideaza.py (ROSU pe cod vechi 5 failed, VERDE dupa). RAMAS proba: import de fisier
     BUN -> N randuri nenule (ZERO-BASE pozitiv) inca nefacut pe fiecare.
   - **UI-PATH MAP (toate 172 LIVE) GATA**: doar 4 LIVE fara Acces UI (F001/F105/F106/F116) = infra legitima; ZERO
     user-facing fara cale.
   - **HARNESS BROWSER-DS construit**: frontend_test/cert_ds_browser.py (login 4163 + click card + verifica DOM
     randat: modal .fereastra non-gol, 0 erori consola, clase DS). Dashboard cabinet (13 carduri) CERTIFICAT
     DS-curat in browser.
   - **URMATOR**: (a) extinde harness-ul browser-DS la ecrane firma-level (Firme->firma->emitere/declaratii/
     operatiuni/banca/casa) + portal/client; (b) proba comportamentala pozitiva per functionalitate (nu doar
     respingere gunoi) - emitere factura reala, generare PDF, contare, etc.; (c) certificare cap-coada restul 201.
1-N. **Fronturi mostenite (campania verifica-201, INCHISA)**: F116 headere securitate DEPLOYATE 11.08 pe nginx (64e8b1b): X-Frame/X-Content/Referrer/HSTS-300/CSP-enforce, verificat login+38 ecrane 0 violari+0 5xx, config sub versionare config_server/iconta-nginx.conf; RAMAS optional HSTS lung (Costin). [vechea nota: decizie infra
   Costin, snippet gata); D406 PARTIAL (F035-037, scope); F124 (proces nu feature); test-debt import (proba pozitiva).

## (raport livrat)
RAPORT UNIC certificare-comportament livrat 11.08 pe HEAD 7fbb2aa (four-way: RUNNING 38dbb06 = ultima schimbare runtime). CAMPANIE CERTIFICARE-COMPORTAMENT COMPLETA (11.08): 3 dimensiuni certificate; date operationale populate pe ALFA + proba pozitiva ZERO-BASE + write-flows (emitere/chitanta/contare) + deep sub-screen emitere DS-curat. Import class reparat+gardat. Ramas: bonuri portal (partial), sub-ecrane adanci exhaustiv (esantionat).

## (c) Ce e in lucru acum
Campania certificare-comportament (front 0). Cluster import certificat+reparat; harness browser-DS pe dashboard
cabinet; urmeaza ecranele firma-level + proba comportamentala pozitiva.

## (d) Ce urmeaza
1. Extinde cert_ds_browser.py la ecranele firma-level + portal (navigare mai adanca).
2. Proba comportamentala POZITIVA (fisier bun -> N randuri; emitere -> factura; PDF -> %PDF-; etc.) pe fiecare
   functionalitate, grupat pe loturi (ca verifica-201: transversal/facturare/contab/stocuri/salarizare/fiscal/
   control/cabinet).
3. Raport UNIC final (§2.2, 11 sectiuni): certificat cu ce proba functionalitate-cu-functionalitate; LIVE fara UI
   (deja: 0 user-facing); abateri DS ecran-cu-ecran; reparat; gasit-nereparat; necertificat + de ce; four-way.

## Unelte
- Certificare comportament import: gard core/test_import_migrare_valideaza.py (in poarta verde).
- Browser-DS: frontend_test/cert_ds_browser.py (login sessionStorage token; NU in poarta verde). Creds
  ~/.iconta/fe_test.env (cabinet 4163; tenants 8396 ALFA/8397 BETA/8398 GAMA/8399 DELTA).
- DUK declaratii: PYTHONPATH=$PWD frontend_test/valideaza_duk.py. Registru: 5 garduri in core/test_registru_*.
- Poarta verde: commit ruleaza pytest suita (~6min) + verificator (0); post-commit publica origin/main +
  backup/lant-<data>; apoi restart iconta-nou (four-way).

## (stare 11.08 seara) DECIZII §6 EXECUTATE (0304128)
D1: refactor DS-input (29 inputuri -> .camp-input) + gard INPUT_NECONFORM (verificator, rosu pe 27 cod vechi). D2: 4 butoane console-400 (Casa/REGES/SEPA/portal) disabled+motiv + backend /stat-plata reges_configurat. Verificat vizual + comportamental, 0 regresii. Four-way RUNNING=HEAD=0304128.
