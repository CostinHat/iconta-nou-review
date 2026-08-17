Citeste CLAUDE.md §2.2 (structura raportului) si §2.3 (lant, siguranta, limba - pct.11 poarta verde vizuala) + ARHITECT.md "FORMA COMENZII" (7 puncte), apoi acest PREDARE_LANT.md, inainte de a incepe.

# PREDARE LANT — audit vizual tenant_005 (Constructii Profit Trim SRL / P2, cabinet 1968); clusterele 1+2+3 LIVRATE

## REPORNIRE (comanda exacta, gata de dat)
Continua auditul vizual tenant_005 (P2, Constructii Profit Trim SRL) cap-coada cu Playwright (captura PRIVITA +
axe-core + mobil pe fiecare ecran atins - Regula 14 integral), REPARAND ce gasesti; ce gasesti pe o firma cauta pe
toate (Regula 13). Valorile fiscale se verifica la sursa (anaf_surse/*_struct + XSD + DUK), NU se cer de la Costin.
Fiecare gard nou: mutatie probata RED pe cod vechi, prin rulare. DS inainte de orice cod de interfata, cu capitolul
citat. DUPA ORICE editare static/js: `versioneaza_assets.py --scrie` INAINTE de commit (altfel poarta rosie).
PUNCTUL LA CARE AM RAMAS: clusterele 1 (import salariu_brut, 5dd0dc2), 2 (semnal baza lipsa + editare salariu,
b642d8e), 3 (import articole stoc-fara-pret, ec4923f) LIVRATE. RAMAS, in ordinea comenzii:
- **FRONT B (URMATORUL) - ECRANELE straturilor de migrare 2-9**: am facut sweep pe VALIDATORII de import (backend,
  Regula 13) - toti curati acum (doar salariu_brut + articole aveau gap-ul, reparate). RAMAS: parcurgerea VIZUALA a
  ecranelor fiecarui strat (import->preview->salvare->confirmare->ECRANUL unde apar datele), cu blocaje provocate la
  preview: Vector fiscal, Solduri initiale, Solduri parteneri, Asociati, Mijloace fixe, Istoric declaratii, Plan de
  conturi. NEparcurse vizual (doar salariati + articole parcurse cap-coada).
- **FRONT C - CURAT (verificat)**: "facturi emise necontabilizate" = design normal (jurnal_api: "AI propune ciorna,
  contabilul valideaza"); nota e ciorna nepostata, D100 exclude corect venitul nepostat. NU e defect.
- **FRONT D - declaratiile ramase la XML+DUK**: DONE (DUK valid) D300 Q2/Q3, D394 Q2/Q3 (codPR 27 taxare inversa
  cladiri_terenuri verificat in XML), D406 L9. D100 blocheaza CORECT pe zero. RAMAS: D112 (auditabil - Ionescu are
  salariu 5000; construcții CAEN 4321 - VERIFICA la sursa daca facilitatea art.60 pt.5 e in vigoare 2026 sau abrogata
  inainte de a decide daca lipsa scutirii e defect; azi impozit 266.61/CASS 500 = NEscutit), D101/D205 anuale, Bilant
  S1005 (blocat CORECT de "Nr. registrul comertului lipsa"). Wizard pas 3 (coada) NEATINS pe nicio declaratie.
- **FRONT E (mic) - editarea celorlalte campuri ale salariatului**: butonul "Salariu" cableaza editarea salariului;
  nume/CNP/data_angajare/norma tot NU se pot edita din UI (doar IBAN/COR/incetare/salariu + creare). Cluster separat.

## FOUR-WAY (de confirmat de urmatoarea tura)
Comituri livrate aceasta tura: 5dd0dc2, 1c5ab0c (PREDARE), b642d8e, 5d260be (PREDARE), ec4923f, + acest PREDARE.
Poarta verde pe fiecare: 2276->2279 passed, verificator TOTAL 0. Post-commit publica origin/main +
backup/lant-2026-08-17 + restart iconta-nou automat. HEAD = origin/main = backup. RUNNING confirmat BEHAVIORAL prin
proba vizuala pe fiecare (importurile resping; semnalul baza_lipsa apare/dispare). Sentinele PUSH_*_ESUAT absente.

## LIVRAT (clustere RED-probate + vizual)
1. **Import salariati: salariu_brut obligatoriu** (5dd0dc2). verifica_randuri respinge brut lipsa/0/negativ.
2. **Stat de plata: semnal baza lipsa + editare salariu cablata** (b642d8e). stat_plata.baza_lipsa + buton "Salariu"
   (PUT /salariati/{id} {salariu_brut, valabil_din}); reparata data reziduala Ionescu (0->5000).
3. **Import articole: stoc-fara-pret invalid** (ec4923f). extrage respinge cant>0 & pret<=0 (valoare stoc 0 tacita).
   Generalizarea Regula 13: sweep pe TOTI validatorii de import - doar salariu_brut + articole aveau gap-ul.
Toate cu gard RED->GREEN, axe/mobil pe ecranul atins (fara-eticheta 0, title-only 0; contrast/tinte pre-existente).

## VERIFICAT SI CURAT (nu sunt defecte)
Vector fiscal P2 (profit/platitor/T/fara IC); D300/D394 pe trimestru trec DUK; D394 codPR 27. Dropdown declaratii:
d301/d390 "nu se datoreaza" cu motiv. Date firma banner "Nr. reg com lipsa -> blocheaza Bilant" precis. Casete
SEPA/REGES indisponibile vizibile. Facturi necontabilizate = ciorna nepostata (design). Validatorii de import 2-9
(mijloace fixe/solduri/istoric/retete/parteneri/asociati): curati (asociati - reziduu ingust, neridicat la GAP).

## BACKLOG (mostenit din tenant_001, tot deschis)
D112 podea part-time (FRONT #1 t001, cere autoritate externa), E7 cod boala 17, umbrire strat migrare, mesaj TVA
semafor diacritice, D406 SAF-T micro. Infra vizuala (contrast, tinte <44px) - Costin da ordinea.
