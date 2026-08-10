Citeste CLAUDE.md §2.2 (structura raportului) si §2.3 (lant, siguranta, limba), si ARHITECT.md "FORMA COMENZII" (forma comenzii primite - 7 puncte), inainte de a incepe.

# PREDARE_LANT — STARE CURENTA

Se SUPRASCRIE la fiecare publicare (al 5-lea pas, CLAUDE.md §2.3 pct.10). NU e jurnal - jurnalul e ISTORIC.md.
Ritual pornire: `ssh iconta 'cd ~/iconta_nou && git log -1 && git status --porcelain'`.

## (a) Four-way de la ultima executie
Ultimul commit de COD: tura 29 (LANT legislatie TURA 3/4 - mesajul exact pre-DUK: validator identitate partajat
+ reparatii pe toate 10 declaratiile). Four-way exact (SHA + ora) = in raportul turei 29. Anterior: tura 28 = 8b74ccb
(CATALOG_INVALIDITATE). Serviciul iconta-nou ruleaza din ~/iconta_nou; static-ul servit de pe disc.

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

6. **Declaratii DUK — auditate + reparate (turele 24-26); RAMAS = doar decizii de model de date** — toate 10
   confruntate field-by-field cu sursa (tura 25); deciziile §6 ale lui Costin reparate (tura 26). Cod reparat:
   D112 asiguratD refuz + fixtures, D205 divid_D/P + Rezid, D300 taxare-inversa R12/R25 + 0% clasificat, D301
   pers_inreg reachable, D394 op11 manual + prsAfiliat, D406 TaxCode 380304 + PF master. Seed corectat: D390 CUI UE
   reale, D394 cereale 1005 -> D390/D394 acum VALID pe date. REGULA: XSD-vs-DUK -> validatorul e autoritatea.
   RAMAS (decizie Costin, NU defect de cod):
   (a) 3 COLOANE de date (cod gata + default sigur, NEadaugate ca sa nu atinga schema cabinetului 1968):
       firma_profil.inreg_art317 (D301 pers_inreg=2), firma_profil.are_operatiuni_afiliate (D394 prsAfiliat=1),
       facturi.natura_scutire (D300 clasificare livrari 0% R14/R15/export). + optional discriminator taxare_inversa
       art.331-vs-general (D300 R12/R25 vs R7/R20).
   (b) salveaza_concediu: gard simetric serie/numar/data_acordare/data_inceput (garanteaza doar D_7 acum) - UX la
       salvare, recomandat, neaplicat.
   (c) UI care sa POPULEZE campurile de mai sus (altfel raman pe default).
   Unealta: PYTHONPATH=$PWD venv/bin/python3 frontend_test/valideaza_duk.py.

## (c-lant) LANT LEGISLATIE (4 ture, Costin) - inchide "declaratie invalida" (T1-3) + "valida dar nereflectand
contabilitatea" (T4). Fiecare tura se raporteaza inainte de urmatoarea.
- TURA 1 (legislatia) = GATA tura 27: actul care aproba forma fiecarei declaratii adus in corpus (12 ordine
  oficiale). RAMAS de adus dintr-un mirror accesibil (legislatie.just.ro respinge serverul): D205 102/2025, CPF
  207/2015; CF master consolidat de reimprospatat (pre-2025). Flag: validatorul D112_209 e ANTERIOR formei
  605/2026 (iulie 2026) -> DUK server o generatie in urma pe D112.
- TURA 2 (datele care invalideaza) = GATA tura 28: CATALOG_INVALIDITATE.md - ~350 tipuri per declaratie (ce
  invalideaza / ce incalca / sursa / mesaj curent a/b/c/d) + 11 teme transversale. Tintele: TURA 3 (T1 checksum
  CUI/CNP nepre-validat 9/9, T2 valideaza() cod mort D300/D301/D406/D390, T3 coercitie tacita, T4 avertizeaza-dar-
  emite, T6 passthrough netrunchiat, T9 exceptii brute); TURA 4 (T7 semantic, T8 non-impunere DUK).
- TURA 3 (mesajul catre utilizator) = GATA tura 29: core/identitate.py (validator CUI/CNP partajat) + reparatii
  pe toate 10 declaratiile ca aplicatia sa arate motivul EXACT pre-DUK (T1 checksum, T2 valideaza() cablat, T3
  coercitii vizibile, T4 op11 exclus, T6 lungimi, T9 exceptii prietenoase) + fix conformitate D406 03+CNP. Baseline
  valid ramane DUK-valid. RAMAS decizii produs: D101 scadenta LL+3/LL+6, D394 G-x1 cota, D301 pers_inreg
  (inreg_art317), D390 VIES full-27, T10 feature (rectificativa etc.), T11 DUK D112_209.
- TURA 4 (reconcilierea sursa-vs-declaratie, gardata sa nu moara tacit - clasa D300 mort) - urmeaza dupa confirmare.
  Tinte din TURA 2/3: T7 (D205 imp1≠rate×baza, D301 RON curs≠1, D710 suma_ded, agregare mis-contabilizata, D100
  suma_dat) + T8 (D300 CR-5 R25=R12, D101 d_reg/d_succ/cod_bug).

## (c) Ce e in lucru acum
Conformitatea declaratiilor la spec oficial DUK (front 6) + firul de intrare (front 1). Turele recente:
20 proba browser + fix antet wizard, 22 ZERO-BASE avertisment, 23 DUK-validat + D100 gol refuzat, 24 refacut 4
declaratii la spec oficial, 25 TOATE 10 declaratiile confruntate field-by-field (8 reparate, 2 conforme), 26
reparate deciziile §6 Costin (6 declaratii cod + seed corectat + regula XSD-vs-DUK). Metoda 25-26: audit/fix paralel
cu agenti proaspeti + DUK pe date populate - a scos defecte pe care validarea pe nil le rata.

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
