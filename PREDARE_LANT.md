Citeste CLAUDE.md §2.2 (structura raportului) si §2.3 (lant, siguranta, limba), si ARHITECT.md "FORMA COMENZII" (forma comenzii primite - 7 puncte), inainte de a incepe.

# PREDARE_LANT — STARE CURENTA

Se SUPRASCRIE la fiecare publicare (al 5-lea pas, CLAUDE.md §2.3 pct.10). NU e jurnal - jurnalul e ISTORIC.md.
Ritual pornire: `ssh iconta 'cd ~/iconta_nou && git log -1 && git status --porcelain'`.

## (a) Four-way de la ultima executie
Ultimul commit de COD: tura 20 (fix antet wizard navigator.js + capacitate proba browser). Four-way exact (SHA + ora)
= in raportul turei 20. Anterior stabil: tura 19 = 888ae7d (izolare /raportari). Serviciul iconta-nou ruleaza din
~/iconta_nou; static-ul (js/css) e servit de pe disc.

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

6. **Declaratii DUK — 4 defecte structurale ramase (tura 23)** — validate oficial prima oara pe 4163; D100 gol
   reparat (refuz). RAMAN: D394 codPR 21 (la op11 = subcod NC 1001..., nu 21; seed cereale prea grosier);
   D112 asiguratB3 CM (zile/baza CAS pe indemnizatia de concediu medical); D301 data_doc ISO (bug de SEED,
   nu app - seed a ocolit ruta ZZ.LL.AAAA); D406 SupplierID pe PurchaseInvoices (SAF-T XSD). Fiecare = fix
   la sursa + gard + re-validare DUK. Unealta: frontend_test/valideaza_duk.py. BLOCAJ: neprogramate (una pe comanda).

## (c) Ce e in lucru acum
Parcurgerea firului de intrare (front 1). Turele recente: 13 izolare cheie API, 14 cross-check D300 mort, 16 doua
"forme care spun altceva", 17 diacritice solduri, 18 PREDARE al 5-lea pas de publicare, 19 izolare /raportari,
20 capacitate proba browser + fix antet wizard.

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
