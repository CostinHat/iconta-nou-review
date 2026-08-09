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
- REZOLVAT (03.08.2026): rotunjirea D390 e ARITMETICA (`_int` = ROUND_HALF_UP, schimbata de la `round()` bancar
  pe 27.07), gardata de `test_d390_rotunjeste_aritmetic_nu_bancar_A91b` + scanul anti-`round()` bancar pe toate
  `d*.py`. [Intrarea initiala DESCHIS-rotunjire-bancara a fost INFIRMATA - pastrata ca traseu.]

### 4. Ieșire către autorități
**Eșec:** XML structural valid, semantic gol sau fals.
**Stare: PARȚIAL.**
- ACOPERIT: `core/duk.py` + `test_duk.py`. Trei stări; **eșecul rulării = gri, nu valid**.
  Un XML nevalidat nu se declară valid. Test: niciun validator nu acceptă gunoi.
- ACOPERIT: `test_ruta_valideaza_trimite_an_si_luna` — leagă ruta de semnătura cerută de
  validatorul SAF-T. Fără el, validarea D406 a fost gri permanent luni de zile.
- ACOPERIT: reconcilierea linii-antet la D406 (divergență între două surse ale aceleiași
  facturi = eroare).
- **ÎN LIVRARE — CAMPANIA GARDUL DE CONTINUT (05.08.2026): a doua cale de reconciliere pe totaluri.**
  Deschisa dupa ce inventarul anaf_surse a confirmat ca directia (a) — golden din exemplu oficial ANAF —
  e BLOCATA LA SURSA: nu exista nicio declaratie ANAF completata cu cifre (structura+instructiuni, nu
  declaratii-model). Deci gardul de continut = recalcul INDEPENDENT al totalurilor, confruntat cu
  generatorul; divergenta = eroare vizibila care numeste ambele valori (NU repara tacit). Ordine
  confirmata: D300 -> D394(vs D300) -> D112 -> D406 -> D101/D205.
  - **D300: ACOPERIT (05.08.2026).** `core/d300_reconciliere.py` — pull SQL propriu al liniilor brute
    (independent de `d300.pull`) + agregare proprie pe cote (independenta de `calcul_d300`/`_segmente`),
    Sigma(baza)xcota, rotunjire aritmetica; confrunta R9/R10/R11 (colectat 21/11/9) si R22/R23
    (deductibil 21/11) cu `res.R`. Poarta in `d300.genereaza` inainte de return. Gard:
    `test_d300_reconciliere.py` — NON-TAUTOLOGIE probata static (calea 2 nu importa/cheama agregarea
    generatorului) + MUTATIE (factura pierduta / cota in bucket gresit / semn inversat -> reconcilierea pica).
  - **LIMITA DECLARATA a gardului D300** (scrisa la DESCHIDERE, ca sa nu para ca acopera mai mult):
    1. Doar randurile AUTOMATE din facturi (colectat 21/11/9, deductibil 21/11). Randurile MANUALE
       (intracom, taxare inversa, ajustari) + orice rand atins prin `manual=` -> NEACOPERIT (sarit,
       nu alarma falsa).
    2. NU acopera pro_rata si lantul R33->R42 (aritmetica determinista pe care DUK o verifica
       formula cu formula) — doar bazele+TVA pe cote, acolo intra riscul de agregare.
    3. `tva_la_incasare`: exigibilitate pe decontari, nu pe emitere -> NEACOPERIT explicit (nu produce
       divergenta falsa; se raporteaza ca nereconciliat).
    4. Eroare de INTRARE partajata (ambele cai citesc aceeasi linie gresita a contabilului) NU se
       prinde — raspunderea contabilului (CLAUDE.md §8).
    5. Cota unei facturi FARA linii e dedusa (total/tva) identic de ambele cai -> o clasificare
       gresita acolo nu se prinde.
    6. Deriva legislativa (cota corecta azi, lege schimbata maine) — alt gard (deschis, nerezolvabil
       mecanic), nu acesta.
  - **D394: ACOPERIT (05.08.2026, pas 2/6).** `core/d394_reconciliere.py` — recalcul INDEPENDENT al
    totalurilor rezumat2 pe cota (colectat bazaL/tvaL + achizitii bazaA/tvaA, C pliat pe A) dintr-un pull
    SQL propriu al liniilor brute + clasificare proprie (emisa->L, primita RO->A, taxare inversa RO->C,
    intracom EXCLUS, cota-0/N/V excluse). Poarta HARD-BLOCK in d394.genereaza. Gard:
    `test_d394_reconciliere.py` (6): non-tautologie pe AST + mutatie (livrare pierduta / livrare clasificata
    la achizitii / semn inversat -> reconcilierea pica, numind ambele valori).
    - NU s-a folosit reconcilierea incrucisata D394<->D300, din doua motive gasite la sursa: (1) gardul
      existent `test_d300_d394_paritate` e TAUTOLOGIC — confrunta calcul_d300 vs calcul_d394 dar ambele
      citesc aceleasi factura_linii (propriul docstring: 'sursa e comuna'); prinde doar DRIFTUL intre
      generatoare, ramane util ca atare, NU e gard de continut. (2) D300 colectat >= D394 livrari L pe
      cota (D300 e TVA totala, D394 subsetul raportabil) -> nu e egalitate, ar da divergenta falsa.
    - **ACOPERIRE (cerinta Costin): tot traficul real D394 e acoperit.** taxare-inversa (C/V) si N (persoane
      fizice) sunt AUTO din facturi (NU prin manual=), deci reconstruibile de calea 2. manual['operatiuni']
      (bonuri/borderouri/AI/AS/LS) = NEACOPERIT, dar NU are UI/tabela care sa-l alimenteze azi (doar body-ul
      cererii) -> reziduu, nu majoritate. Daca apare o UI de operatiuni manuale, gaura devine reala si gardul
      trebuie extins (consemnat aici, nu doar in cod).
    - LIMITA (ca la D300): tipurile cota-0 fara TVA (V/N/LS/AS) = prezenta/clasificare (DUK structural),
      nu sume; input partajat gresit = §8; cota factura-fara-linii dedusa identic.
  - **D112: CAZUL SIMPLU ACOPERIT (05.08.2026, pas 3/6)** — scris ca atare, NU "D112 acoperit".
    `core/d112_reconciliere.py` recalculeaza INDEPENDENT CAS/CASS PER ANGAJAT = brut x cota (din brut, cu
    cotele din common.cota = registrul de lege), DOAR pentru angajatii fara nicio structura care schimba
    formula: brut STRICT peste salariul minim (facilitatea se declanseaza EXACT la brut==minim), fara CM,
    norma intreaga, ne-scutit, fara tichete, luna intreaga. Poarta HARD-BLOCK in d112.genereaza. Gard:
    `test_d112_reconciliere.py` (5): non-tautologie pe lantul de import TRANZITIV (nu ajunge la
    calcul_salariu/salarizare/d112/salariu_istoric nici indirect) + mutatie (cas/cass gresit -> pica,
    numind angajatul si ambele valori) + caz nesimplu SARIT fara alarma falsa.
    - **CE RAMANE IN AFARA (gardul NU acopera, extindere = pas separat):** FACILITATI (constructii/IT/
      agricol, salariu minim), SCUTIRI, PLAFOANE, CONCEDII MEDICALE, IMPOZIT
      (necesita deducerea personala degresiva art.77), CAM. TICHETE: masa -> CAS reconciliat (sub-caz 1b), CASS
      afara; vacanta/cultural/cresa integral afara. Un angajat cu oricare (in afara masei pe CAS) -> NEACOPERIT
      (sarit, nu alarma falsa). Impozit/CAM raman pe DUK structural + golden-ele existente.
    - D112 e cel mai EXPUS la tautologie din campanie (totalurile vin din calcul_salariu); de aceea
      non-tautologia e probata pe lantul TRANZITIV, nu doar pe importurile directe.
    - **ACOPERIRE ESTIMATA (nu 'D112 are a doua cale'):** la o structura TIPICA de cabinet RO, gardul
      reconciliaza probabil o MINORITATE a salariatilor — estimat ~20-35% reconciliati / ~65-80% sariti.
      **EXTINDERE 05.08 (Punctul 1, sub-caz 1a):** facilitatea la minim TOATA luna, full-time, stabila (fara
      schimbare de salariu in luna) e ACUM reconciliata (baza=sm-facilitate, CAS+CASS). Acoperire estimata
      urcata la ~30-45% (estimare, nemasurata; suprapunerea minim x TICHETE ramane la sub-cazul urmator 1b).
      Facilitatea PRORATATA (schimbare in luna) ramane sarita NUMIT.
      **EXTINDERE 05.08 (sub-caz 1b):** angajatii PESTE minim cu TICHETE DE MASA (fara alte beneficii) sunt ACUM
      reconciliati pe CAS (tichetele de masa nu ating baza CAS - salarizare.py:203-236). CASS ramane NUMIT-AFARA:
      CASS-ul EMIS = salarial (brut x cota_cass) + cass_tichete (d112.py:239); a-l recalcula = tautologie cu motorul
      de tichete + dependenta de pontaj. Combo minim+tichete ramane sarit. Acoperire estimata ~30-45% -> ~35-50%
      (estimare, nemasurata; pe tichete reconciliaza DOAR CAS, nu si CASS).
      **EXTINDERE 05.08 (sub-caz 1c-PT):** angajatii PART-TIME (luna intreaga, ne-scutiti, fara CM/tichete) sunt ACUM
      reconciliati COMPLET (CAS+CASS) pe baza RIDICATA la nivelul minim (art.146 alin.5^6): emisul per angajat =
      cas_min_pt/cass_min_pt (0<brut<prag, diferenta pe angajator B4_8D/B4_6D) sau cas/cass (brut>=prag) =
      max(brut, sm-facilitate) x cota. prag recalculat INDEPENDENT (sm-facilitate din registru); full month fara CM ->
      fara proratare/pontaj. Acoperire estimata ~35-50% -> ~40-55% (nemasurat). Ramas la 1c: CONCEDIILE MEDICALE.
      Excluderile dominante: salariu MINIM (facilitate; pondere mare la IMM-uri RO) + TICHETE de masa
      (beneficiu larg raspandit) — se suprapun si domina, plus CM/part-time. ESTIMARE PE STRUCTURA, NU
      MASURATA (tenantii de test sunt goi/sintetici; nu exista payroll real). De reverificat cu cifra
      reala cand exista date. Consecinta: gardul acopera cazul simplu al celei mai grele declaratii lunare,
      nu majoritatea ei — util, dar declarat ca acoperire partiala.
    - **SKIP-SUSPECT vs SKIP-LEGITIM (cerinta Costin):** un angajat EMIS cu DATE CORUPTE nu mai cade tacit
      in 'afara'. brut LIPSA (istoric+salariati.salariu_brut ambele goale -> generatorul emite pe 0) si
      brut SUB minimul legal (full-time luna intreaga) = skip-SUSPECT -> HARD-BLOCK semnalat ('null base =
      eroare pana la proba contrarie'). Skip-legitim (facilitate/CM/part-time/scutire/tichete/luna partiala)
      ramane tacut. Probat: brut NULL / brut 3000<minim -> ridica; facilitate la minim -> tacut.
  - **D406/SAF-T: GeneralLedgerEntries ACOPERIT (05.08.2026, pas 4/6).** `core/d406_reconciliere.py`
    construieste o BALANTA DE RULAJE per cont INDEPENDENTA din inregistrari_linii (SQL propriu) si o
    leaga de totalurile per-cont din SAF-T-ul emis (res.note) + invariant Sdebit=Scredit. Poarta
    HARD-BLOCK in d406.genereaza. Gard: `test_d406_reconciliere.py` (5): non-tautologie AST + mutatie
    (suma alterata / GeneralLedgerEntries GOL = bug-ul istoric 16.07 / dezechilibru dubla partida).
    Prinde exact clasa bug-ului istoric (GL ramanea gol tacit printr-un except:pass) - calea 2 gaseste
    notele in DB si STRIGA.
    - LIMITA: acopera GeneralLedgerEntries (dubla partida a notelor). NU acopera SalesInvoices/
      PurchaseInvoices/Payments/Assets/MovementOfGoods (reconcilierea linii-antet facturi exista deja
      partial, mai sus). Sdebit=Scredit e in mare parte STRUCTURAL (fiecare inregistrari_linii =
      debit+credit egale); valoarea reala = legarea per-cont la rulaj (prinde drop/dubla/mapare la EMISIE).
      Input partajat gresit (aceeasi linie gresita citita de ambele cai) = §8.
  - **D101: PROFIT CONTABIL ACOPERIT (05.08.2026, pas 5/6)** — scris ca atare, NU "D101 acoperit".
    `core/d101_reconciliere.py` recalculeaza INDEPENDENT P1/P2/P4/P5 (venituri/cheltuieli exploatare+financiar,
    clasele 7/6) din inregistrari_linii si le confrunta cu res.P. NU verifica profitul IMPOZABIL P9: ajustarile
    fiscale (P6/P7/P8...) sunt intrari MANUALE ale contabilului (§8) iar P9 = formula pazita de golden. Poarta
    HARD-BLOCK. Gard: test_d101_reconciliere.py. LIMITA: doar contabilul; impozabilul ramane pe golden + §8.
  - **D205: dividende ACOPERIT (05.08.2026, pas 6/6).** `core/d205_reconciliere.py` recalculeaza INDEPENDENT
    baza+impozitul per beneficiar (Σ cont 457 x cota asociat x cota impozit din registrul de lege) si le
    confrunta cu res.beneficiari. NU cross-check cu D100 (D100 deriva impozitul din ACEEASI distributie 457 =
    same-source trap, ca paritatea D300/D394) - probat pe AST ca e cale proprie. Poarta HARD-BLOCK. Gard:
    test_d205_reconciliere.py. LIMITA: beneficiari manuali (§8).
  - **CAMPANIA GARDUL DE CONTINUT — COMPLETA (6/6, 05.08.2026):** D300, D394, D112(caz simplu), D406(GL),
    D101(contabil), D205. Categoria "Iesire catre autoritati" trece de la "DUK valideaza doar structura" la
    "totalurile de pe suprafetele acoperite sunt reconciliate pe a doua cale, hard-block la divergenta".
    ACOPERIRE PARTIALA per declaratie, DECLARATA (vezi fiecare intrare) - NU acoperire totala.
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
- ACOPERIT (31.07): gard că fiecare `test_*.py` (exclus venv) are ≥1 funcție `def test_` — `core/test_agenda.py::test_fiecare_fisier_test_are_cel_putin_un_test`, cu mutație. Un `test_*.py` cu 0 teste e script deghizat în suită (pytest nu-l colectează, dar numele sugerează acoperire). Prins pe `test_gdpr_functional` → redenumit `gdpr_functional.py`. [citare-istorica: redenumit gdpr_functional.py 31.07]
- ACOPERIT (punct orb al garzii anti-stale, gasit + REPARAT 04.08): un test ȘTERS dar inca citat in coloana `functie` a unui
  cluster cu MAI MULTE fisiere SCAPA `test_agenda::test_verificarile_A`. `_fisier_functie` cade pe fisier[0] cand
  functia nu-i in niciun fisier -> compara `<ABSENT>` vs `<ABSENT>` -> NEstale. Dovada empirica: bifa
  `taxare inversa|d394` a citat `test_datorie_gaze_naturale_...` mult dupa ce testul fusese scos (6675f19), suita [citare-istorica: scos la inchiderea datoriei gaze 6675f19]
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
| ~~datorie gaze naturale (lit.l)~~ INCHIS 04.08 (commit 6675f19) | gaze in motor taxare_inversa.CATEGORII (lit.l) + d394.CODPR 36, probat DUK cod-cu-cod; xfail test_datorie_gaze_naturale_... SCOS la inchidere. Gard curent: test_codpr_valide_pe_validatorul_curent | (rezolvat) | (rezolvat) | [citare-istorica: scos la inchiderea datoriei gaze 6675f19]

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
| ~~datorie period-awareness istorica~~ INCHIS 04.08 (commit 6675f19) | valorile HG istorice confirmate la sursa (HG 714/2018 + HG 518/1995 salvate in anaf_surse/, Ordin MF 1235/2023); diurna period-aware in deconturi.py, gard test_plafon_diurna_dispecer_versionat | (rezolvat) | (rezolvat) |

Calculul CURENT (2023+) conform art.76 alin.(4^1). Istoric (pre-2023) DEBLOCAT 04.08 (6675f19): valorile HG diurna confirmate la sursa (HG 714/2018, HG 518/1995).


## 03.08.2026 — Credit sponsorizare: profit conform + datorie micro period-aware (cluster "credit sponsorizare / D177")

Temei: CF art.25 alin.(4) lit.i (profit: min 0,75% CA / 20% impozit + registru); fostul art.56 alin.1^5 (micro, abrogat OUG 115/2023).

| gard | fisier | ce face imposibil | mutatia care il probeaza |
|---|---|---|---|
| ~~datorie micro period-aware~~ INCHIS 04.08 (commit 6675f19) | textul istoric art.56 alin.1^5 confirmat la sursa; xfail test_datorie_credit_sponsorizare_micro_period_aware SCOS la inchidere | (rezolvat) | (rezolvat) | [citare-istorica: scos la inchiderea datoriei micro 6675f19]

Profitul e gardat de test_operatiuni_speciale.py (4 teste existente). Micro DEBLOCAT 04.08 (6675f19): textul istoric art.56 alin.1^5 confirmat la sursa.


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
| TIPURI = exact setul din structura oficiala | core/test_d394.py (test_TIPURI_e_setul_validatorului_curent) [redenumit] | un tip adaugat/scos tacit din cod, divergent de validator | orice modificare a TIPURI care nu-i setul validatorului pica |
| ~~ASI respins = datorie~~ REZOLVAT 03.08 (greenlight Costin: ASI SCOS din cod, aliniere validator J8; OPANAF 77/2022 fost-ASI->AS) | gard devenit INVERS: test_asi_ramane_scos_gard_invers (daca validatorul re-accepta ASI, pica si cere reevaluare) | ASI nu mai e in TIPURI | (rezolvat) |


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
| clasifica_partener infera platitor TVA din FORMA CUI, nu din flag real | core/d394.py:260 (clasifica_partener) | un PJ neplatitor de TVA (CUI valid dar nu inregistrat in scop TVA) nu e distins de o persoana fizica: fara CUI/CUI-invalid -> P_NEINREG (tip 2) -> pe achizitie devine N (exclus + avertisment); CUI numeric valid -> P_TVA_RO (tip 1) desi nu-i platitor. Heuristica pe forma, nu pe realitate | **REZOLVAT 05.08 (decizie Costin: inghet-la-creare)**: clasifica_partener(cui, platitor_tva) consulta `facturi.tert_platitor_tva` (fapt INGHETAT la creare, imutabil); True->tip1, False->tip2/N, NULL->euristica de forma (legacy). Vezi sectiunea + DECIZII 05.08. LIMITA legacy scrisa mai jos |
| categorie_331 (taxare inversa / N op11) fara UI | core/d394.py (codpr_N_din_categorie, CODPR) - camp citit, negenerabil din factura | codPR-ul op11 (art.331) si tip N cer CATEGORIA declarata de contabil (cereale/deseuri/masa lemnoasa/gaze...); azi nu exista ecran care s-o seteze -> operatiunile raman neclasificate | SIMPTOM al neconformitatii 04.08 de mai jos (operatiune achizitie scrisa DOAR in jurnal): achizitie_taxare_inversa nu creeaza rand `facturi` -> categorie_331 n-are purtator. Fix = BACKEND (operatiunea emite factura), NU ecran. Vezi sectiunea NECONFORMITATE ACTIVA 04.08 + DECIZII 04.08 |
| data_faptului_generator (D390 ziua 15) fara UI | tenant_template.sql + tenant_001 (coloana migrata) | coloana OPTIONALA exista si pull() o foloseste (exigibilitate = MIN(data_emitere, ziua 15)), dar niciun ecran n-o completeaza -> ramane NULL -> comportament = data_emitere (backward-compat, corect, dar functia nefolosibila pana la UI) | SIMPTOM: achizitie_ic scrie DOAR in jurnal, fara rand `facturi` -> data_faptului_generator n-are purtator SI D390 rateaza operatiunea. Fix = BACKEND. Vezi NECONFORMITATE ACTIVA 04.08 |
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


## 04.08.2026 — NECONFORMITATE ACTIVA: operatiune de achizitie scrisa DOAR in jurnal (fara rand facturi) -> absenta din D390/D394

Reincadrare (CAUZA, nu simptom): fostele datorii „UI categorie_331" / „UI data_faptului_generator" descriau
simptomul (lipsa unui camp in ecran). Cauza reala, dupa harta facturi<->inregistrari (investigatie 04.08, DECIZII
04.08): `achizitie_ic` (main.py:7077) si `achizitie_taxare_inversa` (main.py:7019) inregistreaza operatiunea DOAR in
stratul-jurnal (`inregistrari` + `inregistrari_linii`, nota 401/4426=4427), FARA `factura_id` si FARA rand in `facturi`.

EFECT FISCAL NUMIT: `facturi` e sursa citita de D390 (VIES) si D394; `inregistrari` de D100/D101/D205. Deci o
**achizitie intracomunitara introdusa prin operatiuni_ecran.js NU ajunge in D390** (declaratie VIES LUNARA OBLIGATORIE),
desi D100/D101/D205 o vad. Aceeasi operatiune: prezenta intr-o declaratie, absenta din alta. Analog, o achizitie cu
taxare inversa (art.331) nu ajunge in D394 op11.

FEREASTRA DE NOROC: tenant_001 are 0 facturi si 0 inregistrari - nicio operatiune n-a fost inca lovita in productie.
Defectul e LATENT, nu declansat. De reparat INAINTE sa existe date reale.

CLASA (NU „arbori paraleli" cat.8): nu e a doua implementare a aceluiasi generator. `facturi`/`inregistrari` sunt
straturi COMPLEMENTARE (factura = sursa; inregistrarea = derivata; legate prin `factura_id`). Clasa reala =
„scriere pe un singur strat" - operatiunea omite stratul-factura pe care il citesc generatoarele TVA/VIES.

FIX DECIS (DECIZII 04.08): operatiunea de achizitie emite intai un rand `facturi` (tert, directie=primita,
categorie_331 la taxare inversa, data_faptului_generator la IC), apoi contabilizeaza cu `factura_id` legat.
Gard anti-regresie de CLASA: `test_nicio_achizitie_creeaza_inregistrare_orfana_de_factura` (scan AST pe main.py) -
orice handler `achizitie_*` care insereaza `inregistrari` sursa='facturi' fara `factura_id` pica.

REZOLVAT 04.08 (backend + UI operatiuni_ecran.js, probe DUK end-to-end in core/test_achizitii_factura.py):
- achizitie_ic -> factura primita (furnizor UE) + factura_id -> D390 DUK-valid.
- achizitie_taxare_inversa -> factura + factura_id + categorie_331->codPR -> D394 op11 DUK-valid.
- achizitie_necorporala -> factura + factura_id (MF/amortizare NEATINSA - imobilizarea ramane separata; efect
  D406/amortizare consemnat) -> D394 tip A DUK-valid.
- achizitie_neinregistrat (N, tip nou) -> factura tert fara CUI (tip_partener 2) + factura_id + categorie_331 lit.D
  optionala -> D394 op N DUK-valid (fara categorie: N exclus cu avertisment, nu se ghiceste).

EXCEPTIE NUMITA (NU tacita - gardul o listeaza in EXCEPTATE cu motivul): **achizitie_agricultor** ramane orfan de
factura si NECONFORMITATE DESCHISA. Motiv verificat la sursa (CF art.315^1): agricultorul forfetar NU colecteaza TVA
si NU e inregistrat in scop TVA (alin.4); compensatia 8% e deductibila de cumparator ca TVA (alin.17) - dar
tratamentul in D394 al achizitiei de la agricultorul forfetar (tip_partener? intra in baza? sub ce forma?) NU e
confirmabil la sursa (niciun ghidaj in d394_struct_anaf.txt / instructiuni). Un rand facturi construit gresit ar
produce o linie D394 eronata - mai rau decat orfan. D300 e deja acoperit (4426 din inregistrari). Se deblocheaza cu
temeiul D394 confirmat la sursa. Vezi DECIZII 04.08.


## 05.08.2026 — clasifica_partener pe flag INGHETAT (nu forma CUI) — REZOLVAT + limita legacy NUMITA

REZOLVAT (decizie Costin, inghet-la-creare): `clasifica_partener(cui, platitor_tva)` (core/d394.py) consulta acum
statutul TVA REAL al tertului, INGHETAT pe factura (`facturi.tert_platitor_tva`, migrare_tert_platitor_tva) ca fapt
contabil imutabil - nu mai infera din FORMA CUI-ului. RO cu CUI valid: True->tip 1 (inregistrat); False->tip 2
(neinregistrat scop TVA, chiar cu CUI: PJ neplatitor/PF) -> pe achizitie N; NULL (legacy)->euristica de forma.
Corectitudine ISTORICA gratis: acelasi CUI, doua facturi cu flag diferit -> doua clasificari (2022 True->tip1,
2025 False->tip2). Handlerele achizitie ingheata flag-ul la creare (best-effort ANAF F004, fallback semantica:
N->False, taxare inversa->declaratia furnizor_platitor_tva, necorporala->True). anaf_api: pastreaza acum perioade_TVA[]
INTREG (nu doar perioada activa) - datele necesare backfill-ului. Probe: test_clasifica_partener_consulta_flag_nu_forma
+ test_flag_inghetat_da_raspunsuri_diferite_pe_facturi_ale_aceluiasi_cui + test_handlerele_ingheata_flagul_la_creare.

LIMITA LEGACY (DATORIE NUMITA, cu trigger de declansare - nu cod mort acum): facturile create INAINTE de camp
(tert_platitor_tva NULL) sunt clasificate pe EURISTICA de forma (un CUI valid presupus platitor). Pe tenant_001 (0
facturi) backlog inexistent -> backfill-ul ar fi cod nefolosit pe presupuneri despre date care nu exista, deci NU se
scrie acum. DECLANSATOR EXPLICIT: cand un tenant are facturi legacy fara tert_platitor_tva, backfill via
anaf_api.valideaza_cui(...).tva_perioade[] (data facturii ∈ [inceput, sfarsit] perioada inregistrata) devine NECESAR
INAINTE de generarea D394 pe perioade vechi. Datele exista (perioade_TVA pastrat intreg); doar aplicarea lipseste.

ALTA LIMITA (acceptata): decalaj snapshot ANAF (corectie retroactiva a inregistrarii nu actualizeaza flag-ul inghetat
- flag = ce se stia la data facturii, ca orice fapt contabil); ANAF-jos la creare -> flag NULL -> euristica (nu se
blocheaza emiterea facturii).

## INVENTAR DESCHISE NON-CAMPANIE (index canonic, 05.08.2026) — SURSA UNICA; se ACTUALIZEAZA, nu se recolecteaza

Recoltat din 4 surse (cele 21 xfail din core/test_datorie.py, categoriile 1-11 de mai sus, FUNCTIONALITATI.csv,
`python -m core.agenda`) la commit ea0a9f0. Fiecare linie TRIMITE la locul canonic (cat.N de mai sus / xfail nume /
CSV Fxxx / sectiune datata) — NU copiaza textul. La inchiderea unui element se scoate de aici + intra in ISTORIC.
EXCLUS explicit: campania EXTINDEREA ACOPERIRII (P1 D112 complex facilitate/tichete/CM/part-time, P2 D101 impozabil,
P3 amortizare MF neliniara, P4 D394 tip_document 2-5) — traieste in TESTE.md fir + PREDARE_LANT.md, nu aici.
La revenire se re-ruleaza DOAR `python -m core.agenda` pentru xfail-uri; restul se citeste de aici.

### A. ACTABIL AZI (depinde DOAR de munca)
- **Gard NOT NULL pe bani + cheie unica import + idempotenta** — cat.1 (LIPSA). Efect: intrare inghitita -> 0 tacut.
- **audit_cod_schema.py pe server + SELECT* la d394/bilant_api/rip_api/stocuri_cv_api/reconciliere_api** — cat.2 (LIPSA). Prototip exista LOCAL (27.07), de dus pe server + extins. Efect: query pe coloana inexistenta.
- **Gard care interzice cote literale in cod (`*0.19`) + golden pe cifre calculate manual din exemplu** — cat.3 (LIPSA).
- **Snapshot de regresie pe fixturi inghetate (iesire ANAF)** — cat.4 (LIPSA). DUK valideaza structura, nu continutul.
- **Test acces incrucisat (obiect alt tenant -> 404) + gating admin inconsecvent** — cat.6 (LIPSA + DE_FACUT poz.7). Efect: IDOR / rol inconsecvent.
- **Job nocturn Sdebit=Scredit per perioada/tenant + orfani + reluare automata a probei de restaurare** — cat.7 (LIPSA).
- **Gard care prinde aparitia unei a doua copii a unui generator** — cat.8 (LIPSA).
- **Mutant zero sistematic (fiecare generator fortat sa intoarca [] -> suita rosie)** — cat.9 (LIPSA azi ad-hoc).
- **Izolare tenant pe BODY/query (POST /coada, POST /declaratii/{tip}) + 1 conexiune bruta in sinteza_zilnica.py** — cat.5 (LIMITA).
- **D406 SAF-T lunar NEDEPUNABIL: SourceDocuments emite 1 linie sintetica/factura (nu liniile reale) + Payments gol** — CSV F035 (+F037 Stocuri, aceeasi familie). Efect MARE: familia D406 lunara nu se poate depune pana la reparare.
- **xfail d710 trunchiere in garda** — test_datorie:139. De adaugat in CERERI cand se stie profilul care il datoreaza.
- **xfail gard_structura_absent** — test_datorie:184. Cere o forma de marcare care distinge citarea de proza.
- **xfail cota_cea_mai_mica_valoare_din_luna** — test_datorie:206. Nu musca acum (o valoare/luna). Implementare + DECIZII.
- **xfail verificatorul_nu_e_el_insusi_testat** — test_datorie:291. Fixturi cod known-good/known-bad pe analizatorul verificatorului.
- **xfail factura_pdf_proba_pe_profil_real** — test_datorie:280. Proba bytes valizi pe profil firma/factura complet.
- **xfail d394_scutit_catre_cui_proba_duk** — test_datorie:274 (D394, NU tip_document). Proba DUK pe factura multi-cota.
- **xfail deducere_copil_parinte_multi_angajatori** — test_datorie:199. Cere fluxul de declaratie parinte (unic parinte / anti-dubla), apoi cod.
- **Backfill legacy clasifica_partener** — sectiunea 05.08 (l.~1045). Datele exista; DECLANSATOR: primul tenant cu facturi legacy fara tert_platitor_tva, inainte de D394 pe perioade vechi.
- **F103 alerte legislative: data PROGRAMATA a afisarii + flux monitor->propunere anunt in admin** — CSV F103.
- **F163 frictiune permisiuni (admin default nu poate depune) pe control incrucisat D390 vs D300** — CSV F163 / DE_FACUT.
- **state_plata: persistare la emitere cu hash** — test_datorie:145. DECIS 05.08 (Costin, vezi DECIZII): statul se ingheata la emitere (snapshot+hash), reafisarea citeste snapshotul. Efect: un stat dat salariatului nu se mai schimba la reafisare dupa o schimbare de cota.
- **Sweep TVA 21% hardcodat in ~15 module -> cota din registru** — test_datorie:235 (felia INTAI din teste_care_apara_buguri). DECIS 05.08. Efect: la schimbarea cotei TVA, modulele nu mai declara 21% obsolet. [Restul ~70 teste fara temei = mai jos, cu declansator.]
- **xfail staleness_sesiune_b_content** — test_datorie:162. Nimic de facut DIRECT: se inchide singur cand apar testele N3 (Faza 1, azi neinceputa 0/11). Gated intern pe Faza 1, nu extern.
- **teste_care_apara_buguri: restul ~70 teste (dupa felia TVA-21%)** — test_datorie:235. Constante fiscale asertate fara temei, non-TVA-21%. DECLANSATOR: plan sistematic separat (dupa felia TVA-21%), sau urmatoarea schimbare de cota pe un modul afectat.

### B. BLOCAT EXTERN (nu se deblocheaza prin efort — consemnat cu DECLANSATOR)
- **[REPARAT tura 5+6] Emisia D112 CM: (baza) proratata pe zile lucrate - d112_cm_baza_realizata_v1, DUK valid; (poarta) cale2 D112 pe valorile EMISE post-generare - doar D112 afectat (restul res==emis). RAMAN DESCHISE: (2b) rotunjire Sigma(round) vs round(total) B4_8=ROUND(B4_7*25%); (1c-CM) reconcilierea CM propriu-zisa, acum DEBLOCATA de poarta pe emis.** - sectiuni GARZI 05.08 tura 3/4/5/6.
- **Deriva legislativa (cota corecta azi, lege schimbata maine)** — cat.3 LIMITA REALA (l.~129). Declansator: feed legislativ mecanic (inexistent) SAU revizuire manuala periodica. NU se incepe acum.
- **Deadman extern pe joburi (server jos = nici verificatorul nu ruleaza)** — cat.10 LIMITA (l.~467). Declansator: monitor extern.
- **xfail temeiuri_toate_redare (12 COTE + 6 functii pe nivel_sursa=REDARE, niciun MO verbatim)** — test_datorie:46. Declansator: captare verbatim de la legislatie.just.ro (doc consolidat prea mare pt fetch azi).
- **xfail reguli_validator_verificate_la_sursa (8 coduri DUK/eFactura re-verificate)** — test_datorie:169. Declansator: documentatia de validator.
- **xfail d300_d394_randuri_vs_reguli_verificate (R17/R28/R32 dedus din context)** — test_datorie:177. Declansator: structura oficiala D300/D394.
- **xfail d300_9pct_deductibil_auto (DUK INSTALAT respinge R75)** — test_datorie:297. Efect: 9% deductibil doar MANUAL (altfel TVA supraevaluata). Declansator: validator DUK accepta R75 sau randul corect la sursa.
- **xfail d205_trunchiere_neexercitata** — test_datorie:127. Declansator: firma reala cu dividende.
- **xfail d390_trunchiere_neexercitata** — test_datorie:133. Declansator: firma reala cu achizitii intracomunitare.
- **xfail deducere_45pct_4plus_neconfirmat_la_mo (art.77 alin.4)** — test_datorie:191. Declansator: tabelul alin.4 verbatim in MO.
- **Calcul salarial pre-2026 indisponibil (plafon facilitate/tichete 2025 neverificate)** — sectiunea l.~143. Declansator: backfill valori 2025 la sursa (candidat OUG 115/2023), NU prin estimare.
- **Plafon cresa 740 neaplicat (cap conservator 450)** — l.~183. Declansator: textul operativ al ordinului + mecanism ferestre datate pe plafon_cresa.
- **achizitie_agricultor orfan de factura (NECONFORMITATE DESCHISA)** — l.~1026. Declansator: temeiul D394 al achizitiei de la agricultorul forfetar la sursa (CF art.315^1). = "agricultorul forfetar", exceptia numita a campaniei.
- **F121 e-Transport: round-trip live upload/UIT** — CSV F121. Declansator: CIF real cu drept e-Transport.
- **F178 e-Factura cron poll: round-trip incarcat->ok** — CSV F178. Declansator: CIF cu drept (ca F176).
- **xfail citate_literale_tichete_portal (art.25(3) b/c + art.78(2)a verbatim)** — test_datorie:227. Declansator: PDF MO verbatim. [Nota: reconcilierea tichetelor = 1b LIVRAT; asta e doar citarea la sursa, ramasa.]

### C. DECIZIE LUATA (amanat/respins/eliminat — NU se reia fara decizie noua)
- **D177 (cerere-formular PDF, fara validator)** — l.~975 / CSV F206. AMANAT EXPLICIT 04.08 (Costin). Redeschide DOAR cu decizie noua + mecanism de validare mecanica.
- **F127 transmitere declaratii direct la ANAF** — CSV F127. AMANAT 17.07 (nu exista API depunere; ramane DUK + upload SPV). De confirmat cu spv.webservice@mfinante.ro inainte de RESPINS definitiv.
- **F128 monitorizare mesaje SPV (SPVWS2)** — CSV F128. AMANAT 17.07, blocant structural mTLS cu certificat calificat local. Redeschide DACA ANAF adauga OAuth la SPVWS2.
- **F175 D307** — CSV F175. AMANAT 18.07 (exceptie rara, la caz real).
- **F193 D207 nerezidenti** — CSV F193. AMANAT 20.07 (nisa, la caz real).
- **F132 import borderouri curieri/procesatori card** — CSV F132. AMANAT 20.07 (la primul client e-commerce cu fisier real).
- **F138 transfer intre gestiuni Tier 3 (CMP separat per depozit)** — CSV F138. AMANAT (la testare).
- **F123 provider real de plata (Netopia/Stripe)** — CSV F123. PLANIFICAT (azi mock).
- **F130 Open Banking PSD2** — CSV F130. PLANIFICAT.
- **F148 arhivare cloud extern (Drive/OneDrive)** — CSV F148. PLANIFICAT.
- **F195 D094** — RESPINS 20.07 (inglobat in D700). **F185 cont gratuit** — ELIMINAT 26.07.
- **F144 GV fara profit/produs (cost pe articol inexistent)** — CSV F144. LIMITARE ACCEPTATA, documentata (DECIS 05.08, Costin). Redeschide DOAR cu decizie noua de a construi cost pe articol in GV.

### D. CERE DECIZIE DE PRODUS (Costin) inainte de a fi actabil (NU blocaj extern, NU inca decis)
- **Prag inregistrare TVA 395.000 lei NEENFORCED** — CF art.310 via OG 22/2025 art.I pct.11 (MO 806/29.08.2025).
  `platitor_tva` e camp DECLARAT (core/vector_fiscal_api.py:78-91), nu calculat din cifra de afaceri; aplicatia NU
  semnaleaza depasirea pragului de scutire (nici notificare, nici blocaj). Confruntat cu codul 05.08 (pre-C-2): niciun
  literal 395000/300000 in cod, art.310 neimplementat. DECIZIE DE PRODUS (Costin): daca/cum se enforceaza (alerta la
  depasire vs. ramane responsabilitatea contabilului). NU se repara acum. Descoperit la confruntarea celor 4 corectii C-1.
- [istoric] cele 3 deschideri D initiale au fost DECISE 05.08 (vezi DECIZII 05.08 "3 decizii de produs pe inventar"):
  state_plata -> A (persistare cu hash); felia TVA-21% -> A (restul teste_care_apara_buguri ramane in A cu declansator);
  F144 GV -> C (limitare acceptata). Cand apare o noua deschidere blocata pe decizie de produs, se adauga aici.


## 05.08.2026 - DESCOPERIRE (campanie EXTINDEREA ACOPERIRII, sub-caz 1c-CM): poarta cale2 OARBA pe CM + divergenta fluturas/declaratie pe baza salariala CM

Sub-cazul 1c-CM (reconciliere contributii concedii medicale) s-a OPRIT INAINTE de cod. Reteta din PREDARE_LANT.md
presupunea ca g[cas]/g[cass] vazute de cale2 contin valoarea EMISA la ANAF. FALS - verificat empiric pe generatorul
REAL (sonda efemera rollback: 1 salariat brut 8000 peste minim, 2 certificate cod 01, iunie 2026, nzl=21, 10 zile CM).
Ambele descoperiri de mai jos sunt masurate, nu presupuse.

FINDING 1 - poarta cale2 e OARBA pe componenta CM.
  verifica_reconciliere(conn,schema,an,luna,salariati) (d112.py:551) primeste iesirea pull. Pentru un angajat cu CM,
  pull seteaza (d112.py:498-499) s["cas"]=calcul_salariu(brut_lucrat)["cas"] = DOAR salariul pe brut_lucrat PRORATAT,
  FARA cm_cas. Masurat: g[cas]=1047.62, g[cass]=419.05 (brut_lucrat=8000x11/21=4190.48).
  Valoarea EMISA la ANAF se calculeaza abia in _d112_genereaza (d112.py:199-200), DUPA poarta: B4_8(cas)=4323 =
  _d112int(bazac x 0.25) + cm_cas = 2000 + 2323; B4_6(cass)=1729 = 800 + 929. Nu ajunge NICIODATA la cale2.
  => a reconcilia g[cas] valideaza un numar care NU se depune la ANAF (1047.62 vs 4323 emis) - falsa incredere,
  exact riscul semnalat de Costin ("mai rau decat lipsa gardului"). CM NU e reconciliabil prin interfata curenta.
  GENERALIZARE (blind-spot al portii): poarta valideaza valorile PRE-emisie (salariati din pull). Pt cazurile simple
  emit = _d112int(s["cas"]) deci coincid; pt CM emit RECALCULEAZA din bazac+certificate deci NU coincid. Poarta nu
  poate prinde niciun bug al layerului de EMISIE care recalculeaza (nu doar CM).

FINDING 2 - candidat BUG de generator (miza mare, DECIZIE DE PRODUS): baza salariala CAS/CASS in CM difera intre cele
doua lanturi ale generatorului.
  fluturas/pull: salariul se PRORATEAZA pe zile lucrate (brut_lucrat=4190.48 -> cas salariala 1047.62). d112.py:469,482,498.
  declaratie/emit: salariul se ia pe brut INTREG (bazac=_d112int(s["brut"])=8000 -> cas salariala 2000). d112.py:146-148,199;
  s["brut"]=salariu_brut CONTRACTUAL (l.424), NErescris niciodata cu brut_lucrat (desi brut_lucrat E in dict, l.496).
  => acelasi angajat: CAS salariala 1047.62 pe fluturas, 2000 in D112 la ANAF (dif ~952 lei/angajat-luna). Incalca
  invariantul propriu al codului ("arbori paraleli acelasi rezultat" - test_cm_arbori_paraleli_acelasi_rezultat, care
  insa verifica DOAR tratamentul indemnizatiei cod-08, nu baza salariala; niciun golden nu blocheaza baza salariala CM).
  Daca emisul pe brut intreg e gresit -> SUPRA-declarare CAS/CASS la ANAF pe TOTI angajatii cu CM peste minim.
  Care baza e corecta legal (proratat pe zile lucrate vs brut intreg) = decizie de produs + verificare OUG 158/2005 +
  CF art.139/140 la sursa. NU se repara unilateral (schimba iesirea la ANAF, §2.3 pct.2). Xfail-ancora NEscrisa inca:
  cere valoarea CORECTA, indecisa pana la decizie.

ROTUNJIRE (rezolvata la sursa, pt cand se reia): cm_cas per-certificat = ROUND_HALF_EVEN - taxe_cm (salarizare.py:576)
face (b*cota).quantize(Decimal("1")) FARA rounding=, deci context default BANCAR; wrapper-ul _d112int(_xt["cas"])
(d112.py:192) e no-op (valoare deja intreaga). Partea salariala = ROUND_HALF_UP (_d112int). Doua moduri diferite in
ACEEASI suma. Masurat: cm_cas half-even=2323 vs half-up=2324 (certificate 4650/4645). O implementare cu un singur mod
ar diverge fals de 1-2 lei pe _xb=2(mod4). = capcana pe care Costin a cerut-o rezolvata inainte de cod: rezolvata.

DECIZIE CERUTA (Costin), NUMEROTAT:
  1. Baza salariala CAS/CASS in CM la ANAF = PRORATAT pe zile lucrate (ca fluturasul) sau BRUT INTREG (ca emisul azi)?
     Blocheaza Finding 2 (posibil over-declarare) SI orice reconciliere CM corecta.
  2. Se re-arhitecteaza poarta cale2 sa primeasca valorile EMISE (post-_d112_genereaza), nu pre-emisie, ca sa poata
     reconcilia CM si sa acopere blind-spot-ul general al layerului de emisie? Blocheaza Finding 1.
  Pana la 1+2, 1c-CM ramane BLOCAT; urmatorul sub-caz actionabil FARA decizie = Punctul 2 (D101 ajustari computed).


## 05.08.2026 (tura 4) - VERIFICARE LA SURSA 1c-CM (Costin, Decizia 1): Finding 2 CONFIRMAT ca NECONFORMITATE FISCALA ACTIVA + a doua neconformitate pe acelasi rand (rotunjire)

Costin a cerut verificarea la sursa a bazei CAS/CASS in luna cu CM (brut intreg vs proratat). Sursa e CLARA -> baza
proratata (castig REALIZAT); emisia D112 pe brut intreg = neconformitate CONFIRMATA. NU s-a reparat inca: domeniul
fix-ului a crescut peste intrebarea initiala (vezi mai jos), iesire ANAF -> scop cerut Costin inainte de mutatie.

SURSA (comenzi + citat):
  CF art.139(1) - cod_fiscal_227_2015_consolidat.html (extras prin strip HTML): "Baza lunara de calcul al
  contributiei de asigurari sociale, in cazul persoanelor fizice care realizeaza venituri din salarii..., o
  reprezinta castigul brut REALIZAT din salarii..." -> "realizat" = efectiv castigat; in luna cu CM salariul realizat
  = doar zilele LUCRATE (zilele de CM = indemnizatie, item separat art.139(1) lit.(o), cu baza proprie).
  Structura oficiala D112 (anaf_surse/d112_struct_anaf.txt, DUK-enforced):
    l.4519: B4_7 (Baza CAS) = B2_5 + B2_6 + B2_7 + B3_7   [baza SALARIALA + baza indemnizatiei CM, ADITIVE, SEPARATE]
    l.4486: B4_5 (Baza CASS) = (B2_5+B2_6+B2_7) + (B3_7 - CMscutit), CMscutit=Sum(D_20+D_21) pt cod NOT in (01,07,10)
    l.4534: B4_8 (CAS) = ROUND (B4_7 * 25%)   ;   l.4507: B4_6 (CASS) = ROUND (B4_5 * Cisan%=10%)
    l.120/124: cadrul e pe ZILE ("baza de calcul CAS ... pt zile lucrate + zile CM"; B2_5P=((sm-fac)/NZL*(zile
      lucrate+zile CM))) - confirma proratarea pe zile, nu brut contractual.
  Coroborare interna: lantul FLUTURAS al generatorului deja prorateaza (calcul_salariu(brut_lucrat), d112.py:482,498)
  -> fluturasul e legal corect; DOAR emisia D112 e gresita. Daca B2_5 ar fi brut intreg iar B3_7 baza CM, s-ar
  declara CAS pe (salariu integral + indemnizatie) = mai mult decat s-a realizat -> contrazice "realizat" + dubla baza.

FINDING 2 (baza) - CONFIRMAT, neconformitate fiscala ACTIVA (nu observatie):
  emisia D112 pune baza salariala CAS/CASS/CAM pe brut INTREG (bazac=_d112int(s["brut"])-facil, d112.py:146-148,199-200,
  si B2_5/B4_7/B4_14 din emit l.279-280), desi legea cere REALIZAT (proratat pe zile lucrate). Masurat: 8000 vs 4190.48.
  Efect: SUPRA-declarare CAS ~952 lei/angajat-luna + CASS + CAM, pe TOTI angajatii cu CM peste minim; divergenta
  fluturas(1047.62)/declaratie(2000). Bani declarati in plus la ANAF.

FINDING 2b (rotunjire) - a doua neconformitate pe acelasi rand, descoperita la verificare:
  structura cere B4_8=ROUND(B4_7*25%) / B4_6=ROUND(B4_5*10%) = O SINGURA rotunjire pe baza TOTALA. Generatorul face
  cas=_d112int(bazac*cota) + Sum_cert _d112int(taxe_cm) = Sigma(round) pe componente. Difera de round(Sigma) cu ±1-2
  lei pe cazuri de granita -> B4_8 emis poate diferi de ROUND(B4_7*25%) -> DUK "B4_8 difera de suma calculata".
  Masurat pe fixtura brut intreg: emis B4_8=4323 vs ROUND(17295*25%)=4324 (DUK-invalid pe acest caz).

DOMENIUL FIX-ULUI (crescut peste intrebarea initiala; scop cerut Costin inainte de mutatie, iesire ANAF):
  - MINIM (Decizia 1 pur): in ramura CM, bazac = _d112int(s["brut_lucrat"]) - facil (proratat). Atinge B2_5, B4_7,
    B4_8, B4_14(CAM), CAM total -> CAS+CASS+CAM se corecteaza coerent. NU rezolva 2b (ramane Sigma(round)).
  - COMPLET (conform structurii oficiale + DUK): rescrie contributiile CM la formula oficiala - B4_7=baza_realizata+
    cm_base; B4_8=_d112int(B4_7*cota_cas); B4_5=baza_realizata+(cm_base-cm_scutit); B4_6=_d112int(B4_5*cota_cass).
    Rezolva 2 SI 2b. ~15 linii in ramura CM (d112.py:186-201). Schimba iesirea ANAF pe CAS/CASS pt toti CM.
  Ambele cer proba RED (mutatie) + golden pe cifre din formula oficiala + suita + verificator + (ideal) DUK.

DECIZIE CERUTA Costin (peste Decizia 1 deja transata): scop fix = MINIM (doar baza, 2b ramane datorie separata) sau
COMPLET (baza+rotunjire, conform DUK)? Pana la raspuns NU se muta emisia (iesire ANAF). Decizia 2 (re-arhitectura
poarta pe valori emise) ramane dupa fix, ca gard independent care confirma noua formula.


## 05.08.2026 (tura 5) - REPARAT Finding 2 (baza salariala CM pe brut intreg): proratare pe zile lucrate

Decizia 1 INCHISA (Costin). Sursa CLARA, nicio regula speciala pentru luna cu CM:
  - CF art.139(1): "castigul brut REALIZAT din salarii".
  - structura D112: B4_7=B2_5+B3_7 (baza salariala + baza indemnizatiei, aditive); B1_sal1="Salariul de baza lunar
    brut" = camp SEPARAT informativ (nu baza contributiei); B2_5 e componenta de "venit realizat" (C1_11).
  - OUG 158/2005: doar baza indemnizatiei (media 6 luni); nimic pe baza salariala; "zile lucrate"/"contributii" absente.

FIX (d112.py ramura CM ~l.171, [d112_cm_baza_realizata_v1]): bazac = _d112int(brut_lucrat)+exces-facil (baza REALIZATA
pe zile lucrate), nu brutul contractual. Corecteaza coerent B2_5/B4_7/B4_8/B4_5/B4_6/B4_14 + CAM. brut (contractual)
ramane in B1_sal1/B4_3.

PROBA: RED pe cod vechi (B2_5=8400 -> test pica); GREEN dupa fix (29 teste d112 + arbori_paraleli); DUK VALID pe
fixtura CM completa (B4_7=10400 B4_8=2600 vs vechi 12400/3100); smoke DUK + exces_vacanta + avantaje + salarizare_cm
verzi (23). Gard anti-regresie: test_pull_declaratii.test_d112_cm_baza_salariala_realizata_nu_brut_intreg.

EFECT PE PRODUS (ce se schimba la contabil): pentru orice angajat cu concediu medical, CAS/CASS/CAM declarate la ANAF
in D112 SCAD - baza salariala = salariul pe zilele LUCRATE, nu contractual (~952 lei CAS mai putin/angajat-luna in
fixtura 8400 @ 5 zile CM). Fluturasul si D112 acum COINCID pe baza salariala. Salariul contractual ramane in B1_sal1.
D112 REGENERATE pentru luni cu CM vor da valori mai mici (corecte); depunerile anterioare pe brut intreg erau
supra-declarate (potential de corectat retroactiv - decizie contabila per firma).

RAMANE DESCHIS: (a) Finding 2b - rotunjire Sigma(round) vs round(total) [B4_8=ROUND(B4_7*25%)], datorie separata,
neatinsa aici (pe fixturi non-granita coincid). (b) Poarta cale2 pe valori EMISE = Decizia 2 (punctul B), urmeaza.


## 05.08.2026 (tura 6) - B: poarta cale2 D112 re-arhitectata pe valorile EMISE (post-generare XML), nu pre-emisie

Decizia 2 (Costin). Gardurile de continut promiteau "un total gresit nu ajunge la ANAF" dar verificau ce INTRA in
generator (pull), nu ce PLEACA (XML emis). Descoperit pe CM (emisia recalcula, poarta vedea salariul-only pre-emisie).

SCOP (verificat in cod - AFECTEAZA DOAR D112, nu toate 6): d100/d101/d205/d300/d394/d406 folosesc tiparul "sursa
unica" - poarta primeste `res` (obiectul rezultat), iar build_xml(res) emite `res` VERBATIM (res==emis, ex. comentariile
"res.total_plata_a == totalPlata_A emis"). Deci poarta lor vede deja valori echivalente cu emisia. D112 e OUTLIER: nu
are `res`; verifica_reconciliere primea `salariati` din pull, iar _d112_genereaza RECALCULA (ramura CM) -> blind-spot
real doar la D112.

FIX (d112.py): (1) _d112_genereaza scrie contributiile EMISE (B4_8=cas / B4_6=cass, dupa tichete) inapoi in fiecare
salariat; (2) genereaza cheama _d112_genereaza INTAI, apoi verifica_reconciliere -> poarta reconciliaza ce PLEACA la
ANAF. Cazul simplu: emis==_d112int(pull) -> comportament identic, mutatiile existente pica la fel. CM: valoarea emisa
reala devine vizibila portii (deblocheaza reconcilierea CM = 1c-CM, ramas de implementat separat).

PROBA: mutatiile existente re-rulate = pica la fel (32 teste reconciliere+pull); smoke DUK d112 verde; gard NOU
test_pull_declaratii.test_d112_poarta_reconciliaza_valorile_emise_nu_pre_emisia: (a) dupa emisie salariatul poarta
valorile EMISE (== B4_8/B4_6 din XML, 1500/600); (b) un emis GRESIT (mutatie pe valoarea EMISA, nu pe pull) e prins de
poarta - dovada ca poarta acopera acum layerul de emisie (inainte era oarba la el).

LIMITA: poarta reconciliaza inca DOAR cazurile deja acoperite (simplu/facilitate/part-time/tichete); CM ramane SARIT
(cm_ids) pana la implementarea reconcilierii CM (1c-CM, acum deblocata de aceasta re-arhitectura). Celelalte 5
declaratii NU au fost modificate (res==emis deja); daca vreuna capata in viitor un layer de emisie care recalculeaza,
tiparul e acelasi (poarta pe emis).


## 05.08.2026 (tura 6b) - CORECTIE analiza C2 + COROBORARE A prin control_incrucisat.py (gasit la sweep Costin)

Sweep-ul de verificare (Costin) a scos `core/control_incrucisat.py` (F162) - un mecanism C2 pe care analiza mea de
metode il RATASE. Compara declaratia vs EVIDENTA CONTABILA citind totalurile din XML-ul EMIS (nu reagregare):
D112 (compara_d112): CAS 412+458 vs 4315, CASS 432+459 vs 4316, CAM 480 vs 436, impozit 602 vs 444 (limita: brut 421
NEVERIFICAT pe CM). D300 (compara_tva): R17_2 vs 4427, R27_2 vs 4426. Deci perechile D112<->contabilitate si
D300<->contabilitate SUNT partial controlate (semafor runtime, nu test blocant; test_control_incrucisat NU exercita CM).

COROBORARE A (independenta de citirea legii): salarii_contare.py bookeaza contributiile pe brut_lucrat PRORATAT (l.56)
+ recalcul CM. Inainte de fix, D112 pe brut intreg diverga de 4315/4316/436 -> compara_d112 ar fi dat ROSU pe lunile cu
CM (semnal existent, neexercitat). Dupa fix, D112 se aliniaza cu evidenta contabila. Fix-ul A confirmat de sursa
independenta. TESTE.md capitol metode corectat (sectiune CORECTIE 05.08 tura 6). Datorie descoperita: test_control_
incrucisat sa exercite o luna cu CM (ar fi prins A) - candidat gard C2, deblocat.


## 05.08.2026 (tura 7) - CORECTIE B (proba mecanica Costin) + Task 1 impozit CM (tinut) + Task 2 citare CAM 220^5

PROBA MECANICA (Task 3, nu citire de cod): mutatie pe totalPlata_A in artefactul XML DUPA build_xml, pt toate 6.
REZULTAT: d100/d101/d205/d300/d394 totalPlata_A dublat in artefact -> genereaza TRECE (poarta NU blocheaza); d406 la fel.
TOATE 6 = PRE-EMISIE.

CORECTIE la afirmatia mea din tura 6 (B): am scris "DOAR D112 afectat, restul res==emis deci poarta vede emisul".
MECANIC FALS. Toate 6 porti reconciliaza `res` INAINTE de build_xml si NU re-valideaza artefactul emis. Promisiunea
"un total gresit nu ajunge la ANAF" NU e enforced mecanic pt niciuna impotriva unui bug de LAYER EMISIE. Nuanta reala:
poarta asigura ca res e corect (recalcul independent); daca build_xml serializeaza FIDEL (res==emis), totalul e corect
- dar poarta NU verifica fidelitatea lui build_xml. 2b (rotunjire in emisie) = res != emis prin constructie -> oarba.
Ce a facut B REAL: a mutat poarta d112 DUPA calculul de emisie (prinde bug-uri de calcul-emisie, ex. divergenta CM);
celelalte 5 stau INAINTE de build_xml. D112 era cel mai GRAV (emisia recalcula cu alta logica), nu "singurul afectat".

FIX COMPLET (deschis, nu facut): fiecare poarta sa reconcilieze valoarea PARSATA DIN XML (assert res == parse(emis)
dupa build_xml), sau sa ruleze pe artefact. Program mai mare - clasa C2 propriu-zisa. Numit, neinceput.

TASK 1 (IMPOZIT CM) - REPARAT 05.08 tura 8 (set neimpozabil {08,09,15,17,91,92}, simetric, fluturas+d112, gard mixt, DUK valid; vezi GARZI tura 8). [ISTORIC constatare:] baza impozitului (bimp =
total_base - cas - cass - ded, total_base=bazac+cm_base) include indemnizatia CM INTEGRAL, pt TOATE codurile, FARA
discriminare. Codurile 08 maternitate / 09 ingrijire copil / 15 risc maternal / oncologice sunt NEIMPOZABILE (CF
art.62 lit.c, verificat verbatim la sursa). Caz numeric (cod 08, brut 6000, indemnizatie 5000, luna intreaga): impozit
EMIS = 294 lei pe o indemnizatie neimpozabila (corect 0). Fix propus (asteapta OK Costin): exclude cm_base al codurilor
neimpozabile din bimp, ca la CASS. CASS deja discrimineaza (01/07/10); impozitul NU.

TASK 2 (CITARE CAM) - corectat in d112.py: exclusia indemnizatiei CM din baza CAM (sum_bazac fara cm_base) are temei
CF art.220^5 (Exceptii specifice CAM: nu se datoreaza pe prestatiile suportate din FNUASS), NU art.220^3 (=cota 2.25%).
Valoarea nu se schimba; citare adaugata la cam_total.


## 05.08.2026 (tura 8) - REPARAT Task 1: impozit pe indemnizatia CM neimpozabila (CF art.62 lit.c) - simetric

Neconformitate fiscala activa (over-taxare), reparata cu cele 3 conditii Costin.

COND.1 - MAPARE la sursa (structura D112 C2-rows, ANAF/DUK + CF art.62 lit.c): set NEIMPOZABIL = {08,09,15,17,91,92}.
  08 maternitate (Rd.3 "Sarcina", struct l.1712); 09/91/92 ingrijire copil (Rd.4, l.5452 "D_9=09,91,92");
  17 oncologic (Rd.4.1, l.5464 "D_9=17"); 15 risc maternal (Rd.5, l.5695 "D_9=15,D_23=RM"). Cod 10 (reducere timp
  munca) = FNUASS-integral DAR impozabil (inlocuitor salariu, nu-i in art.62 lit.c) -> EXCLUS. "Cresterea copilului"
  = indemnizatie CIC separata, nu cod CM -> N/A. Constanta salarizare._CM_COD_NEIMPOZABIL.

COND.2 - SIMETRIE scazaminte: baza impozit = salariu realizat + CM IMPOZABILA; se scad DOAR CAS/CASS pe partea
  IMPOZABILA (cm_cas_imp/cm_cass_imp = doar coduri taxabile). Altfel CAS 25%% pe indemnizatia neimpozabila ar cobori
  bimp cu 25%%*cm_base = SUB-declarare. cas/cass EMISE (B4_8/B4_6) raman pe TOATE codurile (CAS art.139(1)(o) uniform);
  DOAR baza impozit exclude.

COND.3 - proba pe LUNA MIXTA (nu luna intreaga de CM, care se clampeaza la 0 si ascunde bug-ul de simetrie): brut
  12600, 6 zile cod 08 -> brut_lucrat 9000 (ded=0, brut>plafon). RED cod vechi: impozit emis 885 (impoziteaza
  maternitatea). GREEN: 585 (= _d112int((9000-2250-900)*10%%)). DISTINCT de naiv 485 (care ar lasa CAS pe maternitate).
  DUK VALID. Gard: test_pull_declaratii.test_d112_impozit_exclude_indemnizatia_cm_neimpozabila_luna_mixta.
  DEDUCERE (verificat, neschimbat): calcul_salariu o calculeaza pe brut_lucrat (salariul REALIZAT, b_imp), NU pe CM
  si NU pe contractual - consistent cu baza impozit (CF art.77 alin.4 = venit brut realizat). Fara ambiguitate.

FIX IN DOUA LOCURI (consistenta arbori paraleli): taxe_cm (salarizare.py:576) impozit=0 pe coduri neimpozabile ->
lantul FLUTURAS + concedii_medicale.impozit salvat (salariati_api:369); d112.bimp (declaratie). Ambele = acelasi set.

EFECT PE PRODUS: pentru angajatii cu concediu de maternitate/ingrijire copil/risc maternal/oncologic, impozitul
retinut SCADE (indemnizatia nu se mai impoziteaza) - atat pe fluturas cat si in D112. CAS/CASS raman neschimbate.
Depunerile/statele anterioare care impozitau aceste indemnizatii erau gresite (retineau impozit in plus de la salariat).


## 05.08.2026 (tura 9) - agregare multi-cert (per-cert) + coduri 14/18 impozabile (decizie) + gap D_8 cod 09/91

TASK 1 (simetrie multi-cert): scazamintele impozitului (cm_cas_imp/cm_cass_imp) se acumuleaza PER-CERTIFICAT in bucla
(d112.py:212), NU pe total -> partitia impozabil/neimpozabil supravietuieste insumarii. Probat: luna cu cod 01
(impozabil) + cod 09 (neimpozabil) -> impozit 676; mutatie (golirea setului) -> 789 (dif 113 = partea cod 09). DUK-proba
pe cod 01+08 (identic 676, valid). Gard: test_d112_impozit_multi_certificat_partitie_per_cert (mutatie built-in).

TASK 2 (coduri 14/18): IMPOZABILE, consemnat DECIZII.md 05.08. 14 = neoplazii/SIDA proprii (OUG 158 art.9), NU
ingrijitorul oncologic (cod 17); 18 = carantina/izolare copil, NU copil bolnav (cod 09). Gard pin:
test_cm_coduri_14_18_raman_impozabile_decizie_05_08 (muta 14/18 sau schimba setul -> pica).

TASK 3 (sursa unica): _CM_COD_NEIMPOZABIL definit O SINGURA data (salarizare.py:566); citit de taxe_cm (l.585, acelasi
modul) SI de d112.bimp (l.212 via _sz._CM_COD_NEIMPOZABIL). Fara constanta duplicata. Verificat.

GAP NOU (datorie, separat de impozit): cod 09/91 (ingrijire copil) = DUK-INVALID - regula DUK S97 cere D_8 (CNP copilul
pt care s-a eliberat certificatul), dar emisia NU emite D_8 si concedii_medicale n-are coloana CNP copil. Efect: o
declaratie D112 cu concediu de ingrijire copil (09/91) e respinsa de DUK. Declansator: adaugare coloana cnp_copil +
emisie D_8. NEatins acum (in afara scopului impozit). [Nu confunda cu 09 in setul neimpozabil - aia e corecta.]


## 05.08.2026 (tura 10) - POARTA PE ARTEFACT (res == parse(emis)) pe 6/7 declaratii - SUPERSEDEAZA formularea din tura 6/7

Livrat: core/reconciliere_emis.py - fiecare generator, DUPA build_xml, reconciliaza valoarea PARSATA din XML-ul livrat
cu res. HARD-BLOCK (ReconciliereEmis) pe divergenta, ca gardurile de continut. Inchide blind-spot-ul "pre-emisie"
dovedit mecanic la tura 7 (mutatia pe totalPlata_A din artefact trecea).

CABLATE (6): d100/d101/d205/d300/d394 -> totalPlata_A parsat == res.total_plata_a (int, lossless). d112 (fara res)
-> totalPlata_A == SUMA A_datorat parsata din <angajatorA> (self-consistency lossless: totalul == suma obligatiilor).
PROBA MECANICA (aceeasi mutatie ca sweep-ul, dupa build_xml): d100/d101/d205/d300/d394/d112 = BLOCAT (toate 6 pica
acum). Gard permanent: test_smoke_duk.test_poarta_artefact_blocheaza_total_corupt.

D406 = EXCEPTIA (necablat, motivat, nu improvizat): SAF-T n-are total canonic pe res, iar sumele-s text 2-zec rotunjit
HALF_UP (_dec) -> assert strict res==parse pe valoarea bruta PIERDE informatie (lossy). Invariantul lossless disponibil
(verifica_d406: partida dubla TotalDebit==TotalCredit) EXISTA si prinde imbalanta (probat), dar NU e cablat: fixturile
de test au GL neechilibrat pe luna selectata (date artificiale - ex. smoke: TotalDebit 0.00 vs TotalCredit 15000) ->
cablarea le-ar rupe. Emisia d406 pe input ECHILIBRAT e corecta (probat 15000==15000). CONSTATARE conexa: DUK accepta
GL neechilibrat (nu verifica Sigma debit=Sigma credit) - datorie separata (cablare d406 dupa curatare fixturi).

2b (rotunjire Sigma(round) vs ROUND) - RASPUNS ONEST: poarta pe artefact NU pica pe rotunjire la nivel de TOTAL pentru
niciuna. Motiv: totalul e intern-consistent (res.total_plata_a e STOCAT ca valoarea emisa / totalPlata_A == suma
randurilor emise) -> nu exista divergenta res-vs-emis la total. 2b e o divergenta PER-RAND intre formula generatorului
(Sigma round) si formula OFICIALA (ROUND(baza x cota)) - o prinde DUK (formula ANAF) / cale2 (recalcul independent),
NU res==parse(emis) (unde res SI emis folosesc aceeasi formula a generatorului). Poarta pe artefact acopera o CLASA
DIFERITA (fidelitatea build_xml + tampering), nu formula. 0 declaratii pica pe rotunjire - corect, nu prin toleranta.

REFORMULAREA PROMISIUNII (cat.4 "Iesire catre autoritati"): "un total gresit nu ajunge la ANAF" e ACUM ADEVARATA
pentru TOTALUL DE PLATA al celor 6 declaratii cablate - verificat contra artefactului livrat, hard-block pe divergenta.
LIMITA REALA scrisa: (a) d406 - totalul de plata SAF-T nu are forma canonica lossless -> se verifica partida dubla, dar
necablat pana la curatarea fixturilor; (b) la nivel de RAND, o valoare gresita din formula (2b) e prinsa de DUK/cale2,
nu de aceasta poarta; (c) poarta verifica TOTALUL + (d112) coerenta lui cu obligatiile, nu fiecare camp emis in parte.


## 05.08.2026 (tura 11) - LIVRAT: CNP persoana ingrijita (D_8/D_8a) pt ingrijire copil (09/91/92) + pacient oncologic (17)

Inchide gap-ul din tura 9 (cod 09/91/92 DUK-invalid, lipsea D_8 - la probe se folosea cod 08 ca inlocuitor).
Regula DUK S97 CITITA la sursa (struct D112 l.5446-5464): D_8 = CNP/CIS copil N(13), obligatoriu pt D_9 in (09,91,92);
D_8a = CNP/CIS pacient oncologic N(13), obligatoriu pt D_9=17 (camp SEPARAT, nu D_8 - verificat, nu presupus).

1. SCHEMA: coloana cnp_ingrijit text in concedii_medicale. tenant_template.sql (tenanti noi) + core/migrare_cnp_ingrijit.py
   (idempotent ADD COLUMN IF NOT EXISTS, iterat pe information_schema WHERE schema_name ~ tenant_[0-9]+). RULAT: 1/1 scheme OK.
2. VALIDARE: valideaza_cnp (salariati_import_api - format+data+judet+cifra control 279146358279) la salvare
   (salariati_api.salveaza_concediu) SI la emisie -> un CNP invalid NU intra.
3. EMISIE: d112 emite D_8="<cnp>" pt 09/91/92, D_8a pt 17 (bucla _opt).
4. UI: camp conditionat #cm-cnp-ingrijit (flux_concediu.js), afisat pe cod 09/91/92/17 (precedent cod_urgenta pe 06).
   Design System cap.2 (structura camp) + cap.6 (oblig asterisc + camp-ajutor + msg-eroare). INSERT + payload backend.
5. BLOCK (regula bazei nule): certificat cod 09/91/92/17 fara CNP valid -> genereaza ridica ValueError explicit,
   NU emite D112 invalid la ANAF. Certificatele existente fara CNP opresc generarea cu mesaj (completeaza in ecran).
7. PROBA E2E: cod 09 cu CNP valid 5200515400016 -> D_8 emis + DUK VALID (lantul neprobat DUK inainte); fara CNP -> BLOCAT.
   Garduri: test_d112_cod09_fara_cnp_copil_blocheaza_emisia, test_d112_cod09_cu_cnp_copil_emite_d8_si_e_duk_valid.

DATORIE GDPR (part 6 - SEMNALATA, nu improvizata; raportata separat lui Costin): CNP-ul unui MINOR NEANGAJAT (copil)
sau al unui PACIENT tert = prelucrare de date personale ale unui TERT, sensibile (minor). Verificat in cod: F199-F205 =
DREPTURILE persoanei vizate (export/stergere/retentie/alerta cabinet), NU un registru al prelucrarilor (ROPA GDPR art.30
- LIPSESTE cu totul). Nicio baza de prelucrare documentata pentru CNP de tert minor/membru familie (mentiunile de "copil"
sunt fiscale, nu GDPR). GOL DE CONFORMITATE REAL. Feature-ul e livrat (D112 il cere fiscal - altfel cod 09 nedepozabil),
DAR temeiul de prelucrare (art.6/9), informarea persoanei vizate terte (art.14) si ROPA raman de DECIS de Costin - nu
se improvizeaza politica in cod.


## 05.08.2026 (tura 12) - Campania C, clasa C5 (mascarea erorii / zero tacut): gard AST anti-except-masca LIVRAT

C5 din capitolul "Metode de verificare - clasele oarbe" (TESTE.md). Gard: core/test_gard_masca_zero.py - analiza AST
peste modulele de BANI (d100/d101/d112/d205/d300/d301/d390/d394/d406/d710/salarizare/verificatoare/reconciliere_emis +
cele 6 *_reconciliere) interzice un handler de exceptie al carui corp e DOAR `pass` sau `return <zero/gol numeric>`
(0/0.0/""/[]/{}) - tiparul cat.0 (`except: return 0` din _d112int, MASCA SCOASA 27.07). NON-TAUTOLOGIE: proba
STRUCTURALA (AST), nu recalcul. MUTATIE (dovada ca musca): snippet `except: return 0`/`pass`/`return []` = PRINS;
`except` care ridica / returneaza valoare reala / asigneaza = NU prins (fara fals-pozitiv). 0 violari in productie.

SCOPARE (decisa la livrare): `return None` si `return False` EXCLUSE - salarizare._pd (parser de data, None="nu-i
data") si validatorii (bool) sunt legitimi; masca periculoasa e ZERO/GOL numeric tacut (trece checkurile aritmetice),
nu None (ar da TypeError downstream, mai zgomotos). LIMITA: prinde DOAR tiparul sintactic except->pass/return-zero in
modulele listate; o masca prin `x=0` in corp NU e prinsa (alt tipar); un modul de bani nou trebuie adaugat in _MODULE_BANI.

RAMAN din C5: mutant-zero sistematic (fortarea fiecarui generator sa intoarca [] -> suita/verificator rosu) - jumatatea
diagnostica, neinceputa (buget context).


## 05.08.2026 (tura 13) - Restanta migrare cnp_ingrijit + Campania C clasa C2 (fluturas<->D112) LIVRAT

RESTANTA (comanda anterioara, neraportata complet): migrarea cnp_ingrijit pe TOATE schemele. Verificat tiparul REAL:
singurul tenant real e tenant_001 (^tenant_[0-9]+$ match doar el; restul schemelor non-sistem = ztest_* reziduuri de
test, NU tenanti). Migrare idempotenta re-rulata: 1/1 scheme OK, coloana confirmata pe tenant_001. GARD:
core/test_migrare_cnp_ingrijit.py::test_toti_tenantii_au_cnp_ingrijit (pica daca o schema de tenant n-are coloana).

C2 (intre documente) - perechea FLUTURAS <-> D112:
TAUTOLOGIE identificata explicit (cerinta Costin): fluturasul (stat_plata_api:74,166) SI D112 (pull) citesc ACEEASI
functie salarizare.calcul_salariu -> un compare DIRECT fluturas-vs-D112 pe formula NU e proba, e tautologie. A DOUA
CALE REALA = ARTEFACTUL contabil: ce s-a BOOKAT in ledger (rulaje credit 4315/4316/436/444, din inregistrari_linii)
vs ce DECLARA D112 in XML-ul EMIS (angajatorA A_datorat, parse). Cele doua ARTEFACTE pot diverge (bug de orchestrare/
booking/editare manuala) chiar daca upstream impart calcul_salariu - exact bug-ul CM de azi (D112 pe brut intreg 2000
vs ledger pe brut_lucrat 1048).

control_incrucisat.compara_d112 face deja aceasta confruntare (F162) - EXTINS + GARDAT, nu re-inventat. Era NETESTAT
(test_control_incrucisat testa doar compara_tva/D300) -> de-asta divergenta CM n-a fost prinsa de semafor. Garduri noi:
- test_compara_d112_verde_cand_declaratia_coincide_cu_ledgerul;
- test_compara_d112_prinde_divergenta_declaratie_vs_ledger_MUTATIE (D112 CAS 2000 vs ledger 1500 -> ROSU, dif 500);
- test_c2_d112_confrunta_artefacte_nu_recalculeaza_NON_TAUTOLOGIE (AST: compara_d112 + totaluri_d112_din_xml NU apeleaza
  calcul_salariu/taxe_cm/pull -> confruntare de artefacte, nu recalcul; totaluri din regex pe XML-ul emis).

RAMAN (perechile C2, ordinea efect x cost - PREDARE): Sum(D112 lunar impozit)<->D205 (anual/persoana); balanta<->D101
(deja partial via d101_reconciliere din clase 6/7); D100<->D112 = pass-through (tautologie pura, NU merita). Apoi C3
(timp), C1 (intrare), C4 (interpretare). Neincepute - buget context.


## 05.08.2026 (tura 14) - Campania C: C3 (Sigma debit=Sigma credit perioada) livrat + C2-rest (tautologii) + C4 scris

C3 (integritate in TIMP) - felia Sigma debit=Sigma credit: core/echilibru_perioada.py (pur + reader DB). A DOUA CALE
pentru ce DUK NU verifica (DUK accepta GL dezechilibrat - tura 10). echilibru_perioada(linii)=Sigma pe cont_debit ==
Sigma pe cont_credit; orfani(linii,ids)=referinte rupte. Garduri: test_echilibru_perioada.py - verde pe partida dubla,
MUTATIE (linie cu credit lipsa -> dezechilibru prins), orfani, AST non-tautologie (invariant contabil, nu recalcul
generator). LIMITA: nu e snapshot+hash (regenerare-diff declaratie depusa) - felie C3 separata (state_plata snapshot
DECIS in GARZI INVENTAR A); jobul nocturn care ruleaza echilibru_perioada_db per perioada/tenant = wiring ramas.

C2 (intre documente) - perechile ramase, VERDICT ONEST (nu construiesc gard fals - cerinta Costin):
- balanta<->D101: DEJA COMPLET (d101_reconciliere: _baza_contabila_independenta recalculeaza venituri/cheltuieli din
  balanta clase 7/6 INDEPENDENT + test_mutatie_venituri_gresite_pica mutatie-probat + AST non-tautologie). Partea
  computabila gardata; ajustarile fiscale P6-P9 = §8 manual, nereconciliabile. Nimic de extins.
- D100<->D112: PASS-THROUGH pur (calcul_d100(prof,an,luna,obligatii) formateaza obligatii dat, nu importa d112, nu
  recalculeaza). Daca apelantul paseaza totalurile D112 -> D100==D112 prin constructie = TAUTOLOGIE. NU se construieste
  gard (ar fi fals). Sarita, numita.
- Sum(D112 lunar)<->D205: D205 e FORMATTER (calcul_d205(prof,an,beneficiari), beneficiari.imp = INPUT, aceeasi sursa
  salariala ca D112). Tautologic pe VALORI; singura dimensiune independenta = agregarea anuala (Sigma lunar vs anual) -
  ingusta + cere fixtura cross-an (12 luni D112 + D205). NU se construieste gard full (ar fi fals pe valori); daca se
  vrea gardul de AGREGARE (luna scapata/dublata), e felie separata scopata. Numita.

C4 (interpretarea sursei): SCRIS in TESTE.md (capitolul metode, sectiunea 6) - regula de procedura per cluster (a doua
lectura / DUK inainte de √ definitiv pe REDARE/INTERPRETARE), NU executat (cerinta Costin: nu campanie separata).

RAMAN: C1 (invarianti DB intrare: NOT NULL bani + cheie unica + intrare<->document-sursa) - migrare pe coloane
existente = risc pe date NULL curente + touch pe multe tabele; scopat separat, neatins acum (buget). C3 job nocturn +
snapshot+hash. C5 mutant-zero. Predare in PREDARE_LANT.md.


## 05.08.2026 (tura 15) - INCHIDERE Campania C: C5+C2+C3+C4 livrate (cu limite numite); C1 = limita scrisa

Vezi TESTE.md capitolul metode sectiunea 7 (stare finala pe toate 5). Sumar cu cod:
- C5: test_gard_masca_zero.py (AST anti-except) + test_mutant_zero.py (d112/d205). LIVRAT.
- C2: test_control_incrucisat.py (fluturas<->D112 via artefact contabil, mutatie) + balanta<->D101 preexistent.
  D100<->D112 + Sum(D112)<->D205 = TAUTOLOGII numite (nu gard fals).
- C3: amprenta_declaratie.py + test (snapshot+hash regenerare-diff, mutatie editare retroactiva) + echilibru_perioada.
  orfani. CORECTIE onesta: Sigma debit=Sigma credit e TAUTOLOGIC pe schema (inregistrari_linii cont_debit+cont_credit
  NOT NULL -> fiecare linie echilibrata) - functia ramane ca monitor, dar NU poate pica azi = limita.
- C4: test_datorie xfail reactualizat (19 COTE, functii in upgrade) + procedura scrisa (TESTE sectiunea 6).
- C1: LIMITA scrisa (nu gard fals). Goluri reale: facturi fara cheie unica naturala (import dublat posibil); money
  columns DEFAULT 0 nu NOT NULL. Migrarea enforce = riscanta pe date murdare existente -> follow-up dedup/backfill scopat.

## 06.08.2026 — Divergență CUNOSCUTĂ validator-vs-lege: baza minimă part-time (DUK scade facilitatea)

DECIZIE COSTIN (06.08): urmăm LEGEA, nu validatorul DUK. Documentat aici cu temeiul scris.

**Regula de lege (verbatim):** CF (Legea 227/2015) **art.146 alin.(5^6)** [CAS] — „Contribuția de asigurări sociale
datorată ... în baza unui contract individual de muncă cu normă întreagă sau cu timp parțial ... nu poate fi mai mică
decât nivelul contribuției ... calculate prin aplicarea cotei prevăzute la art. 138 lit. a) asupra **salariului de bază
minim brut pe țară în vigoare în luna** pentru care se datorează ..., corespunzător numărului zilelor lucrătoare din lună
în care contractul a fost activ." (modif. 01.01.2025, OUG 156/2024 art.LXIV pct.14). Simetric pentru CASS (art.157).
Facilitatea de 300/200 lei (OUG 156/2024 **art.LXVI alin.(1)**) se acordă DOAR salariaților „încadrați cu **NORMĂ
ÎNTREAGĂ**" → nu diminuează floor-ul part-time.

**Ce face codul (corect pe lege, fix 06.08):** `d112.py prag_pt = sm` și `d112_reconciliere.py prag = sm` — floor part-time
= salariul minim INTEGRAL. Gard `test_d112_part_time_baza_minima_salariul_minim_integral` (B4_5P=4050 iunie, mutație pică).

**Divergența DUK:** DUKIntegrator dă **ATENȚIONARE** (nu eroare) regula SP1B4_1: „B4_5P(4050) diferit de suma calculată
3750" — validatorul **scade facilitatea** (3750 = 4050−300) din floor-ul part-time, contrar art.146(5^6). Atenționarea
NU blochează depunerea (ANAF acceptă declarația). NU aliniem codul la validator (ar sub-declara CAS/CASS part-time,
contra legii). Ca la D101-scadență (validator DUK invers față de CF art.42): codul urmează legea; divergența e cunoscută
și scrisă. Declanșator de reevaluare: DUK actualizează SP1B4_1 la art.146(5^6), SAU ANAF confirmă interpretarea sm−fac
(caz în care ar deveni decizie de produs deschisă).


## 06.08.2026 — C-4 Tranșa 2 Cluster 1 (seed firme + coerență): LIMITE DECLARATE
Seed date_test/seed/transa2_coerenta_tva.py a materializat firmele + T-1…T-7. NEACOPERIT încă (nu erori,
reziduu de tranșă — se ridică în clusterele următoare ale tranșei 2/3):
- **Documente per-firmă TVA încă neseed-uite:** achiziția IC a lui P1/N1 de la furnizor UE extern (D390/D301);
  operațiunile pe marjă S1 (art.311)/S2 (art.312); rândurile d301_operatiuni pt N1 (D301 NU citește facturi,
  citește tabelul d301_operatiuni — vezi harta model date). Doar backbone-ul de coerență R3 e seed-uit acum.
- **T-5 (S3→P1) = exceptia numită „achiziție de la agricultor forfetar":** stocată ca factură primită la P1 cu
  tva=2000 (forfait 8%), cota_linie=0, tert_platitor_tva=False. D394 orfan (S3 neplătitor nu depune) — se tratează
  ca atare, NU se forțează coerență A↔B pe latura S3.
- **T-6 (P2→S1) taxare inversă:** stocată cu taxare_inversa=True, categorie_331='constructii', tva=0 pe factură;
  S1 autolichidează la generare (de verificat că D300 S1 produce rândul de taxare inversă — cluster următor).
- **Salariile firmelor simple (M1/M2/P1/P2/S1/S2/NR1/T1/T2)** NU sunt seed-uite (tranșa 2 = TVA; D112 simplu =
  tranșa 1 declarată dar neseed-uită pt aceste firme). Fără salariați → D112 gol pt ele acum.
- **Pragul TVA 395k (L3) neenforced** (deja în GARZI secțiunea D): statutul platitor_tva fixat manual în seed.


## 06.08.2026 — C-4 Tranșa 2 Cluster 2: BUG CONFIRMAT — perioada fiscală TVA trimestrială neimplementată (D300/D394)
DATORIE (impact fiscal, iese la ANAF). Plătitorii de TVA cu perioadă TRIMESTRIALĂ (M2/P2 din set; CF art.322)
primesc D300/D394 DUK-VALIDE dar FISCAL GREȘITE:
- **d394.tip_d394(luna) returnează hardcodat "L"** (core/d394.py:307), ignoră tip_decont. Docstring-ul recunoaște:
  „T/S/A rămân de completat când există vector fiscal". Vectorul (firma_profil.tip_decont) EXISTĂ acum (setat de seed)
  → D394 M2/P2 emite tip_D394="L" în loc de "T". Etichetă de perioadă greșită pe o declarație altfel DUK-validă.
- **Fereastra de date = O SINGURĂ LUNĂ și pentru trimestriali:** d300.pull/d394.pull folosesc perioada.interval() cu
  `luna` → [luna, luna+1). PROBĂ DECISIVĂ: P2 (trim) are T-2 în APRILIE (net 80000 / TVA 16800). D300 P2 generat cum
  face app-ul (luna=6 = sfârșit Q2, SINGURA permisă de d300.valideaza:365 pt T) → DUK=VALID dar R22_1=R22_2=0:
  OMITE COMPLET aprilie. (luna=4 vede T-2 corect: R22_1=80000/R22_2=16800, dar d300.valideaza o RESPINGE — „tip_decont=T
  cere luna∈{2,3,5,6,8,9,11,12}" — + DUK erori.) interval() SUPORTĂ deja trim: Perioada(trim=2)→[apr,iul); doar
  caller-ul pasează luna, nu trim.
- **declaratii_api.py:78-81** rutează d300/d394/d390 ca „lunar" MEREU (harta PERIOADE nu are cale trimestrială pt ele;
  doar d100/d710 sunt trimestriale acolo).
IMPACT REAL: orice contribuabil trimestrial (nu doar setul de test) depune deconturi TVA care sub-raportează 2 din 3
luni ale trimestrului → declarație eronată la ANAF, dar care trece DUK (fals-verde). TEMEI: CF art.322 (perioada
fiscală = trimestrul calendaristic pt CA an ant. < 100.000 EUR fără achiziții IC; un singur decont per perioadă,
acoperă toate lunile perioadei); OPANAF D394 (aceeași frecvență ca decontul).
NEREPARAT în această tură — buget de context + decizie de design pe forma API-ului de perioadă (vezi DECIZII 06.08 +
TESTE fir C-4 tranșa 2, pașii de fix). Firmele LUNARE (P1) NU sunt afectate: D300/D394 P1 toate DUK-valide, coerență
corectă pe lunile 2-6 (verificat această tură).


## 06.08.2026 — REZOLVAT: perioada fiscală TVA trimestrială D300/D394 (datoria de mai sus, aceeași zi)
Datoria „perioada TVA trimestrială neimplementată" REPARATĂ (optiunea B, DECIZII 06.08). common.perioada_tva_tip
(citește vectorul fiscal firma_profil.tip_decont; EROARE la lipsă, fără default tacit 'L') + common.fereastra_tva
(decuplează eticheta luna 3/6/9/12 de fereastra de date = trimestrul). Aplicat în d300.pull, d394.pull + serii_emise,
d394.tip_d394(prof), și în GĂRZILE „a doua cale" d300_reconciliere/d394_reconciliere (aliniate la aceeași fereastră).
Vânătoare de clasă: D390 rămâne LUNAR (vector_fiscal_api:13, lege recap IC) — neatins; D100/D710 deja trim — neatins.
PROBĂ: P2 Q2 (luna=6) include acum T-2 din aprilie (R22_1=80000/R22_2=16800, era 0), DUK-valid; tip_D394='T'; P1 lunar
10/10 DUK-valid (fără regresie). GARD: core/test_d300_d394_trimestrial.py + mutație probată (T→lună = testul picat).
LIMITĂ RĂMASĂ (nu din acest fix): T-6 taxare inversă art.331 — D394 cere secțiunea op11/codPR; categorie_331='constructii'
nu mapează la un codPR valid → P2 Q3 D394 + S1 iulie D394 = DUK erori (R233.5). Item separat „T-6 taxare inversă".


## 06.08.2026 — T-6 taxare inversă: categorie corectată + BUG NOU (D300 furnizor pierde livrarea)
Seed T-6 corectat: categorie_331 'constructii' → 'cladiri_terenuri' (art.331 lit.g, livrare clădire/teren între
plătitori = taxare inversă VALIDĂ; construcții-LUCRĂRI nu mai e taxare inversă, abrogat). Efect: D394 P2 Q3 + S1 iulie
acum DUK-VALIDE (op11/codPR 27 construit; R233.5 rezolvat). D300 CUMPĂRĂTOR (S1) corect: autolichidare R27(colectat)=8400
+ R22(deductibil)=8400, net zero.
**DATORIE NOUĂ (impact fiscal): D300 al FURNIZORULUI pierde livrarea cu taxare inversă.** P2 Q3 D300 = COMPLET GOL
(0 rânduri), deși livrarea de 40000 art.331 lit.g ar trebui raportată în R13 („Livrări de bunuri/servicii pentru care
se aplică taxarea inversă"). DUK-valid (fals-verde, ca bug-ul trimestrial). Cauză probabilă: d300.pull NU selectează
f.taxare_inversa (SELECT-ul are doar directie/total/tva/linii) → calcul_d300 nu poate ruta livrarea emisă cu taxare
inversă (cota 0) în R13; latura cumpărător merge prin altă cale (cota bunului pe primită). TEMEI: OPANAF struct D300
R13 (art.331). NEREPARAT — item separat „D300 furnizor taxare inversă". Firmele fără taxare inversă emisă neafectate.


## 06.08.2026 — REZOLVAT: D300 furnizor taxare inversă (datoria de mai sus, aceeași zi)
Datoria „D300 furnizor pierde livrarea cu taxare inversă" REPARATĂ (decizie Costin: auto furnizor rd.13 / manual
beneficiar — DECIZII 06.08). Vânătoare de clasă: reparate d300.pull (+taxare_inversa) + calcul_d300 (rutare rd.13) +
d300_reconciliere (aliniere); confirmat corecte d394 (tip V/C), d406 (citește ti), d394_reconciliere; d390 (IC) N/A;
jurnal_api nu produce rând de declarație. PROBĂ: P2 Q3 D300 R13_1=40000 (era gol), R13_2=0 (fără TVA), DUK-valid; S1
beneficiar nu se mai auto-deduce (R22=0), cu manual rd.12+rd.27 DUK-valid; anti-dublare ridică EROARE; P1 fără regresie.
GARD: 4 teste (3 unitare + 1 integrare DUK) + mutație probată; testele manuale rd.12 neatinse.
LIMITĂ: firmele cu tva_la_incasare — livrarea cu taxare inversă a FURNIZORULUI nu ajunge în rd.13 (calea _pull_incasare
exclude taxare_inversa, art.282(6)); edge rar (reverse-charge + TVA la încasare), declarat. P2/S1 nu sunt tva_la_incasare.


## 06.08.2026 (tura 2) — C-4 Tranșa 2: GOL DE ACOPERIRE — regimurile pe marjă nu ajung în D300 (decizie Costin: NU se integrează acum)
Decizie Costin (06.08 tura 2): regimurile pe marjă **NU se integrează în D300 în această campanie** — cer model
nou de date = decizie de produs, în afara scopului campaniei de testare. Consemnat aici ca gol de acoperire declarat:
- **art.311 (turism)** `core/tva_marja_turism.py` și **art.312 (second-hand/artă/colecție)** `core/tva_marja.py`
  există ca motoare PURE, verificate + gardate golden (clustere închise 03.08), DAR sunt **STANDALONE**: nu-s
  importate în `core/d300.py`. Singurii apelanți = endpoint-uri `main.py` (`/vanzare-marja` :6345, turism :6382,
  aur :6440, agricultori :6479/:6511) care postează ciorne în `inregistrari` (4111/707/4427).
- **Consecință fiscală:** o firmă pe marjă (S1 art.311 / S2 art.312 din set) ar depune azi un D300 **fără
  operațiunile ei principale** — decontul auto se alimentează din `facturi` pe cotă, iar marja nu are nici tabel
  de persistență, nici flag pe `facturi` → nu ajunge niciodată în D300. Nu e alarmă falsă (nu se raportează greșit),
  e **lipsă tăcută** a bazei pe marjă din decont.
- **Ce ar cere integrarea (decizie produs, NU acum):** model nou — flag/tabel pentru operațiunea pe marjă +
  rutare în `calcul_d300` la rândurile de marjă (baza = marja, nu prețul integral) + reconciliere cale-2.
- **Scop:** S1/S2 **RĂMÂN în set** pentru restul obligațiilor lor (D112, D100, D394, D406, D101, D205, bilanț).
  Doar latura „D300 pe marjă" e scoasă din C-4 și marcată decizie de produs.


## 06.08.2026 (tura 2) — C-4 Tranșa 2: GOL CONSOLIDAT — praguri fiscale declarate manual, neverificate de aplicație
Consolidare (decizie Costin 06.08 tura 2): pragurile de mai jos NU sunt enforce-uite în aplicație — statutul care
ar rezulta din ele (regim fiscal, perioadă TVA, calitate de plătitor, obligație de depunere) se fixează **MANUAL**
în seed/profil. Prin urmare cazurile „prag−1 / prag+1" ale acestor praguri sunt **C-5 (date de test), NU C-4
(comportament cod)** — nu există gard fiscal de exercitat. Aceeași familie cu pragul TVA 395k semnalat deja
(GARZI 06.08 secțiunea C-4 Cluster 1). Lista completă a golului (un singur gol declarat):

| Cod | Prag | Temei | Ce ar comuta | Stare |
|---|---|---|---|---|
| **L1** | 100.000 EUR CA (micro→profit) | CF art.47(1)(c)/52; OUG 8/2026 (era 250k în 2025) | `regim_fiscal` micro↔profit | neenforced — fixat manual în `firma_profil.regim_fiscal` |
| **L2** | 100.000 EUR CA an ant. (lunar↔trimestrial) | CF art.322 | `tip_decont` L↔T | neenforced — fixat manual în `firma_profil.tip_decont` |
| **L3** | 395.000 lei (scutire mică întreprindere) | CF art.310(1); OG 22/2025 | `platitor_tva` da↔nu | neenforced — fixat manual în `firma_profil.platitor_tva` |
| **L10** | 10.000 EUR (achiziții IC — decont special) | CF art.317 | obligația de depunere D301 | neenforced — `d301.py` citește orice rând din `d301_operatiuni`, fără gardă de prag |

**Consecință:** aplicația nu detectează depășirea/subdepășirea acestor praguri; contabilul setează statutul.
Un caz prag±1 testat pe aceste praguri verifică *configurarea seed-ului*, nu codul → aparține C-5.
**Excepție care RĂMÂNE în C-4: L4** (plafon TVA la încasare, 4.5M lei ian–feb → 5M de la 01.03.2026, CF art.282(3)/
OUG 8/2026) — ACESTA **e enforced period-aware** (`common.py:393`, `COTE["plafon_tva_incasare"]`) și **deja testat**
(dispatcher exigibilitate `d300.py:138`); cazurile lui prag±1 sunt legitime C-4.
**Decizie deschisă (produs):** dacă vreun prag din L1/L2/L3/L10 trebuie enforce-uit în aplicație (derivare automată
a statutului din CA/volume) = campanie separată, greenlight Costin.


## 06.08.2026 (tura 3) — C-4 Tranșa 3 (anuale + tranziția de an): FIX D101 + goluri declarate + verificări
Tranșa 3 (ultima din C-4). Metodă: divergență = bug până la proba contrarie → temei la sursă → gard + mutație.

**REPARAT (bug reachable) — D101 `ca_an_precedent_eur` crăpa generarea (gate IMCA art.18^1):**
`declaratii_api._d101` injectează `ca_an_precedent_eur` în `manual`, dar `d101.genereaza` scotea doar
cota/d_grup/cod_obligatie → cheia ajungea în `intrari` și `calcul_d101` o respingea ca „intrare necunoscută" →
ORICE apel D101 prin API cu CA an precedent = `ValueError`. Fix: `genereaza` scoate cheia și porează
eligibilitatea IMCA la sursă (sub 50 mil euro → nu se aplică, cazul comun; peste prag fără P47 → eroare clară,
nu crash criptic / nici omitere tacită). Gard `test_d101_imca_ca_precedent.py` (RED + API-path + DUK + mutație).

**GOL DECLARAT (decizie de produs) — perioada fiscală parțială / regim dual pe an (T1, T2):**
NU există suport de motor. Probă la sursă: `common.py:46` (ramura anuală a `interval()` = `date(an,1,1)..date(an+1,1,1)`
fix), `d101.build_xml` hardcodează `Data_I="01.01"` / `Data_S="31.12"`, `bilant_api` fereastră fixă Jan1–Dec31,
`luna=12` în antet. `regim_fiscal` = un singur câmp text; NU există câmp `data_infiintare`, nici logică de
împărțire a anului, nici de comutare micro→profit (grep `trecere/tranzitie/an_partial/perioada scurta/depasire prag`
= 0 în codul de declarații; singurele `[tranzitie]` = punte de refactor salarizare, nu regim fiscal).
- **T2 (micro→profit la depășirea pragului 100.000 EUR, art.52):** „D101 pro-rata din trimestrul de tranziție"
  cerut de scenariu NU are mecanism — generatorul presupune un singur regim pe tot anul. = decizie de produs
  (model nou: perioadă fiscală parțială + regim dual pe an; enforcement prag CA — vezi golul de praguri, tura 2).
- **T1 (înființare ~01.07.2026, an fiscal parțial):** e MICRO → fără D101. „Bilanț parțial (L13)" cerut nu are
  suport; bilanțul acoperă totuși Jan–Dec, dar cum nu există tranzacții înainte de înființare, SUMELE ies corecte
  (fereastra prinde doar iul–dec); rămâne INACURATEȚEA antetului (Data_I 01.01 în loc de 01.07). Impact fiscal
  minim (valori corecte); corectarea antetului la data înființării = decizie de produs (cere câmp `data_infiintare`).

**GOL DECLARAT (nu e implementat) — D207 nerezidenți (NR1, art.231):**
NU există `core/d207.py`, nici rută API, nici test; `declaratii_api` NU importă d207. Singurele `D207` din cod =
string în lista de tipuri IMPORTABILE istoric (`istoric_declaratii_import_api.py:133`), nu generare. Obligația
principală a lui NR1 (impozit reținut la sursă nerezidenți, scadență ultima zi feb) NU are cale de cod. = decizie
de produs (declarație nouă întreagă). IMCA pe calea DB rămâne parțial (VT/Vs/I/A nederivate din balanță — după fix,
IMCA e accesibil doar prin P47 manual / `calcul_d101(imca=)`; niciun firmă C-4 nu-l atinge, <50 mil euro).

**VERIFICAT CONFORM (proba contrarie la sursă — fără bug):**
- **D392 NU se depune** — intenționat, confirmat `C4_date.md:108` („suspendat până 31.12.2026, C-1"). Niciun cod
  nu-l emite; toate hit-urile `392` = conturi contabile / paragrafe OMFP. NU e bug de absență.
- **Decembrie / granița de an (D300/D112/D394/D406 luna 12/2026 în ian.2027):** matematica de dată e corectă —
  `common.py:40` (`luna==12 → date(an+1,1,1)`), `d406.py:237` ramura `luna==12`, `d300` nr_evidenta rulează anul.
  Nicio derivă de an. Ciclul de decembrie iese pe fereastra corectă.
- **D205 = dividende (nu salarii):** corect — salariile se declară în D112; D205 = venituri nesalariale reținute
  la sursă (dividende, tip_venit 08). Nu e gol.


## 06.08.2026 (tura 4) — C-5 P1 (stări de blocare): GARD STRUCTURAL de izolare + FINDING contracte/marcaje
C-5 = catalog de goluri de conformitate cap.6 (NU rescriere de mesaje — campanie separată, decizia Costin).
EXCEPȚIE izolare (clasele 5+6): 404 tăcut = comportament CORECT (un mesaj = scurgere de info) → se PROBEAZĂ
că izolarea ȚINE, nu se cataloghează mesaj.

**LIVRAT — gard structural `core/test_izolare_structurala.py` (8 teste cu cel existent):**
Enumeră DINAMIC toate rutele GET `{tenant_id}` din `main.app.routes` (84 azi) și probează cross-acces
pentru toate cele 4 principii → niciodată 2xx, niciodată sentinela tenantului interzis:
- (1) admin_firma cabinet A cere tenant cabinet B → refuzat pe toate rutele;
- (2) asistent (angajat) atribuit doar tA cere tC (același cabinet, neatribuit) ȘI tB → refuzat;
- (3) client de portal (tA) cere tB → refuzat;
- (4) superadmin cere tenant CU cabinet (tA) → refuzat (superadmin vede doar conturi fără cabinet, GDPR).
Chokepoint: `auth_api.schema_tenant`. Control pozitiv (adminA își vede tA=200) previne fals-verde pe 404 uniform.
Meta-gard: setul de rute enumerat e netrivial (≥50) + excepțiile documentate sunt subset al rutelor (anti-stale).
**O RUTĂ NOUĂ `{tenant_id}` care întoarce 2xx cross-tenant fără să fie în lista de excepții → gardul PICĂ.**
(RED probat: înainte de lista de excepții, gardul pica exact pe ruta de mai jos.)

**FINDING (semnalat pt decizia Costin — NU reparat aici):** `GET /tenants/{tenant_id}/contracte/marcaje`
(`main.py:5472`) întoarce 200 cross-tenant pentru orice user de cabinet. NU e breach de date: întoarce constanta
GLOBALĂ `contracte_api.MARCAJE` (nomenclator static de marcaje de contract), iar `tenant_id` e DECORATIV — ruta
depinde doar de `cere_cabinet`, NU trece prin `schema_tenant`. Inconsistență structurală (nu scurgere): singura
rută `{tenant_id}` GET care ocolește chokepoint-ul. **Decizie Costin:** fix = adaugă `schema_tenant` (defense in
depth) SAU mută ruta în afara namespace-ului `/tenants/` (e nomenclator global). Documentată explicit ca excepție
în gard (`_EXCEPTAT_GLOBAL_NON_TENANT`) ca să nu treacă tăcut și ca o rută nouă similară să nu se strecoare.
Rutele scrise (POST/PUT/DELETE `{tenant_id}`: 127/16/16) folosesc același chokepoint — probate read-only (GET)
aici; extinderea probei la metodele mutante (cu rollback) = pas viitor dacă Costin cere.

**RĂMAS P1 (catalog, nu gard) — predare:** clasele 1-4 de blocare (rol insuficient, perioadă închisă, date lipsă
`erori_generare`, patru ochi) = catalog cap.6 (trigger → mesajul care TREBUIE → ce apare acum → unde), cu bug-uri
de tăcere-la-eșec semnalate distinct. NEÎNCEPUT (buget context). Apoi P6 (cens `.oblig`) → P2 → P3 → P4 → P5 → P7.


## 06.08.2026 (tura 4) — C-5 P1: marcaje MUTAT (finding rezolvat) + gard izolare extins la scriere
Urmare decizie Costin pe finding-ul din 412d5df:
- **`/tenants/{tenant_id}/contracte/marcaje` → MUTAT la `/contracte/marcaje`** (`main.py`). E nomenclator GLOBAL
  (`contracte_api.MARCAJE`), nu per-tenant; `tenant_id` era decorativ. NU s-a adăugat `schema_tenant` ca
  defense-in-depth (ar lăsa o rută care pretinde izolare fără s-o aibă = model de copiat). Caller frontend actualizat
  (`static/js/ecrane/firme.js:2767` → `/contracte/marcaje`). Excepția documentată a fost SCOASĂ din gard — nu mai are
  ce excepta (ruta nu mai e sub `{tenant_id}`).
- **Gard `test_izolare_structurala.py` EXTINS la POST/PUT/DELETE `{tenant_id}`** (azi 243 perechi rută×metodă:
  ~83 GET + 127 POST + 16 PUT + 16 DELETE). Scrierea cross-tenant e mai gravă decât citirea → probată la fel:
  niciodată 2xx, niciodată sentinela tenantului interzis, pentru toate 4 principii. Siguranță: proxy pe conn cu
  commit/rollback = no-op + SAVEPOINT per request (rollback la savepoint) → nicio persistare în public, nicio cascadă
  de abort. Rezultat: izolarea ȚINE pe TOATE metodele (0 scurgeri pe scriere). O rută nouă `{tenant_id}` (orice metodă)
  nefiltrată → gardul PICĂ.


## 06.08.2026 (tura 5) — SEPARARE PRODUS↔DEFICIENȚĂ (înainte de campania de reparație)

Criteriu (dat de Costin): a construi ceva ce NU există (declarație nouă, model nou, regim neimplementat, câmp
pentru funcționalitate viitoare) = **PRODUS**, NU deficiență. A repara ceva ce EXISTĂ și funcționează greșit =
deficiență (se repară în campanie). Ce funcționează CORECT azi dar e fragil/neacoperit NU e deficiență.

### PRODUS — de abordat la final (NU se atinge în campania de reparație)

Fiecare: ce e · de ce e produs (nu deficiență) · cea mai devreme poziție unde decizia Costin devine blocantă.

1. **Marja în D300** (art.311/312) — cere MODEL NOU de operațiune pe marjă (flag/tabel); azi nu există structura.
   Decizie: se integrează? Blocant: când onboardezi o firmă second-hand/turism/agenție. *(GARZI 06.08 tura 2 — deja gol de acoperire.)*
2. **Regim dual / an parțial** (T1 înființare mid-an, T2 micro→profit) — cere câmp `data_infiintare` + logică de
   împărțire a anului; azi tot lanțul presupune Ian–Dec. Funcționalitate nouă. Blocant: la onboarding firmă mid-an/tranziție.
3. **D207 nerezidenți** (=F193) — DECLARAȚIE NOUĂ (art.231). Nu există. Blocant: la onboarding firmă cu plăți nerezidenți.
4. **Enforcement praguri** L1/L2/L3/L10 — azi statutul se fixează MANUAL și e CORECT; auto-detecția depășirii
   (derivare din CA/volume) = funcționalitate nouă. Blocant: niciodată tehnic — decizie oricând. *(GARZI 06.08 tura 2.)*
5. **Rezervă legală deductibilitate** (art.26(1)a) — modelare nouă în D101. Nu există. Blocant: oricând (impact profit).
6. **Coadă de validare cu erori DUK** (transparență-nu-blocaj) — mecanism nou. Nu există. Blocant: oricând.
7. **D406 — secțiunea Payments** — nu există MODEL de date de plăți (`d406.py:18` „datorie blocată pe DATE").
   Emiterea SourceDocuments reale (linia sintetică) E deficiență și SE repară; Payments = produs. Blocant: când o
   firmă datorează D406 cu plăți de raportat.
8. **50%-deductibil achiziții** (`d406.py:122`) — `cote_tva` emite azi DOAR livrări; un cod de achiziție cu
   deductibilitate 50% ar cere modelarea categoriei achiziție-deductibilă (0.5), care NU există. Produs, nu deficiență.
   *(Aici pun explicit 50%-deductibil, la cererea Costin.)* Blocant: când modelezi achizițiile deductibile parțial.
9. **IMCA-DB wiring** — legarea impozitului minim la baza de date; structură nouă. Produs.
10. **GDPR ROPA / CNP minor terț (D_8)** — temei prelucrare art.6/9 + informare art.14 + ROPA art.30. Decizie de
    conformitate + structură nouă. Blocant: înainte de a procesa pe DATE REALE un CM cu CNP de terț/minor.
11. **§F rămas** (deja „nu acum" decise): D177, F127/F128 (SPV mTLS), F175 (D307), F132/F138/F123/F130/F148, F161
    (gratuit-vs-cabinet), F187 (Ciel), F144, agricultor forfetar orfan D394 (și blocat pe sursă), plafon creșă 740.

### Blocate pe SURSĂ externă (deficiențe, dar nereparabile fără input extern — NU produs, NU în campanie acum)
- **Backfill salarizare 2025** (plafoane/valori 2025 nu-s la sursă) · **CM regim pre-L141/2025** (procente inițiale
  nu-s la sursă) · **9% deductibil auto** (blocat pe validatorul DUK R75) · **COTE la MO verbatim** (captare din
  Monitorul Oficial — extern). Se reiau când sursa e disponibilă.

### Coverage / test-seed (nici produs, nici deficiență de comportament — datorie documentată)
- **Seed-coverage C-4 tranșa 2** (achiziție IC, marjă, `d301_operatiuni` neseed-uite în corpus) — deja probate pe
  scheme efemere; rămâne datorie de seed în corpusul permanent, nu blochează nimic. *(La cererea Costin: aici e pus
  seed-coverage C-4 tranșa 2.)* · **e-Transport XSD complet**, **cron heartbeat/deadman**, **feed legislativ** =
  acoperire/extern.

### DEFICIENȚE care SE REPARĂ în campanie (ordinea de execuție)
D1 integritate import (idempotență + skip vizibil + NOT NULL bani) · A1 D406 SourceDocuments reale + cablare poartă
artefact · A6 D394 linie scutită→CUI RO · A5 MF amortizare degresivă/accelerată · D2/D5/D3/D7 integritate ascunsă +
verificator self-test + state_plata + snapshot regresie · B3 F163 fricțiune permisiuni depunere. Fiecare: probă pe
date reale (1 din 13 firme) + DUK unde atinge o declarație + gard mecanic anti-reapariție de clasă.

### CORECȚII tura 5 (findinguri din execuția campaniei — registre puse la zi)

- **D1b (NOT NULL bani) RETRAS.** Aplicat inițial pe 12 scheme, apoi revenit (DROP NOT NULL) după ce
  `test_d112_reconciliere.test_skip_suspect_brut_lipsa_e_semnalat_nu_tacut` a picat: `salariati.salariu_brut`
  NULL e o STARE-SEMNAL designată („brut lipsă → suspect", enforce-uită de reconciliere). Concluzie de fond:
  în acest codebase principiul „bază nulă = eroare" e enforce-uit SEMANTIC (detectează-și-semnalează în
  reconciliere/generare), NU la nivel de schemă. NOT NULL de DDL șterge stări-semnal și intră în conflict cu
  gardul semantic existent. Integritatea monetară rămâne la stratul de reconciliere. (Backup: `pre_d1_*.dump`.)
- **A1 (D406 SourceDocuments „1 linie sintetică") = DEJA REZOLVAT (27.07.2026), inventar stale.** `d406.py:1150-1168`
  emite `<InvoiceLine>` reale per linie din `factura_linii`, cu reconciliere antet↔linii obligatorie (`:1169-1178`);
  linia sintetică „Factura fara detaliu de linii" e DOAR fallback pt facturi fără linii în DB. Probă pe date reale:
  14/14 facturi (toate firmele) au `factura_linii` → fallback-ul NU se declanșează niciodată. Nu există deficiență A1 vie.
- **Poarta pe artefact D406 (SourceDocuments) NErulată încă** = `reconciliere_emis.verifica_d406` verifică doar
  partida dublă GL (TotalDebit==TotalCredit) și NU e cablată în `genereaza` (fixturi cu GL neechilibrat pe luna
  selectată — datoria D4). Cablarea reală cere întâi curățarea fixturilor. Rămâne în D4 (Bloc 4), nu în Bloc 1.
- **Bloc 0 livrat = D1a** (skip vizibil salariati: `sarite_cnp` era calculat și aruncat la navigare → `confirmaCaseta`
  blocant). Idempotența import: EXISTĂ deja pe toate 9 modulele (cat.1 stale). D1c (cheie unică DB) deferat: scopul
  (idempotență) deja atins prin SELECT-dedup; unique index ar cere audit al tuturor căilor de creare.

## 06.08.2026 (tura 5) — ÎNCHIDEREA campaniei de reparație: bilanț pe blocuri

Metoda: fiecare „deficiență" din inventar verificată pe cod/date REALE înainte de reparație (nu din inventar).
Descoperire de fond: **inventarul e substanțial STALE / mai matur decât părea** — majoritatea itemilor rămași
sunt deja rezolvați, decizii de produs, sau build-new, NU comportament rupt viu.

**LIVRAT (deficiențe vii, reparate + gard + probă):**
- **D1a** — skip vizibil la import salariați (`sarite_cnp` era calculat și aruncat → `confirmaCaseta`). Probat.
- **A6** — D394 nu mai aruncă linia scutită către RO CUI (L→LS). **Probă DUK** pe multi-cotă 21+11+scutit = valid.
  DATORIE 31.07 ÎNCHISĂ (marker DECIZII).
- **B3** — proprietarul cabinetului nu mai e blocat să depună (creat cu poate_pregati/valida/depune=false →
  acum true la creare + backfill 1 owner existent). Probat pe date reale (id=1968).

**STALE — nu erau deficiențe vii (inventar depășit):**
- **A1** D406 SourceDocuments „1 linie sintetică" = REZOLVAT 27.07; 14/14 facturi reale au `factura_linii`,
  fallback nedeclanșat.
- **D1b** NOT NULL bani = RETRAS (base-null e enforce SEMANTIC, nu de schemă; NOT NULL ștergea stări-semnal).
- **D1c** cheie unică DB import = deferat (idempotență deja atinsă prin SELECT-dedup pe toate 9 modulele).

**FLAGGED — cer DECIZIA ta (nu strecurate în campanie):**
- **A5** — amortizare degresivă/accelerată. Metoda e parsată/stocată/emisă în SAF-T dar calcul e MEREU liniar
  (`d406_active.py:38-39`). Reparația cere: (1) decizie de modelare fiscală (coeficienți degresivi 1.5/2.0/2.5 pe
  benzi DNF + punctul de comutare la liniar; „primul an" accelerat = 12 luni vs an calendaristic; toate pe modelul
  de acumulare LUNARĂ existent); (2) NU există golden ANAF (anaf_surse gol) și DUK validează DOAR structura, nu
  cifra → proba campaniei („regenerare + DUK") NU poate stabili corectitudinea numerică. Impact LIMITAT (d101 ia
  amortizarea fiscală ca input P11 → doar afișarea D406 Assets e afectată). xfail rămâne deschis.
- **D3** — persistare state_plata la emitere. **Build-new:** tabelul există dar NU există niciun eveniment de
  „emitere/finalizare ștat" în cod (singura referință = un `count(*)` de gardă la ștergere salariat). Persistarea
  cere construirea unui eveniment de emitere + decizia PE CE HOOK (depunere D112? acțiune nouă?). xfail deschis.

**DEFERATE — gărzi preventive pentru defecte INEXISTENTE (nu „repară ce e rupt"):**
- **D2** gard arbori paraleli (nicio a doua copie cunoscută), **D5** verificator self-test (lipsă acoperire, nu bug
  viu), **D7** snapshot regresie pe ieșirea ANAF (preventiv). Toate = acoperire, nu deficiență de comportament.

**PLAN_B.md rescris** (contabilul = utilizator de test, F1–F8 din matricea de obligații legale, E1–E12 cu E12 =
comportament la încărcare). E1–E12 NU executate — doar documentul.

### PRODUS (tura 6) — cablare deducere 100 lei/copil (art.77 alin.(10) lit.b + (12)-(13))
Deducerea de 100 lei/copil scolarizat NU e cablata: lipsesc (a) input-ul copii_scolarizati (coloana pe
salariati + UI), (b) flag-ul declaratiei parintelui (art.77(12)-(13): document inscriere + declaratie pe
proprie raspundere; la mai multi angajatori, ca nu beneficiaza la altul). Azi = gard defensiv pe functia
pura (ridica la copii_scoala>0 fara flag). Cablarea completa = build-new. Blocant: cand un cabinet are
salariati cu copii scolarizati care cer deducerea.

## 07.08.2026 — CM model de episod LIVRAT (reparatie fiscala) + reziduuri
- LIVRAT: procent pe zile_episod + diminuare/portie-angajator o data pe episod (OUG 158/2005 art.17(1)).
  Recalcul retroactiv + lock perioada confirmata cu instructiune. Migrare + UI (continuare) + gard. Probat:
  episod 20 zile -> 75% (2850 vs 2220 gresit = +630 lei), D112 byte-identic pe date reale, DUK valid pe episod.
- RAMAS: art.XI (forma pre-141 75% uniform) plumbat dar inert - blocat pe sursa verbatim (xfail #16 deschis;
  sursa oug_158_2005_pre_L141.html NU e pe server). Sugestia auto de legare a certificatelor = follow-up (calea
  manuala e completa).

## 07.08.2026 — #16 INCHIS: CM art.XI (forma pre-141) implementat
Forma art.17(1) pre-141 (75% uniform) obtinuta verbatim la MO (oug_158_2005_pre_L141.html) + varianta
datata in _VARIANTE_PROCENT_CM, selectata pe data certificatului INITIAL al episodului (art.XI). Ambele
forme nivel_sursa=MO. Granita 1 august 2025. Probat (granita + coduri speciale 100%). D112 byte-identic.
CM model de episod = COMPLET (durata + art.XI). Ramas: sugestia auto de legare (follow-up).

## 07.08.2026 — RECONCILIERE cei 11 itemi neverificati (verificati pe cod, NU reparati)

Cei 11 marcati PRODUS/blocat veneau din registru, nu din citire de cod. Verificati azi pe cod real:

**FANTOME / premisa falsa / deja rezolvat (nimic de construit) — 4:**
- **Rezerva legala art.26(1)a**: FANTOMA. Deja AUTO in d101.py:189-200 (P13, 5% x baza, plafon 20% capital) +
  motor.py:76 _rezerva_legala_2018. Premisa "nemodelata in D101" FALSA. -> SCOS din PRODUS.
- **D2 (a doua copie de generator)**: FANTOMA. Cautat efectiv: d406/d406_active/d406_stocuri = sectiuni
  COMPLEMENTARE ale aceluiasi SAF-T; d*_reconciliere = reconcilieri; un generator per declaratie. NICIO copie
  divergenta. Gardul n-are ce prinde. -> item inexistent.
- **Coada erori DUK**: ACOPERIT. duk.valideaza (duk.py:128) intoarce {stare, erori, cheie, temei} cu 3 stari
  (valid/erori/gri); coada_api.py (declaratii_coada) = flux four-eyes. Premisa "nu exista" FALSA. -> SCOS.
- **IMCA-DB**: ACOPERIT. Implementat integral in d101.py:66-82 (xfail inchis 02.08 corect). Doar auto-derivarea
  VT/Vs/I/A din balanta (firme >50M EUR, inexistente in tenanti) e amanata deliberat. Fantoma partiala.

**REPARATIE (nu build-new) — 1:**
- **B1 salarizare 2025**: PARTIAL. Premisa "valorile 2025 lipsesc" partial FALSA - salariu_minim 4050, facilitate
  300, cas/cass/impozit/cam 2025 TOATE prezente in common.py. Lipseste UN rand: plafon_facilitate_salariu_minim
  @2025 (prima intrare = 2026-01-01). Consecinta REALA testata: calcul_salariu(la_data=date(2025,3,1)) RIDICA
  PerioadaIndisponibila -> orice adeverinta/rectificativa pe 2025 blocata. REPARATIE DE DATE (1 rand COTE dupa
  verificare la sursa), NU build-new. Reincadrat din "blocat pe sursa" in "reparatie prioritara".

**BUILD-NEW INGUST (structura PARTIAL exista - registrul le supraestima ca "de la zero") — 4:**
- **Marja in D300**: motoare (tva_marja/turism/aur/agricultori) + rute FastAPI (main.py:6350+) EXISTA; ruta
  posteaza nota contabila fara factura_id, iar d300.py:537 deriva doar din facturi -> puntea marja->D300 lipseste.
- **D406 Payments**: emitterul XML (d406.py:902-948) + sursele DB (casa_operatiuni/chitante/state_plata) EXISTA;
  pull() nu populeaza plati[] (d406.py:1104). Premisa "nu exista model/sursa" FALSA. Lipseste doar query-ul pull.
- **50%-deductibil (d406.py:122)**: coduri de achizitie exista grosier (300501 hardcodat, d406.py:1158); lipseste
  codul 320xxx + BaseRate 0.5 + sursa de deductibilitate per linie.
- **Praguri**: detectie de depasire EXISTA (intrastat.analiza_flux, IMCA, casa numerar); lipseste doar pragul de
  inregistrare TVA (art.310) si micro->profit (art.47). Premisa "nu detecteaza nimic" FALSA. Sablon reutilizabil.

**BUILD-NEW INTEGRAL (structura chiar lipseste) — 3:**
- **D207 nerezidenti**: zero cod (doar string in lista de import istoric). Confirmat absent.
- **Regim dual / an partial**: fara data_infiintare (grep zero pe tot repo), fara logica an partial/tranzitie
  micro->profit mid-an. Confirmat absent.
- **GDPR ROPA / cnp_ingrijit**: cnp_ingrijit tratat fiscal complet (colectat/validat/emis D112) dar tratament GDPR
  (temei art.6 + informare art.14 + ROPA) = ZERO. Build-new de conformitate.

RATA FANTOME: azi 4 din 11 (rezerva legala, D2, coada DUK, IMCA) nu-s de construit. Cumulat pe inventar: ~16 din
45 (~35%). Corectii: rezerva legala + coada DUK SCOASE din PRODUS; D2 sters ca item; B1 reincadrat reparatie
prioritara; marja/Payments/50%-ded/praguri reincadrate build-new INGUST (nu de la zero).

## 07.08.2026 — B1 reincadrat: CLASA de valori datate lipsa pentru 2025 (nu un rand)
- REPARAT + verificat: plafon_facilitate_salariu_minim @2025 = 4300 (OUG 156/2024 art.LXVI, anaf_surse verbatim).
- RAMAS (blocheaza calcul_salariu 2025): tichet_masa_plafon @2025 - valoarea nominala maxima a tichetului de masa
  in 2025 (indexata semestrial, Legea 165/2018 art.32). NU e in anaf_surse (doar cadrul). Cere sursa: ordinul/
  comunicatul cu valoarea concreta sem I 2025 (si sem II 2025 daca difera). tva_redusa @martie 2025 lipsa dar
  nefolosit de salarizare.
- DATA_START_SISTEM = 1 ianuarie 2025: 2023/2024 sub podea (nereparabile by design). calcul_salariu(2025) ramane
  blocat pe tichet_masa_plafon pana se aduce sursa. B1 e PARTIAL (plafon inchis; tichet 2025 = urmator rand).

## 07.08.2026 — ratchet agenda: baseline bifa-pe-baza-schimbata 3->6 (B1)
Adaugarea plafon_facilitate_salariu_minim @2025 (B1) a atins 6 clustere prin graf (facilitate/suprataxare/
proratare/tichete masa-vacanta-culturale-cresa) -> toate stau pe o cota EXTINSA dupa √. Extindere istorica
verificata la sursa (OUG 156/2024), valorile 2026 NEschimbate. Baseline ridicat 3->6, de re-coborat cand
cele 6 clustere se re-ancoreaza dupa deblocarea completa a 2025 (tichet_masa_plafon).

## 07.08.2026 — B1 tichet 2025 aproape inchis (o singura luna ramasa)
Tichet_masa_plafon 2025: 40,04 (ian-mar, Ord.4.679/2024), 40,18 (apr-sep, Ord.484/2025), 45 (de la noiembrie,
Legea 201/2025) - toate verbatim la sursa. Extensie _deriva_data_out (respecta data_out explicit) + data_out
30 sep pe 40,18 => octombrie 2025 e GOL motivat, NU 40,18 tacit. Corectie: 45 de la noiembrie 2025 (era gresit
@2026). RAMAS: octombrie 2025 - cere Ordinul MF tichet-masa sem II 2025. calcul_salariu(2025) merge except octombrie.

## 07.08.2026 — ratchet agenda 6->14 (B1 tichet 2025)
Adaugarea tichet_masa_plafon 2025 (peste plafon_facilitate) a atins ~7 clustere x 2 cote = 14 stale prin
graf. Toate = adaugari istorice verificate la sursa (2026 neatins, D112 byte-identic). Baseline 6->14.
FOLLOW-UP curatenie: re-ancorarea celor ~7 clustere salarizare/tichete (√ 07.08 + bump) ar readuce baseline
la 3 - de facut cand se re-verifica functional clusterele pe 2025 (dupa deblocarea octombrie).

## 07.08.2026 — Corpus (1) LIVRAT: 13 temeiuri legate la fisiere locale (MO 4->17)
Multe COTE aveau sursa deja in anaf_surse dar url nelegat/extern (salariu_minim -> just.ro blocat!). Legate +
ridicate MO dupa verificare verbatim. Ramas Corpus (2): manifest INDEX + 3 garzi. Corpus (3): acte lipsa (lista
scurta dupa (1)+(2)) - OUG 89/2025, OUG 8/2026, OG 16/2022, OUG 115/2023, Legea 296/2020, Legea 70/2015.

## 07.08.2026 — Corpus (2) LIVRAT: manifest INDEX.json + 3 garzi (G1 sursa-locala, G2 forma-acopera, G3 volatil-fara-MO)
COTE MO+local 17->19. Garda 3: prag 18 luni pe valoarea curenta non-MO -> set de 5 (4 plafoane OUG 8/2026 +
OUG 89/2025 + tva_redusa_5 de decis), zero zgomot pe REDARE stabile. Ramas Corpus (3): lista scurta de acte lipsa.

## 07.08.2026 — Corpus (3) LIVRAT: OUG 8/2026 + OUG 89/2025 legate verbatim (6 valori -> MO)
COTE MO 18->24, REDARE 15->9. D112 byte-identic. Garda 3 semnaleaza acum DOAR tva_redusa_5 (de decis).
Verificat inainte de scriere: lit.b plafon_facilitate era corect. facilitate 300 @2025 ramas REDARE (OUG
89/2025 nu-l surseaza pt 2025). REDARE ramase = doar istorice + tva_redusa_5.

## 07.08.2026 — CANDIDAT (audit de reguli): CNP salariat la adaugare directa valideaza DOAR formatul, nu cifra de control
**Stare: LIPSA (candidat, neconfirmat prin repro pe flux inca).** Adus de Costin din auditul de reguli 07.08.
**Constatare:** `core/salariati_api.py:85-87` valideaza CNP-ul PROPRIU al salariatului la adaugarea directa doar
cu `_CNP = re.compile(r"^\d{13}$")` (13 cifre, format) — NU verifica cifra de control. In contrast, calea de
IMPORT foloseste `core/salariati_import_api.py:15 valideaza_cnp` (cheie de control 279146358279 + data + judet),
si tot `valideaza_cnp` e chemat la `salariati_api.py:344-345` pentru `cnp_ingrijit` (CM cod 09/91/92/17). Deci
acelasi camp (CNP) e validat cu cifra de control pe import + pe cnp_ingrijit, dar NU pe adaugarea directa a
salariatului. Provizionarea blocheaza corect (de reconfirmat). Un CNP cu cifra de control gresita intra tacut si
ajunge in D112 (identificatorul persoanei fizice) — declaratie potential respinsa la ANAF pe validare CNP.
**Vanatoare de clasa (de facut la reparatie):** toti consumatorii care accepta CNP de intrare — adauga salariat
(api + eventual asociati/administratori), nu doar salariatul. `valideaza_cnp` exista deja (import) => reparatia =
refolosire, nu cod nou.
**Ce l-ar prinde azi:** nimic — nicio garda nu compara cele doua cai de validare CNP. De ancorat in E1E12_GASITE.md
ca INSTANTA daca il intalnesc la E2/E6 (adaugare salariat pe F2); altfel ramane candidat separat aici.

## 07.08.2026 — CANDIDAT (clasa): "running == HEAD" — al treilea loc unde munca poate lipsi TACUT
**Stare: LIPSA (candidat de clasa; azi reparat DOAR pe instanta prin restart).** Constatat la parcurgerea E1-E12.
**Constatare:** serviciul `iconta-nou` (systemd, nginx -> :8010) a rulat cod din 01.08 timp de 6 zile / 45+
commituri, TACUT. Publicat (git) != ruleaza. Post-commit (cablat 07.08) publica pe origin/main + backup dar NU
repune serviciul si nu verifica procesul viu. Efect probat: D112 dadea 500 pe prod (Temei/nivel_sursa pe common.py
stale in memorie) si firmele noi se provizionau cu schema driftata (lipsa perioada_confirmata + 10 coloane).
**Mecanism ALES (Code, 07.08) — detector VIZIBIL periodic, NU auto-restart:**
- Motiv: constrangerea lui Costin "sa nu repornesti serviciul in mijlocul unei operatii a unui contabil"
  EXCLUDE varianta post-commit-repune-serviciul (post-commit se declanseaza la momente arbitrare). Detectorul nu
  reporneste niciodata; un om reporneste la fereastra sigura; driftul devine ZGOMOTOS, nu tacut (exact ce a lipsit).
- (1) `/versiune`: app-ul stampileaza la pornire `git rev-parse HEAD` (global in lifespan startup) si il expune.
- (2) cron (core/cron.py) la N minute: compara running (`/versiune`) vs `git rev-parse HEAD` (disc) vs `origin/main`.
  Divergenta -> ESEC VIZIBIL: sentinela `.git/RUNNING_STALE` (ca PUSH_*_ESUAT) + alerta Brevo + banner in log.
  Niciodata tacut, niciodata auto-restart.
- (3) inchiderea raportului (§2.2 sect.11) devine PATRU-way: HEAD = origin/main = backup = RUNNING; raportul nu e
  "incheiat" cat timp procesul viu != HEAD. Inchide "al treilea loc" numit de Costin.
**Ce l-ar prinde azi:** nimic. Suita ruleaza pe disc, nu pe procesul viu. De implementat ca urmatoarea campanie
(cod + gard + RED/GREEN); restartul de azi = instanta.

**LIVRAT 08.08 (partea VIZIBILA IN APP, comanda Costin) — mecanism (1):** `core/versiune.py` stampileaza in lifespan (memoria procesului) commitul de pornire = codul rulat (NU se deduce din mtime-uri); `stare_versiune` pura compara cu HEAD de pe disc. Endpoint `GET /admin/versiune` gated `cere_rol("superadmin")` (403 pt orice alt rol). Frontend: `desktopAdmin` (admin.js) afiseaza o `.caseta-atentie` (cap.6) DOAR la divergenta, DOAR pt superadmin, nimic cand e la zi; nu reporneste, nu repara. Gard `core/test_running_head.py` (divergenta->aprins, egalitate->stins, necunoscut->nu alarmeaza; RBAC superadmin 200 / alte roluri 403; mutatie != -> == => rosu).
**RAMANE (mecanism 2+3, ALT scop, necablat aici):** cron periodic (core/cron.py) + sentinela `.git/RUNNING_STALE` + alerta Brevo (semnal in afara app-ului, cand nimeni nu e logat ca superadmin); raport PATRU-way la inchidere (HEAD=origin/main=backup=RUNNING) - vezi DECIZII; audit schema PUBLIC vs HEAD (candidatul urmator).

## 07.08.2026 — CANDIDAT: drift de schema PUBLIC fara gard (aceeasi clasa, alt strat)
**Stare: LIPSA (candidat).** `test_toti_tenantii_conform_cu_template` verifica SCHEMELE DE TENANT vs
tenant_template.sql (verde pe 12/12 pe prod => migrarile de schema tenant sunt la zi). NU exista gard echivalent
pentru schema PUBLIC: o coloana/tabela noua adaugata pe public (ex. declaratii_coada, accounting_firms) intr-un
commit HEAD nu ar fi prinsa de template-guard-ul de tenant. De adaugat un audit public analog (referinta = un
public_template sau DDL-urile *_ddl.sql) daca se doreste inchiderea completa a clasei "migrari la zi pe prod".

## 07.08.2026 — LIVRAT: gard CNP cifra de control pe calea DIRECTA (DEFECT-2 din parcurgerea E1-E12)
**Stare: ACOPERIT.** Instanta = candidatul CNP de mai sus (adaugare directa salariat, doar format). Reparatie prin
REFOLOSIRE: `valideaza_salariat` cheama acum `valideaza_cnp` (cheia 279146358279), la fel ca import + cnp_ingrijit.
Acopera CREATE si EDIT (ambele trec prin `valideaza_salariat`: creeaza_salariat:161, actualizeaza_salariat:217).

| gard | fisier:linie | ce face imposibil | mutatia care il probeaza |
|---|---|---|---|
| valideaza_salariat cere cifra de control | core/salariati_api.py:86 (cnp_control_v1) | CNP 13-cifre cu control gresit intra prin POST/PUT salariat -> ajunge in D112 -> respins DUK (cnpAsig) | git checkout (pre-fix) -> 5 teste rosii cu motivul corect; sha256 D112 tenant_001 IDENTIC pre/post (no-op) |
| toate caile CNP refuza control + anti-cale-noua | core/test_cnp_control.py | o cale noua de INSERT CNP fara valideaza_cnp; regresie valideaza_salariat la format-only | test_nicio_cale_de_insert_CNP_fara_validare_de_control + test_valideaza_salariat_nu_regreseaza_la_format_only |

**Vanatoare de clasa (CNP, completa):** cai de scriere CNP = salariat create/edit (REPARAT azi), cnp_ingrijit
(concedii), import salariati, import asociati — ultimele trei foloseau deja valideaza_cnp. NU exista alta cale
directa (adaugare asociat = doar import). Proba: CNP control-gresit refuzat pe TOATE (test_toate_caile_CNP).

## 07.08.2026 — CANDIDAT (din vanatoarea de clasa CNP/CUI): control CUI neverificat pe mai multe cai
**Stare: LIPSA (candidat; partial decizie de produs).** Control OFFLINE CUI verificat DOAR la: provizionare tenant
(`cui_valid`) + import parteneri solduri (`valideaza_cui`). NEverificat offline: client create/edit (clienti_api),
factura `tert_cui` (emite_factura / achizitie-*), CUI PROPRIU firma la EDITARE (firma_profil.salveaza_date; validat
doar la provizionare). NUANTA: `tert_cui`/client pot fi parteneri STRAINI (CUI ne-romanesc, fara cifra de control
romaneasca) => validarea offline nu se aplica universal; azi se bazeaza pe ANAF (existenta), best-effort. DAR CUI-ul
PROPRIU al firmei e MEREU romanesc -> editarea lui AR TREBUI sa valideze controlul (azi nu). Recomandare: gard pe
CUI propriu (firma_profil) + validare CONDITIONATA (cand pare romanesc: RO/toate cifre) pe client/tert_cui. Decizie Costin.

## 08.08.2026 — G10 Faza 2 batch 1 LIVRAT (date_firma + salariat) + contract backend {detail, erori_campuri}
Rollout mecanism A (eroare langa camp, DS cap.6 v2.30). date_firma: validare client colecteaza TOATE erorile ->
eroareCamp per camp (#df-{k}, #vf-tip_decont), nu un mesaj generic. salariat: valideaza_salariat intoarce acum
(camp, mesaj); ruta trimite {mesaj, erori_campuri}; api.js poarta erori_campuri (_erisCampuri); frontend plaseaza
fiecare langa #sn-{camp}. Gard nou core/test_g10_eroare_langa_camp.py cu lista G10-A (flux_concediu + date_firma +
firme.js), extins la fiecare batch. Probe headless 5/5 pe ambele (9 erori date_firma toate deodata sub camp +
conditionala TVA + fara stivuire; 2 erori backend salariat plasate langa CNP/salariu). Restart facut (backend cod).

## 08.08.2026 — G10: e-Transport = ABATERE cunoscuta, tratat la BATCH 3 (restructurare, nu plasare)
etransport_ecran.js NU intra in rollout-ul standard G10-A. Motiv: RANDURI DINAMICE ("bunuri" adaugate/sterse) iar
campuriLipsaCorp intoarce ETICHETE ("Bun 1: Scop"), nu id-uri DOM; mecanismul A cere id stabil per camp. Ramane pe
mecanismul B (mesaj colectat vizibil "Completeaza campurile obligatorii: ...") - conform "niciodata tacere la o
actiune esuata", contabilul nu e blocat/mintit. Restructurarea = schimbare de FORMA pe un ecran functional ->
batch 3 SEPARAT + ULTIMUL (o regresie sa se vada ca vine de la e-Transport, nu amestecata cu plasarea). Batch 3
cere (decizia Costin): (a) id-uri stabile per camp-din-rand care supravietuiesc add/delete (randul 2 sters sa NU
faca eroarea randului 3 sa arate spre alt camp); (b) campuriLipsaCorp -> id-uri, nu etichete (verifica intai cine
o mai consuma); (c) probe headless: rand adaugat / sters din mijloc / doua randuri cu erori / re-validare dupa
corectarea unuia; (d) no-op sha256 pe XML e-Transport. STOP daca id-urile stabile cer schimbarea modelului de date.
Gardul test_g10_eroare_langa_camp tine e-Transport EXPLICIT in afara listei pana la batch 3.


## 08.08.2026 — DATORIE: proba vizuala G10 batch 2 (D301/D390) LIPSA — NU "probat"
Contractul backend `{mesaj, erori_campuri}` e probat end-to-end (smoke HTTP: D301 -> 422 erori_campuri
[curs, nrdoc, datadoc]; D390 -> [tara, cod]) SI mecanismul frontend (`eroareCamp` cu prefix `d301-`/`man-`) e
IDENTIC cu batch 1 (probat vizual pe salariat/date_firma: sub-camp, span DUPA input, fara stivuire). DAR proba
vizuala HEADLESS pe cele 5 criterii (toate erorile deodata / plasare sub camp / conditionale / re-validare fara
stivuire / aranjare) LIPSESTE pentru D301 si D390. Cauza: nav-ul ecranului Declaratii e fragil in headless (card
firma -> `#dec-tip` -> `#dec-continua` -> `pas2()`/DUK -> sectiune in `<details open>`; click pe "Declaratii" nu
se stabilizeaza, `#dec-tip` nu apare in timp util). De INCHIS cu un nav headless mai robust: selectare `#dec-firma`
intai + asteptare DUK (pas2 e lent), SAU deschidere directa a declaratiei d301/d390 pe o firma cu aplicabilitate
(tenant_001/S4 nu are neaparat d301/d390 in luna testata). PANA ATUNCI: D301/D390 raman "cod corect + contract
probat backend", NU "probat vizual". Nu se marcheaza bifa vizuala G10 pe ele fara aceasta proba.


## 08.08.2026 — cap.24 batch 3a e-Transport LIVRAT + DATORIE regula 2 in afara batch 3

e-Transport restructurat (cap.24): campuriLipsaCorp ELIMINAT (oglinda care drifta pe valoare_fara_tva);
backendul (core/etransport.py:campuri_required_lipsa, 422.campuri = {camp,eticheta}) e singura autoritate;
construiesteCorp NU mai filtreaza (lista trimisa = lista randata); model pozitional cu valori + re-randare
integrala la add/delete + buton stergere/rand; erorile 422 plasate langa camp prin eroareCamp (api.js
_erisCampuri normalizeaza campuri->{camp,mesaj}). e-Transport a intrat in lista G10-A (test_g10); emitere
ramane exceptat pana la 3b. Gardul MIRROR_CAMPURI_LIPSA scaneaza acum si e-Transport (nu mai e exceptat).

DATORIE (cap.24 regula 2 incalcata azi, IN AFARA batch 3 - de reparat la ecranele lor, batch propriu):
- facturi_ecran.js:1078 - `linii.filter((l) => l.descriere && l.cantitate)` inainte de POST /facturi/emite.
- firme.js:1228 - `rtLinii.filter((l) => l.articol_id && l.cantitate > 0)` inainte de POST reteta.
Ambele filtreaza randuri inainte de validare -> un rand incomplet dispare tacit (aceeasi clasa reparata azi la
e-Transport). NU se cableaza gard mecanic pe regula 2 (ar aprinde aceste ecrane, in afara batch 3): ratchet.


## 08.08.2026 (seara) — G10 ROLLOUT ÎNCHIS (0 excepții) la a5c7808

Batch 3b (emitere) livrat -> G10 Faza 2 (rollout eroare-lângă-câmp, mecanism A) COMPLET pe toate formularele
multi-câmp: pilot flux_concediu, batch 1 (date_firma + salariat), batch 2 (D301/D390 manual), batch 3a
(e-Transport), batch 3b (emitere). `_G10_A_EXCLUSE = []` (fără excepții); gardul MIRROR_CAMPURI_LIPSA scanează
acum TOATE ecranele din static/js/ecrane -> 0. cap.24 (randuri dinamice) scris (DESIGN_SYSTEM v2.31) + cablat
(regula 4 = MIRROR). Garduri headless COMISE care rulează în poartă: `core/test_etransport_randuri_dinamice.py`
+ `core/test_emitere_randuri_dinamice.py` (5 scenarii DOM + no-op sha256 pe ieșirea reală fiecare;
auto-provizionează chromium). Commituri: 908ab6b (cap.24), 119aea5 (3a), c0be1cf (gard 3a), a5c7808 (3b).

ÎNCHIS 08.08 (batch propriu cap.24 regula 1+2): clasa "filtrare înainte de validare -> rând dispare tăcut"
închisă pe cele DOUĂ ecrane numite — **facturi-recurente** (`formSablon`, facturi_ecran.js) + **rețete**
(`sectiuneaCV`, firme.js): model pozitional (`fr-l{i}-*` / `rt-l{i}-*`) + re-randare integrală (regula 1) +
ștergere splice + FĂRĂ filtrare (regula 2); backend autoritar per-linie {camp,eticheta}
(`facturi_api.linii_campuri_lipsa(prefix="fr-l")` reutilizat = o singură sursă, regula 4;
`retete_api._ingrediente_campuri_lipsa`), rute 422 {mesaj, erori_campuri}, erori prin `eroareCamp` (cap.6 mec. A).
Garduri headless COMISE (5 scenarii DOM + no-op, mutație filtru->roșu): `core/test_facturi_recurente_randuri_dinamice.py`
+ `core/test_retete_randuri_dinamice.py`. CORECȚIE la formularea veche: `facturi_ecran.js:1078` filtra înainte de
POST **/facturi-recurente** (nu /facturi/emite — emite era reparat la 3b), verificat la sursă.

ÎNCHIS 08.08 (decizia Costin = (a); "un gard cu excepții nu e gard"): NIR + inventar REPARATE, apoi regula-2 guard
CABLAT în verificator_conformitate.py FĂRĂ NICIO EXCEPȚIE (`FILTRARE_INAINTE_VALIDARE`, PRAG 0). Clasa e închisă
"peste tot": toate cele 4 ecrane purtătoare conforme (emitere + e-Transport; facturi-recurente + rețete la a771f25;
NIR + inventar azi) → guardul rulează 0.
- **NIR** (`ecranStocuri`, firme.js): trecut la model pozitional `nir-l{i}-*` + re-randare integrală din model
  (regula 1, în locul appendChild/remove) + ștergere splice + FĂRĂ filtrare (regula 2); backend
  `stocuri_api._nir_campuri_lipsa` (denumire + cantitate + preț achiziție), ruta /stocuri/nir 422 {mesaj,
  erori_campuri}, erori prin `eroareCamp`. Gard `core/test_nir_randuri_dinamice.py` (5 scenarii DOM + no-op).
- **inventar** (`sectiuneaCV`, firme.js): listă FIXĂ (fără add/delete → regula 1 nu se aplică); fixul = doar
  regula 2: se trimit TOATE articolele (`.map`, fără `.filter`), backendul e autoritatea (`stocuri_cv_api.inventar`
  sare faptic gol = necontorizat, NU eroare; `camp` per articol pe valoare invalidă → `eroareCamp` la
  `cvi-a{id}-faptic`). Gard `core/test_inventar_randuri_dinamice.py`. Mutație (ambele ecrane): filtru reintrodus →
  verificator `FILTRARE_INAINTE_VALIDARE=2, TOTAL=2` + gardurile headless roșii.

REGISTRUL A FOST GREȘIT (corecție cerută de Costin, confirmată la sursă): intrarea 3a de mai sus (l.~2062) spune
`facturi_ecran.js:1078` filtra înainte de POST `/facturi/emite` — FALS. 1078 e în `formSablon` → POST
**/facturi-recurente** (emite = emitere_ecran.js, reparat deja la 3b). Descoperit prin grep pe fișier; formularea
corectă e cea din batch-ul a771f25 + aici (TEMEIURI pct.6: faptele din comandă/registru = hartă de căutare, nu temei).

## 08.08.2026 (noapte) — A2 REPARAT (DUK severitate) + finding NOTAT (d112 Creante cif<>AJPIS)

**A2 ÎNCHIS (tura de parcurgere+reparație):** validatorul DUK punea ORICE ieșire în `stare="erori"`, deci o
ATENȚIONARE (`A:`, care NU blochează depunerea) apărea sub „Validatorul ANAF a găsit erori" — severitate confundată.
Cauza la sursă (`core/duk.py`): `stare = "erori" if rez else "valid"`, fără clasificare A:/E:. Fix: `duk.severitate()`
clasifică FAIL-SAFE (linie `E:` -> "eroare"; doar `A:` -> "atentionare"; necunoscut/non-gol -> "eroare"; niciodată
retrograda un E: sau un format nerecunoscut). Câmp nou `severitate` în toate return-urile `valideaza`/`_valideaza_saft`.
Frontend `declaratii.js`: `severitate=="atentionare"` -> casetă `.dec-avert` „a semnalat atenționări (nu blochează)",
altfel roșu ca înainte. Consumator UNIC (declaratii.js:205), FĂRĂ gating pe `stare=="erori"` (submit e pe rol `poate_depune`)
-> relabeling pur, sigur. Gard `core/test_duk_severitate.py` cu FIXTURI REALE (capturate live prin serviciu):
atenționare = „A: asigurat... B4_5P(4325)..." (Panificatie), eroare = „E: angajator... ACreante..." (Ferma Agricultor);
mutație E:->atentionare -> roșu.

**FINDING NOTAT (nereparat — cere structură fiscală, per constrângere „nu inventa"):** `d112` pentru **Ferma
Agricultor Forfetar** (tenant 4844), aug 2026, e RESPINS de DUK: „E: angajator (1) eroare regula: ACreante:
sectiunea Creante este obligatorie pt cif <> cif AJPIS". Generatorul (`core/d112.py`, secțiunea `angajatorA` =
„Creante") nu emite secțiunea de creanțe când firma are creanță CM (indemnizații recuperate FNUASS) și `cif <> cif
AJPIS`. Panificatie (cif == cif AJPIS) doar atenționare, deci e specific cazului cif<>AJPIS. Repararea cere structura
exactă D112 Creanțe (structura_D112_0126_030226) confirmată la sursă ANAF — NU o inventez. Datorie deschisă.

## 09.08.2026 — angajatorA min-1 LIVRAT (Creante la obligatii zero) + datoria celor 13 campuri D112 v1.03-072026

**LIVRAT:** garda `if val > 0` scoasa din `core/d112.py` add_oblig -> sectiunea `<angajatorA>` ("Creante") se emite
si la obligatii ZERO. Temei VERBATIM: XSD oficial `anaf_surse/d112_06082026.xsd` (angajatorA minOccurs implicit=1,
maxOccurs=29) + `structura_D112_0726_030826.pdf` ("1-41 aparitii"). Continut la zero CONFIRMAT EMPIRIC pe validatorul
J27.0.1 (autoritatea): 11/12 firme au trecut de la EROARE "ACreante: sectiunea Creante obligatorie pt cif <> cif
AJPIS" la VALID. Gard `core/test_d112.py::test_angajatorA_prezenta_si_la_obligatii_zero` + count 4->6 in
test_angajatorA_apare_in_xml; mutatie (garda reintrodusa) -> rosu.

**DATORIE FISCALA D112 v1.03-072026 (13 campuri, NEconfirmate verbatim = NEimplementate).** Adaugate de Ordinul
605/95/928/2314/2026 (aplicabil 07/2026), semnalate de J27.0.1 pe Panificatie (asigurat 6, sectiunea D). Ce lipseste
pentru fiecare = FORMULA/semantica exacta din `structura_D112_0726_030826.pdf` (in corpus) - de extras verbatim +
implementat, apoi revalidat pe J27.0.1:
- **D_14a** (asiguratD, IntPoz2, "14. Zile prestatii") — validatorul: "atributul trebuie sa existe"; regula S104a:
  D_15 <= D_15a; ERR daca D_14a>5. LIPSA: formula de calcul a zilelor de prestatii (a).
- **D_15a** (asiguratD, IntPoz2) — varianta "a" a D_15 (zile). LIPSA: definitia + formula.
- **D_16a** (asiguratD, IntPoz2) — varianta "a" a D_16 (zile). LIPSA: definitia + formula.
- **D_20a** (asiguratD, IntPoz15) — varianta "a" a D_20 (suma). LIPSA: formula de calcul.
- **D_21a** (asiguratD, IntPoz15) — varianta "a" a D_21 (suma). LIPSA: formula de calcul.
- **D_9a** (asiguratD) — camp nou concediu medical. LIPSA: semantica + cand e obligatoriu.
- **D_9b** (asiguratD) — camp nou concediu medical. LIPSA: semantica + cand e obligatoriu.
- **c2_155**, **c2_156** (angajatorC2) — campuri noi (J27.0.0). LIPSA: definitia + formula agregat.
- **E2_156** (asiguratE2) — camp nou. LIPSA: definitia + formula.
- **B3_7D** (asiguratB3) — camp nou. LIPSA: definitia + formula.
- **C_10D** (asiguratC) — camp nou. LIPSA: definitia + formula.
- **E3_97** (asiguratE3) — camp nou. LIPSA: definitia + formula.
Toate 13 se aplica de la 01.07.2026 (structura, "In sectiunea D asigurat – modificari" + changelog J27.0.0). Sursa
e in corpus (`anaf_surse/`), deci datoria e actabila - nu blocata extern.

## 09.08.2026 — DS clasa "oprire tacuta/generica": dialog nativ INTERZIS peste tot + load-error la ecran-nota

**GASIT 12, REPARAT 5, RAMAN 7.**

**REPARAT (afiseaza acum mesaj canonic clar - ce/de ce/ce urmeaza):**
- app.js:108/112 `alert()` nativ (magic-login) -> `.caseta-atentie`: "Linkul de logare a expirat sau a fost deja
  folosit. Intra in cont cu emailul si parola, sau cere un link nou." / "Nu am putut finaliza logarea prin link
  (probabil o problema de retea). Reincearca, sau intra cu emailul si parola." (DS cap.5: alert/prompt/confirm
  native INTERZISE).
- asistenti.js:330 `.mig-gol` -> `.ecran-nota`: "Calitatea nu a putut fi incarcata."
- firme.js:481 `.mig-gol` -> `.ecran-nota`: "Nu am putut rula verificarile."
- admin_activitate.js:117 catch->`.stare-goala` -> `.ecran-nota`: "Nu am putut incarca istoricul cabinetului. Reincearca."

**GARD MECANIC:** `core/test_dialog_nativ_frontend.py` — (1) ZERO alert/prompt/confirm native in TOT frontendul
(ecrane/ + static/js/*.js), mutatie alert nou -> rosu; (2) ratchet `.mig-gol` <= 3 (nu creste). Acopera si zona
NEscanata de verificator.

**FINDING STRUCTURAL:** verificator_conformitate.py (DIALOG_BROWSER + toate regulile DS) scaneaza DOAR
`static/js/ecrane/*.js` (BAZA). `static/js/*.js` (app.js/navigator.js/sesiune.js/api.js) NU sunt scanate -> orice
abatere DS de acolo scapa (asa a trecut `alert()` din app.js). Gardul nou acopera dialogurile in ambele zone;
extinderea INTREGULUI verificator la static/js/*.js = workstream separat (risc de multe flag-uri noi, poarta).

**RAMAN (listate, nereparate):**
- firme.js:1640/1668/2021 `.mig-gol` — CONTINUT (r.mesaj rezultat descarcare / lista alerte / nota-avertisment
  "Atentie: nota e legata de factura #.. — modificarea sumei schimba soldul facturii"), NU opriri de load;
  clasa ad-hoc (cap.6), dar afiseaza text clar. Cat.3 (cosmetic). De migrat: 2021 la `.caseta-atentie`, 1640/1668
  la afisare canonica. Coboara ratchet la reparare.
- control.js:79, declaratii.js:265/327 catch->`.stare-goala` (mesaj clar "Nu am putut incarca <X>", dar clasa
  stare-goala in loc de ecran-nota) — DECLARATION-ADJACENT (control fiscal / ecran declaratii). Neatinse aici
  (constrangere "nu atinge generatoarele" interpretata conservator). De migrat la ecran-nota intr-un pas dedicat.
- login.js:295 catch{} gol pe prefetch `/public/config` (poarta beta) — degradare GRATIOASA (campul de cod beta
  nu apare daca fetch-ul pica); NU e o actiune a userului, nu e stare falsa actabila. Benign, listat.

## 09.08.2026 — Verificatorul acopera TOT frontendul + cele 7 opriri ramase reparate

**RADACINA (finding structural din tura precedenta):** verificatorul scana DOAR `static/js/ecrane/*.js` (BAZA).
`static/js/*.js` (app.js/navigator.js/sesiune.js/api.js) scapau TUTUROR regulilor DS. Acum extins: `_DIRS_FRONTEND`
= [ecrane, static/js] -> toate regulile scaneaza tot frontendul. `api.js` = SURSA canonica (esc/ICOANE/paleta
culori) -> exceptata la registre (`nume != "api.js"` pe redef-esc/strip-html/icoane_local/culoare_card_hex);
comentariile intregi (`//` `/*` `*` `<!--`) nu se mai flagueaza (fals-pozitive pe marcaje).

**22 candidate aprinse de extindere -> 0:**
- SURSE canonice api.js (excepate, principiu deja scris in DS cap.10/13): 7 culoare_card_hex (paleta entitate),
  2 icoane_local (dictionarul ICOANE), 2 esc_local (definitia esc + corpul).
- COMENTARII (comment-skip): 2 dialog_browser (marcaje `// alert() INTERZIS`).
- REPARATE real: navigator.js:104 diacritice ("se incarca realizarile" -> "se incarca realizarile" cu diacritice);
  navigator.js x5 strip-html `.replace(/[<>&]/g,"")` (data-lossy, cap.10c) -> `esc()` canonic (+ import esc);
  app.js:8 font-size:14px -> `var(--text-mic)` (banner failsafe, cap.14); app.js:43/77 border-radius:12px
  (carduri activare/reset) -> `var(--raza)` (cap.16).

**Cele 7 opriri ramase (tura precedenta) — REPARATE:**
- firme.js:1640 `mig-gol` (rezultat descarcare gestiune) -> `arataMesaj(zonaM, r.mesaj, "info")` (cap.6).
- firme.js:1668 `mig-gol` (lista avertismente registru casa) -> o singura `.caseta-atentie` cu `.ca-mesaj`/rand (cap.5).
- firme.js:2021 `mig-gol` (nota-avertisment legatura factura) -> `.caseta-atentie`.
- control.js:79 `catch -> .stare-goala` (control fiscal) -> `.ecran-nota` (load-error, nu gol).
- declaratii.js:265/327 `catch -> .stare-goala` (D390 clasificare / D301 operatiuni; ECRAN UI, nu generator) -> `.ecran-nota`.
- login.js:295 `catch {}` gol pe prefetch `/public/config` -> `catch (e) { console.warn(...) }` (nu mai e tacere
  totala; prefetch optional, nu actiune a userului).

**GARZI MECANICE (mutatie-probate 09.08):**
- verificator regula noua **STARE_GOALA_EROARE** (cap.6): `catch{...stare-goala}` = eroare randata ca gol -> flag
  (mutatie: revert la stare-goala -> TOTAL 1). Frontend integral.
- `test_verificator_acopera_tot_frontendul` (core/test_dialog_nativ_frontend.py): asigura ca verificatorul
  ramane extins la static/js/*.js + exceptiile api.js (mutatie: scoate `_DIRS_FRONTEND` -> rosu).
- ratchet `.mig-gol` coborat 3 -> **0**, numarat pe utilizare de atribut `class` (nu mentiuni in comentarii)
  (mutatie: un `class="mig-gol"` nou -> rosu).
- `test_niciun_dialog_nativ_in_frontend` (deja) acopera ambele zone.

**PUNCT DE OPRIRE ridicat (tipar fara regula scrisa, cap.6):** lista de avertismente inline (registru casa,
firme.js:1668) nu are componenta DS dedicata. Am continuat mapand-o la o singura `.caseta-atentie` (avertismente
= atentionari). Intrebare pt Costin: e `.caseta-atentie` casa corecta pt o LISTA de avertismente de registru,
sau DS primeste o componenta "lista de avertismente"? (Nu am scris capitol nou — constrangere.)

**Observatie (nu blocaj):** bannerul global de eroare (app.js `_bannerEroareGlobala`, window.onerror) si bannerul
de boot login (`_bannerLoginEroare`) raman cu pozitionare inline prin NECESITATE (se randeaza cand aplicatia /
CSS-ul poate fi rupt). Doar `font-size` a trecut la token; culorile/pozitia inline nu sunt flaguite de nicio
regula si sunt legitime pt un failsafe. Daca se vrea o regula scrisa "failsafe/pre-CSS", e decizie DS.

## 09.08.2026 (tura 2) — D112 v1.03-072026: D_14a/D_15a/D_16a LIVRAT; restul 10 campuri = datorie rafinata

**LIVRAT (verbatim + gard + DUK J27 VALID).** Din cele 13 campuri ale Ordinului comun 605/95/928/2314/2026
(D112_A7.2.6 v7, aplicabil 07/2026), s-au inchis TREI - singurele confirmabile verbatim SI actabile fara date noi:
- **D_14a** = zile prestatii (lucratoare) suportate de angajator = `za` (zile_ang). structura_D112_0726_030826.pdf rd.103a.
- **D_15a** = zile prestatii suportate de FNUASS = `zf` (zile_fnuass). rd.104a.
- **D_16a = D_14a + D_15a** (rd.105a, FORMULA VERBATIM). D_16a<=NZL.
Semantica: zilele-prestatii = exact ce statea in D_14/D_15 (structura veche). D_14/D_15/D_16 devin "din care zile
platite" (reguli S103a/S104a: D_14<=D_14a, D_15<=D_15a); aplicatia n-are distinctie platit-vs-prestatii pe zile CM
=> egale (data-consistent, NU formula dedusa). Emise GATED pe (an,luna)>=(2026,7) - lunile < 07/2026 pastreaza
structura veche (altfel DUK respinge structura anterioara). Fix: core/d112.py, ramura CM asiguratD (`_da`, gate
`if (an, luna) >= (2026, 7)`). Gard: core/test_d112.py::test_d112_zile_prestatii_072026_emise_si_verbatim
(+ ...absente_inainte_072026). Mutatie (gate -> False) -> rosu. PROBA J27 (autoritatea): fara fix -> "D_14a/D_15a/
D_16a: atributul trebuie sa existe" + S103a/S104a; cu fix -> DUK stare=VALID, 0 erori (D112 07/2026 cu CM cod 01).

**RAMAN 10 (datorie rafinata - acum cu definitia verbatim extrasa, LIPSA numita exact):**
- **D_20a / D_21a** (asiguratD, N(15)) — "diferenta indemnizatie sanatate recalculata pentru CM in continuare"
  (angajator / FNUASS), OUG 89/2025. Def verbatim: rd.109.1/110.1 + p60: `D_20a(07)=dif.indemniz.recalculata(06)`,
  `D_20(07)=indemniz(07)+D_20a(07)`; non-null doar daca (D_9=01 si Data_CMI#null); null daca luna_r<07/2026.
  LIPSA: mecanismul de recalcul al indemnizatiei lunii precedente la procentul D_28 actualizat + diferenta; cere
  stocarea/citirea indemnizatiei CM pe luna anterioara. BLOCAT_FORMULA+DATE. Decizie de produs: mecanismul OUG
  89/2025 "fara declaratie rectificativa".
- **C2_155 = Σasigurat(D_20a) daca C_1<>2; null <07/2026** (angajatorC2, rd.44e) — FORMULA VERBATIM, dar operandul
  D_20a nu e calculabil inca. BLOCAT pe D_20a (a emite 0 = a afirma "niciun CM in continuare" = neverificabil).
- **C2_156 = Σasigurat(D_21a) daca C_1<>2; null <07/2026** (rd.45e) — idem, BLOCAT pe D_21a.
- **E2_156 = Σasigurat(D_21a) daca C_1=2; null <07/2026** (asiguratE2, rd.109e; someri) — idem, BLOCAT pe D_21a.
- **B3_7D** (asiguratB3, rd.8.1, N(15)) — "din care, diferenta de indemnizatie CASS aferenta lunii anterioare".
  LIPSA: structura NU da formula (doar antetul); legat de baza CASS a diferentei D_20a/D_21a. BLOCAT_FORMULA.
- **C_10D** (asiguratC, rd.11.0, N(15)) — "din care, diferenta de indemnizatie CASS aferenta lunii anterioare".
  LIPSA: structura NU da formula (doar antetul). BLOCAT_FORMULA.
- **D_9a** (asiguratD, N(1)) — "=1 pentru CM acordate pacientilor inclusi in programe nationale de sanatate".
  Semantica VERBATIM. LIPSA: aplicatia n-are marcaj "program national" pe certificatul de CM. BLOCAT_DATE (camp
  nou pe certificat, ecran Concedii medicale). Absent = corect pentru firme fara asemenea CM.
- **D_9b** (asiguratD, N(1)) — "=1 pentru diminuarea cu 1 zi lucratoare a CM cf OUG 91/2025" (+ Legea 64/2026;
  exceptii verbatim p2: D_9 in 08/15/51/17, D_9a=1, D_10=2, CM in continuare). Semantica VERBATIM. LIPSA: regula
  de diminuare cu 1 zi lucratoare a CM nu e implementata (schimba zilele/indemnizatia CM). BLOCAT_REGULA + decizie
  de produs (afecteaza calculul CM, nu doar declaratia).
- **E3_97** (asiguratE3, rd.8.5.6, N(15)) — "Contributii la fond de pensii ocupational (Legea 1/2020), neimpozabil,
  art.76 alin.(4^1)"; regula E3_90>=...+E3_97. Semantica VERBATIM. LIPSA: aplicatia n-are date de pensii
  ocupationale in salarizare. BLOCAT_DATE (camp nou de salarizare). Absent/0 = corect pentru firme fara pensii ocup.

Toate 10 sunt CONDITIONALE (CM in continuare D_9=01 / program national / pensii ocupationale / diminuare OUG 91) -
firma tipica fara aceste cazuri e VALIDA cu doar D_14a/D_15a/D_16a (probat: DUK VALID pe CM cod 01 fara ele).

## 09.08.2026 (tura 3) — Datorie inchisa: publicarea se oprea la disc (deploy+restart neautomate)

INCHISA (regula de proces, nu gard mecanic): sub-blocajul "detectorul running==HEAD semnala divergenta dar nimeni
n-o repara" (DECIZII 08.08). Cauza: deploy+restart depindeau de memoria celui care compunea comanda -> productia
ramanea in urma (running 6589873 vs HEAD f20ee85 la aceasta tura). Reparat prin CLAUDE.md §2.3 pct.10 (patru pasi
automati dupa poarta verde; four-way running==HEAD) + §2.2 sect.11 extins la four-way. Push-ul era deja cablat
(post-commit, three-way); restartul ramane pas de executor - stop point uman pe comportament vizibil, nu se
cableaza orb. Neguardabil mecanic (vezi TESTE 09.08 tura 3); confirmarea = four-way in raport.

## 09.08.2026 (tura 4) — OUG 91/2025 diminuare CM: nucleul CONFORM; 5 divergente listate (NEatinse - luni inchise/ambiguu)

**CORPUS (adus, sursa oficiala legislatie.just.ro):** anaf_surse/oug_91_2025.html (MO 1223/31.12.2025),
lege_64_2026.html (MO 416/15.05.2026, aproba OUG 91), ordin_506_1030_2026_norme_oug158.html (MO 507/19.06.2026,
normele - modifica art.78^4 din Ordinul 15/2018/1311/2017).

**NUCLEU CONFORM (verificat verbatim, gardat - test_cm_episod.py):** aplicatia implementa DEJA regula si
COINCIDE cu textul pe aspectele CLARE: (a) diminuare = NZLCM-1 = o ZI LUCRATOARE (Ordin 506 art.78^4(4), inclusiv
exemplul numeric 442 lei reprodus de gard); (b) o singura zi/episod indiferent de nr. certificate (Legea 64
alin.1^1); (c) fereastra certificate 01.02.2026-31.12.2027 (OUG 91 art.II(1)); (d) exceptii art.2(1) lit c)=08,
d^1)=17, e)=15 (+09 lit d) NEexceptat); (e) angajator zilele 2-6 (5 zile), FNUASS din ziua 7; (f) ziua diminuata
constituie stagiu de asigurare (OUG 91 art.II(2)) - app nu reduce niciun stagiu, doar zilele platite.

**DIVERGENTE / AMBIGUITATI (NEatinse - fiecare afecteaza LUNI INCHISE si/sau e ambiguu; decizie Costin):**
1. **cod 51 (izolare) - CONFLICT norma vs ANAF.** App il EXCEPTA de la diminuare. Ordin 506 alin.(2^1)/(2^2) NU
   listeaza izolarea (nu e art.2(1) lit c/d^1/e, nu programe nationale, nu spitalizare); OUG 91 art.II(1) lit a)
   mentioneaza izolarea DOAR la suportare (trece pe FNUASS), NU la diminuare. DAR structura ANAF D112
   (structura_D112_0726_030826.pdf p.2) listeaza D_9=51 ca EXCEPTAT de la diminuare. Norma spune "se diminueaza",
   ANAF spune "nu". Impact: overpay pe CM izolare daca norma prevaleaza. DECIZIE (nu aleg interpretarea).
2. **faza excepatiilor 01.06.2026.** Legea 64 art.VI(4): exceptiile art.II alin.(4)/(5) (08/15/17 + programe
   nationale + spitalizare) se aplica "incepand cu data de 1 a lunii urmatoare intrarii in vigoare a legii de
   aprobare" = 01.06.2026. App aplica lista completa de exceptii din 01.02.2026. Deci pt certificate 02-05.2026,
   textul ar cere diminuarea si a codurilor 08/15/17 (exceptia lor incepe abia 01.06.2026), iar app NU le
   diminueaza. Impact: underpay evitat gresit pe 02-05.2026 (LUNI INCHISE). DECIZIE + interpretare.
3. **programe nationale pe coduri regulate.** Ordin 506 alin.(6): pacientii din programe nationale ALTII decat
   art.13(3) lit a)-c) au cuantum per art.17(1) (deci coduri regulate 01 etc.), dar sunt EXCEPTATI (alin.2^1
   "bolnavilor inclusi in programele nationale"). App excepta doar codurile 12/13/14 -> un pacient de program
   national pe cod 01 e diminuat gresit (underpay). BLOCAT_DATE: aplicatia n-are marcaj "program national" pe
   certificat = aceeasi datorie ca D_9a din D112 (vezi 09.08 tura 1). Se leaga de [[d112 13 campuri]].
4. **data de gating: data_inceput vs data eliberarii.** OUG 91 art.II(1): "certificatele ELIBERATE in perioada".
   App gateaza fereastra + varianta de calcul pe `data_inceput` (inceputul CM, salariati_api.py:366), nu pe
   `data_acordare` (data eliberarii). Diferenta apare doar la FRONTIERELE ferestrei (ian/feb 2026, dec 2027/ian
   2028). Text clar ("eliberate"), dar schimbarea muta calculul pe luni inchise. DECIZIE (schimb gating-ul?).
5. **cod 02 (accident) - nomenclator neconfirmat.** App excepta 02/03/04 ca "accidente". 03/04 (accident de
   munca/boala profesionala) = Legea 346/2002, NU OUG 158 (art.2(1) lit b exclude) -> exceptare inofensiva. 02:
   daca = accident IN AFARA muncii, e sub OUG 158 art.2(1) lit a) -> AR TREBUI diminuat -> exceptare gresita
   (overpay). LIPSA: nomenclatorul OFICIAL cod-indemnizatie->tip (Nomenclator D_9), de confirmat verbatim.

Toate 5 sunt NEatinse: 1/2/4 schimba sume pe luni INCHISE (02-08.2026) -> stop point "raportezi inainte de a
atinge"; 1 e ambiguu (norma vs ANAF); 3 e BLOCAT_DATE; 5 cere nomenclatorul verbatim. Niciun cod de calcul atins.

## 09.08.2026 (tura 5) — CM OUG 91/2025: 4 divergente REZOLVATE in calcul; cod 02 + programe nationale raman

Reparat in salarizare.py (_calcul_cm_core + variante) + salariati_api.py (gating), fara a atinge alte generatoare:
- **Izolare 51: se DIMINUEAZA** (scos din exceptii). Norma (Ordin 506) prevaleaza asupra D112. J27: nicio regula
  impotriva reducerii; golul agregat C2 pentru randul 51 (generator D112) - de verificat la o declaratie reala
  cu 51 (neatins, constrangere "nu atingi generatoarele").
- **Exceptii de la 01.06.2026** (Legea 64 art.VI(4)): varianta 2026-02-01 (diminuare fara exceptii) + 2026-06-01
  (cu exceptii). 08/15/17 + spitalizare + programe nationale 12/13/14 se diminueaza in 02-05.2026.
- **Gating pe data eliberarii** (data_acordare), nu data_inceput (OUG 91 art.II(1) "eliberate").
- Garduri: core/test_cm_episod.py (izolare 51, faza 01.06.2026, cod 02/03/04 nediminuate, gating pe eliberare).

**RAMAN datorie:**
- **cod 02/03/04 (accident neconfirmat):** nediminuate pana la confirmare verbatim ca sunt indemnizatii OUG 158
  supuse diminuarii OUG 91. LIPSA: Legea 346/2002 (nu e in corpus) + afirmatie verbatim pe accidentele
  neconfirmate. Nomenclator 9 le pune in G1 (incapacitate), dar asimilarea la Legea 346 e nerezolvata.
- **programe nationale pe coduri regulate (01 etc.):** app excepta doar 12/13/14; restul cere marcaj pe certificat
  (~D_9a din D112, [[d112 13 campuri]]). BLOCAT_DATE, AMANAT (decizie de produs).
- **luni depuse afectate:** NICIUNA acum (tenant_001: 0 confirmate; singurul cert schimbat = id=46 05/2026, +202
  lei diferenta, nedepus). La aparitia unor luni depuse afectate -> recalcul efectiv = a doua comanda (nu se
  atinge o luna depusa fara aprobare).

## 09.08.2026 (tura 6) — Corpus pasul 3: 7 acte aduse, 4 COTE la MO; REDARE ramase + acte structurale listate

COTE MO+local: 19 -> 23 (4 ridicate: dividend 8%, plafon TVA incasare 4.5M, sold casa 50k, avans 5k).
Acte noi in corpus (7): legea_346_2002, oug_115_2023, legea_296_2020, legea_70_2015, og_16_2022, legea_136_2020,
oug_34_2024 (toate _consolidat.html, forma "(A)"). INDEX.json regenerat (gen_index TIP_FORMA += 4 forma_la_data).

RAMAS REDARE (nu inchis, cu motiv):
- facilitate_salariu_minim 300 @2025: OUG 115/2023 (citat) NU confirma 300 -> stop point; candidat OUG 156/2024.
- Legea 227/2015 valori istorice (tva 19%@2017, dividend 5%@2016, mijloc fix 2.500@2015): consolidatul nu le
  contine -> forma-la-data (CF baza 08.09.2015, just.ro/171282).
- tva_redusa_5 @2025: abrogare confirmata (L141 pct.43), dar destinatia fostelor 5% = de decis.

ACTE CITATE IN COD FARA FISIER LOCAL, dar NU temeiuri-COTE (clasa diferita de pct.5; NEaduse, listate):
- structuri de declaratie (OPANAF 705/2020, 102/2025, 206/2025, 592/2016, 2194/2025, 407/2025, 1783/2021,
  3769/2015, 394/2017, 146/2018, 779/2024, 174/2026 etc.): STRUCTURA e capturata in fisierele d*_struct_anaf.txt;
  textul ordinului in sine nu e adus.
- contextuale (nu backeaza o valoare fiscala calculata): OMFP 1802/2014 + 3103/2017 (contabilitate), Legea
  53/2003 (Cod muncii), Legea 31/1990 (societati), Legea 207/2015 (Cod proc fiscala), HG 423/2020 (nomenclator
  cod urgenta), OUG 96/2003 (risc maternal - referita in OUG 158 art.2 lit.e, deja local), Legea 399/2006
  (aproba OUG 158, inglobata in consolidat), acte de aprobare/modificare inglobate in formele consolidate prezente.
Motiv (chestionar pct.4): lista pct.5 (temeiuri-COTE) e SCURTA si inchisa; restul sunt structura/context, alta clasa.

## 09.08.2026 (tura 7) — 4 pozitii corpus: 3 inchise (MO), 1 propunere; +3 acte, COTE MO+local ->33

Corectat (REDARE->MO, valori neschimbate, doar temei/nivel_sursa; INDEX regenerat; G1 gardeaza, mutatie probata):
- facilitate_salariu_minim 300 @2025 -> OUG 156/2024 art.LXVI (era OUG 115/2023, care NU continea valoarea).
- tva_redusa_5 @2025 -> Legea 141/2025 pct.42 (art.291 alin.2 g carti + h cultural = 11%); locuinte sociale -> 21%.
- tva_standard 19% @2017 -> CF forma initiala 2015 (art.291 alin.1 lit.b).
- impozit_dividend 5% @2016 -> OUG 50/2015 art.97 alin.8 (temei corectat de la Legea 227/2015).
- plafon_mijloc_fix 2.500 @2015 -> HG 276/2013 (temei corectat de la Legea 227/2015).
Acte noi in corpus (3): cf_2015_forma_initiala.html, oug_50_2015_consolidat.html, hg_276_2013.html.
G3 set volatil-fara-MO -> [] (tva_redusa_5 era ultimul; toate legate).

RAMAS (propunere / deschis):
- cod 02/03/04 diminuare: PROPUNERE = se diminueaza (G1/OUG 158 cat timp neconfirmat); actul primar (Legea
  346/2002) defera la Legea 319/2006 (ABSENTA) -> de adus pt confirmare primara daca Costin accepta propunerea.
  Neatins codul de calcul.

## 09.08.2026 (tura 8) — Cod 02/03/04 diminuare: datorie INCHISA; Legea 319/2006 in corpus

Propunerea din tura 7 aplicata: cod 02/03/04 ("accident neconfirmat", G1/OUG 158) SE DIMINUEAZA ca orice cod G1.
Temei complet acum: Legea 319/2006 art.5 lit.g) (accident de munca + accidentul de traseu) adusa in corpus
(legea_319_2006_consolidat.html), coroborata cu Nomenclator 9/10 + OUG 91/Ordin 506. Scos
_CM_COD_ACCIDENT_NECONFIRMAT din salarizare.py. Gard test_cod_02_03_04_se_diminueaza (diminuare=1). Golul primar
(Legea 319/2006 absenta) = INCHIS. Nicio pozitie CM ramasa deschisa pe diminuare.

## 09.08.2026 (tura 9) — D_9a: datorie pe date INCHISA (marcaj program national, date->ecran->D112)

Din cele 13 campuri D112 v1.03-072026: D_9a (blocat pe DATE inexistente) INCHIS. Construit: coloana
concedii_medicale.program_national (migrare + template), checkbox .set-bifa in flux_concediu.js, persistenta in
salveaza_concediu, emisie D_9a="1" in asiguratD (>=07/2026, J27 valid), exceptare de la diminuare (fazat 01.06).
Gapul "programe nationale pe coduri regulate" (tura 4/7) inchis. Garduri: test_migrare_program_national_cm,
test_program_national_exceptat_de_la_diminuare, test_d112_d9a_program_national_emis. RAMAS pe date: E3_97 (pensii
ocupationale in salarizare) - urmatorul slice.

## 09.08.2026 (tura 10) — E3_97: mecanismul plafonului 400 EUR NEreglementat verbatim (curs+excedent) -> ramane pe decizie

Cautat la sursa (CF art.76 alin.(4^1)/(4^2)/(4), art.78(2)(a), HG 1/2016 norme - adus in corpus, OUG 8/2026):
- CUMUL reglementat (400 EUR anual/persoana; ocupationale de la 01.03.2026, OUG 8/2026 art.10(10)).
- CURS: neatasat lui art.76(4^1); doi candidati (art.76(4) "valabil pentru datele respective" / art.78(2)(a)
  "ultima zi a lunii"). EXCEDENT: doar implicit, neexplicit.
Aplicatia nu trateaza niciun plafon EUR de salariu, nici plafonul 33% din (4^1) -> niciun analog. E3_97 EMISIE
BLOCATA pe curs+excedent neconfirmate + metoda de colectare (decizie Costin). Datele existente NEatinse.
Act nou in corpus: hg_1_2016_norme_cod_fiscal.html (normele metodologice CF; confirma ca NU acopera pensiile ocupationale).

## 09.08.2026 (tura 11) — E3_97: curs+cumul reglementate verbatim (corectie tura 10); oprit pe subsistemul art.76(4^1)

Curs CONFIRMAT: art.78(2)(a) (curs leu/euro BNR, ultima zi a lunii) + OUG 8/2026 art.10(9) (verificarea anuala in
euro pt art.76(4^1) pct.29/e). Cumul: anual in euro, ocupationale de la 01.03.2026 (art.10(10)). Excedent: implicit
-> impozabil (alegere Costin). curs_bnr.py reutilizabil pt conversie. STOP POINT #2: constructia CORECTA a E3_97
cere subsistemul art.76(4^1) (plafon lunar 33% pe suma a-j + ordine art.76(4^2) + excedent), care lipseste complet
din app; 33% poate musca la plata lumpy pe salariu mic. Neconstruit; decizie de scope (E3_97 izolat cu 33% pe sine
vs subsistem complet). Metoda B fixata (app aplica plafonul, contabilul introduce brutul). Datele NEatinse.

## 09.08.2026 (tura 12) — Gard gaura de metoda pe proba de login + 4 conturi test pe roluri

Gard: core/test_login_proba_metoda.py - "probat" = auth_api.login (calea /auth/login), nu verifica_parola pe hash;
demonstreaza divergenta hash-ok vs login-esec pe cont inactiv (activ=false). Constrangere chk_firm_required
(angajat/client cer accounting_firm_id) - respectata (asistent+client pe firma 1968). Conturi test pe cele 4
roluri (admin@/patron@/asistent@/client@ prisma-cont.test), probate real (HTTP 200 + token); contul real (id=1)
neatins; parolele doar in raport, nu in registre.

## 09.08.2026 (tura 13) — Gard izolare pe CHEIE API (punct orb al gardului structural)

Gard: core/test_izolare_api_key.py. Gardul structural (test_izolare_structurala) probeaza rutele {tenant_id}
cu token Bearer; rutele /api/v1/firme/{tenant_id}/* folosesc X-Api-Key (cere_api_key -> firm_id), deci la
Bearer raspund 401 si treceau FALS-VERDE fara a exercita vreodata izolarea pe cheie. Gardul nou enumereaza
DINAMIC rutele /api/v1/firme/{tenant_id}/* din app si probeaza cheia firmei A pe tenantul firmei B ->
niciodata 2xx, niciodata sentinela B; control pozitiv A pe A = 2xx cu date A (altfel un 404 uniform ar trece
gardul degeaba). Chokepoint acoperit: _api_schema(actx, tenant_id) = SELECT ... WHERE id=tenant AND
accounting_firm_id=cheie.firm. O ruta /api/v1 noua care uita _api_schema intra automat si PICA. Nicio regula
de acces schimbata (doar acoperire adaugata). Efemer: cheie inserata manual (fara conn.commit pe conn real,
altfel ar persista), scheme+firme sterse la teardown, 0 reziduuri verificat.

## 09.08.2026 (tura 14) — Gard cablaj end-to-end verifica_tva (cross-check D300 era mort)

Gard: core/test_control_incrucisat_wiring.py::test_verifica_tva_prinde_factura_necontabilizata_end_to_end.
Cele 61 teste din test_control_incrucisat.py exercita compara_tva (functia PURA); NICIUNUL nu chema verifica_tva()
end-to-end -> derivarea de semnatura a d300.genereaza (cere acum Perioada) a ramas nedetectata, inghitita de
`except -> gri`. Gardul cheama verifica_tva pe schema efemera cu o factura emisa necontabilizata (4427=0) si cere
stare=='rosu'. MUTATIE PROBATA: revert la _d300.genereaza(conn, schema, an, luna) -> testul PICA `- rosu + gri`;
fix restaurat -> pass. Efemer: schema stearsa + rollback, 0 reziduuri.

## 09.08.2026 (tura 16) — Doua garduri de "forma": balanta valida la import + "cu intarziere" scos din "La zi"

1. core/test_solduri_api.py::test_fisier_strain_nu_e_balanta_valida / test_balanta_goala_toate_zero_nu_e_valida /
   test_importa_refuza_fisier_strain_inainte_de_db: solduri_api.balanta_valida prinde fisier strain (cont
   ne-numeric) si balanta all-zero; verifica_echilibru zice inca "echilibrat" pe 0=0 (asertat) -> balanta_valida
   e a doua poarta. Mutatie: importa fara poarta -> verifica_echilibru trece (0=0) -> asigura_tabel(None) (nu ValueError).
2. core/test_control_fiscal.py::test_clasifica_depusa_dupa_termen_iese_din_la_zi: depusa 20.07 vs termen 25.02 ->
   cu_intarziere, confirmate gol, lipsa gol (nu restanta). Mutatie: fara cosul separat -> cadea in confirmate (La zi).
