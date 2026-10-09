## 25.09.2026 — **frontul-7 de formulare UI închis**: încă 6 declarații în selector (D318 le închide), comis `453af646`

**Pentru un contabil.** Ziua a schimbat ceva concret: **încă șase declarații** au acum formular de completat direct în
aplicație, în selectorul de declarații (înainte se puteau doar prin API, nu de la ecran):
- **D600** — baza estimată pentru CAS/CASS (persoane fizice care își estimează venitul);
- **D104** — distribuirea veniturilor/cheltuielilor între asociați (asocieri fără personalitate juridică);
- **D114** — CAM (contribuția asiguratorie pentru muncă), cazul care nu trece prin D112;
- **D110** — regularizarea/restituirea impozitului reținut la sursă (cu IBAN pentru restituire);
- **D398** — OSS, TVA la regimuri speciale UE/non-UE/import (livrări pe fiecare stat de consum);
- **D318** — **cererea de rambursare a TVA plătită în alt stat membru UE** (Directiva 2008/9/CE): perioada de rambursare
  (implicit tot anul), contul de rambursare (IBAN/BIC), activitatea (cod NACE) și facturile de achiziție/import din statul
  respectiv, cu furnizorul UE.

Împreună cu **D603** (exceptare CASS), livrată în noaptea de 24.09, acestea sunt cele **7 declarații ale frontului**.
Cu cele 13 dinainte, sunt acum **20 de declarații cu formular** în aplicație. Fiecare a fost probată cu validatorul oficial
ANAF (DUKIntegrator) și dă „valid". Producția a trecut la `453af646`.

*Context (24.09, în git, nescris încă aici):* în aceeași zi cu D603 au intrat în selector și restul declarațiilor D2xx
(D230 redirecționare 3,5% · D204/D223 asocieri · D216 impozit bunuri de valoare mare · D208 transfer imobiliare · D221
venituri agricole), plus D220 documentată ca acoperită de D212; și cele 14 acte lipsă din corpus (deblocând ghidurile).

**Ce s-a făcut (tehnic).** Cele 7 declarații, în ordinea cerută de Costin (D603→D600→D104→D114→D110→D398→D318), pe
**tiparul „proof-of-pattern" identic** cu frontul D2xx: backend = scos din `_DOAR_API` (intră în selector) + bloc
`valideaza_cerere` cu mesaj de contabil; frontend `declaratii.js` = stare `S.dXXX`, `_dXXXManual()`, `randeazaFormularDXXX()`;
gard structural `core/test_dXXX_formular.py` (ElementTree, nu „șir" in xml); probă F4 `frontend_test/proba_dXXX_f4.py` (DUK
„valid"); rând FUNCTIONALITATI.csv → LIVE; cascadă doc-sync (login.js GRUPE_FUNC, `?v=`, 3 artefacte ui_hash, GARZI.md).
Câte un commit + four-way fiecare — D603 `cc1027f8`, D600 `b24c6287`, D104 `940a72ef`, D114 `5eea2150`, D110 `a25fb9b4`,
D398 `df371a83`, **D318 `453af646`** (închiderea).

- **Constrângeri DUK per declarație, documentate ca increment (nu ascunse):** D603 folosește coduri de județ auto (2 litere,
  ex. CJ), nu numerice; D600 acceptă doar `cas_opt=1` + baze lunare (intervalele libere sunt respinse); D114 restricționează
  luna (luna=6 validă); D318 = cea mai adânc-nested (D318 > Applicant + BusinessDescription + PurchaseInformation > EuSupplier
  + GoodsDescriptionP), DUK-valid din prima probă.
- **Cerința „fără estimări de durată":** fiecare operație a fost MĂSURATĂ în ms (`_artefacte_masurare/front7_durate.tsv` din
  ZIP). Lecția vizibilă: munca de fond (patch/gardă/probă/cascadă) e de ordinul zecilor–miilor de ms, iar **poarta+four-way
  domină fiecare commit cu ~37 min** — costul frontului e poarta, nu construcția.
- **Livrare:** `/home/costin/livrari/front7_declaratii_453af646.zip` (634 KB, 39 fișiere) — cod + GARZI.md +
  FUNCTIONALITATI.csv + artefacte ui_hash + `front7_durate.tsv` + `_livrare/{COMMITURI,DIFFSTAT,FISIERE_SCHIMBATE}`.
- **O reparație pe parcurs:** primul regen GARZI.md la D318 dublase markerii `INVENTAR-GARZI` (`redare_md()` include markerii;
  înlocuirea corectă e tot blocul START..STOP). Prinsă de `test_garzi_inventar` la sweep, refăcută, verde.
- **Poarta verde** la fiecare din cele 7; la D318: **6542 passed**, verificator TOTAL 0, four-way 2/2.

## 23.09.2026 (noapte) — **D201 în selector** (a treia declarație D2xx din Task 2, comisă `c7f94f22`)

**Pentru un contabil:** Declarația 201 (veniturile realizate din străinătate de persoane fizice) e acum în selectorul
de declarații: identitate PF (CNP/nume/inițiala tatălui/prenume) + secțiuni pe pereche (țară, categorie de venit), cu
venit brut/cheltuieli/impozit plătit în străinătate. Producția a trecut de la `28bb92ad` la `c7f94f22`.

**Ce s-a făcut (tehnic).** Task 2, a treia declarație: **D201** (pe tiparul D200). `d201` scos din `_DOAR_API`;
formular-listă în `declaratii.js` (`S.d201`, `_d201Manual()`, `randeazaFormularD201()`) cu identitate + secțiuni; câmpuri
condiționate pe categorie (categ=23 = doar venit net; categ=14 = admite impozit pe salarii, imp2). venit_N = venit_B −
chlt_D calculat.
- **Increment (ca D212):** categ_venit + codurile de țară ISO-3166 numerice trăiesc în bytecode-ul validatorului, nu în
  corpus — deci contabilul introduce codurile (cu text ajutor: Germania 276, Franța 250…), nu dropdown din nomenclator.
- **DUK-valid pe F4:** `proba_d201_f4.py` (categ=3, țara=276, venit 1000 → `valid`). Gard `core/test_d201_formular.py`
  (5 teste structurale: R33 imp2/categ14, R30 venit_N). FUNCTIONALITATI.csv: F222 AMÂNAT → LIVE. Ajutor „?" = F222.
- **Poarta verde: 6436 passed**, verificator TOTAL 0. Cascada doc-sync (login.js grupe Fiscalitate 33→34, ?v=, 3 artefacte).

**Un incident operațional:** push-ul automat pe origin/main + backup a eșuat pe o eroare de server GitHub («Internal
Server Error», tranzitorie); public/main + prod erau OK. Rezolvat manual (`git push origin HEAD:main` + `HEAD:backup/...`),
four-way închis complet. *Lecție (R176): un braț four-way poate rămâne deschis dintr-un hopa GitHub, nu doar dintr-un bug.*

## 23.09.2026 (târziu) — **două corecții fiscale de producție** (IMCA 0,5% 2026 + câștig lichidare 10%), comise `28bb92ad`

**Pentru un contabil:** două cote greșite în calculul automat, care puteau umfla declarații D101 / note de lichidare
reale, sunt corectate. Cerute de Costin, verificate la sursă înainte (Cod fiscal consolidat + ghiduri).

1. **IMCA** (`core/d101.py`): cota era **1% fix**. OUG 89/2025 (MO 1203/24.12.2025) reduce cota IMCA de la 1% la
   **0,5% pentru anul fiscal 2026** (CF art.18^1; aplicare până la 31.12.2026). Acum versionată pe an
   (`_VARIANTE_COTA_IMCA`, Temei inline, tiparul `_VARIANTE_SCADENTA`): 1% până în 2025, 0,5% din 2026. Efect:
   P47 pentru 2026 se înjumătățește (272M bază: 2.720.000 → 1.360.000).
2. **Câștig din lichidare** (`core/lichidare.py`): impozitul pe câștigul din lichidare la asociat **PF** folosea
   **greșit cota dividendelor** (art.97 alin.7, 16% din 2026). Temeiul corect e **CF art.97 alin.(5): cotă FIXĂ
   10%**, impozit final — articol și cotă DISTINCTE de dividende; alin.(5) e neschimbat de Legea 141/2025 (care
   a modificat alin.7=dividende). Verificat verbatim în codul consolidat (linia 9458) + ghidul de lichidare
   (care documenta chiar el bug-ul). Efect: `partaj` reține 10% (nu 16%) — corectată o suprataxare de 60% din 2026.

**Lecția (scrisă în [[doc-sync-cascada-la-schimbari-cod]]): o schimbare de cotă fiscală are o rază largă de
doc-sync.** Poarta a respins de DOUĂ ori (7 apoi 2 gărzi) — fiecare o gardă de sincronizare a registrelor de
temeiuri. Cea mai instructivă: **un articol CF NEMODIFICAT (art.97 alin.5) nu intră curat în `common.COTE`** —
G1 (COTE+MO cere url) și convenția interdicției 50 (articol CF cere url ≠ codul fiscal) intră în conflict fiindcă
nu există act modificator de citat. Soluția: cota ținută **inline** în modul (`_VARIANTE_...` cu Temei inline),
ca IMCA. COTE rămâne pentru cote cu istoric de acte modificatoare (dividendele: L141/OUG156/OG16).

Ghidul `calcul-venit-lichidare-societate.md` adus la zi: claimul „aplicația calculează cu cota dividendelor" →
„aplică 10%"; rămâne consemnată limitarea PF/PJ (art.23 lit.j — asociatul PJ cu deținere nu e distins).

## 23.09.2026 (seara) — **D212 în selector** (a doua declarație D2xx din Task 2, increment, comisă `6a6be4ca`)

**Pentru un contabil:** Declarația unică (D212) e acum în selectorul de declarații: se completează identitatea PF
(CNP/nume/adresă), se poate „trage fișa RIP" (venit net + CAS/CASS + impozit din registrul de încasări/plăți, informativ),
și se generează declarația de identificare. Producția a trecut de la `ad548790` la `6a6be4ca`.

**Ce s-a făcut (tehnic).** Task 2, a doua declarație: **D212** (increment, decizie Costin — NU full-populat). Pe tiparul D200:
`d212` scos din `_DOAR_API`; formular `S.d212` (identitate) + `_d212Manual()` + `randeazaFormularD212()` (identitate +
„Trage fișa RIP" afișată informativ); generează cazul minim DUK-valid (identitate + bife 0; `totalPlata_A` = suma cifrelor
CNP, DUK regula R4).
- **DUK `valid` pe F4** (tenant_052): `frontend_test/proba_d212_f4.py` — gol refuzat, identitate → DUK valid; fișa RIP citită (0 pe F4, fără operațiuni RIP).
- **Gard** `core/test_d212_formular.py` (4 teste structurale, ElementTree). FUNCTIONALITATI.csv: F246 AMANAT → LIVE. Ajutor „?" = F030 (Motor D212).
- **Poarta verde: 6429 passed**, verificator TOTAL 0, four-way închis (`6a6be4ca`).

**Trei respingeri de poartă, fiecare o cascadă doc-sync** (poarta a avut dreptate de fiecare dată):
1. `ui_hash` GLOBAL → 3 probe stale (`test_asistent_arbore` + `test_declaratii_50`, nu doar scanul vizual) → re-rulat toate 3.
2. `test_live_accesibil` (regula 9): declarație în selector ⇒ rândul CSV trebuie LIVE → F246 flip-uit. Plus `test_temeiuri`:
   „regula R4" în `core/*.py` cere prefixul canonic „DUK regula".
3. Verificator GRUPE_FUNC: flip-ul LIVE a dus D212 în grupele publice (`login.js`) → `genereaza_grupe_functii.py --scrie`
   (Fiscalitate 32→33, total 152) → versioneaza (`app.js` ?v=) → **al treilea re-scan** al celor 3 probe.
*Lecția: un flip AMANAT→LIVE nu e o schimbare de o linie — cascadează prin selector, grupe publice (login.js), ?v= și cele 3
artefacte ui_hash. Scris acum în PREDARE „primul lucru".*

**D212 full-populat (cap11/oblig_realizat din fișa RIP) rămâne backlog R&D DUK necartografiat** (categ_venit cap11 ≠ D200 -
doar în bytecode-ul validatorului; R4 cu obligații; ~90 câmpuri) — v. PREDARE „primul lucru" + `/tmp/duk_probe_d212.py`.

## 23.09.2026 — **D200 e LIVE** (prima declarație D2xx PFA din Task 2, comisă `ad548790`)

**Pentru un contabil:** Declarația 200 (veniturile realizate din România de persoane fizice) e acum **disponibilă** în
selectorul de declarații — se poate completa (identitate + secțiuni pe categorie de venit) și genera. Producția a trecut
de la `4641e568` la `ad548790` (four-way închis).

**Ce s-a făcut (tehnic).** Task 2 (UI pentru declarațiile D2xx PFA), prima declarație: **D200**. Comis `ad548790`, LIVE.
- **Formular manual** în `static/js/ecrane/declaratii.js`: identitate PF (nume + prenume **separat** — validatorul
  respinge `prenume_c` vid) + secțiuni pe categorie de venit. Nomenclatorul `categ_venit` (1,2,3,4,5,7,9,10,13,14) adus
  de la **sursa oficială ANAF** (`structura_D200`), nu ghicit — validatorul acceptă doar codul numeric. Reguli pe
  categorie: 14=câștig/pierdere, 13=jocuri de noroc (cere organizator).
- **Backend:** d200 scos din `_DOAR_API` (intră în selectorul de declarații) + bloc de validare (gol → mesaj de contabil).
- **DUK-valid pe F4** (tenant_052): `frontend_test/proba_d200_f4.py` — apel gol refuzat, generat (venit net 70000), DUK `valid`.
- **Gard** `core/test_d200_formular.py` (6 teste structurale, ElementTree) + cascada doc-sync (pagina publică, GARZI.md, `?v=`).
- **Poarta verde: 6423 passed**, four-way închis (origin=public=backup=proces viu, 2/2 procese pe `ad548790`).

**Trei lecții din închidere (merită păstrate).**
- **Calea scanului vizual, rezolvată (decizie Costin).** Scanul nu putea rula pe 8010/prod: conturile de test
  (`patron@prisma-cont.test`, `fir-intrare@prisma-cont.test`) NU există în producție (`patron` face `w_auth` să pice la
  import; `fir-intrare` din `fe_test.env` dă 401 pe prod). Nici 8011 cu doar `test.env` (n-are `JWT_SECRET`). Soluția:
  **8011 pe iconta_test cu `test.env` (DB) + `api_keys.env` (JWT)** — mediul nativ al scanului (conturi + JWT). Rețeta e în
  PREDARE_LANT.md „primul lucru".
- **`ui_hash()` e GLOBAL** — o editare de JS face stale **trei** artefacte de probă, nu unul: `acoperire_vizuala.json`,
  `proba_decl50.json`, `proba_r175_arbore_asistent.json`. Prima poartă a picat pe ultimele două (`test_asistent_arbore`,
  `test_declaratii_50`) fiindcă re-rulasem doar scanul vizual. Reparat re-rulând toate trei pe 8011.
- **Operațional (prod curat acum):** o publicare din arbore pe prod (restaurată la HEAD prin trap) + un `pkill -f` (evitat
  acum: kill pe PID). Prod verificat: static=`ad548790`, 8010=200.

## 20.09.2026 — SESIUNEA B: Faza 0 (curățenie prod) + F1 etapele 1-2 prin interfață

**Pentru un contabil:** portofoliul de test a fost șters complet (clean slate), păstrând doar contul de
platformă al lui Costin. Apoi prima firmă de test (F1) a fost creată și configurată EXACT ca de un
contabil care intră prima dată — prin ecranele reale, nu prin script: înregistrare cabinet, adăugare
firmă, vector fiscal, preluarea soldurilor/partenerilor/stocului/salariaților.

**Ce s-a făcut (tehnic).** Sesiunea B (testare pe flux), Faza 0 + Faza 1 F1 etapele 1-2 (DECIZII 60).
- **Faza 0:** backup + ștergerea a 55 cabinete (gdpr_sterge canonic) + 4 superadmini test + 19 tenants
  `ztest_` orfani + 33 scheme (`scripts/curata_ztest_orfani.py`, gard de scop, permisiune îngustă).
  Rezultat: cabinete=0, tenants=0, scheme=0, useri=1 (id=1 păstrat), referință/sistem intacte.
- **F1 etapa 2 (config):** `frontend_test/proba_f1_etape12.py` (Playwright, UI real): înregistrare cabinet
  → login → adaugă F1 (SRL, CUI RO401002001) → Date firmă → vector fiscal (micro, TVA lunar, fără IC).
- **F1 etapa 1 (preluare):** upload prin interfață a 4 CSV-uri (solduri, parteneri, articole/stoc,
  salariați). **Invarianți verificați în DB (tenant_049):** Σdebit=Σcredit=**17.000** (ECHILIBRAT),
  plan 185 conturi (auto-completat), 2 solduri parteneri, 1 articol / stoc 5.000, **3 salariați activi**
  (salariu în salariu_istoric de la 2026-01-01), vector = D300/D394/D112/**D100**/D406.
- **Fișier de așteptări** scris ÎNAINTE (`frontend_test/asteptari_f1.md`), din temeiuri; D101→D100 corectat.
- Observație pentru etapa 4: salariu_brut=0 pe rândul salariat, salariul e în istoric — de verificat la
  stat de plată. Vezi DECIZII (60).

## 20.09.2026 — GARZI cat.1 sub-lotul 2: mijloace_fixe UNIQUE(cod) (după curățare duplicat proba tenant_003)

**Pentru un contabil:** un mijloc fix nu se mai poate dubla pe același cod de inventar la reimport — codul
e unic. Înainte, un import repetat putea crea același activ de mai multe ori.

**Ce s-a făcut (tehnic).** GARZI cat.1 sub-lotul 2 (decizia Costin 20.09, DECIZII 59). tenant_003 avea 8
rânduri `NEC-SOF` identice (reziduu din rulări repetate ale testului E2-F, zero FK) — șterse (varianta a,
niciunul activ real). Apoi `UNIQUE(cod)` pe `mijloace_fixe` (migrare pe 20 scheme + tenant_template),
`mijloace_fixe` scos din whitelist-ul ratchet `core/test_intrare_date_garduri.py` (mutație: scos UNIQUE
din template → ratchet RED). Rămâne `produse` singurul tabel de import fără cheie (fără câmp de cod,
decizie de schemă deschisă). Vezi DECIZII (59), GARZI cat.1.

## 20.09.2026 — GARZI cat.1 sub-lotul 1: NOT NULL pe bani + chei naturale UNIQUE pe import

**Pentru un contabil:** două clase de greșeli tăcute devin acum imposibile la nivelul bazei. (1) O sumă
lipsă nu mai poate deveni NULL → 0 nevăzut: coloanele de bani sunt NOT NULL. (2) Datele-cheie importate
(furnizori/clienți pe CUI, asociați pe CNP, solduri pe cont, facturi SPV pe mesaj, articole pe cod de bare,
state de plată pe salariat×lună) nu se mai pot dubla la reimport — au cheie unică. Excepțiile firești
(cursul valutar pe o factură în lei, un client persoană fizică fără CUI) rămân permise, declarat.

**Ce s-a făcut (tehnic).** GARZI cat.1 (Intrare date), LIPSA linia 69-70. Sub-lotul 1 (decizia Costin 20.09,
DECIZII 58): NOT NULL pe 13 coloane de bani (cat. A cu 0 NULL + cat. B cu default 0; 3 candidate excluse la poartă — vezi mai jos); UNIQUE natural pe 8
tabele de import curate — cu trei corecții ridicate la sursă (produse exclus, fără câmp de cod; articole pe
`barcode` nu `cod`; solduri_parteneri pe `(cont, cui)` nu `(cont)`). `core/migrare_intrare_date_garduri.py`
+ tenant_template (aplicat pe 20 scheme reale + baza de test). Gard-ratchet `core/test_intrare_date_garduri.py`
(6 teste: coloană de bani nullable nedeclarată / tabel de import fără cheie nedeclarat PICĂ; whitelist-uri
anti-stale; funcțional UniqueViolation/NotNullViolation; mutație pe template → RED). Sub-lotul 2 (mijloace_fixe)
separat, după curățarea unui duplicat real de cod în tenant_003. Vezi DECIZII (58), GARZI cat.1.

## 20.09.2026 — C5: import extras bancar idempotent (tabel `extras_import`, hash de fișier)

**Pentru un contabil:** dacă reimporți din greșeală același extras bancar (dublu-click, sau conexiunea
a picat după ce serverul salvase deja), aplicația nu mai adaugă liniile a doua oară — îți spune „extras
deja importat: N linii" și nu dublează nimic. Înainte, un reimport dubla toate liniile → notele pe 5121
se dublau. Două tranzacții reale identice în același extras (ex. două comisioane egale în aceeași zi)
rămân amândouă — dedup-ul e pe FIȘIER, nu pe conținutul liniei.

**Ce s-a făcut (tehnic).** Restanța **C5** din auditul independent 2026-09-17, confirmată la sursă +
funcțional (2 importuri identice → 4 rânduri). Decizia Costin (20.09, varianta A): idempotență la nivel
de fișier, pe hash de conținut. (1) Tabel nou `extras_import` (`core/migrare_extras_import.py` +
tenant_template; aplicat pe cele 20 de scheme reale + baza de test) cu `UNIQUE(fisier_hash)`. (2)
`repo_banca.inregistreaza_import` (INSERT ON CONFLICT DO NOTHING RETURNING id — race-safe pe cursa
dublu-click) + `import_existent_nr_linii`. (3) `reconciliere_api.importa_extras` primește `continut`,
hash-uiește, și la reimport întoarce `{"deja_importat": True, "nr_linii": N, "linii": []}` fără să
insereze. (4) Frontend `firme.js`: mesaj vizibil „Extras deja importat: N linii" (nu no-op tăcut). Notă:
`conteaza` bloca deja dubla-contare a aceleiași linii — dublarea notelor venea EXCLUSIV din rândurile
duplicate, deci idempotența la import e fix-ul rădăcină. Garduri `core/test_c5_extras_idempotent.py` (4,
end-to-end pe schemă efemeră; mutație = gard dezactivat → reimport dublează → RED). Vezi DECIZII (56).

## 19.09.2026 — A12b (UI, A12 ÎNCHIS): clasificare destinație TVA per linie pe ecranul de validare SPV

**Pentru un contabil:** la validarea unei facturi primite din SPV (e-Factura), fiecare linie importată
primește acum un selector „destinație TVA" — **taxabilă** (implicit, deducere integrală), **scutită**
(fără deducere) sau **mixtă** (intră în pro-rata, art. 300 alin. (5)). Restul liniei rămâne read-only:
faptul importat din XML nu se editează, doar se clasifică. Alegerea ajunge exact pe achiziția din D300,
deci pro-rata se aplică doar liniilor „mixt". Închide A12 pe calea SPV (partea „UI urmează" din A12 PART A).

**Ce s-a făcut (tehnic).** (1) Regulă DS nouă **cap.28** (clasificare per-linie pe ecran de validare a
documentelor importate) + gard verificator **CLASIF_SELECT** (un `<select>` de clasificare `pr-dest` fără
`aria-label` pică poarta; `.camp-input` e deja cerut de INPUT_NECONFORM). (2) Frontend: `primitaDetaliu`
randează per linie un `<select class="camp-input pr-dest">` (taxabilă/scutită/mixtă, default `selected`),
trimis ca `destinatii[]` în ordinea liniilor. (3) Backend: `factura_primita_valideaza` aplică
`repo_facturi.actualizeaza_destinatii_linii(fid_final, destinatii)` — UPDATE în ordinea liniilor (ORDER BY
id), robustă și la dedup (liniile pre-existente). Valoare în afara setului închis → `ValueError`, nu
scriere tăcută. **Verificat la sursă:** calea „flat" (operatiuni_ecran) e complet separată de
`primitaDetaliu`; din 34 de operațiuni flat, doar 4 creează facturi, toate regimuri speciale (taxare
inversă/IC/neînregistrat/necorporală), niciuna achiziție art.300-general → varianta (a) e suficientă.
Garduri: `core/test_a12b_destinatie_linie.py` (4, end-to-end pe XML real cu 2 linii; mutație ORDER BY
DESC → 2 teste RED, revertită). Vezi DECIZII (55), DESIGN_SYSTEM cap.28.

