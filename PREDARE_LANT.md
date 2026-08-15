Citeste CLAUDE.md §2.2 (structura raportului) si §2.3 (lant, siguranta, limba), si ARHITECT.md „FORMA COMENZII” (forma comenzii primite - 7 puncte), inainte de a incepe.

# PREDARE_LANT — STARE CURENTA

Se SUPRASCRIE la fiecare publicare (al 5-lea pas, CLAUDE.md §2.3 pct.10). NU e jurnal - jurnalul e ISTORIC.md.
Ritual pornire: `ssh iconta 'cd ~/iconta_nou && git log -1 && git status --porcelain'`.

## (a) Four-way de la ultima executie
Stare la 2026-08-15. HEAD = **087b33a** (sistem de versionare asseturi cu gard - #1, disciplina ?v= negardata).
Plimbarea lui Costin pe Firma Grea e INCHISA in 4 commituri DEJA COMISE: 58e2aed (render CSS #5/#6 + favicon + canal
note_rezultat #7), 8a965f4 (UX coada #2/#3/#4), 434efa3 (gard diacritice pe frontend #8 + carduri de meniu), 087b33a
(versionare asseturi cu gard #1). Proba RUNNING = start-time > commit (se citeste la predare, nu se presupune):
`sudo systemctl status iconta-nou` (ExecMainStartTimestamp) + `git log -1`. App pe 127.0.0.1:8010. Publicare
origin/main + backup/lant-<data> prin post-commit (ritual neconditionat - restart la fiecare commit).
NB: LOTUL CURENT (registrele acestei ture: GARZI/DECIZII/ISTORIC/TESTE + acest fisier) e NEcomis in arborele de lucru -
il comite Costin prin poarta (FARA git commit din partea agentului). Cele 4 commituri de campanie sunt deja comise.

## (b) Fronturi deschise
1. **GHID - 19 fisiere .md PARCATE.** In ~/ghid_pending/ (mutate din ghid/ ca sa NU sparga test_ghiduri_servite -
   suita e verde acum, N=N). ASTEAPTA de la Costin blocul cu cele 19 titluri/descrieri VERBATIM ca sa li se puna
   front-matter, apoi: restaurare in ghid/, test_ghiduri_servite (N=N), sitemap, publicare. Doua dintre ele -
   `compensare-datorii-terti` si `ro-e-tva-decont-precompletat` - descriu functionalitati FARA ecran accesibil (de
   nereparat acolo, DOAR de raportat: fara ecran, functionalitatea nu exista - regula permanenta 9).
2. **D300 dependent de ANAF / limita declarata, RAPORTAT SEPARAT, NEreparat in app** (vezi GARZI 15.08 D300):
   - import non-UE (primita non-UE 0%) ramane pe R26 - TVA vamala / deferment de import depinde de raspunsul ANAF;
   - T/R (triangulatie / regim special agricultori) NU sunt pe axa bun-serviciu -> rutate numeric ca bunuri, semnalate
     explicit, neacoperite pe D300 (limita declarata, nu tacere).
3. **Limita declarata a gardului de diacritice pe frontend** (nou, 434efa3): poarta zero-diacritice SARE sirurile care
   au deja cel putin o diacritica -> nu prinde un cuvant ASCII langa unul diacriticizat in acelasi sir (false-negative
   deliberat, ca sa evite false-pozitive pe siruri mixte). De ridicat cand exista un criteriu care separa
   ASCII-necesar-diacritice de ASCII-legitim in siruri mixte. Vezi GARZI 15.08.
4. **Fronturi mostenite, NEMISCATE:**
   - D406 F035/F036/F037 PARTIAL: F035 = Payments neemis (asteapta sursa maparei); F036 = amortizare doar liniara
     (art.28 degresiva/accelerata neimplementate) + fragment; F037 = fragment (nu in AuditFile lunar). Scope Costin.
   - F116 headere de securitate: HSTS lung ramas optional - decizie INFRA Costin.
   - D101G: schema v2 (OPANAF 206/2025) neinstalata in DecValidation pe server -> test xfail(strict); se probeaza
     cand se instaleaza DecValidation care cunoaste d101g v2.

## (c) Ce e in lucru acum
Nimic in lucru. Plimbarea lui Costin pe Firma Grea (8 constatari + garzi de disciplina ?v= si diacritice-frontend) e
INCHISA (4 commituri de mai sus, deja comise). Aceasta tura a facut DOAR actualizarea registrelor (GARZI / DECIZII /
ISTORIC / TESTE / PREDARE) - NEcomisa. FUNCTIONALITATI.csv NEatins: cardul „De depus” e o re-etichetare
patru-ochi-aware a suprafetei de coada EXISTENTE (nu o functionalitate noua cu ecran nou), iar favicon nu e
functionalitate -> niciun rand nou nu se justifica; atingerea CSV ar fi cascadat regenerarea login.js + re-stampilarea
asseturilor fara motiv. De ce niciun front deschis nu s-a miscat: campania a avut raza fixa (cele 8 constatari ale lui
Costin); fronturile mostenite (ghid, D300-ANAF, D406, F116, D101G) asteapta fiecare o DECIZIE sau un INPUT de la Costin.

## (d) Ce urmeaza
La cererea/decizia lui Costin:
1. **Ghid**: livrarea blocului cu cele 19 titluri/descrieri -> front-matter -> restaurare in ghid/ -> test_ghiduri_
   servite (N=N) -> sitemap -> publicare.
2. **D300 ANAF-dependent**: la raspunsul ANAF pe TVA vamala/deferment -> tratarea importului non-UE dincolo de R26.
   Eventual: acoperirea T/R pe axa proprie (azi doar semnalate explicit).
3. **Diacritice frontend**: ridicarea limitei pe siruri mixte cand exista un criteriu de separare ASCII-necesar vs cod.
4. **Mostenite**: D406 (sursa Payments; amortizare degresiva/accelerata + fragment AuditFile); F116 HSTS; D101G la
   instalarea DecValidation v2.

## Unelte
- Versionare asseturi: generator versioneaza_assets.py (`venv/bin/python versioneaza_assets.py --scrie` re-stampileaza
  toate referintele cu hash de continut); gard core/test_versionare_assets.py (6 teste). Orice schimbare de asset
  JS/CSS cere re-rulare (altfel gard rosu). Daca se atinge FUNCTIONALITATI.csv: regenereaza login.js cu
  `venv/bin/python genereaza_grupe_functii.py --scrie` APOI re-ruleaza versioneaza_assets.py --scrie (login.js isi
  schimba hash-ul).
- Gard diacritice: core/test_diacritice_afisate.py (AST, baseline 0) - scaneaza .py SI static/js/**; text afisat =
  diacritice, log/assert/marker = ASCII.
- Render: constatarile vizuale se probeaza cu chromium headless (getComputedStyle + screenshot), nu curl/grep. Creds
  browser: ~/.iconta/fe_test.env (cabinet 4163). Capturi campanie in frontend_test/ (def5_*, def6_*, coada_mono_*).
- Registru: inventar A + anti-stale in core/test_agenda.py (bifa √ ancorata la commitul in care fisierul de test
  intra in git - comit INTAI fisierul, apoi bifa; redenumire = re-ancorare + bump). Bifa test_versionare_assets ancorata
  la 087b33a (fisier deja in git HEAD).
- Poarta verde: commit ruleaza pytest (~6min) + verificator (0); post-commit publica origin/main + backup/lant-<data>;
  apoi restart iconta-nou NECONDITIONAT (four-way RUNNING==HEAD).
