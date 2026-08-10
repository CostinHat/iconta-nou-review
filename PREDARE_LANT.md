Citeste CLAUDE.md §2.2 (structura raportului) si §2.3 (lant, siguranta, limba), si ARHITECT.md "FORMA COMENZII" (forma comenzii primite - 7 puncte), inainte de a incepe.

# PREDARE_LANT — STARE CURENTA

Se SUPRASCRIE la fiecare publicare (al 5-lea pas, CLAUDE.md §2.3 pct.10). NU e jurnal - jurnalul e ISTORIC.md.
Ritual pornire: `ssh iconta 'cd ~/iconta_nou && git log -1 && git status --porcelain'`.

## (a) Four-way de la ultima executie
Ultimul commit de COD: tura 25 (TOATE declaratiile confruntate field-by-field cu sursa oficiala; 8 reparate,
2 conforme). Four-way exact (SHA + ora) = in raportul turei 25. Anterior: tura 24 = c9869a1 (4 declaratii DUK).
Serviciul iconta-nou ruleaza din ~/iconta_nou; static-ul (js/css) e servit de pe disc.

## (b) Fronturi deschise (cu blocajul fiecaruia)
1. **Test fir de intrare cabinet nou** — ACTIV. Cabinet test izolat 4163 "CABINET TEST FIR INTRARE SRL", cont
   admin_firma fir-intrare@prisma-cont.test (user 6504; parola in raportul turei 15). 4 firme: ALFA=tenant_013(8396),
   BETA=014(8397), GAMA=015(8398), DELTA=016(8399). seed_profil aplicat. Fisiere/ordine/verdicte: ~/date_test_cabinet/
   README.md; runner ~/date_test_cabinet/aplica.py profil|luna. SETUP COMPLET (tura 21): asociati+XML+seed_luna
   aplicate pe 4163; fir parcurs cap-coada, TOATE verdictele README confirmate pe cabinetul real (fixurile 14/16/17
   valideaza). Ramane: review UI Costin / depunere efectiva. Cabinetul REAL 1968 (12 firme) = neatins.
2. **E3_97 (pensie ocupationala, Legea 1/2020)** — build oprit pe stop point (cere subsistemul art.76(4^1): plafon
   lunar 33% + ordine). BLOCAJ: decizie de scope Costin.
3. **D101 scadenta: lege vs validator INVERS** — codul urmeaza validatorul DUK. BLOCAJ: decizie de produs Costin.
4. **Descoperiri proba date-test (neprogramate)** — D710 nederivabil; D300 achizitii (R5/taxare inversa/9-5%) nederivate
   + fara stocare importabila; D406 lunar fara Active/Stocuri.
5. **Frontend probe — de completat** — proba browser exista (vezi Unelte) dar acopera prin UI real doar migrare/firme/
   facturi; pachete/setari (depth) + portal/admin/asistent (cer rol client/superadmin/angajat in 4163) raman de probat.

6. **Declaratii DUK — TOATE 10 confruntate field-by-field cu sursa (tura 25); 8 reparate, 2 conforme** — audit
   pe anaf_surse/*_struct + XSD, pe date POPULATE (nu nil), fiecare cu gard + DUK before/after. Reparate: D100
   (scadenta micro trim IV - respins de ANAF), D101 (nr_evid poz.1-2), D205 (cifR/den1 goale), D300 (sub-declarare
   tacita), D390 (rotunjire R16), D394 (V cota0 + crash pull), D406 (PaymentMethod), D112 (carantina C2_213/215).
   Conform: D301, D710. RAMAS = DATE/DECIZIE PRODUS Costin (NU defect de cod):
   (i) D112 asiguratD D_1..D_7 obligatorii-goale = aceeasi clasa ZERO-BASE ca D205 cifR; cere migrarea a 4 fixtures
       shared (test_pull_declaratii.py) + confirmarea ca salveaza_concediu garanteaza serie/numar/date. DECIDE Costin.
   (ii) D390 R24.1 - CUI UE FALS in seed (cu CUI real = valid, dovedit); corecteaza seed, NU exclude tacit.
   (iii) D394 R233.6 - seed cereale de la PF fara subcod NC pe factura.
   (iv) D300 - rate 19%/5% fara rand DUK-valid 2026 (rutare R16?), achizitii taxare-inversa aruncate tacit.
   (v) D205 divid_P mereu 0 (distribuit-vs-platit); D301 pers_inreg / D394 prsAfiliat / D205 Rezid hardcodate
       (lipsa coloana/model de date). D406 GL TaxCode 300, PF tip-04 absent din master (radacina facturi_api).
   Unealta: PYTHONPATH=$PWD venv/bin/python3 frontend_test/valideaza_duk.py.

## (c) Ce e in lucru acum
Conformitatea declaratiilor la spec oficial DUK (front 6) + firul de intrare (front 1). Turele recente:
18 PREDARE al 5-lea pas, 19 izolare /raportari, 20 proba browser + fix antet wizard, 22 ZERO-BASE avertisment,
23 DUK-validat + D100 gol refuzat, 24 refacut 4 declaratii la spec oficial, 25 TOATE 10 declaratiile confruntate
field-by-field cu sursa (8 reparate, 2 conforme). Metoda tura 25: audit paralel cu agenti proaspeti + DUK pe
date populate - a scos defecte pe care validarea pe nil le rata (ex. D100 micro trim IV respins de ANAF).

## (d) Ce urmeaza
1. Costin: importa CSV migrare + XML e-Factura -> "gata XML"; eu rulez aplica.py luna.
2. Costin: Control fiscal + Audit preluare + genereaza declaratiile -> confirma verdictele din README.
3. Orice "forma care spune altceva decat faptul" -> comanda de reparatie (ca turele 16-17-20).

## Unelte
- **Proba browser (Playwright)**: `ssh iconta 'cd ~/iconta_nou && venv/bin/python3 frontend_test/proba_wizard_antet.py'`
  (antet wizard; exit 0 = ok). Observatii per-wizard: frontend_test/observa_*.py. Auth via token, creds in
  ~/.iconta/fe_test.env (in afara git). Doar cabinet 4163. NU in poarta verde (rulare manuala; pytest nu colecteaza
  frontend_test/ - fisiere non-test_).
- Poarta verde: commit ruleaza pytest suita intreaga + verificator_conformitate (TOTAL 0); post-commit publica
  origin/main + backup/lant-<data>; apoi restart iconta-nou (four-way).
