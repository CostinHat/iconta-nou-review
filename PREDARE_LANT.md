Citeste CLAUDE.md §2.2 (structura raportului) si §2.3 (lant, siguranta, limba - pct.11 poarta verde vizuala) + ARHITECT.md "FORMA COMENZII" (7 puncte), apoi acest PREDARE_LANT.md, inainte de a incepe.

# PREDARE LANT — audit tenant_006 (Achizitii IC Neplatitor SRL / N1, cabinet Prisma 1968)

## REPORNIRE (comanda exacta, gata de dat) — CAMPANIE ACTIVA: colectii date valide+invalide per firma + corectitudine (F5)
Costin (18.08): pentru FIECARE firma din matrice (cabinet 1968: t001-t012 + t017; + demo 8396-99) construieste o
colectie de date VALIDE (genereaza toate declaratiile aplicabile DUK-valid) + una INVALIDE (provoaca fiecare blocaj/
refuz/camp obligatoriu). La cele INVALIDE conteaza ca MESAJUL de pe ecran sa-l ajute pe contabil sa inteleaga si sa
remedieze intrarea - "nu facem economie de vorbe" (F5/Regula 14.4: ce lipseste + unde se corecteaza + consecinta;
FARA nume interne; motiv VIZIBIL nu title-only; obligativitate inainte de buton). NU vanez defect/firma - verific
CORECTITUDINEA aplicatiei, holistic. Instrument: frontend_test/audit_tenant.py <id> --user=<email> (F2 DUK + F7
semafor + F6 axe/mobil; F3/F5 manuale). Metoda = MODEL_AUDIT_TENANT.md (8 fatete, extensibile). Fiecare firma cap-
coada -> rand in ISTORIC_TENANTI.md; roșurile de corectitudine reparate cu tiparul P3 (app-wide) + gard RED-probat.
Criteriu "gata de productie" (AGREAT Costin): fiecare functionalitate a trecut fatetele aplicabile pe >=1 firma cu
date valide+invalide, roșurile de corectitudine reparate, restul documentat ca decizie de produs (NU "zero bug").

COMANDA DE REPORNIRE (gata de dat): "Continua campania colectii date valide+invalide + corectitudine. Instrument:
audit_tenant.py pe matricea 1968 (--user=patron@prisma-cont.test). Reia de la 006. PRIORITATI din re-testul 006 (18.08):
(A) F5 - mesajul D301 'nr_doc gol' EXPUNE numele intern -> rescrie in limba contabilului ('Operatiunea N: completeaza
numarul documentului'); cauta TIPARUL 'nume intern in paranteza' in TOATE mesajele de generare (grep pe erori_generare/
valideaza) si repara app-wide. (B) a11y APP-WIDE (P3, iesit pe 006 SI ALFA): campuri fara eticheta pe fa-stocuri(4)/
fa-registratura(2)/fa-banca(1)/fa-rapoarte(1); contrast pe fa-control(2)/fa-etransport(1)/fa-centrecost(2); mobil
tinte<24px pe fa-casa/fa-banca - reparate cu tiparul + gard test_a11y_touch_target/contrast_tokens extins. (C) apoi
colectii INVALIDE per firma (CSV-uri bad per strat + valori la limita), provocate cu F5, mesaj util. Toate: poarta
verde + rand ISTORIC_TENANTI."

STARE MATRICE (harta F2/F7 pe cabinet 1968, 18.08): DEFECTE REALE = t001 (D112 erori DUK 'asigurat idAsig=4' + cod
boala '91' pe concediu medical), t006 (D301 operatiune fara nr_doc), t009 (D406 factura COER-T5 nereconciliata:
antet net/tva != suma liniilor). SUB-EXERCITATE (fara date de validat) = t005/t011/t012 (au nevoie de DATE, nu de
stergere - regimuri valoroase: profit-trim/startup-partial/tranzitie). REFUZ CORECT by-design (D100 pe zero) =
t002/t009/t017. CURAT F2 = t004/t007/t008/t010. Concluzie firme (agreat): cele 13 ≈ set minim de REGIMURI; nu se
reduc - se umplu cu date. audit_tenant.py: --user mint server-side + F6 + XSD pre-check + user sanitizat (18.08).


