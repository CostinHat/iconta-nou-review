# PREDARE LANT — oprire pentru context (03.08.2026)

Predare scrisa pentru o sesiune NOUA cu context GOL (§2.3 pct.6). Contine tot ce trebuie ca sa continui
lantul de clustere fara sa fi citit sesiunea anterioara.

## HEAD si stare
- **HEAD:** `213c23f` · tree curat (`git status --porcelain` gol) · **ahead 24 fata de origin/main, NEPUSHAT**.
- **Poarta la oprire (toate VERZI):** `pytest` EC=0 (1284 collected, ~1261 passed / 2 skipped / 20 xfailed);
  `verificator_conformitate.py` TOTAL 0; tree curat. Oprire la stare sanatoasa (nu pe rosu).
- **Push:** decizia EXCLUSIVA a lui Costin (decizia c). NU impinge. Commite local si continua.

## Sold lant (aceasta rulare)
`SOLD LANT: 2 clustere inchise / 1 blocaj deschis / 0 xfail deschise nou / HEAD start 368091a -> curent 213c23f`
- Inchise: **tichete cresa** (√ 02.08) + **cota profit 16% + IMCA** (√ 03.08).
- IMCA (CF art.18^1) a fost implementat in aceasta rulare (era xfail; acum inchis, sold datorii 20).

## Clusterul URMATOR (mecanic)
Ruleaza `python3 -c "from core import agenda; print(agenda.urmator_cluster())"`.
La predare intoarce: **`('amortizare', 'd101')`, 59 ramase, 0 blocate.**
- Amortizare | d101 = verificare de SUBSISTEM (CF art.28 amortizare fiscala: metode liniara/degresiva/accelerata
  + durata normala de utilizare Catalog HG 2139/2004). d101 ia amortizarea ca INPUT (P-fields deduceri fiscale
  P23-P33); calculul traieste in subsistemul mijloace fixe (core/reevaluare.py, core/mijloace_fixe_import_api.py,
  core/leasing.py, core/inventariere.py). NU e un castig rapid - cere citit CF art.28 + codul de amortizare la sursa.

## Blocaje deschise (cu motiv)
1. **Plafon indexat tichete cresa** (>450 lei/luna/copil, ex. 740/2026) - GRI (verdict 17). Ordinul MF/MMSS
   368/179/2026 nu s-a obtinut la sursa primara (mmuncii.gov.ro HTTP 503 persistent). `common.plafon_cresa()`
   aplica baza confirmata 450/copil (L165 art.19(1)) si BLOCHEAZA grant-urile peste baza. Se deblocheaza cand
   ordinul e obtinut la MO si adaugat ca fereastra in `plafon_cresa` (ca la `plafon_cultural`). Consemnat in
   DECIZII.md + GARZI.md. NU e xfail (cf. §2.3 pct.3: GRI = blocheaza si merge mai departe).
2. **Gap minor cota profit** (nu blocheaza, nu e datorie): d101 foloseste literalul `COTA_STANDARD=16` in loc de
   `cota("impozit_profit")` period-aware - valoarea 16% e corecta (CF art.17), rutarea prin COTE = follow-up.

## Registre atinse in aceasta rulare
- **DECIZII.md:** intrari tichete cresa; cota profit + IMCA (partial, apoi IMCA implementat/inchis).
- **GARZI.md:** garduri cresa + IMCA; contoare 1277 -> 1284 teste.
- **TESTE.md:** index tichete cresa √ 02.08 + cota profit √ 03.08; secventa 61 -> 60 -> 59 (renumerotata).
- **CLAUDE.md:** §2.3 CONTINUITATE INTRE CLUSTERE + REGIM DE LUCRU IN LANT NESUPRAVEGHEAT (pct.1-6) - regulile lantului.
- **anaf_surse/:** HG 1506/2024 + HG 146/2026 (salarii minime, din campania cresa/CM4).

## Cum continui (sesiune noua)
1. Citeste CLAUDE.md §2.2 (structura raportului) + §2.3 (regim de lant).
2. Ruleaza `agenda.urmator_cluster()` -> porneste campania pentru clusterul indicat (amortizare | d101).
3. Verifica temeiurile la sursa (anaf_surse/ intai; daca lipseste, cauta la sursa oficiala si SALVEAZA - decizia d).
4. Increments testate (rosu->verde->mutatie), commit local per increment, gard + registru la inchidere.
5. Limita: max 6 clustere/rulare (ai facut 2 in rularea anterioara - contorul se reseteaza la sesiune noua).
6. Sterge acest fisier (PREDARE_LANT.md) dupa ce ai reluat lantul.
