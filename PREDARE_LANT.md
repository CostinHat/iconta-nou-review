Citeste CLAUDE.md §2.2 (structura raportului) si §2.3 (lant, siguranta, limba) inainte de a incepe.

# PREDARE LANT — 03.08.2026 (rularea 3)

Sesiune noua, context gol. Comanda de pornire: "Citeste PREDARE_LANT.md si continua lantul."
Raspunde in ROMANA. Server: `ssh iconta`, `~/iconta_nou` (branch main). Rulezi pytest/DUK/verificator/commit PE SERVER.

## Ritual de pornire (§5)
1. `git log --oneline -1` -> HEAD asteptat: **93b01a6** (sau mai nou). `git status --porcelain` -> TREE_CURAT.
2. `venv/bin/python -m pytest -q` -> asteptat ~1336 passed, 2 skipped, 21 xfailed. Verificator: `venv/bin/python3
   verificator_conformitate.py` -> TOTAL 0 candidate.
3. `venv/bin/python3 -c "from core import agenda; print(agenda.urmator_cluster())"`
   -> **(('nomenclator tari (HR->CR)', 'd390'), 17, 1)** = urmatorul cluster, 17 ramase, 1 blocat (preexistent).

## Urmatorul cluster: nomenclator tari (HR->CR) | d390
D390 = declaratia recapitulativa livrari/achizitii intracomunitare. Verifica nomenclatorul de tari - in special
maparea HR (Croatia ISO) -> cod ANAF. Tipar probabil VERIFICARE: codurile de tara emise = nomenclatorul oficial ANAF
(OPANAF 705/2020 sau structura D390). Vezi core/d390.py (`_tara_xml`, linia ~102) + anaf_surse/ pt D390. Daca e
conform, gard pin pe mapare; daca difera, red->green. NOTA: clusterele d390 anterioare (tipuri operatiune IC,
rotunjire, reclasificari, exigibilitate) sunt INCHISE - vezi Inventar A.

## Ce am facut in rularea asta (4 clustere verzi + 1 schimbare de guvernanta; HEAD b2c3b60 -> 93b01a6)
- **GUVERNANTA (cerere Costin mid-tura)** (c1a679c): CLAUDE.md §2.3 pct.6 - PREDAREA trimite EXPLICIT la reguli.
  Prima linie a oricarui PREDARE_LANT.md e trimiterea la §2.2/§2.3 (vezi prima linie a acestui fisier). O sesiune
  noua citeste regulile INAINTE de primul cluster.
- **checksum totalPlata_A | d205** (3a1f69c): VERIFICARE valoare emisa conforma (nrben+Tcastig+Tpierd+T_VB+T_GAR+
  Tbaza+Timp, OPANAF 102/2025 l.80-85, DUK-valid) + ALINIERE sursa unica. Capcana latenta clasa-d100:
  res.total_plata_a tinea DOAR Timp (nu checksum-ul), build_xml recalcula independent - d205 era ULTIMUL outlier de
  la conventia res.total_plata_a==totalPlata_A emis (d100/d101/d300/d390/d710). FIX: calcul_d205 calculeaza checksum
  ->res, build_xml il emite. Invariantul e acum UNIVERSAL pe toate generatoarele cu checksum.
- **trunchiere den/adresa | d205** (bbf1967): NECONFORMITATE reparata, PROBATA DUK boundary-cu-boundary. Campurile
  text se trunchiau la 75 (default text_anaf), dar struct D205 + DUK dau: den C(200) (200 valid/201 erori), adresa
  C(1000) (1000/1001), functie_declar C(50) (50/51), den1 beneficiar C(100) (100/101). den/adresa OVER-trunchiate=
  pierdere date; functie 51-75 si den1 >100 (netrunchiat) RESPINSE de ANAF. FIX: limite explicite _t(...,200/1000/
  50/100) in build_xml. LECTIE: text_anaf default 75 e doar pt C(75); orice alt camp paseaza limita EXPLICIT.
- **randuri / checksum | d300** (8192249): VERIFICAT CONFORM + gard golden. totalPlata_A=suma(camp 27..124) cu 62/63
  (rd14.1/14.2=R67/R68) ELIMINATE; res.total_plata_a=sum(res.R) sursa unica; R67/R68 nu-s in allow-list -> excluse
  prin constructie. Probat total==sum==7810==DUK-valid + R67/R68 manual->ValueError. Gard golden+pin adaugat.