## REPORNIRE (comanda exacta, gata de dat) — CAMPANIE: 6 formulare manuale pt declaratiile _DOAR_API
Costin a cerut formulare de introducere manuala pentru 6 declaratii (din cele 41 _DOAR_API care au generator+DUK dar
n-au ecran), in ordinea frecventei la un cabinet SRL: **d710, d311, d307, d107, d177, d207**. Cap-coada fiecare:
(1) parametri cititi din SEMNATURA generatorului (nu presupusi); (2) formular UI pe modelul panoului D301 (clase DS
cap.6, ZERO clase noi, regula 0 citata in cap; identitate intre situatii similare); (3) scos din declaratii_api._DOAR_API
-> apare in GET /declaratii/tipuri; (4) traseu live probat pe firma demo: formular->generare->XML->DUK valid, CAPTURA
PRIVITA. GARDA per declaratie: formular gol nu produce declaratie (refuz backend cu mesaj de CONTABIL, nu nume de camp),
mutatie-probata RED. CSV FUNCTIONALITATI (Stare AMANAT->LIVE) odata cu codul; test_registru_functionalitati verde.

CAMPANIE INCHISA (18.08.2026): GATA toate 6 - d710+d311+d307+d107+d177+d207. Fiecare LIVE, scos din _DOAR_API,
formular UI + gard formular-gol (mesaj de contabil) + DUK valid + Playwright (axe 0/0 + mobil 393). Commit d207: 89c3a26.

GATA (18.08.2026, commit 0392b3b): (1) axe region/landmarks app-wide -> 0 - fix STRUCTURAL in navigator.js
(<header class="bara-antet"> banner peste bara+subbara+bara3; role="dialog"+aria-modal pe ferestre; role="status"
pe toast); scan_region_all.py = 0 pe dashboard + 5 ECRANE; gard core/test_a11y_landmarks.py (RED-probat din
backup-copie). (2) D406 731-738 verificat la sursa (nomenclatorul ANAF) = excludere CORECTA din norma A
(731-738 sunt in planul ONG, nu in bal_soc_com); gard test_conturi_ong_731_738_norma_specifica (ambele laturi).

GATA (18.08.2026, commit dc1ee22): (3) mobil/touch-target AA 2.5.8 pe cele 5 ecrane -> 0 tinte <24px
(.fir-veriga 19->24, .ajutor-btn 20->24, flex-shrink:0 pe controale copil-direct in .fer-larg; bug #pc-cauta
40->20px reparat); gard test_a11y_touch_target. (4) IMPORT: tiparul "motiv de refuz livrat DOAR prin title"
(pierdut pe touch) reparat pe 4 straturi (salariati/asociati CNP, mijloace fixe, istoric) -> motiv VIZIBIL
(span.mig-motiv); probat live tenant_006 (salariati bad_sal.csv); gard test_import_motiv_vizibil.

COMANDA DE REPORNIRE (gata de dat): "Continua auditul tenant_006. RAMAS: provoaca INDIVIDUAL straturile de import
inca neprobate cap-coada - firme (CUI la ANAF), vector_fiscal, solduri_parteneri (cont nepartener / CUI invalid),
plan_conturi (adauga cont: simbol/denumire gol/duplicat) - cu date GRESITE, citind mesajul rendat (limba
contabilului, camp marcat, fara nume interne, obligativitate inainte de buton - Regula 14.4). Metoda Regula 13+14."

**GATA: d710** - formular "Obligatii corectate" (cod 121 micro/103 profit, suma initiala/corecta, cota la micro),
obligatii in memorie -> body, refuz-pe-gol, gard test_d710_formular, CSV F192->LIVE. Model: declaratii.js::randeazaFormularD710.

