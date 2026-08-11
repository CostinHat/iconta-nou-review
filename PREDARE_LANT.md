Citeste CLAUDE.md §2.2 (structura raportului) si §2.3 (lant, siguranta, limba), si ARHITECT.md "FORMA COMENZII" (forma comenzii primite - 7 puncte), inainte de a incepe.

# PREDARE_LANT — STARE CURENTA

Se SUPRASCRIE la fiecare publicare (al 5-lea pas, CLAUDE.md §2.3 pct.10). NU e jurnal - jurnalul e ISTORIC.md.
Ritual pornire: `ssh iconta 'cd ~/iconta_nou && git log -1 && git status --porcelain'`.

## (a) Four-way de la ultima executie
Ultimul commit de COD: 1ef33b1 (Lot 4-8, campania verifica-201 COMPLETA). FOUR-WAY (11.08.2026): HEAD =
origin/main = origin/backup/lant-2026-08-11 = RUNNING = 1ef33b1; restart start 03:24:36 > commit-time 03:18:28;
sentinele absente; HTTP 200; tree curat. Deasupra, commit PREDARE (markdown) fara restart. App pe 127.0.0.1:8010.

## (b) Fronturi deschise
0. **CAMPANIE "verifica toate 201 functionalitatile" (Costin, 10.08) — COMPLETA (9/9 loturi).**
   Toate cele 201 confruntate cap-coada cu realitatea (prima verificare integrala). Registru corectat la adevar;
   2 garduri noi de registru; fundatii probate. NIMIC nou de executat pe aceasta comanda - ramase doar deciziile/
   datoriile de mai jos.
   - Loturi: 0 adevar registru (f189e91), 1 transversal (18e05d6), 2 facturare (verif), 3 contab+CONCURENTA
     (a0856e4), 4-8 stocuri/salarizare/fiscalitate/control/cabinet (1ef33b1).
   - Drift reparat: F117/F121/F152/F188 cai; 5 descrieri gratuit-eliminat; F150/F122/F151 proza->cod; 10x
     CONCURENTA->cod; F043 Testat; F116 headere->adevar. Garduri: test_sursa_cod_refera_fisiere_care_exista +
     test_sursa_cod_nu_e_referinta_de_concurenta. ELIMINAT(10) probate 404 pe app viu.
1. **F116 headere de securitate NEDEPLOYATE** (HSTS/X-Frame/X-Content/Referrer) — SINGURA DECIZIE DESCHISA.
   nginx server config = /etc/nginx/sites-available/iconta (root, in afara git, ne-gated). Snippet add_header
   pregatit. La OK Costin: adauga pe blocul 443 + nginx -t + reload + adu configul sub versionare in config_server/.
2. **Test-debt** (cablate + rute live, fara test dedicat): F007/F053/F059/F079/F084/F085/F150/F151 (migrari),
   F017/F018/F045-gen/F048, F118/F054/F145, F075. De acoperit cu smoke pe cabinet 4163.
3. **F124 "Testare pilot P1-P5"** — proces finalizat, NU feature; Sursa cod "DE_FACUT sectiunea 1". De reincadrat/scos.
4. **F035/F036/F037 D406 PARTIAL** — familia nedepunabila (SourceDocuments sintetic + Payments gol). Scope Costin.
5. **Alte fronturi preexistente**: fir intrare 4163 (review UI/depunere); E3_97 BLOCAJ scope; D101 scadenta lege-vs-
   validator BLOCAJ produs; Declaratii DUK 24-26 ramas decizii model de date (3 coloane; UI populare).

## (c) Ce e in lucru acum
NIMIC in lucru - campania verifica-201 e completa (9/9). Urmatoarea comanda a lui Costin decide directia.

## (d) Ce urmeaza
La comanda Costin: (a) deploy headere F116; (b) acoperire test-debt cu smoke pe 4163; (c) reincadrare F124;
(d) reparatie D406 (feature mare, scope). Sau firul de intrare / declaratii DUK (decizii model de date).

## Unelte
- Registru: 4 garduri in core/test_registru_functionalitati.py (structura x2 + existenta fisiere + anti-CONCURENTA).
  Gardul anti-stale citari (core/test_agenda.py) accepta DOAR teste din core/test_*.py.
- Proba browser (Playwright): frontend_test/proba_wizard_antet.py + observa_*.py; creds ~/.iconta/fe_test.env
  (cabinet 4163). DUK pe declaratii: PYTHONPATH=$PWD frontend_test/valideaza_duk.py (4 firme 4163). NU in poarta verde.
- Poarta verde: commit ruleaza pytest suita (~6min) + verificator (0); post-commit publica origin/main +
  backup/lant-<data>; apoi restart iconta-nou (four-way). AI: cheia in ~/.iconta/api_keys.env.
