Citeste CLAUDE.md §2.2 (structura raportului) si §2.3 (lant, siguranta, limba), si ARHITECT.md "FORMA COMENZII" (forma comenzii primite - 7 puncte), inainte de a incepe.

# PREDARE_LANT — STARE CURENTA

Se SUPRASCRIE la fiecare publicare (al 5-lea pas, CLAUDE.md §2.3 pct.10). NU e jurnal - jurnalul e ISTORIC.md.
Ritual pornire: `ssh iconta 'cd ~/iconta_nou && git log -1 && git status --porcelain'`.

## (a) Four-way de la ultima executie
Ultimul commit de COD: LOT 1 = 18e05d6 (transversal & infra - fundatii probate + registru la adevar).
FOUR-WAY (10.08.2026): HEAD(cod) = origin/main = origin/backup/lant-2026-08-10 = RUNNING = 18e05d6;
restart iconta-nou start 23:23:34 > commit-time 23:17:24; sentinele push absente; HTTP 200. Pe deasupra sta
un commit de PREDARE (markdown, acest fisier) fara restart (nu schimba runtime). Anterior: Lot 0 = f189e91.
Serviciul iconta-nou ruleaza din ~/iconta_nou. App pe 127.0.0.1:8010.

## (b) Fronturi deschise (cu blocajul fiecaruia)
0. **CAMPANIE "verifica toate 201 functionalitatile" (Costin, 10.08)** — ACTIV. 9 loturi aprobate; lantul curge
   fara comanda intre loturi. Fiecare lot: raport §2.2 complet + four-way. Constrangere: DOAR cabinet 4163;
   cabinetul real 1968 (12 firme) NEATINS.
   - **LOT 0 INCHIS (f189e91)**: adevarul registrului. Drift reparat (Sursa cod + descrieri gratuit-eliminat);
     gard test_sursa_cod_refera_fisiere_care_exista; ELIMINAT probate 404 pe app viu.
   - **LOT 1 INCHIS (18e05d6)**: transversal & infra (35 LIVE). Fundatii PROBATE: F008 auth (login live 200+401),
     F001 AI (apel real Claude 'OK'), F116 securitate (rate-limit/TLS/fail2ban OK; HEADERE absente = gol real
     -> registru corectat + FLAG decizie infra). Cronuri toate instalate/ruleaza. Migrari cablate. PWA F113 servit.
     Drift reparat: F150+F122 Sursa cod -> cod real.
   - **URMATOR: LOT 2 (Facturare & e-Factura, 21 LIVE)** — NEINCEPUT. Metoda: pytest + Playwright wizard
     (frontend_test/proba_wizard_antet.py) + DUK (UBL) + verificator DS. Fundatie de raportat aici: F043 (import
     e-Factura, fara proba). NB: F004 (Validare CUI ANAF, fara proba) e grupat NU in Lot 1 - de probat la lotul lui.
1. **F116 headere de securitate NEDEPLOYATE** (HSTS/X-Frame/X-Content/Referrer) — DECIZIE INFRA Costin. nginx
   server config = /etc/nginx/sites-available/iconta (root-owned, in afara git, ne-gated). Snippet pregatit
   (add_header ... always pe blocul 443). Recomandare: adu-l sub versionare in config_server/.
2. **Test-debt migrari** (F007/F053/F059/F079/F084/F085/F150) — cablate, fara proba functionala adanca (fara pytest).
3. **F124 "Testare pilot P1-P5"** — campanie de test finalizata, NU feature; Sursa cod "DE_FACUT sectiunea 1" stale.
4. **F035/F036/F037 D406 PARTIAL** — familia nedepunabila (SourceDocuments sintetic + Payments gol). Scope Costin.
5. **Test fir de intrare cabinet 4163** — parcurs cap-coada tura 21; ramane review UI / depunere. 1968 NEATINS.
6. **E3_97 (Legea 1/2020)** BLOCAJ scope; **D101 scadenta lege-vs-validator INVERS** BLOCAJ produs.
7. **Declaratii DUK (24-26)** — ramas decizii de model de date Costin (3 coloane; UI populare). Unealta frontend_test/valideaza_duk.py.

## (c) Ce e in lucru acum
Campania de verificare (front 0). Lot 0 + Lot 1 inchise; Lot 2 (Facturare & e-Factura) urmatorul.

## (d) Ce urmeaza
1. LOT 2 — Facturare & e-Factura (21 LIVE): emitere, PDF factura (F045), model factura (F048), import e-Factura UBL
   (F043), e-Factura SPV send/receive, chitante (F017), export SAGA/WinMentor, link plata. Probe: pytest + Playwright
   wizard + DUK UBL + verificator DS. Raporteaza F043 + F004 (unde-i grupat) explicit.
2. Apoi Lot 3 (Contabilitate) ... Lot 8 (Cabinet/portal), fara comanda intre loturi.
3. Orice "forma care spune altceva decat faptul" -> corectie registru + cod (ca Lot 0/1).

## Unelte
- Registru: gard structura + anti-drift in core/test_registru_functionalitati.py (3 teste). LIMITA: Sursa cod PROZA
  (fara path-token) nu e prinsa (F124 inca).
- Proba browser (Playwright): frontend_test/proba_wizard_antet.py + observa_*.py; creds ~/.iconta/fe_test.env
  (cabinet 4163, admin_firma fir-intrare@prisma-cont.test). DUK: frontend_test/valideaza_duk.py. NU in poarta verde.
- Poarta verde: commit ruleaza pytest suita intreaga (~6min) + verificator (TOTAL 0); post-commit publica
  origin/main + backup/lant-<data>; apoi restart iconta-nou (four-way). AI: cheia in ~/.iconta/api_keys.env.
