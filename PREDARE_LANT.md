Citeste CLAUDE.md §2.2 (structura raportului) si §2.3 (lant, siguranta, limba - pct.11 poarta verde vizuala) + ARHITECT.md "FORMA COMENZII" (7 puncte), apoi acest PREDARE_LANT.md, inainte de a incepe.

# PREDARE LANT — audit vizual tenant_005 (Constructii Profit Trim SRL / P2, cabinet 1968); clusterele 1+2 LIVRATE

## REPORNIRE (comanda exacta, gata de dat)
Continua auditul vizual tenant_005 (P2, Constructii Profit Trim SRL) cap-coada cu Playwright (captura PRIVITA +
axe-core + mobil pe fiecare ecran atins - Regula 14 integral), REPARAND ce gasesti; ce gasesti pe o firma cauta pe
toate (Regula 13). Valorile fiscale se verifica la sursa (anaf_surse/*_struct + XSD + DUK), NU se cer de la Costin.
Fiecare gard nou: mutatie probata RED pe cod vechi, prin rulare. DS inainte de orice cod de interfata, cu capitolul
citat. DUPA ORICE editare static/js: `versioneaza_assets.py --scrie` INAINTE de commit (altfel poarta rosie).
PUNCTUL LA CARE AM RAMAS: clusterele 1 (import salariu_brut, 5dd0dc2) + 2 (semnal baza lipsa + editare salariu,
b642d8e) LIVRATE. Ionescu Marin (tenant_005) are ACUM salariu 5000 (reparat prin noul buton). RAMAS, in ordinea comenzii:
- **FRONT B (URMATORUL) - restul straturilor de migrare (8 din 9)**: doar stratul Salariati auditat cap-coada.
  NEatinse: import firme, Vector fiscal, Solduri initiale, Solduri parteneri, Asociati, Mijloace fixe, Istoric
  declaratii, Plan de conturi, Articole/stoc initial. Fiecare: import->preview->salvare->confirmare->ecran, cu
  blocaje provocate la preview (fisiere stricate, coloane lipsa, valori invalide).
- **FRONT C - operarea P2**: Facturi/Banca/Casa neauditate in adancime. Observat: "2 facturi emise necontabilizate"
  (T6 taxare inversa 40000 + factura normala 12100 din 08.2026 NU sunt contabilizate pe cont 70x -> D100 nu se depune
  pe zero, CORECT semnalat). De verificat fluxul de contare a facturilor emise (Registru jurnal / contare pe 70x).
- **FRONT D - declaratiile ramase la XML+DUK**: DONE (DUK valid) D300 Q2/Q3, D394 Q2/Q3 (codPR 27 taxare inversa
  cladiri_terenuri, verificat in XML), D406 L9. D100 blocheaza CORECT pe zero. RAMAS: D112 (ACUM auditabil - Ionescu
  are salariu 5000; de generat + DUK, atentie construcții CAEN 4321 = facilitatea art.60 pt.5 / minim sectorial),
  D101/D205 anuale, Bilant S1005 (blocat CORECT de "Nr. registrul comertului lipsa"). Wizard pas 3 (coada) NEATINS.
- **FRONT E (mic, gasit cluster 2) - editarea celorlalte campuri ale salariatului**: butonul "Salariu" cableaza
  editarea salariului; dar nume/CNP/data_angajare/norma tot NU se pot edita din UI (doar IBAN/COR/incetare/salariu +
  creare). O greseala de nume/CNP la un salariat existent nu se poate corecta din ecran. Cluster separat (form de editare).

## FOUR-WAY (de confirmat de urmatoarea tura)
Comituri livrate aceasta tura: 5dd0dc2 (import salariu_brut), 1c5ab0c (PREDARE cluster 1), b642d8e (semnal baza
lipsa + editare salariu), + acest PREDARE. Poarta verde pe fiecare: 2276->2278 passed, verificator TOTAL 0.
Post-commit publica origin/main + backup/lant-2026-08-17 + restart iconta-nou automat. HEAD = origin/main = backup.
RUNNING confirmat BEHAVIORAL pe fiecare prin proba vizuala (importul respinge; semnalul baza_lipsa apare si dispare
la editare). Sentinele PUSH_*_ESUAT absente.

## LIVRAT (clustere RED-probate + vizual/DUK)
1. **Import salariati: salariu_brut obligatoriu si > 0** (5dd0dc2). verifica_randuri respinge brut lipsa/0/negativ
   (motiv salariu_lipsa) - coloana absenta fabrica 0.0 tacit (DS cap.17). Mesaj vizibil prin gateazaPreview. Gard
   test_salariu_brut_lipsa/negativ_e_respins. axe/mobil import: fara-eticheta 0, title-only 0.
2. **Stat de plata: semnal baza lipsa + editare salariu cablata** (b642d8e). (a) stat_plata intoarce baza_lipsa +
   salariu_baza; cardul arata badge rosu "salariu de baza lipsa" + sub-linie explicativa (net 0 dar cost 825 din
   suprataxa sub-minim art.146(5^6)/168(6^1)), cifrele vizibile dar EXPLICATE (MEMORY §13). (b) buton "Salariu"
   cableaza PUT /salariati/{id} {salariu_brut, valabil_din} (necablat pana acum; SalariatEdit.valabil_din adaugat) -
   editarea/marirea salariului nu exista in UI. Schimbare = UPSERT pe istoric la data. Gard
   test_stat_plata_semnaleaza_baza_lipsa (KeyError pe cod vechi) + test_editarea..._dateaza_istoricul. Vizual: badge
   apare pe Ionescu (brut 0), dispare dupa editare (brut 5000 -> cost 5112.50 coerent). axe/mobil Stat plata:
   fara-eticheta 0, title-only 0; pre-existent contrast 14, tinte <44px 29, info-touch 3.

## VERIFICAT SI CURAT (nu sunt defecte)
- Vector fiscal P2 (profit/platitor/T/fara IC) corect; D300/D394 pe trimestru trec DUK; D394 codPR 27 taxare inversa
  cladiri_terenuri verificat in XML. Dropdown declaratii: d301/d390 "nu se datoreaza" cu motiv. Date firma banner
  "Nr. registrul comertului lipsa -> blocheaza Bilant S1005" precis. Casete SEPA/REGES indisponibile vizibile.

## BACKLOG (mostenit din tenant_001, tot deschis)
D112 podea part-time (FRONT #1 t001, cere autoritate externa), E7 cod boala 17, umbrire strat migrare, mesaj TVA
semafor diacritice, D406 SAF-T micro. Infra vizuala (contrast, tinte <44px) - Costin da ordinea.
