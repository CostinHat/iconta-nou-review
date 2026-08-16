Citeste CLAUDE.md §2.2 (structura raportului) si §2.3 (lant, siguranta, limba), si ARHITECT.md „FORMA COMENZII” (forma comenzii primite - 7 puncte), inainte de a incepe.

# PREDARE_LANT — STARE CURENTA

Se SUPRASCRIE la FIECARE publicare (al 5-lea pas, CLAUDE.md §2.3 pct.10), INCLUSIV la publicarile de continut - fara scutire (Costin, 15.08.2026: aici sta marca de sincronizare intre sesiuni; nerescris => o sesiune noua porneste de la o marca statuta). NU e jurnal - jurnalul e ISTORIC.md.
Ritual pornire: `ssh iconta 'cd ~/iconta_nou && git log -1 && git status --porcelain'` (da hash-ul literal al HEAD - acest fisier descrie varful, nu-si poate purta propriul hash).

## (a) Four-way de la ultima executie
Stare la 2026-08-16. HEAD = **acest commit** (P3: acoperire AJUTOR — 50 de intrari LIVE fara ajutor contextual au primit ajutor cu traseu din ecranul principal; garda `test_acoperire_ajutor_nu_regreseaza` intarita de la Stare=='LIVE' EXACT la startswith('LIVE'), baseline 0 => "nicio intrare LIVE fara ajutor"; RED probat: 50 pe CSV HEAD). Ultimul din 3 probleme de onboarding (comanda Costin): peste **fc0a330** (P1 ecran onest la esec firma la inregistrare cu CUI invalid: motiv real in backend + ecran propriu cu identitate/cale in login.js, probat Playwright; P2 link "Inregistreaza cabinetul" pe formularul de autentificare), peste **8ecbdc4** (registrul declaratiilor coerent+complet+gardat), 72fb521 (D112 fix 3 generalizare), 1b175a1 (D112 fix 2 CAM), 0889a0e (D112 fix 1 deducere), b0171d6 (chicken-and-egg), 12df714 (campania D300 8/8). Ruleaza `git log -1` pentru hash. Proba RUNNING = start-time > commit (se CITESTE): `systemctl show iconta-nou -p ExecMainStartTimestamp` + `git log -1`. App+prod pe 127.0.0.1:8010 (systemd `iconta-nou`, uvicorn --port 8010; EnvironmentFile ~/.iconta/db.env + ~/.iconta/api_keys.env). Publicare origin/main + backup/lant-<data> prin post-commit + restart la fiecare commit.

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
LIVRAT (fc0a330 + acest commit): **3 probleme de onboarding** gasite de Costin parcurgand inregistrarea cu CUI invalid (12345678). P1: ecran alb la esecul adaugarii firmei -> ecran onest (identitate + motiv REAL al esecului + cale de intrare) + backend care poarta motivul (nu mai inghite "CUI invalid: cifra de control"); probat Playwright pe ambele cai (CUI invalid/valid). P2: formularul de autentificare n-avea cale catre inregistrare -> link "Inregistreaza cabinetul". P3: 50 de intrari LIVE fara ajutor (garda oarba filtra Stare=='LIVE' EXACT, ratand "LIVE (data)") -> ajutor scris pentru toate 50 (Ce face + Cum ajungi cu traseu) + garda intarita la startswith('LIVE'). ANTERIOR: registrul declaratiilor coerent+complet+gardat (8ecbdc4); inainte, Task 2 D112 - 3 fixuri (deducere/CAM/generalizare), backlog D112 triat in GARZI (zilieri/mandat, nesalariale, B1_3 part-time, atribute, scutiri sectoriale, headcount).