**GATA: d311** (TVA cod anulat, commit aceasta tura) - PANOU-CAMP (nu lista): data anularii + motiv (oficiu/cerere) +
3 situatii oficiale baze/TVA (livrari / achizitii cu taxare inversa / livrari cu TVA la incasare exigibila dupa anulare),
subtotaluri+total CALCULATE, total de plata LIVE la tastare. Model complet: declaratii.js::randeazaFormularD311 +
_d311Manual + S.d311 (in memorie) + hook-urile pas2 (S.tip==="d311", DOUA locuri: eroare + succes, indentare diferita).
Backend: erori_generare d311.py rescrise in limba contabilului (fara Data_A/d_anul1/OB_51); test_d311 re-ancorat;
gard core/test_d311_formular.py (RED-probat prin sed pe mesaj). Scos din _DOAR_API (ATENTIE: nu sterge si vecinul -
am scos din greseala d307, prins de test_live_accesibil). CSV F207->LIVE + login.js GRUPE_FUNC regenerat
(`python3 genereaza_grupe_functii.py --scrie`, ALTFEL verificatorul RESPINGE commitul: CSV live-count != pagina).
Proba: frontend_test/proba_d311_formular.py (ALFA MICRO 8396; declarant setat via API /firma-profil/date; DUK valid,
axe 0, mobil Pixel5). CUI-uri demo sintetice (301111003) TREC DUK.

**GATA: d307** (ajustare/corectie TVA, commit aceasta tura) - LISTA de operatiuni (model d710): fiecare operatiune tip
(A=transfer active/cedent, L=leasing/finantator, C=anulare cod TVA/beneficiar) + cod fiscal + denumire operator + TVA
(poate fi <=0 la regularizare); tvaA/L/C + total de ajustare CALCULATE (total afisat, recalculat la randare). Model:
declaratii.js::randeazaFormularD307 + _d307Manual + S.d307 (operatiuni in memorie) + hook pas2 (S.tip==="d307", DOUA locuri).
Backend: erori_generare d307.py rescrise in limba contabilului; valideaza_cerere prietenos; gard core/test_d307_formular.py
(RED-probat sed pe denO). Scos DOAR d307 din _DOAR_API. CSV F217->LIVE + GRUPE_FUNC regenerat + registre IN ACELASI commit
(lectia d311). Proba: frontend_test/proba_d307_formular.py (ALFA MICRO, 2 operatiuni tip A+C cu TVA negativ, DUK valid, axe 0, mobil body=393).

**GATA: d107** (informativa sponsorizari/mecenat/burse, commit aceasta tura) - LISTA de beneficiari (model d307):
fiecare beneficiar cu denumire + cod fiscal (CUI/CNP) + adresa + trei sume (acordata Val1 / reportata Val2 / dedusa Val3);
TVal1/TVal2/TVal3 + totalPlata_A (suma de control) CALCULATE si afisate (coincid cu serverul). Anexa neindividualizati
(entit1) intr-un `<details>` colapsat, mini-lista conditionata de Val2_NI>0 (regula validatorului). Model complet:
declaratii.js::randeazaFormularD107 + _d107Manual + S.d107 (in memorie) + hook pas2 (S.tip==="d107", DOUA locuri:
div placeholder + render, indentari diferite 6/4 si 4/2 sp) + id #d107-totaluri. Backend: erori_generare d107.py rescrise
in limba contabilului + valideaza_cerere d107 rescris (NU mai expune `manual.beneficiari` - prins de proba Playwright,
nu de unit); test_d107 re-ancorat; gard core/test_d107_formular.py (RED-probat sed pe Val2_NI). Scos DOAR d107 din
_DOAR_API. CSV F211->LIVE + GRUPE_FUNC regenerat (148) + registre IN ACELASI commit. Proba:
frontend_test/proba_d107_formular.py (ALFA MICRO an 2024, 2 beneficiari, DUK valid, axe 0, mobil body=393).

**GATA: d177** (redirectionare impozit profit -> ONG/cult, commit aceasta tura) - cea mai bogata forma: ANTET (plafoane
suma_max/ant/rest + perioada fiscala) + LISTA de beneficiari, fiecare cu tip (1 cult / 2 alte / 3 mecenat / 5 UNICEF;
4 nepermis), cod fiscal (CUI, CNP la mecenat - eticheta se schimba), denumire, IBAN, suma, acord, contract (obligatoriu
la tip<5, ascuns la UNICEF). Total alocat vs. ramas afisat; suma de control = 0. Model complet: declaratii.js::
randeazaFormularD177 + _d177Manual + _D177_TIPB + S.d177 (in memorie) + hook pas2 (DOUA locuri) + id #d177-totaluri.
Backend: erori_generare + valideaza_cerere rescrise (fara tipB/cuiB/sumaRest/etc); test_d177 re-ancorat; gard
core/test_d177_formular.py (RED-probat sed pe sumaRest). BUG REAL reparat: luna XML derivata din dataSfarsit (dispatch
trimitea luna=6 -> R4.1 respins), aserție regresie in gard. Scos DOAR d177 din _DOAR_API. CSV F210->LIVE + GRUPE_FUNC
(149) + registre IN ACELASI commit. Proba: frontend_test/proba_d177_formular.py (ALFA MICRO an 2025, DUK valid, axe 0, mobil body=393).

