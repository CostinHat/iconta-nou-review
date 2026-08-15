Citeste CLAUDE.md §2.2 (structura raportului) si §2.3 (lant, siguranta, limba), si ARHITECT.md „FORMA COMENZII” (forma comenzii primite - 7 puncte), inainte de a incepe.

# PREDARE_LANT — STARE CURENTA

Se SUPRASCRIE la FIECARE publicare (al 5-lea pas, CLAUDE.md §2.3 pct.10), INCLUSIV la publicarile de continut - fara scutire (Costin, 15.08.2026: aici sta marca de sincronizare intre sesiuni; nerescris => o sesiune noua porneste de la o marca statuta). NU e jurnal - jurnalul e ISTORIC.md.
Ritual pornire: `ssh iconta 'cd ~/iconta_nou && git log -1 && git status --porcelain'` (da hash-ul literal al HEAD - acest fisier descrie varful, nu-si poate purta propriul hash).

## (a) Four-way de la ultima executie
Stare la 2026-08-15. HEAD = **acest commit** (SEO: robots.txt allow-list + titlu/meta/OG pe landing + X-Robots-Tag noindex pe /public/plata + rescriere PREDARE), IMEDIAT peste **50cec89** (39 ghiduri publicate). Ruleaza `git log -1` pentru hash. Proba RUNNING = start-time > commit (se CITESTE la predare, nu se presupune): `systemctl show iconta-nou -p ExecMainStartTimestamp` + `git log -1`. App+prod pe 127.0.0.1:8010 (serviciul systemd `iconta-nou`, ExecStart uvicorn --port 8010). Publicare origin/main + backup/lant-<data> prin post-commit (neconditionat) + restart la fiecare commit.