## (d) Ce urmeaza
**In curs (nu decizie - tura exhaustiva D112 Task 2):** fixurile urmatoare din tura - zilieri/mandat/cenzori necablat la d112.pull, B1_3 part-time hardcodat (P1..P7 din ore), atribute hardcodate (E3_3/asigSO/asigCI/E3_2), nesalariale (diurna/avantaje natura/pensii/plafon 33%), scutiri sectoriale istorice 2025, headcount vs REGES, CAM temei art.220^1->220^3, apartenenta la perioada. Corectitudinea NU e decizie de produs; ce depinde de ANAF se raporteaza separat.

La cererea/decizia lui Costin:
1. **Ghiduri fara ecran**: a lega motorul de compensare la un ecran, SAU a decide statutul e-TVA / retragerea ghidului.
2. **D212 2026**: actualizarea butonului Fisa D212 + pragurilor la 2026 (sm 2026, plafoane Legea 239/2025).
3. **D300 ANAF-dependent**: la raspunsul ANAF pe TVA vamala/deferment -> import non-UE dincolo de R26; eventual acoperirea T/R pe axa proprie.
4. **Diacritice frontend**: ridicarea limitei pe siruri mixte cand exista criteriu de separare.
5. **Mostenite**: D406 (Payments; amortizare degresiva/accelerata + fragment AuditFile); F116 HSTS; D101G la instalarea DecValidation v2.

## Unelte
- SEO/crawler: robots.txt = allow-list (main.py public_robots): indexabil / (exact), /ghid, /public/termeni, /static/, /sitemap.xml, /robots.txt; restul Disallow. Motivul: Allow: / lasa Google sa culeaga fragmente de rute din app.js (18x404 Search Console). /public/plata = X-Robots-Tag noindex (ref secret in URL). Landing title/meta/OG in static/index.html (og sincronizat cu title+description). sitemap.xml generat dinamic din ghid/ (main.py:9026). Middleware `_edge_canonic_head` (main.py, langa _audit_middleware): www.iconta.eu -> 301 canonic (fara www) pastrand calea+query; HEAD pe rutele GET -> tratat ca GET (FastAPI nu adauga HEAD -> altfel 405; Googlebot foloseste HEAD). Sursa unica host canonic = _GHID_BAZA. Gard: core/test_edge_canonic_head.py.
- Versionare asseturi: generator versioneaza_assets.py (`venv/bin/python versioneaza_assets.py --scrie` re-stampileaza toate referintele cu hash de continut); gard core/test_versionare_assets.py (6 teste). Orice schimbare de asset JS/CSS cere re-rulare (altfel gard rosu). Daca se atinge FUNCTIONALITATI.csv: regenereaza login.js cu `venv/bin/python genereaza_grupe_functii.py --scrie` APOI re-ruleaza versioneaza_assets.py --scrie (login.js isi schimba hash-ul).
- Gard diacritice: core/test_diacritice_afisate.py (AST/heuristica, baseline 0) - scaneaza .py (roluri AST) SI static/js/** (pozitii de afisare); text afisat = diacritice, log/assert/marker = ASCII.
- Ghiduri: fisiere in ghid/*.md cu front-matter (title/description/published/modified intre ---). Slug kebab-case ASCII. Gard test_ghiduri_servite.py: N pe disc = N servite = N in index+sitemap. Titlul din front-matter = heading-ul „# ” din corp.
- Render: constatarile vizuale se probeaza cu chromium headless (getComputedStyle + screenshot), nu curl/grep. Creds browser: ~/.iconta/fe_test.env. Paginile /ghid/{slug} + landing sunt publice (fara auth).
- Registru: inventar A + anti-stale in core/test_agenda.py (bifa √ ancorata la commitul in care fisierul de test intra in git - comit INTAI fisierul, apoi bifa; redenumire = re-ancorare + bump).
- Poarta verde: commit ruleaza pytest (~7.5min) + verificator (0); post-commit publica origin/main + backup/lant-<data>; apoi restart iconta-nou NECONDITIONAT (four-way RUNNING==HEAD). Push backup-only = `HEAD:backup/lant-<data>` remote.