- **checksum totalPlata_A (R28) | d301** (93b01a6): VERIFICAT CONFORM (fara fix). totalPlata_A=INT(sum baza1..5+
  tva1..5) toate 5 tipurile, DUK R28; res=sum, build_xml emite res (sursa unica). Deja gardat golden 12044+DUK in
  clusterul rollup; adaugat gardul de legatura EXPLICITA res==emis==suma toate tipurile.

## DATORIE NOUA DESCHISA (importanta - de reluat): limita text pe TOATE declaratiile
Docstring-ul lui text_anaf (27.07) sustine ca D300/D301/D390/D394/D112 RESPINGEAU empiric atribute >75, si de aceea
s-a pus trunchiere BLANKET la 75. Aceasta afirmatie e acum INFIRMATA de proba DUK pe DOUA declaratii: D205 (den/adresa
accepta 200/1000) si D300 (adresa accepta 152). Deci adresa/den din D300 (si probabil D301/D390/D394/D112) sunt
OVER-trunchiate la 75 = PIERDERE DE DATE tacuta pe adrese/nume reale (adresele reale depasesc frecvent 75).
RECOMANDARE: cluster/audit dedicat "limita text" pe fiecare declaratie din lista - limitele reale = din structura
FIECARUI formular, verificate pe DUK, NU 75 uniform. NU l-am reparat (in afara scopului clusterelor din rularea asta).
Consemnat in DECIZII.md (cluster randuri/checksum d300, sectiunea OBSERVATIE).

## Reguli permanente (rezumat - detaliile in CLAUDE.md §2.2/§2.3)
- NU push pe main (decizia c). Push de siguranta la finalul rularii: `git push -f origin HEAD:backup/lant-20260803`.
  Ultimul facut la 93b01a6.
- Nu opri lantul la granite curate. Continua pana la un criteriu §2.3: blocat / decizie de produs / neconformitate
  care cere oprire / poarta rosie sau tree murdar / context efectiv epuizat. "Ca sa dirijeze Costin ordinea" NU e
  criteriu - ordinea o da agenda. Oprirea rularii asta = CONTEXT (pct.6), la granita curata 93b01a6.
- Fiecare cluster: red->green (daca fix) sau verificare, gard §9, raport §2.2 sectiuni 1-10, DECIZII/GARZI/TESTE
  actualizate, Inventar A bifat √, secventa regenerata (renumerotare DOAR pe blocul secventei - ATENTIE sa nu atingi
  alte liste numerotate din TESTE.md; mi s-a intamplat si am revenit cu git checkout, apoi replace literal pe bloc),
  consistenta secventa==calculata (test_agenda), commit LOCAL.
- Gard anti-stale test_agenda: bifa Inventar A in ACELASI commit doar daca fisierul de test EXISTA deja in git;
  fisier de test NOU -> 2 commituri. (In rularea asta toate testele au intrat in fisiere existente - bifa in acelasi commit, OK.)
- §3: nu construi pe temei neverificat; daca textul difera de intelegere, TEXTUL CASTIGA. DAR atentie la derogari
  temporare (OUG) - lectia R17. SI atentie la afirmatii "empirice" nedocumentate in cod (ex. text_anaf 75) care pot
  fi INFIRMATE de proba DUK - vezi datoria noua de mai sus.

## Datorii deschise (in DECIZII.md, campania "achitare datorii" - separat de lant)
NOUA: limita text 75 pe toate declaratiile (vezi mai sus). Preexistente: A2 (D390 ziua 15), A3 (D177 form), C1/C2
(tichete cresa/culturale MO), C3 (amortizare MF neliniara xfail), C4 (D112 avantaje 8.3), C5 (migrare tichete
culturale). D101 scadenta lege-vs-validator (decizie produs Costin, DECIZII 03.08). Plus subsistemul mijloace fixe (xfail).

## Xfail-uri (21) = registrul de datorie (test_datorie.py). Toate legitime. Nu le "repara" fara sa citesti motivul.
