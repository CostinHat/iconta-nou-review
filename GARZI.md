# GARZI.md — registrul gardurilor

**Ce e:** indexul mecanismelor care prind defecte automat, pe categorii de eșec.
**De ce:** gardurile au apărut reactiv, după fiecare bug, în patru locuri diferite. Fără un
index, nimeni nu poate răspunde la *„câte mai lipsesc"* — iar un gard lipsă e invizibil
exact ca defectul pe care ar fi trebuit să-l prindă.

**Se actualizează** în același commit cu gardul livrat. Registru stale = fals sentiment de
acoperire.

---

## Ce înseamnă „gard"

Un mecanism e gard doar dacă îndeplinește toate:

1. **Rulează automat** — în suită, în verificator, sau la runtime. Un document nu e gard.
2. **Pică pe defect** — dovedit prin mutație: strici lucrul, gardul devine roșu.
3. **Trece pe cod corect** — un gard cu fals-pozitiv se dezactivează și moare.
4. **Spune cauza** — „a picat ceva" nu ajută; mesajul poartă fișierul, valoarea, motivul.

Punctul 2 nu e formal. Pe 27.07 o gardă a „picat pe mutant" în timp ce crăpa cu `NameError`
— pica pe orice, deci nu testa nimic. **Mutația verifică MOTIVUL eșecului, nu doar eșecul.**

---

## Unde trăiesc gardurile

| Loc | Ce acoperă | Când rulează |
|---|---|---|
| suita pytest (1322 teste, 133 fișiere) | logică, schemă, semnături, contracte | la dev, înainte de commit |
| `verificator_conformitate.py` | Design System, frontend (28 gardieni) | la dev, TOTAL 0 obligatoriu |
| `core/verificatoare.py` | echilibru notă/balanță, TVA pe cotă, trezorerie | în aplicație, pe date reale |
| `core/control_incrucisat.py` | D112/D300/D390 vs evidență, cotă TVA | în aplicație, semafor |
| `core/cron.py` | eșecul joburilor de fundal | în producție, la fiecare rulare |

---

## Categoriile de eșec

Legenda stării: **ACOPERIT** / **PARȚIAL** / **LIPSĂ**

### 0. Mascarea erorii (transversal — cauza rădăcină)
**Eșec:** `except` care întoarce default gol; eroarea nu ajunge nicăieri; un query rupt
produce zero rânduri, iar declarația iese validă structural și goală.
**Stare: ACOPERIT.**
- `core/d406.py` — 6 măști scoase (27.07), zero rămase. Fiecare cauză cu mesajul ei.
- `d112/d300/d390` — `except: return 0` scoase (27.07), regula în `numere.numar_fiscal`.
- Rămân 2 în `core/jurnal_api.py:84,141` — pe scrierea în `ai_corectii`. Clasă mai blândă
  (nu strică nota contabilă, pierde tăcut date de învățare), dar tot tăcere.
- ACOPERIT: `core/test_masti.py` (27.07) — scan AST pe tot repo-ul; orice `except` cu corp
  mut peste un query pică. Regula: **înghițirea e permisă, tăcerea nu** — handlerul trebuie
  să spună ce a eșuat (`observare.esec_secundar`) sau să poarte marcajul `# MASCA MOTIVATA:`
  cu explicația. Dovedit prin mutație pe cod real.
- Cele 15 măști peste query din `main.py` și `jurnal_api.py` (audit_log, metrici, precompletare
  ANAF, învățare AI) sunt acum zgomotoase. Nu li s-a schimbat comportamentul: efectul secundar
  tot nu oprește operația principală — dar lasă urmă.
- LIMITĂ DECLARATĂ: acoperă doar măștile peste query. Cele peste conversii numerice sunt
  tratate separat (`numere.numar_fiscal`). Nu verifică dacă eticheta e corectă.

### 1. Intrare date
**Eșec:** câmp lipsă → NULL → 0; import duplicat; valoare cu virgulă zecimală devenită 0;
cotă TVA inexistentă la data documentului; semn inversat.
**Stare: PARȚIAL.**
- ACOPERIT: `core/numere.numar()` — sursă unică de parsare (extrasă din 9 copii pe 15.07;
  6 transformau `(200)` în 0.0 tăcut). `numar_fiscal()` pentru valori care intră în
  declarații: absența e legitimă, invalidul e eroare.
- ACOPERIT: F184 conformitate cotă TVA la dată; F185 coliziune CUI; audit de preluare firmă.
- LIPSĂ: gard care cere NOT NULL pe fiecare coloană de bani și cheie naturală unică pe
  fiecare tabel de import. Idempotența importurilor nu e verificată mecanic.

### 2. Graniță cod–bază
**Eșec:** query pe coloană/tabel inexistent; drift între schema unui tenant și template.
**Stare: PARȚIAL.**
- ACOPERIT: F165 `core/audit_schema.py` + `test_audit_schema.py` — poartă reală pe DB, cu
  test de mutație negativă. Direcția template→tenant = drift HARD.
- LIMITĂ DECLARATĂ: direcția tenant→template e informativă. Decizie din 22.07 (un whitelist
  ever-growing produce roșu fals). Consecință acceptată: un tabel creat ad-hoc într-un
  tenant rămâne „extra informativ" — cazul `d205_beneficiari`, care s-a dovedit legitim
  (cod mort, zero consumatori).
- ACOPERIT parțial: `core/test_pull_declaratii.py` (27.07) — teste pe `pull()`, granița
  cod↔bază, pe schemă temporară din template cu ROLLBACK. Două clase: `pull` **vede** datele
  care există, și `pull` **crapă zgomotos** când schema nu se potrivește. Cele ~175 de teste
  pe generatoare erau toate pure (`calcul_dXXX` + `build_xml` cu fixturi) — `pull()` nu era
  atins de niciunul, deși acolo au trăit toate defectele din iulie.
- ACOPERIT: `common.cere_coloane` — `SELECT *` nu crapă la coloană lipsă; rândul iese fără
  cheie, `get()` dă `None`, iar absența e tratată legitim ca 0. Dovedit pe D112: cu
  `salariu_brut` redenumită, declarația ieșea cu salarii ZERO (1333 car. în loc de 1890).
  Garda verifică PREZENȚA cheii; valoarea 0 rămâne legitimă.
- LIMITĂ DECLARATĂ: `cere_coloane` verifică rândurile CITITE, deci **o tabelă goală trece**.
  O coloană dispărută pe o firmă fără salariați nu se semnalează.
- LIPSĂ: verificare statică a query-urilor din cod contra schemei reale (`audit_cod_schema.py`
  a fost prototipat local pe 27.07, **nu e pe server**). Ar prinde defectul înainte de rulare.
- LIPSĂ: aceeași gardă la celelalte `SELECT *` pe date fiscale (d394, bilant_api, rip_api,
  stocuri_cv_api, reconciliere_api). Vezi DE_FACUT.