## 19.09.2026 — A12 (nucleu fiscal): pro-rata TVA doar pe achizițiile mixte, clasificate per linie

**Pentru un contabil:** la o firmă cu regim mixt (pro-rata < 100%), ajustarea de pro-rata se aplică
acum DOAR pe achizițiile marcate „mixt", nu pe tot deductibilul. O achiziție „exclusiv taxabilă" se
deduce integral chiar la pro-rata sub 100%; una „exclusiv scutită" nu se mai deduce deloc (și se
semnalează). Clasificarea e per LINIE de achiziție (`destinație TVA`), implicit „exclusiv taxabilă".

**Ce s-a făcut (tehnic).** Coloană nouă `factura_linii.destinatie_tva` (`core/migrare_destinatie_tva.py`
+ tenant_template; aplicată pe cele 20 de scheme reale). În `d300`, destinația călătorește prin
`_segmente` → bucla `ded`: scutit exclus (art.300 alin.4), mixt izolat → `R31_2` pe `ded_mixt_t` (alin.
3/5/11), nu pe tot `r28_2`. Garduri (test_d300): pro-rata **-42 nu -84** (mutație), taxabil neatins la
pro_rata<100, scutit exclus; DUK valid. LIMITĂ: la TVA la încasare decontările pierd destinația liniei
→ baza pro-rata rămâne r28_2 (combinație rară). Vezi DECIZII (54). **UI (câmpul pe formular) urmează.**

## 19.09.2026 — A9 part 2 (A9 ÎNCHIS): tvaDedAI = TVA pe facturile AI achitate în perioadă

**Pentru un contabil:** câmpul `tvaDedAI` din D394 (TVA dedusă pe achizițiile de la furnizori cu TVA la
încasare) nu mai e 0 fix, ci reflectă **TVA-ul de pe facturile AI plătite efectiv în perioadă** (deducerea
e amânată până la plată, art.297 alin.2). Plată integrală → toată TVA-ul; plată parțială → proporțional;
neplătit → 0.

**Ce s-a făcut (tehnic).** `d394._tva_ded_ai_platite` calculează, în `pull()`, TVA dedusă per cotă din
decontările reale, reutilizând tiparul plăți-AI din D300 (`repo_d300.select_inregistrari_2` = plăți pe cont
401 pe facturi cu `furnizor_tva_incasare`, + `d300._aloca_pe_cote` = apartajarea sumei plătite pe cote) —
SURSĂ UNICĂ, nu a doua interogare. `calcul_d394` rămâne pur (primește `date["tva_ded_ai"]`). Garduri:
plată integrală→210, parțială 605→105, neachitat→0; DUK valid cu tvaDedAI populat. Vezi DECIZII (53).
**A9 (audit R2) e ÎNCHIS** (part 1 tip AI + freeze; part 2 tvaDedAI real).

## 19.09.2026 — A9 part 1: D394 emite tipul AI, iar statutul furnizorului vine din ANAF