Lantul recent, DEJA COMIS: plimbarea Firma Grea (0054a4a -> 50cec89): 58e2aed (render CSS #5/#6 + favicon + canal note_rezultat #7), 8a965f4 (UX coada #2/#3/#4), 434efa3 (gard diacritice frontend #8), 087b33a (versionare asseturi cu gard #1), 5eeb9f2 (registre), 50cec89 (39 ghiduri cu front-matter, 79 pe disc = 79 servite = 79 sitemap). Peste el, lotul SEO (acest commit).

## (b) Fronturi deschise
1. **Ghiduri fara ecran accesibil (DOAR de raportat, regula 9 - fara ecran, functionalitatea nu exista).** Dintre cele 79 publicate, DOUA descriu o functionalitate a aplicatiei fara ecran:
   - `compensare-datorii-terti`: motorul EXISTA si e testat (core/compensare.py: suma_compensabila / nota_compensare / propune_compensari / pull; core/test_compensare.py) DAR nu e legat de niciun endpoint/ecran (niciun @app, absent din GRUPE_FUNC). Motor construit, ecran inexistent - decizie de produs Costin (a lega motorul sau a retrage ghidul).
   - `ro-e-tva-decont-precompletat`: nicio functionalitate e-TVA in cod (doar sursa de corpus in anaf_surse). Feature inexistent.
2. **D212 cablat pe date 2025** (semnalat 15.08, NEreparat): butonul „Fisa D212” (rip_ecran.js -> /rip/d212/) e cablat pe 2025 / „sm 4.050 lei” 2025, iar ghidurile declaratia-unica-2026 / cas-cass-pfa-2026 sunt pe 2026. Problema de ACTUALITATE a datelor (nu absenta de ecran). De actualizat la 2026.
3. **D300 dependent de ANAF / limita declarata, RAPORTAT SEPARAT, NEreparat** (GARZI 15.08 D300):
   - import non-UE (primita non-UE 0%) ramane pe R26 - TVA vamala / deferment de import depinde de raspunsul ANAF;
   - T/R (triangulatie / regim agricultori) NU sunt pe axa bun-serviciu -> rutate numeric ca bunuri, semnalate explicit, neacoperite pe D300.
4. **Limita gardului de diacritice frontend** (434efa3): poarta zero-diacritice SARE sirurile care au deja cel putin o diacritica -> nu prinde un cuvant ASCII langa unul diacriticizat in acelasi sir (false-negative deliberat vs false-pozitive pe siruri mixte). De ridicat cand exista un criteriu care separa ASCII-necesar-diacritice de ASCII-legitim. Vezi GARZI 15.08.
5. **Fronturi mostenite, NEMISCATE:**
   - D406 F035/F036/F037 PARTIAL: F035 = Payments neemis (asteapta sursa maparei); F036 = amortizare doar liniara (art.28 degresiva/accelerata neimplementate) + fragment; F037 = fragment (nu in AuditFile lunar). Scope Costin.
   - F116 headere de securitate: HSTS lung ramas optional - decizie INFRA Costin.
   - D101G: schema v2 (OPANAF 206/2025) neinstalata in DecValidation pe server -> test xfail(strict); se probeaza cand se instaleaza DecValidation care cunoaste d101g v2.

## (c) Ce e in lucru acum
Nimic in lucru. Lotul SEO (robots allow-list, titlu/meta/OG landing, plata noindex, PREDARE) e in ACEST commit. Frontul „ghid parcat” din predarile anterioare e INCHIS (toate 39 publicate in 50cec89, ~/ghid_pending gol). De ce niciun alt front nu s-a miscat: lotul a avut raza fixa (cele 4 cereri SEO ale lui Costin); fronturile ramase asteapta fiecare o DECIZIE/INPUT (compensare/e-TVA = produs; D212 2026 = date; D300-ANAF = raspuns ANAF; D406/F116/D101G = scope/infra/instalare).

## (d) Ce urmeaza
La cererea/decizia lui Costin:
1. **Ghiduri fara ecran**: a lega motorul de compensare la un ecran, SAU a decide statutul e-TVA / retragerea ghidului.
2. **D212 2026**: actualizarea butonului Fisa D212 + pragurilor la 2026 (sm 2026, plafoane Legea 239/2025).
3. **D300 ANAF-dependent**: la raspunsul ANAF pe TVA vamala/deferment -> import non-UE dincolo de R26; eventual acoperirea T/R pe axa proprie.
4. **Diacritice frontend**: ridicarea limitei pe siruri mixte cand exista criteriu de separare.
5. **Mostenite**: D406 (Payments; amortizare degresiva/accelerata + fragment AuditFile); F116 HSTS; D101G la instalarea DecValidation v2.

## Unelte
- SEO/crawler: robots.txt = allow-list (main.py public_robots): indexabil / (exact), /ghid, /public/termeni, /static/, /sitemap.xml, /robots.txt; restul Disallow. Motivul: Allow: / lasa Google sa culeaga fragmente de rute din app.js (18x404 Search Console). /public/plata = X-Robots-Tag noindex (ref secret in URL). Landing title/meta/OG in static/index.html (og sincronizat cu title+description). sitemap.xml generat dinamic din ghid/ (main.py:9026).
- Versionare asseturi: generator versioneaza_assets.py (`venv/bin/python versioneaza_assets.py --scrie` re-stampileaza toate referintele cu hash de continut); gard core/test_versionare_assets.py (6 teste). Orice schimbare de asset JS/CSS cere re-rulare (altfel gard rosu). Daca se atinge FUNCTIONALITATI.csv: regenereaza login.js cu `venv/bin/python genereaza_grupe_functii.py --scrie` APOI re-ruleaza versioneaza_assets.py --scrie (login.js isi schimba hash-ul).
- Gard diacritice: core/test_diacritice_afisate.py (AST/heuristica, baseline 0) - scaneaza .py (roluri AST) SI static/js/** (pozitii de afisare); text afisat = diacritice, log/assert/marker = ASCII.
- Ghiduri: fisiere in ghid/*.md cu front-matter (title/description/published/modified intre ---). Slug kebab-case ASCII. Gard test_ghiduri_servite.py: N pe disc = N servite = N in index+sitemap. Titlul din front-matter = heading-ul „# ” din corp.
- Render: constatarile vizuale se probeaza cu chromium headless (getComputedStyle + screenshot), nu curl/grep. Creds browser: ~/.iconta/fe_test.env. Paginile /ghid/{slug} + landing sunt publice (fara auth).
- Registru: inventar A + anti-stale in core/test_agenda.py (bifa √ ancorata la commitul in care fisierul de test intra in git - comit INTAI fisierul, apoi bifa; redenumire = re-ancorare + bump).
- Poarta verde: commit ruleaza pytest (~7.5min) + verificator (0); post-commit publica origin/main + backup/lant-<data>; apoi restart iconta-nou NECONDITIONAT (four-way RUNNING==HEAD). Push backup-only = `HEAD:backup/lant-<data>` remote.