### 3. Calcul fiscal
**Eșec:** cotă/prag greșit, rotunjire greșită, graniță de perioadă — **și bază zero pentru
că intrarea a fost înghițită**.
**Stare: PARȚIAL.**
- ACOPERIT: cotele parametrizate cu data în `common.cota()` (period-aware).
- ACOPERIT: `control_incrucisat.py` — D112 vs rulaj, D300 vs jurnal, D390 vs evidență +
  D300 depus. Trei stări (verde/roșu/**gri**), temei + limită pe fiecare constatare.
- ACOPERIT parțial: regula bazei nule. `d205.genereaza` refuză explicit să emită fără
  beneficiar. La celelalte, `declaratii_api.numar_operatiuni` numără operațiunile, iar ecranul
  pune o **poartă** (DS cap.5 `.caseta-poarta`) înainte de trimiterea în coadă: omul confirmă
  că firma chiar n-a avut activitate. Nu blochează depunerea pe zero (obligație reală), dar
  golul nu mai trece tăcut. `None` = nu se poate număra (d101/d112) → fără poartă.
- LIMITĂ DECLARATĂ: poarta e doar în ecran. `POST /coada` regenerează declarația și n-are
  poartă — un apel direct de API trimite pe zero fără întrebare.
- LIPSĂ: gard care interzice cote literale în cod (azi nimic nu împiedică un `* 0.19`).
- LIPSĂ: teste golden pe cifre calculate de mână din exemplul oficial.
- LIPSĂ: gard de **derivă legislativă** (deschis 31.07.2026). Garda anti-stale a agendei
  (`core/test_agenda.py`) e UNIDIRECȚIONALĂ: prinde codul schimbat sub o bifă (ancoră =
  commit), NU legea schimbată sub un cod care stă — un act care modifică art.77 fără ca
  nimeni să atingă fișierul lasă bifa verde la infinit. Cere: temeiuri structurate
  (act+nr+articol+dată) citibile mecanic, o sursă de adevăr externă pentru „actul X s-a
  modificat după data D", reset al bifei la orice atingere a unui act citat. Fundație
  parțială: `core/temeiuri.py` găsește deja locurile care citează un act; lipsește partea
  care întreabă dacă actul s-a schimbat. Nu se începe acum — clusterele nebifate sunt risc
  prezent. (Poziția cerută pt. DE_FACUT.md, care nu mai există; trăiește aici, în registrul
  gardurilor.)
- ACOPERIT (31.07.2026): temei STRUCTURAT (`common.Temei`: act/nr/an/art/alin/lit/data_in/
  data_out/url) pe toate cotele din `common.COTE` + garda de EXPIRARE pe `data_out`. `cota()`
  RIDICĂ după `data_out` (nu întoarce tăcut valoarea veche) — mecanismul PRINCIPAL de derivă, nu
  un proxy: nu există API legislativ RO fiabil (dovedit repetat). Gard ratchet în verificator:
  orice cotă nouă cu temei string (nestructurat) blochează. Inventar A generat parțial din COTE,
  cu overlay persistent pentru judecățile umane (`genereaza_inventar_a.py` + `INVENTAR_A_OVERLAY.tsv`).
- LIMITĂ REALĂ (rămâne descoperit, 31.07.2026): o schimbare de lege **între `data_in` și
  `data_out`** NU e detectabilă. `data_out` semnalează doar când TRECE valabilitatea DECLARATĂ,
  nu când actul se modifică dedesubt mai devreme decât s-a estimat. Sistemul nu detectează
  schimbarea legii — refuză doar să răspundă cu o valoare expirată; eroarea apare la CALCUL, nu la
  depunere. `estimat=True` marchează `data_out`-urile ghicite (sfârșit de perioadă rezonabilă:
  an fiscal/semestru), unde fereastra nedetectabilă e mai largă. Închiderea ar cere un feed
  legislativ mecanic care nu există — degradează la revizuire manuală periodică ghidată de registru.
- ACOPERIT (01.08.2026): BLOCAJ MOTIVAT pe cote de regula late-start. O cota citita de o functie de
  regula cu `data_in` mai tarziu decat `common.DATA_START_SISTEM` (2025-01-01, podeaua datelor salariale)
  ridica `common.PerioadaIndisponibila` (subclasa ValueError, tag `PERIOADA_BLOCATA`) cand e ceruta pentru o
  perioada din [podea, data_in) - handler-ul global (`main.py`) o arata utilizatorului ca 423 cu mesaj (cele
  4 elemente: ce s-a oprit / de ce / ce se poate face / cine decide), NU ca traceback 500. Gard in verificator
  (`GARD BLOCAJ MOTIVAT`, PRAG 0): probeaza runtime ca fiecare cota de regula late-start produce blocaj motivat,
  nu exceptie bruta. Test: `core/test_perioada_indisponibila.py`. Commit-uri 1d37d3a (mecanism) + 1de6ac9 (gard).
- LIMITA DECLARATA (01.08.2026): calculul salarial NU e disponibil pentru perioade anterioare lui 2026-01-01,
  fiindca plafonul facilitatii (`plafon_facilitate_salariu_minim`) si plafonul tichetelor (`tichet_masa_plafon`)
  nu sunt verificate la sursa pentru 2025 - desi salariu_minim/facilitate exista din 2025-01-01. O adeverinta/
  rectificativa pentru o luna 2025 da mesajul motivat, nu crapa. Se DESCHIDE prin backfill la sursa (candidat:
  OUG 115/2023 pentru plafon), NU prin estimare - nu se inventeaza o valoare. Ramificatie: `tva_redusa`
  (start 2025-08-01) rupe similar `calcul_tva` (cititor subtire, NU functie de regula) pentru facturi pre-
  2025-08 - acoperit de acelasi mecanism central (cota()), dar out-of-scope pentru gardul de reguli.
- ACOPERIT (02.08.2026): **CM4 plafon 12 salarii minime** pe baza de calcul CM (OUG 158/2005 art.10 alin.(1);
  OMS 15/2018 ART.61 + Exemplul nr.5). `_calcul_cm_core` capeaza fiecare venit **LUNAR** la
  `12 * cota("salariu_minim", luna)` INAINTE de mediere (param `venituri_lunare`). GARD MECANIC =
  `test_cm_plafon_traverseaza_schimbarea_sm`: fereastra Apr-Sep 2026 are sm 4050 (Apr-Iun) si 4325 (Iul-Sep) ->
  plafoane 48600/51900 diferite pe luni; **MUTATIE**: cine muta plafonarea pe MEDIA (un singur sm) pica testul
  (media zilnica difera). + `test_cm_plafon_{toate_sub_nu_se_activeaza, o_luna_peste, toate_peste, luni_asimilate_stagiului}`.
- ACOPERIT (02.08.2026): **ziua 15 CM = 75%**. `test_cm_ziua15_este_75pct` fixeaza ziua 15 la 75% (gol de
  redactare art.17(1): lit.b "8-14", lit.c "peste 15"; decizie arhitect favorabila asiguratului); **MUTATIE**:
  mutarea tacita la 65% pica testul.
- **BLOCAJ MOTIVAT (02.08.2026) — plafon CM "salariul minim IN LUNA".** CE S-A OPRIT: nimic la runtime; regula
  "plafon lunar = 12 x sm-in-luna" e APLICATA in cod, dar NEconfirmata verbatim la sursa. DE CE: OMS 15/2018
  Exemplul 5 exemplifica plafonul cu sm **ANUAL** ("pentru anul X = 12 x sm"), din era cu un singur sm/an (claim
  5 GRI); pentru era cu doua sm/an (din 2024) textul nu confirma explicit "in luna". CE SE POATE FACE:
  reconfirmare la sursa (ordin/circulara MS/CNAS pe era cu doua sm/an, sau forma la zi a art.61); pana atunci se
  aplica interpretarea coerenta cu "12 sm lunar" din art.10(1). CINE DECIDE: Costin (arhitect). Consemnat
  DECIZII.md 02.08.
- DATORIE DESCHISA (02.08.2026, art.XI L141/2025): forma pre-01.08.2025 a procentelor CM (art.17(1)) NU e
  implementata (`_VARIANTE_PROCENT_CM` are o singura varianta = forma L141/2025, aplicata inclusiv episoadelor
  cu certificat initial anterior lunii august 2025). Procentele vechi nu-s verificate la sursa -> blocaj motivat,
  `xfail test_datorie_cm_art_xi_regim_initial`.
- ACOPERIT (02.08.2026): **tichete culturale** (Legea 165/2018 cap.V). GARD `test_bilete_valoare_declara_
  toate_tratamentele` (BILETE_VALOARE_TRATAMENT): fiecare bilet de valoare declara EXPLICIT cele 4 tratamente
  (impozit/CAS/CASS/CAM) + sursa plafonului; **MUTATIE**: adaugi un tip nou fara declaratie -> pica. + GARD
  plafon semestrial `plafon_cultural()`: fereastra oct.2025-mar.2026 CONFIRMATA la PRIMAR (04.08.2026, Ordin
  MF/MC 1.574/3.246/2025, MO 900/01.10.2025 - 240 lei/luna, 470 lei/eveniment; era GRI verdict 16 pana la reconfirmare)
  in _FERESTRE_CULTURAL (_CULTURAL_GRI=None), test_plafon_cultural_oct2025_mar2026_confirmat_240_470 +
  test_cultural_db_oct2025_confirmat_insereaza. Progresie 220/450 -> 240/470 -> 250/490. Divergenta esentiala vs etalon:
  culturalul NU are CASS (art.157(2)) - test_cultural_diferit_de_masa_pe_cass.
- ACOPERIT (02.08.2026): **tichete de cresa** (Legea 165/2018 art.19). Tratament = ca CULTURAL (impozit
  10%, FARA CAS/CASS/CAM), in registru BILETE_VALOARE_TRATAMENT (gardul 4 tratamente il acopera). GARD plafon
  `plafon_cresa()` = 450/copil (baza art.19(1) confirmata); indexarea 740 (S1 2026, Ordin MF/MMSS 368/179/2026,
  MO 249/31.03.2026) e CONFIRMATA la EMITENT (mmuncii.gov.ro) + MO-referinta (04.08.2026), dar NEAPLICATA: textul
  operativ al ordinului neobtinut + plafon_cresa n-are mecanism de ferestre datate (ca plafon_cultural) + valorile
  intermediare (710) necercetate. Cap conservator 450, BLOCAT motivat in beneficii_api.seteaza
  (test_cresa_seteaza_peste_plafon_*), NU se aplica 740 tacit (era GRI verdict 17).
  Divergenta CASS vs etalon (cresa fara CASS, art.157(2)) prinsa de registru + test_cresa_in_registru_fara_cass.
- ACOPERIT (02.08.2026): **IMCA - impozit minim pe cifra de afaceri** (CF art.18^1) in d101. Formula
  1% x (VT-Vs-I-A) (negativ -> 0) + prag 50 mil euro + wiring P47 + comparatie P48. GARD prin teste de VALOARE
  (test_imca_formula_1pct, test_datoreaza_imca_prag_50mil_euro) + **proba DUK** (test_imca_d101_duk_valid: d101
  cu IMCA trece DUKIntegrator). MUTATIE: schimbarea formulei/pragului pica testele golden.
- ACOPERIT (03.08.2026): **amortizare fiscala in d101** (CF art.28). Ajustarea fiscal-contabil (P11 amortizare
  fiscala dedusa in P16; P28 amortizare contabila adaugata inapoi in P34) + prag MF 5000 lei (art.28 alin.2b).
  Teste golden cu temei: test_amortizare_ajustare_fiscala_art28, test_mf_prag_amortizabil_5000_art28. DESCHIS
  (subsistem MF, nu d101): modulul MF calculeaza doar amortizare LINIARA; degresiva/accelerata (art.28 alin.5)
  mapate dar necalculate -> xfail test_datorie_mf_metode_amortizare (impact pe amortizarea contabila/D406, nu pe
  d101 care ia amortizarea fiscala ca input).
- ACOPERIT (03.08.2026): **cotele de contributii salariale in D112** (CAS 25% CF art.138, CASS 10% art.156,
  impozit 10% art.78, CAM 2.25% art.220^3) rutate PERIOD-AWARE prin cota() din COTE - eliminate literalele
  hardcodate (0.25/0.10/0.0225) din core/d112.py. Ca la restul COTE: o cota schimbata de lege se modifica intr-un
  singur loc (fereastra de data), nu ramane literal ascuns in urma legii. Value-preserving (golden D112 + DUK
  neschimbate). GARD anti-hardcode prin inspectia sursei functiilor (test_d112_ruteaza_cotele_prin_cote_nu_literale)
  + test de valoare cu temei verbatim (test_cotele_contributii_din_cote_cu_temei).
- ACOPERIT (03.08.2026): **rotunjirea minimului PART-TIME in D112** (A91b). prag_zile/cas_min_pt/cass_min_pt
  foloseau round() BANCAR (half-to-even), iar _d112int ulterior era no-op pe valoarea deja intreaga -> bancarul
  ajungea in B4_*P declarat (prag_zile=1226 -> CAS 306 in loc de 307). Rutate prin _d112int (half-up). GARD: proba
  pe valori reale (test_partime_minim_rotunjeste_aritmetic_nu_bancar) + inspectia sursei pull
  (test_partime_minim_foloseste_d112int_nu_round_bancar). Regula A91b: ANAF cere rotunjire aritmetica pe contributii.
- ACOPERIT (03.08.2026): **impozitul retinut pe dividende in D205** (CF art.97 / Legea 141/2025). Era
  hardcodat 10% in calea auto -> gresit pentru 2026 (16% de la 01.01.2026). Rutat prin cota("impozit_dividend")
  period-aware. GARD: proba DB reala (test_d205_contract_pull_genereaza_perioada: 50000 div 2026 -> 8000) + proba
  DUK valida + inspectia sursei (test_d205_rata_dividend_din_cota_nu_hardcodat). Structura sect_II/tip_venit=08
  verificata la sursa (OPANAF 102/2025, anaf_surse/d205_struct_anaf.txt).
- ACOPERIT (03.08.2026): **rotunjirea sumelor in D205** (regula A91b, aritmetica). d205 folosea deja _i =
  quantize(ROUND_HALF_UP) pe toate sumele (fara round() bancar), dar _i nu era in gardul de identitate
  cross-generator. Adaugat _i in test_rotunjirea_e_identica_intre_generatoare (a==b==c==d) + proba d205-specifica
  (test_d205_rotunjeste_aritmetic_nu_bancar). Fara schimbare de comportament - inchidere gap de acoperire.
- ACOPERIT (03.08.2026): **maparea cotelor TVA pe randurile D300** (structura v12 + proba DUK). Livrari
  21/11/9 -> Rd.9/10/11 corecte. REPARAT achizitii deductibile: 11% era la R74 (=19% legacy, DUK marja 18-20%) ->
  R23 (Rd.25); 9% era la R76 (taxare inversa, pierdut din totalul R27) -> scos din auto + avertisment manual
  (validatorul instalat respinge si R75 din v12). GARD: proba DUK (test_cote_tva_d300_proba_duk_valid) + gard pe
  valori (test_cote_tva_maparea_pe_randuri_d300). DATORIE: 9% deductibil auto (xfail test_datorie_d300_9pct_deductibil_auto).
- ACOPERIT (03.08.2026): **TVA la incasare in D300** (CF art.282/297, OUG 8/2026). Firma pe sistem -> D300
  calculeaza exigibilitatea din DECONTARI (incasari 4111 / plati 401 validate in perioada), suta marita,
  proportional pe plati partiale; taxare inversa exclusa; deducerea amanata la plata. GARD: proba DB reala (factura
  emisa luna 5, incasata luna 6 -> exigibila luna 6) + proba DUK (test_tva_incasare_d300_proba_duk_valid) + gard
  taxare inversa (F3) + gard firma-fara-flag neschimbata. Fara cap 90 zile (eliminat de OUG 8/2026).
- ACOPERIT (03.08.2026): **taxare inversa in D300** (CF art.331, rd.12). REPARAT: R12_ lipsea din allow-list-ul
  manual -> rd.12 (auto-taxare beneficiar) era silentios ignorata. Acum settabila; proba DUK pe decont echilibrat
  rd.12=rd.27 (test_taxare_inversa_d300_proba_duk_valid) + gard anti-drop. GRI reverse-charge D300/D394 INCHIS
  (reconfirmat la sursa: art.331 + structura Rd.12 D300 + campuri bun/tip in structura D394).
- ACOPERIT (03.08.2026): **pro-rata deducere in D300** (CF art.300, regim mixt). d300 aplica pro-rata ca
  AJUSTARE R31_2 (Rd.33), nu scalare directa: R32 dedusa = R28 x pro_rata/100. Corect prin constructie; gardat
  acum cu pro_rata<100 (test_pro_rata_ajustare_deductibila_art300) + gard pro_rata=100 + proba DUK.
- ACOPERIT (03.08.2026): **ajustari/regularizari in D300** (CF art.304/305). REPARAT: R29 (restituiri straini),
  R30 (regularizari taxa dedusa), R35 (sold reportat), R36 (diferente inspectie) lipseau din allow-list-ul manual ->
  silentios aruncate. Acum settabile (R29/R30 -> R32, R35/R36 -> R37); randurile computate raman neschimbate. GARD:
  proba DUK (test_ajustari_d300_proba_duk_valid) + gard anti-drop (test_ajustari_r30_fara_fix_ar_fi_dropped).
- ACOPERIT (03.08.2026) - CLASA: **allow-list manual incompleta = drop tacit** in generatoarele de declaratii.
  Radacina a bug-urilor R12 / R29-R30-R35-R36 / R38-R39-R43-R44 din D300. GARD PE CLASA (nu doar instante): d300
  urmareste cheile manual aplicate si ridica ValueError pentru orice cheie neaplicata; d390/d394 ridica pe tip
  necunoscut (nu mai fac `continue` tacit). d301 respinge tot manual; d112/d406 nu au manual. Teste:
  test_{d300,d390,d394}_manual_*_necunoscut_ridica. Un rand introdus de contabil care nu e in lista STRIGA acum.
- DESCHIS: rotunjirea din D390 e bancară (`round()`), în timp ce D112 documentează că ANAF
  cere aritmetică. Schimbare fiscală — se verifică la sursă. Vezi DE_FACUT.

### 4. Ieșire către autorități
**Eșec:** XML structural valid, semantic gol sau fals.
**Stare: PARȚIAL.**
- ACOPERIT: `core/duk.py` + `test_duk.py`. Trei stări; **eșecul rulării = gri, nu valid**.
  Un XML nevalidat nu se declară valid. Test: niciun validator nu acceptă gunoi.
- ACOPERIT: `test_ruta_valideaza_trimite_an_si_luna` — leagă ruta de semnătura cerută de
  validatorul SAF-T. Fără el, validarea D406 a fost gri permanent luni de zile.
- ACOPERIT: reconcilierea linii-antet la D406 (divergență între două surse ale aceleiași
  facturi = eroare).
- LIPSĂ: totalurile din XML reconciliate pe **a doua cale de calcul**, independentă.
- LIPSĂ: snapshot de regresie pe fixturi înghețate.
- **DUK validează STRUCTURA, nu conținutul.** Nu e gard de conținut și nu se tratează ca atare.

### 5. Izolare tenanți
**Eșec:** `search_path` nesetat; constrângere nescopată la `current_schema()`; job de
fundal pe tenantul greșit; **IDOR** (id tenant din URL neverificat contra userului).
**Stare: ACOPERIT (mecanism + probă dinamică + gard structural).**
- Mecanismul: `db.get_conn(schema)` cu `SET LOCAL`; `auth_api.schema_tenant(uid, tenant_id)` →
  `None` fără acces → 404. Model API-key: `_api_schema` scopat pe `accounting_firm_id`.
- ACOPERIT (probă DINAMICĂ, 31.07): `core/test_izolare_incrucisata.py` — doi tenanți sub cabinete
  diferite, acces încrucișat real prin HTTP (5 rute) → 404, zero date; mutație `schema_tenant`
  bypass → leak → testul pică. + măsurat: `from core.db import` = 0 module (proba e completă).
- ACOPERIT (gard STRUCTURAL, 31.07): `verificator_conformitate.py` — orice rută cu `{tenant_id}`
  în path care deschide `get_conn` TREBUIE să rezolve accesul (schema_tenant SAU resolver pe
  accounting_firm_id/user_tenants). CODEBASE-WIDE (`@<var>.<verb>` în tot `.py`, nu doar main.py
  @app) + META-GARD pentru APIRouter nemontat. Baseline 0. RED dovedit (gol în alt fișier; router
  nemontat).
- LIMITĂ DECLARATĂ a criteriului: gardul acoperă `{tenant_id}` în **PATH**. Rute care iau
  `tenant_id` din **BODY/query** (POST `/coada`, POST `/declaratii/{tip}`) NU sunt acoperite de
  criteriul structural — azi rezolvă accesul (`/coada`→`_schema_sau_404`, declaratii→schema_tenant,
  verificat manual 31.07), dar gardul nu le impune. Resolveri pe 2 niveluri de indirectare:
  neacoperiți (măsurat: 0 azi).
- LIMITĂ (conexiuni brute): 1 conexiune brută în afara helperului (`sinteza_zilnica.py`, citește
  doar `public.*`) — nepăzită mecanic.

### 6. Acces
**Eșec:** rută fără dependență de rol; IDOR (id din URL neverificat contra tenantului).
**Stare: PARȚIAL.**
- ACOPERIT: `core/test_rute_autentificate.py` (27.07) — AST pe `main.py` **și**
  `core/spv_rute.py`; orice rută fără `Depends` trebuie să fie în lista `PUBLICE`, declarată
  explicit cu motivul. Lista e verificată și invers: o intrare care nu mai corespunde unei
  rute fără auth pică (nu se acumulează acoperire moartă). Dovedit prin mutație pe cod real.
- Cele 3 rute din `core/spv_rute.py` (declarate cu `@app.get` *în interiorul* funcției
  `monteaza`) fuseseră ratate de auditul manual — garda le acoperă.
- LIMITĂ DECLARATĂ: verifică PREZENȚA dependenței, nu corectitudinea ei. O rută de cabinet
  care cere din greșeală `cere_client` trece.
- LIPSĂ: test de acces încrucișat (obiect din alt tenant → 404).
- DESCHIS: gating admin inconsecvent (`cere_rol("superadmin")` vs `cere_cabinet` + gardă
  inline) — DE_FACUT poz. 7.

### 7. Integritate în timp
**Eșec:** modificare retroactivă în lună închisă; declarație depusă regenerată altfel;
balanță ≠ sumă înregistrări; backup nerestaurabil.
**Stare: PARȚIAL.**
- ACOPERIT: `perioade_blocate`; declarația depusă persistată cu rânduri (F163v2);
  `verificatoare.echilibru_nota` / `balanta`.
- ACOPERIT: backup local + off-site cu alertare la N eșecuri consecutive.
- ACOPERIT: restaurarea din off-site **a fost testată cap-coadă pe 18.07** (`pg_restore` exit 0,
  scheme identice cu producția, `tenant_002.facturi=5`, apoi `dropdb`). Am scris inițial aici
  „LIPSĂ" fără să verific — vezi ISTORIC 18.07. Ce lipsește e **repetarea automată**: proba a
  fost făcută o dată, manual; nimic n-o reia periodic.
- LIPSĂ: verificare nocturnă Σdebit=Σcredit per perioadă/tenant + orfani.

### 8. Integritate cod — arbori paraleli
**Eșec:** două implementări ale aceluiași generator; repari copia moartă.
**Stare: ACOPERIT DE FAPT, gard absent.**
- Verificat 27.07: pe server există **un singur arbore** (`core/`). `declaratii.*` și
  `motor.*` nu există aici. Zero module neimportate (toate `migrare_*` sunt scripturi CLI;
  `alerta_acces`, `audit_retentie`, `sinteza_zilnica` rulează din cron).
- LIPSĂ: gard care să prindă apariția unei a doua copii.

### 9. Onestitatea testelor
**Eșec:** teste verzi care nu testează nimic (fake-uri pe codul auditat, teste stale,
fișiere necolectate).
**Stare: PARȚIAL.**
- ACOPERIT de fapt: 1322 teste colectate; fake-uri (`monkeypatch`/`MagicMock`) doar pe
  integrări externe (SPV, e-Factura, e-Transport, JWT). **Zero fake pe generatoarele de
  declarații.**
- LIPSĂ: **mutantul zero sistematic** — forțezi fiecare generator să întoarcă `[]` și suita
  trebuie să devină roșie. Se aplică azi ad-hoc, la reparații.
- ACOPERIT (31.07): gard că fiecare `test_*.py` (exclus venv) are ≥1 funcție `def test_` — `core/test_agenda.py::test_fiecare_fisier_test_are_cel_putin_un_test`, cu mutație. Un `test_*.py` cu 0 teste e script deghizat în suită (pytest nu-l colectează, dar numele sugerează acoperire). Prins pe `test_gdpr_functional` → redenumit `gdpr_functional.py`.
- ACOPERIT (punct orb al garzii anti-stale, gasit + REPARAT 04.08): un test ȘTERS dar inca citat in coloana `functie` a unui
  cluster cu MAI MULTE fisiere SCAPA `test_agenda::test_verificarile_A`. `_fisier_functie` cade pe fisier[0] cand
  functia nu-i in niciun fisier -> compara `<ABSENT>` vs `<ABSENT>` -> NEstale. Dovada empirica: bifa
  `taxare inversa|d394` a citat `test_datorie_gaze_naturale_...` mult dupa ce testul fusese scos (6675f19), suita
  a ramas verde. REPARAT 04.08: `_functie_schimbata` cauta functia in TOATE fisierele clusterului la ambele commituri (stergere=schimbat, mutare-neschimbata=NU stale, absent la ambele=citare moarta semnalata); regresie gardata de test_functie_schimbata_cauta_toate_fisierele_punct_orb_04_08. Rularea pe tot inventarul a mai scos 5 bife ascunse de acelasi punct orb (plafon diurna=datorie period-awareness rezolvata nereflectata + 4 citari/fisiere gresite), toate reparate. Detaliu
  metodic: TESTE.md cap. „Clustere — metoda” sectiunea 7.
- ACOPERIT (04.08): gard `test_agenda::test_fisiere_coloana_completa` - fiecare test citat in coloana `functie`
  a unui cluster traieste intr-un fisier LISTAT in `fisiere`. Prinde golul la CREAREA clusterului - fereastra in
  care `test_verificarile_A` e OARBA (lucreaza doar pe clustere cu √; unul nou porneste nebifat). Mutatie:
  `test_fisiere_coloana_completa_prinde_gol`. A prins retroactiv 5 bife cu testul in afara coloanei (04.08).
- LIMITA + RULARE PERIODICA (04.08): `test_verificarile_A` compara doar CAPETELE (√-AST vs HEAD-AST) - un drift
  DUS-INTORS (functia modificata dupa √, apoi readusa la forma de la √) scapa. Verificat 04.08 pe tot istoricul:
  ZERO drift acum, dar riscul creste cu varsta bifei (ferestrele √->HEAD sunt scurte azi). Verificarea completa NU
  e in suita (ar reciti istoricul git la fiecare commit) - e o UNEALTA PERIODICA NEAUTOMATIZATA:
  `python3 -m core.agenda_drift`. DECLANSATORI (prag motivat): (a) o bifa cu √ mai vechi de ~3 luni; (b) repornirea
  unei campanii pe un cluster deja bifat, inainte de a te sprijini pe bifa veche. De ce 3 luni: ~ un ciclu fiscal RO
  (declaratii lunare/trimestriale, legislatia se schimba la granite de an/semestru); sub atat, fereastra e prea
  scurta ca sa merite recitirea istoricului.

### 10. Joburi de fundal
**Eșec:** job care crapă nesupravegheat; job mort care arată identic cu unul care n-a avut
nimic de făcut.
**Stare: PARȚIAL.**
- ACOPERIT: `core/cron.py` — traceback în log + alertă (canal unic, cu throttling) + exit 1.
  `test_cron.py` verifică mecanic că fiecare din cele 7 module din crontab cheamă
  `cron.ruleaza`. Alerta care crapă nu maschează eșecul.
- ACOPERIT: **heartbeat** (27.07) — fiecare rulare reușită scrie în `public.cron_batai`;
  `core/cron.verifica_batai` compară cu pragul per job (ritm ×2 + marjă) și alertează.
  Rulează pe **systemd timer** la 6 ore, nu pe cron — singurul mecanism care supraviețuiește
  unui crontab pierdut. `bootstrap()` evită falsul-pozitiv la instalare.
- LIMITĂ DECLARATĂ: verificatorul rulează pe **același server**. Server jos = nici el nu
  rulează, nimeni nu află. Un deadman extern (ping către un serviciu terț) ar acoperi și asta.

### 11. Interfață (Design System)
**Eșec:** dialecte de formatare, culori hardcodate, stări goale ad-hoc.
**Stare: ACOPERIT mecanic, PARȚIAL vizual.**
- `verificator_conformitate.py`, 28 gardieni, TOTAL 0 obligatoriu înainte de commit.
- LIMITĂ DECLARATĂ: prinde SEMNĂTURA TEXTUALĂ, nu randarea. ~20/30 ecrane nevăzute cu ochii.

---

## Cum se strică un gard (lecții trăite, 27.07.2026)

Toate patru la aceeași gardă, în aceeași zi.

1. **Regex naiv pe cod.** `[^)]*` se oprește la prima paranteză închisă, deci ratează
   `body.get("an")`. Garda pica pe cod **corect**. Extragerea din cod se face pe paranteze
   echilibrate sau cu AST, niciodată cu regex naiv.
2. **Gardă care crapă.** `NameError` (import lipsă) → pică pe orice, inclusiv pe mutant.
   Testul de mutație a trecut **fals**. Mutația verifică motivul, nu doar eșecul.
3. **Verificare trunchiată.** `pytest -q | tail -3` taie mesajul la `AssertionEr...`.
   Verificarea unei gărzi citește output complet (`--tb=long` în fișier).
4. **Comparație pe `hash()`.** Randomizat per proces în Python — a raportat 6 diferențe
   false. Artefactele se compară pe SHA256 sau diff, niciodată pe `hash()`.

A cincea, din aceeași zi, la altă gardă:
5. **Poartă decorativă.** Verificarea rulează dar nu blochează (commit legat de `py_compile`,
   nu de probă). Dacă proba nu e poartă, e comentariu.

---

## Reguli de scris în acest registru

- Starea se schimbă **doar cu dovadă în același commit**.
- „ACOPERIT DE FAPT, gard absent" e o stare distinctă și onestă: azi e curat, mâine nu se știe.
- Limita declarată a fiecărui gard se scrie explicit. Un gard fără limită scrisă e citit ca
  acoperire totală.


## 03.08.2026 — Gard anti-fabricare a cursului de schimb (D301, cluster "baza = val x curs")

**Temei:** CF art.290 alin.(2) — cursul aplicat operatiunii in valuta e cel BNR/BCE ori al
bancii de decontare, valabil la exigibilitate. Un curs real e > 0; pentru RON e 1 (dat ca dată).

| gard | fisier:linie | ce face imposibil | mutatia care il probeaza |
|---|---|---|---|
| calc_baza refuza curs None/<=0 | core/d301.py (calc_baza) | fabricarea tacita curs=1 pe valuta (baza subevaluata la ANAF, fara eroare) | calc_baza(1000, None) -> ValueError; generator EUR fara curs -> ValueError (INAINTE: baza=1000 tacut). test_d301_curs.py |
| reader grilei fara fabricare | core/d301_operatiuni_api.py:lista | afisarea unei baze fabricate (curs=1) pe o linie cu curs NULL | fake cursor cu curs=None -> lista ridica. test_d301_curs.py |
| schema fara DEFAULT 1 pe curs | tenant_template.sql (d301_operatiuni) | DB sa fabrice 1 la insert-fara-curs (tenant nou) | insert fara curs -> NULL -> calc_baza ridica la generare |

**Limita gardului:** calc_baza nu distinge curs=1 REAL (RON valid) de un curs=1 fabricat de un
DEFAULT pe tenant EXISTENT (nemigrata). Pe tenantii deja creati, coloana pastreaza DEFAULT 1
pana la migrare (sarcina deployment, §2.3 pct.3). Poarta de intrare adauga() cere oricum
curs>0 explicit, deci calea UI nu atinge acest rest.


## 03.08.2026 — Gard period-aware pe cota redusa TVA (D301, cluster "cota TVA")

Temei: CF art.291 alin.(2) — redusa 11% de la 01.08.2025 (Legea 141/2025 a comasat 9%/5% in 11%).

| gard | fisier:linie | ce face imposibil | mutatia care il probeaza |
|---|---|---|---|
| cota redusa period-aware (nu literal) | core/d301_operatiuni_api.py:cote_perioada | oferirea unui 11% redusa pe o perioada < 01.08.2025 (cand reducerile erau 9%/5%) -> tva eronat persistat (fals-verde) | cote_perioada(2025,6) NU contine 11 (inainte: il continea); adauga(2025-06, cota=11) respinge (inainte: persista tva=55). test_d301_cota.py |

Limita: perioadele < 01.08.2025 raman FARA optiune de cota redusa (9%/5% coexistente nemodelate in COTE).
Fail-loud (omitere) preferat unui 11% fals. Modelarea corecta = decizie de produs deschisa (DECIZII 03.08).


## 03.08.2026 — Gard-pin nomenclator tipuri operatiune D390 (cluster "tipuri operatiune IC")

Temei: OPANAF 705/2020 (anaf_surse/d390_struct_anaf.txt), restrictia campului <operatie> tip = (L,T,A,P,S,R).

| gard | fisier | ce face imposibil | mutatia care il probeaza |
|---|---|---|---|
| TIPURI == lista oficiala | core/test_d390.py (test_tipuri_operatiune_sunt_exact_nomenclatorul_oficial_opanaf_705_2020) | schimbarea tacita a nomenclatorului de simboluri D390 (add/scoate/reordoneaza) | mutant in-process TIPURI+("X",) -> assertion cade; pin cere reverificare la sursa |

Nota: gardul anti-DROP tacit pe tip manual necunoscut exista deja (d390.py:159 raise, test_d390_manual_tip_necunoscut_ridica_nu_dispare). Pin-ul acopera driftul de SURSA (editare TIPURI), complementar.


## 03.08.2026 — Gard cote reduse istorice period-aware (9%/5%, urmare decizie produs Costin)

Temei: CF art.291 alin.(2) 9% / alin.(3) 5%, comasate in 11% de Legea 141/2025 de la 01.08.2025.

| gard | fisier | ce face imposibil | mutatia care il probeaza |
|---|---|---|---|
| cote_perioada pe registru period-aware | core/test_d301_cota.py (test_cote_perioada_veche_ofera_9_si_5_coexistente) | oferirea unei cote reduse gresite pt perioada (11% pe era 9%/5%, sau lipsa reduselor) | cote_perioada(2020,3)=[19,9,5,0]; 2026=[21,11,0] |
| cota() refuza cote istorice inainte de ancora | core/test_d301_cota.py (test_cota_reduse_istorice_indisponibile_inainte_de_ancora_2017) | presupunerea unei valori 9%/5% pt perioade < 2017 (nedocumentate in sursa) | cota("tva_redusa_9", 2015) -> PerioadaIndisponibila |
| ETICHETE acopera cheile noi | core/test_expirare_cote.py | drift eticheta<->cheie COTE la adaugarea unei chei | monkeypatch scoate eticheta -> garda de acoperire pica (existent) |

Limita: datele de inceput 9%/5% ancorate la 2017-01-01 (REDARE, de reconfirmat la MO); textul verbatim al fostului
alin.(3) la 5% neconfirmat verbatim (doar "Abrogat" in consolidat). Consemnat in DECIZII 03.08.


## 03.08.2026 — Proba rotunjire aritmetica D390 pe valoare (cluster "rotunjire aritmetica A91b")

Referinta: DUK regula A91b (ANAF: sumele fiscale se rotunjesc half-up, nu bancar). Referinta de validator, NU act normativ (§3.1).

| gard | fisier | ce face imposibil | mutatia care il probeaza |
|---|---|---|---|
| _int(D390) rotunjeste aritmetic pe VALOARE | core/test_d390.py (test_d390_rotunjeste_aritmetic_nu_bancar_A91b) | revenirea la round() bancar pe sumele fiscale D390 | _int(2.5)=3, _int(112.5)=113 (bancar ar da 2/112) |

Complementar celor DOUA garduri existente: identitate cross-generator (test_rotunjirea_e_identica_intre_generatoare,
importa d390._int == d300 == d112 == d205) + scan anti-round() bancar pe toate d*.py (test_toate_generatoarele_
rotunjesc_aritmetic). Proba pe valoare fixeaza CIFRA aritmetica, nu doar egalitatea (daca toate ar fi bancare,
identitatea ar trece fals).


## 03.08.2026 — Gard read-side reclasificare D390 (cluster "reclasificari manuale")

Temei: DECIZII 21.07 "achizitia nu poate deveni livrare si invers" + OPANAF 705/2020 (L/T/P/R = livrare/prestare, A/S = achizitie).

| gard | fisier | ce face imposibil | mutatia care il probeaza |
|---|---|---|---|
| calcul_d390/operatiuni_auto valideaza reclasificarea direction-aware | core/d390.py (_reclasificare_tip) | fallback tacit la default pe un override invalid din d390_reclasificare (misclasificare: intentia contabilului inlocuita tacut) | reclasificari={...:"Z"} sau "A"-pe-emisa -> ValueError (inainte: revenea tacit la L). test_d390.py |

Uniformizeaza read-side cu write-side (salveaza_reclasificare valida deja) SI cu gardul liniilor manuale (d390.py:159).
TIPURI_DIRECTIE mutat in d390.py (sursa unica, importat de API - elimina si riscul de import circular). Pe date valide: 0 schimbare.


## 03.08.2026 — Gard temporal incadrare D390 pe data_emitere (cluster "exigibilitate / prag")

Temei: CF art.283/284 (exigibilitatea intracom = data emiterii facturii) + art.325 alin.(1)/(4).

| gard | fisier | ce face imposibil | mutatia care il probeaza |
|---|---|---|---|
| pull incadreaza pe data_emitere, fereastra [M-01,(M+1)-01) | core/test_pull_declaratii.py (test_d390_pull_incadreaza_pe_data_emitere_exigibilitate) | schimbarea tacita a campului/ferestrei de incadrare in luna D390 | factura UE 30 iun intra; 1 iul si 31 mai NU (fereastra gresita ar aduce mai/iulie -> cade) |

Golul de acoperire inchis: testele calcul ocoleau pull, deci incadrarea temporala (unde sta potentiala neconformitate) nu era testata.


## 03.08.2026 — Garduri cote acceptate D394 (cluster "cote acceptate")

Temei: OPANAF 2194/2025 (validator v5, TVA 21%/11% de la 01.08.2025) + structura D394 2020 (cota in 0,5,9,19,20,24).

| gard | fisier | ce face imposibil | mutatia care il probeaza |
|---|---|---|---|
| pin d394.COTE == setul validatorului v5 | core/test_d394.py (test_d394_cote_acceptate_sunt_setul_validatorului_v5) | drift tacit al setului de cote acceptate de D394 | COTE != (0,5,9,11,19,20,21,24) -> cade |
| CROSS-MODUL: common.COTE tva_* subseteaza d394.COTE | core/test_d394.py (test_d394_cote_acopera_toate_cotele_tva_din_common) | o cota TVA noua adaugata in common ignorata TACIT de D394 (Cota nedeclarabila) | cota 7% in common -> lipsa={7} -> cade |

d394 e deja modelul period-aware (cota_standard din common.cota, agregare pe cota reala) - fara literal de cota hardcodat (spre deosebire de d301).


## 03.08.2026 — Gard anti-regresie taxare inversa CATEGORII->CODPR + datorie gaze naturale (cluster "taxare inversa")

Temei: CF art.331 alin.(2) lit.a-l (12 categorii de taxare inversa) + structura D394 op11 (codPR obligatoriu).

| gard | fisier | ce face imposibil | mutatia care il probeaza |
|---|---|---|---|
| orice categorie taxare inversa are codPR D394 | core/test_d394.py (test_toate_categoriile_taxare_inversa_au_codpr_d394) | adaugarea unei categorii in motor (taxare_inversa.CATEGORII) fara cod D394 -> factura recunoscuta dar dropata din op11 (D394 structural incomplet) | set(CATEGORII)-set(CODPR) != {} -> cade |
| datorie gaze naturale (lit.l) | core/test_datorie.py (test_datorie_gaze_naturale_taxare_inversa_art331_lit_l, xfail strict) | uitarea golului lit.l gaze naturale | gaze in CATEGORII+CODPR -> xfail trece -> strict pica -> semnaleaza inchiderea |

NECONFORMITATE (11/12 litere art.331): lit.l gaze naturale lipseste din motor + D394. CORECTARE blocata: codPR-ul D394 gaze NU e in sursele repo (Ghid 2016, anterior Legii 296/2020; 21-31 tip1, 32-35 rezervate tip2). Nu se inventeaza (§3). Gardul anti-regresie forteaza fixul complet cand apare codPR.


## 03.08.2026 — Gard TaxCode livrari period-aware D406 (cluster "SourceDocuments")

Temei: Legea 141/2025 (coduri TaxCode SAF-T livrari noi de la 01.08.2025) + structura D406/SAF-T (corespondent rand D300).

| gard | fisier | ce face imposibil | mutatia care il probeaza |
|---|---|---|---|
| _taxcode_livrari period-aware pe data facturii | core/test_d406.py (test_taxcode_livrari_period_aware) | emiterea codurilor TaxCode post-2025-08 pe o factura dinainte (raportare retroactiva cu coduri gresite) | 19%@2025-06=310309 (inainte: 310312 taxare inversa gresit); 9% pre=310310 != post=310357 |


## 03.08.2026 — Gard plafon diurna curent + datorie period-awareness istorica (cluster "plafon diurna")

Temei: CF art.76 alin.(2) lit.k + alin.(4^1) - min(2,5x diurna bugetara; 3 salarii/zile lucratoare) x zile.

| gard | fisier | ce face imposibil | mutatia care il probeaza |
|---|---|---|---|
| golden pe plafonul curent (2023+) | core/test_deconturi.py | schimbarea tacita a formulei/valorii curente | 23*2,5=57,50; capul 3-salarii musca pe salariu mic; neimp/impozabil pe cifre |
| datorie period-awareness istorica | core/test_datorie.py (xfail strict) | uitarea ca varianta e unica (valorile de azi aplicate retroactiv) | >=2 variante -> xfail trece -> strict pica |

Calculul CURENT (2023+) conform art.76 alin.(4^1). Istoric (pre-2023) blocat pe valorile HG diurna (nu-s in surse repo).


## 03.08.2026 — Credit sponsorizare: profit conform + datorie micro period-aware (cluster "credit sponsorizare / D177")

Temei: CF art.25 alin.(4) lit.i (profit: min 0,75% CA / 20% impozit + registru); fostul art.56 alin.1^5 (micro, abrogat OUG 115/2023).

| gard | fisier | ce face imposibil | mutatia care il probeaza |
|---|---|---|---|
| datorie micro period-aware | core/test_datorie.py (test_datorie_credit_sponsorizare_micro_period_aware, xfail strict) | uitarea ca micro=0 e aplicat retroactiv (2019-2023 avea credit) | credit micro @2022 > 0 -> xfail trece -> strict pica |

Profitul e gardat de test_operatiuni_speciale.py (4 teste existente). Micro fix blocat pe textul istoric art.56 alin.1^5 (abrogat, nu-i in consolidat).


## 03.08.2026 — Gard formula rezerva legala contabila (cluster "rezerva legala")

Temei: Legea 31/1990 art.183 + OMFP 1802/2014 pct.421 (rezerva 5% profit, plafon 20% capital).

| gard | fisier | ce face imposibil | mutatia care il probeaza |
|---|---|---|---|
| golden pe formula rezervei contabile | core/test_operatiuni_speciale.py (test_rezerva_legala_5pct_plafon_20pct_capital) | schimbarea tacita a formulei (5%/plafon 20% cumulat) | 5%*100000=5000; plafon musca la 3000; atins->0; profit neg->0 |

Formula contabila corecta + period-aware. Deductibilitatea FISCALA art.26(1)a (add-back cheltuiala impozit) = decizie de produs (DECIZII).


## 03.08.2026 — Gard period-aware zilieri CAS (cluster "zilieri | contracte_speciale")

Temei: OUG 26/2019 (CAS pe zilieri de la 01.05.2019); CF art.76(2) lit.r (impozit), art.142 lit.t (fosta exceptare CAS, abrogata).

| gard | fisier | ce face imposibil | mutatia care il probeaza |
|---|---|---|---|
| variante zilier period-aware pe CAS | core/test_versionare_formule.py (test_calcul_zilier_dispecer_versionat) | aplicarea CAS 25% zilierilor INAINTE de 01.05.2019 | 2018 -> CAS 0, net 90; 2019 -> CAS 25 (inainte: CAS 25 din 2018-01-01) |


## 03.08.2026 — Gard golden TVA pe marja second-hand (cluster "regim marja second-hand")

Temei: CF art.312 alin.(4) - baza = marja profitului, EXCLUSIV valoarea taxei aferente (TVA extras din marja).

| gard | fisier | ce face imposibil | mutatia care il probeaza |
|---|---|---|---|
| formula suta marita cota/(100+cota) | core/test_versionare_formule.py (test_tva_marja_formula_suta_marita_art312) | folosirea cota/100 in loc de cota/(100+cota) pe marja | marja 400 cota 21 -> TVA 69,42 (nu 84); marja negativa -> 0; cota 19 -> 63,87 |


## 03.08.2026 — Gard golden TVA marja turism (cluster "regim marja turism")

Temei: CF art.311 alin.(4) (baza = marja, exclusiv taxa; suta marita) + alin.(5) (scutire proportionala non-UE).

| gard | fisier | ce face imposibil | mutatia care il probeaza |
|---|---|---|---|
| suta marita + scutire proportionala non-UE | core/test_versionare_formule.py (test_marja_turism_formula_suta_marita_si_scutire_non_ue_art311) | folosirea cota/100 sau ignorarea scutirii non-UE | tot UE 400 -> TVA 69,42; 50% non-UE -> scutita 200, TVA 34,71; negativa -> 0 |


## 03.08.2026 — Fix cote istorice impozit dividend (cluster "impozit dividend")

Temei: CF art.97 alin.(7); 5% de la 2016 (OUG 50/2015), 8% de la 2023 (OG 16/2022), 16% de la 2026 (Legea 141/2025).

| gard | fisier | ce face imposibil | mutatia care il probeaza |
|---|---|---|---|
| impozit dividend period-aware 5/8/16 | core/test_impozit_dividend.py + core/test_d205.py | cota 10% falsa sau lipsa istoric (2023-2025 = 8%, nu 10%) | 2020 -> 0.05, 2024 -> 0.08, 2026 -> 0.16 (inainte: 10% pt tot pre-2026) |

Nota: testele CIMENTAU valoarea gresita 10% (clasa "teste care apara buguri" - de aceea nu s-a auto-detectat) - actualizate la valorile reale.


## 03.08.2026 — Corectie temei + verificare contributii PFA D212 (cluster "contributii PFA")

Calcul CONFORM (CAS art.148 praguri 12/24 sm; CASS art.170 alin.1 liniar 6 sm..plafon 60/72 sm; sm period-aware).
Gardat de test_d212.py (valori CAS/CASS + praguri 2026) + test_d212_reper.py (reper sm period-aware).

FIX de TEMEI (§3.1): plafonul CASS 72 sm (venituri 2026) era atribuit gresit "Legea 141/2025" (aceea = TVA/accize);
corect = Legea 239/2025 art.XII pct.19 (MO 1160/15.12.2025). Valoarea 72 sm corecta si confirmata la sursa; doar
actul citat era gresit (grep-ul pe act ar fi dus in locul gresit). Corectat in d212_engine.py (3 locuri) + test_d212.py.
OBSERVATIE: calea 2026 dormanta in productie (rip_api.py:145 poarta an=2025) - de ridicat la depunerea din 2027.


## 03.08.2026 — Fix cont bugetar D100 (5503) + gard anti-drop (cluster "nomenclator cod_oblig<->cod_bugetar")

Temei: nomenclator ANAF D100 (d100_struct_anaf.txt:562 - 20470101 inlocuit cu 5503 din 26.07.2018; camp cod_bugetar C(10) X-padat).

| gard | fisier | ce face imposibil | mutatia care il probeaza |
|---|---|---|---|
| cod bugetar 5503XXXXXX + raise pe cod nemapat | core/d100.py + core/test_d100.py/test_d710.py | contul obsolet 20470101 sau omiterea TACITA a cod_bugetar (atribut obligatoriu) | 121/103 -> 5503XXXXXX; cod_oblig 999 -> ValueError (inainte: 20470101 / omis tacit) |

Coroborare: d101/d112 emit deja 5503XXXXXX pentru acelasi cod_oblig 103 - d100 isi contrazicea fratii.


## 03.08.2026 — Gard bidirectional cota micro D100 (cluster "cota micro 121 (flag)")

Temei: struct D100 poz.17a - "daca cod_oblig=121 atunci cota=1 altfel cota=null" (ERR cota micro invalida).

| gard | fisier | ce face imposibil | mutatia care il probeaza |
|---|---|---|---|
| cota micro 121 bidirectional | core/d100.py build_xml (test_cota_micro_121_gard_bidirectional) | XML respins de validator: 121 fara cota="1" SAU cota pe alt cod_oblig | 121 fara cota -> ValueError; 103 cu cota -> ValueError; 121+cota=1 -> cota="1" in XML |


## 04.08.2026 — DATORIE: suport COMPLET operatiuni N (D394) - ce lipseste (decizie Costin, approach a viitor)

STARE CURENTA (approach a CONDITIONAT, livrat 04.08 dupa reviziune): operatiunile N (achizitii de la parteneri
NEINREGISTRATI, tip_partener=2) se EMIT VALID cand au `categorie_331` din nomenclatorul lit.D (tip_document=1 facturi,
document_N=1, op11 codPR, detaliu nrN/valN) - PROBAT DUK (test_N_cu_categorie_litD_e_declarat_si_valid_pe_duk). FARA
categorie_331 (azi nu exista UI care s-o seteze) N ramane EXCLUS cu avertisment vizibil (furnizor+suma), D394 valid
pentru rest. Categorie ne-lit.D -> exclusa, nu emite cod invalid (test_N_categorie_ne_litD_e_exclusa).

CE MAI LIPSESTE (dupa livrarea approach-a conditionat) - campanie proprie, dupa ce se decide UI-ul:
- **UI categorie_331** - fara ecran care sa seteze categoria art.331 pe operatiunea de la neinregistrat, N ramane
  exclus in calea auto. Deblocajul principal. (Datorie in sectiunea „04.08 Datorii deschise ale campaniei".)
- **op1.tip_N** (pct.229) - DESCOPERIT ca **NU EXISTA in validatorul v5** (tiparul ASI: injectat -> J8 "tip_N
  atribut necunoscut"; extras din v5/Op1.class = absent). NU e un camp de emis/introdus, iese din scope (fostul
  "camp nou de contabil" era o presupunere din pdf, infirmata la sursa).
- **op1.tip_document 2-5** (pct.228: 2=borderouri / 3=file carnet / 4=contracte / 5=alte) - calea AUTO emite deja
  1=facturi (livrat); 2-5 = EXTINDERE DE CONTRACT (facturi/manual n-au campul, cere sursa noua). Ramas.
LIVRAT deja (nu mai e "lipsa"): tip_document=1 + rezumat1.document_N=1 pentru facturi + op11.codPR din categorie_331.
Excluderea din calcul_d394 e acum CONDITIONATA (doar cand lipseste categorie_331), iar gardul invers
test_N_ar_fi_respins_de_validator_daca_emis_GARD_INVERS e ACTIV (pazeste un N emis incomplet). Vezi DECIZII 04.08.


## 04.08.2026 — Gard UoM UN/ECE D406 (cluster "UoM UN/ECE")

Temei: SAF-T UnitOfMeasure = cod UN/ECE Recommendation 20 (NU unitatile romanesti; BUC respins). Codurile-tinta
din UOM_UNECE sunt validator-confirmate (proba 15.07.2026 + extractie D406Validator.jar). Default H87 (bucata).

| gard | fisier | ce face imposibil | mutatia care il probeaza |
|---|---|---|---|
| UOM_UNECE = coduri UN/ECE valide + default H87 + semnal la necunoscut | core/test_d406.py (test_uom_unece_mapare_coduri_valide) | o unitate romaneasca (BUC) ca valoare-tinta / un cod ne-UNECE / pierderea semnalului la necunoscut | buc->H87, mp->MTK, necunoscut->(H87,False), BUC nu e valoare-tinta |


## 04.08.2026 — Gard plan conturi pe norma D406 - conturi excluse VIZIBILE (cluster "plan conturi pe norma")

Temei: SAF-T (D406) - planul de conturi se filtreaza pe nomenclatorul OFICIAL al normei firmei (plan_oficial);
conturile ne-norma se exclud (ANAF le respinge). Reparat drop tacit: conturile excluse se SEMNALEAZA acum in
avertisment (numite), ca operatiunile N in d394 - nu dispar tacit (decizie Costin 04.08).

| gard | fisier | ce face imposibil | mutatia care il probeaza |
|---|---|---|---|
| conturi straine de norma = SEMNALATE, nu excluse tacit | core/test_d406.py (test_conturi_straine_de_norma_sunt_semnalate_nu_excluse_tacit) | un cont cu sold exclus din SAF-T fara ca contabilul sa stie | firma A cu cont 731 (ONG) -> exclus + numit in avertisment |


## 04.08.2026 — Gard totalPlata_A R17 D394 (cluster "totalPlata_A (R17)")

Temei: R17 validator D394 - totalPlata_A = Suma(informatii.nrCui1..4) + Suma(rezumat2.baza[L+A+AI]).
res.total_plata_a calculat in calcul_d394, emis din res in build_xml (sursa unica, clasa d100).

| gard | fisier | ce face imposibil | mutatia care il probeaza |
|---|---|---|---|
| totalPlata_A: res==emis + R17-valid pe validator | core/test_d394.py (test_totalPlata_A_R17_sursa_unica_si_probat_pe_validator) | divergenta res-vs-emis SAU o formula care nu trece R17 | res==emis==3002 DUK-valid; totalPlata_A+999 -> R17 respins |


## 04.08.2026 — Gard nomenclator codPR pe validator (cluster "nomenclator codPR (art.331)")

Temei: d394.CODPR (categorii art.331 -> cod op11 + subcod NC cereale). Sursa citata in cod = Ghid_D394_2016
(INVECHIT); AUTORITATEA = validatorul J8 instalat (codPR eronat -> "codPR eronat in dictionar"). Toate codurile
sunt validator-confirmate, inclusiv gaze_naturale 36 (fostul blocaj lit.l, rezolvat 6675f19).

| gard | fisier | ce face imposibil | mutatia care il probeaza |
|---|---|---|---|
| codPR din CODPR = acceptate de validatorul curent | core/test_d394.py (test_codpr_valide_pe_validatorul_curent) | un codPR care nu mai e in nomenclatorul validatorului (invechit din Ghid 2016) | deseuri(22)/gaze(36)/cereale(1001) taxare inversa -> DUK valid |


## 04.08.2026 — Gard rezumat1 campuri + datorie N (cluster "rezumat1 campuri complete")

Temei: rezumat1 D394 cere campurile COMPLETE (0-umplut) pe (tip_partener, cota), setul din validatorul RULAT
(J8). Pentru parteneri inregistrati/straini = verificat J8-valid. N (neinreg): cu categorie_331 lit.D emite
document_N/tip_document/codPR si e J8-VALID (approach a conditionat, 04.08); fara categorie_331 = exclus (UI lipsa).

| gard | fisier | ce face imposibil | mutatia care il probeaza |
|---|---|---|---|
| rezumat1 tp1/tp3 complet + J8-valid | core/test_d394.py (test_rezumat1_campuri_complete_tp1_tp3_valide_pe_validator) | un camp rezumat1 lipsa/in plus pt parteneri inreg/straini | L(tp1)+A(tp1)+L(tp3) -> DUK valid |
| N cu categorie lit.D = J8-valid (emis) | core/test_d394.py (test_N_cu_categorie_litD_e_declarat_si_valid_pe_duk) | ca emisia N valida sa regreseze tacit | achizitie neinreg + categorie lit.D -> N emis (document_N/tip_document/codPR) -> DUK valid |
| N emis fara campurile cerute ar fi respins (gard invers) | core/test_d394.py (test_N_ar_fi_respins_de_validator_daca_emis_GARD_INVERS) | ca un N incomplet sa para acceptat | N emis fara document_N/tip_document -> DUK respinge (R228/R60) |


## 04.08.2026 — Gard clasificare tip_partener D394 (cluster "tip_partener")

Temei: pct.216 (OPANAF 77/2022) - 4 categorii tip_partener. cui_ro e normalizare; validitatea cuiP e
enforced de validator (R218.2). Ramura UE/non-UE se sprijina pe _TARI_UE (verificat DUK, cluster HR->CR).

| gard | fisier | ce face imposibil | mutatia care il probeaza |
|---|---|---|---|
| tip_partener acopera exact cele 4 categorii pct.216 | core/test_d394.py (test_tip_partener_clasificare_pct216) | o clasificare care rateaza o categorie sau confunda RO/UE/non-UE | RO+CUI->1, fara/ne-numeric->2, UE(DE/HR)->3, non-UE(CH)->4 |


## 03.08.2026 — Gard tipuri operatiune D394 + datorie ASI (cluster "tipuri operatiune (pct.215)")

Temei: TIPURI op1 D394 = setul din structura oficiala (formulele op1(tip)=X). Discrepanta: ASI e in structura
pdf dar D394Validator instalat il respinge ca enum (probat izolat). Corectare blocata pe decizie de produs.

| gard | fisier | ce face imposibil | mutatia care il probeaza |
|---|---|---|---|
| TIPURI = exact setul din structura oficiala | core/test_d394.py (test_tipuri_operatiune_pin_la_structura_oficiala) | un tip adaugat/scos tacit din cod, divergent de structura | orice modificare a TIPURI care nu-i in formulele op1(tip)=X pica |
| ASI respins de validator = consemnat (datorie) | core/test_d394.py (test_asi_respins_de_validatorul_instalat_DATORIE) | ca discrepanta pdf-vs-jar sa dispara tacit | substituie tip=ASI pe baza valida -> DUK "nu se afla in lista"; daca validatorul accepta ASI, pica si cere reevaluare |


## 03.08.2026 — Gard nomenclator tari Croatia HR (cluster "nomenclator tari (HR->CR)")

Temei: nomenclatorul de tari D390 (ANAF) foloseste prefixul de TVA (= cod ISO) pt fiecare tara; Croatia = HR.
Maparea HR->CR era o NECONFORMITATE (probata DUK: tara=CR respins "nu se afla in lista", tara=HR valid).

| gard | fisier | ce face imposibil | mutatia care il probeaza |
|---|---|---|---|
| Croatia emite HR, nu CR | core/d390.py (_TARA_XML gol) + core/test_d390.py (test_croatia_emite_HR_nu_CR, test_croatia_HR_trece_duk) | o remapare de tara care produce un cod absent din nomenclatorul ANAF | partener croat (OIB valid) -> tara="HR" in XML + DUK valid; readaugarea HR->CR -> tara=CR respins de DUK |


## 03.08.2026 — Gard limita text d406 (SAF-T) — extindere audit

Temei: SAF-T are limite proprii din XSD SimpleTypes (short 18 / middle1 35 / middle2 70 / long 256), nu din struct.
d406 emitea majoritatea campurilor text NETRUNCHIATE (Customer/Supplier Name, City, Description-uri, PostalCode,
PaymentMethod). Reparat: toate trec prin text_anaf cu limita din LIMITE_TEXT_ANAF["d406"]. Gardul de clasa AST
extins sa prinda si `.text_anaf` (Attribute), acopera d406. DUK boundary indisponibil (d406 DUK = xfail preexistent).

| gard | fisier | ce face imposibil | mutatia care il probeaza |
|---|---|---|---|
| campurile text SAF-T trec prin text_anaf cu limita din registru | core/d406.py + core/test_limita_text_anaf.py (test_limitele_de_text_vin_din_registry, extins pt .text_anaf) | un Name/City/Description SAF-T emis netrunchiat sau cu limita literala | orice `_esc(x)` pe camp text fara `_t` sau `c.text_anaf(x, 256)` literal in d406 pica gardul de clasa |


## 03.08.2026 — Gard de CLASA limita text per-camp (audit "limita text" pe toate declaratiile)

Temei: fiecare camp text din XML-ul declaratiilor are o lungime oficiala C(n) proprie din structura ANAF,
CONFIRMATA pe DUK boundary-cu-boundary (C(n) valid / C(n)+1 respins). Sursa unica: core.common.LIMITE_TEXT_ANAF.
common.text_anaf CERE limita explicit (fara default global). Reparate 3 clase: over-trunchiere (den/adresa/nume),
under-trunchiere cu respingere (functie_declar 74>50), fara-limita cu respingere (denO/denP/mail/banca/cont/telefon).

| gard | fisier | ce face imposibil | mutatia care il probeaza |
|---|---|---|---|
| limita text vine DIN registru (nu literal, nu lipsa) | core/test_limita_text_anaf.py (test_limitele_de_text_vin_din_registry, AST scan pe generatoare) | o limita de text hardcodata / un _t fara limita = limita ne-oficiala | orice `_t(x)` sau `_t(x, 75)` intr-un generator pica testul |
| fiecare atribut trunchiat la C(n) propriu | core/test_limita_text_anaf.py (test_generatoarele_trunchiaza_la_limita_per_camp, fara DB) | over-trunchiere (prea mic) SAU atribut mai lung decat C(n) | den 250->200, adresa 1500->1000, functie 80->50, nume 90->75 pe fiecare generator |
| limita = limita reala impusa de DUK | core/test_limita_text_anaf.py (test_limite_text_confirmate_pe_duk_boundary, gated DB/DUK) | o limita din registru care nu e cea a validatorului | den/functie: len C(n)->valid, len C(n)+1->respins de DUK, pe fiecare declaratie |
| text_anaf cere limita explicit | core/common.py (text_anaf fara default) | emisie de text cu limita globala ne-oficiala | `text_anaf("x")` -> TypeError (test_text_anaf_trunchiaza_la_limita_data_si_normalizeaza) |


## 03.08.2026 — Gard checksum totalPlata_A R28 D301 (cluster "checksum totalPlata_A (R28)")

Temei: struct d301 poz.28 - totalPlata_A = INT(baza1..5 + tva1..5), suma de control impusa de DUK regula R28 (respinge orice alt total). res.total_plata_a = sum pe toate tipurile, build_xml emite res (sursa unica). Checksum-ul include 4.1 prin definitie; TVA datorat (tva4) ramane o singura data.

| gard | fisier | ce face imposibil | mutatia care il probeaza |
|---|---|---|---|
| res.total_plata_a == totalPlata_A emis == sum(baza+tva) toate tipurile | core/test_d301_rollup.py (test_checksum_r28_res_egal_emis_egal_suma_toate_tipurile) | divergenta res vs emis / un tip scapat din suma / checksum recalculat independent | res==emis==suma==12044; un tip omis din suma sau res!=emis cade |


## 03.08.2026 — Gard checksum + excludere 14.1/14.2 D300 (cluster "randuri / checksum")

Temei: struct D300 - totalPlata_A = suma(camp 27..124), campurile 62 (rd 14.1=R67) si 63 (rd 14.2=R68) ELIMINATE din suma de control. Codul: res.total_plata_a=sum(res.R) (sursa unica, build_xml emite res); R67/R68 nu-s in nicio allow-list manuala -> gardul-clasa le respinge, excluse prin constructie. DUK impune checksum-ul (ERR suma de control eronata).

| gard | fisier | ce face imposibil | mutatia care il probeaza |
|---|---|---|---|
| totalPlata_A == sum(res.R) == DUK-valid | core/test_d300.py (test_checksum_totalplata_a_egal_suma_randuri_emise_duk_valid) | checksum divergent de suma randurilor emise / respins de DUK | golden 7810 == sum(R) == DUK valid pe decont 21/11 |
| 14.1/14.2 (R67/R68) eliminate nu intra in checksum | core/test_d300.py (test_randuri_14_1_14_2_eliminate_nu_intra_in_checksum) | adaugarea tacita a R67/R68 in allow-list ar strica suma de control | R67_1/R68_1 manual -> ValueError (neacceptate) |


## 03.08.2026 — Gard trunchiere text D205 (cluster "trunchiere den/adresa")

Temei: ANAF struct D205 (OPANAF 102/2025) + probat direct pe validatorul DUK - den C(200), adresa C(1000), functie_declar C(50), den1 beneficiar C(100). NECONFORMITATE: toate se trunchiau la 75 (default text_anaf) - den/adresa OVER-trunchiate (pierdere de date, ANAF le accepta pana la 200/1000; D205 NU era in lista 27.07 de respingere empirica >75), functie 51-75 si den1 >100 emiteau si DUK RESPINGEA. Probe boundary DUK: den 200 valid/201 erori; adresa 1000/1001; functie 50/51; den1 100/101.

| gard | fisier | ce face imposibil | mutatia care il probeaza |
|---|---|---|---|
| den C200/adresa C1000/functie_declar C50/den1 C100 (limite explicite _t) | core/d205.py + core/test_d205.py (test_trunchiere_den_adresa_functie_den1_la_limitele_anaf, test_trunchiere_lunga_ramane_duk_valida) | pierdere de date pe den/adresa + respingere ANAF pe functie/den1 lungi | den250->200, adresa1500->1000, functie80->50, den1(150)->100; proba DUK pe inputuri lungi trunchiate = valid |


## 03.08.2026 — Gard checksum totalPlata_A D205 (cluster "checksum totalPlata_A")

Temei: ANAF struct D205 (OPANAF 102/2025, l.80-85) - totalPlata_A = suma(nrben)+suma(Tcastig)+suma(Tpierd)+suma(T_VB)+suma(T_GAR)+suma(Tbaza)+suma(Timp). La dividende (tip_venit 08) Tcastig/Tpierd/T_VB/T_GAR=0, deci checksum = nrben+Tbaza+Timp. Aceeasi capcana latenta ca d100 (res.total_plata_a divergea de valoarea emisa) - d205 era ultimul outlier de la conventia res.total_plata_a==totalPlata_A emis (d100/d101/d300/d390/d710).

| gard | fisier | ce face imposibil | mutatia care il probeaza |
|---|---|---|---|
| totalPlata_A = res.total_plata_a (o sursa) + res == suma sect_II parsata din XML | core/d205.py + core/test_d205.py (test_total_plata_a_res_egal_checksum_emis) | divergenta intre res.total_plata_a (tinea DOAR Timp) si checksum-ul emis; recalcul independent in build_xml | res.total_plata_a==58001==header==nrben(1)+Tbaza(50000)+Timp(8000); inainte res=Timp(8000), emis 58001 recalculat independent |


## 03.08.2026 — Gard checksum totalPlata_A R11b D100 (cluster "checksum totalPlata_A (R11b)")

Temei: DUK regula R11b - totalPlata_A = sum(suma_dat + suma_ded + suma_plata + suma_rest) = 2x sum(suma_dat) la obligatia simpla.

| gard | fisier | ce face imposibil | mutatia care il probeaza |
|---|---|---|---|
| totalPlata_A = res.total_plata_a (o sursa) | core/d100.py + core/test_d100.py (test_totalplata_a_checksum_r11b_din_res) | divergenta intre res.total_plata_a si valoarea emisa | res.total_plata_a==4800==XML (2x 2400); inainte res=1x, emis 2x recalculat independent |


## 03.08.2026 — Gard scadenta + nr_evidenta D100 (cluster "scadente/nr_evidenta")

Temei: struct D100 poz.15 (scadenta=25 a lunii urmatoare perioadei) + nr_evidenta 23 pozitii (format oficial + suma control poz.22-23).

| gard | fisier | ce face imposibil | mutatia care il probeaza |
|---|---|---|---|
| scadenta 25 luna urmatoare + nr_evid 23 poz | core/test_d100.py (test_scadenta_25_luna_urmatoare_perioadei, test_nr_evid_cifra_de_control) | scadenta/nr_evid gresit | _scadenta_zile(2026,6)=(25,7,2026); XML scadenta="25.07.2026"; nr_evid 23 poz + checksum poz.22-23 |


## 03.08.2026 — Structura P1-P53 D101 verificata (cluster "structura P1-P53")

Temei: OPANAF 206/2025 (D101_A600 v10, d101_struct_anaf.txt). Toate formulele derivate P3-P53 conforme rand-cu-rand.

| gard (EXISTENT) | fisier | ce face imposibil | mutatia |
|---|---|---|---|
| golden lant formule oficiale | core/test_d101.py (test_golden_lant_formule_oficiale) | schimbarea oricarei formule P1-P53 (P3=P1-P2 ... totalPlata_A=sum P1..P53) | golden 419200 pe lantul complet; orice formula gresita cade + proba DUK |

Nu s-a adaugat gard nou: structura era deja acoperita complet de golden + proba DUK (reconstructie 01.08). §9: reaparitia imposibila prin golden-ul pe lantul de formule.


## 03.08.2026 — Gard limita text D112: nume/prenume salariat + functie_declar (cluster "limita text 75")

Temei: structura ANAF D112 0126_030226 - numeAsig/prenAsig C(75), functie_declar C(50).

| gard | fisier | ce face imposibil | mutatia care il probeaza |
|---|---|---|---|
| trunchiere nume salariat + functie 50 | core/test_d112.py (test_limita_75_asigurat_si_functie_declar_50) | numeAsig/prenAsig >75 netrunchiate (respinse) + functie_declar la 74 in loc de 50 | salariat nume 90 car -> numeAsig 74; functie 60 car -> functie_declar 50 |


## 03.08.2026 — Gard cod_oblig <-> cod_bugetar D112 (cluster "nomenclator cod_oblig")

Temei: structura ANAF D112, Nomenclator 3 (Obligatii de plata BS/BASFS). Codurile 602/412/432/480/458/459 conforme.

| gard | fisier | ce face imposibil | mutatia care il probeaza |
|---|---|---|---|
| perechea cod_oblig/cod_bugetar | core/test_d112.py (test_cod_oblig_pereche_cu_cod_bugetar_corect) | inversarea codului bugetar (ex. 480 CAM cu 5503XXXXXX in loc de 20470300XX) | 480 -> 20470300XX; 602/412/432 -> 5503XXXXXX |


## 04.08.2026 — Datorii deschise de campania „implementarile ramase" (registrul canonic)

Campania a livrat 5/7 puncte si a lasat urmatoarele deschise. Cele deja in registru se REFERENTIAZA, nu se
duplica (regula sursei unice). NOI in GARZI:

| datorie | unde | de ce e deschisa | ce o inchide |
|---|---|---|---|
| clasifica_partener infera platitor TVA din FORMA CUI, nu din flag real | core/d394.py:260 (clasifica_partener) | un PJ neplatitor de TVA (CUI valid dar nu inregistrat in scop TVA) nu e distins de o persoana fizica: fara CUI/CUI-invalid -> P_NEINREG (tip 2) -> pe achizitie devine N (exclus + avertisment); CUI numeric valid -> P_TVA_RO (tip 1) desi nu-i platitor. Heuristica pe forma, nu pe realitate | flag `platitor_tva` pe partener in DB (verificare VIES/ANAF), clasificare pe flag nu pe forma. Decizie de produs Costin |
| categorie_331 (taxare inversa / N op11) fara UI | core/d394.py (codpr_N_din_categorie, CODPR) - camp citit, negenerabil din factura | codPR-ul op11 (art.331) si tip N cer CATEGORIA declarata de contabil (cereale/deseuri/masa lemnoasa/gaze...); azi nu exista ecran care s-o seteze -> operatiunile raman neclasificate | ecran pe factura/operatiune care seteaza categorie_331 din nomenclatorul art.331 |
| data_faptului_generator (D390 ziua 15) fara UI | tenant_template.sql + tenant_001 (coloana migrata) | coloana OPTIONALA exista si pull() o foloseste (exigibilitate = MIN(data_emitere, ziua 15)), dar niciun ecran n-o completeaza -> ramane NULL -> comportament = data_emitere (backward-compat, corect, dar functia nefolosibila pana la UI) | camp pe factura IC de completat cand faptul generator difera de data emiterii |
| D177 canal de emitere (formular, nu declaratie XML) | anaf_surse/OPANAF_3562_2024_D177.* (structura salvata) | D177 e o CERERE-formular PDF, nu un XML validat de jar DUK -> nu are autoritatea R17 pe care sta arhitectura; mecanismul (PDF-form vs XML) + scope = decizie de produs | **DECIS 04.08 (Costin): AMANAT EXPLICIT** (vezi sectiunea D177 mai jos + DECIZII 04.08 + FUNCTIONALITATI.csv F206). Se redeschide doar cu decizie noua Costin |

Deja in registru (REFERINTA, nu duplic):
- **tip_document 2-5 (suport N complet D394)** -> sectiunea „04.08 DATORIE: suport COMPLET operatiuni N (D394)".
  Approach a CONDITIONAT livrat (N emis valid cu categorie_331, DUK-probat); ramas doar tip_document 2-5 + UI
  categorie_331. (tip_N a iesit din scope - nu exista in v5.)
- **amortizare MF neliniara (degresiva/accelerata art.28 alin.5-8)** -> Categoria 3, `xfail
  test_datorie_mf_metode_amortizare`. Subsistem MF, impact pe amortizarea contabila/D406, nu pe d101.

SOLD xfail: NESCHIMBAT de campanie (28 markeri in test_datorie.py la baseline 3dbb175 = 28 acum; ~21 xfail runtime).
Datoriile noi de mai sus NU sunt xfail - sunt garduri DATORIE live (N respins de J8 = consemnat), blocaje motivate
in DECIZII, sau goluri de UI documentate. Campania nu a introdus regresii verzi-false.


## 04.08.2026 - D177: DECIZIE DE PRODUS AMANATA EXPLICIT (Costin)

D177 (cerere de redirectionare a impozitului pe profit/micro catre sponsorizare, OPANAF 3562/2024) RAMANE IN AFARA
SCOPE-ULUI - decizie de produs AMANATA EXPLICIT (Costin, 04.08.2026), NU "de facut candva".

Motivul: D177 e o **cerere-formular PDF, nu o declaratie XML** - **nu are validator instalat**. Toata arhitectura de
declaratii se sprijina pe validatorul DUK ca AUTORITATE (principiul R17); D177 ar fi **prima piesa construita pe
interpretarea unui PDF, fara proba mecanica** - exact tiparul care a produs ASI (D394), HRK (D301) si nomenclatorul N
gresit (fiecare: structura pdf spunea un lucru, jar-ul instalat il infirma). In plus: e o cerere **ANUALA**, nu o
obligatie lunara - impact mic fata de riscul de a construi fara ancora de validare.

Structura OPANAF 3562/2024 ramane salvata in anaf_surse/ (OPANAF_3562_2024_D177.pdf/.txt/.sha256 +
d177_structura_note.txt), ca sa nu se re-descarce la o eventuala redeschidere. Se redeschide DOAR cu o decizie noua a
lui Costin (si numai daca apare un mecanism de validare mecanica sau se accepta explicit constructia pe interpretare
de PDF). Consemnat: DECIZII 04.08, FUNCTIONALITATI.csv F206 (Stare AMANAT).
