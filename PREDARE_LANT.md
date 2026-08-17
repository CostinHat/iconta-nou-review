Citeste CLAUDE.md §2.2 (structura raportului) si §2.3 (lant, siguranta, limba - pct.11 poarta verde vizuala) + ARHITECT.md "FORMA COMENZII" (7 puncte), apoi acest PREDARE_LANT.md, inainte de a incepe.

# PREDARE LANT — audit tenant_006 (Achizitii IC Neplatitor SRL / N1, cabinet Prisma 1968)

## REPORNIRE (comanda exacta, gata de dat)
Continua auditul cap-coada tenant_006 (N1, neplatitor micro cu achizitii intracomunitare; id 4841, schema tenant_006,
CUI 95451848). Livrat tura asta: fix de coerenta semafor (existenta_firma_an numara achizitiile IC + casa/banca),
commit 288f886. Livrat si: D100 pe fapt de venituri (b196943), a11y contrast Control fiscal + import blockages
verificate. Fronturi RAMASE: field-level error marking (front 3, formulare SAVE), D390 ignora d301 (front 2, decizie
ceruta), axe "region"/landmarks app-wide, D406 conturi 731-738. Metoda Regula 13+14: captura PRIVITA + axe/mobil pe
fiecare ecran atins, REPARAND, gard RED-probat prin
rulare; DS inainte de cod UI; versioneaza_assets --scrie dupa editare static/js|css; commit pe iconta_nou = poarta
~8min + post-commit publica+restart. Probe Playwright: helper ~/probe_t006/wt006.py (deschide_firma -> "Achizitii IC
Neplatitor"); scripturi in ~/probe_t006 (server). Env: `set -a && . ~/.iconta/db.env && . ~/.iconta/api_keys.env`.

## FOUR-WAY (de confirmat de urmatoarea tura)
Confirmat de raportul acestei ture (four-way pe commitul a11y). Comituri tura tenant_006: 288f886 (existenta_firma_an),
50c3ebf (registre+predare), b196943 (D100 pe fapt de venituri), c55308f (predare), + commitul a11y contrast +
import-verificat al acestei ture. Poarta verde pe fiecare, verificator 0.

## INCHIS tura asta — CLUSTER A11Y CONTRAST pe Control fiscal (LIVRAT)
17 violari color-contrast pe panoul #e9edf3, reduse la 2 tokeni, reparate SCOPED: `.cf-rand-decl/.cf-incr-cap
.mig-sold-cont` (coduri declaratii) #347ab8->#2f6fa6 (4.53); `.cf-incr-temei` (sub-text verdicte) #9aa3b2->#5c6675
(4.95). Token global neatins. axe contrast=0 dupa (captura privita, identitate pastrata). Gard test_a11y_contrast_tokens
extins (mutatie-probat). DS v2.43. versioneaza_assets --scrie. Import blockages verificate CURAT (salariati CNP /
solduri dezechilibru = model). RAMAS a11y: axe "region" (landmark) 8-19 noduri app-wide (moderat, structural);
D406 avertisment conturi 731-738 excluse din norma A (neverificat la sursa).

## FRONT 2 — D390 nu vede achizitiile din d301_operatiuni (DECIZIE CERUTA, temei de verificat)
d390.genereaza(tenant_006, 6/2026) refuza "pe zero: nicio operatiune intracomunitara" DESI exista achizitia IC in
d301_operatiuni (iun 2026). D390 se construieste din facturi, nu din d301_operatiuni - acelasi tipar ca bug-ul de
existenta reparat. DAR: (a) D390 e "gri" oricum cat timp art.317 nu e marcat pe firma (neplatitor); (b) daca o achizitie
IC de bunuri inregistrata NUMAI in d301 (fara factura) trebuie sa apara in D390 (cod A) pentru un neplatitor art.317 -
de confirmat la sursa (OPANAF 705/2020 + relatia D301<->D390 pentru achizitii de bunuri la neinregistratii art.316).
NEVERIFICAT: comportamentul cu art.317=da (firma are art317=False acum). Nu reparat - cere temei + scenariu art.317.

## INCHIS tura asta — D100 micro pe fapt de venituri (commit b196943)
Semaforul arata D100 micro restanta ignorand baza de venituri, DAR D100 pe zero e structural invalid la DUK
(generatorul refuza) -> restanta falsa. Reparat: d100_fapt (simetric d390_fapt/d112_fapt) gateaza D100 pe baza de
venituri; trimestru inchis fara venituri -> "nu se datoreaza", nu restanta. tenant_006 (achizitie IC, fara venituri):
D100 T1/T2 -> "Nu se datoreaza" (captura privita); restante ramase D406 T1/T2 + D301 iun (toate genereaza DUK-valid).
tenant_003 (venituri 0) corectat identic; tenant_002 T1 (are venituri) pastrat. Gard RED(mutatie)->GREEN test_d100_fapt.

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
micro/neplatitor/IC=Da), Date firma (art.317 editabil=nu). Declaratii la XML+DUK: D301 valid, D406 valid (68895B),
D101/D112 genereaza gol, D205/D390 refuza pe gol. D100 pe zero (semafor restanta vs generator refuza) REPARAT tura asta
(vezi INCHIS mai jos).
