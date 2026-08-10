Citeste CLAUDE.md §2.2 (structura raportului) si §2.3 (lant, siguranta, limba), si ARHITECT.md "FORMA COMENZII" (forma comenzii primite - 7 puncte), inainte de a incepe.

# PREDARE_LANT — STARE CURENTA

Se SUPRASCRIE la fiecare publicare (al 5-lea pas, CLAUDE.md §2.3 pct.10). NU e jurnal - jurnalul e ISTORIC.md.
Ritual pornire: `ssh iconta 'cd ~/iconta_nou && git log -1 && git status --porcelain'`.

## (a) Four-way de la ultima executie
Ultimul commit de COD: LOT 0 = 42b97fb (adevarul registrului FUNCTIONALITATI.csv). FOUR-WAY (10.08.2026):
HEAD = origin/main = origin/backup/lant-2026-08-10 = 42b97fb; RUNNING = 42b97fb (restart iconta-nou
start 21:52:36 > commit-time 21:45:51; versiune.py stampileaza git HEAD la pornire, HEAD nemiscat de atunci),
HTTP 200. Sentinele push absente. Anterior: tura 30 = 123a7e5 / predare 4b4cbad. Serviciul iconta-nou ruleaza
din ~/iconta_nou. LIMITA: /admin/versiune (running in-memory) cere superadmin - neinterogat; RUNNING confirmat
prin start-time+HEAD (citirea canonica §2.3 pct.10).

## (b) Fronturi deschise (cu blocajul fiecaruia)
0. **CAMPANIE "verifica toate 201 functionalitatile" (Costin, 10.08)** — ACTIV, in lucru. Ia toate cele 201
   intrari din FUNCTIONALITATI.csv, verifica-le (inclusiv conformitate Design System), repara pe masura;
   corecteaza REGISTRUL cand nu corespunde realitatii (nu doar codul). 9 loturi aprobate de Costin, ordine:
   Lot 0 adevarul registrului -> 1 transversal/infra -> 2 Facturare/e-Factura -> 3 Contabilitate -> 4 Stocuri/
   banca/casa -> 5 Salarizare -> 6 Fiscalitate/declaratii -> 7 Control fiscal -> 8 Cabinet/portal client.
   Lantul curge fara comanda intre loturi (Costin opreste daca e nevoie). Fiecare lot: raport §2.2 complet + four-way.
   - **LOT 0 INCHIS (42b97fb)**: registrul confruntat cap-coada cu realitatea. Drift reparat (F117/F121/F152/F188
     Sursa cod; F092/F171/F172/F180/F188 descrieri gratuit-eliminat). Gard nou test_sursa_cod_refera_fisiere_care_exista.
     ELIMINAT(10) probate 404 pe app viu + cod absent; RESPINS/AMANAT/PLANIFICAT fara cod-fantoma; PARTIAL D406 exact.
   - **URMATOR: LOT 1 (transversal & infra, ~34 LIVE)** — NEINCEPUT. Include ~15 fundatii fara proba de test.
   - Accente Costin: (1) ELIMINAT - probeaza rutele pe app viu (facut Lot 0); (2) marcheaza explicit cele 33 LIVE
     fara proba, grupat, si urmareste care FUNDATII raman neprobate dupa lotul lor (F008 auth, F116 securitate,
     F004 ANAF, F043 import e-Factura, F001 AI, F081 scadente).
1. **Test fir de intrare cabinet nou** — cabinet test izolat 4163; fir parcurs cap-coada tura 21. Ramane review UI
   Costin / depunere efectiva. Cabinetul REAL 1968 (12 firme) = NEATINS (constrangere absoluta a campaniei).
2. **E3_97 (pensie ocupationala, Legea 1/2020)** — BLOCAJ: decizie de scope Costin (subsistem art.76(4^1)).
3. **D101 scadenta: lege vs validator INVERS** — codul urmeaza validatorul DUK. BLOCAJ: decizie de produs Costin.
4. **Declaratii DUK (turele 24-26)** — RAMAS doar decizii de model de date Costin (3 coloane firma_profil/facturi;
   salveaza_concediu gard simetric; UI populare). Unealta: frontend_test/valideaza_duk.py.
5. **F035/F036/F037 D406 PARTIAL** — familia D406 NEDEPUNABILA (SourceDocuments sintetic + Payments gol). Reparatie =
   feature mare -> decizie de scope. Registru marcat corect PARTIAL (confirmat Lot 0).
6. **Datorii Lot 0 nereparate** — F176 Descriere cita F160 (ELIMINAT) - de reincadrat la Lot 1 (F176 = OAuth); 3
   comentarii cod stale (login.js:418, main.py:2728/2786) - cosmetic, de curatat oportunist.

## (c) Ce e in lucru acum
Campania de verificare cap-coada a celor 201 functionalitati (front 0). Lot 0 inchis; Lot 1 (transversal & infra)
urmatorul. Metoda Lot 1: pytest existent + functional pe cabinet 4163 + citire cod, marcaj explicit al fundatiilor
fara proba.

## (d) Ce urmeaza
1. LOT 1 — transversal & infra (~34 LIVE): F001 AI client, F002 incredere AI, F004 ANAF, F005 API keys, F008 auth,
   F107 magic-link, F116 securitate perimetru, backup off-site, GDPR, notificari, etc. Marcheaza cele fara proba.
2. Apoi Lot 2 (Facturare/e-Factura) ... pana la Lot 8, fara comanda intre loturi.
3. Orice "forma care spune altceva decat faptul" -> corectie de registru + cod, ca in Lot 0.

## Unelte
- Registru: gard structura + anti-drift in core/test_registru_functionalitati.py (3 teste).
- Proba browser (Playwright): frontend_test/proba_wizard_antet.py + observa_*.py; creds ~/.iconta/fe_test.env
  (cabinet 4163, admin_firma fir-intrare@prisma-cont.test). DUK: frontend_test/valideaza_duk.py. NU in poarta verde.
- Poarta verde: commit ruleaza pytest suita intreaga (~6min) + verificator (TOTAL 0); post-commit publica
  origin/main + backup/lant-<data>; apoi restart iconta-nou (four-way). App pe 127.0.0.1:8010.
