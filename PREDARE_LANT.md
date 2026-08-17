Citeste CLAUDE.md §2.2 (structura raportului) si §2.3 (lant, siguranta, limba - pct.11 poarta verde vizuala) + ARHITECT.md "FORMA COMENZII" (7 puncte), apoi acest PREDARE_LANT.md, inainte de a incepe.

# PREDARE LANT — audit vizual tenant_001 (Panificatie Salarii Speciale SRL, cabinet 1968); 1 cluster de cod reparat

## REPORNIRE (comanda exacta, gata de dat)
Continua auditul vizual tenant_001 cap-coada cu Playwright (captura PRIVITA, nu selectoare - Regula 14),
REPARAND ce gasesti; ce gasesti pe o firma cauta pe toate (Regula 13). Punctul la care am ramas: parcurse
VIZUAL ecranele de sus (meniu firma 26 module, Import=10 straturi LISTATE, Date firma+vector, Salariati=Stat
plata 12 salariati, semafor Control fiscal, Declaratii wizard, Casa/Banca/Facturi=goale/meniu). Reparat +
livrat: default fabricat pe selecturile vector din Date firma. D112 dus la XML+DUK pe O luna (06/2026).
RAMASE, NEATINSE (prioritatea sus):
- **D112 celelalte luni + Trimite in coada**: doar 06/2026 dus la Pas 2 (DUK). ian-mai, iul-aug neparcurse; Pas 3
  (coada) neatins pe nicio luna.
