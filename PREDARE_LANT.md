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

## INCHIS tura asta — FRONT 2 (D390<->d301) rezolvat pe corectitudine
INVESTIGAT: D390 SE POATE produce manual - UI-ul de clasificare intracomunitara are Tip A (achizitie bunuri IC cu
tara + cod TVA furnizor). Probat: linie manuala cod A -> d390.genereaza produce XML valid (nr_opi=1); DUK valideaza
algoritmul codului TVA. Deci NU e blocaj de corectitudine. FIX LIVRAT: refuzul D390 "pe zero" semnaleaza acum
operatiunile din d301_operatiuni si indruma spre adaugarea manuala (Tip A), in loc de mesajul generic fals "verifica
facturile UE". Mirror al refuzului D301<->facturi. Gard test_d390_d301_semnal (mutatie-probat).
RAMAS = DECIZIE (recomandare executor: NU construi): auto-derivarea d301->D390 cod A ar cere migrare DB (coloane
partener cod TVA+tara pe d301_operatiuni) + camp in ecranul D301, pentru un caz de margine (art.317). Calea manuala +
avertismentul acopera corect fluxul.

## INCHIS tura asta — D100 micro pe fapt de venituri (commit b196943)
Semaforul arata D100 micro restanta ignorand baza de venituri, DAR D100 pe zero e structural invalid la DUK
(generatorul refuza) -> restanta falsa. Reparat: d100_fapt (simetric d390_fapt/d112_fapt) gateaza D100 pe baza de
venituri; trimestru inchis fara venituri -> "nu se datoreaza", nu restanta. tenant_006 (achizitie IC, fara venituri):
D100 T1/T2 -> "Nu se datoreaza" (captura privita); restante ramase D406 T1/T2 + D301 iun (toate genereaza DUK-valid).
tenant_003 (venituri 0) corectat identic; tenant_002 T1 (are venituri) pastrat. Gard RED(mutatie)->GREEN test_d100_fapt.

## INCHIS tura asta — FIELD-LEVEL ERROR MARKING (front 3, LIVRAT)
eroareCamp (api.js) ancora mesajul rosu langa camp DAR nu marca inputul (fara contur). Reparat app-wide (7 ecrane):
eroareCamp adauga `.camp-invalid` + aria-invalid, curataEroriCamp o scoate la corectare; contur rosu #a3231c + glow.
Capcana: bordura globala `!important` (contrast_ferestre_v1, specificitate 0,6,1) - overrideul reproduce selectorul +
`.camp-invalid` (0,7,1). Captura privita Date firma (2 campuri goale -> contur rosu + mesaj, dispar la corectare).
Gard test_fieldmark.py mutatie-probat. DS v2.44.

## INCHIS tura asta — AUTO-DERIVARE d301->D390 cod A/S (CONSTRUITA, decizia Costin)
Costin a cerut construirea (peste recomandarea executorului). Livrat: migrare DB (furnizor pe d301_operatiuni, 19/19
scheme) + ecran D301 cu 3 campuri furnizor + indicator grila + generator d390.operatiuni_din_d301 (tip 1/3->A, 5->S;
2/4 excluse) + reconciliere a-doua-cale _pull_d301. Proba: tenant_006 op cu furnizor DE -> D390 auto-derivat DUK VALID
(cod A, baza 52261); captura privita ecran D301. Gard mutatie-probat (cele doua cai coincid). DS v2.45.
tip 3 (accizabile) -> cod A VERIFICAT la sursa (OPANAF 394/2017 anexa 2: cod A = achizitii IC de bunuri, fara
excludere accizabile) + DUK (bazaA); tip 5 -> cod S DUK (bazaS). tip 4 (art.307 alin.(3)(5)(6): gaz/energie +
bunuri din regim suspensiv + taxare inversa locala) VERIFICAT la sursa (CF art.307) = NEintracomunitar -> exclus
din D390 CORECT (serviciile IC art.307(2) = tip 5). Rafinare: achizitii_d301 numara doar tip 1/3/5 fara tara;
grila D301 clarifica tip 2/4 ("nu intra in D390 — ..."). Toate cele 5 tipuri D301 verificate la sursa.
Mis-clasificare: tip 4 cu cod TVA furnizor -> indiciu soft "poate e serviciu IC -> foloseste tip 5 (D390 cod S)"
(flag d390_posibil_serviciu), ca un serviciu IC ratacit pe tip 4 sa nu ramana absent din D390.

## RAMAS deschis (fronturi pt urmatoarea tura)
- axe "region"/landmarks app-wide (moderat, structural, 8-19 noduri/ecran).
- D406 avertisment conturi 731-738 excluse din norma A (neverificat la sursa).
- Import: provocate salariati+solduri (curat); restul 8 straturi neprovocate in aceste ture.
- Vizual/mobil (Pixel 5): rulat doar pe Control fiscal; restul ecranelor tenant_006 neanalizate pe telefon.

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