**GATA: d207** (LIVRAT 18.08, commit 89c3a26 - ULTIMA, CAMPANIA INCHISA; DUK valid + axe 0/0 + mobil body=393;
nomenclator tip venit SURSAT din structura_D207_2025 cap.III - 25 coduri, impozabile+scutite; suma control 10801
JS=server; scutit->impozit dezactivat+0. LECTIE: RED-proof pe fisier needitat-committed NU cu git checkout -
sterge si editarile necommitate; re-aplica editarea sau foloseste o copie). Istoric metoda: informativa nerezidenti, ULTIMA din
campanie, MANUALA). Citeste core/d207.py (semnatura genereaza + calcul + erori_generare + build_xml) si valideaza_cerere
d207 (linia "d207 cere `manual.beneficiari` (lista de beneficiari nerezidenți)" - de rescris in limba contabilului).
Model LISTA de beneficiari nerezidenti, grupati pe tip_venit (verifica structura la sursa in anaf_surse). DE FACUT identic
cu d177/d107: (1) mesaje contabil in erori_generare SI valideaza_cerere; (2) formular-lista + hook pas2 AMBELE locuri;
(3) scoate DOAR d207 din _DOAR_API; (4) ajutor d207 (F-number in CSV, rand existent); (5) gard test_d207_formular RED;
(6) CSV ->LIVE + GRUPE_FUNC + registre IN ACELASI commit; (7) proba Playwright ALFA MICRO -> DUK valid + axe + mobil.
RESTART OBLIGATORIU dupa scoaterea din _DOAR_API. ATENTIE (lectia d177): ruleaza proba pe traseul REAL, cu default-urile
dispatchului - bug-urile de parametru (ex. luna/perioada) trec de unit-teste dar cad la DUK pe traseu. Cu d207 campania de 6 e INCHISA.
RESTART OBLIGATORIU dupa scoaterea din _DOAR_API (modificare backend, altfel tipul nu apare in selectorul live - prins la d307).

## REPORNIRE (audit tenant_006 - context anterior)
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
(flag d390_posibil_serviciu), ca un serviciu IC ratacit pe tip 4 sa nu ramana absent din D390. Fals-pozitivul
benign (gaz/energie alin.3/5 cu furnizor inregistrat) -> buton "confirma (nu e serviciu)" (coloana
d390_confirmat_local + ruta PUT confirma-local) stinge indiciul reversibil. Confirmarea PERSISTA per-furnizor
(tara+cod): un furnizor confirmat pe orice operatiune stinge indiciul si pe viitoarele lui (alta luna),
marcate "✓ furnizor confirmat local" (derivat din confirmarile existente, fara tabel nou).

## RAMAS deschis (fronturi pt urmatoarea tura)
- [INCHIS 18.08 commit 0392b3b] axe region/landmarks app-wide -> 0 (fix structural navigator.js + gard test_a11y_landmarks).
- [INCHIS 18.08 commit 0392b3b] D406 731-738: verificat la sursa = excludere CORECTA din norma A (sunt in planul ONG); gard intarit.
- [PARTIAL 18.08 commit dc1ee22] Import: reparat tiparul motiv-title-only pe 4 straturi (salariati/asociati/mijloace/istoric)
  -> motiv vizibil, probat live salariati. RAMAS de provocat individual: firme (CUI ANAF), vector_fiscal,
  solduri_parteneri (cont nepartener/CUI), plan_conturi (adauga cont gol/duplicat).
- [INCHIS 18.08 commit dc1ee22] Vizual/mobil (Pixel5): 5 ecrane (import mf, vector, plan conturi, stat plata, declaratii)
  -> 0 tinte <24px (AA 2.5.8), fara revarsare/hover-loss. RAMAS: casa/banca, facturi, produse neanalizate pe telefon.

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