**Pentru un contabil:** o achizitie de la un furnizor care aplica TVA la incasare apare acum in D394 cu
tipul corect **AI** (inainte era raportata ca achizitie normala „A"). Statutul „furnizor cu TVA la
incasare" se ia automat din ANAF la introducerea facturii (nu mai depinde doar de bifa manuala), din
serviciul ANAF deja folosit pentru verificarea platitorului de TVA.

**Ce s-a facut (tehnic).** `anaf_api.furnizor_incasare_freeze` (oglinda `platitor_tva_freeze`, aceeasi
sursa `valideaza_cui`→`RTVAI.statusTvaIncasare`), apelat la ingestia facturii primite in
`uc_tenants.factura_creeaza` (inainte de conexiune, ca sa nu tina o conexiune peste apelul ANAF).
`repo_d394.select_facturi` aduce `furnizor_tva_incasare`; `d394.tip_operatiune`→"AI" (art.297 alin.2;
alin.3 exclude taxarea inversa/IC/import). Garduri: `test_d394` (AI vs A, mutatie + DUK valid),
`test_anaf_api` (freeze best-effort). Vezi DECIZII (53).

**Part 2 (in lucru):** `tvaDedAI*` = TVA pe facturile AI ACHITATE in perioada (art.297 alin.2), per cota
— refoloseste tiparul plati-AI din D300. Azi tvaDedAI ramane 0 (corect pentru AI neachitat; DUK valid).

## 19.09.2026 — A11 inchisa: exigibilitatea IC in D300 aliniata la art.284 (ca D390)

**Pentru un contabil:** o factura intracomunitara (achizitie/livrare in UE) intra acum in decontul de TVA
(D300) pe ACEEASI luna ca in declaratia recapitulativa (D390). Inainte, o factura IC cu faptul generator
intr-o luna si factura emisa in luna urmatoare putea aparea in D300 pe luna faptului si in D390 pe luna
facturii — aceeasi operatiune, doua luni, reconciliere ANAF rosie degeaba.

**Ce s-a facut (tehnic).** D300 aplica pe latura IC (partener UE) exigibilitatea art.284 alin.(2) /
art.283 alin.(1) — data emiterii sau a 15-a zi a lunii urmatoare faptului, oricare mai devreme (LEAST) —
nu regula generala art.282 (COALESCE). Expresia traieste intr-un singur loc (`core/d390.py::EXIG_IC`),
folosita de ambele declaratii; `core/d300.py::_exig_d300()` o combina cu regula interna. Gard nou
`test_A11_exigibilitate_IC_d300_aceeasi_luna_ca_d390`, mutatie probata. Vezi DECIZII (52).

**Supersedeaza** consemnarea din 18.09 (mai jos) care lista A11 printre restantele DESCHISE: A11 e acum
INCHISA. A9 si A12 raman deschise, blocate pe decizii de date (sursa `furnizor_tva_incasare` din registrul
ANAF; clasificarea destinatiei achizitiilor pentru pro-rata).

## 18.09.2026 — **da, s-au schimbat patru cifre pe care le depui**

**Pentru un contabil: patru corecții, fiecare la o cifră care pleacă la ANAF.** Toate au venit dintr-un
audit independent al aplicației, iar fiecare a fost reparată cu o probă care merge de la cazul contabil
până în rândul declarației.

- **Dividende (D205): cota se ia după data DISTRIBUIRII, nu după anul depunerii.** Un dividend aprobat
  în 2025 și plătit la începutul lui 2026 se impozitează acum cu **10%** (cota de la distribuire), nu cu
  16% (Legea 141/2025 art. VII: cei care au distribuit interimar în 2025 rămân la 10%, fără recalculare).
  Înainte, o astfel de plată ieșea supradeclarată cu 6% din dividend — cazul cel mai frecvent de la
  început de an.
- **Impozit pe profit (D100): se calculează CUMULAT de la 1 ianuarie.** Plata trimestrială e diferența
  față de ce s-a impozitat deja, iar pierderea unui trimestru scade cumulatul. Un trimestru cu profit
  după unul cu pierdere nu mai plătește 16% pe tot profitul lui, ci pe cumulat (art. 41 Cod fiscal).
- **Import e-Factura: baza liniei ia reducerea și prețul „la mia de bucăți".** Dacă factura UBL are o
  reducere pe linie (`AllowanceCharge`) sau un preț exprimat la o cantitate de bază (`BaseQuantity`),
  baza care intră în D300/D394 e acum cea reală — nu `cantitate × preț` brut, care o umfla.
- **Factură primită cu două cote (21 și 11): TVA deductibilă se face PE COTE.** Nota contabilă a unei
  facturi mixte nu mai aplică cota cea mai mare pe toată baza; 4426 se calculează pe fiecare cotă, iar
  controlul încrucișat cu D300 nu mai iese roșu degeaba.

**Ce s-a mai făcut, și NU se vede din scaunul contabilului:** o recalibrare mare a instrumentelor cu care
mă verific pe mine — scanerele care spun „ce rută atinge o cifră de declarație" și „ce n-are probă"
raportau cifre goale fiindcă erau oarbe pe câteva drumuri (apeluri prin parametru, citiri prin `%s`, nume
prinse dintr-un comentariu). Corectate, iar un clichet care spunea „zero" spune acum „zece", cu cele zece
rute numite. *Nu schimbă nicio cifră pe care o depui; schimbă cât de mult pot minți instrumentele mele
despre aplicație.* La fel, o reparație la o poartă internă care se blocase fiindcă a intrat a doua
jumătate a lunii (o verificare care se activează spre scadența TVA) — invizibilă din afară.

*Restanțe închise în runda asta: A1–A8, A10, B1–B4, C1–C3, E-nota, D1–D10. Restanțe rămase deschise, cu
motiv scris: A9, A11, A12, C4, C5, C6, plafonul micro, CAM pe concediul medical, `salarizare.cam`, și
căile de mașină din §0. Poarta: verde de trei ori azi — `d9de53a2`, `8bf059c2`, `5ff1b8ba`.*

## 17.09.2026, partea a doua — **nu s-a schimbat nimic pentru un contabil**

**Se scrie ca atare, nu se sare.** Restul zilei n-a atins niciun ecran, niciun refuz, nicio cifră și
nicio declarație. Dacă deschizi aplicația azi după-amiază, se poartă exact ca azi-dimineață. *O zi
fără schimbare, nescrisă, se citește peste o lună ca o zi în care nu s-a lucrat — și asta ar fi la
fel de fals ca o schimbare neconsemnată.*

**Ce s-a făcut, și de ce nu se vede din scaunul contabilului:**

- **Aplicația a primit un material de audit independent, publicat.** Tot ce se poate verifica despre
  ea — registrele, cifrele cu instrumentul care le recalculează, lista a ce **nu** e verificat,
  valorile fiscale cu temeiul și data verificării la sursă, măsurătorile brute — stă acum într-un
  singur loc, pe oglinda publică, unde poate fi citit de cineva din afară. *Nu schimbă ce face
  aplicația; schimbă cine poate să verifice ce face.*
- **S-a scris, negru pe alb, ce NU e verificat.** Fără atenuare: cele 53 de restanțe deschise cu
  starea lor, `xfail`-urile cu motivul, orbirea declarată a fiecărui instrument, rutele fără probă,
  și faptul că nicio declarație n-a fost depusă efectiv la ANAF prin aplicație. *Partea asta e cea
  care contează cel mai mult pentru un contabil care ar folosi-o pe date reale, chiar dacă nu se
  vede pe niciun ecran.*
- **Starea proiectului s-a scris ca stare:** lanțul e **în așteptarea folosirii aplicației de către
  Costin**, nu în așteptarea unei teme. Nu se mai alege nimic din backlog; ce iese din folosire
  devine lucrarea următoare.

**Ce s-a reparat, și e o reparație la un instrument al meu, nu la aplicație:** scanul care caută
chei și parole înainte de orice publicare **se număra pe sine** — mostrele lui de calibrare sunt
secrete sintetice scrise cu mâna, iar propria lui ieșire conținea fragmentele care se potriveau cu
tiparele ce le produseseră. Măsurat: 48 de potriviri cu el însuși numărat, 34 fără. *Un instrument
care se măsoară pe sine raportează creșteri care nu există în lumea măsurată.*

*Restanțe închise: niciuna. Restanțe deschise: niciuna. Poarta: verde de două ori, `b56bdca8` și
`d8034c54`.*

## 17.09.2026 — **reevaluarea nu mai poate scădea o amortizare care nu s-a înregistrat**

**Pentru un contabil: da, s-a schimbat ceva, și e un refuz nou.** Dacă reevaluezi un mijloc fix
înainte de a fi înregistrat amortizarea lunilor scurse, aplicația **nu mai trece operațiunea**. Îți
spune de ce, cu cifrele pe masă: *fișa activului arată atât, contul de amortizare are atât, diferența
e atâta* — și îți spune ce să faci: înregistrează amortizarea lipsă, apoi reevaluarea merge.

**De ce e un refuz și nu un avertisment.** Reevaluarea începe prin scoaterea din evidență a
amortizării strânse. Dacă fișa a luat-o înainte, nota ar fi scăzut din cont o amortizare care nu
există acolo — soldul ar fi trecut pe minus, iar valoarea rămasă a activului ar fi devenit o cifră
care **arată bine și e greșită**: se calculează, se afișează, pleacă în declarație, și nimic n-o
contrazice. *Un avertisment ar fi lăsat-o să plece.*

**Și a doua schimbare, tot de azi:** nepotrivirea dintre registrul de imobilizări și contul de
amortizare — găsită ieri pe trei conturi reale — **cere acum confirmare scrisă înainte de depunere**.
Constatarea spune, de la prima frază, că poate numi **contul**, nu activul: amortizarea nu se ține pe
mijloc fix. *Cine o citește află ce are și ce n-are, în loc să caute un activ pe care constatarea nu-l
poate numi.*

*Restanțe închise: R115 (a doua oară), R192. Ambele pe deciziile lui Costin din 17.09.*

## 16.09.2026, partea a patra — **cele patru lucrări numite sunt terminate**

**Pentru un contabil, ce s-a schimbat azi în total, în ordinea în care se simte:**

1. **Reevaluarea unei imobilizări ajunge, în sfârșit, și în declarație.** Până azi fișa activului
   rămânea pe valoarea veche, iar SAF-T-ul anual declara către ANAF costul vechi.
2. **Aplicația compară amortizarea pe care o declară cu cea pe care a înregistrat-o** — și a găsit
   trei nepotriviri pe firmele existente, dintre care una de 900 de lei.
3. **Opt operațiuni care ajung în declarații au acum probă până în cifră**, nu doar până la „a
   mers": ieșire de stoc, inventar, reclasificare, reevaluare, contare bancară, chitanță de casă,
   consum de rețetă, import de firmă. *Nu se schimbă nimic din ce vezi; se schimbă ce nu mai poate
   trece neobservat.*
4. **Trei verificări spuneau că le face validatorul ANAF. Nu le face.** Le facem noi, înainte de
   depunere — și acum scrie corect cine le face. *Dacă cineva s-ar fi bazat pe validator pentru un
   `totalPlata_A` greșit sau o sumă zero pe o declarație inițială, ar fi trecut.*

**Trei lecții de metodă din ziua asta, fiecare plătită:**
- *Un `valid` de la validator nu înseamnă nimic până nu dovedești că valoarea rea era în fișier.*
- *`rollback` nu întoarce o secvență* — singurul lucru care supraviețuiește tranzacției.
- *Poarta rulează arborele de lucru, nu indexul* — un lucru în curs poate înroși commitul altcuiva.

*Restanțe închise azi: R59, R191. Deschise: R192 (așteaptă o decizie de produs), R115 (redeschisă —
tăria constatării noi e a lui Costin).*

## 16.09.2026, partea a treia — **aplicația compară, în sfârșit, amortizarea pe care o declară cu cea pe care a înregistrat-o**

**Pentru un contabil: nu se schimbă nimic din ce vezi azi, dar aplicația începe să-ți spună ceva ce
până acum nu putea.** Amortizarea unui mijloc fix se calculează în două locuri: în fișa activului
(de unde pleacă raportarea SAF-T către ANAF) și în nota lunară care intră în contabilitate. Până azi
nimic nu verifica dacă cele două spun același lucru.

**Acum verifică — și prima rulare a găsit trei nepotriviri pe firmele existente**, dintre care una
mare: o firmă la care fișele activelor spun 3.500 lei amortizare strânsă, iar contul din
contabilitate are 2.600. Cauza obișnuită e simplă și reparabilă: nota lunară de amortizare n-a fost
generată pe una sau mai multe luni. Aplicația o spune acum, cu ambele cifre, și îți zice ce să faci.

**Ce NU face, deliberat: nu blochează nimic.** Constatarea se vede în supervizor și atât. Dacă cere
sau nu o confirmare înainte de depunere e o decizie a lui Costin, pe care n-o iau eu — și până o dă,
constatarea n-are niciun efect asupra depunerii.

**Când refuză să acuze.** Dacă există note încă în ciornă pe contul de amortizare, aplicația spune
*„nu mă pronunț încă"*, nu *„e greșit": diferența se poate închide chiar la validarea lor. La fel
dacă nu poate calcula amortizarea unui activ (metodă nepermisă de lege pe categoria lui) — atunci
propria ei cifră e incompletă, și n-are dreptul să acuze contabilitatea pentru asta.

**Ce a ieșit la iveală construind, și e despre unealta mea, nu despre aplicație:** prima formă a
comparației **tăcea** exact în cazul în care nu putea citi fișele — adică fix când ar fi trebuit să
strige. A prins-o propria ei probă, înainte de orice rulare pe date reale.

*Restanța închisă: R191. Restanță redeschisă: R115 (tăria constatării noi e a lui Costin). R192
rămâne deschisă: confruntarea există, decizia de produs nu.*

## 16.09.2026, partea a doua — **reevaluarea unei imobilizări ajunge, în sfârșit, și în declarație**

**Pentru un contabil: da, s-a schimbat ceva.** Până azi, când reevaluai un mijloc fix, aplicația
scria corect nota contabilă — dar **fișa activului rămânea pe valoarea veche**. Consecința pe care
n-o vedea nimeni: SAF-T-ul anual declara către ANAF **costul vechi**, iar amortizarea lunilor
următoare se calcula tot pe el. Două evidențe despre același utilaj, și nici una nu știa de cealaltă.

**Acum:** reevaluarea se consemnează ca propunere (notă ciornă, ca înainte), iar în momentul în care
**validezi nota**, fișa activului urcă la valoarea reevaluată — și declarația o declară. Măsurat pe
un activ de 3.000 lei reevaluat la 3.500: după ciornă declarația spune tot 3.000 (corect — nimic n-a
fost aprobat încă), după validare spune 3.500.

**Și ceva ce nu se vedea din cerință.** Amortizarea nu continuă pur și simplu pe valoarea nouă: la
reevaluare, amortizarea strânsă până atunci se **șterge** din valoarea activului (așa cere norma
contabilă), deci de la data aceea utilajul se amortizează de la zero, pe valoarea nouă, pe **durata
rămasă**. Dacă am fi urcat doar cifra din fișă, aplicația ar fi socotit amortizare care nu s-a
înregistrat niciodată — o greșeală mai greu de găsit decât cea reparată. Dacă durata normală s-a
epuizat deja, aplicația **refuză** și spune de ce: durata nouă se ia din raportul evaluatorului, nu
o poate inventa programul.

**Ce s-a întrebat pe validatorul oficial.** Un câmp din SAF-T (`AppreciationForPeriod`) era zero de
când există generatorul, iar acum poartă creșterea reală. Validatorul ANAF a fost rulat pe fișierul
nou: **valid**.

**Ce a ieșit la iveală reparând, și rămâne deschis:** cifra pe care nota o șterge din amortizare se
calculează din **motorul de amortizare**, nu din ce s-a înregistrat efectiv. Dacă reevaluezi înainte
de a genera amortizarea lunii, cele două nu coincid. E consemnat ca **R192** și se închide împreună
cu R191 — confruntarea dintre amortizarea declarată și cea înregistrată, care e chiar lucrarea
următoare.

*Restanța închisă: R59, deschisă pe 26.08.2026. Restanță deschisă: R192.*

## 16.09.2026 — **etapa 2 se închide; trei lucruri care schimbă ce vede contabilul, dintre care unul bloca declarația de tot**

**Pentru un contabil: da, azi s-a schimbat ceva, în trei locuri.** Nu e o zi de întărire.

**MIJLOACELE FIXE NU PUTEAU IEȘI DELOC ÎN SAF-T, de două zile.** Ruta care scoate lista de mijloace
fixe pentru D406 răspundea cu eroare la **orice** cerere — nu la una anume, la toate. Cine încerca să
genereze SAF-T-ul cu mijloace fixe nu primea nici fișier, nici un motiv pe care să-l poată citi.
Cauza, în cod: numele coloanelor se citeau **înainte** de a se face interogarea, deci veneau de la
interogarea dinainte sau lipseau cu totul. Reparat, și păzit de-acum: o gardă nouă cade dacă cineva
mai scrie vreodată cele două în ordinea greșită. *Defectul stătea de două zile și nu-l semnalase
nimeni — nu fiindcă nu se folosea, ci fiindcă eroarea era de tipul care nu ajunge la un om.*

**O ACHIZIȚIE INTRACOMUNITARĂ DE SERVICII AJUNGEA PE RÂNDUL BUNURILOR.** În decont, serviciile primite
din UE se declară la rândul 7, bunurile la rândul 5 — două rânduri diferite, cu aceeași sumă
posibilă. Aplicația întreba omul „bunuri sau servicii?" la introducere, **și apoi uita răspunsul**:
nu-l scria nicăieri, iar la generarea decontului totul cădea pe rândul bunurilor. Acum răspunsul se
scrie **pe factură**, ca o coloană a ei, și rămâne înghețat acolo: o factură emisă azi va spune
peste doi ani același lucru, indiferent ce s-a mai schimbat în fișe. *Alegerea a fost a lui Costin, și
motivul ei e mecanic: singura altă sursă posibilă — reclasificarea — ține minte perechea
partener-lună, deci n-ar fi putut despărți două operațiuni ale aceluiași partener din aceeași lună.*

**O VÂNZARE INTRACOMUNITARĂ NU PRODUCEA NICIO FACTURĂ.** Se înregistra ca operațiune, dar nu lăsa
niciun rând în facturi — iar fără rând în facturi nu ajungea nici în decont (rândurile 1 și 3), nici
în declarația 390. Practic: livrarea exista în aplicație și **lipsea din amândouă declarațiile**. Acum
emite factură, ca orice livrare, și s-a probat cap-coadă că ajunge în amândouă.

**Cât de mult s-a schimbat pe portofoliul viu:** deocamdată **nimic de recalculat**, fiindcă nicio
firmă din portofoliu n-are încă o achiziție IC de servicii sau o vânzare IC înregistrată pe calea
asta. Ca și ieri, defectele erau reale în cod și neexercitate în producție. *Diferența e că azi două
dintre ele ar fi produs o declarație greșită, nu una imposibil de generat — iar o declarație greșită
pleacă la ANAF fără să se plângă nimeni.*

**Restul zilei: etapa 2 a campaniei s-a închis.** Cele 29 de unități rămase — locurile prin care o
valoare intră în aplicație și ajunge într-o declarație — sunt acum probate una câte una, pe lanțul
întreg: valoarea intră, se înregistrează, ajunge în rândul corect al declarației cu suma corectă, iar
declarația se generează și trece validatorul oficial. **31 de lanțuri, 29 verzi.** Cele două roșii
n-au fost greșeli ale probei: erau chiar defectele de mai sus.

**Ce a mai ieșit la iveală ieri seară, și se scrie aici fiindcă ziua de ieri s-a consemnat la prânz:**
o **proformă** făcea decontul de TVA imposibil de generat, fiindcă a doua cale de verificare o
număra · o **achiziție intracomunitară** se scria ca fiind din România, deci lipsea din decont · iar
**două ortografii ale aceluiași partener** (cu și fără diacritice) fac declarația 394 de nedepus, și
nimic nu spunea asta înainte de a o trimite. Toate trei, reparate.

**Un lucru pe care l-am aflat greșind, și e de folos oricui atinge zona:** am lărgit interogarea ca să
aducă noua coloană, dar am uitat locul de dedesubt care **enumeră** câmpurile facturii — coloana
venea din bază și se pierdea o linie mai jos, tăcut, iar declarația arăta exact ca înainte. *Un
SELECT lărgit nu e o citire lărgită.* Și, tot azi: proba mea a citit greșit fișierul XML de cinci ori
la rând, iar a patra oară **a suprascris datele reale ale unui asociat** — refăcute din artefactul
probei dinainte. De-aceea fiecare probă are acum două lucruri pe care nu le avea: o verificare că
n-a măsurat în gol, și o desfacere care readuce starea de unde a plecat.

**Ce urmează nu se mai alege.** Costin a numit patru lucrări, în ordine: reevaluarea care nu ajunge la
registrul de amortizare · amortizarea calculată de două ori din surse diferite, fără nimic care să
confrunte cifrele · cele opt locuri prin care se scriu date de declarație fără nicio probă · și cele
opt trimiteri la validatorul oficial care nu se regăsesc în el. După ele nu se deschide nicio temă
nouă.

## 15.09.2026 — **planul E se închide; și, pentru prima dată în etapa asta, se schimbă o cifră pe care o vede contabilul**

**Pentru un contabil: da, azi s-a schimbat ceva** — și merită citit, fiindcă zilele dinainte au fost
toate „nimic vizibil".

**O PROFORMĂ NU MAI INTRĂ ÎN D300.** Până azi, o proformă emisă era numărată ca livrare taxabilă:
măsurat pe o firmă cu o singură operațiune în lună, o proformă de 500 + 105 lei dădea `R9_1=500`,
`R9_2=105`, TVA de plată 105. Iar dacă proforma se transforma apoi în factură, **aceeași operațiune
economică se declara de două ori**, în două luni. Cauza, în cod: interogarea principală a lui D300
filtra pe dată și pe status, dar niciodată pe **tipul documentului** — iar proforma primește un status
declarabil. Tiparul corect exista deja alături: D394 excludea proformele de mult. Acum regula trăiește
într-un singur loc (`nomenclator_status_factura.clauza_tip_document`), iar D300 o cere pe toate cele
patru drumuri ale lui prin `facturi`.

**PARTENERUL DIN D394 SE CITEȘTE DE PE FACTURĂ**, nu din fișa clientului. Până azi, o corectură de CUI
în fișa unui client schimba partenerul dintr-un D394 **regenerat pentru o lună trecută**, deși
documentul emis atunci spunea altceva. Decizia lui Costin, scrisă în registru: *factura e autoritatea;
istoria se corectează prin storno și reemitere, nu prin editarea fișei.* Fișa rămâne rezervă — o
factură veche fără cod fiscal, emisă doar pe `client_id`, și-ar pierde altfel partenerul cu totul.

**Cât de mult s-a schimbat azi, măsurat înainte de a atinge codul:** **zero**. Portofoliul viu are 47
de documente, toate de tip `factura` — nicio proformă, niciun aviz —, și 28 de facturi emise, niciuna
cu CUI diferit de fișă. Defectele erau reale în cod și **neexercitate în producție**. *Dacă
portofoliul ar fi avut proforme, reparația ar fi rescris declarații deja depuse, și ar fi cerut alt
plan — de-aia cifra se măsoară înainte, nu se presupune după.*

**Restul zilei a fost întărire**, fără efect vizibil: planul E s-a închis pe toate etapele lui.
`MODULE_CU_SQL_FARA_STRAT` **78 → 0** (E2a: registrul straturilor s-a lărgit la *orice* modul cu SQL,
cu migrările într-o clasă de excludere numită, nu tăcută) · `REPOSITORY care își deschid conexiunea`
**32 → 0** (E2b: 39 de `commit`-uri scoase din depozite, actul cursului BNR mutat în modulul lui, două
programe CLI plecate în `scripts/`, opt acte etichetate greșit care și-au primit stratul adevărat) ·
cele patru datorii fiscale din registru, **scoase** (E4) · iar subsetul rutelor care scriu în cifre de
declarație, **49 → 8**, cu probe care merg până în rândul declarației, nu până la codul HTTP.

**Două lucruri pe care le-am aflat greșind, și se scriu ca atare.** La E4, „dependența" scrisă în plan
— *o firmă de probă cu profilul potrivit* — **nu exista**: lipseau datele, nu firma, iar ele încap în
câteva rânduri semănate în schema efemeră a probei. Se aștepta de o lună și jumătate după trei
insert-uri. Și, tot la E4: pragul „75 de caractere" din datorie era **vechi** — din 03.08 fiecare câmp
are limita lui oficială, iar garda care conta **sărea** exact peste declarațiile din datorie. *Un test
care sare nu e o verificare, e o intenție.*

**E5 n-a fost închis: a fost mutat.** „Motoarele fiscale se pot citi" nu are criteriu de ieșire —
lizibilitatea nu se termină, fiindcă motoarele se schimbă odată cu legea. A devenit **regula 9** din
`PLAN_LUCRU.md`: un motor deschis pentru altceva se lasă citibil la închidere. *Un pas care nu se
poate închide, ținut în plan ca pas, e o datorie care crește tăcut în dreptul unui plan altfel
terminat.*




## 14.09.2026, partea a doua — **E1: ritmul se numără o singură dată**

Pentru un contabil: nimic vizibil. Aceleași praguri, același refuz, același text. Ce s-a schimbat e
**unde** se numără.

**Ce era.** Trei limitatoare anti-abuz țineau starea în memoria procesului — `_reset_rate`,
`_cui_rate`, `_magic_rate` —, iar funcția care le folosea își scria premisa în docstring:
*„in-memory, **single worker**"*. Premisa murise la P6 valul 3, când unitatea a primit
`WEB_CONCURRENCY=2`. Consecința, măsurată: **prag efectiv dublu** pe trei rute publice (una dintre
ele apără cheia ANAF), contoare golite la fiecare publicare, și un dicționar care nu uita niciodată
un IP — cheiat pe un antet venit din cerere.

**Ce e acum.** `public.cereri_ritm`, cu tiparul scris la P6 pentru `login_esecuri`: un rând per
cerere admisă, fereastra în `WHERE`, ștergerea celor expirate la fiecare scriere, ridicare la bază
căzută. Peste tipar, un lucru nou: un **blocaj consultativ pe `(cheie, ip)`**. La login, două
inserări concurente sunt amândouă adevărate; la ritm, două cereri simultane ar fi putut trece
amândouă de prag. *Cursa nu s-a micșorat, s-a scos.*

**Cum se știe că ține.** Nu din citirea codului: din **două procese reale**. Unul epuizează pragul
pe `/public/magic-link`, celălalt — alt PID, altă memorie — primește `429` la a șasea. Forma
dinainte ar fi răspuns `200`, fiindcă al doilea proces pornea cu dicționarul gol.

**Ce a rămas deschis, și se scrie ca să nu pară închis:** rotația jurnalelor. Fișierul e scris și
verificat (`config/iconta-logrotate`, `logrotate --debug` fără nicio notă), dar instalarea în
`/etc/logrotate.d/` cere root — ca `WEB_CONCURRENCY=2` la P6. Până atunci, `uvicorn.log` crește în
continuare, iar constatarea D3 din audit rămâne DESCHISĂ.

## 14.09.2026 — **planul de întărire P0…P7 se închide formal**

Pentru un contabil: nimic. Nicio linie de cod de producție n-a fost atinsă azi — e o zi de
consemnare, nu de lucru.

**Ce s-a scris.** Cei opt pași P0…P7 sunt marcați `CLOSED_ACCEPTED`, fiecare cu commitul lui final,
într-un tabel la capătul lui `PLAN_HARDENING.md`. Lângă el stau două lucruri care fac diferența
între o închidere și o declarație: **poarta care a lăsat-o să treacă**, copiată din ieșirea
hook-ului (5840 de teste, ruff OK, verificator `TOTAL: 0`, arbore curat), și **cele șase restanțe
care rămân deschise**, fiecare cu cifra ei și cu motivul pentru care nu blochează.

*O închidere care n-ar numi ce rămâne ar fi o cifră flatantă — exact clasa pe care planul o
păzește de opt pași.* Niciuna dintre cele șase n-are lucrare pornită, și niciuna nu contrazice
criteriul pasului ei: `_raspuns` e serializarea mutată la P5 · `D3`=1 e stratul HTTP însuși ·
cele 7 rute GRI sunt clichet, iar GRI nu e verde · cele 6 căi C5 au verdict scris · R178 și R183
sunt proprietăți ale configurației, măsurate, nu regresii.

**Ce rămâne în vigoare:** gărzile. Criteriile celor opt pași nu sunt propoziții dintr-un raport, ci
probe care rulează la fiecare commit.

## 13.09.2026, partea a cincea — **P7 · valul use-case: 385 de corpuri de rută, și faza se ÎNCHIDE**

Pentru un contabil, a cincea oară azi: nu s-a schimbat nimic. Aceleași ecrane, aceleași declarații,
aceleași refuzuri — cuvânt cu cuvânt, și asta nu mai e o promisiune, e o confruntare.

### Ce s-a schimbat, sub capotă

**Cele 385 de corpuri de rută au plecat din `main.py`** în **27 de module `core/uc_*.py`**, împreună
cu **58 de helperi** și **12 nume de modul** pe care le cereau. `main.py`: **11714 → 6546** de linii.
Fiecare rută a rămas la locul ei, cu decoratorul, semnătura și docstringul — FastAPI validează pe
semnătură, deci contractul de intrare e literal același —, iar corpul a devenit o delegare.

Cifra care a ținut faza deschisă două valuri, **`RUTE_CARE_DESCHID_SINGURE_TRANZACTIA`**, a mers
**385 → 73 → 17 → 5 → 0**. Cu ea, **toate cele patru criterii canonice ale lui P7 sunt satisfăcute**,
și faza se închide.

### Ce a făcut posibilă mutarea: un vocabular de refuz

`HTTPException` nu poate trăi în use-case — al doilea criteriu canonic o interzice. Dar decizia care
produce refuzul se ia **înăuntrul tranzacției**, adică exact în codul care pleacă. S-a scris deci
`core/erori.py`: clase care numesc **condiția** (*inexistent*, *fără drept*, *conflict*, *date
invalide*…), iar traducerea condiție → cod HTTP e **o singură hartă**, în stratul HTTP.

**Ce face traducerea sigură e o măsurătoare, nu o speranță:** `HTTPException` **nu e prinsă
nicăieri** — zero `except HTTPException` în tot repo-ul —, deci înlocuirea ei nu poate schimba niciun
flux de control. La fel s-a măsurat că niciun obiect de răspuns nu se construiește înăuntrul unei
tranzacții.

### Ce NU a trecut granița

Obiectele de protocol. Un `Response`/`FileResponse` se construiește tot în înveliș, din valorile pe
care use-case-ul le întoarce (**15 rute**); un `UploadFile` se citește în înveliș și se pasează ca
`bytes` + nume (**12 rute**); gărzile de ritm care se uită la IP-ul cererii rămân deasupra, pe primul
rând (**2 rute**). *Un use-case care vorbește HTTP n-ar fi un use-case.*

Și un al treilea fel de graniță, care n-a fost evident: `_TENANT_TEMPLATE` și `_STATIC_DIR` nu sunt
constante — se **aleg la pornire**, în stratul HTTP. Mutate ca valori, use-case-ul ar fi rămas cu
`None` iar scriitorul cu copia lui: o legătură ruptă pe tăcute, care s-ar fi văzut abia în producție.
S-au mutat invers, și așa e și corect ca strat: **HTTP-ul configurează, use-case-ul consumă.**

### Dovada că nu s-a schimbat contractul

`core/test_p7_uc.py` ia `main.py` **de la commitul dinainte de val** (`git show 43fd2197:main.py`) și
confruntă, **funcție cu funcție**, mulțimile de perechi `(cod HTTP, mesaj)` pe care le ridică —
mesajul comparat ca **arbore**, nu ca text, fiindcă dedentarea schimbă sursa fără să schimbe
valoarea. Trece cu **o singură abatere declarată**, cu motivul scris în fișier: un input-guard
telegrafic (`"suma invalida"`) care a intrat în domeniul regulii G5 odată cu mutarea și și-a primit
constrângerea în mesaj.

*Fișierul acela era citat de două ori în cod înainte să existe — `core/erori.py` și `main.py` îl
numeau ca dovadă a parității. Trimiterea la ceva inexistent se semnalează; aici s-a semnalat
construind lucrul citat.*

### Ce a ieșit la iveală mutând, și e clasa zilei

**Întreaga mașinărie de gărzi doc↔cod era ancorată pe presupunerea că logica aplicației stă în
`main.py`.** Mutând-o, ~40 de gărzi au devenit deodată oarbe sau roșii — nu fiindcă s-ar fi stricat
codul, ci fiindcă se uitau unde nu mai e nimic. Fiecare a fost re-ancorată prin accesorul comun
(`core/scan_sql_efectiv.py`), fără să-și piardă semantica.

**Patru lucruri s-au pierdut tăcut, și fiecare a fost prins de alt instrument:** două gărzi
anti-spam (`_rate_limit_*`) lăsate pe dinafară de mutator · comentariile de pe linia decoratorului,
printre care cinci marcaje `[api_intern_v1]` pe care un instrument le citește ca declarație · și un
RE-EXPORT (`main.pastila_firma`) scos de curățenia automată de importuri, care a lăsat șase firme cu
`control_fiscal` în eroare. Toate patru erau lucruri pe care codul le spunea, iar valul le-a rescris
din ceva care nu le conținea. Fiecare și-a primit garda.

**Iar două scanere aveau `main.py` ca punct orb DECLARAT** (`scan_data_curenta`, `scan_constante`):
valul le-a închis gaura, iar clichetele lor au urcat — nu fiindcă s-a scris cod nou, ci fiindcă
**instrumentul vede mai mult**. Fiecare urcare e scrisă cu lista exactă a cazurilor nou-expuse, și
fiecare caz se regăsește, la aceeași formă, în `git show HEAD:main.py`.


## 13.09.2026, partea a patra — **P7 · valul D4: 215 instrucțiuni mutate, și faza tot nu se închide**

Pentru un contabil, a patra oară azi: nu s-a schimbat nimic. Aceleași ecrane, aceleași declarații,
aceleași cifre. Ce s-a schimbat e unde stă SQL-ul — și ce știm despre cât mai avem de făcut.

### Ce s-a schimbat, sub capotă

Cele **37 de module mixte** — cele care făceau două straturi deodată, de la `core/d223.py` cu o
instrucțiune la `core/control_incrucisat.py` cu 45 și `main.py` cu 38 în helperii de modul — și-au
dat cele **215 instrucțiuni SQL** la **37 de `core/repo_*.py`**. `D4` **37 → 0**.

Mutarea a fost făcută de un instrument, `scripts/p7_d4_separa.py`, nu cu mâna. Motivul e o
măsurătoare, nu o preferință: 215 poziții în 13 forme diferite de loc, iar modul de eșec al unei
mutări manuale — parametri schimbați de ordine, un `fetchone` devenit `fetchall`, un `%s` pierdut —
**nu se vede la citire**. Instrumentul mută expresii, nu text; ce nu poate rezolva mecanic
raportează și lasă neatins. **Rest: 0 din 215.**

**Dovada că s-a mutat, nu s-a rescris:** amprenta SQL a întregului cod de producție — **1050
instrucțiuni distincte, 1307 în total** — e identică înainte și după.

### Partea care merită citită: cifra care arăta bine

După val: `D1`=0, `D2`=0, `D4`=0, **`P7_ACTION_REQUIRED`=0**. Citită singură, cifra spune că faza s-a
terminat. **Nu s-a.** Textul canonic cere patru straturi, iar despre use-case spune că *deține
tranzacția (P4) și orchestrează*. Măsurat: **385 din 421 de rute își deschid singure tranzacția**,
doar **7** deleagă către un modul `USE_CASE`, iar use-case-uri declarate sunt **4**.

*Un `ACTION_REQUIRED=0` care nu acoperă un criteriu canonic nu e o stare, e o lipsă de detector.* Am
închis golul cu un instrument și o gardă, nu cu o propoziție în predare: `scripts/p7_criterii.py`
măsoară toate patru criteriile, iar `core/test_p7_criterii.py` ține clichetul celor 385 **și
interzice planului să declare P7 închisă peste el**.

### Ce a mai scos valul, și toate trei sunt aceeași clasă

1. **O justificare ancorată prin vecinătate nu se mută cu codul.** Trei `ON CONFLICT DO UPDATE` au
   trecut în depozit, iar `# upsert-ok:` a rămas în modulul vechi. Prins de `test_upsert_motivat` la
   prima rulare — de instrument, nu de mine.
2. **Instrumentul traseelor a tăcut din nou**, a doua oară în două valuri: 12 adnotări deodată.
   Reparat cu **perechea nominală** modul ↔ `repo_<același nume>`.
3. **Citările în plan s-au mutat iar** — 8 ancore. De data asta reparate cu un instrument,
   `scripts/reancoreaza_plan.py`, care a greșit el însuși de două ori înainte să meargă: cerea
   unicitatea fragmentului pe tot planul, și lua reperul din fișierul deja editat.

### Cifre

`D4` **37 → 0** · `P7_RAW_ITEMS` **38 → 1** · `P7_ACTION_REQUIRED` **37 → 0** · straturi declarate
**167** (96 `FISCAL_ENGINE` · 65 `REPOSITORY` · 4 `USE_CASE` · 2 `HTTP`). Criteriul rămas:
**385/421**. Poarta: **5795 verzi / 0 roșii** · 12 sărite · 14 xfail ·
verificator **TOTAL 0**.

**P7 RĂMÂNE DESCHISĂ.** *Zero pe toate detectoarele nu e zero pe fază.*

---

## 20.09.2026 — Sesiunea B, F1 etapa 3: D1 (factură emisă) + bug NIR-GV prins și reparat

**F1 etapa 3, D1 (factură emisă) prin interfață.** `frontend_test/proba_f1_etapa3.py`: emitere factură
10 buc Marfa A × 100 = 1.000 + 21% 210 = 1.210, cu descărcare de gestiune (poarta F172 „pleacă marfa
acum?" → DA). Verificat în DB (tenant_049): factură total 1.210/TVA 210 client 410001005; linie 10×100@21%;
miscari_stoc ieșire 10 buc/500 (CMP 50); stoc rămas 90 buc/4.500. Cota vine prin AI (`potriveste_cota`,
round-trip ~3.4s) — proba veche eșuase pe un `python -c` în shell care NU încărca `api_keys.env`; serviciul
viu ÎL are, deci AI e disponibil (diagnostic corectat la sursă).

**Neconformitate prinsă (CICLUL): NIR-GV rupt.** La D2 (achiziție prin NIR) → 422 „Cota de TVA nu s-a
dat" pe orice NIR, deși fiecare linie avea cota. Cauză: `nir_gv` (core/stocuri.py) verifica R29 pe
`cota_tva_implicita` global, pe care apelantul real nu-l pasează (cota e per-linie).
- GENERALIZARE: clasa „motor multi-linie cu gardă pe cotă globală" — o singură instanță (`nir_gv`);
  celelalte ~24 raise-uri sunt funcții pe operațiune unică (cotă scalară), R29 corect, neatinse.
- CORECTARE: garda mutată în bucla per-linie (R29 păstrat, fără default tăcut).
- GARD: 3 probe în `core/test_stocuri.py` care apelează `nir_gv` EXACT ca producția (fără global);
  mutație = reintroducerea gărzii globale → 2 roșii. Blindspot vechi: testele apelau `nir_gv([...], 21)`.
- PROBĂ funcțională (schemă efemeră, ROLLBACK): `adauga_nir` → id=1, eroare=None, note 371=401 1000 /
  4426=401 210 / 371=378 1000 / 371=4428 420.

**D2 (factură primită) MĂSURAT prin calea reală SPV (decizie Costin: investighează+măsoară, nu repara).**
Factura primită vine DOAR prin SPV (nu există intrare manuală, corect RO e-Factură). Test: inserat
efactura_primite (simulare livrare SPV, XML UBL) + validat prin UI (#fac-primite → cont 371 → Validează).
Rezultat: factură directie='primita' 1210/210, note 371=401 1000 + 4426=401 210, **D300 sept.:
R9=1000/210 colectat (D1) + R22=1000/210 deductibil (D2) → TVA de plată = 0**. Deductibila SPV AJUNGE în D300.
**FINDING confirmat (NU reparat):** validarea SPV NU mișcă stocul CANTITATIV — cantitatea rămâne 90 buc,
deși 371-contabil urcă la 5.500 → **divergență 1.000** între cartea mare și fișa de magazie. SPV=D300+valoare;
cantitatea=separat prin NIR/CV, care ar DUBLA nota 371/4426. Nicio cale non-SPV nu alimentează D300 cu
deductibila de stoc. Decizia despre reconciliere/legare = a lui Costin (nedeschis campanie de reparație).

**D3 (extras bancar) prin interfață — ETAPA 3 ÎNCHISĂ.** `frontend_test/proba_f1_etapa3_banca.py` +
`extras_f1.csv`: import extras (2 linii) → contare. Note: 5121=4111 1.210 (încasare client 410001005) +
401=5121 1.210 (plată furnizor 420002008). Banca ÎNCHIDE soldurile: **4111 sold 0, 401 sold 0** (verificat
în DB). Etapa 3 = D1 emisă + D2 primită (SPV) + D3 bancă, toate prin interfață. Finding D2 (SPV↔stoc)
consemnat ca restanță în DECIZII (marcaj D406/bilanț). Decizie Costin: cascada continuă.
**Observație etapa 1 (de verificat la D406/bilanț):** Marfa A a migrat cu cont_stoc=302/cont_cheltuiala=601
(materiale), nu 371/607 (mărfuri) — CSV fără coloană cont_stoc → default 302; descărcarea D1 iese 601=302.

**Etapa 4 (salarizare) prin interfață.** `frontend_test/proba_f1_etapa4.py` + `asteptari_f1_etapa4.md`.
Statul de plată citește baza din `salariu_istoric` (baza_lipsa=False), NU din `salariati.salariu_brut=0`
(observația DS v2.33 — handled de `stat_plata_api.py:47-54`). Contare stat (sursa='salarii'): 641=421 13.900
(brut total), 421=4315 3.475 (CAS), 421=4316 1.390 (CASS), 421=444 688 (impozit reținut, rotunjit per salariat
215+269+204), 646=436 313 (CAM 2,25%). **CORECȚIE DE DATE DE TEST:** salariile inițiale (4.000) erau SUB salariul
minim 2026 = 4.325 (HG 146/2026, verificat la sursă `common.salariu_minim_luna`); gardul `ReconciliereD112` a
REFUZAT corect contarea ("date probabil corupte") — nu bug, test-data. Corectate la 4.500/5.000/4.400 în
`salariu_istoric` (tenant_049) + `salariati_f1.csv`. OBS: `salariati.cor` gol pe toți 3 — obligatoriu la D112.

**Etapa 5 (Contabilizare / validare jurnal) prin interfață.** `frontend_test/proba_f1_etapa5.py` +
`asteptari_f1_etapa5.md`. Toate cele 6 note ciornă (facturi 2, stocuri 1, banca 2, salarii 1) validate prin
`#fa-jurnal` (patru-ochi pe rol admin_firma, R55) → **6 validata, 0 ciornă**. Balanță echilibrată
**Σdebit=Σcredit=25.106** (solduri inițiale 17.000 + note validate); fișa 5121 populată din notele validate
(ciornele nu apăreau — „fișa se face din note VALIDATE"). Etapele 3-5 = fluxul date→jurnal complet și verificat.

**Etapele 6-8 (F1, prin interfață/generatoare).**
- **Etapa 6 (Sfârșit de lună):** luna septembrie ÎNCHISĂ prin `#fac-inchide` (`facturi/perioada/confirma`,
  confirmat=True). Pentru F1 (comerț micro): amortizare N/A (fără mijloace fixe), CMP descărcat per-factură.
- **Etapa 7 (Verificări interne):** Control fiscal (`#fa-control`) se randează; verdict = **roșu DOAR din
  declarații nedepuse** (28 lipsă, corect pre-etapa 8), **reconciliere_surse VERDE**, fără corupție de date.
- **Etapa 8 (Declarații — generare, parțial):** D300/D394/D112/D100 generate pe fluxul F1 și validate pe
  **DUK = toate 'valid'**. D300 TVA plată 0 (colectat 210/deductibil 210); D394 1 livrare+1 achiziție; D112
  impozit 688/CAS 3475/CASS 1390/CAM 313 (total control 5866); D100 micro 10 (1% × venit 1000, totalPlata_A
  20 = checksum R11b). Precondiții completate ca date de test: COR (522102/331302/432101). Fals-alarmă
  investigată și închisă: totalPlata_A=20 la D100 e checksum de structură (2×suma), nu bug (d100.py:181).
- **D406 (SAF-T) = STOP:** finding SPV↔stoc (achizițiile de stoc nu ajung la D300/nu mișcă cantitatea) —
  marcaj de revizitare obligatorie înainte de D406/bilanț (DECIZII). Decizie Costin înainte de a genera D406.

## 21.09.2026 — REPARAT finding SPV↔stoc (decizie Costin opțiunea 1); F1 reconciliat; etapa 8 completă (D406 valid)

**Campania A (cod + gard).** `factura_primita_valideaza` (uc_tenants) apelează acum
`stocuri_cv_api.intrare_din_factura` când factura primită e contată pe un cont de STOC (`CONTURI_FOND_EXACT`
371/301/302/303/213): o singură recepție = notă contabilă (din factură: 371=401, 4426=401 → D300) + cantitate
în fișa de magazie (legată prin `factura_id`). `intrare_din_factura` e cantitate-DOAR (nota vine din factură →
nu se dublează) + idempotentă + potrivește articolul pe denumire. Temei OMFP 1802/2014 (recepția = act unic;
concordanța GL↔fișă). Gard `core/test_reconciliere_factura_stoc.py` (5 probe; mutație = golirea intrării → 3
roșii; probă end-to-end pe schemă efemeră: validare cont 371 → miscari_stoc 20/1000 + note 371=401/4426=401).
Alternative respinse: D300 din jurnal (refactor uriaș), NIR creează primită (dublă notă) — vezi DECIZII.

**Campania B (curățare date F1).** F1 avea o inconsistență de cont: opening GL 371=5000, dar articolul migrat pe
302 (materiale) — CSV fără cont_stoc → default 302; descărcarea D1 ieșise 601=302. Curățat la 371 (comerț marfă):
articol 302→371/607, nota D1 601=302→607=371, cantitatea D2 intrată (20/1000 prin `intrare_din_factura`).
**RECONCILIAT: GL 371 = fișă 371 = 5.500, cantitate 110 buc.** Observat (de urmărit separat): defaultul de
migrare pt articole fără cont_stoc e 302, dar `cv_intrare` folosește 371 — inconsecvență de default.

**Etapa 8 COMPLETĂ.** D300/D394/D112/D100/**D406** toate DUK-valid pe F1 reconciliat (D406 SAF-T 96KB, valid).
Cascada reia: etapa 9 (depunere) → 10 (ieșiri externe) → 11 (transversal); apoi F2-F7.

## 21.09.2026 — Sesiunea B: F1 1-8 declarat suficient (9-11 front deschis); F2 pornit (etapele 1-2)

Decizie Costin: F1 (etapele 1-8) suficient acoperit; etapele 9-11 rămân front deschis în PREDARE_LANT.md
(depunerea reală la ANAF/SPV e [EXTERN] — blocant certificat mTLS). Trecere la **F2**, același regim (§2.2/etapă).

**F2 (SRL, TVA trimestrial, profit 16%, mijloc fix/amortizare, fără salariați) — etapele 1-2 prin interfață**
(`frontend_test/proba_f2_etape12.py` + `asteptari_f2.md` + `solduri_f2.csv` + `mijloace_f2.csv`). Cabinet A
(existent din F1) → login → adaugă F2 → vector **profit/TVA-trimestrial/fără-IC** → import solduri + mijloc fix.
Verificat în DB (tenant_050): Σdebit=Σcredit=**17.000**; mijloc fix MF-001 (utilaj 12.000, rezidual 10.000, 60
luni, liniar, 2131/2813, PIF 2025-01-15); vector (profit, TVA t, trimestrial); 0 salariați. Ce testează F2 unic
față de F1: D300 trimestrial, profit 16% (D100/D101), amortizare + mijloace fixe (etapa 6 nu mai e N/A), registru casă.

**F2 etapa 3 (documente primare) prin interfață.** `frontend_test/proba_f2_etapa3.py` + `asteptari_f2_etapa3.md`.
Factură serviciu emisă 5.000 + 21% = **6.050** (fără articol → fără poarta F172, corect pentru serviciu; cotă
21% via AI). Registru de casă (F2 unic): 2 operațiuni — ridicare bancă 1.000 (5311=581) + plată furnizor 500
(401=5311) → **sold casă 5311 = 500**. Verificat DB tenant_050.

**F2 etapele 4-8 (COMPLET 1-8).** 4 salarizare = **N/A** (0 salariați, sărit explicit). 5 contabilizare: 3 note
ciornă → validate. **6 amortizare (F2 unic):** MF-001 → nota 6811=2813 **200/lună** (12.000/60). **CORECȚIE DE DATE
DE TEST:** inițial amortizarea a ieșit **33,33** fiindcă pusesem rezidual=10.000 (confuzie); `amortizare_luna`
(d406_active.py:408) folosește `amortizabil = valoare − rezidual`, deci rezidual = valoarea reziduală FINALĂ
(salvage, standard CF art.28), nu „neamortizat". Corectat rezidual→0 (amortizabil 12.000 → 200/lună), opening
2813→2.200. Observație: eticheta „valoare rămasă (rezidual)" din import poate induce în eroare (de clarificat,
nu blochează — calculul e standard-corect). 7 control fiscal renderează. **8 declarații:** D300-T3 (TVA de plată
1.050), D394, D100-T3 (**cod 103 PROFIT**, impozit **768** = 16% × profit 4.800 = venit 5.000 − amortizare 200),
D406 — toate **DUK-valid**. D101 (profit anual) = la închiderea anului. **F2 acoperă: profit 16%, TVA trimestrial,
amortizare/mijloc fix, registru de casă.** Următor: F3 (neplătitor+art.317, micro 3%, D301/D390/taxare inversă).

## 21.09.2026 — Sesiunea B: F3 pornit (etapele 1-2); cotă micro corectată 3%→1% (2026)

Decizie Costin: F3 = **micro 1%** (nu 3%). Verificat la sursă (REGULA DE AUR): `common.py:650` `impozit_micro`=1%
unic din 2023; temeiul citat — **OUG 89/2025 (MO 1203/24.12.2025) art.I pct.5 a ABROGAT cota 3% (alin.1^1)** de
la 01.01.2026, pct.4 păstrează 1% unic; pe 2026 nu mai există split 1%/3% nici pragul 60.000 EUR (verificat
05.08.2026, validat Costin). Planul Sesiunea B scria „F3 micro 3%" (din legea veche) — obsolet pe 2026.

**F3 (SRL, neplătitor TVA + art.317, micro 1%, operațiuni IC, fără salariați) — etapele 1-2 prin interfață**
(`proba_f3_etape12.py` + `asteptari_f3.md` + `solduri_f3.csv`). Tenant tenant_051, Cabinet A. Vector: micro /
platitor_tva=false / operatiuni_ic=true / inreg_art317=true. Sold Σdebit=Σcredit=5.000 (simplu — F3 nu are
stoc/mijloace fixe). Set declarații: **D301** (achiziții IC + servicii UE, la neplătitor art.317), **D390**
(recapitulativ), D100 (micro), D406. NU D300 (neplătitor), NU D112 (0 salariați), NU D394 (plătitori). Ce
testează F3 unic: taxare inversă IC/servicii UE → D301/D390. Următor: etapa 3 (documente IC).

## 21.09.2026 — ÎNCHIDERE ZI (efect pentru contabil)

Ziua a fost în cea mai mare parte **testare pe flux (Sesiunea B)** — firmele de test F1/F2/F3 (tenant_049/050/051),
care NU ating datele niciunui contabil real. DAR ziua **A schimbat două lucruri vizibile pentru un contabil real**,
prin cele două reparații de cod publicate (four-way, procesul viu le rulează):

1. **Salvarea unui NIR funcționează din nou.** Înainte, orice notă de intrare-recepție pica la salvare cu
   422 „Cota de TVA nu s-a dat", deși cota era completată pe fiecare linie (bug NIR-GV — garda R29 verifica o cotă
   globală pe care apelantul n-o pasa). Acum se salvează normal. (commit 3dbeb987→817d0c70, gard test_stocuri.py.)

2. **Validarea unei facturi PRIMITE de marfă mișcă acum și fișa de magazie.** Înainte, validarea unei facturi de
   marfă (cont de stoc) urca soldul contabil (371) dar NU mișca cantitatea din gestiune → divergență tăcută între
   cartea mare și fișa de magazie (contabilul trebuia să facă manual o intrare separată, iar dacă uita, D406/bilanțul
   ieșeau incoerente). Acum, o singură validare face ambele: nota contabilă (din factură) + cantitatea în fișă
   (legată de factură, fără dublă notă). (finding SPV↔stoc reparat, decizie Costin opțiunea 1, commit 49bb7ce7,
   gard core/test_reconciliere_factura_stoc.py; temei OMFP 1802/2014.)

Restul zilei (F1/F2/F3 etape, generări de declarații DUK-valid, corecții de date de test) = validare internă a
fluxului, **fără efect asupra datelor reale**. Detaliile per etapă/reparație sunt în intrările de mai sus din 21.09.

## 21.09.2026 — Poarta de producție ghiduri (pasul 2), fir paralel Sesiunii B

Comandă Costin (lista producție ghiduri, pasul 2): import `index_titluri_ghid.csv` (8.713 titluri indexate) ca
listă de bază + poarta de verificare pre-publicare cu două controale obligatorii care blochează publicarea
oricărui ghid nou. Fir PARALEL — agenda (`urmator_cluster`) rămâne pe F3. Detaliul deciziilor: DECIZII (61); gardul:
GARZI (21.09, poartă conținut public).

**Livrat.** `core/ghid_titluri.py` (reader canonic al listei de bază); `core/ghid_poarta.py` (extractor citări cu
AMBELE forme reale — slash `OUG 89/2025` și dată `OUG nr. 89 din 23 decembrie 2025`; index corpus prin
`scan_provenienta`, alias CF/CPF = Legea 227/2015 și Legea 207/2015, toleranță `hg714`/`hg_714`; verificare F-ID
LIVE + «Sursa cod» pe disc + back-link `ghid_slug`; CLI care blochează cu exit≠0); `core/test_ghid_poarta.py`
(calibrare + ratchet legacy, mutații probate); `ghid/_legacy_pre_poarta.txt` (baseline 202, clichet — grandfathering).

**Defect prins la self-review și reparat pe clasă (CICLUL DE NECONFORMITATE):** forma „OUG nr. 89 din 23 decembrie
2025" era ratată la extracție (ziua „23" bloca ajungerea la an) → citări scrise doar așa nu erau verificate.
Reparat pe ambele forme, apărat cu `test_CALIBRARE_forma_cu_data_e_extrasa`.

**Măsurat pe corpusul real:** 122 identități de act în corpus; 46/202 ghiduri legacy citează acte încă neaduse
în corpus (grandfathered, declarat). Efect vizibil pentru contabil: NICIUNUL (tooling intern; niciun ghid nou
produs încă). Raport §2.2 + oprire înainte de redactarea propriu-zisă (pasul 3), conform comenzii.

## 21.09.2026 — Reparație extractor citări ghiduri (urmare a listei de acte lipsă)

La comanda „extrage lista actelor lipsă din cele 46 ghiduri grandfathered", extracția a scos ani
imposibili (Ordin 417/1204, 1826/2372, 1337/1268) și o misclasificare (OMFP 2861/2009 → „Legea") —
fals-pozitivi în extractorul livrat mai devreme azi. OPRIRE înainte de livrarea listei (REGULA DE AUR:
nu se livrează o listă știut-greșită) + reparație pe clasă (CICLUL DE NECONFORMITATE):

- ordin comun `nr1/nr2` → gard de plauzibilitate an (1900–2035); un an imposibil nu devine act;
- cuvânt comun „lege" prinzând actul următor peste paragraf → TIP case-sensitive + punte tempered token
  `(?!TIP)` (fără `re.I`, care strica clasa negată; fără forma-cuvânt „Lege");
- fals-negativ „Hotărârea Guvernului nr. 1/2016" (calificativ Title-case) → puntea îl acceptă fără a
  traversa alt act.

5 teste `test_CALIBRARE_*` noi (fiecare pe cazul real). Numere corectate: **44/202 ghiduri** citează
**47 acte distincte** neaduse în corpus (SUPERSEDĂ 46/51 din intrarea anterioară — DECIZII 62). Suita
verde, verificator 0.

## 21.09.2026 — Import corpus FISCAL urcat în anaf_surse (decizie Costin: TOT)

Costin a urcat `import_fiscalos/active` (71 poziții, OPIS 15.09, content-addressed + proveniență bogată:
official_source, accessed_at, source_SHA256, V4_EVIDENCE). Decizie: import TOT, bytes oficiali → anaf_surse.

Executat cu `scripts/import_corpus_fiscal.py` (idempotent, fail-closed): 48 acte importate (material principal
BASE/CUTOFF_VERSION → anaf_surse/<tip>_<nr>_<an>.html + .sha256 + PROVENIENTA ADUS cu motiv structurat),
17 deja prezente (skip), 6 ordine comune nr1/nr2/an raportate (identitate mecanic nestabilibilă). Detaliu:
DECIZII 63.

Efect: corpus_acte 122→170 identități; acte lipsă (grandfathering) 47→41, ghiduri afectate 44→42; cele 6
acte suprapuse acoperite. Recalibrat test_identitate_acte: acoperire 52%→60% (188/311), clichet fara_titlu
neschimbat (123 — toate cele 48 au titlu). Garduri corpus/identitate verzi, verificator 0.

## 21.09.2026 — Pasul 3 pornit: primul ghid produs sub poartă

După aterizarea four-way a importului (8a5c01d1), am trecut la redactare (pasul 3, autorizat de Costin).
Primul ghid: `ghid/curs-valutar-factura-valuta.md` — „Ce curs valutar folosești pentru o factură în valută".
Temei verificat VERBATIM la sursă (nu din memorie): CF art. 290 alin. (2) (cf_2015 în corpus) + Normele
HG 1/2016 pct. 35 alin. (1) (hg_1_2016 în corpus). Funcționalitate legată: F025 „Curs valutar BNR"
(core/curs_bnr.py, LIVE — docstring-ul codului confirmă aceeași regulă), cu back-link F025.ghid_slug.

Frontmatter contract (DECIZII 61): `poarta: v1` + `functionalitate: F025`. Poartă VERDE (2a citări în
corpus + 2b F-ID LIVE+sursă+back-link), servit (test_ghiduri_servite), verificator 0. Am evitat citarea
art. 319 (TVA în lei pe factură) fiindcă textul lui nu s-a putut pin verbatim din corpus (apărea doar în
cuprins) — REGULA DE AUR: nu se citează text neverificat.

Oprire pentru DECIZIE DE PRODUS: volumul și prioritatea redactării (care din ~8.500 titluri neproduse,
câte per rundă) — alegere de scop care schimbă ce ajunge la public, deci a lui Costin (§2.3 pct.2).

## 01.10.2026 — Pachet FiscalOS §1–§3 comis (reluare după întrerupere)

Sesiunea anterioară s-a închis la repornirea terminalului cu §1 (corpus) și §3 (4 defecte) aplicate dar necomise
și §2 pe jumătate. Am verificat ce era făcut (fără să refac): cele 54 de acte înlocuite au SHA256 consistent și 53
sunt byte-identice cu formele oficiale din manifestul FiscalOS; OUG 24/2026 adusă separat; patru rânduri din COTE
deja atinse.

§2 terminat. În loc să mut constantele în registrul COTE (ar fi schimbat tipul la fiecare consumator), le-am dat
temeiul ca OBIECT prin `common.ancoreaza(...)` — valoarea rămâne aceeași, iar scanerele (`scan_constante`,
`scan_citate`, inventarul FiscalOS) le văd ca sursate. Toate cele 18 temeiuri aprobate + încă două din aceeași
clasă (plafonul de sold 500.000 la cash&carry și pragul Brent de 70 USD, respins în pachet doar pentru că OUG
24/2026 era ilizibilă — §1 a rezolvat-o). Fiecare citat a fost căutat verbatim în forma nouă; fiecare `data_in`
citit din nota de modificare a actului.

Pe drum, o clasă nouă: temeiul declarat pe un articol, citatul din altul. Trei apariții (dividendele 2026 și
2023 pe art.97 cu text din art.43; impozitul pe salarii pe art.78 cu text din art.64), plus un temei curent pe un
alineat abrogat (cota redusă de 5% → 11% pe art.291 alin.3, abrogat). Toate reparate, iar clasa are gard pe toate
temeiurile din core. Și nota colaterală a arhitectului: la o firmă cash&carry mesajul de încasare cita lit.a) deși
plafonul aplicat era lit.b) — acum are cod propriu.

Verificând §1 am găsit că FiscalOS adusese azi o consolidare mai nouă a HG 1045/2018 (30.09.2026) decât cea din
corpus: reproduce ordinele din MO 830/30.09.2026 — tichet de masă 45 lei (iConta are deja 45) și **tichete de
creșă 770 lei de la 1 octombrie**, plus tot istoricul indexărilor din 2024. iConta plafonează creșa la 450 (decizia
din 04.08, condiționată de obținerea ordinelor). Deschis ca fir separat, commitul următor.

## 01.10.2026 — Tichetele de creșă: plafonul urmează ordinele de indexare (770 lei din octombrie)

Neconformitatea găsită la verificarea §1, tratată imediat. Forma oficială a HG 1045/2018 din 30.09.2026 a intrat în
corpus (cea din 15.09 arhivată), iar plafonul tichetelor de creșă nu mai e blocat la 450: urmează ferestrele
ordinelor de indexare reproduse verbatim în ea — 640, 660, 670, 710, 740 și, de azi, 770 lei pe copil. Plafonul se
ia pe luna beneficiului (înainte se lua pe ziua de azi). Ecranul statului de plată nu mai afirmă „indexare
neconfirmată — blocată". Dinainte de aprilie 2024 și după martie 2027 rămâne baza legală de 450, cu motivul spus.

## 02.10.2026 — D212 Etapa 2: venitul din registrul PFA ajunge în Declarația unică, validat de ANAF local

Am citit întâi tot ce decide forma: validatorul oficial (în pachetul în vigoare, capitolul de venit se verifică doar
structural, iar categoriile acceptate sunt coduri de tip 1016), generatorul PDF oficial (care spune că 1016 înseamnă
„activități independente" — informația lipsea din tot corpusul și din validator) și instrucțiunile de completare,
rând cu rând. Două surprize: impozitul NU se scrie în acest capitol când există venit net (se calculează în altă
secțiune — Etapa 4), iar regula de control R4 cere mereu suma cifrelor CNP, nu suma de plată cum credea emitter-ul —
o declarație cu obligații ar fi fost respinsă; reparat. Pe ecranul D212, contabilul bifează „Include venitul din
registrul RIP", poate declara pierderea reportată (compensată în limita a 70%, Codul fiscal art.118) și CAEN-ul; pe
firma F4, XML-ul iese cu venitul real și trece validatorul. Pe drum: bifele cu etichete lungi se striveau pe telefon
— reparat global.

## 02.10.2026 — Ziua, pentru un contabil

Ce s-a schimbat azi în aplicația pe care o folosește un contabil (amândouă au ajuns în producție în noaptea de 1 spre 2
octombrie):

- **Tichetele de creșă pot fi acordate la valoarea legală de azi: 770 lei pe lună pentru fiecare copil.** Până acum
  aplicația oprea orice sumă peste 450 lei și spunea că indexarea „nu e confirmată". Acum plafonul urmează ordinele de
  indexare publicate în Monitorul Oficial (640, 660, 670, 710, 740 și, din octombrie 2026, 770 lei) și se verifică pe
  luna pentru care se acordă tichetul, nu pe ziua în care îl introduci. Impozitul de 10% se calculează pe suma întreagă,
  fără CASS, ca înainte.
- **Declarația unică (D212) pentru un PFA în sistem real se poate completa cu venitul din registrul de încasări și
  plăți.** Pe ecranul D212 bifezi „Include venitul din registrul RIP", treci, dacă e cazul, pierderea reportată din anii
  trecuți și codul CAEN, iar declarația iese cu venitul brut, cheltuielile deductibile și venitul net completate și
  trece validatorul oficial ANAF. Pierderea reportată se scade în limita a 70% din venitul net, cum cere Codul fiscal.
  **Ce nu face încă:** impozitul și contribuțiile (CAS/CASS) nu sunt încă scrise în declarație — le completezi tu
  până la etapa următoare; nici venitul pe normă, nici asocierile.

Restul zilei (verificări, gărzi, registre) nu schimbă nimic din ce vede sau depune un contabil.

## 02.10.2026 — Lot 19: două decizii consemnate, corpusul de legi readus întreg, cinci defecte fiscale reparate

**Deciziile lui Costin, scrise.** Bifele rămân de 16px (ținta de clic e eticheta — acum garantată ≥ 24px prin regula
globală și verificator); cele patru constante care dublează chei din registrul de cote intră în registru doar când modulul
lor e atins oricum.

**Corpusul de legi.** La înlocuirea cu formele oficiale de ieri, două ordine ANAF (cazierul fiscal și e-Popriri) rămăseseră
doar cu procedura din anexă — articolele ordinelor lipseau. Comparând pe articol toate cele 82 de forme înlocuite, alte
pierderi reale nu există (doar note editoriale ale portalului, numite una câte una). Dar căutând clasa, am găsit 41 de acte
cărora le lipseau documente publicate separat pe portal — inclusiv anexa cu formularul și instrucțiunile D212 — plus
facsimilele formularelor: 130 de documente aduse, cu proveniența și amprenta lor.

**Ce se schimbă pentru un contabil:**
- **D216 pe 2026** se calculează cu 0,9% (era 0,3% — validatorul ANAF respingea declarația).
- **D300 include TVA-ul din rapoartele Z** (casa de marcat, import sau tastat), pe cote, la rândurile 9 și 10. Până azi
  decontul vedea doar facturile, iar TVA-ul încasat pe bon rămânea în 4427 și lipsea din declarație.
- **Statul de plată și D112 calculează brutul pe zilele din contract**: angajare sau plecare în cursul lunii, concediu
  fără plată sau suspendare (buton nou „Suspendare / CFP" pe salariat) și mărire de salariu în cursul lunii. În D112,
  salariul din contract și venitul realizat stau acum în câmpurile lor, iar orele de CFP în câmpul de ore suspendate.
- **O firmă neplătitoare de TVA nu mai primește 21% propus pe factură** și nu poate emite o factură cu TVA; PDF-ul ei nu
  mai tipărește „TVA 0%", ci mențiunea de scutire (art. 310 Cod fiscal).
- **D205 împarte dividendele după asociații de la data distribuirii.** La importul asociaților se poate trece data
  cesiunii: structura veche se păstrează pentru dividendele distribuite înainte.

**Ce rămâne de decis:** D394 nu preia încă rapoartele Z în secțiunea de încasări prin casa de marcat (cere date pe care
ruta tastată nu le culege).

## 02.10.2026 — D212 Etapa 3: venitul pe normă de venit intră în Declarația unică

**Ce se schimbă pentru un contabil:**
- **Pe formularul D212 apare lista „Venit pe normă de venit".** Pentru fiecare activitate (fiecare loc) se trec norma
  publicată de direcția regională, norma ajustată dacă e cazul, datele de început/încetare și zilele de întrerupere sau
  de scutire. Aplicația calculează venitul net (proporțional pe 365 de zile când activitatea n-a durat tot anul), venitul
  impozabil și impozitul de 10%, și le pune în subsecțiunea I.1.2 a declarației — câte o secțiune pe activitate.
  Proba pe firma PFA de test: două activități → impozit pe normă 4078 lei, declarație validă la ANAF local; înainte,
  aceleași date dispăreau din declarație fără niciun semn.
- **Venitul agricol pe normă** nu se poate încă genera: validatorul ANAF instalat e al formularului pentru veniturile
  2024 și nu are câmpurile agricole. Aplicația refuză cu explicația, nu îl pune în altă parte.
- **Explicațiile a zece declarații nu mai spun că declarația lipsește din aplicație.** D114, D200, D201, D204, D212, D216,
  D318, D398, D600 și D603 sunt în lista de declarații a firmei de la sfârșitul lui septembrie, dar textul de ajutor încă
  spunea „încă nu o produci din interfață”. Acum arată drumul real până la ea.

**Pe dedesubt.** Două gărzi noi de clasă: orice câmp pe care ecranul Declarații îl trimite trebuie să fie citit de
generatorul declarației (altfel o dată introdusă s-ar putea pierde tăcut, cu declarația tot „validă"); și graful care
leagă testele de valorile fiscale citește acum importurile corect — trei verificări D394 păreau, fals, afectate de
schimbarea cotei D216 de azi. La poartă a mai ieșit o slăbiciune de același fel: verificarea „valoarea fiscală apare în textul legii” sărea
peste constantele D212 când rula singură — acum își încarcă singură toate modulele.

## 02.10.2026 — D394 preia încasările prin casa de marcat din rapoartele Z

**Ce se schimbă pentru un contabil:**
- **Ecranul Raport Z are câmpul „Nr. bonuri fiscale”** (e tipărit pe raport). Fără el raportul nu se salvează; la importul
  fișierului AMEF numărul se ia din fișier.
- **D394 completează secțiunea încasărilor prin casa de marcat (Î1)**, câte o linie pe lună: câte case de marcat s-au
  folosit, câte bonuri, totalul încasărilor și baza/TVA pe cote. Până azi secțiunea rămânea goală, deși încasările erau în
  evidență. Proba pe firma de test: două case, 255 de bonuri, 1795 lei — declarație validă la ANAF local.
- **Un raport Z fără casă sau bonuri oprește D394 cu numele raportului** — nu se declară zero. Azi nu există niciunul
  (în producție nu era înregistrat niciun raport Z, iar ambele căi le scriu de acum înainte).

## 02.10.2026 — CASS pentru PFA cu venit mic: aplicația spunea că nu se datorează

**Ce se schimbă pentru un contabil:**
- **Fișa D212 (ecranele Încasări/plăți și D212) nu mai spune „neobligatoriu — sub 6 salarii minime” la CASS.** Pentru un
  PFA cu venit net pozitiv sub 6 salarii minime (24.300 lei), CASS se calculează la baza minimă — 2.430 lei pe an —, iar
  fișa arată separat diferența până la baza minimă și suma care rămâne dacă persoana are salarii, pensii sau alte venituri
  cu CASS de cel puțin 6 salarii minime (atunci se datorează doar 10% din venitul real). Exemplu: venit net 20.000 lei —
  înainte CASS 0 și impozit 2.000; acum CASS 2.430 și impozit 1.800 (diferența de 430 lei nu se scade din impozit).
- **Cinci ghiduri publicate despre CASS au fost corectate** — trei spuneau că sub 6 salarii minime plata e opțională.

Găsit citind instrucțiunile Declarației unice pentru etapa următoare; un ghid consemna defectul din septembrie, fără să fi
fost reparat.

## 02.10.2026 — D212 Etapa 4: Declarația unică include acum contribuțiile și impozitul

**Ce se schimbă pentru un contabil:**
- **D212 generată din aplicație conține CAS, CASS, impozitul și suma de plată.** Până azi declarația purta veniturile
  (din registrul PFA și de pe normă), dar secțiunile cu contribuțiile, impozitul în sistem real și sumarul obligațiilor
  lipseau — iar validatorul ANAF o accepta așa. Acum se calculează din aceleași venituri, pe rândurile formularului: CAS pe
  treptele de 12/24 salarii minime, CASS pe venitul cumulat (cu baza minimă de 6 salarii minime), contribuțiile
  deductibile împărțite pe ponderea venitului din sistem real, impozitul de 10% și totalul de plată. Proba pe firma PFA de
  test (venit net 70.000 lei din registru + o normă de 30.000): CAS 24.300, CASS 10.000, impozit 7.599, de plată 41.899
  lei, declarație validă la ANAF local.
- **Pe formularul D212 se poate alege excepția de la baza minimă CASS** (salarii, pensii sau alte venituri cu CASS de cel
  puțin 6 salarii minime).
- **Opțiunea de a plăti CAS sub 12 salarii minime nu se poate încă declara din aplicație**: formularul validatorului ANAF
  instalat nu are căsuța ei. Aplicația refuză cu explicația.

## 02.10.2026 — Factura cerută de client pentru un bon fiscal nu mai dublează vânzarea

**Ce se schimbă pentru un contabil:**
- **Pe ecranul de emitere apar câmpurile „Emisă pe baza bonului fiscal: nr. bon / data”.** Factura primește mențiunea
  „conform bon fiscal nr./data”, iar vânzarea se numără o singură dată — rămâne în raportul Z: factura nu mai intră în D300,
  nu mai primește notă de vânzare, nu mai descarcă stocul; în D394 apare la client, iar suma ei se scade din încasările prin
  casa de marcat ale lunii. Proba pe firma de test: o factură de 121 lei dintr-un bon deja în Z — înainte D300 avea 2.100 / 441
  și evidența 441 lei TVA colectat; acum 2.000 / 420, D394 cu încasările prin casă 1.089 în loc de 1.210, ambele declarații
  valide la ANAF local.

## 02.10.2026 — D212 Etapa 5: Declarația unică primește și celelalte venituri ale persoanei

**Ce se schimbă pentru un contabil:**
- **Pe formularul D212 apare lista „Alte venituri ale persoanei”**: drepturi de autor (pe cote forfetare sau în sistem real),
  chirii, închirierea camerelor în scop turistic, activități agricole/silvicultură/piscicultură în sistem real, câștiguri din
  investiții și venituri din alte surse — câte o sursă pe rând. Se arată doar câmpurile categoriei alese; cheltuielile
  forfetare (40% / 20%), compensarea pierderilor (70%) și impozitul de 10% le calculează aplicația. Până azi asemenea venituri
  nu aveau unde intra: declarația ieșea fără ele, iar validatorul ANAF o accepta.
- **CASS pe aceste venituri se calculează pe trepte** (6, 12 sau 24 salarii minime), cu dividendele, dobânzile și venitul din
  asocieri cu persoane juridice scrise lângă excepția CASS. Dacă CASS pe aceste venituri se datorează, diferența până la 6
  salarii minime la activitatea independentă nu se mai cere. **CAS ține cont și de drepturile de autor.**
- **Zilele de scutire pentru handicap** se pot trece la venitul din registrul RIP și la drepturile de autor/agricole.
- Proba pe firma PFA de test (veniturile 2025): drepturi de autor 30.000, o chirie de 24.000, agricol 50.000/30.000 cu
  pierdere reportată, câștig din investiții 8.000, alte surse 3.000 și dividende nete 10.000 — impozit 5.760, CASS 4.860
  (treapta 12 salarii minime pe 78.200 lei), de plată 10.620, declarație validă la ANAF local.
- Regulile pe categorii sunt cele pentru **veniturile 2025**; pentru 2026 legea s-a schimbat (Legea 239/2025), iar ANAF n-a
  publicat formularul — aplicația refuză cu explicația.

## 03.10.2026 — D212 Etapa 5c-1: veniturile din străinătate în Declarația unică

**Ce se schimbă pentru un contabil:**
- **Pe formularul D212 apare lista „Venituri din străinătate”**: câte o țară și o sursă — activități independente, drepturi de
  autor, chirii, agricole, titluri, dobânzi, dividende, alte venituri, lichidare, salarii plătite din România pentru munca din
  străinătate. Se alege metoda de evitare a dublei impuneri; impozitul în România se calculează cu cota categoriei, iar
  impozitul plătit acolo se scade cel mult până la impozitul român (metoda creditului) sau impozitul e zero (metoda scutirii).
- **Veniturile din străinătate intră în CAS și CASS**, afară de cazul în care persoana e asigurată în alt stat — atunci se bifează
  „Fără CAS/CASS în România”.
- Proba pe firma PFA de test (veniturile 2025): Germania 80.000/20.000 cu 4.000 plătit acolo, drepturi de autor din Austria
  20.000 cu 2.000 plătit, chirie în Franța pe metoda scutirii, dividende din SUA 10.000 — de plată în România 2.000 impozit,
  CAS 12.150, CASS 8.430, total 22.580, declarație validă la ANAF local. Înainte, lista nu exista și declarația ieșea fără
  aceste venituri.
- Premiile, jocurile de noroc, pensiile, transferul proprietăților și moștenirea din străinătate nu sunt încă în listă (pasul următor).

## 03.10.2026 — D212 Etapa 5c-2a: premii, jocuri de noroc, vânzări de proprietăți și moșteniri din străinătate

**Ce se schimbă pentru un contabil:**
- **Lista „Venituri din străinătate” primește premiile, jocurile de noroc, transferul proprietăților imobiliare și moștenirea.**
  La premii suma neimpozabilă de 600 lei se scade singură (câte un rând pe premiu); la jocurile de noroc se alege felul jocului
  și data plății — baremul se schimbă de la 1 august 2025, iar la cazinouri, poker, slot-machine și lozuri primii 66.750 lei din
  fiecare plată nu se impozitează; vânzarea unei proprietăți: 3% (deținută cel mult 3 ani) sau 1%; moștenirea: 1%.
- Proba pe firma PFA de test: un premiu de 5.000 lei, un câștig la cazinou de 100.000 lei în martie (5.000 plătiți acolo), un alt
  câștig de 20.000 lei în septembrie, o vânzare de 300.000 lei sub 3 ani (6.000 plătiți acolo) și o moștenire de 500.000 lei —
  impozit de plată în România 19.140 lei, fără CASS, declarație validă la ANAF local.

## 03.10.2026 — D212 Etapa 5c-2b: pensii și remunerații de administrator din străinătate

**Ce se schimbă pentru un contabil:**
- **Lista „Venituri din străinătate” primește pensiile și remunerațiile de administrator, membru în consiliul de administrație,
  cenzor și similare.** La pensii se scriu brutul anului și numărul lunilor — suma neimpozabilă de 3.000 lei pe lună se scade
  singură. La remunerații, CAS (25%) și CASS (10%) datorate în România se calculează pe câștigul brut, intră în secțiunea lor și
  în totalul de plată, iar impozitul se calculează după scăderea lor; pentru un asigurat în alt stat se scriu contribuțiile
  plătite acolo.
- **CASS pe pensia din străinătate datorată în România (de la august 2025) nu se poate încă declara din aplicație**: formularul
  ANAF instalat n-are secțiunea; aplicația refuză cu explicația.
- Proba pe firma PFA de test: o pensie din Germania de 60.000 lei (12 luni, 1.000 plătiți acolo), o remunerație din Austria de
  40.000 lei și una din Franța de 20.000 lei pentru un asigurat acolo — impozit 5.600, CAS 10.000, CASS 4.000, total 19.600 lei,
  declarație validă la ANAF local.

## 03.10.2026 — D212 etapa finală: ghidurile spun ce face aplicația azi; a doua activitate independentă se poate declara

**Ce se schimbă pentru un contabil:**
- **Ghidurile despre Declarația unică nu mai spun că D212 „se completează manual”, „produce doar identificarea” sau că
  aplicația „nu calculează” norma, CASS pe chirii/dividende ori creditul fiscal din străinătate** — 65 de ghiduri corectate,
  cu limitele reale păstrate (fără depunere în SPV, fără evidența pierderilor pe ani, fără opțiunea CAS sub 12 salarii minime,
  fără agricolul pe normă și fără CASS pe pensiile din străinătate până la formularul ANAF nou).
- **În lista „Alte venituri” a formularului D212 apare „Activități independente (sistem real, din afara registrului)”**: o a
  doua activitate ținută în altă firmă din aplicație, sau perioada unei forme de exercitare anterioare din același an, se
  adaugă cu venitul brut și cheltuielile ei, iar CAS și CASS se calculează pe venitul total, cum cere legea.

## 03.10.2026 — Agenda nu mai propune pași deja făcuți

**Ce se schimbă (intern, fără efect pe ecranele contabilului):** agenda campaniei arăta ca „pas următor” o etapă a firmei de
test F3 terminată pe 21.09 — citea un rând vechi de stare. Cititorul se uită acum doar la firele în lucru și sare peste cele
închise sau blocate; șapte fire livrate au primit închiderea, cu commitul care o dovedește. Pasul următor real: refacerea
generatorului D112 pe contractul comun al declarațiilor (calculul separat de XML). Tot azi, o notă internă despre D394 spunea
că încasările prin casa de marcat (Î1) nu se declară — se declară de ieri; corectată.
- (completare, aceeași zi) Agenda citește și „cere greenlight” ca blocaj; după D212 nu mai rămâne niciun pas fără o decizie a lui
  Costin — cinci decizii sunt listate în predare.

## 03.10.2026 — Lotul 19 publicat: 433 de ghiduri noi, 20 de ghiduri corectate, opt defecte reparate

**Ce se schimbă pentru contabil:**
- **Import mijloace fixe:** valoarea rămasă din registrul vechi nu mai devine „valoare reziduală”. Un activ preluat la
  jumătatea duratei se amortiza doar pe jumătate, iar unul fără coloana de rezidual nu se amortiza deloc.
- **Termenele lunii noiembrie:** apar pe 21 decembrie, nu pe 28 (calendar, semafor, lista de termene, prognoza de
  trezorerie).
- **D208 (notari):** se alege pe lună, nu pe semestru.
- **Dividende interimare:** regularizarea nu mai înregistrează o încasare care n-a avut loc. Restituirea de la asociat
  (netul) și impozitul recuperat de la buget se înregistrează la încasare. Dividendul interimar se poate alege acum și din
  ecran.
- **D300:** ajustarea pentru bunurile de capital (art. 305) intră la rândul 34. Rândurile manuale nu mai pot purta o
  coloană pe care formularul ANAF n-o are.
- **Mijloace fixe:** aparatura de cercetare-dezvoltare marcată „C&D” se poate amortiza accelerat din orice cont.
- **Facturi:** factura unei societăți tipărește capitalul social (la SA și SCA, subscris și vărsat). Dacă în Date firmă
  lipsesc forma juridică sau capitalul, factura nu se emite până se completează. Ecranul spune ce lipsește și trimite la
  Date firmă, iar factura rămâne cum a fost scrisă. Firmele de test din portofoliu trebuie completate.
- **Operațiuni speciale:** Garanția și Restanța la credite, Reluarea subvenției și Calculul scutirii ONG puteau fi trimise
  din ecran, dar ruta le refuza mereu. Leasingul (rate), Minusul la inventar, Decontul de deplasare, Autofactura SGR și
  Vânzarea activului la lichidare n-aveau câmp de cotă. Acum funcționează toate.
- **Răspunsurile „Nu” din formulare erau citite ca „Da”:** imputabil, furnizor plătitor de TVA, agricultor în registru.
  Taxarea inversă se aplica și cu un furnizor neplătitor.
- **Ghiduri:** 433 de ghiduri noi publicate. Corectate 20 de ghiduri existente, între care: numerotarea veche din Codul
  muncii, sporul de noapte de 25%, termenul de noiembrie al decontului, cazierul fiscal, punctul de lucru cu salariați,
  scutirea pentru mici întreprinderi din alt stat UE și situațiile financiare (31 mai).

## 03.10.2026 — D394 Î2: încasările din activitățile scutite de casa de marcat intră în D394 și în D300

**Ce se schimbă pentru contabil:**
- **Date firmă → Casa de marcat:** o firmă se poate marca „exceptată de la casa de marcat”, cu activitatea din OUG 28/1999
  art. 2 (18 activități, din lista în vigoare; lit. p e abrogată). Lista activităților e în ordonanță, nu în HG 479/2003,
  cum se presupunea.
- **Casă → „+ Chitanță fără factură”** (doar la firma exceptată): se emite chitanța unei vânzări fără factură, cu cota de TVA
  (0% dacă activitatea e scutită). Nota iese 5311 = venit + 5311 = 4427, nu 5311 = 4111.
- **D394:** apare secțiunea **Î2** pe fiecare lună (total, bază și TVA pe cote, fără număr de case și bonuri). Dacă o
  chitanță fără factură n-are cotă, D394 nu se generează și spune care chitanță e. Cota se stabilește din Casă
  («Stabilește cota»), cât timp nota e ciornă. O încasare din casă fără chitanță (alta decât ridicarea de la bancă) apare
  ca avertisment: nu blochează, dar se vede.
- **D300:** TVA-ul acestor vânzări intră la rândurile 9/10. Până acum vânzarea fără factură a unei firme scutite de casa de
  marcat nu ajungea în nicio declarație.
- **Firmele neexceptate:** chitanța fără factură rămâne încasare de creanță (5311=4111), ca până acum. O chitanță de
  vânzare (cu cotă) e refuzată: vânzarea fără factură se face cu bon fiscal.
- **Totalul lunii din D394 (Î1 și Î2)** e acum suma rubricilor rotunjite. Validatorul ANAF dădea o atenționare falsă când
  rotunjirea totalului diferea cu un leu.

## 03.10.2026 — Factura emisă pe baza bonului fiscal: marcată în SAGA, WinMentor, D406 și e-Factura; încasată la emitere

**Ce se schimbă pentru contabil:**
- **Export SAGA:** factura emisă pe baza bonului intră cu tipul „f – factură cu bon fiscal”. Până acum SAGA o importa ca
  vânzare nouă, peste raportul Z.
- **Export WinMentor:** factura din bon intră ca „Info CM” (ClasificareSAFT 751, casa de marcat, un bon). Facturile storno
  intră ca storno (381); până acum erau „factură inițială”.
- **D406:** factura din bon se raportează cu codul de taxă 310327, cum cere nota ANAF pentru facturile emise pe baza bonului.
- **e-Factura:** factura din bon pleacă la ANAF cu codul 751 („factură informativă”) și cu mențiunea „Factura încasată cu
  bon fiscal”. Cu 380, vânzarea ar fi apărut la ANAF de două ori.
- **Încasare:** factura din bon apare încasată de la emitere. Nu mai primește memento de scadență către client și nu mai
  oferă „Emite chitanță”.
- Nicio factură nu lipsește din exporturi.

## 04.10.2026 — Bifa „C&D” jurnalizată; schemele de test șterse din producție

**Ce se schimbă pentru contabil:**
- **Mijloace fixe → bifa „C&D”:** o poate pune oricine poate modifica fișa (fără drept separat). Fiecare schimbare rămâne
  scrisă cu cine a făcut-o, când și din ce în ce (da/nu). Apăsarea pe aceeași valoare nu lasă urmă, fiindcă nu schimbă nimic.
- **Baza de producție:** au fost șterse 8 scheme rămase de la teste mai vechi de 11.09 (cu backup). Nu erau firme; firmele
  reale (5) sunt neatinse.

## 04.10.2026 — Punctul 4: salariul contractual are o singură sursă (coloana veche din fișa salariatului retrasă)

**Ce se schimbă pentru contabil:** nimic vizibil. Statul de plată, fluturașul și D112 dau aceleași cifre (probat pe F1). În
spate, salariul de bază se citește numai din istoricul de salariu (valabil de la o dată). Coloana veche, care rămăsese
neactualizată după schimbările de salariu din iulie, a fost ștearsă. Salariații care n-aveau istoric au primit unul de la data
angajării, cu salariul pe care îl aveau.

## 04.10.2026 — Salariul în timp: schimbarea salariului cu dată de la care se aplică; D112 A1 cu condiție scrisă

**Ce se schimbă pentru contabil:**
- **Statul de plată → „Salariu”:** zona arată istoricul salariului (de la ce dată, ce sumă). O dată care nu există, o dată
  dinaintea angajării sau de după încetare și o dată la care există deja un salariu sunt refuzate lângă câmpul „de la”, cu
  motivul. Ce ai tastat rămâne în casete. Pentru o dată deja ocupată apare butonul „Înlocuiește salariul de la …”. Până
  acum, salariul de la aceeași dată se rescria fără nicio întrebare.
- **Lunile închise:** o schimbare de salariu care ar atinge o lună închisă (declarată) e refuzată, și atunci când e datată
  înaintea ei. Până acum, lunile închise se rescriau retroactiv.
- **Mărirea în cursul lunii:** pe statul de plată și în D112 luna se împarte pe zile între salariul vechi și cel nou (probat:
  4.400 → 5.000 de pe 15.09.2026 dă brut 4.727,27; D112 valid).
- **D112 contract uniform A1:** rămâne „nu acum”. Se face la prima modificare reală a modulului D112, în același commit
  (scris în fir și în capul modulului).
- **Punctul 4 (03.10), încheiere:** migrarea producției a rulat după deploy (04.10, 05:02; 5/5 firme; backup
  `~/backup_pre_2b_coloana_20261004_0502.sql.gz`). Cifrele statului de plată și ale D112 pe F1 sunt identice înainte și după.
- **Accesibilitate (toată aplicația):** 54 de câmpuri de formular care, pentru un cititor de ecran, n-aveau nume (eticheta era
  un text alăturat, nelegat de câmp) au acum eticheta legată. Asta include zonele din statul de plată, dialogurile, portalul
  și emiterea.

## 04.10.2026 — Ziua, pe scurt: ce s-a schimbat pentru contabil

Intrările de mai sus, ale aceleiași zile, au detaliul. Pe scurt:

- **Salarii — schimbarea salariului cu dată:** în statul de plată, la „Salariu”, se vede istoricul salariului. Mărirea se pune de la o
  zi anume, iar luna se împarte pe zile între salariul vechi și cel nou, pe statul de plată și în D112. O dată greșită (care nu există,
  dinaintea angajării, după încetare) sau una la care există deja un salariu e refuzată lângă câmp. Ce ai scris rămâne. Salariul de la
  o dată existentă se înlocuiește doar dacă apeși „Înlocuiește …”. O schimbare care ar atinge o lună închisă e refuzată.
- **Salarii — în spate, fără efect pe cifre:** salariul de bază are o singură sursă, istoricul. Coloana veche, neactualizată din iulie,
  a fost ștearsă. Statul de plată și D112 dau aceleași cifre ca înainte (verificat pe F1).
- **Mijloace fixe — bifa „C&D”:** o pune oricine poate modifica fișa. Fiecare schimbare rămâne scrisă (cine, când, din ce în ce).
- **Accesibilitate:** 54 de câmpuri din formulare (salarii, dialoguri, portal, emitere) au acum eticheta legată pentru cititorul de
  ecran. Vizual nu se schimbă nimic.
- **Baza de producție:** au fost șterse 8 scheme rămase de la teste vechi (cu backup). Nu erau firme.
- **Declarații:** nicio schimbare de formular. D112 contract uniform A1 rămâne „nu acum”, cu condiția scrisă: se face la prima
  modificare reală a modulului D112.

## 04.10.2026 — Testarea ca asistent: drepturile pe rol + cele 7 constatări (comanda Costin, decizia „varianta 2”)

**Ce a găsit Costin, testând ca asistent** (cabinet Sesiunea B, Ana, „asistent junior”, F1+F2): „Adaugă firma” nu făcea nimic;
asistentul vedea „+ Adaugă firmă”, „Import în masă” și „Scoate”; emailul superadminului trecea la „Email client”; bun-venitul se
închidea doar de la capăt; ghidul era același pentru toate rolurile; contorul Asistenți număra administratorul; ghidul promitea
„maximum 48 de ore”.

**Ce s-a măsurat înainte** (proba în browser pe producție, contul Anei, fără scrieri): refuzul 403 cădea într-un rând gri la 333 px
DEASUPRA butonului; serverul refuza asistentului nu doar firmele, ci ~50 de operații curente (factură, chitanță, importuri…).

**Decizia Costin („varianta 2”)** — verbatim în DECIZII: „Poate pregăti” = munca curentă; „Poate valida” = validări, amortizare,
închiderea lunii; „Poate depune” = depunerea; doar administratorul = firme, asistenți, chei API, GDPR, abonament, datele cabinetului,
deblocarea perioadei; mereu pe firmele alocate; interfața urmează serverul.

**Ce s-a făcut:** garda `cere_drept` pe 215 rute (nivelurile din `core/drepturi.py`, bifa citită live, firma alocată verificată în
gardă); `GET /eu/drepturi` derivat din gărzi; în interfață, poarta `data-actiune` (184 de apeluri declarate, legate pe element unde se
poate dovedi); refuzul lângă buton și pe câmp; emailul clientului verificat înainte de crearea firmei (aceeași regulă la accesul
clientului, în portal, la invitația de asistent); X + Esc pe ferestrele informative (mecanism unic); ghidul pe rol; contorul cu
administratorul separat; fraza cu 48 de ore scoasă.

**Găsite pe drum și reparate (ciclul de neconformitate):** (1) 11 rute de scriere pe firmă stăteau pe `cere_context` — un CLIENT de
portal le putea chema (facturi recurente, pontaj, model factură, respingerea unei facturi primite); (2) „Răspunsuri REGES” chema GET pe
o rută POST — 405 la fiecare apăsare, din 05.07.2026; (3) invitația de asistent nu dădea „Poate pregăti” și ecranul scria „Nivel 1” la
zero competențe; (4) funcția de creare a asistentului avea parametrii numiți greșit; (5) 35 de refuzuri scrise direct în text (fără
stil de eroare, 4 dintre ele ca HTML neescapat); (6) aceeași numărătoare greșită (administratorul ca „asistent”) în semaforul echipei și
în Capacitate; (7) contrast insuficient la numerele grupelor din ghid.

**Ce se schimbă pentru contabil (pe scurt):**
- **Asistentul** vede doar ce are voie să facă. Cu „Poate pregăti” lucrează pe firmele alocate: facturi, chitanțe, importuri,
  note în ciornă, pontaj, mijloace fixe, export SAGA/WinMentor, e-Transport, declarații de pregătit. Validările (note, declarații,
  amortizarea, închiderea lunii) cer „Poate valida”; depunerea cere „Poate depune”. Adăugarea, importul și scoaterea firmelor,
  asistenții, cheile API, GDPR, datele cabinetului și deblocarea unei luni închise rămân la administrator. Butoanele interzise
  nu mai apar; dacă o cerere e totuși refuzată, mesajul spune ce drept lipsește și cine îl dă.
- **Invitația unui asistent** dă implicit „Poate pregăti”. Un asistent fără nicio bifă apare ca „fără competențe”, nu „Nivel 1”.
- **Adaugă firmă:** refuzul apare sub buton, cu roșu, iar câmpul vinovat e marcat. O adresă de email care aparține unui cont cu
  alt rol e refuzată numit, iar firma NU se mai creează.
- **Bun venit:** se închide și din X (sus) și cu Esc. Asistentul vede doar pașii pe care îi poate face; fără firme, i se spune să
  ceară administratorului. Din fraza despre Suport a ieșit termenul „se rezolvă în maximum 48 de ore” (fraza rămâne, fără termen).
- **Firme scoase:** istoricul firmelor scoase din portofoliu îl vede doar administratorul (asistentul vedea și firme care
  nu-i fuseseră niciodată alocate).
- **Asistenți:** contorul arată administratorul separat („1 administrator · 1 asistent (1 activ)”).
- **Răspunsuri REGES** (administratorul) nu mai primește eroarea de metodă de la fiecare apăsare (cerea GET pe o rută POST).
  Răspunsul propriu-zis depinde de conexiunea REGES a firmei — neprobat aici, cere credențiale ITM reale.
- **Anunțul** „Mesaj de la iConta.eu” are X; închiderea înseamnă „am citit”.

- **Asistentul fără drepturi** nu mai vede nici butoanele care deschid formulare de lucru („+ Notă nouă”, „+ NIR nou”,
  „+ Salariat nou” …): s-au văzut pe producție după prima publicare (contul Anei) și s-au reparat în commitul următor.

**Proba pe producție, după publicare (contul Anei, fără bife, doar citire):** vede F1 și F2; nicio acțiune afișată (Adaugă /
Import / Scoate / Firme scoase / „+ Notă nouă” / pașii de import / operațiunile); ecranele de import și de operațiuni spun că trebuie
„Poate pregăti” și cine îl dă; cererea de adăugare a unei firme e refuzată (403) cu mesajul care numește administratorul; consola
fără erori.

**Atenție la contul Ana (producție):** în bază are toate trei bifele pe „nu” (invitația veche nu dădea „Poate pregăti”). Cu
regula nouă vede firmele F1, F2, dar nu poate lucra pe ele până nu i se bifează „Poate pregăti” din Asistenți.

## 04.10.2026 — Confirmările de drepturi (răspunsurile lui Costin la cele 8): documentele de terț la „Poate pregăti”, regimul de TVA jurnalizat, REGES la „Poate depune”

**Ce a decis Costin** (verbatim în DECIZII, „PIVOT pe drepturi”): R52 răsturnat — asistentul cu „Poate pregăti” vede fluturașul,
PDF-ul chitanței și fotografia bonului pe firmele alocate; regimul de TVA rămâne la „Poate pregăti”, cu fiecare schimbare jurnalizată
(utilizator, dată, vechi → nou); REGES: cheile la administrator, trimiterea și răspunsurile la „Poate depune”. Ana: datele ei NU s-au
atins (bifa i-o pune Costin).

**Ce s-a măsurat înainte** (browser, cod HEAD, asistent doar cu „Poate pregăti”): fluturașul ascuns; fotografia bonului — „o deschide
doar administratorul”; PDF-ul chitanței 403; regimul de TVA schimbat Nu → Da fără nicio urmă. Și, neprevăzut: „Chei REGES” și butonul
„REGES” de pe fiecare salariat (12) erau vizibile asistentului, deși ruta din spatele lor îl refuza.

**Ce s-a făcut:** cele trei documente pe `cere_drept(PREGATI)`; `reges-poll` / `reges-trimite-salariat` pe `DEPUNE`, `reges-config` rămâne
la administrator; tabela `firma_profil_jurnal` în schema fiecărei firme (migrare + template; producția migrată, backup după); o singură
funcție de jurnal (`repo_firma_profil.jurnalizeaza_regim_tva`) chemată de ambele căi care scriu regimul, cu utilizatorul din token.

**Găsite pe drum și reparate (ciclul de neconformitate):** (1) garda R56 număra ca „scrie credențiale” rutele care doar CITESC cheile
REGES și rata crearea unei chei API — sonda reparată, nu ocolită cu o excepție; (2) 18 butoane care deschid formularul unei acțiuni
restrânse („Chei REGES”, „REGES”, „Stornează”, „Trimite pe email”, „Inventar”, editările salariatului…) rămâneau vizibile celui refuzat —
treaptă structurală nouă în scanner; (3) 13 mesaje de eroare de la server puse neescapat în HTML — `esc()` + regulă în verificator
(DS v2.65); (4) mesajul de refuz „Poate depune” vorbea doar de ANAF.

**Proba după** (browser, același asistent): fluturașul se descarcă (12 butoane, PDF 200); fotografia bonului se afișează (imagine
200); PDF-ul unei chitanțe se deschide (200, `%PDF-`); Nu → Da la TVA lasă rândul `platitor_tva false → true` cu numele asistentului;
doar cu „Poate pregăti”, niciun buton REGES; cu „Poate depune”, „Răspunsuri REGES” și „REGES” pe salariați, dar nu „Chei REGES”.

## 05.10.2026 — Secretele scoase din git: parola contului de probă, parola bazei de producție, rețeta conturilor de test (comanda Costin)

**Ce a cerut Costin:** parola contului `contabil.b@sesiuneab.test` era în `frontend_test/f1_helper.py`, iar oglinda e publică —
resetare, citire din `~/.iconta/fe_test.env`, aceeași căutare în tot arborele.

**Ce s-a găsit căutând:** în arborele urmărit, parola VIE a lui contabil.b (de două ori) și parola seed-urilor de test (moartă, dar
reactivabilă la o nouă rulare); un tabel cu 6 conturi de test și parolele lor (`date_test/C3_cabinete.md`); în ISTORIE, căutând
invers fiecare valoare din `~/.iconta`, **parola bazei de producție**, scrisă pe 09.09.2026 de un instrument de măsurare într-un
artefact comis. Restul cheilor (JWT, ANAF, Brevo, Anthropic, Fernet, Woo, baza de test) n-au fost niciodată în git.

**Ce s-a făcut:** contabil.b — parolă nouă (sesiunile vechi invalidate), citită de probe din `fe_test.env` (care acum țintește acest
cont; înainte ținea un cont al bazei de test, refuzat pe producție); seed-urile citesc `SEED_CABINET_PAROLA` din mediu; parolele din
tabel scoase; **parola bazei de producție rotită** (baza ascultă doar local, deci nu era folosibilă din afară; `db.env` rescris,
serviciul repornit, joburile cron citesc același fișier); artefactul redactat și instrumentul reparat; gard nou în poartă, iar
scannerul de secrete existent (orb la `CAB_PAROLA = …` și la `"parola": …`) reparat.

**Proba:** parola din istoric -> 401, cea nouă -> 200, un token emis înainte -> 401; parola veche a bazei -> refuzată de Postgres,
cea nouă -> conectat; aplicația 200 după repornire; cele 16 căi de logare ale uneltelor din `frontend_test` -> 200.

## 05.10.2026 — Testarea ca asistent (2): povestea lunii pe termenii pachetului, aprobarea la „Poate valida”, motivul acțiunilor ascunse, Asistenți, iconițe, Pachete (comanda Costin)

**Ce a găsit Costin:** povestea generată de AI scria „încasări” acolo unde pachetul spune „venituri”; „Aprobă” și „Trimite” erau
la „Poate pregăti”; fără drept, fereastra poveștii rămânea fără butoane și fără explicație; administratorul apărea fără „Poate
valida”; „Raportează” n-avea iconiță; alegerea firmei apărea de două ori în Pachete; previzualizarea cu povestea goală n-avea cifre.

**Ce s-a măsurat înainte:** cu AI-ul real, pe ALFA MICRO SRL (venituri 3.000, cheltuieli 8.186, pierdere 5.186), promptul vechi a
scris „firma a avut încasări de 3.000 de lei” la ambele generări; în browser, toate cele șapte situații reproduse pe contul de asistent.

**Ce s-a făcut:** promptul cere termenii și sumele pachetului, iar textul se verifică după generare (o reîncercare, apoi avertisment
pe ecran) — cu promptul nou, zero abateri la ambele generări; aprobarea poveștii are rută proprie pe „Poate valida”, trimiterea la
fel; poarta drepturilor pune, în orice fereastră unde ascunde acțiuni, motivul („cer dreptul «…»… Îl acordă administratorul
cabinetului, din ecranul Asistenți”) — se vede și pe alte ecrane (ex. Registrul jurnal); administratorul apare cu toate drepturile,
fără bife, iar serverul nu-i mai schimbă bifele; iconițele „Raportează” / „Raportări” refăcute; un singur control pentru firmă;
emailul (și previzualizarea) arată cifrele pachetului, iar „Trimite” spune de ce e inactiv.

**Găsite pe drum:** un rezultat zero apărea „(profit)” în pachet; administratorul de pe producție avea „Poate valida” scos din ecran,
deci nu era numărat printre validatori (repus, regula B3 din 06.08); contrast insuficient pe pastilele de drepturi și pe griurile din
email.

## 05.10.2026 — Fluxul de factură pe F1 (A): ce s-a completat nu se mai pierde (comanda Costin, pct.1)

**Cauzele, din jurnale:** Ana s-a logat pe 04.10 la 11:29:34; tokenul ține 24 h și nu se reînnoia cât lucra, deci a expirat pe 05.10
la 11:29:34; prima cerere de după (căutarea cotei pentru linia facturii) a primit 401, iar aplicația a trimis-o la logare, golind
factura. Serverul nu repornise. A doua pierdere: după refuzul emiterii (lipsea forma juridică), „Deschide Date firmă” -> „Înapoi”
redesena factura de la zero, deși mesajul promitea că rămâne.

**Ce s-a făcut:** sesiunea se reînnoiește singură cât se lucrează; dacă totuși expiră, parola se cere într-o fereastră peste ecran,
iar cererea refuzată se reia; navigatorul păstrează orice ecran în care s-a tastat ceva când se deschide altul peste el; anunțul de
versiune nouă nu reîncarcă peste un formular început.

**Proba (browser, asistent, baza de test):** înainte — la expirare ecranul de logare, factura goală; după Date firmă -> Înapoi,
factura goală. După — fereastra de reautentificare peste factură, toate câmpurile intacte, cererea reluată (401 -> logare -> 200);
după Date firmă -> Înapoi, toate câmpurile intacte; o sesiune trecută de jumătate s-a reînnoit singură.

## 05.10.2026 — Fluxul de factură pe F1 (B): emiterea (comanda Costin, pct.2–5)

**Ce s-a făcut:** la deschiderea „Emite factură” se spune ce lipsește din Date firmă (forma juridică, capitalul), cu „Deschide Date
firmă”, iar „Emite” e inactiv cu motiv până se completează; forma juridică e propusă din ANAF și din denumire când nu se contrazic;
cota TVA a fiecărei linii se alege dintr-o listă, iar schimbarea față de cea propusă se consemnează (propus -> ales, cine, când);
formularul arată și lasă de setat data emiterii, scadența și seria; PDF-ul facturii are „Cod TVA: RO…”, „Seria X nr. N”, „Data
emiterii”, „Data scadenței” și titlu de document (la fel toate PDF-urile aplicației).

**Proba (browser, asistent, baza de test):** înainte (HEAD f8e08e72) — nicio notă la deschidere, „Emite” activ, fără dată/scadență/
serie, cota fixă, 422 la emitere. După — nota „Forma propusă: SRL”, „Emite” inactiv; Date firmă cu SRL preselectat -> Salvează ->
Înapoi: nota dispare, „Emite” activ, clientul păstrat; cota 11 -> 21, rând de jurnal [1, „Pâine albă feliată”, 11, 21, asistentul];
factura cu data 05.10.2026, scadența 04.11.2026; PDF „Cod TVA: RO96653616” / „RO14399840”, „Data emiterii: 05.10.2026”.

**Găsit pe drum:** Date firmă nu se putea salva deloc pe o firmă cu o lună închisă (refuz 500) — poarta perioadei închise se punea
la prezența câmpurilor, nu la schimbarea lor; reparat în trei locuri (Date firmă, vector, regim TVA). Tabelul nou s-a migrat pe
producție după backup verificat. Tot pe drum: tabelul nou fusese legat de factură fără regulă la ștergere, deci o factură
necontată emisă cu altă cotă nu s-ar mai fi putut șterge — legătura e acum în cascadă (migrare refăcută pe producție, după backup
complet); căutând clasa, ștergerea unei facturi legate de SPV ieșea tot cu eroare brută — acum refuzul e numit, cu ieșirea.

**Respins de poartă, reparat în același pas:** lista de cote se citea „azi” când lipsea data — acum se citește la data facturii din
formular și se reîncarcă la schimbarea ei. Căutând de unde vine data formularului: 21 de locuri din 10 ecrane produceau data în UTC
(între 00:00 și 03:00 „azi” era ieri; intervalul „luna” din activitatea cabinetului și termenul UIT din e-Transport greșeau ziua
oricând) — toate trec acum prin `dataIso`, cu gard în verificator.

## 05.10.2026 — Fluxul de factură pe F1 (C): documentul notelor, starea facturii, banca, linia facturii (comanda Costin, pct.6–9)

**Ce s-a făcut:** nota 607=371 de la emitere și notele din extras poartă documentul sursă (factura, extrasul), iar odată cu ele
casa, NIR-ul, bonul, raportul Z și statul de plată; în Registrul jurnal, ciorna fără document e marcată și „Validează” cere
confirmare, iar nota primește un câmp „Document justificativ”; factura spune „notă propusă, de validat” cât nota e ciornă și
duce la notă; banca numără ce s-a potrivit, contarea comisionului spune nota creată (627=5121), liniile noi apar primele;
pe linia facturii, prețul și UM vin din nomenclator, UM se vede și se trimite, linia fără articol spune că marfa nu se
descarcă; cantitățile și CMP-ul se arată fără zecimale de prisos, în toată aplicația.

**Proba (browser, asistent, baza de test):** înainte (HEAD dadd5f86) — „stoc 110.000”, preț gol, fără UM, fără semn; factura
„contabilizată” cu nota ciornă; „Iesire stoc … x2.000”; validarea fără document trecea din primul clic; „2 linii importate și
potrivite.”, „Nota 401=5121 — 0 înregistrări create.”. După — „stoc 110 buc”, preț 5 și „buc” din nomenclator, semnul liniei
fără articol (dispare la alegerea articolului); „notă propusă, de validat” + „nota #17”; „Ieșire stoc … × 2 buc” cu
„Factură 1 din 05.10.2026”; confirmarea „Nota #16 nu are document justificativ. Validezi totuși?” fără nicio cerere trimisă;
„2 linii importate: 0 potrivite pe facturi, 2 fără potrivire…”, „Notă 627=5121 creată (ciornă #19)”.

**Găsite pe drum:** ID-ul e-Factura ar fi dublat seria („COERCOER-T3”); sugestia învățată de la bancă nu rula niciodată;
galbenul și griul de semafor erau folosite ca culoare de text în 10 ecrane (contrast sub prag, prins de axe pe jurnal și bancă).

**Respins de poartă (C), reparat în același pas:** cinci roșii, toate efecte ale lui C: două calibrări vechi
(`test_verde_derivat`, `test_c1_pontaj_neconfirmat_gri`) erau scrise pe tokenii de semafor pe care DS v2.70 îi scoate de pe
text — forma condiționată și starea gri au rămas, s-a schimbat tokenul; validarea notei mutată într-o funcție separată nu
mai era legabilă de butonul ei (clichetul drepturilor, 36 > 35) — cererea a revenit în ascultătorul butonului; blocul de
clichete din PREDARE fusese regenerat cât exista o aserțiune pe text, deja înlocuită.

## 05.10.2026 — Fluxul de factură pe F1 (D): Stocuri, descărcarea lunii, fereastra firmei (comanda Costin, pct.10–12)

**Ce s-a făcut:** ecranul Stocuri se deschide cu situația stocului (articol, UM, cantitate, CMP, valoare, total), iar
formularele stau dedesubt, la cerere; Rețete apare numai la firmele HoReCa (CAEN din lista Codului fiscal) sau la cele cu
rețete; „Descarcă gestiunea lunii” nu mai poate scrie de două ori aceeași lună, iar descărcarea din factură nu se dublează;
fereastra firmei grupează cele 32 de carduri sub cinci titluri (Zilnic · Registre · Raportări și declarații · Operațiuni
speciale · Firma), dintr-o singură sursă; cardul Produse are culoare; Solicitări se deschide în fereastră.

**Confirmarea cerută (pct.10):** descărcarea lunii nu descarcă a doua oară marfa descărcată la emitere — vânzarea din
factură nu intră în baza ei (probată de test). Limita, ridicată ca decizie: factura de marfă fără articol, la o firmă
global-valorică, nu se descarcă deloc; la HoReCa, rețetele și raportul Z pot descărca de două ori.

**Proba (browser, asistent, baza de test):** înainte (HEAD d582e083) — 31 de carduri într-o grilă plată, fără titluri;
Stocuri fără situație, cu formularele deschise și Rețete la o brutărie. După — Zilnic 11 · Registre 6 · Raportări și
declarații 5 · Operațiuni speciale 3 · Firma 6 (31 de carduri, 0 în afara grupurilor, la fel pe telefon); Stocuri începe cu
„Pâine albă feliată · buc · 110 · 2,00 · 220,00”, total 220,00; formularele închise; fără Rețete.

**ZIP (pct.13):** `/home/costin/ghid_incoming/iconta_testare_factura_F1.zip` — patch-urile A–D, fișierele atinse, probele înainte/după
(JSON + capturi + factura PDF), hărțile de cod, temeiul, jurnalele mutațiilor; scanat de parole înainte de arhivare.

## 06.10.2026 — Lotul 06.10, partea 1: răspunsul la §6 din raportul F1 (comanda Costin)

**Ce s-a făcut:** seria facturii e obligatorie — refuzul o cere chiar în mesaj și emiterea continuă; notele generate de aplicație
fără document extern primesc documentul intern numerotat (tablou de amortizare, situația de descărcare, bon de consum, listă de
inventariere, notă de calcul); metoda de stoc e o setare explicită în Date firmă, iar fiecare ieșire se descarcă o singură dată
(factura fără articol la global-valoric intră în descărcarea lunii; la cantitativ-valoric Z-ul HoReCa nu mai intră în descărcarea
globală); orice schimbare din Date firmă se jurnalizează și se vede în „Istoricul modificărilor”.

**Proba (browser, asistent, baza de test, firma cu numerotare fără serie, ca F1/F2 în producție):** înainte (HEAD 365ea19c) —
factura „7” emisă fără serie; Date firmă fără metodă și fără istoric. După — refuz 422 `SERIE_LIPSA` cu câmpul seriei; „ZT” salvat
din mesaj, factura „ZT7” emisă cu formularul păstrat; metoda „cantitativ-valoric” aleasă, iar istoricul arată cine a schimbat-o,
cu valoarea veche și cea nouă.


## 06.10.2026 — Lotul 06.10, partea 2: /ghid pentru indexare (comanda Costin)

**Ce s-a făcut:** adresele vechi de ghid răspund 301 (6 slug-uri cu înlocuitor, `.md`, `GH-#####`, `proba-ghid`), iar 11 linkuri
interne rupte s-au reparat; `/ghid` devine cuprinsul a 19 teme (5,6 KB în loc de 2,3 MB), fiecare temă cu pagina ei, în
sitemap; fiecare ghid arată tema și 6 ghiduri înrudite; „(sursă: anaf_surse/…)” devine numele actului cu link spre
legislatie.just.ro sau static.anaf.ro (129 din 132 de surse cu adresă verificată), iar căile `core/….py` din proză au dispărut
— 3.828 de ghiduri rescrise. Niciun ghid nou publicat.

**Măsurat:** Google real n-a cerut `/sitemap.xml` în cele 14 zile de jurnal (505 cereri pe site, 0 pe sitemap); sitemap-ul
răspunde 200, valid, 6.581 de adrese. Titluri aprobate nepublicate: GH-09299 (lotul 19).

## 06.10.2026 — Lotul 06.10, partea 3: salariile F5 din aceleași sume ca D112 (comanda Costin)

**Ce s-a făcut:** CAS, CASS și impozitul de pe stat și fluturaș sunt cele declarate în D112 (rotunjite aritmetic pe salariat),
deci netul iese din aceleași sume ca nota: F5 10/2026 — net 6.809,45 (era 6.810,24), 421 soldat. CAM pe baza contributivă,
împărțit pe cartele așa încât suma lor = codul 480 (260, era 259,77). Propunerea notei verifică 421 la ban și spune ce a
verificat. Rotunjirea bancară implicită (`quantize` fără mod) scoasă din 65 de locuri, între ele CAS-ul pe concediul medical.
Temeiul rotunjirii bazei impozitului (HG 1/2016 Norme tit.IV pct.4) confirmat, fără schimbare. Ciorna de salarii vizibilă
cabinetului (pct.12): oprită — mecanismul de validare presupus pentru facturi nu există; decizie cerută.

**Măsurat:** producție 20/20 de luni-firmă soldează 421 la ban și au CAM = 480; baza de test 41/52 — cele 11 rămase au toate
concediu medical (indemnizația nu e contabilizată).

## 06.10.2026 — Lotul 06.10, partea 4: povestea lunii (comanda Costin)

**Ce s-a făcut:** povestea pleacă fără marcaje (generare, salvare, email, portal — și poveștile aprobate înainte); aceeași
curățare pe analiza tiparelor și pe răspunsul AI la raportări; „Rezultat înainte de impozit” pe pachet, email, prompt și portal,
iar cifra exclude impozitul (691/698, 79x); restanțele nu mai intră în povestea pentru client, iar un text care le pomenește
e semnalat în editor.

**Proba (browser, asistent, baza de test):** înainte — emailul previzualizat cu „**Veniturile**”, „# Titlu”, „*pozitiv*” și
„Rezultat 0,00 lei (neutru)”; după — „Veniturile lunii au fost bune. / Titlu / Rezultatul e pozitiv.” și „Rezultat înainte de
impozit 0,00 lei (neutru)”.

## 06.10.2026 — Lotul 06.10, închiderea

**Producție:** backup complet `iconta_v2` (`/home/costin/backups/iconta_v2_pre_lot0610_20261006_0408.dump`, 2,4 MB, 353 de tabele cu
date, verificat cu `pg_restore -l`), apoi migrările `documente_interne_contor` și `firma_profil.metoda_stoc` pe tenant_049–053 (5/5),
verificate în catalog. **Lanțul vizual** (server de probă din worktree separat — static-ul publicat lângă el, nu în directorul servit
de producție): axe 0 încălcări pe ecranele scanate (inclusiv stat de plată), probele P3/P4 axe 0, arborele asistentului 0 perechi
greșite, Declarații 50 de celule fără revărsare; mobil fără overflow-x. Rezidiu de probă șters din baza de test: produsul
„Consultanță contabilă lunară” creat de proba părții 1 (umfla antetul T21).

## 06.10.2026 — Validarea notelor prin coadă și concediul medical în nota de salarii (comanda Costin, răspunsul la §6)

**Ce s-a făcut:** ce pregătește asistentul (orice notă ciornă) intră în coada de validare a cabinetului — aceeași coadă ca
declarațiile: contorul „pregătite” / „de validat”, notificarea, Activitate cabinet, „Note de validat” cu Validează / Respinge
cu motiv; jurnalul și statul de plată arată unde e nota; nota respinsă se retrimite explicit. Nota de salarii cuprinde
indemnizația de concediu medical (6458 / 4382 = 423, reținerile ei pe 423); fluturașul și fișierul de plată folosesc
reținerile declarate; 421 și 423 se soldează la ban (probat pe certificat de continuare). Pe drum: tichetele peste plafon
pe 642, zilele angajatorului pe episod. Defectul D112 al zilei de diminuare: consemnat ca datorie, decizie cerută (D1).
Titlurile aprobate nepublicate: 287 (112 candidat + 175 asemănător) + 3 fără corespondent în registru.

**Închiderea (06.10.2026):** backup `iconta_v2_pre_validare_note_20261006_0831.dump` (2,4 MB, 358 de tabele cu date, verificat cu
`pg_restore -l`), apoi migrarea `core.migrare_validare_note` pe producție: `declaratii_coada.fel` + autorul și triggerul pe
tenant_049–053 (5/5). Commitul de lucru `11cd3150`, avansat pe main; poarta completă la commitul de închidere.

**Poarta de închidere, prima rundă: RESPINSĂ (06.10.2026).** 15 picate / 7382 trecute / 9 sărite / 14 xfail, toate pe gărzi
structurale, niciuna pe comportament. Reparate înainte de a doua rundă: ruta `retrimite` n-avea use-case cu numele ei
(scanerul cădea pe atribuirea pe modul: 20 de tabele „scrise” → redenumit `uc_coada.jurnal_retrimite`, acum 1 tabel); rândul
individual din `p4_clasificare` pentru retrimitere (două tranzacții: elementul, apoi anunțul); `db.get_conn` scrie autorul cu
`SET iconta.utilizator TO …` (forma lui `SET search_path`), nu cu `SELECT set_config` — nu e SQL de date, deci `db.py` nu intră
în universul E2a; butonul „Trimite din nou” își afișează refuzul cu `arataMesaj` direct (helperul local `eroare` e o limită
declarată a scanerului de refuz tăcut); cheile `stari_note` → `stare_coada`/`motiv_respingere`; un singur apel `/aproba` în
`validat.js`; retrimiterea verifică luna închisă (R42); blocul de clichete regenerat.

**A doua rundă: RESPINSĂ (06.10.2026)** — 3 picate / 7394 trecute: efecte ale reparațiilor din prima rundă, pe care nu le
rulasem țintit (blocul și adnotarea TRASEE ale retrimiterii, numărătoarea P7 286 → 287 pentru `nota_cu_linii` din
`jurnal_retrimite`). Regenerate / ridicată cu motivul numit; setul țintit de 16 fișiere de gărzi: 438 trecute.

**A treia rundă: VERDE (06.10.2026)** — 7397 trecute / 9 sărite / 14 xfail (COLLECTED 7420), verificator TOTAL 0; commitul `a7dcb741`,
publicat four-way (HEAD = origin/main = backup/lant-2026-10-06 = RUNNING), ZIP `iconta_validare_note.zip`.

## 06.10.2026 — Ziua, pe scurt: ce s-a schimbat pentru contabil

Intrările de mai sus, ale aceleiași zile, au detaliul. Pe scurt:

- **Facturi — seria e obligatorie:** o factură fără serie e refuzată, iar mesajul cere seria chiar acolo; după ce o scrii, emiterea
  continuă cu formularul păstrat. **În producție, toate cele 5 firme au seria goală**: prima emitere a fiecăreia va cere seria.
- **Stocuri — metoda de stoc se alege explicit** în Date firmă (cantitativ-valoric sau global-valoric). Până e aleasă, orice ieșire de
  marfă e refuzată cu trimitere la Date firmă. **În producție, toate cele 5 firme o au necompletată.** Fiecare ieșire se descarcă o
  singură dată (fără dublare între factură și descărcarea lunii).
- **Date firmă — istoricul modificărilor:** orice schimbare rămâne scrisă (cine, când, valoarea veche și cea nouă).
- **Notele generate de aplicație** care nu au document extern primesc un document intern numerotat (tablou de amortizare, situație
  de descărcare, bon de consum, listă de inventariere, notă de calcul).
- **Salarii — statul și fluturașul folosesc exact sumele din D112** (CAS, CASS, impozit, rotunjite pe salariat), deci netul iese din
  aceleași sume ca nota. Exemplu F5 10/2026: net 6.809,45 (era 6.810,24); CAM 260 (era 259,77), egal cu codul 480 din D112. Propunerea
  notei de salarii verifică 421 la ban.
- **Salarii — concediul medical intră în nota de salarii:** partea angajatorului pe 6458 = 423, partea din FNUASS pe 4382 = 423,
  reținerile pe indemnizație pe 423; fluturașul și fișierul de plată (SEPA) plătesc și indemnizația netă. 421 și 423 se închid la ban
  și în lunile cu concediu medical. Excesul de tichete de vacanță trece pe 642 (cheltuiala cu tichetele), nu pe 641. La un certificat de continuare, zilele plătite de angajator se
  socotesc pe tot concediul (episodul), nu de la zero pe fiecare certificat.
- **Validarea notelor de către cabinet:** o notă scrisă de un asistent care are doar „Poate pregăti” ajunge la cabinet, în aceeași coadă
  ca declarațiile: contorul „de validat”, notificare, „Note de validat” cu Validează / Respinge cu motiv, Activitate cabinet. Jurnalul și
  statul de plată arată unde e nota; o notă respinsă se vede cu motivul și se trimite din nou cu „Trimite din nou la validare”.
- **Povestea lunii pentru client:** fără marcaje de formatare, „Rezultat înainte de impozit” (fără 691/698), fără restanțe în text.
- **Ghiduri publice:** /ghid e împărțit pe 19 teme; sursele apar cu numele actului și link oficial; adresele vechi redirecționează.
- **Declarații:** niciun formular schimbat. Un defect cunoscut, nereparat: la un certificat medical INIȚIAL cu zi de diminuare, D112
  declară salariu și pentru ziua neplătită — reparația cere modificarea modulului D112 (pasul D1), decizie cerută lui Costin.
- **Baza de producție:** două migrări de structură (după backup verificat): metoda de stoc + contorul documentelor interne, apoi coada
  de validare a notelor (autorul notei + sincronizarea cu jurnalul). Nicio cifră existentă schimbată.


## 06.10.2026 — Lotul 07.10: D112 ziua de diminuare, retestul F5/F1, titlurile aprobate nepublicate (comanda Costin)

Trei părți, fiecare cu commitul ei pe ramura `lucru/lot-07-10` (fără poartă completă între ele), apoi închiderea pe `main` cu o
singură poartă completă. Decizia, verbatim, și consecințele: DECIZII 06.10.2026 („Lotul 07.10”).

- **P1 — D112 (`1749dde8`).** Pasul D1 al contractului uniform: `calcul_d112` + `build_xml` extrase din generator, `pull` /
  `genereaza` / `obligatii` pe `Perioada`, 76 de apelanți rescriși; dovada = XML identic byte cu byte pe toate testele D112 (169 de
  XML-uri, 29 de refuzuri). Apoi reparația: salariul realizat, zilele lucrate, tichetele și pragul part-time pe zilele
  CERTIFICATULUI, ca statul de plată. Probă: certificat inițial de 5 zile (o zi de diminuare), salariu 6.000 — D112 declara 4.909,09
  / 18 zile, acum 4.636,36 / 17 zile = statul; CAS 1.384 -> 1.316, CASS 554 -> 527; DUK valid.
- **P2 — retestul (`b8a5d0ce`).** Cele 20 de puncte (2–21): factura păstrată pe orice drum, butonul spre Date firmă pe refuz,
  mesajele aduse în vedere, coada pe document (o factură = o validare) și pe pregătire (retrimiterea nu e pregătire nouă), nota la
  validare blocată la editare/ștergere, data notelor lunare = ultima zi, notificările cu firmă și cu destinație, cardul = fereastra,
  scadența propusă (Legea 72/2013), istoricul Date firmă lizibil, formularele ascunse chiar ascunse. Pe drum: o probă oarbă (rețeta
  peste stoc) și o gardă nouă oarbă (prinsă de mutație), reparate.
- **P3 — titlurile (`f6807786`).** 62 de titluri aprobate fără pagină publicată (exact); registrul de titluri adus la zi (81 de
  rânduri publicate, rămase „candidat”/„asemănător”, plus un titlu dublat) și păzit.

## 06.10.2026 (seara) — Ciorna facturii, a patra pierdere: fila veche; prețul și articolul pe care nu le-a ales omul (comanda Costin)

Decizia și temeiul: DECIZII 06.10.2026 („Ciorna facturii, a patra pierdere”). Gărzile: GARZI 06.10.2026 (aceeași intrare).

- **Cauza pierderii a patra** n-a fost ciorna: fila lui Costin rula codul de dinainte de ea (încărcată 19:12:40, publicarea 19:15:26,
  autentificarea 19:46:51 fără reîncărcare), iar anunțul „Versiune nouă” nu apărea, fiindcă își lua referința la autentificare.
  Acum referința e amprenta codului încărcat; proba pe fila veche: înainte fără anunț, după „Versiune nouă · reîncarcă”.
- **Ciorna, pe drumul exact** (Facturi → completat → ← → ← → Date firmă → ← → Facturi → Emite) și pe toate celelalte ieșiri (X,
  reîncărcare, firul de sus, tab nou, „Schimbă seria”, emitere refuzată): păstrată, cu anunț; altă firmă / alt utilizator: formular
  gol; „Renunță”: ștearsă. Pe codul vechi: pierdută pe drumul exact.
- **Prețul** pe care nu l-a ales nimeni nu mai stă pe rând: propunerea nomenclatorului se golește când denumirea se schimbă, golul
  rămâne gol, serverul refuză linia fără preț lângă câmp (CF art.319 alin.(20) lit.i). La fel: factura recurentă, intrarea în stoc
  (care, în plus, crea articolul înainte de refuz și ieșea 500), nomenclatorul și rețeta.
- **Articolul**: rândul „Carte – Ghid contabil 2026” pleca legat de „Marfa A” și s-ar fi descărcat din stocul ei — acum denumirea
  scrisă de mână dezleagă articolul. La fel: ingredientul nou al rețetei, transferul, reclasificarea, fișa de magazie.
- **Scadența** se propune la deschiderea formularului nou (06.10 → 05.11.2026); „zz.ll.aaaa” era tot codul vechi din filă.

## 06.10.2026 (seara) — Parcurgerea g11 · g08 · g09 ca un contabil, pe baza de test (doar constatări)

67 de puncte, pe codul `de36b2a1` (8011, `iconta_test`), cu rolurile din plan (asistentul = Ana, fără validare/depunere;
patronul = cabinetul) și firmele după tip (F1–F5 sunt numai pe producție). Raportul punct cu punct, capturile și jurnalele:
`~/ghid_incoming/iconta_parcurgere_g08_g09_g11.zip`. Nimic reparat; constatările: GARZI 06.10.2026 („Parcurgerea g11/g08/g09”),
cele mecanice ca datorie în `core/test_datorie.py`.

- **g11:** DUK valid pe tot ce s-a generat, cu excepția D112 part-time (atenționare SP1B4_1 — prag 4.125 față de 3.750);
  drepturile țin (Ana 403 la aprobare și depunere); depunerea cu o constatare certă cere confirmare scrisă; declarațiile depuse se
  persistă cu xml + rânduri. Două drumuri nu ajung în coadă: **D390 (500 la server)** și **orice declarație cu formular manual**
  (ecranul nu trimite formularul). Recipisa nu se întoarce (SPV, extern).
- **g08:** amortizarea cere „Poate valida”; notele ciornă se văd în jurnal înainte de validare; refuzurile au mesaje clare. Constatări:
  „nicio notă” afișat când nota există (comodat), „ID mijloc fix” fără listă, „Dovadă” text liber față de da/nu, reevaluare cu
  cont lipsă, „nimic de amortizat” fără motiv.
- **g09:** schimbarea regimului TVA e jurnalizată și avertizează la diferența față de ANAF; „Achiziție de la agricultor” deschide
  vânzarea (cheie dublată); marja turism negativă dă o creanță mai mare decât încasatul; TVA la încasare și aur — fără firmă de test.

## 07.10.2026 — C1/C2/C7 reparate; validatorul D112 la zi; atenționarea DUK cu confirmare; bilanțul prin coadă (comanda Costin)

Decizia și temeiurile: DECIZII 07.10.2026. Gărzile: GARZI 07.10.2026.

- **Validatorul D112** era J27.0.1; ANAF publicase J27.0.6 (corecția regulii salariului minim în J27.0.2). Instalat: D112 part-time
  09/2026 (4.125 = 4.325 − 200, OUG 89/2025 art.III alin.(5) lit.b) iese valid. Încă 4 validatoare în urmă (D100, D101, D710, B230),
  instalate; toate 62 = publicat, cu manifest și gardă.
- **Atenționarea DUK** nu mai oprește coada: se arată și cere confirmarea scrisă a contabilului (păstrată cu numele lui, legată de
  XML); **eroarea DUK oprește** la intrare, aprobare și depunere, fără portiță.
- **C1** D390 intră în coadă (era 500); **C2** declarațiile cu formular manual intră în coadă (D307 probat; D230 anual: era 500);
  **C7** „Achiziție de la agricultor” deschide formularul de achiziție.
- **C4** mijlocul fix se alege din registrul activelor; **C11** bilanțul S1005/S1003 trece prin coadă (pregătit → validat → depus),
  cu termenul din Legea 82/1991; **fila veche** se reîncarcă singură la autentificare când nu e niciun formular început.
- Datorie nouă: 29 de tipuri fără termen de depunere sursat (coada le pune perioada de raportare).

## 07.10.2026 — C5 și C6 reparate, cu clasa (comanda Costin)

Decizia: DECIZII 07.10.2026 („C5 și C6”). Gărzile: GARZI 07.10.2026 („C5 și C6”).

- **C5** Operațiuni › Chirii / comodat: după nota scrisă, ecranul spunea „Calcul (nu s-a generat nicio notă): inregistrari: 31”; acum
  „Notă generată (ciornă) #33”. **Aceeași clasă:** REGES › Răspunsuri spunea „niciun răspuns nou” după un mesaj consumat din coada
  REGES și scris; acum spune ce a venit, pentru ce mesaj, cu ce referințe și dacă s-a păstrat. Două citiri moarte scoase.
- **C6** Export extracomunitar: „Dovada export (DVE)” era text („acceptă doar da sau nu”); acum DA/NU. **Aceeași clasă:** 8 bife pe care
  serverul le citea și formularul nu le avea (un provizion pe o creanță în faliment ieșea „deductibil 0%”, acum 100%), 3 cu „Da”
  preselectat, una opțională — toate cerute explicit, cu „— alege —”. `puritate` (aur) = număr.
- Rămân 33 de chei opționale fără câmp în formularele Operațiunilor — ratchet; care intră în ecran e decizie de produs.

## 07.10.2026 — Cele 33 de chei: fiecare fapt fiscal cerut explicit în Operațiuni (comanda Costin)

Decizia și încadrarea fiecărei chei: DECIZII 07.10.2026 („Cele 33 de chei”). Gărzile: GARZI 07.10.2026.

- 31 din cele 33 de chei citite de server fără câmp au intrat în formulare (conturi ale notei, linii, baza diurnei, creditul de
  sponsorizare, regimul aurului și al turismului); 2 rămân în afara ecranului, cu motivul.
- Au intrat și ramurile care nu se vedeau: turism normal și intermediar, aur-monedă, calculul plafonului de diurnă.
- Aceeași regulă pe tot registrul: niciun select nu mai vine cu o opțiune aleasă (36 veneau), câmpurile al căror gol era un implicit
  al serverului sunt obligatorii, dobânda la plata creditului și sursa bacșișului distribuit se pot da.
- Probat: plata creditului cu dobândă neangajată -> 666 = 5121 și comision 627; bacșișul distribuit în numerar -> 462 = 5311 (era 5121);
  moneda de aur -> scutită; turism intermediar 300 cu TVA -> 247,93 + 52,07.

## 07.10.2026 — Ecranele scrise de mână: niciun fapt fiscal ales de ecran (comanda Costin)

Decizia și clasificarea celor 82: DECIZII 07.10.2026 („Ecranele scrise de mână”). Gărzile: GARZI 07.10.2026.

- 59 de liste care alegeau în locul contabilului pornesc acum cu „— alege —”, iar trimiterea fără alegere se refuză lângă câmp:
  formularele manuale ale declarațiilor, emiterea (moneda, țara, tipul operației, documentul), eTransport, tipul firmei, S1005/S1003,
  casa, RIP, codul CM, salariații (norma, contractul, suspendările, tichetele cadou), registrul PF.
- Formularele declarațiilor nu mai pornesc cu răspunsuri în stare (D230 „Un an”, D208 „Teren”, D110 „Regularizare”, D318 „DE”/„A” …).
- Probat: casa fără categorie -> refuz lângă câmp; cu categorie -> dispoziția și nota 5311 = 4111. Selecturi alese la deschidere pe 23
  de ecrane: 54 -> 9 (rămase = valori salvate).
- Decizii deschise: destinația TVA pe linie (conflict DS), implicitele din schemă (Date firmă), input-urile precompletate.

## 07.10.2026 — Lotul 07.10 B, frontul B: sitemap-ul (comanda Costin)

- Cauza din jurnalele nginx: Google n-a încercat preluarea sitemap-ului după retrimiterea din 05.10 (singurele cereri Google verificate:
  Inspection Tool, 200); serverul răspundea corect. În sitemap era un URL redirecționat (`cote-tva-2025`).
- Reparat: index de sitemap-uri `https://iconta.eu/sitemap-index.xml` (pagini + ghiduri pe bucăți de 1.000), indicat de `robots.txt`;
  ghidurile redirecționate scoase din sitemap și din cuprins.

## 07.10.2026 — Lotul 07.10 B, frontul A: preselecția corectată (comanda Costin)

Supersedează, pe partea de preselecție, intrarea „Ecranele scrise de mână” de mai sus (PIVOT în DECIZII 07.10.2026, „frontul A”).

- Emiterea revine precompletată vizibil: moneda RON, țara DEDUSĂ din CUI (DE123456789 -> DE, CUI numeric -> RO), operațiunea normală,
  factura. Moneda facturii recurente: RON. Destinația TVA pe linie: „taxabilă”. D318: cererea inițială.
- Conturile din Operațiuni vin precompletate cu sugestia standard (5124, 4111, 371, 707, 301 …); golite, se refuză („Câmp obligatoriu:
  Cont bancă”).
- 13 bife care răspundeau „Nu” în locul omului devin întrebări Da/Nu cu „— alege —”: funcția de bază (venea bifată), declarația pentru
  copii, scutirea de contribuția minimă; CM — continuare, spitalizare, program național; TVA la încasare la furnizor; acordul D177;
  e_int D398; RIP / cota forfetară / CAS-CASS străinătate la D212.
- Declarații: D204 forma de organizare și D208 modalitatea de transfer (plecau „1” fără câmp) se aleg; D204 categoria nu mai vine „1”;
  D216 cota de deținere nu mai vine „0.3” (era cota impozitului); D318 moneda nu mai vine „EUR”; D398 moneda e fixă, EUR (prin lege).
- Date firmă: exceptarea AMEF și înregistrarea art.317 n-au implicit; nealese, se cer o dată, la prima chitanță fără factură / D394 cu
  chitanțe fără cotă, respectiv la D301. Pe baza de test: 28 de firme cu AMEF și 27 cu art.317 au devenit „neales”.

## 07.10.2026 — Lotul 07.10 B, frontul C: retestul 07.10 (comanda Costin)

- Coada: contarea și ieșirea din stoc ale aceleiași facturi sunt un singur element și pentru elementele vechi (F1A3 fusese creat înaintea
  grupării); cele 4 note ale unui NIR — un element; o plată legată de factură rămâne documentul ei.
- Notele derivate (factură, stoc, NIR, casă, extras, chitanță, stat de plată, raport Z, amortizare) nu se mai editează din Registrul-
  jurnal: refuzul spune unde se corectează. „Recontabilizează statul” / „Contabilizează” factura înlocuiesc nota respinsă și o trimit
  din nou la validare.
- NIR-ul urmează metoda de stoc a firmei: la cantitativ-valoric intră la cost (371=401, 4426=401), fără 378/4428 și fără preț de raft,
  iar stocul îl arată imediat; articolul se alege din listă sau se creează explicit; furnizorul din ANAF; NIR-ul salvat se deschide.
- Ecran: „plătitor TVA” revine după restaurarea ciornei; linia fără articol e informare, nu eroare; trimiterea la validare și
  respingerea / validarea se confirmă vizibil; butonul Respinge din fereastra de motiv nu mai pare dezactivat; cifra de pe clopoțel
  nu mai acoperă iconița.

## 07.10.2026 — Lotul 07.10 B, închiderea (după publicarea C, `b572089b`)

- Producția: `core.migrare_grup_coada` rulat după publicare (backup al cozii `~/backups_db/iconta_v2_coada_pre_grup_20261007_2000.dump`):
  8 elemente legate de documentul lor — F1A3 (11385/11386) -> `factura-49`; NIR 1 (11388–11391, la validare) -> un singur
  document `nir-1`; statul 11/2026 (11383/11384) -> `nota-2`.
- Publicarea C: GitHub a răspuns „Internal Server Error” la push (ambele depozite, chiar și pentru un commit deja publicat — problemă
  a serverului, githubstatus „All Systems Operational”); a doua încercare a trecut; sentinelele scoase după four-way închis.

## 07.10.2026 — „Deciziile 07.10” + retesturile 07.10 (F1 după-amiază, F5 seara) — un singur lot, o singură poartă

- D1: metodele de stoc nesuportate (cantitativ-valoric la preț de vânzare, FIFO) apar „nesuportat încă” și se refuză la salvare;
  restanța e test de datorie.
- D2: NIR-ul legat de factura primită (global-valoric) scrie numai adaosul și TVA neexigibilă; costul trebuie să fie al facturii;
  formularul cere „fără factură” sau factura; factura legată nu se mai șterge.
- D3: raportul Z la cantitativ-valoric intră ciornă și nu se validează fără descărcarea pe articol (ieșire / rețetă legată de Z) sau
  declarația „fără marfă din stoc”; ecranul Raport Z are secțiunea de descărcare.
- D4: salariatul pe API și la import cere norma, funcția de bază și scutirea de contribuția minimă (rândul fără ele se refuză numit);
  modelul CSV și previzualizarea le arată.
- D5: seria chitanței nu mai vine „CH” din oficiu: se cere la prima chitanță, se scrie în Date firmă.
- R1: respingerea unui document cu mișcare de stoc o stornează în fișă (în roșu, cu valoarea ei); NIR-ul respins apare „respins” cu
  motivul și se reface; factura respinsă se reface cu „Contabilizează”. Pe F1, NIR 1 nu avea mișcare în fișă — stocul rămâne 116 /
  5.900,00 (raport §6).
- R2: titlul documentului din coadă e scurt: „NIR nr 1 din 07.10.2026 · DANTE INTERNATIONAL SA · 4 note”, la fel în confirmare.
- S1: prime, sporuri, ore suplimentare pe salariat și lună — în brut, CAS, CASS, impozit, D112 (validat pe DUK), nota de salarii, pe
  fluturaș distinct; facilitatea de la minim cade când venitul realizat (cu prime și CM) trece de plafon. Pe drum: statul nu trecea
  cadoul taxabil, nota nu trecea funcția de bază — aliniate, cu gard.
- S2: „Salariu — de la” pornește cu prima zi a lunii lucrate.
- S3: recontabilizarea / retrimiterea identică cu nota respinsă cere confirmare; cardul din coadă spune „retrimisă după respingere”,
  motivul și dacă s-a schimbat.
- S4: notificările „de validat” se rezolvă singure când elementul e validat / respins / înlocuit; clopoțelul le arată rezolvate.
- Facilitatea de la salariul minim: condiția „venit realizat ≤ plafon” (OUG 89/2025 art.III lit.b) se aplică acum și în luna cu
  mărire de salariu; un salariat mărit la mijlocul lunii peste plafon nu mai primește facilitatea proratată pe luna aceea.
- Contrast: textul secundar în gri deschis (ora notificărilor, rapoarte, ghid) trece pe griul de text (DS cap.15 v2.80).

## 08.10.2026 — Ziua în care lotul „Deciziile 07.10” a ajuns în producție

**Pentru contabil, ziua a schimbat ceva:** lotul scris pe 07.10 (D1–D5, R1–R2, S1–S4, intrarea de mai sus) a ajuns în aplicația din
producție la 03:14 (commitul `876e87a2`, four-way închis), iar baza de producție a fost migrată după backup
(`~/backups_db/iconta_v2_pre_decizii0710_20261008_0218.dump`). Ce vede contabilul de azi:

- **Chitanțe**: niciuna din cele 5 firme nu mai are seria „CH” din oficiu (F1 o avea fără nicio chitanță emisă); prima chitanță cere
  seria în Date firmă, la „Chitanțe”.
- **Stocuri (F1, cantitativ-valoric)**: NIR 1, respins pe 07.10, apare „Respins la validare” cu motivul și „Refă NIR-ul”. Stocul Marfa A
  rămâne **116 buc / 5.900,00** — NIR 1 n-a avut niciodată mișcare în fișă, deci n-a avut ce storna (cifra „105 / 5.350,00” din retest
  așteaptă confirmarea lui Costin). Intrarea NIR 2 e legată de NIR-ul ei.
- **Coada și clopoțelul**: titlurile documentelor sunt scurte (document · partener · număr de note — 12 elemente actualizate);
  notificările „de validat” ale NIR 1 / NIR 2 și ale notelor F5 #3 / #4 apar „rezolvată: respinsă / validată”, iar „Nota #3 … a fost
  respinsă” (F5, înlocuită de #4) apare „rezolvată: înlocuită” — rezolvată pe producție după migrare, cu funcția deja publicată, după un
  al doilea backup (`iconta_v2_post_migrare_decizii0710_20261008_0315.dump`). Rămâne activă, corect, „NIR 1 a fost respins” (F1, de refăcut).
- **Salarii (F5)**: statul de plată are „Prime, sporuri, ore supl.” pe fiecare salariat (nicio valoare introdusă încă); „Salariu — de la”
  pornește cu ziua 1 a lunii lucrate.
- **Nimic nu s-a recalculat retroactiv**: nicio notă, nicio declarație depusă și nicio cifră existentă nu s-a schimbat (stornările:
  0; elementele de salariu: 0).
- **Ce nu s-a putut lega**: patru notificări din 06.10 (44, 45, 46, 48) n-au id de element (dinaintea legăturii) — rămân fără stare,
  toate citite.


## 08.10.2026 — „Deciziile 08.10”: răspunsurile lui Costin la §6 al lotului „Deciziile 07.10” — un lot, o poartă, registrele în același commit

Comanda (verbatim în DECIZII 08.10.2026) a răspuns la cele trei decizii deschise și a adăugat două: F1 confirmat (116 / 5.900,00, fără
stornare fabricată); D2 în ordinea inversă; verificarea mesajului înaintea pytest; notificările fără element; registrele în commitul lotului.

- **NIR „fără factură”, apoi factura (global-valoric)**: contarea facturii de marfă (371) de la un furnizor cu NIR nelegat nu mai trece
  tăcut. Pe orice drum (Contează din Istoric facturi, Validează din SPV, Contabilizează facturile din controlul fiscal) apare caseta
  „NIR-ul acestei livrări”, cu NIR-ul de același cost propus; „Leagă” scrie stornarea în roșu a costului NIR-ului (371=401 și 4426=401
  cu minus, documentul = NIR-ul), „Altă livrare” contează normal și o consemnează. Măsurat pe probă: înainte 371 D 1.350,00 / 401 C
  1.331,00 / 4426 D 231,00 și K 0,091780; după 800,00 / 665,50 / 115,50 și K 0,168129 — aceleași solduri ca ordinea directă. D406
  cu liniile în roșu: valid pe DUK. La cantitativ-valoric aceeași clasă rămâne deschisă (decizie cerută, datorie strictă).
- **Poarta**: `commit-msg` verifică întâi mesajul și abia apoi pornește suita (mutată din `pre-commit`); un mesaj greșit costă
  secunde, nu ~55 de minute.
- **Clopoțelul**: notificările de acțiune fără element primesc „rezolvată: elementul nu mai există”; baza nu mai primește altele
  (`notificari_element_ck`), iar „a fost respinsă” a unei declarații se rezolvă când declarația intră din nou în coadă.
- **Găsit apăsând (proba de browser)**: după „Contează”, rândul facturii rămânea „Contează” — butonul-rând era aplatizat la text de
  blocarea din timpul scrierii (`api.js`), din codul vechi. Reparat în mecanismul unic (45 de butoane cu elemente, 10 fișiere), cu gard
  în browser și regula în DS cap.1 (v2.81). Odată rândul întreg, axe a văzut „Contează” la 4,13:1 pe rândul zebră — linkul de acțiune
  din listele zebră folosește acum albastrul închis al DS (5,55:1), cu gard (DS cap.15 v2.81).
- **Registrele** (PREDARE, ISTORIC, DECIZII, GARZI, TESTE) intră în commitul care conține această intrare; SHA-ul lui, four-way-ul și
  migrarea pe producție sunt în raportul turei.

## 08.10.2026 — „Deciziile 08.10”, continuare: retestul de dimineață, controlul fiscal, balanța pe lună, registrul MF (același lot)

Opt mesaje Costin în aceeași zi, toate în același lot și același commit (verbatim în DECIZII 08.10.2026).

- **Statul și ciorna veche (F5)**: contabilizarea înlocuiește ciorna nevalidată cu alte sume cu nota statului de acum; ciorna #1 de pe
  producție se tratează la fel, după publicare. CAM-ul pe salariat include elementele variabile (124 în loc de 113 pe probă).
- **Coada și refacerile**: elementele vechi își primesc documentul, deci NIR-ul refăcut arată „retrimis după respingere”; „Refă
  NIR-ul” vine cu articolul și cu 10 / 55,00; NIR-ul respins și refăcut e o singură linie „Respins · înlocuit de NIR nr …”.
  Clopoțelul își păstrează pictograma (aceeași cauză ca butonul aplatizat). Titlul cozii spune ce conține.
- **Facturi și chitanțe**: „încasată / încasată parțial: X din Y / neîncasată” pe factură și în Istoric facturi; refuzul seriei duce la
  câmpul seriei; nota chitanței spune ce factură stinge, iar detaliul notei are Validează / Respinge.
- **Declarații**: D300, D394, D390 nu intră în coadă când TVA-ul lor nu se potrivește cu 4427 / 4426 (F1 10/2026: blocat, 4426 −241,50 —
  TVA din NIR fără factură, decizie cerută); D406 nu intră când GeneralLedgerEntries ≠ rulajul balanței (F1: −6.953,00 = cele două
  ciorne de bancă); notele de stocuri au jurnal propriu; „[object Object]” a dispărut; rezumatul stă în „Rezumat”, nu în
  „Avertismente” (și la D301, D406). Contul din afara planului legal (731–738, semănate de șablon) poartă avertisment.
- **Control fiscal**: restanțele de la luna preluării (F1: 32 -> 0, cele 32 separat), „depusă în afara iConta” cu recipisă, „nedeclarat”
  în loc de „diferă de contabilitate” când nimic nu e depus, „de urmărit” pe 30 de zile (F1: 0 -> 5), cardul recalculat imediat după
  orice scriere.
- **Balanța**: cinci egalități (sold inițial, sume precedente, rulajele lunii, total sume, sold final); rulajele lunii = notele din
  Registrul jurnal pe lună (F2 octombrie: 7.750 -> 0, cele 7.750 la „sume precedente”), pe ecran și în PDF (A4 culcat).
- **Mijloace fixe și închiderea lunii**: registrul arată amortizarea înregistrată (F2: 2.400), diferența (1.800) cu lunile lipsă
  (01–08/2026; 02–12/2025 sunt în soldul preluat), durata, codul din catalogul HG 2139/2004 și planul lunar; cardul „Închidere lună”
  (Zilnic) arată ce oprește închiderea — inclusiv amortizarea neînregistrată — și semnalează 581 cu sold. „C&D” cere «Poate
  valida». Balanța, Mijloacele fixe și Declarațiile se deschid late.
- **Găsite pe drum și reparate pe clasă**: SQL scris direct în use-case (mutat în repository, prins de gardurile P7); soldul inițial al
  amortizării citit din planul de conturi (0) în loc de soldurile inițiale (prins la mutație); `destinatie_cd` brut în registru (prins de
  ratchet-ul P7, extins pentru corpurile extrase într-un ajutor); scanerul 1b citea chei inexistente ale balanței.
- **Găsite de proba de browser, la final**: „Salvează” fără dată ștergea formularul „depusă în afara iConta” — mesajul de stare rescria
  containerul; reparat în mecanismul unic (orice container cu câmpuri își primește mesajul într-un copil), cu gard în browser. axe pe
  Balanță: verdele „● se închide” pe rândul zebră la 4,12:1 (și înainte de lot) — zebra tabelelor folosește acum verdele închis (4,53:1).

## 08.10.2026 — „Deciziile 08.10 §6”: NIR-ul fără factură pe 408, luna preluării în Date firmă, R36 — evidența e ce a validat un om

Răspunsul lui Costin la §6 al lotului „Deciziile 08.10” (verbatim în DECIZII 08.10.2026), cu prioritate față de registrul de parametri
fiscali. Un lot, o poartă, registrele în același commit (commitul care conține această intrare).

- **NIR fără factură** (pct.1–3): NIR-ul scrie datoria pe 408 și TVA-ul pe 4428.01; factura legată închide 408 și trece TVA-ul în 4426
  odată cu ea. Merge acum și la cantitativ-valoric, fără a doua intrare în stoc (datoria din 08.10 închisă). Diferența de preț intră în
  luna facturii: 378 la global-valoric; la cantitativ-valoric ajustare de valoare în fișă (CMP nou) sau 607 pentru marfa deja vândută.
  NIR-ul din exercițiul trecut se propune cât timp 408 e deschis, fără nicio scriere în exercițiul lui. NIR-urile vechi (F1: 2 și 3) se
  leagă prin stornare, ca înainte.
- **Poarta D300** compară cu 4426: NIR-ul singur R27_2 0 = 4426 0; după factură 116 ↔ 115,50. D406 cu NIR + factură: **valid** pe DUK.
- **Luna preluării** (pct.4): câmp în Date firmă, cu propunerea alături (F3 -> 06/2026, măsurat pe producție), refuz lângă câmp după
  luna primei note, jurnalizat; Control fiscal numără de la ea.
- **R36** (pct.6–7): amortizarea, bonul aprobat și raportul Z tastat se scriau direct validate — acum intră ciornă; a doua generare
  înlocuiește ciorna nevalidată, cea validată nu se atinge (și la descărcarea GV). Balanța arată numai validatul, iar ciornele apar cu
  indicator (ecran și PDF). Porțile D300/D394/D390/D406 avertizează, nu blochează, când perioada are ciorne.
- **Găsite pe drum și reparate pe clasă:** re-contarea după respingere; ajustarea din D406 Stocuri și din refacerea stocului; analiticul
  cu punct în D406 (pe sintetic, ambele căi); semnalul fals pe 4428 la global-valoric; 4428 debitor lipsă din creanțele bilanțului;
  refuzurile din Date firmă fără câmp. **Rămas, decizie cerută:** creditorul 4428 numărat de două ori în bilanț (datorie strictă).

## 08.10.2026 — „Retest 08.10”: deciziile la §6 ale lotului „Deciziile 08.10 §6” + constatările retestului 4–21 (un lot, o poartă)

Comanda Costin (verbatim în DECIZII), 24 de puncte, 17 operații date înainte de execuție; un commit, registrele în el.
- **Bilanțul 4428** (pct.1): TVA-ul din prețul de raft trece pe analiticul 4428.02 (NIR GV, descărcare, K); bilanțul îl scade numai la
  rd.05, nu-l mai numără la datorii; datoria strictă din lotul trecut e închisă. Migrarea mută liniile 371/4428 (producția n-are niciuna).
- **Coada** (pct.3): „De validat” validează mai multe note deodată, fiecare pe drumul aprobării ei.
- **NIR 2 și NIR 3 F1** (pct.4): note de refacere pe 408 / 4428.01 (stornare în roșu + forma nouă), ciorne de validat; poarta D300 se
  face verde după validarea lor.
- **D406 / D394** (pct.5–6): liniile facturilor își arată suma pe sensul ei; totalurile facturii pe fiecare cotă (XML); D394 citește
  numărul fără cifrele seriei (F1A3 -> 3) și semnalează factura fără serie. DUK: D406 și D394 F1 10/2026 valide.
- **Control fiscal** (pct.7–10): contoarele numără fapte (restanțe / de urmărit / …), nu culoarea; D100/D205 2025 la „înainte de
  preluare”; grupul pliat cu „Marchează toate ca depuse de contabilul anterior”; marcarea se modifică și se anulează, fără salt sus.
- **Închiderea lunii** (pct.11–12): luna în curs nu se mai poate închide (perioada și evidența facturilor, aceeași regulă); „Blochează
  luna” inactiv pe blocaje; un singur loc, cardul; semnal nou: 401 cu sold debitor (F2: 500).
- **Mijloace fixe** (pct.13): acțiunile într-un meniu, PIF pe un rând, lunile lipsă în intervale („8 luni: 01–08/2026”).
- **Limba ecranelor** (pct.14): ~200 de texte ale serverului și 17 ale ecranelor rescrise (diacritice, fără cod, fără majuscule);
  gardul nou vede și rolurile pe care cele vechi nu le vedeau.
- **D406 / D394 pe ecran** (pct.15–16): fără suprapuneri și goluri (regula ferestrei largi, pe clasă); „Rezumat” apare (validarea și
  generarea întorc aceleași câmpuri).
- **731–738** (pct.17): scoase din șablon și din cele 5 firme de producție (nefolosite).
- **PDF balanță / nota chitanței / luna preluării** (pct.18–20): CUI + momentul generării în antet; descrierea notei de casă spune
  felul, documentul, ce stinge și partenerul; „Luna preluării” vine completată cu propunerea.
- **C&D** (pct.21): proba pe asistent fără «Poate valida» — buton inactiv, API 403, nimic scris.
- **Rămas, decizie cerută:** descrierea notei 118 F1 (validată) — se păstrează sau se rescrie.

## 09.10.2026 — „Retest 2”: retestul în aplicație al lotului „Retest 08.10” (20 de puncte, un lot, o poartă)

Comanda Costin (verbatim în DECIZII), 17 operații date înainte de execuție; un commit, registrele în el.
- **Limba ecranelor, judecată pe ecran** (pct.2): instrument nou care citește textul afișat în browser (160+ ecrane: cardurile celor
  patru firme de test, desktopul cabinetului, D300/D390/D394/D406 generate) și îl judecă (cod, diacritice dintr-un lexicon derivat din
  corpusul legislativ, majuscule, sume, date, perioade, acord, prescurtări, jargon); tot ce a prins, rescris. Gardul de sursă vede și
  mesajele excepțiilor, șabloanele și „LipsĂ”. Rândurile D300/D101 se numesc cu rândul formularului (D300 numea greșit rândurile ≥ 17);
  diferențele porților de reconciliere în cuvinte; notele 121/122 rescrise și retrimise la validare.
- **Control fiscal** (pct.1, 3, 9, 10): „Înainte de preluare” rămâne deschis și pe rândul atins; contoarele pe o regulă; F3 neplătitor:
  „nu se aplică” la D300 / D390 față de D300, restanțele D390 numai pe lunile cu operațiuni; termen și perioadă pe rândurile dinaintea
  preluării. Pe drum: verificarea TVA la trimestrial genera decontul pe luna din mijloc (R18) — acum pe decontul trimestrului.
- **Casă** (pct.4): o operațiune cu notă validată nu se mai șterge — se stornează (operațiune inversă + notă ciornă în roșu).
- **Mijloace fixe / Registru jurnal / Note de validat** (pct.5–7): amortizarea până la ultima lună încheiată; totalurile pe validat,
  ciornele separat; rulajul notei în loc de „total 0,00”.
- **Închidere lună / ciorne / plan de conturi** (pct.11–13): declarația nedepusă cu termen în lună = semnal; „Notele tale în ciornă” în
  „De validat”; ecranul „Plan de conturi” (căutare, analitice sub sintetic, adăugare, contul folosit nu se șterge).
- **Formate și surse** (pct.14–16): date românești în D406 / Casă / Bancă, jurnalele D406 în cuvinte, perioadele în trei forme,
  confirmările scurte, „1 partener”; D394: o factură cu două cote se numără o dată la cota cu TVA-ul mai mare (OPANAF 2194/2025 pct.5) —
  ecranul o spune; antetul PDF: „Cod TVA RO…” la plătitor.
- **Rămas, decizie cerută:** pct.8 (nereprodus pe cabinetul de test); cele două întrebări ale lotului trecut (nota 118, mesajele
  generatoarelor manuale).

## 09.10.2026 — Neconformitate prinsă la migrarea „Retest 2”: nota de corecție respinsă storna stocul NIR-ului contat

- **Producție, migrarea „Retest 2”** (rulată de Costin după backup): coloana `casa_operatiuni.storno_de` pe 5/5 scheme — ecranul Casă,
  căzut între restartul lui d0abd48f și migrare, merge din nou. Notele 121/122: descrierea rescrisă; retrimiterea refuzată.
- **Refuzul a arătat un defect**: respingerea notelor de refacere 121/122 (numai pentru descriere) stornase în fișa de magazie NIR 2 și
  NIR 1, contate (notele 114–117 validate). Reparat în cod (DECIZII 09.10.2026, „Neconformitate: nota de corecție …”): stocul în
  evidență nu se mai stornează la respingere; NIR-ul contat nu mai apare „respins” și nu se mai reface. Două teste noi, șase mutații roșii.
- **Rămas, decizie cerută:** reparația celor două rânduri de stornare de pe tenant_049 și gardul „migrarea înainte de restart”.

## 09.10.2026 — Registrul deficiențelor și plasa împotriva regresiilor (comanda Costin)

- **Registrul `DEFICIENTE.md`**: cele 187 + N1–N18 ale lui Costin, plus 188 (rândurile bilanțului) și 189–198 (găsite la verificare).
  Fiecare număr verificat pe aplicația de acum: 161 rezolvate (fiecare cu test de capăt la capăt în browser, dovedit prin mutație),
  4 parțiale, 11 nerezolvate, 8 „nu se aplică”, 19 neverificate; N-urile: 12 reale, 1 nereală, 5 neverificate.
- **Plasa**: cele 167 de teste intră în poartă — aplicația pornește din ce se comite, pe baza de test; o deficiență rezolvată care
  se strică oprește publicarea.
- **Gardul migrării**: producția nu mai repornește pe un commit a cărui migrare n-a rulat (pățit cu ecranul Casă, dimineața).
- **Regulile de fond în bază**: nota validată nu se mai modifică / șterge; luna blocată nu mai pierde note; nota nu se validează fără
  document; stocul unui document contat nu se desface fără notă de corecție.
- **Cifrele de referință F1–F5** (balanța, D300, D394, D406, D112) exportate pentru verificarea lui Costin.
- **Rămas la Costin**: rularea scriptului tenant_049 (deblochează și restartul), aprobarea cifrelor, ordinea reparațiilor.
- **Pe drum (09.10, seara):** forma finală a regulilor din bază, după suita completă — nota validată se poate construi complet în
  tranzacția care o creează, apoi nu se mai atinge; documentul se cere la validare. Dezlegarea unei plăți VALIDATE de factura ei e
  acum refuzată (corectura: stornare). Reparat și un defect al cozii (deficiența 199): cardul unui document retrimis putea spune greșit
  că notele s-au schimbat.
