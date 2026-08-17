Citeste CLAUDE.md §2.2 (structura raportului) si §2.3 (lant, siguranta, limba - pct.11 poarta verde vizuala) + ARHITECT.md "FORMA COMENZII" (7 puncte), apoi acest PREDARE_LANT.md, inainte de a incepe.

# PREDARE LANT — audit tenant_006 (Achizitii IC Neplatitor SRL / N1, cabinet Prisma 1968)

## REPORNIRE (comanda exacta, gata de dat)
Continua auditul cap-coada tenant_006 (N1, neplatitor micro cu achizitii intracomunitare; id 4841, schema tenant_006,
CUI 95451848). Livrat tura asta: fix de coerenta semafor (existenta_firma_an numara achizitiile IC + casa/banca),
commit 288f886. Urmatorul FRONT gata de atacat = CLUSTER A11Y CONTRAST pe Control fiscal (2 tokeni, tinte verificate
mai jos). Metoda Regula 13+14: captura PRIVITA + axe/mobil pe fiecare ecran atins, REPARAND, gard RED-probat prin
rulare; DS inainte de cod UI; versioneaza_assets --scrie dupa editare static/js|css; commit pe iconta_nou = poarta
~8min + post-commit publica+restart. Probe Playwright: helper ~/probe_t006/wt006.py (deschide_firma -> "Achizitii IC
Neplatitor"); scripturi in ~/probe_t006 (server). Env: `set -a && . ~/.iconta/db.env && . ~/.iconta/api_keys.env`.

## FOUR-WAY (de confirmat de urmatoarea tura)
HEAD = origin/main = backup/lant-2026-08-17 (remote) = RUNNING = 288f886. Serviciul restartat 23:24:31 > commit
23:16:06. Poarta verde: 2296 passed / 4 skipped / 16 xfailed, verificator 0.

## FRONT 1 — CLUSTER A11Y CONTRAST pe Control fiscal (gata de atacat, tinte verificate)
axe-core pe Control fiscal tenant_006: 17 violari color-contrast (serious), reduse la 2 TOKENI pe fundalul panoului
#e9edf3:
- `--albastru #347ab8` (var, `.mig-sold-cont` = codurile D100/D406/D301 in `.cf-rand-decl` si `.cf-incr-cap`):
  3.87:1 pe #e9edf3 (AA pe alb 4.54, DAR sub 4.5 pe panou). Fix SCOPED (nu atinge tokenul global, calibrat alb-pe-albastru):
  `.cf-rand-decl .mig-sold-cont, .cf-incr-cap .mig-sold-cont { color:#2f6fa6; }` -> 4.53 pe #e9edf3 (verificat).
- `--gri-semafor #9aa3b2` (`.cf-incr-temei` = sub-textul verdictelor "necunoscut declarat...", stil.css:2253):
  2.16:1 pe #e9edf3. Fix: `.cf-incr-temei { color:#5c6675; }` -> 4.95 pe #e9edf3 (verificat).
Plus: axe "region" moderate 17 (landmark lipsa) - de evaluat separat. Gard: extinde core/test_a11y_contrast_tokens.py
cu perechile (.cf-incr-temei pe #e9edf3, .cf-rand-decl .mig-sold-cont pe #e9edf3) >= 4.5, RED-probat. DS cap.12 paleta.
Dupa fix: re-ruleaza ~/probe_t006/axe_detail.py -> contrast=0. axe/mobil si pe restul ecranelor tenant_006 neatinse.

## FRONT 2 — D390 nu vede achizitiile din d301_operatiuni (DECIZIE CERUTA, temei de verificat)
d390.genereaza(tenant_006, 6/2026) refuza "pe zero: nicio operatiune intracomunitara" DESI exista achizitia IC in
d301_operatiuni (iun 2026). D390 se construieste din facturi, nu din d301_operatiuni - acelasi tipar ca bug-ul de
existenta reparat. DAR: (a) D390 e "gri" oricum cat timp art.317 nu e marcat pe firma (neplatitor); (b) daca o achizitie
IC de bunuri inregistrata NUMAI in d301 (fara factura) trebuie sa apara in D390 (cod A) pentru un neplatitor art.317 -
de confirmat la sursa (OPANAF 705/2020 + relatia D301<->D390 pentru achizitii de bunuri la neinregistratii art.316).
NEVERIFICAT: comportamentul cu art.317=da (firma are art317=False acum). Nu reparat - cere temei + scenariu art.317.

## FRONT 3 — field-level error marking (RAMAS din tura tenant_005, inca deschis)
Erorile de formular numesc campul si consecinta (ex. Date firma: "Profil incomplet - Nr. registrul comertului -
blocheaza Bilant S1005" - CORECT, Regula 14 pct.4) DAR nu marcheaza VIZUAL campul vinovat cu contur rosu langa el.
Pattern app-wide. De reparat la nivel de tipar (marcaj rosu pe campul cu eroare + ancorare mesaj).

## LIVRAT (tura asta, commit 288f886)
existenta_firma_an (control_incrucisat.py) numara acum orice operatiune datata: d301_operatiuni (achizitii IC),
casa_operatiuni, extras_linii, bonuri, chitante, mijloace_fixe; nomenclatoare + solduri initiale EXCLUSE. Repara
contradictia de pe semafor (restanta D301 "operatiuni IC iun 2026" vs "nu pot demonstra ca firma era activa in 2026").
tenant_006 acum consistent cu tenant_002/003 (micro): D100/D406 2026 T1+T2 restante concrete; 2025 ramane necunoscut.
Gard RED->GREEN core/test_existenta_activitate.py (schema temporara, 4 teste). D301 verificat end-to-end: DUK valid,
cifre corecte (baza 52261, tva 10975 @21%, total 63236), avertisment art.317 (pers_inreg=1). Probe vizuale privite:
dashboard, import (10 straturi), declaratii (selector), Control fiscal (inainte+dupa), Vector fiscal (reflecta
micro/neplatitor/IC=Da), Date firma (art.317 editabil=nu). OBSERVATIE (§5, nereparat, pre-existent universal): o micro
fara venituri intr-un trimestru vede D100 restanta pe semafor dar D100.genereaza refuza "pe zero" - comportament comun
tuturor micro (tenant_002/003), nu introdus de fix; relatia semafor<->generator pe zero = de clarificat separat.
