Citeste CLAUDE.md §2.2 (structura raportului) si §2.3 (lant, siguranta, limba) inainte de a incepe.

# PREDARE LANT — 03.08.2026

Sesiune noua, context gol. Comanda de pornire: "Citeste PREDARE_LANT.md si continua lantul."
Raspunde in ROMANA. Server: `ssh iconta`, `~/iconta_nou` (branch main). Rulezi pytest/DUK/verificator/commit PE SERVER.

## Ritual de pornire (§5)
1. `git log --oneline -1` -> HEAD asteptat: **a9634c3** (sau mai nou). `git status --porcelain` -> TREE_CURAT.
2. `venv/bin/python -m pytest -q` -> asteptat ~1328 passed, 2 skipped, 21 xfailed. `verificator` -> 0 candidate.
3. `venv/bin/python3 -c "from core import agenda; print(agenda.urmator_cluster())"`
   -> **(('checksum totalPlata_A', 'd205'), 21, 1)** = urmatorul cluster, 21 ramase, 1 blocat (preexistent).

## Urmatorul cluster: checksum totalPlata_A | d205
D205 = declaratia informativa privind impozitul retinut la sursa (dividende etc.). Verifica checksum-ul
totalPlata_A (suma de control). Tipar deja facut identic pe d100 (cluster "checksum totalPlata_A (R11b)",
commit f26be10) si d101 - probabil VERIFICARE: totalPlata_A = suma obligatiilor, aliniat la sursa unica,
proba DUK daca poate_valida('d205'). Verifica formula la sursa (structura D205 in anaf_surse/ + regula DUK R11b
daca exista). Daca e conform, gard golden pe checksum; daca difera, red->green.

## Ce am facut in rularea asta (5 clustere, toate verzi + push la backup/lant-20260803)
- **scadente/nr_evidenta | d100** (c83fffb): verificare - nr_evidenta 23 poz conform + scadenta 25 luna urmatoare; gard scadenta adaugat.
- **structura P1-P53 | d101** (48352fb): verificare conform+complet OPANAF 206/2025, deja gardat golden+DUK.
- **R17 Data_S / termen | d101** (2f0a81d blocaj -> c00c522 rezolvat): NECONFORMITATE APARENTA care s-a dovedit
  falsa. Scadenta D101 parea inversata fata de lege, DAR valoarea validatorului DUK (2022-2025 -> 25 iunie) e
  LEGAL CORECTA via **OUG 153/2020 art.I alin.(13) lit.a** (derogare art.42, aplicabil 2021-2025, MO 817/04.09.2020)
  - prima cercetare ratase actul. 2026 -> 25 martie baza art.42 = ce cere jar-ul DUK; OUG 8/2026 il muta la iunie
  de la fiscal 2026 cand ANAF actualizeaza validatorul (depunere in 2027; probele DUK pe an=2026 vor pica automat).
  DECIZIE COSTIN: tool-ul urmeaza VALIDATORUL pe ambele ramuri (functia lui = declaratii acceptate de ANAF). Vezi
  DECIZII.md 03.08 + anaf_surse/d101_scadenta_conflict_lege_validator.md. LECTIE: cand un cluster "verifica" cu
  proba DUK, valoarea DUK-valida poate parea sa contrazica textul - verifica daca exista o derogare temporara
  (OUG) inainte de a declara neconformitate.
- **limita text 75 | d112** (fd63231): 2 neconformitati reparate - numeAsig/prenAsig (nume salariat C75) erau
  netrunchiate; functie_declar are C(50) nu 75, se trunchia la 74. Reparat + gard.
- **nomenclator cod_oblig | d112** (a9634c3): verificare conform - toate 6 codurile cod_oblig<->cod_bugetar
  coincid cu nomenclatorul ANAF (480 CAM are 20470300XX distinct); gard nou pe cod_bugetar.

## Reguli permanente
- NU face push pe main (decizia c a lui Costin). Push de siguranta la finalul rularii: `git push -f origin
  HEAD:backup/lant-20260803`. Ultimul facut la a9634c3.
- Nu opri lantul la granite curate. Continua pana la un criteriu §2.3: blocat / decizie de produs / neconformitate
  care cere oprire / poarta rosie sau tree murdar / context efectiv epuizat. Limita de 6/rulare a fost ELIMINATA.
  "Ca sa dirijeze Costin ordinea" NU e criteriu - ordinea o da agenda.
- Fiecare cluster: red->green (daca fix) sau verificare, gard §9, raport §2.2 sectiuni 1-10, DECIZII/GARZI/TESTE
  actualizate, Inventar A bifat √, secventa regenerata, consistenta secventa==calculata, commit LOCAL.
- Gard anti-stale test_agenda: bifa Inventar A merge in ACELASI commit doar daca testul e intr-un fisier care
  EXISTA deja in git; fisier de test NOU -> 2 commituri (cod+fisier intai, bifa dupa).
- §3: nu construi pe temei neverificat (xfail strict); daca textul difera de intelegere, TEXTUL CASTIGA. DAR
  atentie la derogari temporare (OUG) care nu-s in textul consolidat curent - vezi lectia R17.

## Datorii deschise (in DECIZII.md, campania "achitare datorii" - blocaje motivate, de reluat separat de lant)
A2 (D390 ziua 15 schema change), A3 (D177 form - descarca structura ANAF intai), C1/C2 (tichete cresa/culturale
research MO), C3 (amortizare MF neliniara xfail), C4 (D112 avantaje sectiunea 8.3), C5 (migrare tichete culturale).
Plus subsistemul mijloace fixe (xfail test_datorie_mf_metode_amortizare) - amortizarea fiscala intra ca input P11
in d101, calculata extern; nu afecteaza d101.

## Xfail-uri (21) = registrul de datorie (test_datorie.py). Toate legitime, verificate mecanic. Nu le "repara"
fara sa citesti motivul - unele apara buguri prin design (documenteaza valoarea corecta pana la o Faza ulterioara).