- **ATENTIONARE DUK D112 nerezolvata** (vezi FRONTURI #1) — cifra part-time posibil gresita.
- **Cele 9-10 straturi migrare INDIVIDUAL**: import->preview->salvare->confirmare->ecran. Doar meniul Import
  privit (straturile listate). tenant_001 are plan_conturi(185)+salariati(12)+concedii(11)+istoric(30) populate;
  restul goale. Niciun strat parcurs cap-coada; blocaje la PREVIZUALIZARE (fisier stricat) NEPROVOCATE.
- **Salariati in adancime**: doar Stat plata privit. Fluturas/REGES/Concediu/Adeverinta/Pontaj/Incetare pe
  salariat + "+Salariat nou" cu campuri goale (blocaj) + "Fisier plata card (SEPA)" fara IBAN + "Chei REGES"
  fara COR — NEPROVOCATE (vezi FRONTURI #5).
- **Declaratii ramase**: D100 (micro; ACUM regim_fiscal=NULL dupa fix -> semaforul zice "necompletat", de
  confirmat ca D100 refuza corect din ECRAN), D300/D394 (blocate vector), Bilant S1005 (blocat reg_com), D205
  (fara note 2025). Duse la XML+DUK: DOAR D112.
- **axe-core + mobil pe ecranele atinse** (Date firma, Salariati, Declaratii) — Regula 14 addendum, NEFACUT.

## FOUR-WAY (executat automat de post-commit, 17.08.2026)
HEAD = origin/main = backup/lant-2026-08-17 (remote) = RUNNING = **59f4fec**. Service ActiveEnter 06:42:20 >
commit 06:34:04 (procesul viu preia 59f4fec). pytest 2264 passed / 0 failed / 4 skipped / 16 xfailed;
verificator TOTAL scanat 130 = ACCEPTAT 129 + GRI 0 + ROSU 0 + EXCLUS 1 -> TOTAL 0. Poarta verde curata.
NOTA: prima incercare de commit a fost RESPINSA de test_versionare_assets.py (?v= manual sha1sum != hashul
uneltei); reparat cu `venv/bin/python3 versioneaza_assets.py --scrie` (NU stampila ?v= manual - exista gard).

## LIVRAT ACEASTA TURA (1 cluster, cu 2 garzi RED-probate + proba vizuala)
**Default fabricat pe selecturile vector din Date firma** (regim_fiscal/platitor_tva/operatiuni_ic).
Selectul obligatoriu FARA optiune-goala afisa prima optiune ("Microintreprindere"/"Nu") cand valoarea
stocata era NULL -> contrazicea semaforul ("necompletat", Regula 14.2); la Salvare se persista tacit alegerea
fabricata (Regula 4). backend salveaza facea bool(platitor_tva) -> None->False tacit (asimetric cu
operatiuni_ic care era deja corect). Fix in 2 jumatati:
- backend vector_fiscal_api.salveaza respinge platitor_tva=None (TVA_LIPSA); main.py VectorIn.platitor_tva
  Optional[bool]; citeste() expune partida_simpla (PFA n-are regim).
- frontend date_firma.js: alege:true + placeholder "— alege —" + tri-stare la salvare + validare preventiva
  langa camp. firme.js bump ?v=.
Probe: proba_regim_placeholder.py (selecturile arata "— alege —", Salvarea blocheaza cu mesaje per-camp, DB
ramane NULL). Garzi: test_vector_platitor_tva_oblig.py (backend fake-conn), test_date_firma_alege_placeholder.py
(frontend source-scan). Ambele RED pe cod vechi (rulat pe git HEAD:date_firma.js) -> GREEN.

## FRONTURI DESCHISE (gasite aceasta tura, NEREZOLVATE — pentru decizie/tura viitoare)
1. **ATENTIONARE DUK D112 part-time** (E4 idAsig=4, luna 06/2026 H1): `SP1B4_1: B4_5P(4050) diferit de suma
   calculata 3750`. Non-blocant (atenționare), dar inconsistenta INTERNA in XML: aplicatia pune 4050 in B4_5P,
   DUK sumeaza 3750 din celelalte campuri B4. E4 = part-time sub floor (brut 3000). Sector alimentar
   (CAEN 1071 panificatie) cu facilitate -> floor CASS = sm-facilitate = 3750. De rezolvat: (a) verifica legal
   baza minima CAS/CASS part-time sub floor la sector cu facilitate (Regula 5); (b) confrunta cu anaf_surse
   D112_struct + XSD ce e B4_5P si ce sumeaza SP1B4_1; (c) test_d112 part-time existent pineaza 4050 sau 3750?
2. **`declarant_functie or "ADMINISTRATOR"`** (core/d112.py:166): default fabricat (Regula 4) pe functia
   declarantului cand firma_profil.declarant_functie=NULL. tenant_001 are NULL -> D112 emite
   functie_declar="ADMINISTRATOR" inventata. Aceeasi clasa cu clusterul reparat, dar in D112 antet. De decis
   daca se cere explicit (ca regim/tva) sau e acceptat.
3. **Umbrire strat migrare** (Import date, ecran): randurile Plan de conturi/Articole/Retete apar umbrite
   subtil, dar Salariati NU — desi tenant_001 are plan_conturi(185)+salariati(12) cu date si articole(0)/
   retete(0) goale. Daca umbrirea = "stratul are date", e gresita in ambele sensuri. NEINVESTIGAT la sursa
   (migrare.js). Reper: "badge stare per strat" front C3 din predarea t004.
4. **Mesaj TVA semafor cu nume intern + fara diacritice** (LOCALIZAT): sursa = **core/common.py:57-58**
   ("LIPSA tip_decont (perioada fiscala TVA) in vectorul firmei - obligatoriu pentru decontul de TVA
   (D300/D394). Completeaza lunar/trimestrial in vectorul fiscal."). User-facing CONFIRMAT (vazut pe ecranul
   Control fiscal, sectiunea DECLARATIE VS CONTABILITATE) — expune `tip_decont`, fara diacritice (Regula 14.4).
   GAURA DE GARDA: test_control_fiscal_diacritice.py scaneaza DOAR control_fiscal_api.py, deci NU vede mesajul
   din common.py. Fix: rescrie mesajul cu diacritice + label UI ("Periodicitate TVA", nu tip_decont) SI extinde
   gardul sa scaneze common.py (sau modulul care ridica exceptia afisata). Mutatie RED: mesajul curent pica noul
   gard. NEREZOLVAT (al doilea cluster, neinceput ca sa nu las cod neprobat in bugetul turei).
5. **COR ⚠ / IBAN ⚠ pe toti 12 salariatii**: reale (cor=None, iban=None pe toti). COR obligatoriu la REGES
   (NU D112 — d112.py nu consuma coloana cor); IBAN obligatoriu la fisierul SEPA. Seed a inserat direct,
   ocolind API-ul care cere COR ("Ocupatia (cod COR) este obligatorie" in salariati_api.py — ruptura
   seed↔consumator, Regula 10). De provocat: "Fisier plata card (SEPA)" fara IBAN + "Chei REGES" fara COR,
   citeste mesajele (spun ce lipseste, unde, ce consecinta?).

## BACKLOG (mostenit din predarea tenant_002, tot deschis)
Tensiune semafor D100 micro pe zero (decizie de politica). D406 SAF-T datorat de micro neplatitor (verifica
periodicitatea la sursa). Clasa "erori generare dXXX fara diacritice". Prefix "Bilant nu se poate genera" fara
diacritice. Backlog t004: d406 divergenta factura COER-T5; Q9/Q18/Q7/Q8/Q12/Q14. Constatari infra vizuala
(contrast, title-extra, tinte <44px) - Costin da ordinea.
