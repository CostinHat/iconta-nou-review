Citeste CLAUDE.md §2.2 (structura raportului) si §2.3 (lant, siguranta, limba), si ARHITECT.md "FORMA COMENZII" (forma comenzii primite - 7 puncte), inainte de a incepe.

# PREDARE_LANT — STARE CURENTA

Se SUPRASCRIE la fiecare publicare (al 5-lea pas, CLAUDE.md §2.3 pct.10). NU e jurnal - jurnalul e ISTORIC.md.
Ritual pornire: `ssh iconta 'cd ~/iconta_nou && git log -1 && git status --porcelain'`.

## (a) Four-way de la ultima executie
Ultimul commit de COD: LOT 2+3+CONCURENTA = a0856e4. FOUR-WAY (11.08.2026): HEAD = origin/main =
origin/backup/lant-2026-08-11 = RUNNING = a0856e4; restart start 01:16:08 > commit-time 01:09:48; sentinele
absente; HTTP 200; tree curat. Pe deasupra commit PREDARE (markdown, acest fisier) fara restart. Anterior:
Lot 1 = 18e05d6. App pe 127.0.0.1:8010. NB: ramura de backup a trecut la data noua (backup/lant-2026-08-11).

## (b) Fronturi deschise
0. **CAMPANIE "verifica toate 201 functionalitatile" (Costin, 10.08)** — ACTIV. 9 loturi; lantul curge fara
   comanda intre loturi. Fiecare lot: raport §2.2 + four-way. Constrangere: DOAR cabinet 4163; real 1968 NEATINS.
   - **LOT 0 INCHIS (f189e91)**: adevarul registrului; gard test_sursa_cod_refera_fisiere_care_exista.
   - **LOT 1 INCHIS (18e05d6)**: transversal & infra; F001/F008/F116 probate; F116 headere = gol (decizie infra).
   - **LOT 2 VERIFICAT (fara commit propriu)**: Facturare & e-Factura (21); wizard Playwright TRECUT; F004 ANAF
     live; F043 cod+test; 0 defecte. F043 Testat corectat in a0856e4.
   - **LOT 3 INCHIS (a0856e4)**: Contabilitate (23); 55 pytest tintit + suita; F118/F054/F144/F145 verificate.
   - **GENERALIZARE CONCURENTA (a0856e4)**: 10 intrari LIVE (F126/F138-142/F144-147) cu Sursa cod "CONCURENTA:"
     -> module reale + gard nou test_sursa_cod_nu_e_referinta_de_concurenta. A atins deja Sursa cod pt F138-142
     (Lot 4) + F146/F147 (Lot 8); verificarea FUNCTIONALA a acestora ramane la lotul lor.
   - **URMATOR: LOT 4 (Stocuri, banca si casa, 19 LIVE)** — NEINCEPUT. F138-142 au deja Sursa cod corectata.
     Metoda: pytest + functional Postgres pe 4163 + parseri banca (F011/F012). Multe au test (test_stocuri etc.).
1. **F116 headere de securitate NEDEPLOYATE** (HSTS/X-Frame/X-Content/Referrer) — DECIZIE INFRA Costin. nginx
   server config = /etc/nginx/sites-available/iconta (root, in afara git). Snippet add_header pregatit.
2. **Test-debt** (cablate, fara test dedicat): Lot 1 migrari (F007/F053/F059/F079/F084/F085/F150); Lot 2
   (F017/F018/F045-gen/F048); Lot 3 (F118/F054/F145).
3. **F124 "Testare pilot P1-P5"** — proces finalizat, NU feature; Sursa cod "DE_FACUT sectiunea 1" stale.
4. **F035/F036/F037 D406 PARTIAL** — familia nedepunabila. Scope Costin.
5. **Test fir de intrare 4163** (tura 21); **E3_97** BLOCAJ scope; **D101 scadenta** BLOCAJ produs; **Declaratii
   DUK 24-26** ramas decizii model de date.

## (c) Ce e in lucru acum
Campania de verificare (front 0). Loturile 0-3 inchise/verificate; Lot 4 (Stocuri, banca, casa) urmatorul.

## (d) Ce urmeaza
1. LOT 4 — Stocuri, banca, casa (19): F011 contabilizare extras + F012 parser banca (ING/Jasper), F015 casa +
   plafoane, F138-142 stocuri CV (Sursa cod deja corectata), NIR/GV, transfer/analitica/barcode/inventar.
   Probe: pytest (test_stocuri, test_scadentar etc.) + functional Postgres 4163.
2. Apoi Lot 5 (Salarizare), 6 (Fiscalitate/declaratii - proaspat auditate 24-30), 7 (Control fiscal),
   8 (Cabinet/portal - F146/F147 Sursa cod deja corectata). Fara comanda intre loturi.
3. Orice "forma care spune altceva decat faptul" -> corectie registru + cod.

## Unelte
- Registru: 4 garduri in core/test_registru_functionalitati.py (structura x2 + existenta fisiere + anti-CONCURENTA).
  Gardul anti-stale citari (core/test_agenda.py) accepta DOAR teste din core/test_*.py - citeaza teste root-level
  in TESTE.md fara token `test_` (sau muta-le in core/).
- Proba browser (Playwright): frontend_test/proba_wizard_antet.py + observa_*.py; creds ~/.iconta/fe_test.env
  (cabinet 4163). DUK: frontend_test/valideaza_duk.py. NU in poarta verde.
- Poarta verde: commit ruleaza pytest suita (~6min) + verificator (0); post-commit publica origin/main +
  backup/lant-<data>; apoi restart iconta-nou (four-way). AI: cheia in ~/.iconta/api_keys.env.
