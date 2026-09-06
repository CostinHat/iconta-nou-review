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

## 09.08.2026 (tura 17) — Gard ingust: mesajele balanta_valida au diacritice (NU gard de clasa)
core/test_solduri_api.py::test_mesajele_balanta_valida_au_diacritice: fiecare motiv de eroare user-facing are
macar o diacritica RO. Mutatie: mesaj rescris fara diacritice -> pica. NU e gard de clasa pe diacritice (ar da
fals-pozitive pe .py: docstring/comentarii/scripturi migrare/SQL/termeni tehnici/citate legale) - vezi DECIZII.
Regula "diacritice" din verificator ramane frontend-only (.js) prin design.

## 09.08.2026 (tura 19) — Gard izolare pe /raportari (aparare de date, nu doar ruta)
core/test_izolare_raportari.py: sesiune HTTP reala cabinet A -> fir/citit al cabinetului B -> 404 (data-layer
refuza); control pozitiv: autorul isi vede firul (200). MUTATIE PROBATA pe cod vechi (firul_complet nefiltrat +
/citit fara check): test_fir_alt_cabinet_da_404_nu_403 -> 403 (pica), test_citit_alt_cabinet_da_404 -> 200 (pica);
dupa fix -> 3 passed. Efemer (firme/useri/raportare pe conn din pool, get_conn monkeypatch cu SAVEPOINT), rollback.

## 10.08.2026 (tura 20) — Gard browser (Playwright) pe antetul wizardurilor + capacitate noua
Capacitate: Playwright+Chromium pe server (venv, ~/.cache 656M), auth prin token in sessionStorage (creds
~/.iconta/fe_test.env, 600, in afara git), doar cabinet 4163. Gard: frontend_test/proba_wizard_antet.py -
navigheaza calea reala 'Migrare cabinet' > Solduri > (back) > Salariati si aserteaza: back revine la 'Migrare
cabinet' + antetul nu acumuleaza. MUTATIE PROBATA: cod vechi exit 1 (back ramane pe strat; 'Solduri' se acumuleaza
in fir), cod nou exit 0. NU in poarta verde (nume non-test_ -> pytest nu-l colecteaza).
Ruleaza: venv/bin/python3 frontend_test/proba_wizard_antet.py

## 10.08.2026 (tura 22) — Gard ZERO-BASE D100/D300 (avertisment pe zero-suspect)
core/test_zero_base_declaratii.py: firma cu factura emisa necontabilizata -> D100 pe zero EMITE avertisment;
D300 pe zero (TVA la incasare nedecontata) cu facturi EMITE avertisment; control negativ (fara facturi = nil
legal) -> FARA avertisment. MUTATIE PROBATA: cod vechi -> D100 avertismente=[] (pica); cod nou -> 1 passed.
Non-blocant (nu blocheaza generarea/depunerea). Efemer, drop+rollback.

## 10.08.2026 (tura 23) — Gard: D100 pe zero refuzat (nu XML invalid) + DUK-validare
core/test_zero_base_declaratii.py (rescris): D100 pe zero (cu SAU fara facturi) -> ValueError 'nu se depune pe
zero'; D300 pe zero cu facturi -> avertisment; D300 nil fara facturi -> fara avertisment. MUTATIE: cod vechi
(avertisment D100, XML invalid) -> test_d100 NU ridica -> PICA; cod nou -> 3 passed. Unealta DUK re-validare:
frontend_test/valideaza_duk.py (necomis).

## 10.08.2026 (tura 24) — 4 garzi: declaratii refacute la spec oficial (DUK-dovedit)
- core/test_d394_codpr_cereale.py::test_op11_cereale_coarse_nu_emite_centralizatorul_21 /
  ::test_op11_cereale_cu_subcod_NC_emite_codPR_valid / ::test_codpr_N_din_categorie_recunoaste_subcod_NC
  (seam pur calcul_d394, fara DB). MUTATIE pe HEAD pre-fix: coarse 'cereale' -> op11 codPR=['21'] (pica
  assert "21" not in), subcod '1005' -> op11=[] (pica assert "1005" in); cod nou 3 passed. Suita d394 97 passed.
- core/test_d301_data_doc.py::test_data_doc_iso_normalizat / ::test_data_doc_date_obiect_normalizat /
  ::test_data_doc_deja_canonic_pastrat: ISO/obiect date -> ZZ.LL.AAAA; canonic pastrat. MUTATIE: cod vechi
  2 failed (ISO+date), cod nou 11 passed (fara regresie d301_rollup).
- core/test_d406_supplierid.py::test_supplierid_pf_fara_cui_nu_e_zero: factura de la PF fara CUI -> SupplierID
  != "0" si = 04+cod (fixture schema efemera, rollback). MUTATIE: cod vechi SupplierID="0" (pica), cod nou pass.
- core/test_pull_declaratii.py::test_d112_cm_suma_lipsa_din_stocare_recalc_din_media: cert CM cod 01, 5 zile,
  brut_ang=brut_fnuass=0 -> B3_7>0, B3_7=B3_12+B3_13, DUK valid. MUTATIE: cod vechi B3_7="0" (pica assert 0>0),
  cod nou pass. Suita d112 82 passed.
Proba obiectiva comuna: DUKIntegrator pe arborele combinat, 4 firme (frontend_test/valideaza_duk.py, PYTHONPATH=$PWD):
D112/D301/D406 VALID; D394 eroarea codPR "21" DISPARUTA (ramane R233.6=date, vezi DECIZII).

## 10.08.2026 (tura 25) — 9 garzi: toate declaratiile confruntate cu sursa oficiala (DUK-dovedit)
Toate cu MUTATIE pe HEAD c9869a1 (pre-fix) + re-validare DUKIntegrator pe date POPULATE.
- core/test_d100_scadenta_trimiv.py::test_micro_121_trim_IV_scadenta_25_06_an_urmator /
  ::test_profit_103_trim_IV_scadenta_25_LS / ::test_trim_III_neschimbat: micro 121 trim IV -> 25.06.an+1,
  profit 103 luna12 -> 25.12.an. MUTATIE: cod vechi 25.01.an+1 (pica); DUK before micro trim IV = erori R15.1.
- core/test_d101_nr_evid_poz12.py: nr_evid poz.1-2 = "11" (+ structura poz.3-5/6-7 + ancora exemplul ANAF).
  MUTATIE: cod vechi "10" -> assert '10'=='11' pica (2 failed/1 passed -> 3 passed).
- core/test_d205_cifr_obligatoriu.py::test_cifR_gol_refuzat_nu_emis_invalid / ::test_den1_gol_refuzat /
  ::test_beneficiar_valid_nu_e_afectat: cifR/den1 gol -> ValueError. MUTATIE: cod vechi NU ridica (emitea XML
  invalid). DUK before (CNP anulat): "cifR: atribut prezent dar vid nepermis".
- core/test_d300_drop_taxabil.py (4 teste): linie 19% taxabila aruncata -> avertisment CUANTIFICAT ("TVA 190
  lei"), fara "pune-le manual la randurile potrivite", liniile 0% separate. MUTATIE: cod vechi 4 failed.
- core/test_d390_rotunjire_coerenta.py (3 teste): rezumat["L"] == suma operatie(baza tip L) == 2002. MUTATIE:
  cod vechi bazaL=2001 != 2002 (pica); DUK before = erori R16.
- core/test_d394_v_taxare_inversa_cota0.py: V -> cota 0 (nrLivV/bazaLivV doar la cota 0). MUTATIE: cod vechi
  cheia V purta cota 21 (pica); DUK before = erori R217.2/R68.2/R69.2/R35/R77-79.
- core/test_d394_pull_ti_fara_linii.py: pull() pe taxare-inversa fara linii -> cota == cota_standard. MUTATIE:
  cod vechi NameError 'an' la d394.py:831 (crash latent).
- core/test_d406_payment_method.py (3 teste): PaymentMethod in {01,02,03,98,99}; "VIR"->03; "numerar"->01.
  MUTATIE: cod vechi emitea 'VIR'/'numerar' (pica); DUK before (sectiune Payments) = erori "valoarea 'VIR' nu
  se afla in lista".
- core/test_d112_carantina_c2.py: cod 07 carantina -> C2_213=3, C2_215=714, C2_212=C2_213+C2_214. MUTATIE:
  cod vechi C2_213 OMIS (pica); DUK before = erori A49c/A43d.2/A49e.

## 10.08.2026 (tura 26) — 10 garzi: reparate deciziile §6 (Costin). Toate MUTATIE pe HEAD 6cd0054 + DUK populat.
- core/test_d112_asiguratd_zerobase.py: D_1/D_2/D_5/D_6/D_7 gol -> ValueError (numeste salariatul). MUTATIE: HEAD
  5 failed (nu ridica, emitea gol); dupa fix 6 passed. + cele 4 fixtures din test_pull_declaratii.py reparate
  (serie/numar/date realiste) - suita d112 verde cu refuzul activ.
- core/test_d205_divid_platit.py: divid_D=distribuit(credit457), divid_P=platit(debit457). MUTATIE: HEAD divid_P=0.
- core/test_d205_rezid_derivat.py: nerezident dividende (CNP prima cifra 9) -> ValueError (DUK regula R32/R33).
  MUTATIE: HEAD nu ridica (emitea Rezid="1").
- core/test_d300_taxare_inversa_beneficiar.py: achizitie taxare inversa -> R12_1/R12_2 + R25_1/R25_2 net-zero +
  gard anti-dubla-numarare. MUTATIE: HEAD chei absente (aruncata tacit).
- core/test_d300_zero_rate.py: achizitie 0% -> R26_1; livrare 0% -> avertisment per-linie cu suma. MUTATIE: HEAD
  6/8 failed (fara R26_1, agregat).
- core/test_d301_pers_inreg.py: inreg_art317=True -> pers_inreg "2". MUTATIE: HEAD "1" (ramura moarta).
- core/test_d394_manual_codpr.py: manual C(deseuri->22)/V(cereale 1005) -> op11 emis. MUTATIE: HEAD op11 gol.
- core/test_d394_prsafiliat.py: are_operatiuni_afiliate=True -> prsAfiliat "1". MUTATIE: HEAD mereu "0".
- core/test_d406_taxcode_nota.py: GL/Payment TaxCode = 380304 (nu "300"). MUTATIE: HEAD "300".
- core/test_d406_master_pf.py: PF tip-04 in <Suppliers>/<Customers>. MUTATIE: HEAD blocuri goale.

## 10.08.2026 (tura 29) — LANT legislatie TURA 3/4: garzi pe mesajul exact pre-DUK (identitate + coercitii + wiring)
Toate MUTATIE pe HEAD 8b74ccb + baseline DUK-valid nemodificat. FUNDATIE: core/test_identitate.py (valideaza_cui/
cnp/cif ancorat pe valori DUK valid+invalid). Per declaratie (fisiere noi de gard, old-fail/new-pass):
- D100: test_d100_cui_checksum, test_d100_trunchiere.
- D101: test_d101_cui_checksum, test_d101_cod_obligatie_caen, test_d101_valori_pre_duk (P-uri/plafoane V).
- D112: test_d112_cnp_angajat, test_d112_nume_dataang, test_d112_caen_codboala, test_d112_cert_overflow.
- D205: test_d205_cnp_checksum, test_d205_cui_checksum, test_d205_cnp_duplicat (R29/R41b pre-DUK).
- D300: test_d300_valideaza_wired (T2 tip_decont↔luna R18 + marja), test_d300_profil_identitate.
- D301: test_d301_valideaza_wired, test_d301_cif_checksum, test_d301_an_guard, test_d301_nr_doc_c20, test_d301_coercitie_tacita.
- D390: test_d390_diagnostic_partener (checksum_vies DE/HR/FR + tara mistypata + codO>12 + wiring).
- D394: test_d394_partener_cui_litere (G-d1 blocaj), test_d394_cuip_checksum, test_d394_op1_fara_op11 (R233.5 exclus).
- D406: test_d406_cui_checksum, test_d406_cnp_tert (03+CNP DUK-valid), test_d406_coercitie_t3, test_d406_accounttype_wired.
- D710: test_d710_t9_parsare, test_d710_t1_cui, test_d710_nomenclator_manual, test_d710_cod131_132, test_d710_sume_negative.
Fixtures reparate (date invalide inlocuite cu valide, gardurile NEslabite): test_d112_reconciliere, test_d205_reconciliere,
test_d205 (test_id_inreg), test_d710 (test_cod_bugetar - bumpuit √).

## 10.08.2026 (tura 30) — LANT legislatie TURA 4/4: reconciliere + meta-gard anti-mort
- core/test_reconciliere_vie.py: META-GARD - fiecare din 9 dXXX_reconciliere exista + cablat in genereaza (AST,
  orice stil) + non-tautologic (nu importa generatorul) + are test de firing. Prinde mecanic clasa "D300 mort"
  (necablat/tautologizat/sters). MUTATIE: modul inexistent d999 semnalat.
- core/test_d100_reconciliere.py / test_d301_reconciliere.py / test_d390_reconciliere.py: reconcilieri gen-gate NOI,
  non-tautologie (AST) + ANTI-MORT (injectie divergenta ROLLBACK -> verifica_reconciliere RIDICA numind ambele valori)
  + baseline DUK-valid. D301 include semanticul T7 (RON curs=5 -> genereaza ridica baza1 gen=5000 vs cale2=1000).
- core/test_d205_imp_manual.py: beneficiar manual imp1≠rate×baza -> ridica (d1; before: tacit+DUK-valid).
- core/test_d300_r25_r12.py: R12 fara oglinda R25 -> ridica DUK regula V19/V20 (CR-5; before: DUK-valid supra-declarat).
- core/test_d710_suma_ded.py: suma_ded nu mai e aruncat (121 aplicat max(dat-ded,0)+emis; 103 blocat R14-21).
- core/test_control_reconciliere_vizibila.py: reconciliaza_declaratii vizibil in Control fiscal, ACELASI mecanism;
  divergenta -> ROSU numind ambele valori; apel rupt -> ROSU "VERIFICARE INTRERUPTA" (NU gri tacit); verde cand reconciliaza.


## 10.08.2026 — Lot 0: datorii ramase (nereparate)
- **F176 Descriere** cita F160 (ELIMINAT, e-Factura pt cont gratuit) in "e-Factura/e-Transport (F126/F160/F121) ... cinci pozitii un singur auth". Lasat: scoaterea lui F160 cere re-verificarea numaratorii "cinci pozitii" (nu doar stergerea ID-ului). Harm mic (ID intern, nu claim de feature user-facing servit ca disponibil). De reincadrat cand se atinge F176 (Lot 1 transversal - F176 e conectorul OAuth SPV/ANAF).
- **3 comentarii cod stale** referind conceptul "gratuit" ELIMINAT 26.07: static/js/ecrane/login.js:418 ("// null in modul gratuit"), main.py:2728 + :2786 ("acces client+gratuit+cabinet"). Cosmetic - comentarii, NU registru, deci nu feed AI-ul. De curatat oportunist la atingerea fisierelor.
- **F035/F036/F037 D406 PARTIAL**: registru EXACT (marcat corect PARTIAL/nedepunabil), dar familia D406 ramane NEDEPUNABILA (SourceDocuments = linie sintetica per factura in loc de factura_linii reale + Payments gol). Reparatia = feature mare (liniile reale + sectiunea Payments) -> decizie de scope, in afara Lot 0.

## 10.08.2026 — Lot 1: datorii/goluri
- **F116 headere de securitate NEDEPLOYATE** (HSTS/X-Frame/X-Content/Referrer): gol real de securitate; decizie infra Costin. nginx server config in afara git.
- **Test-debt migrari** (F007/F053/F059/F079/F084/F085/F150): cablate dar fara proba functionala adanca (fara pytest). De acoperit cu smoke pe cabinet 4163.
- **F124 "Testare pilot P1-P5"**: campanie de test finalizata, NU feature de cod; Sursa cod "DE_FACUT sectiunea 1" stale/contradictoriu-cu-LIVE. De reincadrat (milestone) sau clarificat.
- **F035/F036/F037 D406 PARTIAL** (mostenit Lot 0).

## 11.08.2026 — Lot 2+3: goluri/datorii
- Test-debt Lot 2: F017 (chitante)/F018 (parteneri)/F045 (generare PDF)/F048 (profil+model) - cablate, fara test dedicat.
- Test-debt Lot 3: F118 (blocare perioade)/F054 (editor note)/F145 (rapoarte config) - cablate, fara test dedicat.
- Fixul CONCURENTA a corectat Sursa cod si pentru F138-142 (Lot 4 Stocuri) + F146/F147 (Lot 8 Cabinet); verificarea FUNCTIONALA a acestora ramane la lotul lor.

## 11.08.2026 — Campanie verifica-201 COMPLETA: datorii ramase (cumulat)
- **F116 headere de securitate NEDEPLOYATE** - DECIZIE INFRA Costin (singura decizie deschisa). Snippet gata.
- **Test-debt** (cablate, fara test dedicat): migrari (F007/F053/F059/F079/F084/F085/F150/F151), F017/F018/F045-gen/F048, F118/F054/F145, F075. Cablate + rute live, dar fara pytest dedicat.
- **F124 "Testare pilot P1-P5"**: proces finalizat, NU feature; Sursa cod "DE_FACUT sectiunea 1" stale. De reincadrat/scos de Costin.
- **F035/F036/F037 D406 PARTIAL**: familia nedepunabila (SourceDocuments sintetic + Payments gol). Scope Costin.
- **Limita gard**: proza-Sursa-cod fara path-token nu e mecanizata (fals-pozitiv pe infra F116/F113/F170) - ramane judecata.

## 11.08.2026 — Ajutor contextual: datorii/limite
- CSV `ajutor` e citit la runtime de core/ajutor.py cu CACHE la pornire -> orice modificare de TEXT ajutor cere `sudo systemctl restart iconta-nou` ca sa se serveasca. Plasarile "?" (JS static) NU cer restart (servite de pe disc). Ancora four-way: RUNNING > ultimul commit care schimba CSV/runtime, nu ultimul commit JS.
- F014 Capacitate: ajutor scris, "?" neplast INTENTIONAT (management fara continut fiscal, ecran auto-explicativ). Decizie, nu datorie.
- Fara gard mecanic ca fiecare functionalitate "cu ceva de spus" sa aiba ajutor scris/plast — ramane judecata (ca actualizarea registrelor). Endpoint-ul ARE garduri: /ajutor/{fid} in PUBLICE (test_rute_autentificate), .ajutor-btn whitelisted (verificator CLASE_BUTON_OK), coloana `ajutor` in test_registru_functionalitati (11 coloane).

## 11.08.2026 — Ajutor de ansamblu: datorii/limite
- users.bun_venit_vazut_la: migrare idempotenta (core/migrare_bun_venit.py) RULATA manual pe DB (ca reset_parola,
  cu env ~/.iconta/db.env). Backfill existenti->vazut = pas UNIC manual (NU in DDL-ul idempotent). Pe un DB nou,
  migrarea creeaza coloana (toti NULL) -> toti ar vedea welcome; daca nu se vrea retroactiv, se re-ruleaza backfill-ul.
- Fara test pytest DEDICAT pe /ansamblu si /cont/bun-venit-vazut (probate cu TestClient + browser, nu in poarta
  verde). Rutele au gard de autentificare (cere_context -> test_rute_autentificate).
- Prezentarea depinde de doua surse: front STRATURI (migrare.js) + back repartizeaza() (/ansamblu). Ambele SURSA
  UNICA a lor -> daca se schimba pasii de migrare sau repartizarea, prezentarea se actualizeaza automat (import/API).

## 11.08.2026 — Restart neconditionat: datorii/limite
- Restartul in post-commit ruleaza `sudo -n systemctl restart iconta-nou` la FIECARE commit pe main. Depinde de
  NOPASSWD in sudoers (costin: NOPASSWD ALL). Esec -> sentinela .git/RESTART_ESUAT + banner (ca push-urile), nu tacut.
- Fiecare commit pe main restarteaza serviciul (cateva secunde downtime). Acceptat: mediu single-user, invariantul
  RUNNING==HEAD prioritar (decizia Costin). Cu utilizatori activi, decizia de fereastra se ia INAINTE de commit.
- Gardul verifica NECONDITIONAREA hook-ului, NU ca restartul chiar reuseste la runtime (aia = sentinela + four-way).

## 11.08.2026 — D406 ALFA: datorii/limite descoperite
- **BUG GENERATOR (negardat, NEcomis):** core/d406.py pull() ~1123/1133 emite RegistrationNumber/CustomerID = id brut
  din clienti/furnizori (nu 00+CUI) cand nomenclatorul e POPULAT -> DUK "format invalid". Mascat pana acum de nomenclator
  gol (cale fallback corecta cu _partener_id_saft). Fix dovedit, NEcomis (raza peste ALFA: alti tenanti cu CUI invalid
  in nomenclator ar RIDICE). Blocheaza un DUK 'valid' pe ORICE tenant cu nomenclator populat. Decizie Costin (ca Payments).
- Corelatie ANUALA vs GL la amortizare: <Assets> proiecteaza la Dec, GL posteaza la zi -> difera mid-an (by-design, nu defect).
- Perioada 08/2026 deblocata pe ALFA (era blocata dintr-un test F118) - necesar pt seed/generare pe acea luna.
- Payments: DATE de trezorerie construite (casa+banca legate de facturi), dar generatorul NU le emite inca (asteapta sursa maparii).

## 11.08.2026 — D406 nomenclator id brut: INCHIS (reparat + gardat)
Datoria "BUG GENERATOR nomenclator -> id brut" (consemnata mai sus, lasata NEcomis) e INCHISA: reparat pe calea
principala (_partener_id_saft, ambele bucle), gardat (core/test_d406_partener_id_neconform, rosu/verde probat), DUK
tenant_013 'valid' FARA patch temporar. Family-check: doar D406 avea tiparul (D394/D390/e-Factura folosesc valoarea
CUI). RAMAS pe D406: sursa maparii Payments (date construite, generator neatins).

## 11.08.2026 — Registru D406 la zi: F035/F036/F037 PARTIAL 11.08 cu motiv real
Starea de record F035/F036/F037 adusa la realitatea de azi (era 27.07 "NEDEPUNABIL linie sintetica"). Deschise RAMAN,
cu motivul de azi: F035 = Payments neemis (asteapta sursa maparei); F036 = amortizare doar liniara (art.28 degresiva/
accelerata neimplementate) + fragment; F037 = fragment (nu in AuditFile lunar). Drift de registru similar: negasit pe
alte randuri.


## 15.08.2026 — D300 remediere: datorii/limite declarate
Limite ale remedierii D300 (B1-B4, HEAD c8d3947). Gard de regresie: core/test_d300_b1_rutare.py (8 teste).
- **Bunuri vs servicii IC — REZOLVAT prin sursă unică partajată D300<->D390 (15.08.2026, commit 0b132c3 + acest lot).**
  Formularea anterioară ("nu există câmp pe factură care să separe bunurile de servicii") era GREȘITĂ: problema NU era
  lipsa unui câmp. Aplicația tratează bun-vs-serviciu ca RECLASIFICARE — o proprietate a OPERAȚIUNII, nu a declarației
  (contabilul reclasifică o dată din panoul D390, în tabelul `d390_reclasificare`). Bug-ul real: D300 primise doar
  JUMĂTATE din model — implicitul de la D390 (emisă->L/R1, primită->A/R5+R18), FĂRĂ mecanismul de corecție
  (reclasificarea). Remediere: D300 și D390 CITESC AMÂNDOUĂ din aceeași sursă (`d390_reclasificare`, via
  `d390.pull_reclasificari`); reclasificarea MUTĂ operațiunea (emisă P -> R3/R3.1; primită S -> R7+R20, oglindă net
  zero), nu o adaugă peste rândul auto (reapariția auto = imposibilă). O singură scriere schimbă ambele declarații ->
  nu există a doua sursă care ar putea diverge; cele două se reconciliază (baza D300 R3_1 == baza D390 bazaP; R7_1 ==
  bazaS). Gard de reconciliere cross-declarație: core/test_d300_b1_rutare.py (test_recon_P_emisa_serviciu_d300_R3_egal_d390_bazaP,
  test_recon_S_primita_serviciu_d300_R7_egal_d390_bazaS, test_recon_sursa_unica_o_scriere_muta_ambele) + gărzile
  F125 din același fișier (test_reclas_emisa_serviciu_P_muta_R1_la_R3, test_reclas_primita_serviciu_S_muta_R5R18_la_R7R20_oglinda).
  Probat pe date reale pe firma grea (tenant_017, iulie 2026): D300 R3_1=5000/R7_1=7000 vs D390 bazaP=5000/bazaS=7000, DUK valid.
  **Limită DECLARATĂ rămasă:** T/R (triangulație / regim special agricultori) NU sunt pe axa bun-serviciu — rămân rutate
  numeric ca bunuri (R1) DAR se semnalează explicit (nu tăcere); neacoperite pe D300, raportate separat. Gard:
  test_reclas_T_emisa_ramane_bunuri_dar_semnaleaza.
- **d300_reconciliere (a-doua-cale) NU acoperă IC/export + deducerea amânată.** Reconcilierea agregă pe cotele
  21/11/9; rândurile IC (R1/R3/R5/R7), exportul (R14) și deducerea amânată a furnizorului cu TVA la încasare cad în
  AFARA agregării -> nu sunt reconciliate de a-doua-cale. Limită aliniată cu cea existentă pentru tva_la_incasare.
- **tip_operatiune='regularizare_avans' NU e ramificat de generator.** E rutat ca operațiune normală pe data
  exigibilității; regularizarea avansului se face prin LINIILE facturii (livrare - storno avans), rezultat net corect.
  Câmpul rămâne INFORMATIV (nu declanșează o ramură dedicată în generator).
- **Import non-UE (primită non-UE 0%) rămâne pe R26.** TVA vamală / deferment de import depinde de răspunsul ANAF
  (RAPORTAT SEPARAT, vezi raportul de audit / PREDARE_LANT); NEreparat în app - nu se repară aici fără decizia ANAF,
  trimite la ce e raportat separat.

## 15.08.2026 — Plimbarea lui Costin (Firma Grea): datorii inchise (?v= negardat, diacritice frontend, .msg-eroare)
Trei datorii de disciplina/render descoperite la plimbarea lui Costin, toate INCHISE cu gard sau fix + trimitere la commit.
- **Disciplina ?v= (cache-bust) era NEGARDATA -> REZOLVAT prin sistem hash-de-continut + gard (087b33a).** Tokenul
  ?v= al fiecarui asset e acum hash de CONTINUT (anti-cascada), nu contor manual; generatorul versioneaza_assets.py
  stampileaza toate referintele (117 stampilate, 86 aveau ?v= lipsa). Gardul core/test_versionare_assets.py cade daca
  un modul JS/CSS e schimbat fara re-stampilare (referinta cu token vechi = gard rosu) sau daca o referinta tinteste
  un asset inexistent. Cauza radacina a constatarii #1 (selectoarele Clasificare TVA invizibile): emitere_ecran.js
  schimbat cu ?v=6 neincrementat -> browserul servea versiunea veche din cache; acum staleness-ul e gard rosu, nu
  descoperire vizuala. Regenerare dupa orice schimbare de asset: `venv/bin/python versioneaza_assets.py --scrie`.
- **Gardul de diacritice acoperea doar Python -> EXTINS pe frontend (434efa3).** core/test_diacritice_afisate.py
  scaneaza acum si static/js/** (41 fisiere, high-precision, baseline 0); 27 siruri afisate reparate (carduri de
  meniu: „Incasari”->„Încasări”, „Operatiuni”->„Operațiuni”, „solduri si”->„solduri și” etc.). LIMITA DECLARATA ramasa: poarta zero-diacritice
  SARE sirurile care au deja cel putin o diacritica -> nu prinde un cuvant ASCII asezat langa unul diacriticizat in
  acelasi sir (false-negative deliberat, ca sa evite false-pozitive pe siruri mixte). De ridicat cand se gaseste un
  criteriu care separa ASCII-necesar-diacritice de ASCII-legitim (markup/cod) in siruri mixte.
- **.msg-eroare fara regula de curgere -> REZOLVAT (58e2aed).** Mesajele de eroare lungi primesc overflow-wrap /
  word-break -> se rup in interiorul casetei, fara overflow orizontal pe pagina (probat prin randare headless:
  scrollWidth == clientWidth pe container si pe document).

## 15.08.2026 — Gard edge crawler/SEO: www canonic 301 + HEAD ca GET (cluster "edge canonic www/HEAD (crawler)")
Gardul a fost LIVRAT în 02869c0 (middleware `_edge_canonic_head` din main.py); înregistrat aici la commitul de ancorare a bifei Inventar A — registrul rămăsese în urmă cu un commit (02869c0 a atins doar main.py + testul + PREDARE, nu și GARZI). Două cereri Costin, ambele în middleware de app (nginx trece Host la upstream, deci rezolvarea în app e versionată/testabilă):
- **#1 duplicat www/non-www (semnal SEO împărțit) -> 301 PERMANENT către forma canonică fără www, PĂSTRÂND calea+query.** `https://www.iconta.eu/...` întorcea 200 identic cu `https://iconta.eu/...` -> Google le tratează ca duplicat (contează cu 79 de ghiduri gata de indexat). Forma canonică = fără www (`_GHID_BAZA`, pe care se generează sitemap + rel=canonical). non-www rămâne 200.
- **#2 HEAD pe rutele GET -> 405 (buget crawl irosit) -> 200.** FastAPI NU adaugă HEAD la `@app.get` (spre deosebire de Starlette brut) -> Googlebot, care folosește HEAD ca să verifice dacă pagina s-a schimbat înainte de a o descărca, primea 405. Middleware: HEAD -> method=GET la rutare; uvicorn suprimă corpul pe fir; Content-Length = cât ar avea GET (RFC 7231 sect.4.3.2: HEAD identic cu GET, aceleași headere, fără corp).
- **Gard:** core/test_edge_canonic_head.py (6 teste, in-process TestClient, fără DB pe /,/ghid): HEAD 200 nu 405 + Content-Length HEAD==GET; www 301 canonic păstrând calea+query; non-www 200; redirect și pe HEAD. MUTAȚIE: scoți middleware-ul -> HEAD 405 / www 200 = roșu. Probat in-process (HEAD 200 CL 1919/26147/7885; www 301 Location corect).
- **Notă infra:** nginx are deja redirect www pe portul 80 (HTTP->HTTPS păstrând hostul), dar blocul 443 servea ambele cu 200 — de aici duplicatul; rezolvat în app.

## 15.08.2026 — Campanie rețeta D300 pe D394: nrFact multi-cotă + implicite fabricate + nrFacturi real (cluster "D394 audit")
Trei neconformități D394 găsite aplicând unghiurile D300 (temei/date reale/implicite/calcul) și reparate cu gard + probă DUK. Gard: `core/test_d394_nrfact_multicota.py` (10 teste; 3 pure, 5 DB pe `tenant_template.sql`, 1 probă DUK). Confruntat la sursă cu `anaf_surse/opanaf_2194_2025_d394.txt` (OPANAF 2194/2025, în vigoare de la 01.08.2025) + `anaf_surse/d394_struct_anaf.txt`.
- **#1 nrFact la FACTURĂ MULTI-COTĂ — supra-numărare tăcută (calcul greșit).** OPANAF 2194/2025 pct.C.5 (`opanaf_2194_2025_d394.txt:1221-1227`): „în situaţia în care în cuprinsul unei facturi ... există operaţiuni cu cote de TVA diferite, la rubrica «număr de facturi» se vor înscrie: valoarea 1 în dreptul operaţiunii cu valoarea cea mai mare a TVA şi valoarea 0 pentru restul; dacă valoarea TVA este aceeaşi ... la cota de TVA cea mai mare." COD VECHI (`d394.py` `pull()` split `pe_cota` + `calcul_d394` literal `1`): fiecare split pe_cotă primea nrFact=1 → o factură cu 2 cote raporta nrFact=2. FIX: `pull()` marchează nrFact=1 doar pe cota cu TVA max (dep. cota max la egalitate), 0 pe rest; `calcul_d394` respectă `f.get("nrFact",1)` (default 1 = backward-compat pentru apelanții cu o linie/factură). Propagă coerent în `rezumat2.nrFacturiL/A`. MUTAȚIE: factură 2-cote → total nrFact=1 (nu 2); la TVA egal (19%×100=20%×95=19) → cota 20 primește 1. Probat DUK: D394 cu nrFact=0 pe o linie op1 e valid.
- **#2 implicite FABRICATE tăcut (regula 4).** `d394.py` `build_xml`: `denR`/`functie_reprez`/`calitate_intocmit` = `"ADMINISTRATOR"` și `judP` = `"40"` (București) când lipsesc din profil — emise TĂCUT. Câmpuri OBLIGATORII la ANAF (`d394_struct_anaf.txt:21-22`), deci implicitul rămâne (altfel DUK respinge câmpul gol) DAR e acum ANUNȚAT prin avertisment vizibil (`res.avertismente`): implicit DECLARAT, nu tăcut. judP anunțat o singură dată (dedup). MUTAȚIE: profil fără reprezentant/județ → avertisment prezent; profil complet → niciun avertisment de implicit.
- **#3 nrFacturi = SPANUL seriei, nu numărul real (calcul greșit).** `d394_struct_anaf.txt:1797`: nrFacturi = „Nr total facturi emise în perioadă". COD VECHI: `sum(1+(max-min))` peste plaja seriei → la numerotare necontiguă (45,46,50) raporta 6 în loc de 3. FIX: `nr_facturi_emise()` numără efectiv facturile emise cu număr numeric (aceeași populație ca `serii_emise` → R131 păstrat: nrFacturi>0 ⟺ serieFacturi tip 2); `pull()` îl întoarce în `date["nr_facturi"]`, `calcul_d394` îl folosește când e disponibil (apelanții puri cad pe span, aproximație documentată). `serieFacturi` păstrează plaja min-max. MUTAȚIE: 3 facturi 45/46/50 → nrFacturi=3, serieFacturi plaja 45-50.
- **Neacoperit (raportat, regula 12):** bonuri fiscale/facturi simplificate/AMEF (Î1/BFAI) rămân 0 — Raportul Z importat de `amef_import.py` e agregat B2C fără CUI beneficiar (mare parte NEraportabil în D394); de verificat la sursă dacă vreo încasare AMEF poartă CUI beneficiar înainte de a alimenta secțiunea. Reconcilierea a-doua-cale acoperă `rezumat2` firmă-nivel (nu per-partener/jurnale, nu cota-0) — limită declarată în `d394_reconciliere.py`. Nicio cale registru/balanță→D394 (ambele căi citesc doar `facturi`). Clasificarea AÎ (achiziții de la furnizori cu TVA la încasare) neimplementată — depinde de stocarea mențiunii pe factura primită.

## 15.08.2026 — Campanie rețeta D300 pe D390 (pas 2/8): NOTA 1 (achiziție IC fără cod) + declarant fabricat + exigibilitate achiziții (cluster "D390 audit")
Aplicat unghiurile D300 pe D390. Trei remedieri cu gard + probă DUK: `core/test_d390_nota1.py` (8 teste: 2 pure declarant, 6 DB pe `tenant_template.sql`, cu probă DUK NOTA 1). Confruntat la sursă cu `anaf_surse/opanaf_394_2017_d390_anexa2_instructiuni.txt` (OPANAF 394/2017) + `d390_struct_anaf.txt`. Traseul probat cu Playwright (`frontend_test/proba_d390_nota1.py`).
- **#1 NOTA 1 — achiziția IC de la furnizor UE fără cod valid era NEDECLARABILĂ (neconformitate legală + pierdere tăcută).** Instrucțiuni:189-201: „Pentru achiziţii intracomunitare de bunuri taxabile în România, în cazul în care furnizorul nu comunică un cod valabil de TVA, dar bunurile sunt transportate de pe teritoriul unui stat membru ... achiziţia se declară: Ţara = statul membru; Cod operator = nu se va înscrie nimic; Tipul operaţiunii = A". COD VECHI: calea auto (`d390.py` `_clasifica_partener`) excludea partenerul fără prefix UE valid (nu are câmp de țară pe factură); calea manuală (`d390_clasificare_api.py:65`) RESPINGEA tip A (doar P/S/T/R) → operațiune obligatorie pierdută, neprinsă nici de reconciliere. FIX: `manual_adauga` acceptă tip **A** cu cod GOL (A nu e în `_CU_COD_OBLIG` → cod opțional; țara rămâne obligatorie = stat membru UE); `build_xml` omite deja `codO` gol pentru A → `<operatie tip="A" tara="DE" denO=".." baza=".."/>` valid DUK; reconcilierea a-doua-cale include deja latura manuală pentru ORICE tip (`_recalcul_independent` folosește `op.get("tip")`) → fără divergență falsă. UI: opțiune „Achiziție bunuri IC fără cod furnizor — NOTA 1 (A)" în selectorul manual D390 (`declaratii.js`) + notă contextuală. MUTAȚIE: tip A respins vechi → acceptat; genereaza emite A fără codO; DUK valid. Probat Playwright: opțiunea A se randează și se adaugă o achiziție fără cod.
- **#2 declarant FABRICAT tăcut (regula 4).** `d390.py` `build_xml` emitea tăcut `nume_declar`/`functie_declar`=„ADMINISTRATOR", `prenume_declar`=„-" când lipseau din profil (câmpuri DA). FIX: implicitul rămâne (DUK cere câmpul) DAR e ANUNȚAT prin avertisment. MUTAȚIE: profil fără declarant → avertisment; profil complet → niciun avertisment.
- **#3 exigibilitate la ACHIZIȚII — gol de probă închis.** Fereastra art.284 „ziua 15" (`pull` `_exig` SQL) se aplica uniform ambelor direcții, dar era probată doar pe livrări (`test_d390_ziua15.py` toate `emisa`). Adăugat caz `directie='primita'`: factură furnizor emisă târziu + fapt anterior → mutată pe luna exigibilității. Fără schimbare de cod — închidere gap de acoperire.
- **Neacoperit (raportat, regula 12):** RECTIFICATIVA D390 (`d_rec="0"` hardcodat, `d390.py:372`) — corectarea unei declarații depuse nu are cale în aplicație; funcțional major, campanie proprie. Art.317 fără PERIOADĂ de valabilitate (boolean, nu interval) → operațiuni din luni în afara valabilității incluse fără avertisment. Serviciile IC (P/S) fără a-doua-sursă nici din evidență, nici din D300 (reconcilierea invers + D300 acoperă doar bunuri L/A). denO multiplu pe (tara,codO) fără gardă pre-DUK. Toate depind de aplicație (nu de ANAF) — semnalate pentru pași proprii.
- **#4 (follow-up) liniile manuale D390 nu se puteau STERGE din UI (angle 7 - ce se afiseaza si nu se poate corecta).** `pull_manual` (`d390.py`) returna liniile FARA `id`, dar `stare()` le trimite la UI iar butonul de stergere cheama `DELETE .../manual/{id}` -> `data-id=undefined` -> 422. Descoperit incidental la proba Playwright (linia de test nu s-a putut curata). FIX: `pull_manual` include `id` (consumatorii de calcul il ignora). Gard: `test_manual_linie_are_id_si_se_poate_sterge` (add -> `stare` are id -> `manual_sterge` reuseste -> dispare).

## 16.08.2026 — Campanie rețeta D300 pe D301 (pas 3/8): zero-base + ruptura facturi IC + Secțiunea 1 art.317 + declarant + panou pe eroare (cluster "D301 audit")
Aplicat unghiurile D300 pe D301. Verificat la sursă `anaf_surse/opanaf_592_2016_d301.txt`. Gard `core/test_d301_zero_ruptura.py` (6 teste, DB + DUK). Traseul probat cu Playwright.
- **#1 ZERO-BASE fără refuz + RUPTURA seed↔consumator (regula 10).** Sursa (instr. II, l.312): „Decontul special se depune NUMAI pentru perioadele în care ia naştere exigibilitatea taxei". COD VECHI: `genereaza` emitea XML cu `baza1..5=0` pe zero, fără refuz. Mai grav: obligația D301 se naşte şi din ACHIZIŢII IC înregistrate ca FACTURI (fluxul normal), dar `pull` (`d301.py`) citeşte DOAR tabelul manual `d301_operatiuni` → o achiziţie IC din facturi neintrodusă manual dispărea din declaraţie (semaforul o semnala la nivel de lună via `d301_luni_facturi_ic`, dar nu curgea în declaraţie). FIX: `genereaza` REFUZĂ pe zero; cross-check best-effort cu `facturi_ic` (achiziţii IC primite) — dacă există facturi IC neintroduse, mesajul le NUMEŞTE (furnizor+sumă), nu refuz generic tăcut; dacă există operaţiuni dar şi facturi IC, avertisment de verificare. MUTAŢIE: zero fără facturi → refuz generic; zero cu facturi IC → refuz care numeşte factura.
- **#2 Secţiunea 1 → art.317 (instr. I, l.220).** „Secţiunea 1 ... se completează NUMAI de către persoanele înregistrate conform art. 317". O operaţiune tip 1 cu `pers_inreg=1` (firmă fără marcajul `inreg_art317`) = declaraţie contradictorie. Marcajul nu e populat fiabil în profil → AVERTISMENT vizibil (nu blocaj, care ar opri orice D301 de secţiunea 1), regula 4/12. MUTAŢIE: tip 1 + fără art.317 → avertisment; cu art.317 → fără avertisment + `pers_inreg=2`.
- **#3 DECLARANT fabricat tăcut (regula 4)** → anunţat prin avertisment (nume/funcţie „ADMINISTRATOR").
- **#4 (traseu, angle 7) chicken-and-egg: refuzul zero-base bloca ACCESUL la ecranul de operaţiuni.** `pas2` (`declaratii.js`) randează panoul editabil DOAR dacă generarea reuşeşte → refuzul zero-base ar fi lăsat o firmă fără operaţiuni FĂRĂ cale să le adauge (acelaşi trap preexistent la D390/D300). FIX: pe eroare de generare, pas2 randează TOTUŞI panoul editabil (`#dec-d301-op` / `#dec-d390-clasif` / `#dec-d300-manual`) + eroarea care explică DE CE; contabilul introduce operaţiunile şi apasă „Regenerează". Repară trap-ul şi pentru D390/D300. Probat Playwright.
- **Neacoperit (raportat, regula 12):** obligaţia de PLATĂ D301 (TVA datorat `Σtva1..5`) nu se înregistrează nicăieri — se urmăreşte doar scadenţa declaraţiei, nu suma către buget. Rectificativa D301 (`d_rec`/`temei` hardcodate „0", deşi OPANAF 779/2024 a adăugat căsuţa). Plafonul 10.000 EUR/an achiziţii IC (CF art.268(4)b) nemonitorizat (declanşează art.317). RON cu curs≠1 în `adauga` (prins la generare de a-doua-cale, dar UI nu previne). Termen special transport nou (înainte de înmatriculare vs 25). Toate depind de aplicaţie — campanii proprii.

## 16.08.2026 — Campanie rețeta D300 pe D112 (pas 4/8): cadou taxabil → D112 (pierdere tăcută de taxe) (cluster "D112 audit")
D112 e cel mai gardat generator (104 teste — cote period-aware, CM, part-time, reconciliere a-doua-cale). Aplicând unghiul „nimic pierdut tăcut" (unghi 2/6) am găsit o pierdere reală: **cadoul TAXABIL era calculat dar nu ajungea în D112**. Verificat la sursă CF art.76(4)a (impozit) + art.142 (contribuții). Gard `core/test_d112_cadou.py` (7 teste, DB + DUK).
- **Cadou taxabil pierdut tăcut (sub-declarare de taxe).** `beneficii_api.cadou_detalii_luna` calcula flag-ul `taxabil`, DAR `d112.pull()` trăgea doar vacanța/cultural/creșă — NU cadou (comentariu vechi „Cadou (E3_73) neinclus"). Un tichet cadou peste plafon (eveniment legal) sau pe eveniment nelegal = venit salarial impozabil (CAS+CASS+CAM+impozit) care **nu ajungea niciodată în declarație** → firma sub-declara taxe la ANAF. Sursa: CF art.76(4)a (l.8051) + art.142 (l.12032): neimpozabil „în măsura în care ... nu depăşeşte 300 lei" DOAR pentru evenimentele legale (Paşte/Crăciun/8 martie/1 iunie); **excedentul peste 300** (eveniment legal) sau **valoarea integrală** (eveniment nelegal) = venit salarial; acelaşi plafon pentru impozit ŞI contribuţii. FIX: `beneficii_api.cadou_taxabil_luna` (suma taxabilă corectă: excedent vs integral); `calcul_salariu(cadou_taxabil)` → intră în `b_imp` (venit salarial COMPLET, ca exces_vac) → CAS/CASS/CAM/impozit; emis în `E3_73`; adăugat şi în brutul DECLARAT (d112.py:207/241, altfel B4_3 vs contribuţii = DUK S74 inconsistent). Reconcilierea a-doua-cale NEAFECTATĂ (sare angajaţii cu intrări `beneficii_lunare` via `ben_ids`, orice tip). MUTAŢIE: cadou 500 pe „craciun" → taxabil 200 (excedent); 400 pe „altul" → 400 (integral); 250 pe „paste" → 0; E3_73 emis; B1_sal1 creşte cu cadoul; DUK valid.
- **Neacoperit (raportat, regula 12) — toate depind de aplicaţie (model/cablaj), campanii proprii:**
  - **[REPARAT 16.08.2026 — Task 2 D112 exhaustiv, vezi secţiunea de mai jos] Deducerea suplimentară cod mort → impozit SUPRA-declarat.** `salarizare.deducere_personala` suporta `sub_26` (tineri) + `copii_scoala` (100 lei/copil, art.77 alin.10), dar NICIUN apelant de producţie le transmitea → tinerii sub 26 şi părinţii cu copii şcolarizaţi aveau impozit SUPRA-declarat. CABLAT: coloane noi `salariati` (data_nastere/copii_scolarizati/declaratie_copii), `d112.pull` + `stat_plata_api` pasează deducerea, `sub_26` derivat din data naşterii.
  - **Zilieri / mandat administrator / cenzori nu ajung în D112.** `contracte_speciale.py` calculează impozit/CAS/CASS „pentru declarare D112" dar e referit doar din teste — `d112.pull()` citeşte doar `salariati`. Venit asimilat salariilor pierdut.
  - **B1_3 (tip contract timp de lucru) hardcodat „N" la part-time** (struct l.3852: valori N/P1..P7; un part-timer 6h ar fi „P6"). Model fără câmp; cuplează B1_4/B1_6/DUK.
  - **Elemente nesalariale neintroductibile:** diurnă peste plafon, avantaje în natură, pensii facultative + asigurări private (plafoane 400 EUR/an), plafonul lunar 33% (CF art.76(4^1)). Grep=0 în pipeline.
  - **Scutiri sectoriale (construcţii/agricultură) pe luni istorice 2025** (abrogate 2026, dar aplicaţia suportă luni date-aware istorice).

## 16.08.2026 — Campanie rețeta D300 pe D100 (pas 5/8): baza impozitului pe PROFIT reparata (venituri->profit) (cluster "D100 audit")
Aplicând unghiul „calcul greșit / reconciliere" pe D100 am găsit un bug GRAV care trecea toate gărzile. Verificat la sursă CF art.17 + `anaf_surse/d100_struct_anaf.txt` (poz.2 cod 103). Gard `core/test_d100_profit_baza.py` (5 teste, DB + DUK).
- **Baza impozitului pe PROFIT (103) era VENITURI × 16%, nu PROFIT × 16% (supra-declarare grosolană).** `d100.py` (branch profit) + `d100_reconciliere.py` (ambele căi!) calculau `suma = venituri(70x) × cotă`. Impozitul pe profit se aplică pe PROFIT (venituri − cheltuieli ± ajustări), NU pe venitul brut (CF art.17 „cota ... asupra **profitului impozabil**"; struct poz.2 „Impozit pe profit"). Un SRL cu venituri 1.000.000 şi profit 100.000 primea o obligaţie de **160.000 în loc de 16.000** — DUK-valid dar grosolan greşit. Eroarea era **PARTAJATĂ de ambele căi de reconciliere** (ambele venituri × cotă) → nimeni n-o prindea (blind-spot declarat implicit la limita 5). FIX: `pull()` citeşte şi cheltuielile (6xx debit); pentru regim profit **baza = venituri(70x) − cheltuieli(6xx)** (profit contabil); ajustările fiscale (nedeductibile/neimpozabile art.19+ CF) + regularizarea anuală se fac la D101 (avertizat pe `res.avertismente`). Profit ≤ 0 (pierdere în trimestru) → fără avans, refuz cu mesaj de PIERDERE (nu „venituri=0" fals). Reconcilierea foloseşte ACEEAŞI bază (fără fals-pozitiv). Micro NESCHIMBAT (baza = venituri, corect pentru 121). BACKWARD-COMPATIBLE: fixturile fără cheltuieli 6xx → profit=venituri → rezultat neschimbat; firmele reale cu cheltuieli primesc baza corectă. MUTAŢIE: venituri 100k + cheltuieli 60k → obligaţie 6400 (nu 16000); pierdere → refuz PIERDERE; micro → venituri × 1%.
- **Neacoperit (raportat, regula 12) — semantice/de scop, app-dependent:**
  - **Fără reconciliere cu vectorul fiscal (GAP critic).** `d100` nu importă `vector_fiscal_api`: nu verifică nici că firma E înscrisă pe obligaţia emisă, nici că nu OMITE o obligaţie pe care o are (dividende 150/604, dobânzi 605, nerezidenţi 631-641, accize). Dividende distribuite contabilizate NU generează linie D100 şi nimic nu semnalează.
  - **112 din 114 obligaţii neacoperite + periodicitate hard-trimestrială.** Generatorul emite doar 121 (micro) + 103 (profit). Obligaţiile lunare (150/604/605/631-641) + accizele (poz.113-114 noi OPANAF 57/2026) imposibil de generat; `calcul_d100` ridică pe lună ∉ (3,6,9,12); canalul `manual` expune doar `cota`.
  - **Cotă 3% micro pentru an < 2026** absentă din registru (subdeclarare micro-3% 2024-2025).
  - **Reducere/sponsorizare/bonificaţie micro** implicit 0 (struct poz.5 model 9# le prevede) → supraplată tăcută.
  - **Trecerea de regim în cursul anului** — `regim_fiscal` punctual, nu period-aware; trimestrul de tranziţie primeşte regimul curent.

## 16.08.2026 — Campanie rețeta D300 pe D101 (pas 6/8): sponsorizare limita 0.75% cifră afaceri (limita DUBLĂ) (cluster "D101 audit")
Aplicând unghiul specific D101 cerut de Costin („creditele: sponsorizarea cu limita DUBLĂ") am găsit că doar jumătate din limită era păzită. Verificat la sursă CF art.25 alin.(4) lit.i (`cod_fiscal_227_2015_consolidat.txt:1975`). Gard `core/test_d101_sponsorizare_075.py` (6 teste).
- **Sponsorizarea: limita 0.75% cifră de afaceri LIPSEA (limita DUBLĂ păzită pe jumătate).** Creditul de sponsorizare (CF art.25(4)i) = min(**0,75% × cifra de afaceri**; 20% × impozit pe profit). DUK verifică DOAR partea de 20% (V5: rd.43 ≤ 20%×(rd.41-rd.42)); limita 0,75% CA nu era nicăieri (grep `0.75` = 0 rezultate). O firmă cu impozit mare dar cifră MICĂ putea deduce peste 0,75% CA fără ca app sau DUK s-o oprească. FIX: gard V5-bis în `_erori_valori_p` (`d101.py`): `P43 ≤ 0.75% × cifra_afaceri`. CA = SUM(cont 70x) = cifra de afaceri netă (**≥ CA reală**, care scade reducerile 709) → gard SOLID (fără fals-pozitive: dacă P43 > 0.75%×70x ≥ 0.75%×CA_reală, e violare sigură). Activ doar când CA e cunoscută din balanță (calea pull); apelanții puri (fără CA) → sărit (backward-compat). Regula 6: gardul intră în verificator (`_erori_valori_p`) simultan. MUTAȚIE: P43=1000 cu CA 100000 (0.75%=750) + impozit mare → V5-bis mușcă (V5 nu); P43=700 → OK; CA=None → sărit.
- **Neacoperit (raportat, regula 12) — Costin le-a cerut expres; toate necesită model/calcul mai amplu, app-dependent:**
  - **Pierderea fiscală: limita 70% / 7 ani / ordinea vechimii — absente.** P39/P39a sunt inputuri; doar V1 (P39a≤P39). Lipsesc: limita anuală 70% din profitul impozabil (Legea 296/2023, de la 2024), fereastra 7 ani, stoc de pierderi pe ani, pierderea pre-2024 (100%) vs post-2024. Risc de supra-deducere.
  - **Costurile excedentare ale îndatorării (ATAD, art.40^2): min(30% EBITDA fiscal; 1M EUR) — absente.** P12/P31 inputuri pure (grep EBITDA/indatorar = 0).
  - **P50 vs D100 — nicio reconciliere impozit declarat vs plăți anticipate.** P50 = input pur; D101 nu citește D100-urile trimestriale → P52/P53 (diferența de plată) se sprijină pe P50 introdus manual, necontrolat.
  - **Protocol 2% (bază proprie) + cheltuieli sociale 5% — nici calculate, nici gardate** (P26 input; cheltuielile sociale nici rând dedicat).
  - **Rectificativa (corectarea) imposibilă:** `d_rec="0"` hardcodat → doar declarații inițiale.
  - **An fiscal modificat / micro→profit mijloc-de-an / dizolvare** nereprezentabile (Data_I/Data_S 01.01–31.12 hardcodate); scadența ignoră cod_obligatie=104 (LL+2) și d_reglem.

## 16.08.2026 — Campanie rețeta D300 pe D205 (pas 7/8): cota impozitului pe dividende 2025 = 10% (nu 8%) (cluster "D205 audit")
Aplicând unghiul „temeiul verificat la sursă" pe D205 am găsit un bug FISCAL ACTIV (campania curentă, pentru anul 2025). Verificat la sursă (sursa bate memoria, regula 2). Gard `core/test_d205_cota_2025.py` (4 teste + DUK).
- **Cota impozitului pe dividende 2025 = 10%, codul aplica 8% (sub-declarare 20%).** Registrul `common.COTE['impozit_dividend']` avea 2023→8%, 2026→16%, DAR **lipsea 2025→10%** → pentru an=2025 `cota()` returna 8% (intrarea 2023). Sursa: **OUG 156/2024 art.LXIV+LXV** (`oug_156_2024.txt:3-4,50`): „Veniturile sub formă de dividende ... se impozitează cu o cotă de **10%** ... impozitul fiind final", în vigoare de la **1 ianuarie 2025**; confirmat INDEPENDENT de `d205_struct_anaf.txt:6` „8%/2024, **10%/2025**, 16%/2026". CAUZA regresiei: un petic anterior avea 10% pe `data_in 2024-01-01` (greșit: 2024=8%); o notă (`impozit_dividende_istoric_cote.txt:23`) + comentariul din cod au declarat „10% e GRESIT, e cota art.78" — au confundat DATA (peticul era greșit pe 2024, nu cota) și au **aruncat cota** în loc s-o mute la 2025. FIX: adăugat `(date(2025,1,1), 0.10, OUG 156/2024)` în registru; corectat comentariul din `common.py` + comentariul din `d205.py` + nota din corpus. Propagă corect period-aware: `decontari_asociati.cota_dividend`, `lichidare`, `d205.genereaza` → 10% pentru 2025 (8% pentru 2024, 16% pentru 2026). Corectate 4 teste care CIMENTAU valoarea greșită (test_d205, test_impozit_dividend din core/, plus decontari_asociati.py si lichidare.py de la radacina). MUTAȚIE: 50000 dividende plătite 2025 → impozit 5000 (nu 4000); DUK valid.
- **Neacoperit (raportat, regula 12) — Costin le-a atins prin unghiuri; app-dependent:**
  - **[CRITIC] Dividende DISTRIBUITE dar NEPLĂTITE la 31.12 dispar din declarație.** `d205.py:359` `if platit > 0` + `baza1=platit` → un dividend distribuit (Σ credit 457 în decembrie) dar neplătit → niciun beneficiar → impozitul DATORAT dispare. Sursa (`opanaf_179_2022_d205_d207_baza.txt:728-730`): impozitul pe dividendul distribuit-neplătit „se cuprinde în declaraţia aferentă perioadei în care s-a aprobat distribuirea". Cere rework model distribuit-vs-plătit (baza pe distribuit) + cuplare reconciliere (recalc din Σ credit 457, nu debit) — campanie proprie.
  - **Tipuri de venit lipsă:** generatorul e dividende-only (tip_venit=08); lipsesc real 09 (dobânzi 10%), 29 (arendă/chirie 10%), 16 (alte surse 10%) + 04/11/12/18/26/27/28/30. (Drepturile de autor și activitatea sportivă NU mai sunt pe D205 actual — corect că lipsesc.)
  - **Fără reconciliere cu contul 446** (impozit reținut): codul recalculează, nu citește impozitul real postat; o plată postată doar net (457=5121, fără 457=446) → baza subevaluată tăcut.
  - **Repartizare per-asociat fabricată din cota de participare, nu din plata reală** (457 neanalitic pe asociat).
  - **Rectificativa imposibilă** (`d_rec="0"`, `luna="12"` hardcodate); cheie unicitate doar-CNP (blochează același beneficiar cu tipuri multiple); niciun avertisment CASS pe dividende peste plafon (D212 beneficiar).

## 16.08.2026 — Campanie rețeta D300 pe D406 (pas 8/8, ULTIMA): RegistrationNumber firmă proprie cu prefix RO (cod mort cablat) (cluster "D406 audit")
Aplicând unghiul „nomenclatoarele / cine scrie-cine citește" (regula 10) pe D406 (SAF-T) am găsit o funcție-fix scrisă dar necablată. Verificat la sursă (`d406_schema_anaf.xlsx` foaia „5. Structures", S.CMH.1 CompanyHeaderStructure). Gard `core/test_d406_reg_number_header.py` (4 teste + DUK).
- **RegistrationNumber al firmei proprii emitea CUI BRUT (fără prefix RO) → „format invalid" la DUK pentru plătitorii de TVA.** `_header` (`d406.py`) emitea `_esc(cui)` cu `cui = _NEDIGIT.sub("", ...)` (cifre brute). Regula oficială S.CMH.1: rezident plătitor TVA → **RO+CIF**; neplătitor → CIF. Funcția `registration_number(prof)` implementa exact această regulă și avea docstring care DESCRIA bugul („Codul scria _NEDIGIT.sub..., adică ștergea exact prefixul cerut → «formatul este invalid» pentru orice plătitor de TVA") — DAR era **COD MORT (0 apeluri reale)**; doar `_partener_registration_number` (pentru parteneri) era folosit. FIX: cablat `registration_number(prof)` în `_header`; adăugat `platitor_tva` în SELECT-ul `pull()` (nu era citit → `prof` nu-l avea → funcția cădea pe default). Acum: plătitor TVA → `RO14399840`, neplătitor → `14399840`. Probat DUK valid. MUTAȚIE: header platitor → RO+CIF; neplatitor → CIF fără RO; gard AST că `_header` cheamă `registration_number`.
- **Neacoperit (raportat, regula 12) — SAF-T e cea mai amplă declarație; toate app-dependent, campanii proprii:**
  - **[TOP] Soldurile de DESCHIDERE (OpeningBalance) sunt ÎNTOTDEAUNA 0; închiderea = soldul curent, nu de sfârșit-de-lună.** `pull()` populează doar `sold_inchidere` din `plan_conturi` (snapshot curent); `sold_deschidere` rămâne 0. Sursa reală (`solduri_initiale`, `solduri_api.py:130`) e neconsumată. Afectează ORICE firmă cu solduri — cel mai grav rest (cere calcul de sold la început/sfârșit de lună = solduri_initiale + Σ rulaje).
  - **Payments neemis (F035):** cod complet scris, dar `pull()` returnează mereu `plati=[]` — trezoreria reală nu se mapează.
  - **Facturile nu se reconciliază cu GL** (`d406_reconciliere.py:19-21`): `facturi` vs `inregistrari` = două surse niciodată confruntate → dublare/omisiune neprinsă.
  - **Stocuri (F037):** `UOMPhysicalStock` emite UM brut (`'buc'`), nu cod UN/ECE (respins DUK); fără metodă de evaluare (FIFO/LIFO/CMP); `StockMovement`/MovementType niciodată emis; nu în AuditFile lunar.
  - **Active:** ieșiri/reevaluări/casări = 0 (doar achiziția e tratată); nereconciliat cu GL (21x/28x). Amortizarea (F036) e ÎNCHISĂ de fapt (degresiv/accelerat/superaccelerat implementate — registrul GARZI 11.08 era STALE pe „doar liniară").
  - **Products stub GENERIC** (fără ProductCode pe linii); Country/Currency forțate RO/RON (partener UE / factură valută raportate greșit); fără perimetru/periodicitate/rectificativă (OPANAF 407/2025); rutele active/stocuri fără UI.

## 16.08.2026 — Clasa CHICKEN-AND-EGG: căutare sistematică în toată aplicația (0 cazuri genuine rămase) + gardă (cluster "chicken-and-egg")
Costin a cerut căutarea CLASEI (nu doar cazurile reparate la D301/D390/D300 în campania rețeta-D300). Tiparul: un ecran randează formularul de INTRODUCERE a datelor DOAR după ce o operație reușește, iar operația are nevoie de datele care se introduc PRIN acel formular → dintr-o stare goală nu există punct de intrare.
- **Căutare sistematică (40 fișiere `static/js/ecrane/` + toate wizardurile/fluxurile): UN SINGUR caz genuin în toată aplicația — pas2 (d300/d301/d390), DEJA reparat în campanie.** Restul ecranelor cu formular de primă introducere sunt BENIGNE, cu o **semnătură structurală distinctivă**: la pas2, poarta era un **POST care GENEREAZĂ+VALIDEAZĂ și REFUZĂ pe zero-base** (`/declaratii/{tip}/valideaza` arunca 422 pentru firmă fără operațiuni), iar formularul editabil era randat DUPĂ acel POST → firmă proaspătă blocată. Peste tot altundeva formularul de adăugare e gardat doar de un **GET de citire care întoarce listă goală (200, nu aruncă)** și e randat NECONDIȚIONAT (empty-state ascunde doar LISTA, nu formularul); `catch{...return}` se declanșează doar la eroare reală de server, unde reîncărcarea e recuperarea corectă. Verificat individual: operatiuni_ecran (config statică REGISTRU), mijloace/produse/salariati/stocuri/casa/centre-cost/registratura/contracte/banca (add-form necondiționat după GET), flux_concediu (#cm-nou necondiționat), facturi/recurente/emitere/etransport, migrare (wizard cu empty-state care trimite ÎNAPOI la stratul 1 = punctul de intrare), date_firma/setari/portal/asistenti (editare din defaults). Niciun al-doilea-ordin: încărcătoarele de panou (`randeazaOperatiuniD301` etc.) fac GET care întoarce listă goală, nu POST care refuză.
- **Gardă mecanică anti-regresie** (`core/test_pas2_panou_editabil_pe_eroare.py`, 2 teste): invariantul e generic — orice container de panou-declarație `dec-XXX` gardat de `S.tip ===` în ramura de SUCCES a lui pas2 trebuie să apară SI în ramura `catch` (+ loader-ul apelat în catch). Un panou editabil NOU adăugat în succes fără randare-pe-eroare pică → reintroduce chicken-and-egg. Mutație: catch fără un panou → roșu (test_gardul_prinde_regresia). Tiparul E descriptibil mecanic pe pas2 (o singură cale de generare-refuză-pe-gol); pentru restul aplicației distincția genuin-vs-benign NU e pur sintactică (benign = GET care întoarce gol), deci o gardă globală ar avea fals-pozitive — de aceea garda e țintită pe pas2 (unde clasa chiar apare).


## 16.08.2026 — Task 2 D112 (turǎ exhaustivǎ pe modelul D300), fix 1/N: DEDUCEREA PERSONALǍ SUPLIMENTARǍ cablatǎ (cluster "D112 exhaustiv")
Prima reparaţie din tura exhaustivǎ D112 (Costin a numit expres deducerea suplimentarǎ). Cod mort raportat în campania pas 4/8, acum CABLAT cap la cap + probat pe date reale.
- **Deducerea personalǎ suplimentarǎ (CF art.77 alin.10) nu ajungea în D112 → impozit SUPRA-declarat.** `salarizare.deducere_personala` calcula corect (a) 15% × salariu minim pentru tinerii SUB 26 de ani (venit ≤ sm+2000), (b) 100 lei/lunǎ per copil ≤18 ani înscris în învǎţǎmânt (pe baza declaraţiei pǎrintelui, alin.12-13) — DAR niciun apelant de producţie nu transmitea `sub_26`/`copii_scoala`/`declaratie_copii`; toţi salariaţii primeau doar deducerea de bazǎ (`persoane`). Un tânǎr sub 26 sau un pǎrinte cu copii şcolarizaţi avea impozit pe venit SUPRA-declarat la ANAF (deducere pierdutǎ). Sursǎ verificatǎ: `cod_fiscal_227_2015_consolidat.txt` l.8693 (15% tineri <26, venit ≤ alin.3) + l.8697 (100 lei/copil <18 înscris, indiferent de nivel). FIX:
  - **Model:** coloane noi pe `salariati` — `data_nastere` (derivǎ `sub_26` la luna venitului, nu flag manual), `copii_scolarizati` (numǎr copii ≤18 în învǎţǎmânt), `declaratie_copii` (declaraţia pǎrintelui — FǍRǍ ea deducerea de 100 lei NU se acordǎ, art.77 alin.12-13). `tenant_template.sql` (sursa unicǎ) + `migrare_d112_deducere_suplimentara.py` (ADD COLUMN IF NOT EXISTS, rulat pe toate schemele tenant). `_CAMPURI_API` + UI `firme.js` (3 câmpuri noi + payload, asset re-ştampilat).
  - **Cablaj:** helper `salarizare.sub_26_la(data_nastere, la_data)` (vârsta < 26 la data venitului). `d112.pull` — dict-ul salariat construit include acum data_nastere/copii/declaratie (SELECT * le aducea, dar dict-ul explicit le omitea → `s.get()` da None → necablat); apelul `calcul_salariu` pasează `sub_26`/`copii_scoala`/`declaratie_copii`. Consistenţǎ fluturaş↔D112: `stat_plata_api` (2 SELECT + 2 unpack + 2 apeluri) la fel. GATE: `copii_scoala` doar dacǎ `declaratie_copii` (fǎrǎ declaraţie → nu se acordǎ, dar NU blochează generarea).
  - **Gard `core/test_d112_deducere_suplimentara.py` (3 teste, DB + DUK):** tânǎr <26 → deducere mai mare + impozit mai mic; diferenţa = 15% × salariu minim (rotunjit); pǎrinte cu 2 copii + declaraţie → +200; copii FǍRǍ declaraţie → gate (nu se acordǎ, fǎrǎ eroare); D112 DUK-valid.
- **Probat pe DATE REALE (firma grea tenant_017, seed regenerat, 3 cazuri noi):** SUB26 (nǎscut 2003) deducere 1032.75 = 425.25 bazǎ + 607.50 tineri; SCOALA (2 copii + declaraţie) 422.75 = 222.75 + 200 copii; NEDECL (1 copil, fǎrǎ declaraţie) 344.25 (gate, fǎrǎ deducere copii); D112 2026-06 DUK-valid.
- **Rǎmâne (Task 2 D112, fixuri urmǎtoare):** zilieri/mandat/cenzori (`contracte_speciale.py` necablat la `d112.pull`); B1_3 part-time hardcodat „N" (P1..P7 din ore); atribute hardcodate (E3_3/asigSO/asigCI/E3_2); nesalariale (diurnǎ peste plafon, avantaje naturǎ, pensii/asigurǎri 400 EUR/an, plafon 33% art.76(4^1)); scutiri sectoriale istorice 2025; headcount vs REGES; CAM temei art.220^1→220^3; apartenenţǎ la perioadǎ.


## 16.08.2026 — Task 2 D112, fix 2/N: temeiul cotei CAM cita articolul gresit (220^1 -> 220^3) (cluster "D112 exhaustiv")
Al doilea fix din tura exhaustiva D112. Corectitudine de TEMEI (regula 3/5), fara schimbare de valoare/DUK.
- **Cota CAM (2,25%) cita `art="220^1"` in loc de `art="220^3"`.** `common.COTE["cam"]` avea Temei cu camp `art="220^1"` care CONTRAZICEA propriul `text_citat` ("art.220^3 alin.(1): Cota contributiei asiguratorii pentru munca este de 2,25%") + comentariile `d112.py:135/500`. Verificat la sursa `cod_fiscal_227_2015_consolidat.txt`: l.14954-14957 art.220^3 alin.(1) = "Cota contributiei asiguratorii pentru munca este de 2,25%"; l.14927 art.220^1 = doar CONTRIBUABILII (cine plateste). FIX: `art="220^3", alin="1"` + `verificat_la` bumpuit la re-verificarea de azi. Gard `test_temei_structurat.py::test_cam_temei_articolul_cotei_e_220_3` (art==220^3 + text_citat coerent + cota nemodificata 0.0225).

## 16.08.2026 — Task 2 D112 (turǎ exhaustivǎ): STARE + backlog triat (regula 12), tura PAUZATA pe context (§2.3 "context epuizat")
Tura exhaustivǎ D112 a livrat 2 fixuri PROBATE (deducere suplimentarǎ = fix 1, CAM temei = fix 2). Restul suprafeţei D112 auditate rǎmâne triat mai jos; fiecare item e un build campanie-size (coloanǎ/model nou + UI + chirurgie XML cu risc de regresie) — de aceea NU s-au atins pe jumǎtate (regula 11: probǎ pe date reale, nu cod pe jumǎtate). Prioritizat dupǎ SEVERITATE:
- **[HIGH — venit nedeclarat] Zilieri / mandat administrator / cenzori nu ajung în D112.** `contracte_speciale.py` (motor pur: zilier impozit 10%+CAS 25%; mandat/cenzor CAS 25%+CASS 10%+impozit 10%) e referit doar din teste — `d112.pull()` citeşte doar `salariati`. Venit asimilat salariilor (CF art.76(2)) COMPLET ABSENT din declaraţie → risc de nedeclarare. Necesitǎ: tabel nou (contracte speciale: CNP/tip/brut/perioadǎ) + CRUD + UI + secţiune D112 cu atribute proprii (tip_asigurat, fǎrǎ CAM la zilieri) + DUK. Campanie proprie.
- **[HIGH — venit potenţial nedeclarat] Elemente nesalariale neintroductibile.** Diurnǎ peste plafon, avantaje în naturǎ, pensii facultative + asigurǎri private de sǎnǎtate (plafon 400 EUR/an fiecare), plafonul lunar 33% (CF art.76(4^1)). Grep=0 în pipeline-ul D112. Venit salarial impozabil care nu are cale de intrare. Campanie proprie (model + calcul plafoane).
- **[MEDIU — mis-declarare tip contract] B1_3 part-time hardcodat "N".** Struct ANAF D112 l.3850-3866: B1_3 ∈ {N, P1..P7} cu i<B1_4 (norma). Un part-timer se declarǎ "N" (norma întreagǎ) în loc de Pi. Amounts corecte (proratarea minimului se face din `part_time` bool), DAR tipul de contract e mis-declarat cǎtre ANAF/inspecţia muncii. Modelul are DOAR `part_time` bool + `ore_zi` (clampat la {6,7,8} = norma) — NU stocheazǎ orele parţiale lucrate (i). Fix cere: coloanǎ `ore_partiale` (1..7) + corecţia `ore_lucr`/B1_6 (azi `zile*ore` supra-numǎrǎ orele part-timerului) + UI + DUK. Temei norma verificat: CM art.111(1) (8h/zi standard) + art.112(1) (6/7/8 pe sectoare) — deja în corpus. Campanie proprie.
- **[MEDIU — cazuri non-standard inexprimabile] Atribute hardcodate în `<asigurat>`.** asigCI="1"/asigSO="1" (asigurat concedii/şomaj), B1_1="1"/B1_2="0", E3_3 (funcţie de bazǎ). Corecte pentru salariatul standard, dar pensionarii/anumite tipuri de contract au valori diferite — inexprimabile azi. Model + UI + DUK.
- **[MEDIU — deriva istoricǎ] Scutiri sectoriale (construcţii/agriculturǎ) pe luni istorice 2025.** Abrogate 2026, dar aplicaţia suportǎ luni date-aware istorice; scutirile nu se aplicǎ retroactiv la lunile 2025. Calcul period-aware.
- **[MEDIU — reconciliere headcount] Numǎr asiguraţi vs REGES.** Fǎrǎ a-doua-cale pe headcount-ul declarat vs registrul de evidenţǎ.
- Toate depind de APLICAŢIE (nu de rǎspunsul ANAF); niciuna nu e decizie de produs. Ordinea recomandatǎ = severitatea de mai sus (zilieri/nesalariale întâi = venit nedeclarat).


## 16.08.2026 — Task 2 D112, fix 3/N: GENERALIZAREA clasei deducerii (§8) la adeverinta + salarii_contare (cluster "D112 exhaustiv")
Generalizarea pe clasa a fix 1 (regula generalizare / §2.2 §8). Cautat TOTI apelantii de productie ai
`calcul_salariu` (`grep -rln "calcul_salariu(" core/*.py | grep -v test_` -> adeverinta, d112, salarii_contare,
salarizare, stat_plata_api). Fix 1 acoperise d112 + stat_plata; §8 a gasit inca DOUA instante genuine ale
aceleiasi clase (formula cablata dar apelantul o cheama fara sub_26/copii):
- **adeverinta.date_auto: net SUBEVALUAT pe adeverinta.** Chema `calcul_salariu` fara sub_26/copii -> un tanar<26
  sau parinte primea o adeverinta de venit cu NET mai mic decat realitatea (impozit supra-declarat). FIX: SELECT
  extins (data_nastere/copii_scolarizati/declaratie_copii) + pasarea deducerii. Probat: net(tanar) > net(matur).
- **salarii_contare.note_lunare: impozit contabil DIVERGENT de D112.** Recalcula impozitul pentru notele contabile
  (444 credit) fara sub_26/copii -> de cand fix 1 a cablat D112, contabilitatea ar fi declarat ALT impozit decat
  declaratia (rupe "coerenta prin constructie", prins de `control_coerenta`). FIX: pasarea deducerii (s vine din
  pull, are deja campurile). Probat: control_coerenta gol pe un tanar<26.
- Gard `core/test_deducere_generalizare.py` (2 teste, DB): net adeverinta reflecta deducerea + note contabile
  coerente cu D112. CLASA INCHISA: toti cei 5 apelanti de productie ai calcul_salariu paseaza acum deducerea (sau
  SUNT functia insasi - salarizare).


## 16.08.2026 — Registrul declaratiilor facut COERENT + COMPLET (comanda Costin) (cluster "registru declaratii")
Aplicatia produce **50 de declaratii** (dict `DECLARATII` din `core/declaratii_api.py` = sursa unica a tipurilor produse: 9 LIVE cu ecran generic + 41 `_DOAR_API`, majoritatea AMANAT backend+DUK fara ecran dedicat). Toate 50 aveau deja rand in `FUNCTIONALITATI.csv` + intrare `CHEIE_DUK` + generator `core/<tip>.py::genereaza()` — registrul era mai complet decat parea. Incoerentele REALE gasite si reparate:
- **5 randuri STALE/duplicate.** D106/D177/D207/D230/D307 aveau fiecare un rand VECHI (Sursa=`—`, stare RESPINS/AMANAT „nu construim") de dinaintea campaniei de constructie, LANGA randul canonic cu generator real (Sursa=`core/dXXX.py`). Rezultat: aceeasi declaratie cu doua stari contradictorii (D106/D230 chiar RESPINS langa AMANAT), o stare falsa (RESPINS pe ceva ce codul acum produce). ELIMINATE randurile stale (F173/F174/F175/F193/F206) — niciun rand referit extern (verificat grep); canonicele (F208/F209/F210/F217/F228) raman.
- **GARDA de reconciliere cod↔CSV↔DUK↔generator** (LIPSEA — nimic nu impiedica desincronizarea; duplicatele o dovedeau). `core/test_registru_functionalitati.py`, 4 teste: (a) BIJECTIE `DECLARATII` (dispecer) ↔ rand canonic „Declarația D###" din CSV (prinde declaratie produsa fara rand SI randuri duplicate); (b) niciun rand „Declarația D###" FANTOMA (fara generator si nemarcat RESPINS/ELIMINAT); (c) nicio STARE FALSA (RESPINS/ELIMINAT pe o declaratie pe care codul O PRODUCE); (d) fiecare tip are `CHEIE_DUK` + `genereaza()`. RED probat pe CSV-ul original: bijectia pica pe d106/d177/d207/d230/d307.
- **Ajutor cu TRASEU onest** adaugat la 29 randuri AMANAT fara traseu: „fara ecran dedicat → apare doar in dispecerul intern; traseul (ecran principal → firma → Declarații → DXXX → perioada) va exista cand devine LIVE". Onest pentru „cele fara ecran / doar in dispecer".
- **Docstring-uri stale reparate:** `declaratii_api.py` („dispatch pentru cele 9 declaratii" → 50 tipuri, cu explicatia 9 generice vs 41 `_DOAR_API`); `duk.py` (lista fixa „Instalate 15.07" → „se citesc de pe disc").
- **Surse de sincronizare (ce impiedica desincronizarea), documentate:** declaratii PRODUSE = `DECLARATII` (o singura definitie). Pagina publica + GRUPE_FUNC (login.js) deriva AUTOMAT din `FUNCTIONALITATI.csv` Stare=LIVE via `genereaza_grupe_functii.py` (gard verificator GRUPE_FUNC_STALE: CSV≠login.js → poarta rosie). Selectorul per-firma = `declaratii_api.tipuri()` (= `DECLARATII − _DOAR_API`, dinamic). Excluderea pe forma de firma = `control_fiscal_api.neaplicabile_forma` (sursa unica, partajata cu dispecerul si semaforul). CSV↔cod = noul gard de mai sus.
- **NICIO stare noua ceruta** (exceptia din comanda): vocabularul existent descrie onest fiecare declaratie — LIVE (9, flux complet), AMANAT+motiv (backend+DUK gata, fara ecran), PARTIAL (D406 Active/Stocuri), RESPINS (neprodus: D392 suspendat legal OUG 115/2023 art.LXII / D094 abrogat / D700 administrativ). d212 corect cu DOUA randuri distincte (F030 Motor=engine LIVE, F246 Declaratia=AMANAT), nu duplicat.


## 16.08.2026 — Traseul de inregistrare (client nou) + acoperire ajutor (comanda Costin, 3 probleme legate)
Costin a parcurs inregistrarea cu un CUI invalid (12345678). Trei probleme in ordinea gravitatii:
- **P1 (fc0a330) — ecran alb la esecul adaugarii firmei.** Dupa inregistrare cu CUI invalid, ecranul era o pagina alba cu un rand generic ("firma nu a putut fi adaugata automat. Te poti loga...") — fara identitate, fara cale de intrare, fara diacritice, fara motivul real. Cauza: `provision_tenant` valideaza cifra de control a CUI-ului si arunca, dar `register` inghitea motivul intr-un mesaj generic; frontend-ul intra tacit intr-un dashboard gol (0 firme) cu un toast pe body. FIX: (backend main.py) raspunsul poarta MOTIVUL real (model "nu putem presupune numarul 1"): CUI invalid -> "CUI-ul introdus (X) nu este valid — cifra de control nu corespunde. Verifica cifrele"; CUI duplicat / eroare tehnica au mesaje proprii; cu diacritice; cadru corect (cont+cabinet create si logat -> "din ecranul Firme"). (frontend login.js) `randeazaContCreatFirmaLipsa`: ecran propriu cu logo, "Contul tau a fost creat", motivul real si buton "Intra in cont" — nu mai intra tacit intr-un dashboard gol. **Probat Playwright**: CUI invalid -> ecran cu logo + motiv real + Intra in cont; CUI valid (13548146) -> firma adaugata, intra in app fara ecranul de esec.
- **P2 (fc0a330) — login fara cale catre inregistrare.** Formularul de autentificare cabinet avea 3 optiuni, toate pentru cont existent (autentificare / magic link / reset). Adaugat "Nu ai cont? Inregistreaza cabinetul" -> fluxul de inregistrare. **Probat Playwright** (link prezent + navigheaza).
- **P3 (acest commit) — 50 de intrari LIVE fara ajutor contextual (fara "?").** Cauza gardii ORBE: `test_acoperire_ajutor_nu_regreseaza` (via `_live_si_indici`) filtra `Stare == "LIVE"` EXACT -> cele 50 cu "LIVE (data)"/"LIVE 20.07" scapau, iar baseline 0 trecea fals. FIX: (a) scris ajutor pentru toate 50 (`## Ce face` din descriere + `## Cum ajungi la ea` cu traseul din coloana Acces UI, regula 8; onest "ruleaza in fundal, fara ecran" pentru cron/infra — fara trasee inventate); (b) garda intarita la `startswith("LIVE")`, baseline 0 -> "nicio intrare LIVE fara ajutor" devine mecanic complet. **RED probat**: pe CSV-ul HEAD (inainte), 50 de intrari LIVE fara ajutor -> garda ar fi picat.


## 16.08.2026 — Parcurgere onboarding CUBUS ARTS: 10 defecte, regula 13 (comanda Costin)
Costin a parcurs onboarding-ul pe o firma reala (CUBUS ARTS SRL, CUI 13548146, CAEN 6210), 10 intrebari.
Regula 13 (perimetru, nu numele din intrebare): fiecare intrebare = punct de intrare; reparat perimetrul + tiparul.
Marca 6acd293 -> 65f8bad, 6 commituri.
- **Q9 (3f6e1b2) — data inregistrarii TVA lipsea pe firme adaugate.** Precompletarea ANAF era DUPLICATA in 3 cai de
  creare firma cu seturi de campuri DIFERITE (register: snapshot TVA+_inceput; add-firm: reg_com+tva_la_incasare FARA
  _inceput; import in masa: nimic). SURSA UNICA `tenant_provisioning.precompleteaza_din_anaf`, chemata de toate 3.
  Gard `core/test_precompletare_anaf_unificata.py`. Proba DB+ANAF real (rollback): add-firm scrie acum _inceput=2007-02-01.
- **Q1+Q8 (9d756a5) — verdict fals "toate declaratiile se pot genera".** `lipsuri()` verifica doar PREZENTA, nu
  validitatea -> CAEN 6210 (out-of-enum D112) trecea ca valid. `d112.caen_in_nomenclator` public + `firma_profil_api.blocaje`
  (CAEN->D112; periodicitate/data TVA lipsa la platitor). Verdict in 3 stari. Gard `core/test_profil_blocaje.py`.
  Proba: `citeste_date`(CUBUS) -> blocaje=[D112: CAEN 6210].
- **Q2+Q3 (855608e) — cauza generica peste explicatia precisa + mesaj CAEN fara diacritice.** `control_incrucisat`
  (verifica_d112/tva/d390): ramura noua `elif isinstance(e, ValueError)` -> cauza=str(e) precis, nu genericul (fix #18
  din M2 acoperise doar `PerioadaNeconfirmata`; genericul ramane doar pentru non-ValueError = bug). Mesajele d112 afisate
  -> diacritice. Garzi `core/test_cauza_precisa_business.py`, `core/test_d112_mesaje_afisate.py` (raise ValueError proza
  in d112 are diacritice - unghiul mort al garzii generale test_diacritice_afisate). Proba: verifica_d112(CUBUS) -> cauza =
  mesajul CAEN precis+diacritice, nu "Date lipsa".
- **Q4-Q7,Q10 (65f8bad) — onboarding UX.** Fereastra bun venit: salut inaintea Suportului (Q6), nota UNDE se face fiecare
  pas (Q5), pasi stivuiti + fereastra mai lata 880->920 (Q7). Solduri: model CSV descarcabil (echilibrat), Salveaza blocat
  pe neechilibru cu mesaj INAINTE de click (nu 422 dupa), transparenta conturi noi "se adauga automat" (Q10). Import firme
  in masa (exista deja in Migrare cabinet) facut descoperibil din lista de firme (Q4 - premisa "nu exista" era gresita).
  Gard `core/test_onboarding_ux.py`. Fereastra bun venit **probata Playwright** (cabinet de test real, sters complet dupa,
  zero poluare).


## 16.08.2026 — Parcurgere import CUBUS (raspunsuri 3-16): corectitudine backend + garda pe rol
Loturi 1-2 din campania "repara TOT pe clasa" (2509330->e090166). Detalii + ce ramane: PREDARE_LANT.md.
- Lot 1 (71995e4): Q3 (cheia dnf_luni la verifica_randuri mijloace), Q4 (ramura juridic/fizic asociati),
  Q11 (norma/ore nefabricate salariati - DS cap.17), Q13 (MijlocFixRand fara default 2131). Garda
  core/test_import_backend_corect.py (comportamentala, RED 6/6 pe cod vechi).
- Lot 2 (e090166): mesajele raise ValueError din 6 parsere de import diacriticizate (ajung la user
  via HTTPException(str(e)); scapau garzii generale prin ROL - Q2/Q17). Garda core/test_import_mesaje_afisate.py
  scopata pe fisierele de import (extensia globala ar fi flagrat 159, incl. erori interne legitim ASCII).

## 16.08.2026 — Amortizare pe METODA (Q6+Q15, tura import CUBUS, lot amortizare)
- Patru situri in main.py calculau MEREU liniar ignorand `metoda` din activ: ecranul /mijloace-fixe
  (tenant_mijloace_fixe, afisa cifra ca "amortizat la zi"), nota lunara (tenant_amortizare, 6811/2813),
  casarea (nota_casare_mf) si reevaluarea (nota_reevaluare). Trei INSCRIAU cifra gresita in jurnal /
  in nota contabila (ajunge la ANAF prin balanta/D406), unul o AFISA. Motorul cu 4 metode
  (core/d406_active.py, CF art.28, reconstruit iunie) exista dar NU era chemat de niciunul.
- Reparat: doua functii noi in motor — `amortizat_la_data(mf, la_data)` (cumulat la zi, ecran/casare/
  reevaluare) si `amortizare_luna(mf, an, luna)` (rata unei luni, nota lunara), coerente cu calc_asset
  la granita de an. Toate 4 situri le consuma. Metoda nepermisa pe categorie (alin.5/8^1) -> eroare pe
  rand (ecran: amortizat/ramas None + camp `eroare`) / HTTPException 422 (note), NU liniar tacit (DS cap.17).
  Ultima luna absoarbe rotunjirea -> suma pe viata = valoarea amortizabila EXACT (liniar SI neliniar).
- Garda core/test_amortizare_ecran_metoda.py (15 teste: coerenta motor, suma-pe-viata, endpoint pe DB).
  RED probat pe main.py vechi: activ constructii(212)+degresiva primea 13333.33 LINIAR in loc de eroare;
  activ echipament degresiv primea liniar in loc de degresivul motorului.
- Registru statut adus la zi: FUNCTIONALITATI.csv F036 (D406) afirma "doar amortizare LINIARA
  (degresiva/accelerata neimplementate, xfail)" — FALS din iunie (motorul are 4 metode); corectat.

## 16.08.2026 — Preview = salvare, O SINGURA POARTA (Q5, lot 2)
- Cele 5 endpoint-uri de preview (/incarca) ale straturilor de migrare (parteneri, salariati, asociati,
  mijloace_fixe, istoric) isi luau verdictul din flagurile lui extrage (`cnp_valid`, `ok`) — o A DOUA
  validare care DRIFTA de la `verifica_randuri`, poarta pe care SALVAREA (importa) o ridica la scriere.
  Preview arata "toate valide", userul trimitea, salvarea intorcea 422 pe randuri nesemnalate la preview
  (ex. salariati: preview numara "valizi" doar pe CNP; salvarea respinge si norma/ore/judet/data lipsa).
- Fix STRUCTURAL (nu instanta cu instanta): fiecare preview intoarce `erori = verifica_randuri(...)` prin
  `migrare_api.erori_verifica` (normalizeaza tuplul parteneri vs lista). Frontend `gateazaPreview()`
  blocheaza Salvarea + arata randurile respinse (DS cap.5/6/24). Un singur validator la AMBELE capete.
- Garda core/test_preview_salvare_poarta.py: acelasi fisier prin ambele capete, verdict IDENTIC pe rand;
  randul-drift (extrage OK / verifica_randuri respinge) prins la preview. RED probat pe main.py vechi
  (6/6 KeyError 'erori'). Flagurile lui extrage NU s-au sters (risc consumatori) — nu mai sunt autoritatea
  de validare; daca raman complet nefolosite dupa mutarea frontendului, sunt cod mort de curatat ulterior.

## 16.08.2026 — COR: preview salariati arata denumirea ocupatiei, nu codul (Q16, lot 3)
- Preview-ul de salariati (migrare.js) afisa `r.cor` (codul COR brut) etichetat "Functie". Fix: endpointul
  de preview imbogateste fiecare rand cu `cor_denumire = cor_api.denumire(conn, cod)` (nomenclator
  public.cor_ocupatii); frontendul arata denumirea, cu fallback la cod si codul in `title`. Cod necunoscut
  in nomenclator -> cor_denumire None (necunoscut declarat, regula 4; UI cade pe cod).
- Garda core/test_q16_cor.py (2 teste): endpointul ataseaza denumirea; codul necunoscut ramane None.
  RED probat pe main.py vechi (KeyError 'cor_denumire').
- Cuplaj rezolvat: Q16 adauga `db.get_conn` in endpointul de preview salariati -> gardul Q5
  (test_preview_salvare_poarta) a cerut fake_conn pe cazul salariati (cor gol = fara lookup).

## 16.08.2026 — Cod mort: skip salariati INEXISTENT (tura audit vizual tenant_003)
- salariati_import_api.importa() BLOCHEAZA la primul CNP invalid (verifica_randuri = prima poarta) -> bucla
  `if not cnp_valid: sarite+=1; continue` + `sarite_cnp` erau COD MORT (sarite mereu 0), iar textele "vor fi
  sarite" / "X sariti" (intro + banda + handlerul de salvare salariati) promiteau un skip inexistent.
- Dovada VIZUALA (regula 14, tenant_003 Comert Micro TVA, fisier stricat cu 2 CNP invalide): pe ACELASI ecran
  banda "2 cu CNP gresit (vor fi sarite)" langa caseta "2 randuri nu pot fi salvate" + butonul Salveaza
  DEZACTIVAT -> contradictie. Gateaza-Preview (Q5) a facut contradictia vizibila.
- Reparat: eliminat codul mort (backend) + aliniat textele la adevar (blocheaza, nu sare; DS cap.6).
- Test core/test_d1_import_integritate.py REscris: superseda test_salariati_skip_surfatat_in_ui [citare-istorica: test rescris in aceasta tura, premisa falsa eliminata] (care cerea
  sarite_cnp surfatat - premisa FALSA). Acum: importa ridica pe CNP invalid (block); fara sarite_cnp; fara
  "vor fi sarite". RED probat pe cod vechi (2/3: sarite_cnp prezent + "vor fi sarite" prezent).
- CLASA (regula 13): promisiunea falsa de skip = DOAR salariati. retete/articole "X sarite (existente/
  invalide)" = skip REAL de duplicate (neatins); asociati.importa ridica la fel (fara skip).
- RAMAS (constatare din aceeasi parcurgere, neatins): (Q8) meniuMigrarePerFirma nu are badge de stare per
  strat -> contabilul nu vede ce e importat. Reparatia e BLOCATA pe un semnal de prezenta pt plan_conturi
  (185 conturi standard, fara flag standard/adaugat) -> un badge count>0 ar fi FABRICAT. Cere decizie de
  model (flag "adaugat" sau definirea "plan importat"). (Q12) avertismentul CNP pe rand e doar in title=.

## 16.08.2026 — Reparatii audit vizual tenant_003 (C7, C6, C5); C8 verificat FALS la sursa
- **C7** [CORECTITUDINE, SISTEMIC]: generarea D300/D394/D406 pe firma TRIMESTRIALA pica cu "luna invalida:
  None (astept 1-12)" -> era BLOCATA pentru toate firmele trimestriale de TVA. Cauza: /declaratii/tipuri +
  wizardul folosesc periodicitatea EFECTIVA (tip_decont), dar `valideaza_cerere` folosea periodicitatea
  STATICA (d300=lunar). Frontendul trimite `trim`, validatorul cerea `luna` -> None. Fix intr-un SINGUR loc
  (dispecerul `genereaza` + `valideaza_cerere`): periodicitate efectiva la validare + conversie trim->luna
  ancora (T1->3, T2->6, T3->9, T4->12; generatoarele-s ancorate pe luna, agrega trimestrul; DUK R18). Gard
  core/test_c7_periodicitate_trimestriala.py (6 teste), RED probat pe cod vechi ("luna invalida: None").
  CLASA (regula 13): setul TVA-decont {d300,d394,d406} (_TVA_PERIODIC) - toate 3 prin acelasi dispecer, fix unic.
- **C6** [text fals]: selectorul de declaratii (declaratii.js:89) afisa HARDCODAT 'nu se aplica (partida
  simpla)' pentru orice declaratie neaplicabila (ex. D301/D390 la un SRL, care tine partida DUBLA), iar
  motivul REAL (neaplicabile_selector, corect) era ascuns in title. Fix: optiunea afiseaza `neap` (motivul
  real). CLASA: singura instanta hardcodata in frontend (grep 'partida simpla' -> doar aici in selector).
- **C5** [acord]: 'Profil incomplet - 1 campuri obligatorii lipsesc' (date_firma.js) - plural hardcodat. Fix:
  ramificare singular/plural. Gard core/test_c6_c5_motiv_acord.py (2), RED probat.
- **C8** [VERIFICAT FALS la sursa, NEreparat]: placeholder 'mm/dd/yyyy' la Casa = randarea NATIVA a
  `<input type=date>` in browserul de test (en-US); NU defect de aplicatie: aplicatia NU seteaza placeholder
  (verificat null), foloseste `<html lang=ro>`, input nativ (formatul e controlat de browser, nu de HTML/JS).
  Nimic de reparat (regula 2 - temeiul la sursa a rasturnat constatarea din parcurgere).

- **C1** [audit tenant_003, adevar/DS cap.23]: statul de plata (firme.js) randa starea de PERIOADA "pontaj
  neconfirmat" ca marcaj ROSU per-salariat (cheiat pe tichete>0) + banner ecran-nota rosu - implica fals ca
  un salariat fara marcaj ar avea pontaj confirmat. Fix: banner .caseta-info + semafor gri (o data/luna);
  per-rand "tichete blocate" gri (consecinta reala). Gard core/test_c1_pontaj_neconfirmat_gri.py (2), RED
  probat. CLASA: grep neconfirmat/confirmat+rosu in static/js -> singura instanta; confirmarea (firme.js:669)
  deja conforma; 941/965 gri informativ; asistenti.js:355 self_approval = atentionare reala (nu stare perioada).

- **C2** [audit tenant_003, UX navigare]: dupa salvarea unui strat de import per firma, migrare.js facea
  nav.deschide(<wizard de cabinet>) -> fereastra noua cu toate firmele, in afara firmei; fara mesaj de succes.
  Fix: nav.inapoiPas() (revenire pe traseu la firma) + mesaj verde care supravietuieste revenirea
  (_migMesaj/_consumaMigMesaj, arataMesaj "ok", DS cap.6). Gard core/test_c2_migrare_revenire_firma.py (2), RED
  probat. CLASA (Regula 13): 7 handlere (6 straturi cu randuri + vector fiscal), toate reparate;
  retete/articole/status-save deja conforme.

- **C4** [audit tenant_003, text/model]: "Descarca model (CSV)" doar la solduri (1/9); intro mijloace omitea
  contul de imobilizare/amortizare (citite de parser). Fix: model comun _descarcaModelCSV + MODELE la toate cele
  8 straturi de import cu fisier (format din parser), intro mijloace+articole completate cu conturile. Gard
  core/test_c4_model_csv.py (3), RED probat. Round-trip probat pe mijloace (model descarcat->reincarcat->parsat).
  CLASA: plan_conturi = cautare/adaugare (fara upload), exclus; intro-urile celorlalte coincid cu parserul.

- **INFRA VIZUALA** [17.08.2026, testare vizuala permanenta]: trei unelte pe pagina randata in
  frontend_test/vizual/ (axe_scan/mobil_scan/baseline_scan) + axe.min.js vandorizat (4.10.2) + 5 baseline.
  Gard core/test_infra_vizuala.py (4 teste): pica daca lipseste vreo unealta, axe.min.js (trunchiat sub
  100KB), vreun baseline, sau un ecran din nav_ecrane.ECRANE. Face imposibila disparitia TACUTA a
  infrastructurii vizuale (Regula 6). Probat: cele 4 teste in suita (2251 passed, c83f152).
  **[03.09.2026] A TREIA UNEALTA A FOST SCOASA**: baseline_scan.py + baseline/ (15 capturi) ies din
  repo prin decizie de arhitectura — un baseline imbatraneste prin constructie, iar regenerarea lui
  ca sa treaca il face formalitate. Locul lui in garda il ia interactiune_scan.py, iar garda cere
  acum si directia opusa: mecanismul NU are voie sa reapara. Motivul intreg: METODA_VERIFICARE.md
  §27; registrul: CONFORMITATE.md, sectiunea capturilor de referinta.

- **VERDICT CONTROL FISCAL — DIACRITICE + FARA NUME INTERN** [17.08.2026, audit vizual tenant_004]:
  gard core/test_control_fiscal_diacritice.py (2 teste) — mesajele de verdict (neclar/neaplic/datorate) din
  control_fiscal_api.py au diacritice si NU scurg nume interne de camp. Acopera PUNCTUL ORB al gardului canonic
  (test_diacritice_afisate.py, roluri: detail HTTPException / dict-display-keys / corpuri de exceptii): args
  pozitionale la gri()/neaplic()/emite_tva(), valori _NEAP_FORMA_SIMPLA, variabile-mesaj (cauza_r), return-uri
  builder (_existenta_fapt). RED probat pe cod vechi (13 mesaje fara diacritice + scurgere platitor_tva_anaf_inceput);
  GREEN dupa fix. Vezi DS cap.20 + DECIZII 17.08.
- **DATORIE DESCHISA — erori de generare declaratii fara diacritice** [17.08.2026, masurat, NEreparata]: scan AST
  core/ (raise-inline + append la liste-mesaj) da ~218 candidati; NU toti sunt defecte (multe = erori DEVELOPER,
  legitim ASCII per criteriu). Clasa REALA = erorile afisate CONTABILULUI la generarea declaratiilor
  (d100/d101/d112/d205/d119/bilant_api: "corecteaza in fisa", "declaratia ar fi respinsa", nume XSD interne
  scurse "(cifR)"/"(den1)"). Distinctia user-facing-pe-ecran vs eroare-developer NU e mecanica -> nereparata (un
  fix fara gard ar incalca Regula 6). De facut: gard care distinge (module de generare dXXX, mesaje prefixate
  "Dxxx:") + diacriticizare + inlocuit numele XSD interne cu descriere umana. Enumerare in raportul 17.08 §5.

## 17.08.2026 - Reconciliere D100 pe semafor REPARATA [audit tenant_002]
- DEFECT gasit pe ecranul Control fiscal (evalueaza_firma -> reconciliere_surse): _thunk_d100 din
  control_incrucisat.py despacheta `prof, venituri = pull(...)` dar d100.pull intoarce 3 (prof, venituri,
  cheltuieli, de la profit-base-fix 16.08). ValueError "too many values to unpack" pe ORICE firma ->
  _ruleaza_una PASUL 1 il clasifica GRI (nu rosu rupt, cum cere clasa "deriva de semnatura"), cu textul
  Python scurs in motiv. Plasa a-doua-cale D100 MOARTA universal (micro t002 + profit t004). Latent: ramura
  profit calcula cota pe VENITURI (nu pe profit) -> rosu fals daca s-ar fi reparat doar aritatea. REPARAT:
  extras d100.deriva_obligatii (sursa unica) chemata de genereaza SI de thunk -> nu mai poate drifta (aritate
  + formula). Gard core/test_reconciliere_d100_wiring.py (RED micro+profit -> GREEN). Vezi DECIZII/TESTE 17.08.

## 17.08.2026 - Bilant S1005/S1003 REFUZA fara reg_com (poarta completata) [audit tenant_002]
- DEFECT provocat pe Date firma (reg_com=None -> UI: "blocheaza Bilant S1005"): bilant_api.erori_generare
  verifica doar cui+nume, deci genereaza emitea S1005 FARA regCom (respins de DUK: "regCom: atributul trebuie
  sa existe") in loc sa refuze - promisiunea UI "blocheaza" era falsa, iar poarta (docstring "nu XML respins de
  ANAF") isi rata exact scopul. REPARAT: reg_com adaugat in erori_generare (partajata S1005+S1003) -> refuz cu
  mesaj clar. Sursa: DUKIntegrator -v S1005 (reguli 2026.1). Gard core/test_bilant_regcom_poarta.py (RED
  S1005+S1003 nu ridicau -> GREEN). Vezi DECIZII/TESTE 17.08.

## 17.08.2026 - Default fabricat pe selecturile vector din Date firma [audit tenant_001]
- DEFECT provocat pe Date firma (regim_fiscal/platitor_tva/operatiuni_ic = NULL): selectul obligatoriu FARA
  optiune-goala afisa prima optiune (Microintreprindere / Nu) ca aleasa; la Salvare frontendul trimitea valoarea
  fabricata iar backend salveaza facea bool(platitor_tva) -> None coerce tacit la False, persistat. Semaforul
  (NULL=necompletat) si Date firma (micro/Nu) dadeau verdicte care nu coincid (Regula 14.2); alegere fabricata
  scrisa fara ca contabilul s-o faca (Regula 4). REPARAT (2 jumatati): backend respinge platitor_tva=None
  (TVA_LIPSA, simetric cu operatiuni_ic care era deja corect); main VectorIn.platitor_tva Optional; citeste()
  expune partida_simpla. frontend date_firma.js: alege:true + placeholder alege + tri-stare + validare preventiva
  langa camp. Garzi test_vector_platitor_tva_oblig + test_date_firma_alege_placeholder (RED pe cod vechi -> GREEN).
  Comit 59f4fec. Vezi DECIZII/TESTE/ISTORIC 17.08.

## 17.08.2026 - IBAN lipsa din importul de salariati + blocaj SEPA/REGES doar prin title [audit tenant_001]
- (a) importul (stratul 4 migrare) NU aducea IBAN (nici parser, nici writer, nici model CSV) -> orice firma migrata
  avea iban=NULL pe toti salariatii -> fisierul SEPA ii excludea pe toti. COR era deja mapat (test_q16). REPARAT:
  mapare + validare mod-97 + INSERT (UPSERT cu COALESCE, nu sterge IBAN manual la re-import) + model CSV cu cor,iban.
  (b) butoanele dezactivate SEPA / Raspunsuri REGES livrau motivul DOAR prin title (invizibil pe touch - Regula 14
  addendum) -> motiv VIZIBIL prin .caseta-info (DS cap.5). Garzi test_salariati_import_iban + test_salariati_blocaj_
  vizibil (RED->GREEN). Comit a62f46b. axe/mobil Stat plata: title_only STRICT 0; PRE-EXISTENT semnalat: contrast 19
  noduri + 160 tinte <44px + overflow-x False.

## 17.08.2026 - FRONT DESCHIS: podea part-time D112 - 3 pozitii contradictorii (CERCETAT, REVENIT) [audit tenant_001]
- Podeaua de suprataxare part-time (art.146(5^6) CAS / art.168(6^1) CASS) e calculata in TREI locuri cu TREI valori:
  salarizare.baza_podea (fluturas) = sm-facilitate LUNAR (3750 H1 / 4125 H2); d112.pull:680 + d112_reconciliere:182
  = sm INTEGRAL (fix 06.08, 4050 H1 / 4325 H2); DUK (SP1B4_1) + structura ANAF (d112_struct_anaf.txt "sm=4050;
  sm=sm-300") = 3750 FIX pe an (ref 1 ian), verificat pe DUKIntegrator iunie SI august. Decizia 06.08 (4050) e
  DELIBERATA, aparata cu art.LXVI in DOUA teste (test_pull_declaratii.py:634 + test_d112_reconciliere.py:307). Am
  incercat 2 fix-uri (sm-fac lunar; ref-ianuarie 3750) - ambele contrazic teste deliberate cu temei legal. NU e
  defect de calcul CLAR -> REVENIT la HEAD. Cere autoritate externa (ANAF/consultant): period-aware vs ref-ianuarie,
  si de ce fluturas != D112 azi. Analiza completa + probe DUK in PREDARE_LANT FRONT #1.

## 17.08.2026 - declarant fabricat "ADMINISTRATOR" tacit pe toate declaratiile [audit tenant_001, thread 3]
- declarant_nume/prenume/functie erau CAMPURI_FISCALE dar NU in OBLIGATORII -> ecranul Date firma nu le cerea,
  iar d100/d101/d205/d112/d300 + bilant emiteau "ADMINISTRATOR" fabricat TACIT cand lipseau (d301/d390 avertizau
  deja). Declaratii semnate de un declarant inventat -> ANAF (Regula 4). REPARAT in 2 jumatati: (1) declarant_nume
  + declarant_functie in OBLIGATORII + ob:true in date_firma.js (se cere EXPLICIT, ca regim_fiscal; salveaza_date
  valideaza; comit 7aef45e); (2) toate generatoarele AVERTIZEAZA cand declarantul lipseste - XML NESCHIMBAT
  (fallback tot ADMINISTRATOR, DUK respinge campul gol; comit ae5bced). declarant_prenume ramane optional
  (fallback "-" legitim). Garzi test_declarant_oblig + test_declarant_warn (RED->GREEN). Vezi DECIZII/ISTORIC 17.08.

## Import salariati — salariu de baza obligatoriu (17.08.2026)

- **Gard:** `core/test_import_migrare.py::test_salariu_brut_lipsa_e_respins` + `::test_salariu_brut_negativ_e_respins`.
- **Ce face imposibil:** un import de salariati cu salariu de baza lipsa/0/negativ sa intre tacit (baza 0 -> suprataxa angajatorului pe podeaua sub-minim, Stat de plata incoerent). `verifica_randuri` respinge (motiv `salariu_lipsa`).
- **Mutatie proba:** `git stash push -- core/salariati_import_api.py` -> testele pica (verifica_randuri intoarce []); pop -> verzi. Rulat 17.08.2026.

## Stat de plata — semnal baza contractuala lipsa (17.08.2026)

- **Gard:** `core/test_salariu_scrieri.py::test_stat_plata_semnaleaza_baza_lipsa` (+ `::test_editarea_salariului_prin_put_dateaza_istoricul`).
- **Ce face imposibil:** ca `stat_plata` sa intoarca un salariat cu baza contractuala 0/lipsa FARA flag `baza_lipsa` (ecranul ar afisa cost 825 din suprataxa sub-minim tacit). Cardul semnaleaza in rosu + ofera butonul „Salariu” de corectie.
- **Mutatie proba:** `git stash push -- core/stat_plata_api.py` -> `KeyError: 'baza_lipsa'`; pop -> verde. Rulat 17.08.2026.

## Import articole — stoc fara pret (17.08.2026)

- **Gard:** `core/test_import_migrare_valideaza.py::test_articole_stoc_fara_pret_e_invalid`.
- **Ce face imposibil:** un articol cu cantitate > 0 si pret 0/lipsa sa intre cu valoare 0 (CMP 0, stoc sub-raportat). `extrage` il marcheaza invalid; preview-ul il arata rosu cu motiv; nu se importa.
- **Mutatie proba:** `git stash push -- core/articole_import_api.py` -> articolul fara pret = valid (test pica); pop -> verde. Rulat 17.08.2026.
## Mesaje user-facing fara nume intern de camp (17.08.2026)

- **Gard:** `core/test_mesaje_fara_camp_intern.py`.
- **Ce face imposibil:** un mesaj user-facing (mesaj/eroare/detail, prin rol sintactic) sa contina un token snake_case = nume intern de camp/coloana (`tip_decont`, `regim_fiscal`, `tenant_id`...). Baseline 0; 2 exceptii temei-diagnostic (bug de cod) cu motiv in _BASELINE.
- **Mutatie proba:** reintrodus `tip_decont trebuie...` in vector_fiscal_api -> gardul pica; restaurat -> verde. 17.08.2026.

## Vector fiscal per-firma: periodicitate legacy + pre-completare (17.08.2026)

- **Gard:** `core/test_tip_decont_lung.py` (contract primitiva + integrare citeste/portal + clamp B1).
- **Ce face imposibil:** (B2) un cod legacy `L`/`T` din tip_decont sa ajunga BRUT la UI (formularul ar arata periodicitatea neselectata); normalizat la forma lunga prin common.tip_decont_lung la citeste + portal. (B1) ca formularVectorFirma sa nu mai incarce vectorul salvat (/vector) si sa apara gol pe traseul per-firma.
- **Mutatie proba:** citeste raw (fara tip_decont_lung) -> `T` scapa la UI, testul pica; scos fetch-ul /vector din formularVectorFirma -> clampul pica. Ambele restaurate. 17.08.2026.

## REZIDUU UX/a11y neridicat (audit tenant_005, 17.08.2026) — pentru cluster a11y dedicat

- Eroarea de la formularul Vector NU marcheaza campul vinovat cu contur (doar cutie generica jos; mesajul il numeste acum). Pattern app-wide (Regula 14 pct.4).
- axe pe ecranul Vector: 15 noduri color-contrast (serious) + 17 tinte <44px + 2 info livrata EXCLUSIV prin `title` (pierduta pe touch). Pre-existent, app-wide.
## Diacritice pe mesajele validatorilor de import (17.08.2026)

- **Gard:** `core/test_diacritice_afisate.py::test_validatori_import_cu_diacritice` + 14 triggere noi.
- **Ce face imposibil:** un mesaj afisat de un validator de import (raise/mesaj/motiv/f-string/avertismente.append) fara diacritice. Scanare INTEGRALA a celor 8 fisiere-validator (integral user-facing), exclus _gaseste_col + SQL.
- **Mutatie proba:** avertisment `"durata lipsa"` in mijloace -> gardul pica; restaurat -> verde. 17.08.2026.

## Plan de conturi: model de body clasificat ca query (17.08.2026)

- **Gard:** `core/test_rute_model_body.py`.
- **Ce face imposibil:** un param tipat cu BaseModel sa fie clasificat de FastAPI ca query (model definit DUPA handler cu future annotations -> request pica cu 422). Prinde clasa app-wide.
- **Mutatie proba:** PlanContIn mutat inapoi dupa handler -> gardul flagheaza param 'date' tip PlanContIn ca QUERY; restaurat -> verde. 17.08.2026.
## Diacritice generatoare declaratii (17.08.2026) + BACKLOG sistemic

- **Gard:** `core/test_diacritice_afisate.py::test_generatoare_declaratii_cu_diacritice` (_GEN_DECLARATII).
- **Ce face imposibil:** mesaj-proza fara diacritice intr-un generator din _GEN_DECLARATII (azi: d205).
- **BACKLOG (~330 mesaje, ~50 fisiere):** d100/d101/d112/d300/d301/d390/d394/d406/d107/d177/d207/bilant_api/declaratii_api + extins d104-d710 - fara diacritice (raise/er.append/avertisment). Se curata cate un fisier, se adauga in _GEN_DECLARATII. Campanie dedicata. Unele scapa si nume de camp (Regula 14 pct.4).
- **Mutatie proba:** mesaj d205 integral ASCII -> gardul flagheaza; restaurat -> verde. 17.08.2026.

## Front E: editarea identitatii salariatului din UI (17.08.2026)

- **Gard:** `core/test_front_e_editare_identitate.py`.
- **Ce face imposibil:** backendul sa nu mai accepte nume/CNP/data_angajare/tip_norma (contract SalariatEdit+_CAMPURI_API), SAU UI-ul sa piarda cablarea editarii (data-date/ed-cnp/cnpValid in firme.js).
- **Mutatie proba:** data-date -> data-XXXX in firme.js -> clampul UI pica; restaurat -> verde. 17.08.2026.
## [ACTUALIZARE 17.08.2026] Diacritice generatoare declaratii — BACKLOG INCHIS

Backlog-ul de ~330 mesaje pe ~50 fisiere (deschis mai sus) e ACUM INCHIS: toate 58 fisierele in _GEN_DECLARATII, gardul verde pe toate. Diacriticizat cu ~/probe_t005/diacriticize.py (reutilizabil). Commit 09010f7.
## a11y: contrast token-uri WCAG AA (17.08.2026)

- **Gard:** `core/test_a11y_contrast_tokens.py` (browser-free, recalcul contrast din sursa).
- **Ce face imposibil:** un token de culoare (--albastru; .camp-ajutor; CULORI_CARD fg/bg) sub 4.5:1 fata de fundalul/textul lui.
- **Mutatie proba:** --albastru->#3d8fd6 -> gardul pica (alb pe el 3.44); restaurat -> verde.
- **RAMAS (nou GAP):** butoanele nav 30-36px = AA(24) dar nu AAA(44); .btn-link #3d8fd6 literal de verificat pe alb. Cluster field-level error marking inca deschis.

## existenta_firma_an: activitate = orice operatiune datata (18.08.2026)

- **Gard:** `core/test_existenta_activitate.py` (4 teste, schema temporara, DB).
- **Ce face imposibil:** existenta_firma_an sa ignore d301_operatiuni / casa_operatiuni / extras_linii intr-un an cu operatiuni datate (ar contrazice restanta D301 pe acelasi ecran, Regula 14 pct.2).
- **Mutatie proba:** pe cod vechi (doar facturi/salariati/note) `test_d301_operatiuni_e_activitate_demonstrabila` pica (existenta 2026 = False cu 1 d301 op, 0 facturi); dupa fix = True. Rulat RED prin pytest inainte de reparatie.
- **RAMAS (limita declarata):** euristica e la granularitate de AN, nu de trimestru — o firma cu activitate doar in T2 arata si restanta D100 T1 (nu suprimata). Pre-existent, nu introdus de fix.

## Fronturi deschise audit tenant_006 (18.08.2026) — vezi PREDARE_LANT.md

- **A11Y CONTRAST Control fiscal (NEreparat, gata de atacat):** axe = 17 violari color-contrast (serious), 2 tokeni pe panoul #e9edf3: `--albastru #347ab8` (coduri declaratii `.mig-sold-cont`, 3.87:1) + `--gri-semafor #9aa3b2` (`.cf-incr-temei`, 2.16:1). Tinte verificate: #2f6fa6 (4.53) blue scoped, #5c6675 (4.95) gri. Ecranul Control fiscal NU era in auditul a11y tenant_005 (dashboard/vector/salariati). Plus axe "region" 17.
- **D390 ignora d301_operatiuni (DECIZIE CERUTA):** d390.genereaza refuza "pe zero" desi exista achizitie IC in d301_operatiuni; D390 citeste facturi, nu d301 (acelasi tipar ca existenta). Latent (D390 gri cat timp art.317 nemarcat). Cere temei (relatia D301<->D390 la neinregistratii art.316) + scenariu art.317=da.
- **D100 pe zero (OBSERVATIE, pre-existent universal):** micro fara venituri vede D100 restanta pe semafor dar generatorul refuza "pe zero". Comun tuturor micro (tenant_002/003), nu introdus de fix-ul existenta. Relatia semafor<->generator pe zero = de clarificat.

## D100 micro pe fapt de venituri: d100_fapt (18.08.2026)
- **Gard:** `core/test_d100_fapt.py` (5 teste pure pe obligatii_datorate).
- **Ce face imposibil:** semaforul sa arate D100 micro restanta pe un trimestru INCHIS fara venituri (D100 pe zero = structural invalid la DUK, ar dead-end la generator).
- **Mutatie proba:** dezactivarea portii (`is False` -> `if False`) -> test_d100_fapt_fara_venituri_suprima_restanta pica (restantele [2025-12,2026-3,2026-6] reapar). Restaurat -> 5 passed.

## a11y contrast Control fiscal: 2 perechi pe #e9edf3 (18.08.2026)
- **Gard:** `core/test_a11y_contrast_tokens.py` (extins: test_cf_incr_temei + test_cf_coduri_declaratii, recalcul contrast pe #e9edf3).
- **Ce face imposibil:** `.cf-incr-temei` sau codurile `.cf-*.mig-sold-cont` sa scada sub 4.5:1 pe panoul Control fiscal.
- **Mutatie proba:** culorile rele (#9aa3b2 / #347ab8) in stil.css -> 2 failed; restaurat -> 5 passed.
- **RAMAS:** axe "region" (landmark lipsa) 8-19 noduri app-wide (moderat, structural). D406 avertisment conturi 731-738 excluse din norma A (neverificat la sursa).

## Field-level error marking: marcaj pe input (18.08.2026)
- **Gard:** `core/test_fieldmark.py` (eroareCamp adauga camp-invalid+aria-invalid; curataEroriCamp o scoate; CSS override input.camp-invalid invinge bordura globala).
- **Ce face imposibil:** eroareCamp sa lase inputul nemarcat (doar mesaj) sau overrideul CSS sa dispara (bordura ar ramane gri sub `!important`-ul global).
- **Mutatie proba:** scot classList.add("camp-invalid") din api.js -> test_eroareCamp_marcheaza_inputul pica.
- **RAMAS:** front D390<->d301 = decizie (d301 n-are TVA partener pt cod A); axe "region" landmarks app-wide; D406 conturi 731-738.

## D390 pe zero semnaleaza d301 (front 2, 18.08.2026)
- **Gard:** `core/test_d390_d301_semnal.py` (achizitii_d301 numara operatiunile d301; refuzul tenant_006 semnaleaza d301 + indruma manual).
- **Ce face imposibil:** D390 sa refuze "pe zero" cu mesaj generic cand D301 are achizitii in perioada (ar duce la omiterea D390 pentru un art.317).
- **Mutatie proba:** bypass ramura d301 (`_d301 = 0`) -> mesajul tenant_006 devine generic -> test pica.
- **RAMAS:** auto-derivare d301->D390 = decizie (recomandare NU); axe region/landmarks app-wide; D406 conturi 731-738.

## Auto-derivare d301->D390 cod A/S (18.08.2026)
- **Gard:** `core/test_d390_autoderivare.py` (mapare tip->cod + filtrul tarii; cele doua cai generator/reconciliere coincid). Plus test_audit_schema (coloanele partener pe toate schemele).
- **Ce face imposibil:** o cale (generator sau reconciliere) sa ignore d301 sau sa driftreze maparea -> gardul de reconciliere ar bloca fals, sau achizitia ar disparea din D390.
- **Mutatie proba:** _D301_TIP_COD 1->S in reconciliere -> cele doua cai difera -> test_cele_doua_cai_coincid pica.
- **RAMAS:** tip 2/4 excluse din auto-derivare (clasificare manuala); codul TVA furnizor validat de checksum_vies la generare (cod invalid -> DUK R24.1). axe region landmarks; D406 731-738.

## tip 3 -> cod A verificat + avertisment d301 rafinat (18.08.2026)
- **Gard:** `core/test_d390_autoderivare.py::test_achizitii_d301_numara_doar_mapabile_fara_tara` + test_mapare (tip 3 -> A).
- **Ce face imposibil:** achizitii_d301 sa numere tip 2/4 (avertisment fals "lipseste tara") sau sa scape tip 1/3/5 fara tara.
- **Temei verificat:** OPANAF 394/2017 anexa 2 - cod A = achizitii IC de bunuri fara excludere accizabile; DUK valid pe tip 3 (bazaA) si tip 5 (bazaS).

## tip 4 exclus din D390 verificat la sursa + nota UI (18.08.2026)
- **Gard:** `core/test_d390_autoderivare.py::test_mapare_tip_cod_si_filtrul_tarii` (tip 4 cu tara NU apare in output).
- **Temei verificat:** CF art. 307 alin.(3)(5)(6) = gaz/energie / bunuri din regim suspensiv / taxare inversa locala generala -> niciuna IC -> exclus din D390 corect.
- **Efect:** grila D301 clarifica tip 2/4 ("nu intra in D390 — ...") chiar cu furnizor.

## Mis-clasificare tip 4 -> indiciu tip 5 (18.08.2026)
- **Gard:** `core/test_d390_autoderivare.py::test_d390_posibil_serviciu_semnaleaza_tip4_cu_cod`. [citare-istorica: mecanism confirma_local/euristica inlocuit de temei_307, 19.08.2026]
- **Ce face imposibil:** d390_posibil_serviciu sa se aprinda pe alt tip decat 4, sau sa rateze tip 4 cu cod.
- **Mutatie proba:** scot conditia tip==4 -> tip 5 cu cod semnalat -> testul pica.
- **Limita:** indiciu SOFT (gaz/energie alin.3/5 cu furnizor inregistrat da fals-pozitiv benign; contabilul confirma).

## Confirmare "nu e serviciu IC" stinge indiciul tip 4 (18.08.2026)
- **Gard:** `core/test_d390_autoderivare.py::test_confirma_local_stinge_indiciul_reversibil` + test_audit_schema (coloana d390_confirmat_local). [citare-istorica: mecanism confirma_local/euristica inlocuit de temei_307, 19.08.2026]
- **Ce face imposibil:** lista sa ignore confirmarea (indiciul ramane pe operatiunile confirmate legitime).
- **Mutatie proba:** scot `and not r["d390_confirmat_local"]` din lista -> indiciul ramane True dupa confirmare -> testul pica.

## Confirmare persistenta per-furnizor (18.08.2026)
- **Gard:** `core/test_d390_autoderivare.py::test_confirmare_per_furnizor_persista_intre_luni`. [citare-istorica: mecanism confirma_local/euristica inlocuit de temei_307, 19.08.2026]
- **Ce face imposibil:** confirmarea unui furnizor sa NU se aplice viitoarelor operatiuni de la el (contabilul ar re-confirma lunar).
- **Mutatie proba:** scot verificarea `... not in _furnizori_conf` din lista -> op-ul din alta luna ramane semnalat dupa confirmarea furnizorului -> testul pica.

## a11y contrast .btn-link + dec-xml summary (18.08.2026)
- **Gard:** `core/test_a11y_contrast_tokens.py` (test_btn_link + test_dec_xml_summary, recalcul din sursa pe alb + #e9edf3).
- **Ce face imposibil:** .btn-link sau .dec-xml summary sa scada sub 4.5:1 (butoane-link app-wide + toggle D301).
- **Mutatie proba:** #2f6fa6 -> #3d8fd6 in .btn-link -> pica pe ambele fundaluri.
- **RAMAS:** axe "region"/landmarks (26 noduri, app-wide, front separat); butoanele-link 18px inaltime = excepatia inline WCAG 2.5.8.

## Formular manual D710: gol nu produce declaratie (18.08.2026)
- **Gard:** `core/test_d710_formular.py` (gol -> refuz cu mesaj de contabil; toate sumele 0 -> refuz; o obligatie valida -> genereaza).
- **Ce face imposibil:** un formular D710 gol sa produca un XML (respins tacit de DUK) in loc de un mesaj clar.
- **Mutatie proba:** dezactivez `if not res.obligatii` in d710.genereaza -> gol produce XML -> testul pica.
- **Mesaj de contabil:** verificat ca NU expune nume interne (obligatii/suma_dat_i/cod_oblig).

## Formular manual D311: gol nu produce declaratie (18.08.2026)
- **Gard:** `core/test_d311_formular.py` (gol -> refuz cu mesaj de contabil; data+motiv completate dar toate sumele 0 -> refuz "nu se depune pe zero"; completat -> genereaza). `core/test_d311.py` extins cu asertia no-nume-interne pe erori_generare.
- **Ce face imposibil:** un formular D311 gol (fara data anularii / motiv / sume) sa produca XML respins tacit de DUK in loc de mesaj clar; SI ca mesajul sa expuna nume interne XSD (Data_A/d_anul1/OB_51).
- **Mutatie proba:** sed reintroduce "OB_51+OB_52" in mesajul de zero din d311.py -> test_d311_fara_sume_refuza pica pe scurgerea numelui intern (rulat RED, restaurat GREEN).
- **Mesaj de contabil:** verificat ca NU expune Data_A/d_anul1/d_anul2/OB_*/manual.

## Formular manual D307: gol nu produce declaratie (18.08.2026)
- **Gard:** `core/test_d307_formular.py` (nicio operatiune -> refuz; operatiune fara tip/denumire/cod -> refuz; o operatiune valida -> genereaza). `core/test_d307.py` extins cu asertia no-nume-interne pe erori_generare.
- **Ce face imposibil:** un formular D307 gol (nicio operatiune) sa produca XML respins tacit de DUK; SI ca mesajul sa expuna nume interne (denO/codO/operatiuni/d_anulare).
- **Mutatie proba:** sed reintroduce "denO" in mesajul de denumire lipsa din d307.py -> test_d307_operatiune_incompleta_refuza pica (rulat RED, restaurat GREEN).

## Strat import FIRME: intrarea ne-CUI nu dispare în tăcere (18.08.2026)
- **Gărzi:** `core/test_separa_cui.py` (4 teste, pure) + `core/test_migrare_ignorate_vizibil.py` (ratchet sursă: rută + frontend).
- **Ce face imposibil:** o intrare fără nicio cifră (typo „ABC", antet de coloană, un token din „vezi lista") să fie curățată la gol și eliminată înainte de ANAF fără niciun semn (Regula 4 — fără default tăcut; Regula 14.4 — spune care dată și de ce). `anaf_api.separa_cui()` întoarce explicit `(curatate, ignorate)`; ruta `/migrare/valideaza` întoarce `ignorate`; `migrare.js` randează banner VIZIBIL `.mig-avert` (role=status, NU title-only — pierdut pe touch).
- **Mutație probă:** pe cod vechi (fără `separa_cui`) cele 7 aserții pică (AttributeError + rută/frontend fără „ignorate"); după fix = 7 passed. Rulat RED prin pytest înainte de reparație.
- **Probă live (Playwright, tenant_006):** lipit „14837428 / ABC / vezi lista / 12-34" → 2 rânduri verificate (BORG DESIGN SRL găsit, CUI 1234 negăsit) + banner „3 intrări nu conțin un CUI și au fost ignorate: „ABC", „vezi", „lista". Un CUI are doar cifre — verifică dacă lipsește vreo firmă." axe=0, mobil body=393px (fără scroll orizontal), banner vizibil. Cifrele se leagă (Regula 14.2): 5 token = 2 verificate + 3 ignorate.
- **RĂMAS (straturi import încă neprobate individual):** vector_fiscal, solduri_parteneri (cont nepartener / CUI invalid), plan_conturi (simbol/denumire gol/duplicat).

## Strat import PLAN DE CONTURI: adaugarea manuala nu suprascrie tacut un cont existent (18.08.2026)
- **Gard:** `core/test_plan_conturi_no_upsert.py` (3 teste, ratchet pe sursa handler-ului).
- **Ce face imposibil:** ruta manuala `POST /tenants/{id}/plan-conturi` sa faca `INSERT ... ON CONFLICT (simbol) DO UPDATE` — un contabil care „adauga" simbolul `101` cu alta denumire REDENUMEA tacut contul OMFP standard „Capital" (seed-uit la crearea firmei), fara avertisment (corupere de date; Regula 4 — fara default tacut). Calea bulk (`solduri_api`) folosea deja corect `ON CONFLICT DO NOTHING`; doar calea manuala era outlierul. Acum: verifica existenta, refuza cu 409 „Contul X exista deja in plan: «denumire»…" (Regula 14.4 — ce + unde se corecteaza), NU suprascrie.
- **Mutatie proba:** pe cod vechi (`DO UPDATE` prezent, fara `SELECT` de existenta) 2 aserții pica; dupa fix = 3 passed. Rulat RED prin pytest inainte de reparatie.
- **Proba live (Playwright, tenant_006):** adaugat simbol duplicat „101" cu denumirea „TEST NU TREBUIE SA SUPRASCRIE" → eroare VIZIBILA „Contul 101 exista deja in plan: «Capital»…"; cautarea „101" arata in continuare „Capital" (NU denumirea injectata) → contul standard neatins. axe=0, mobil body=393px.
- **RAMAS pe stratul plan_conturi (14.4 pct.4, cluster field-marking deschis app-wide):** obligativitatea simbol+denumire se semnaleaza abia la apasarea butonului (buton mereu activ), iar eroarea de camp gol nu marcheaza CARE input lipseste. Acelasi tipar ca la Vector (GARZI mai sus). De atacat in clusterul field-level error marking.

## Vector fiscal: eroarea de camp obligatoriu MARCHEAZA campul vinovat (19.08.2026)
- **Gard:** `core/test_vector_camp_marcat.py` (5 teste: 3 unit pe `salveaza()` - erorile pre-DB - + 2 ratchet rută/frontend).
- **Ce face imposibil:** refuzul de câmp obligatoriu la vectorul fiscal (plătitor TVA fără periodicitate decont; `operatiuni_ic` neales; regim la partidă dublă) să arate DOAR un mesaj generic jos, fără să marcheze grupul vinovat (Regula 14.4 pct.4 - „eroarea care nu marchează câmpul vinovat"). `salveaza()` întoarce acum `camp` lângă `cod`; ruta `/tenants/{id}/vector` îl expune ca `erori_campuri:[{camp,mesaj}]`; `migrare.js` marchează grupul (#vf-regim/#vf-tva/#vf-decont/#vf-ic) cu `.camp-invalid` (box-shadow roșu, generic pe orice element) + `aria-invalid`, și curăță marcajele la fiecare încercare.
- **Mutație probă:** pe cod vechi (fără `camp`) cele 5 aserții pică (salveaza nu întoarce camp; rută/frontend fără erori_campuri); după fix = 5 passed. Rulat RED prin pytest.
- **Probă live (Playwright, tenant_001 - firmă FĂRĂ vector):** micro + TVA=Da + IC=Nu, decont GOL → salvare RESPINSĂ (400, nicio scriere: tenant_001 rămâne None,None,None,None); mesaj „Periodicitate decont TVA: alege Lunar sau Trimestrial (obligatoriu la plătitor de TVA)" + grupul decont cu contur ROȘU (aria-invalid=True, captură privită). axe 0.
- **RĂMAS (cluster field-marking app-wide):** același tipar poate exista în alte formulare cu grupuri de butoane / selecturi care nu folosesc `erori_campuri`. De măturat formular cu formular (mecanism: `api.js` `marcheazaCampInvalid` + `detail.erori_campuri`).

## Plan de conturi (Adauga cont): camp gol marcat + obligativitate INAINTE de buton (19.08.2026)
- **Gard:** `core/test_plan_form_fieldmark.py` (4 teste, ratchet pe sursa).
- **Ce face imposibil:** formularul „Adaugă cont" să semnaleze obligativitatea abia DUPĂ apăsarea butonului (buton mereu activ, mesaj generic „Simbol și denumire sunt obligatorii" fără să marcheze CARE câmp) — Regula 14.4 pct.4. Acum: asterisc `.oblig` pe etichetă (obligativitate ÎNAINTE de buton) + `aria-required`; la submit gol, câmpul/câmpurile lipsă marcate cu `.camp-invalid` + `aria-invalid`, mesaj care numește exact ce lipsește (simbol vs denumire); duplicatul (409) marchează simbolul.
- **Mutație probă:** pe cod vechi (asterisc absent, mesaj generic, fără marcaj) 4 aserții pică; după fix = 4 passed. Rulat RED prin pytest.
- **Probă live (Playwright, tenant_006):** ambele goale → „Completează simbolul și denumirea contului." + ambele câmpuri cu contur roșu; doar simbol completat → „Completează denumirea contului." + DOAR denumirea marcată. axe 0 (captură privită).
- **Perimetru curat:** aceasta era ultima datorie de field-marking ÎN perimetrul stratului plan_conturi (tenant_006). Rămâne doar tiparul în ALTE formulare neatinse (pattern app-wide, NU datoria firmei curente — vezi regula §5-goală).

## a11y: corpul modal .fereastra-corp focusabil din tastatura (mobil, 19.08.2026)
- **Gard:** `core/test_fereastra_focusabila.py` (ratchet: ambele `.fereastra-corp` din navigator.js au `tabindex`).
- **Ce face imposibil:** shell-ul modal partajat `.fereastra-corp` sa fie scrollabil dar nefocusabil din tastatura (axe `scrollable-region-focusable`, WCAG 2.1.1) - iesit pe Pixel 5 (393px) la preview-ul de parteneri, unde continutul depaseste viewportul. Fix o data in navigator.js = app-wide (toate ecranele modale).
- **Mutatie proba:** pe cod vechi (fara tabindex) garda pica; dupa fix = 1 passed. RED prin pytest. Re-probat live mobil: axe pe preview parteneri 0 (era scrollable-region-focusable).
- **Lectie infra (RAMAS, out-of-perimeter):** axe_scan.py = desktop-only, mobil_scan.py nu ruleaza axe -> de adaugat un pas axe-pe-mobil in infra vizuala (prinde clasa asta de violari care apar doar cand continutul overflow-uieste).

## Metoda ca POARTĂ: scan interactiune+a11y gardat pe diff (19.08.2026)
- **Gard:** `core/test_acoperire_vizuala.py` (3: scan proaspat / toate ecranele scanate / fara violari).
- **Ce face imposibil:** o schimbare de UI (`static/js/**.js` + `stil.css`) sa fie comisa fara un scan vizual+interactiune PROASPAT si CURAT. Cupleaza mecanic diff-ul de scan: `ui_hash` stale -> pica; orice violare gasita de scan (axe desktop/mobil, tinta<24 AA, overflow/aliniere la completarea casetelor, erori JS la apasarea butoanelor, layout rupt, title-only) -> pica. Instrument `frontend_test/vizual/interactiune_scan.py` (browser, out-of-band ca `versioneaza_assets --scrie`) -> `acoperire_vizuala.json`. Hash + lista ecranelor in `acoperire_hash.py` (pur, importat de tool SI de gard, fara drift).
- **Mutatie proba:** (a) atins un fisier UI -> `test_scan_proaspat` pica (ui_hash difera); (b) violare injectata in artefact -> `test_fara_violari` pica. Ambele RED prin pytest, apoi restaurat GREEN.
- **De ce:** o regula scrisa si citita NU e o regula pazita — doar poarta tine (ca `test_agenda`). Am sarit DS+mobil+comportament desi erau in metoda; acum metoda nu se mai poate sari. Cerut de Costin (19.08). Vezi F9 + punctul 5 din MODEL_AUDIT_TENANT.
- **RAMAS (out-of-perimeter, infra):** `interactiune_scan.py` acopera 6 ecrane din `nav_ecrane.ECRANE`; de extins treptat la toate ecranele UI. Stratul cabinet "firme" (paste CUI -> ANAF) exclus din scanul automat (dependenta externa nedeterminista) - acoperit de proba dedicata.

## Gard anti-suprascriere-tăcută: DO UPDATE cere justificare + roadmap instrumente (19.08.2026)
- **Gărzi:** `core/test_upsert_motivat.py` + `core/test_instrumente_roadmap.py`.
- **Ce face imposibil:** un `INSERT ... ON CONFLICT DO UPDATE` în producție fără `# upsert-ok: <motiv>` (suprascriere tăcută, Regula 4). Un „adaugă" de utilizator care suprascrie tăcut (ca bug-ul plan_conturi) e prins LA SCRIERE: n-are justificare → pică → folosește `DO NOTHING` / refuz 409. Simetric, `INSTRUMENTE_ROADMAP.md` marcat CONSTRUIT nu poate numi un fișier inexistent.
- **Mutație probă:** pe cod neanotat, 15 `DO UPDATE` pică; după anotare (toate 15 revizuite, legitime — chei naturale) = verde. Roadmap: fișier CONSTRUIT inexistent → pică (RED-probat).
- **RĂMAS (documentat în INSTRUMENTE_ROADMAP #1):** latura DROP tăcut (input curățat-la-gol-eliminat, ca `separa_cui`) — greu static, abordare separată (convenție „funcțiile de curățare întorc `(păstrate, ignorate)`"); `except`-gol prins de `test_masti`, coerciția de `DEFAULT_FISCAL_TACIT`. Instrumentele #2–#11 = backlog urmărit în roadmap.

## Fixturi pe tabele partajate period-keyed: marker sintetic obligatoriu (19.08.2026)
- **Gard:** `core/test_fixturi_shared_period.py`.
- **Ce face imposibil:** o fixtură de test care scrie în `public.declaratii_depuse`/`declaratii_coada` fără marker `# fixtura-sintetica-ok:` (tenant_id sintetic / rollback) și fără an 2099 → risc de coliziune PK cu prima depunere reală pe acel interval (bug 22.07: „verde azi, roșu mâine"). Alegerea sigură devine CONȘTIENTĂ.
- **Mutație probă:** scos un marker → pică; restaurat → verde. Adnotate ~8 situri în test_control_incrucisat/test_declaratii_depuse_randuri/test_tichete_pontaj (toate cu tenant_id sintetic, revizuite).
- **Campanie „gardăm cele 31":** prima din cele 16 de construit (A2 ratchet). Restul: RED-proof → CUI/CNP → hook-uri (registre/predare/DS-citat) → instrumente (#3→#2→#5→#6→#11 + rotunjire/temei/global-first/model-audit).

## CUI/CNP de test trec cifra de control (19.08.2026)
- **Gard:** `core/test_cui_cnp_test_valid.py`.
- **Ce face imposibil:** un CUI/CNP folosit ca date de test VALIDE (`cui=`/`cnp="..."`) cu cifra de control GREȘITĂ = capcană (16.07: validatorul confundă o dată de test greșită cu un bug de cod real). Testele negative (linia conține invalid/control/alterat/format sau marker `# cui-invalid-ok:`) sunt exceptate automat.
- **Mutație probă:** cui invalid nou fără keyword → pică; restaurat → verde. A scos **11 CUI/CNP invalide reale** folosite ca date valide — reparate la cifra de control corectă (înlocuire în tot fișierul, date+aserții consistente). `143000009` din test_d394 = deliberat invalid pt test negativ → marcat, nu reparat. Toate afectate: 43 passed.
- **Campanie „gardăm cele 31": garda #2/16** (A2 ratchet). Următoarele: hook-uri git-diff (registre/predare/DS-citat) → instrumente roadmap.

## Harta ecranelor nu crește tăcut (map completeness v1, 19.08.2026)
- **Gard:** `core/test_harta_ecrane.py` (roadmap #3).
- **Ce face imposibil:** un ecran de firmă `#fa-*` NOU să apară în cod fără a fi înregistrat — pică → forțează decizia: îl adaugi în `nav_ecrane.ECRANE` (scanat vizual/comportamental de `test_acoperire_vizuala`) SAU în `_BASELINE` (datorie de scanat, conștientă). Plus: baseline stătut (ecran dispărut) → pică.
- **Mutație probă:** `fa-nou` injectat → pică; restaurat → verde.
- **Baseline v1:** 27 ecrane; doar 6 în ECRANE (scanate), restul 21 = DATORIE de scanat, de mutat incremental (batch/tură). Scopul v1: niciun ecran nou nu scapă.
- **Campanie „gardăm cele 31": #3/~13** (primul instrument; după fixturi + CUI/CNP).

## Rotunjire fiscală: sumele folosesc ROUND_HALF_UP, nu round() bancar (19.08.2026)
- **Gard:** `core/test_rotunjire_fiscala.py` (AST pe `core/d*.py` + `*engine*.py`).
- **Ce face imposibil:** o sumă fiscală rotunjită cu `round()` (bancar half-to-even — greșit pe .XX5) în modulele de declarații. Se cere `common._q()` (Decimal+ROUND_HALF_UP). Exceptat: `int(round(...))` (rate/cote întregi, bancar==aritmetic), sau marker `# round-ok:` (rație/medie/margine/verificare, nu sumă persistată).
- **A SCOS BUG REAL:** `d212_engine` rotunjea bancar 8 sume fiscale (CAS/CASS/venit_net/impozit/baza_impozit/total_datorat = produse rată×bază + sume) → reparat la `_q`. Cele sigure (sume/diferențe de valori deja la 2 zecimale, medii, verificări) marcate `# round-ok:`.
- **Mutație probă:** `round()` nou pe produs fără marker → pică; restaurat → verde. Teste d112/d208/d300/d212: 67 passed.
- **Campanie „gardăm cele 31": instrument rotunjire-scoped (după fixturi + CUI/CNP + hartă).**

## 19.08 — Campanie gardare: golden-XSD structural (#6) + d402 reparat
- **`core/test_golden_xsd.py`** — ratchet: fiecare XSD de declarație din corpus (anaf_surse/*.xsd + core/saft.xsd) trebuie să aibă generator + ≥1 test care-l generează pe date populate și validează (lxml/jar). XSD nou nemapate sau fără test → blochează. RED-probat (fără test_d402 → semnalează d402).
- **BUG REAL scos:** `d402` (declarație informativă DAC1, generator complet `build_xml`/`genereaza` + XSD oficial) avea **ZERO teste** — XML niciodată probat contra structurii. Reparat: `core/test_d402.py` (fixtură populată → erori_generare gol → XML validează XSD-ul oficial ANAF prin lxml; + total=suma rândurilor R14).
- #7 (temei la sursă) marcat ACOPERIT în roadmap (test_temeiuri + verificator TEMEI/GRI, nu necesită instrument nou). #3 (hartă) mutat la Construite (era stătut).

## 19.08 — #11 §5 CALCULAT (meta-gardul campaniei)
- **`core/test_perimetru_calculat.py`** — din MODEL_AUDIT_TENANT.md (F1..F9) computează §5 = fațetele MANUAL (neacoperite mecanic), CALCULAT nu afirmat. §5 curent = {F3, F4, F5, F7}. Bite: fiecare fațetă cere etichetă `**Acoperire:**`; orice GARDAT numește gard care EXISTĂ (RED-probat: ștergi test_acoperire_vizuala → F6+F9 „enforcement pierdut"); §5 pinat la baseline (fațetă alunecată din GARDAT în MANUAL → §5 crește → pică). Ar fi prins ratatul „am sărit DS+mobil".
- MODEL_AUDIT_TENANT.md: etichete Acoperire pe toate cele 9 fațete (F6/F9 GARDAT test_acoperire_vizuala; F3/F4/F5/F7 MANUAL — pe diligență).

## 19.08 — F5 nume intern în mesajele de generare (perimetru 006/D301 + gardă app-wide)
- **D301 reparat** (perimetru tenant_006): `fără număr document (nr_doc gol)` / `(data_doc gol)` expuneau numele intern → rescrise fără paranteză.
- **`core/test_mesaje_generare_fara_camp_intern.py`** — gardă-ratchet: funcțiile `erori_generare`/`valideaza` din `core/d*.py` nu expun token `snake_case` (nume câmp intern) în mesaje afișate; exclude docstring-uri. Complementar lui `test_mesaje_fara_camp_intern` (care nu vedea listele returnate de erori_generare). Baseline per-fișier = datoria app-wide (274 mesaje/31 fișiere), niciun fișier nu crește; burn-down la 0. RED-probat (d403 36>35 → pică).
- **Datorie F5 app-wide (burn-down, DINCOLO de 006):** 274 mesaje în 31 generatoare expun nume interne (`categ_venit`, `cif_c`, `nr_contract`, `d_temei`…). De rescris în limba contabilului, form cu form. Gardat contra creșterii.

## 19.08 — F6 a11y app-wide (perimetru extins 006) + 7 ecrane gardate
- Audit orchestrator 006 (tid 4841): F2/F7 VERDE, F6 ROȘU pe 7 ecrane shell (fa-stocuri/registratura/banca/rapoarte/etransport/centrecost/casa).
- Reparat cu tiparul (shell partajat, profită toți tenanții): 8 controale fără etichetă → `aria-label`; contrast `.buton-sters`(--rosu-semafor→--rosu), `.cap-titlu`(#888→#6b6b6b), `.pf-frand-nume span`/`CUL.rosu`(→--rosu, 3 text-uses în firme/rip/facturi); țintă<24px `.btn-link`+`input[type=file]`(min-height 24, tiparul .subbara-edu).
- **GARD:** cele 7 ecrane înregistrate în `nav_ecrane.ECRANE` (scan urcă la 13) → `test_acoperire_vizuala` le păzește app-wide; închide 7/21 din datoria hărții (#3). Gardul a prins o violare (`.pf-frand-nume span`) pe care probe-ul static a ratat-o (interactiune_scan apasă butoane, dezvăluie rânduri) — dovada valorii scanului de interacțiune.
- Latent (de verificat când se renderizează): `CUL.galben/gri`-ca-text (contrast).

## 19.08 — D390: dublă-sursă + primită-fără-CUI (audit tenant_006)
- **`core/test_d390_dubla_si_primita_fara_cui.py`** (4 teste) — gard pe `calcul_d390`:
  - [Q1a] o operațiune IC cu bază din AMBELE surse (factură `directie=primita` + linie manuală/din ecranul D301, aceeași cheie tip/țară/cod/den) → avertisment „Posibilă DUBLĂ raportare" (bazele se adună; nu blochează). `core/d390.py:245,320`.
  - [Q2] factură PRIMITĂ fără CUI furnizor → NUMITĂ distinct („exclusă din D390; adaugă codul de TVA"), nu doar numărată anonim cu domesticele RO. `core/d390.py:300`.
  - RED-probat: `cp /tmp/d390.bak core/d390.py && pytest` → cele 2 teste pozitive pică. Probă vizuală R14: wizard D390 pe 006/09-2026 (seed temporar, curățat) afișează ambele în caseta de atenție.
  - Q1b (D394 gol pe firmă IC) și Q3 (ferestre D390/D394) = proiectare corectă, neatinse.

## 19.08 — D301: ruta de adaugare refuza platitorii (audit tenant_006)
- **core/test_d301_op_cere_neplatitor.py** — gard pe core/d301_operatiuni_api.adauga: daca firma e platitoare (platitor_tva=True) refuza operatiunea D301 cu mesaj spre Vectorul fiscal (D301 e pentru NEplatitori). Inchide ruptura care a permis cele 3 operatiuni pe 006 (vector platitor). Aparare-in-adancime: selectorul deja blocheaza calea UI (option disabled). RED-probat (fake conn; fara fix testul de blocare pica). R14: selector 006 D301 disabled "firma e platitoare" (DOM).

## 19.08 — Sweep D300/D390 manual: eligibilitate vector (audit tenant_006)
- **core/test_manual_decl_cere_eligibil.py** (4 teste) — simetric cu gardul D301: d300_manual_api.adauga refuza neplatitorii (D300=platitori); d390_clasificare_api.manual_adauga refuza firmele fara operatiuni_ic (D390=firme cu IC). Tiparul "ruta manuala de declaratie NU verifica vectorul" inchis pe toate 3 rutele. Aparare-in-adancime (UI deja blocata de selector). RED-probat (fake conn).
- DATE 006: vector corectat platitor_tva=False + inreg_art317=true (neplatitor art.317 cu achizitii IC). Verificat pe ecran: D301 -> ACTIV (datorat), D300/D394 -> blocate. Cele 3 operatiuni D301 acum coerente.

## 19.08 — Coada de validare: traseu de vizualizare (audit patru-ochi)
- **core/test_coada_vizualizare.py** — gard: coada de validare are traseu de vizualizare a continutului. Backend GET /coada/{id}/continut (payload stocat xml + avertismente + re-validare DUK); frontend validat.js face fiecare element clicabil (val-vezi -> deschideContinut) cu decodare UTF-8-safe. Fara asta validarea in doi era OARBA (cine aproba nu vedea declaratia/XML/verdict). RED-probat (revers validat.js+main.py -> pica). R14: click pe element -> vizualizare cu verdict DUK verde + avertismente + XML (diacritice corecte dupa fix atob->decodeURIComponent).

## 19.08 — D301: checksum VIES la introducere (audit 006/R24.1, clasa preview↔salvare)
- **core/test_d301_vies_la_introducere.py** — gard: la adaugarea unei operatiuni D301 cu furnizor UE, algoritmul codului de TVA (offline DE/FR/HR) se verifica ACUM in d301_operatiuni_api.adauga si da AVERTISMENT neblocant (simetric cu cifra de control a CUI RO). Fara asta, calea d301-derivata (care NU trece prin _facturi_ic) ducea codul gresit neverificat pana la respingerea DUK R24.1 - aceeasi regula, verdicte diferite in etape diferite. Neblocant: achizitia IC obligatorie nu se pierde. RED-probat. R14: form op D301/006 cu DE811234567 -> avertisment "va fi respins de DUKIntegrator (R24.1)... Verifica-l acum".

## 19.08 — temei_307: excludere D301->D390 auditabila per operatiune (audit tenant_006)
- **core/test_d390_autoderivare.py** (rescris) + **core/test_d301_temei_307_intrare.py** — gard: fiecare operatiune D301 tip 4 (art. 307 alin. 3/5/6) poarta CARE alineat (temei_307), cerut la introducere (respins fara temei); excluderea din D390 devine AUDITABILA (excluse_d301 -> motiv numit + temei citat, simetric cu diag-ul facturilor); temei NULL = SEMNAL, nu verde. Euristica "tip 4 + cod -> serviciu" + confirma_local SCOASE (inlocuite, nu dublate; zero cod mort). Migrare toate schemele (core/migrare_d301_temei_307.py). RED-probat pe operatiuni reale. R14: dropdown temei pe tip 4 + INV-DE-88 "temei art. 307 neconfirmat".
- Acceptare 006/iunie: D390 = 1 linie cod A DE136695976 baza 52.261; INV-DE-88 in excluse cu semnal neconfirmat; tip 4 fara temei respins la introducere. Toate verificate.

## 19.08 — D394 trimestrial: perioada + fereastra inghetate (audit tenant_003, MISDIAGNOSTIC inchis)
- **core/test_d394_trimestrial_perioada.py** (4 teste) — gard: constatarea „D394/003 emite septembrie in loc de trimestru + cifre necorespunzatoare" a fost inchisa ca MISDIAGNOSTIC (cod corect, ZERO reparatie). Gardul ingheata AMBELE laturi ca sa nu regreseze in bug real: (a) eticheta — `trim*3 ∈ {3,6,9,12}` = marcajul ANAF (OPANAF 2194/2025 lit. c: 03/06/09/12; 09=T3, nu „septembrie"); (b) fereastra — `fereastra_tva(·,"T")` = TRIMESTRUL INTREG [2026-07-01,2026-10-01) pe T3, augustul inauntru (factura 5900 baza + 889 TVA = 6789), span 3 luni, orice luna din trimestru -> aceeasi fereastra. RED-probat: mutand fereastra T la doar luna-ancora (regresia care pierde iulie/august) -> 3 teste pica. Inchidere documentata in PREDARE_LANT.md (NU redeschide).

## 20.08 — Patru-ochi: indicatorul nu are voie sa minta + aplicabilitatea nu produce fundatura (audit 006 / cabinet 1968)
- **core/test_patru_ochi_efectiv.py** (14 teste) — gard pe DOUA laturi. (A) ADEVARUL INDICATORULUI: `GET /eu/patru-ochi` intoarce `{activ, posibil, efectiv}` din SURSA UNICA `coada_api.patru_ochi_stare` (aceeasi pe care o foloseste `aproba`); cabinet.js/validat.js DECID pe `efectiv`, nu pe flagul brut `activ`; indicatorul are ramura „suspendat" si da bifa DOAR pe `efectiv`. Fara asta, subbara afisa „Validarea in doi ✓" pe un cabinet cu UN singur validator, in timp ce backendul permitea deja auto-aprobarea — si pe ACELASI ecran cardul zicea „De depus" (contradictie cu sine). (B) FUNDATURA: `posibil` cere >=2 VALIDATORI activi, nu „1 pregatitor + 1 validator + 2 oameni" — vechea formula devenea `true` cand un cabinet solo angaja un asistent DOAR cu `poate_pregati`, iar cele 3 declaratii pregatite de unicul validator deveneau neaprobabile de NIMENI. Latura comportamentala gardata direct pe `aproba` (auto-aprobarea trebuie sa TREACA fara al doilea validator si sa PICE cu el, iar al doilea validator sa poata aproba lucrarea). Plus: o singura definitie a multimii de validatori (`coada_api.validatori_activi`) — era in trei locuri (coada/asistenti/notificari).
  - RED-probat pe HEAD: 8/14 pica inainte de fix (intre care fundatura si bifa mincinoasa). Mutatii prinse: `>= 2` -> `>= 1`; `notificari_api` cu interogare proprie; `var(--ardezie)` -> `var(--verde-inchis)` pe ramura suspendata.
  - **core/test_a11y_contrast_tokens.py** extins: ambele culori ale indicatorului >=4.5:1 pe bara `.subbara` #dfe4ea (`--verde-inchis` 4.57, `--ardezie` 9.85) + starea suspendata NU poate purta un token verde.
  - LIMITA DECLARATA: gardul de front citeste SURSA (variabila de decizie), nu randarea. Randarea e acoperita separat de proba live (R13/R14).
  - R13/R14 pe cabinetul 1968, capturi PRIVITE, trei stari pe acelasi ecran: `po_0_inainte_*` (bifa mincinoasa, cod vechi simulat prin mutatie temporara, restaurata), `po_1_suspendat_*` (text onest, rgb(43,52,64), card „De depus"), `po_2_efectiv_*` (bifa adevarata, card „De validat", ZERO butoane de aprobare pentru pregatitoare). axe 0 desktop + Pixel 5 (body=393), tinta indicator 54px >= AA 2.5.8.

## 20.08 — D390: checksum VIES si pe liniile manuale/D301 (audit 006, inchide clasa deschisa pe 19.08)
- **core/test_d390_checksum_manual.py** (5 teste) — gard: `checksum_vies` era chemat DOAR de `_facturi_ic`; bucla liniilor MANUALE din `calcul_d390` verifica doar `len(codO)>12`. Deci o linie introdusa in ecranul D390 sau derivata din D301 intra in declaratie cu cod TVA nevalidat — aceeasi regula, verdicte diferite dupa calea de intrare. Fixul e la SURSA comuna (`calcul_d390`), nu la fiecare punct de scriere (ar fi fost a treia copie); gardul cere explicit ca cele doua cai sa dea ACELASI verdict pe acelasi cod. Ramane NEBLOCANT (simetric cu latura auto — vezi docstringul `d390.valideaza`): operatiunea obligatorie nu dispare, partenerul e NUMIT, DUK decide.
  - Exceptie deliberata gardata: `codO` gol pe tip A/S nu e raportat ca invalid (A/S pot omite legal codul).
  - RED-probat pe HEAD: 2/5 pica (linia manuala DE136695975 fara niciun diagnostic; cele doua cai cu verdicte diferite). Non-regresie pe date reale: linia lui tenant_006 (iunie 2026, cod A, DE136695976, baza 52.261) ramane curata, D390 in continuare DUK-valid.
  - Completeaza gardul din 19.08 (`test_d301_vies_la_introducere`): acela prinde DEVREME, pe calea D301; asta e plasa care prinde TOATE caile.

## 20.08 — Perimetrul declarat al unei firme: nu poate lipsi, nu poate deveni statut (cerut de Costin)
- **core/test_perimetru_firma_declarat.py** (4 teste) — o firma din matrice poate fi purtatoarea unui REGIM, nu o firma completa: tenant_006 („neplatitor micro cu achizitii IC") are 47 de tabele in schema si date in TREI (firma_profil 1, d301_operatiuni 3, plan_conturi 185 = nomenclatorul OMFP). Fara declaratie scrisa exista doua feluri de a gresi, si gardul le acopera pe amandoua. (1) NESCRIS: golurile se citesc ca DATORIE si cineva porneste sa parcurga F3/F7 pe tabele goale — dar F3 e definita pe „date POPULATE, nu pe fixture goale" si F7 „compara cifrele afisate cu faptele", deci pe gol dau verde fiindca n-au ce contrazice = exact falsul sentiment de acoperire interzis in capul acestui registru. Gardul cere fiecarei sectiuni `## tenant_0XX` un bloc **Perimetru** cu AMBELE laturi numite (ce e IN perimetru, in proza; ce e IN AFARA, ca lista de tabele intre backtick-uri). (2) STATUT: declaratia ramane scrisa dupa ce firma se umple. Gardul verifica pe DB ca fiecare tabel declarat in afara perimetrului EXISTA in schema si e GOL.
  - **FARA BASELINE, deliberat.** Registrul avea la data gardului o SINGURA sectiune de firma (`## tenant_006`; 001/002/003 apar doar ca mentiuni in proza, iar subsolul spune „se completeaza pe masura ce fiecare tenant e atins din nou"). Blocul lui 006 se scrie in ACELASI commit -> poarta e verde din prima, fara nicio amnistie. Gardul musca la prima tura care creeaza sectiunea firmei urmatoare, adica acolo unde e si contextul ei. Un ratchet cu baseline (tiparul `test_mesaje_generare_fara_camp_intern`) e instrumentul corect cand exista o datorie de ars — aici e zero; un baseline gol e greutate moarta, unul ne-gol ar fi fost o lista de amnistie.
  - RED-probat prin trei mutatii pe `ISTORIC_TENANTI.md`, fiecare pentru un fel diferit de minciuna, toate restaurate exact: linia „In afara perimetrului" stearsa (nescris) -> pica; `plan_conturi` (185 randuri) trecut ca fiind in afara perimetrului (statut) -> pica cu „`plan_conturi` e declarat IN AFARA perimetrului dar are 185 randuri — declaratia e STATUTA. Ori firma a capatat regimul asta (mut-o in perimetru si parcurge-i fatetele pe date reale), ori datele sunt reziduu de proba si se curata."; tabel inexistent declarat (verificare pe gol) -> pica.
  - Al patrulea test e anti-vacuu: daca regexul de sectiune nu mai prinde nimic (s-a schimbat formatul antetului), gardul insusi ar trece pe gol -> pica.
  - Scriptul care a compus blocul REFUZA sa scrie daca vreun modul din lista are date (nu are voie sa produca o declaratie falsa din prima) — cele 35 de module au fost numarate la sursa, nu presupuse.
  - **LIMITA DECLARATA:** gardul apara sectiunile CARE EXISTA. Daca o tura auditeaza o firma si nu-i creeaza deloc rand in registru, nimic nu se aprinde aici; asta ramane pe disciplina §11 din CLAUDE.md (raportul numeste obligatoriu ISTORIC_TENANTI.md). Gardul acopera „scris pe jumatate" si „scris si uitat", NU „nescris deloc".
  - MODEL_AUDIT_TENANT.md: F1 numeste gardul in linia **Acoperire** (deci `test_perimetru_calculat` il vede) + paragraf nou „Perimetrul se DECLARA in registru". §5 neschimbat: {F3,F4,F5,F7} — F1 era deja GARDAT.

## 20.08 — §5 se goleste REPARAND: al treilea colt al gardului de perimetru + ramura probata
- Incalcare prinsa de Costin: raportul gardului de perimetru avea §5 cu patru randuri, din care DOUA erau fixabile in cinci minute — deci munca neterminata parcata intr-o lista, nu limite. Regula exista (Regula 12 + §5-gol 19.08) dar era formulata „la finalizarea unei FIRME", iar incalcarea a fost intr-un raport de METODA: **o regula legata de un context prea ingust nu declanseaza**. Corectat la sursa, nu prin nota noua.
- **Fixat, nu explicat.** (1) „lista de module e incompleta, restul tabelelor nu-s gardate" -> **al treilea colt** in `core/test_perimetru_firma_declarat.py`: ORICE tabel GOL din schema trebuie CLASIFICAT, ori „in afara perimetrului" (gardat sa ramana gol), ori „in perimetru, poate primi date" (golul lui e o stare, nu o promisiune). Prinde si tabelele NOI din `tenant_template.sql` — la aparitie, cineva decide o data de care parte sunt. Tabelele CU date nu se cer clasificate (un tabel populat nu e ambiguu). (2) „ramura «schema nu exista» e scrisa, nu probata" -> `test_ramura_schema_inexistenta_e_raportata`, sintetic (`tenant_999`), fara sa creez sau sa sterg ceva in baza; verificarile cu DB au fost extrase in `_probleme_sectiune(cur, schema, corp)` tocmai ca ramura sa fie probabila.
- RED-probat: pe blocul incomplet, coltul 3 a numit exact cele 9 tabele parcate in §5 (`ai_corectii`, `contracte_sabloane`, `d300_manual`, `d390_manual`, `d390_reclasificare`, `notificari_scadenta`, `perioada_confirmata`, `perioade_blocate`, `rapoarte_salvate`).
- Clasificarea NU s-a facut prin umflarea listei: trei dintre cele 9 (`d300_manual`/`d390_manual`/`d390_reclasificare`) sunt caile MANUALE ale unor declaratii DIN perimetru — a le garda „sa ramana goale" ar fi fost o GRESEALA (o linie manuala pe 006 e legitima). Blocul poarta acum CRITERIUL de selectie scris, nu doar lista.
- CLAUDE.md §2.2 pct.5: §5 devine camp TIPAT — gol implicit, trei etichete permise (`[EXTERN]` / `[DECIZIE]` / `[NEVERIFICABIL]`), orice altceva e munca. **Limita: nu e gardabil mecanic** (raportul e text in conversatie, nu fisier); ramane pe lista B, cu inspectia lui Costin ca poarta — dar etichetele il fac verificabil dintr-o privire, iar coltul 3 scoate din discutie subclasa care a produs incalcarea.

## 20.08 — audit tenant_001 (S4): patru gărzi noi pe clase, nu pe cazuri

Auditul firmei celei mai complexe din matrice (12 salariați, 11 certificate CM pe 8 coduri) a scos 10
defecte. Patru gărzi noi; fiecare RED-probată din backup-copie, nu `git checkout`.

- **`core/test_refuz_generator_422.py`** — un generator care REFUZĂ motivat nu ajunge la contabil ca 500 gol.
  `bilant_api.genereaza` ridica `ValueError` cu mesajul potrivit („Nr. registrul comerțului lipsește… Se
  completează la Date firmă"), iar `main.py` nu-l prindea → `@app.exception_handler(Exception)` îl transforma
  în 500 „Internal Server Error". 44 din 392 de rute prindeau deja `ValueError`; astea nu. Regula gardată e
  **auto-întreținută, fără listă de rute**: pentru orice rută care cheamă `X.genereaza*()` unde funcția din
  `core/` conține `raise ValueError`, apelul trebuie să fie într-un `try/except ValueError`. Un generator nou
  care refuză motivat intră automat sub gardă; `api_public.genereaza` (care nu ridică `ValueError`) rămâne în
  afară — deci fără fals-pozitive (GĂRZI regula 3). **Gardul a găsit la prima rulare două instanțe pe care
  nici F9 nici sweep-ul manual nu le prinseseră** (`factura_pdf_ruta`, `factura_email`): contabilul care
  tipărea o factură cu o linie fără cotă TVA primea 500 gol. Total reparat: 6 rute.
- **`core/test_mesaje_valueerror_publicat.py`** — canalul de mesaje NEMODELAT de celelalte două gărzi F5.
  Ambele cheie pe ROL SINTACTIC (`HTTPException(detail=)` / cheie de afișare în dict / subclasă de excepție
  de business, respectiv funcții numite `valideaza`/`erori*`), deci un `ValueError` gol ridicat într-un helper
  din `core/` nu e în niciunul — raportau VERDE pe mesaje pe care nu le vedeau. Canalul, definit mecanic: 71
  de rute fac `except ValueError -> HTTPException`, adică PUBLICĂ orice `ValueError` primesc; ele ajung la 116
  funcții din `core/`, cu 148 de mesaje în proză. Două dimensiuni tratate diferit: **nume intern = ZERO admis,
  fără baseline** (cele 4 existente rescrise, deci pornește curat) și **diacritice = clichet per fișier**
  (baseline 84, burn-down declarat). Al treilea test refuză baseline-ul umflat: dacă cureți un fișier și nu
  scazi cifra, clichetul lasă loc să reintre exact câte ai reparat.
- **`core/test_get_fara_scriere.py`** — o rută GET nu scrie în starea de business (RFC 9110 §9.2.1). Vezi
  ISTORIC 20.08 pentru cazul care a scos-o. Clasa e mică și acum e închisă: 2 rute din 168 scriau. A doua,
  `GET /gdpr/export-cabinet`, scrie în `public.audit_log` cine și când a exportat date personale — aia nu e
  stare de business, e urma faptului că citirea a avut loc, și trebuie să existe TOCMAI fiindcă e un GET.
  **Excepția e mecanică (numele tabelului), nu o listă de rute**: orice rută poate jurnaliza, niciuna nu poate
  scrie altceva. Al treilea test cere ca excepția să fie chiar folosită — o excepție nefolosită e o gaură
  deschisă degeaba.
- **`core/test_stergere_salariat_completa.py`** — ștergerea unui salariat nu lasă jumătate din înregistrare.
  `salariu_istoric.salariat_id` e `integer NOT NULL` FĂRĂ `REFERENCES`, deci nimic nu cascadează: 24 din 30 de
  rânduri orfane pe tenant_001 (celelalte 18 scheme, curate). Regula se citește din SCHEMĂ, nu dintr-o listă:
  fiecare tabel cu `salariat_id` trebuie ori ȘTERS, ori REFUZAT, ori PROTEJAT de FK. **Prima versiune a picat
  pe propria barieră anti-gard-mort** (3 tabele găsite în `tenant_template.sql` vs 5 reale în bază): schema
  trăiește în template PLUS fișierele `NN_ddl_*.sql`. Corectat să le citească pe toate. Tot bariera aia a scos
  că `beneficii_lunare` ARE FK fără `ON DELETE` — deci nu poate orfana, blochează ștergerea zgomotos; îl
  scosesem din `DELETE`, fiindcă a-l șterge tăcut ar fi fost o schimbare de comportament neprobată.

**Extins:** `core/test_a11y_contrast_tokens.py` — test GENERIC pe toate clasele `.cf-*` cu culoare literală,
nu încă două teste per clasă. `.cf-galben`/`.cf-termen-galben` derivaseră de pe tokenul chihlimbar al DS
(`#92500a`) la `#a06713` = 4.02 pe panoul `#e9edf3`. Puse înapoi pe token: 5.30. Prins abia pe t001, fiindcă
doar o firmă cu declarații „de urmărit" RANDEAZĂ starea galbenă — exact latentul notat pe 19.08.

**Trei teste care APĂRAU defecte, inversate.** `test_d112_caen_codboala` asserta `"Str_codBoalaSType" in msg`
și `"Str_caenListSType" in msg` — adică cerea PREZENȚA numelui intern în mesajul contabilului, exact defectul
F5 reparat. A patra apariție a clasei notate în `test_datorie.py:234` (31.07). Aserțiunile cer acum absența
numelui intern + prezența locului unde se corectează.


## 20.08.2026 — clichetul constantelor fiscale nesursate din PRODUCȚIE (`e188018`)

**Ce face imposibil:** o constantă fiscală nouă, scrisă de mână în cod de producție, fără `Temei` atașat.
`core/test_constante_nesursate.py`, clichet **per fișier** (baseline 126 la instalare, se coboară, nu se
ridică). Un fișier fiscal nou pornește de la 0.

**De ce clichet și nu xfail.** Inventarul de pe 31.07 a fost xfail: a *înregistrat* datoria, n-a
*împiedicat-o*, și clasa a produs a cincea apariție opt zile mai târziu. Un xfail e o notiță.

**Instrumentul a picat de două ori înainte să meargă — ambele picări sunt în docstring și în calibrare:**
v1 a căutat literali în aritmetică+comparații (127 rezultate, aproape integral zgomot de format) și a
RATAT ținta cunoscută, fiindcă `_ZIUA.get(tip, 25)` e un default la lookup. v2 a clasat `Decimal("4050")`
ca nesursată deși are `Temei` pe același rând — clasifica ramura care găsise literalul, nu strămoșul
sintactic. De-aia calibrarea e în TREI direcții (nesursat / sursat / nomenclator), nu una.

**Mutația:** `PRAG_INVENTAT = 12345` în `core/cote_tva.py` → roșu, cu fișierul și rândul numite.

## 20.08.2026 — R5: temei legal ≠ regulă de produs în harta casetelor (`feddfd0`)

**Ce face imposibil:** o intrare `TEMEI` care tace despre baza ei legală, o citare care nu aterizează pe un
document din `anaf_surse/`, sau o regulă de produs fără decizia și data care au fixat-o.
`core/test_harta_temei.py`.

**Ce NU face:** nu verifică dacă actul citat chiar spune ce pretinzi — aia cere arbitrul, nu un gard
sintactic. Limita e scrisă în docstring, nu presupusă.

**Mutații (patru):** act inexistent în corpus · decizie fără dată · intrare tăcută pe amândouă câmpurile ·
dispariția felului „citare" (anti-vacuu). Toate roșii, cu mesaj care numește intrarea.

## 21.08.2026 — a patra clasă a scanului: temei PREZENT, dar în PROZĂ (`e22416f`)

**Ce face imposibil:** ca instrumentul de măsură să numere drept datorie exact cazurile bune. O
constantă al cărei act e citat lângă ea, în text, nu mai intră în clichet. `cote_tva.py` reproduce
art. 291 CF în antet și per categorie, e pe `_TVA_EXCLUSE` în verificator tocmai fiindcă el e modulul
care reproduce legea — și totuși scanul îl raporta nesursat. Cele 126 s-au recalculat: **C = 98,
E = 28.** Clichetul a coborât cu diferența.

**Regula, ancorată pe `_TVA_TEMEI` din verificator:** acolo un literal are temei dacă VALOAREA lui e
în registrul valoare → citare. Deci E cere ca aceeași unitate de proză (blocul de comentarii al
instrucțiunii, sau un paragraf din docstringul scope-ului imediat) să conțină ȘI citarea ȘI valoarea.
Citările se șterg din text înainte de căutarea valorii, ca `art. 21` să nu treacă drept cota 21.

**Ancorarea pe valoare nu e un rafinament, e miezul — măsurat, nu presupus:** regula „există o citare
undeva în antetul modulului" ar fi mutat **100 din 126** în E, inclusiv cele 11 `assert` cu valori
așteptate din `d212_engine` și cota în float din `d216`. Un antet care spune despre CE declarație e
modulul nu e temeiul niciunei valori din el.

**Instrumentul a picat de trei ori în construcție, toate în direcția periculoasă — E înghite datorie:**
- antetul ca pătură (100/126) → reparat prin ancorarea pe valoare;
- docstringul modulului guverna orice număr din adâncul funcțiilor: „sursa" ziua 25 din
  `_ZIUA.get(tip, 25)`, adică **chiar cazul de calibrare al nesursatului** → limitat la scope-ul imediat;
- `lit.?\s*[a-z]\)` fără graniță de cuvânt se aprindea pe cuvântul „po**lit**e)" din antetul lui
  `d403` și sursa cinci constante cu o coincidență ortografică.

**Zgomotul rămas e NUMĂRAT și NUMIT, nu aruncat tăcut:** `scan_constante.PROZA_RESPINSA`, două cazuri
privite în sursă și respinse — `d101g.py` „16" (proza vecină spune rd.16 și rd.61 cercetare-dezvoltare
16%, alt 16; geamăna ei din `d101.py:40` e în C, iar aceeași constantă nu poate avea două clase) și
`salarizare.py` „12" (proza spune „PNS 12/13/14", coduri de excepție, nu plafonul de 12 salarii
minime). Fiecare respingere are gard anti-vacuu: dacă nu mai corespunde unui candidat, testul cere
scoaterea ei.

**Calibrarea e acum în PATRU direcții:** nesursat (`25`) · sursat (`4050`) · nomenclator (`40`) ·
temei în proză (`cote_tva` 21/11), plus contra-direcția — `test_proza_nu_inghite_nesursatul` cere ca
`25`, `d216 0.3`, `d101 16` și cele 11 aserțiuni din `d212_engine` să RĂMÂNĂ în C.

**Mutații (patru), toate roșii:** proza fără ancorare pe valoare · granița de cuvânt scoasă de la
`lit.` · antetul guvernând orice scope · o respingere învechită. RED-probate din copie de siguranță.

**Ce NU face:** citește FORMA citării, nu adevărul ei — o proză care numește actul și valoarea, dar
citează greșit, trece drept sursată. Și E **nu e clasa bună**: A e sursat pentru MAȘINĂ (registrul
poate consuma temeiul), E doar pentru OM. Se numără separat tocmai ca să nu se topească în A și să
dispară cu ea și drumul E → A.

## 21.08.2026 — TEMA D: doc contra cod în `cote_tva` (`e22416f`)

**Ce face imposibil:** ca vreun drum din `cote_tva` să întoarcă din nou o cotă marcată
`sursa='fallback'`, și ca `cote_valide()` să reînvie. `core/test_granite_cota.py` TEMA D (3 teste).

**Prima versiune a gardului s-a aprins pe propria explicație.** Căuta „fallback" lângă „21" în
docstring — și l-a găsit în fraza care spune DE CE fallback-ul e greșit. Un gard care nu deosebește
afirmația de negația ei nu păzește nimic; mutat pe invariantul codului (`"sursa": "fallback"` nu
există în modul), nu pe cuvinte.

**Mutații (două):** `return {... "sursa": "fallback"}` pe ramura fără AI → roșu pe două teste (și pe
comportament, nu doar pe text) · `cote_valide()` reînviat → roșu.


## 21.08.2026 — R6: o depunere care contrazice un „nu se datorează" nu mai e invizibilă (`8238ef7`)

**Ce face imposibil:** ca „nu se datorează" și „s-a depus" să treacă una pe lângă alta.
`core/test_depunere_contrazice.py` (8 teste) peste `control_fiscal_api.depuneri_fara_obligatie`.

**Nu era o omisiune, era o proprietate a FORMEI.** `_clasifica` iterează pe `datorate` și consultă
`depuse` ca dicționar — o depunere fără obligație pereche nu era VIZITATĂ niciodată. Nicio trecere
inversă nu exista, deci contradicția era invizibilă **prin construcție**. Diferența față de un bug:
n-avea cum să apară, oricâte date ai fi pus.

**Măsurat înainte de a repara** (sondă de citire pe 17 firme, cu probă de nescriere — 834 de tabele
numărate înainte și după, zero diferențe): din 54 de depuneri, 28 sting o obligație, 18 sunt în afara
ferestrei, **7 contrazic un „nu se datorează"**, 1 e opinie pe un `neclar`. Zero semnale produse.

**Ce NU face — și e miezul:** o depunere nu stinge un `neclar`. Că s-a depus dovedește că firma a
CONSIDERAT că datorează, nu că a considerat corect, și nu spune nimic despre perioadele în care N-A
depus — care e chiar întrebarea. Dacă ar stinge-o, firma care a depus tot ar părea complet verificată,
deși ea e tocmai cea despre care nu știi dacă a depus tot ce trebuia. Gardul cere explicit ca mesajul
de opinie să nu sune a stingere.

**Defect prins în construcție:** prima versiune ținea motivele într-un dicționar pe TIP și a produs
„D100 pe 3/2026 … nu se datorează: «nu se datorează pe T4 2025»" — un mesaj care citează altă
perioadă. Are gard propriu (`test_motivul_citat_e_al_perioadei_depunerii`).

**Mutații (patru), toate roșii:** neaplicabilul periodic nu mai e văzut · motivul luat pe tip ·
opinia formulată ca stingere · rezultatul nu mai ajunge în răspuns.

**Ce NU e cablat:** ecranul. Rezultatul intră în răspunsul semaforului și e consumat de
`frontend_test/audit_tenant.py` (F7); pastila NU e escaladată — o culoare fără explicație ar fi mai
rea decât tăcerea. Randarea așteaptă confirmarea a CE se vede.

## 21.08.2026 — absența unei înregistrări nu mai poate deveni „nu se datorează" (`8238ef7`)

**Ce face imposibil:** un motiv nou de tipul „D40x nu se datorează — niciun X înregistrat", fără
poartă de completitudine numită. `core/test_absenta_nu_e_neaplicabil.py` (6 teste), care citește prin
`ast` toate șirurile vizibile din `control_fiscal_api` (fără docstringuri) și le trece prin
discriminatorul de FORMULARE.

**A patra instanță în două zile** — trei D301 (R2′, 20.08) și D205 (azi). Discriminatorul e al lui
Costin: *„niciun X înregistrat" e aproape întotdeauna `absenta_observatie`*. Criteriul de separare e
REMEDIUL: „verifică dacă faptul a existat" aparține lui «Nu pot verifica», niciodată lui «Nu se
datorează».

**Măsurat, nu presupus:** 12 motive „nu se datorează" în total; **5 formulate ca absență**; dintre
ele 2 au poartă reală (D100 „bază 0" distinge trimestrul genuin gol de cel cu facturi necontabilizate;
D390 se confirmă doar pe luna ÎNCHISĂ), 1 n-avea (D205 — `are_note` cerea o singură notă validată pe
an), 2 veneau dintr-o bifă din Vector. Reparate: D205 reîncadrat la „nu pot verifica" cu remediul
scris; cele două din selector își numesc acum SURSA.

**Ce NU face:** nu judecă dacă poarta e destul de bună, doar că a fost NUMITĂ. O poartă slabă scrisă
în registru se vede și se poate contesta; una nescrisă nu.

**Mutații (trei), toate roșii:** motiv nou formulat ca absență · D205 întors la „nu se datorează" ·
propoziția care ține reîncadrarea D301 ștearsă.

## 21.08.2026 — confruntarea celor două instrumente (`8238ef7`)

**Ce face imposibil:** ca două măsurători ale aceluiași lucru să se contrazică în tăcere.
`core/test_constante_nesursate.py` — verificatorul ținea `cote_tva.py` pe `_TVA_EXCLUSE` („aici
literalii de cotă sunt așteptați"), iar scanul îl raporta cu 2 constante nesursate. Nimeni nu le
compara.

**Testat retroactiv: ieri confruntarea ar fi dat 9 semnale** (cote_tva 21/11, d300 ×4, d394 ×3) —
adică exact miezul celor 28 de false pozitive, **fără să deschizi vreun fișier**. Ăsta e răspunsul la
„se putea ști înainte?".

**Azi dă 1, ținut într-un clichet NUMIT** (nu un număr): `d406.tva_procent: Decimal = Decimal(21)`,
cotă ca default de parametru pe linia de factură D406.

**CORECTIE (21.08, în aceeași zi).** Raportasem 5, dintre care 4 în `d300_reconciliere`, cu
instrucțiunea „repară prin import din sursa unică". Era GREȘIT: duplicarea de acolo e DELIBERATĂ,
scrisă în antetul modulului și apărată de `test_non_tautologie_*` — a doua cale n-are voie să împartă
cod cu prima, altfel gardul de conținut D300 devine tautologic. Judecasem după FORMĂ (două constante
identice) fără să citesc antetul. Ce lipsea era TEMEIUL lângă valori; adăugat, au ieșit din C.
**Confruntarea a avut dreptate că e ceva acolo — eu am greșit ce anume.** Un instrument care semnalează
corect poate fi urmat greșit: semnalul spune UNDE să te uiți, nu CE să repari.

**Citește registrul celuilalt instrument ca DATE, prin `ast`, fără import** — modulul verificatorului
își rulează scanul la nivel de modul, iar un test n-are voie să pornească alt instrument ca efect
secundar.

**Mutații (trei), toate roșii:** cotă nouă nesursată într-un fișier exclus · `_TVA_EXCLUSE` dispare
(gardul spune „repar-o, nu o șterge") · baseline mai larg decât realitatea.


## 21.08.2026 — faptul bate vectorul în selector (`d6f5d44`)

**Ce face imposibil:** ca selectorul să blocheze D390/D301 pe o bifă din Vector când faptul o
contrazice. `core/test_faptul_bate_vectorul.py` (12 teste).

**Tiparul tenant_006, în formă de acțiune.** Vectorul spunea „fără operațiuni intracomunitare", firma
avea achiziții IC reale. Un verdict greșit se poate citi și ignora; un SELECTOR care blochează pe
acel verdict îl împiedică pe contabil să declare o obligație pe care firma o are. Vectorul e o
AFIRMAȚIE, faptul e o OBSERVAȚIE — când se contrazic, faptul câștigă și vectorul devine ce trebuie
corectat.

**Contra-direcția, la fel de gardată:** fapt ABSENT + vector „nu" → blocajul RĂMÂNE, și NU devine „nu
pot verifica" ca la cele trei D301. Acolo tăcea un tabel (absența unei observații), aici a răspuns un
om — verificat în trei locuri: UI-ul refuză salvarea cu placeholder gol și mesaj propriu, backendul
respinge `None` (IC_LIPSA), 17/17 firme au câmpul completat. Vectorul NEcompletat produce deja gri.

**Descoperit citind, nu presupunând:** poarta de BACKEND (`declaratii_api`) folosea doar
`neaplicabile_forma` — deci blocarea pe vector trăia numai în selector. Schimbarea a ieșit mai mică și
mai sigură decât părea.

**Mutații (cinci), toate roșii:** faptul nu mai deblochează · motivul nu-și mai numește sursa · poarta
nu mai vede documentele în așteptare · semaforul ignoră sonda · ruta nu mai cheamă sonda.

**Ce NU face (limită declarată):** sonda de fapt citește facturile IC (ambele direcții) și tabelul
manual D301; NU citește `d390_manual`. O firmă cu DOAR linii manuale D390 rămâne blocată în selector —
dar semaforul îi arată obligația, iar remediul e în mesaj.

## 21.08.2026 — poarta D390: întărită, nu convertită (`d6f5d44`)

**Ce face imposibil:** să se afirme „D390 nu se datorează pe luna X" când există documente primite de
la ANAF și încă neînregistrate pe acea lună. `d390.evidenta_incompleta`.

**Decizia lui Costin, care a ținut designul drept:** *„poarta se întărește, nu se convertește în
necunoaștere — griul își pierde înțelesul dacă acoperă și «nu știm nimic» și «știm, dar poarta e
slabă»"*. Deci gri DOAR pe lunile cu semnal CONCRET: e-Facturi rămase `descarcata` cu data în lună,
numărate în mesaj. Restul lunilor rămân fapt.

**CE LIPSEȘTE ca „lună închisă" să însemne completitudine** (scris în cod și aici, ca tăcerea să nu se
citească drept acoperire):
1. **Perioada confirmată pe domeniul facturi/TVA.** Mecanismul general EXISTĂ — `core/perioada.py`,
   DESIGN_SYSTEM cap.23: cât timp e neconfirmat, datele sunt informative și calculele din aval
   blochează. Dar singurul domeniu folosit azi e `pontaj`. Fără un domeniu de facturi și fără acțiunea
   de confirmare la închidere, nimeni nu declară vreodată luna încheiată. **Asta e jumătatea care
   lipsește, și e muncă de produs.**
2. **Documentele care există doar pe hârtie sau la client** — necunoscute prin construcție. Nicio
   poartă nu le acoperă, deci limita rămâne declarată oricât s-ar întări restul.

**Ambele `except` sunt marcate `# MASCA MOTIVATA`** — gardul de măști le-a prins la commit, corect.
Tăcerea e deliberată și direcția ei contează: un eșec de citire produce „nu pot ști" (deblochează /
lasă poarta cum era), niciodată o afirmație despre lume.

## 21.08.2026 — actul de închidere a lunii pe domeniul `facturi` (`c1043e3`, `396447d`)

**Ce face imposibil:** ca cineva să declare „evidența lunii e completă" peste documente pe care le
vedem deja neînregistrate; și ca o închidere să supraviețuiască unei modificări.
`core/test_inchidere_luna.py` (14 teste, pe schemă efemeră reală).

**Ce lipsea nu era mecanismul.** `core/perioada.py` (cap.23) există din iulie, cu
`confirma`/`deconfirma`/`e_confirmat` pe (an, lună, domeniu). Lipsea DOMENIUL și ACTUL: cineva trebuie
să DECLARE. Până atunci „lună închisă" era o observație despre calendar.

**Cele două reguli, gardate:**
1. **Nu se confirmă peste o absență cunoscută** — blocaj motivat care numește câte sunt și unde se
   rezolvă. Refuzul e verificat și pe stare (nu doar pe excepție): luna rămâne neînchisă.
2. **O modificare de-confirmă automat** — `facturi_api._redeschide_luna` pe creare și pe ștergere,
   simetric cu `pontaj.seteaza`. Cu contra-direcția: o factură din ALTĂ lună nu redeschide luna
   închisă, altfel închiderea n-ar ține niciodată.

**Adoptarea e per firmă** (decizia „poarta se întărește, nu se convertește"): o firmă care n-a închis
nicio lună rămâne exact cu comportamentul de dinainte. Punctul de adoptare e cea mai VECHE lună
închisă, nu ultima.

**Mutații (cinci).** A patra — punctul de adoptare luat ca ULTIMA lună — **a trecut prima dată**:
testul închidea o singură lună, unde „prima" și „ultima" coincid. O aserțiune care nu poate fi
falsificată nu e gardă; întărită cu două luni închise, mutația pică.

**Două defecte găsite PRIVIND capturile, nu numărând** (contorul spunea „casetă prezentă, axe 0"):
starea blocată numea obstacolul fără remediu — contabilul știa CE, nu și UNDE; și butonul rupea fraza
la mijloc, stând inline. Ambele reparate, a doua oară la tiparul pontajului, care era de urmat oricum.

**Probă vizuală** pe ALFA MICRO, trei stări pe aceeași lună (deschis / blocat / închis) + Pixel 5:
axe 0 desktop, axe 0 mobil, body=393 fără overflow. IGIENĂ DE DATE: rândul de e-Factură inserat
temporar și șters, luna redeschisă, numărătorile identice înainte/după.

## 21.08.2026 — P2: un ecran nu scrie în coajă (`e0b8eb7`)

**Ce face imposibil:** ca un chiriaș să-și ia singur spațiu din coajă.
`core/test_proprietate_coaja.py` (9 teste) + contractul din `static/js/coaja.js`.

**Măsurătoarea mi-a corectat diagnosticul.** Spusesem dimineața că *Comunicarea stă în patru locuri*.
Fals: `arataMesaj` (256 apeluri, 22 fișiere), `confirmaCaseta` (27) și `eroareCamp` (35) au fiecare UN
proprietar în `api.js`, iar `test_dialog_nativ_frontend` interzice deja mesajele ad-hoc cu clichet 0.
Defectul real era îngust — **două locuri** în `cabinet.js`.

**Contractul stă în modul propriu**, nu în navigator: `navigator.js` importă `ecrane/ansamblu.js`, deci
un import invers ar fi închis un ciclu. Contractul nu aparține niciunei părți.

**Ambele semnături sunt gardate** — și că nimeni nu ia singur, și că proprietarul încă declară locul.
Fără a doua, `cereLoc` ar întoarce mereu null și chiriașii ar dispărea TĂCUT de pe ecran.

**Gardul a trebuit reparat înainte de a fi scris:** prima versiune se aprindea pe propriul meu
comentariu explicativ. Aceeași greșeală ca gardul de ieri care nu deosebea afirmația de negația ei —
comentariile se scot ÎNAINTE de căutare, și e legat cu două teste (o pomenire nu e încălcare;
`el.className = "subbara-edu"` nici atât — chiriașul își numește propriul nod).

**Mutații (trei), toate roșii:** un ecran ia iar singur loc · nimeni nu mai cere prin contract ·
proprietarul nu-și mai declară locul.

**Probă live** (cabinet 1968, flag aprins temporar și restaurat exact): bara arată identic, axe 0,
Pixel 5 fără overflow, și UN singur indicator după re-randare — idempotența contractului.

## 21.08.2026 — ORDINEA gard↔reparație: ce e închis și ce e doar asertat de autor

Regula (Costin): *garda se scrie ÎNTÂI, pică pe HEAD, apoi vine reparația. Dacă garda apare după fix,
ai fost și observator și comparator, indiferent ce scrie în ea.* Aplicată retroactiv rulării P1–P7,
prin măsurarea istoricului — nu din memorie.

**ÎNCHISE (gardă înainte, roșie pe HEAD):**
- **R2 / R2′** — xfail strict din `8f3a8ba` (20.08), roșu 24 de ore, reparat pe 21.08. Toate cele 12
  constrângeri ale hărții sunt din acel commit: 12/12 scrise înaintea oricărei reparații de azi.
- **P6 Drumul** — fixul e din 10.08 și nu e al meu; am măsurat comportamentul ÎNAINTE de a scrie garda.

**GARDĂ DUPĂ FIX, RED-probată prin mutarea fixului** (nu „închise" — mutația o aleg tot eu):
P2 coajă · P5 termene · #13 citate · octeți invizibili · P4 limite · P7 vector gol.

**Ce lipsește ca să fie închise cu adevărat:** o falsificare INDEPENDENTĂ — mutații generate
sistematic, nu alese de autor. Aia e #2 din roadmap (fuzzer), și e singurul lucru care ar transforma
„am probat că pică" în „nu putea să nu pice".

**De ce contează, dovedit în aceeași zi:** RED-proof-ul retroactiv cerut de Costin a scos un gard care
NU păzea nimic — `test_randerul_chiar_o_afiseaza` a rămas verde după ștergerea titlului din randare,
fiindcă îl găsea în comentariul de deasupra. Dacă n-ar fi cerut ordinea, gardul ar fi rămas în tabel
arătând închis, cu suita verde.

Generalizat imediat în #14 (`core/test_ancore_in_cod.py`): ancora unui gard trebuie să existe în COD,
nu în proză.

## 21.08.2026 — Gărzi noi: statul emis și fluturașul

**`core/test_stat_plata_emis.py`** (16) — documentul emis nu se schimbă când se schimbă datele sub el;
contradicția e derivată, nu un câmp; un motiv o asumă, nu o stinge, și cere cine + când; corecția e al
doilea exemplar care îl referă pe primul; verificarea nu scrie și nu emite; emiterea e idempotentă.
RED-probat cu 7 mutații, toate roșii.

**`core/test_fluturas_egal_stat.py`** (4) — fluturașul nu cheamă direct motorul de salarizare; rândul
din care se tipărește coincide cu statul pe toată populația (192 de perechi); PDF-ul RANDAT arată
cifra statului (citit cu `pypdf`, pe un caz construit prin deconfirmarea pontajului în tranzacție
anulată — nu pe ce se întâmplă să conțină datele unei firme); exemplarul emis bate recalculul.
RED-probat cu 4 mutații, toate roșii.

### Ce a scos RED-proof-ul, și n-ar fi ieșit altfel
Două gărzi treceau pentru motivul greșit:
- `verificarea nu scrie` număra rândurile pe o lună FĂRĂ nicio contradicție — o verificare care emite
  singură corecții ar fi trecut, fiindcă n-avea ce corecta. Acum provoacă divergența întâi.
- `emiterea persistă` chema `emite` o singură dată, deci nimic nu asertea idempotența. Mutația care o
  scotea trecea verde.

Și un ajutor de test trecea pe gol: muta salariul cu `UPDATE salariu_istoric`, dar tenantul are
istoricul GOL (bridge pe `salariati.salariu_brut`), deci prindea ZERO rânduri. Două teste „probau" că
documentul rezistă la schimbarea datelor, într-o lume în care nimeni nu schimbase nimic. Mutarea se
face acum prin sursa unică și **dovedește** că recalculul s-a mișcat înainte de a asertea ceva.

### A patra instanță a clasei „un gard citește proză drept cod"
`test_schema_coloane` tokeniza literalii SQL dintr-un `.py` și lua **docstringurile** drept SQL: un
docstring care pomenea tabelul `state_plata` a produs „coloane" numite `document`, `salariat`,
`altfel`, `aplicația`. Reparat gardul, nu textul: `scan_ancore.domenii_docstring()` (scoasă din
`fara_proza`, din #14) e acum folosită de amândouă. Aceeași unealtă, în cele două direcții — un gard
trebuie să-și găsească ancora în cod, și nu are voie să-și citească dovada din proză.

### Coliziune de nume, prinsă de gardul de izolare
Am definit `_schema_sau_404(tenant_id, ctx)` fără să caut întâi numele. Exista deja
`_schema_sau_404(ctx, tenant_id)`; definiția mea a suprascris-o și a rupt **47 de rute** cu argumentele
inversate. Suita a prins-o pe loc. REGULA DE AUR se aplică și la botez: grep înainte de „e liber".
Tot gardul ăla a prins și ordinea greșită din ruta de emitere — citea corpul cererii înaintea
verificării accesului, deci un străin primea 500 în loc de 404, adică afla că ruta există și ce
câmpuri așteaptă.

## 21–22.08.2026 — P8: afirmațiile despre datele firmei sunt OBIECTE, în TOATĂ aplicația

Decizia exista din 21.08 (`core/afirmatii.py`, R2′/R2), dar trăia pe **un ecran**: un singur consumator
de producție, `control_fiscal_api`. O regulă scrisă și nepăzită e o intenție. Campania a dus-o în tot
codul, cu clichet.

### Cifra
120 netipate la instalare → **24**, din care **7 declarate ca excepții** → **datorie reală 17**.
`control_incrucisat` a ajuns la ZERO și a ieșit din tabel.

### Gărzi noi
| gard | ce face imposibil |
|---|---|
| `core/test_afirmatii_tipate.py` | o afirmație netipată nouă; un fișier care crește; un baseline stale; scanul care orbește pe vocabular; clasificarea care înghite clasele excluse |
| `core/test_respingeri_import.py` | un cod de respingere din afara nomenclatorului închis; un cod declarat-nefolosit; clasificarea după proză în `migrare.js` |
| `core/test_chei_duplicate.py` | o cheie care apare de două ori în același dicționar (Python o dedublează TĂCUT; ruff n-o prinde) |
| `core/test_flag_constatare.py` | o stare a semaforului care nu produce afirmație validă; `an`/`luna` care redevin opționale |
| `core/test_unde.py` | un fel de referent inventat; un referent fără identitate; **un fapt fără niciun domeniu** |
| `core/test_registru_exceptii.py` | registrul care crește; o excepție moartă; un motiv din afara setului închis; rațiunea „rezultat de operație" |

### Ce a ieșit necăutat — defecte reale, nu curățenie
- **Fluturașul dădea 920 lei de tichete pe hârtie** pe care statul le blocase (pontaj neconfirmat,
  HG 1045/2018 art.10(3)). 14 din 192 de perechi salariat×lună divergeau, verificat pe funcția reală.
- **`migrare.js` clasifica duplicatele potrivind PROZĂ** — `(e.mesaj||"").includes("există deja")`.
  O reformulare a mesajului ar fi spus tăcut „0 firme erau deja în portofoliu" despre un import în
  care erau.
- **Câmp mort** `explicatie` pe containerele de modul: 7 din 12 șirul gol, 5 calculate degeaba, citit
  de nimeni (verificat: nici `/api/v1`, nici PDF, nici persistat).
- **Cheie duplicată** într-un nomenclator fiscal — două intrări cu aceeași cheie ar face ca ordinea
  din fișier să decidă ce regulă se aplică.
- **`tip 4 cu temei NECONFIRMAT`** din D390 stătea în aceeași listă cu excluderile confirmate,
  deosebite doar printr-un boolean. Acum una e `fapt` cu temei, cealaltă `necunoastere`.

### Clase de greșeală proprie, consemnate (au produs gărzi sau reguli de metodă)
1. **Default comod care ascunde o cale netestată — de TREI ori.** `an=None`/`luna=None` puse „ca să nu
   ating apelanții"; ramuri care cădeau imediat, fără niciun test. Sonda `sonda_default` măsoară acum
   clasa: **25 din 78** de parametri cu default `None` din modulele fiscale n-au fost NICIODATĂ `None`
   la niciun apel din suită — adică defaultul e o promisiune neverificată.
2. **Gard care-și citește dovada din proză — de PATRU ori**, ultima pe propriul meu comentariu care
   explica de ce forma veche era greșită. Instrumentul exista (`scan_ancore.fara_proza`, #14); nu
   l-am folosit din prima.
3. **AM ORBIT SCANUL.** Ca să scot un fals pozitiv, am lărgit o regulă: a scos **16 din 32** —
   jumătate din datorie — printre care o constatare adevărată. Am revenit. Ce am pus în loc scoate
   EXACT UNU și are gardă pe creștere. Un scan se poate face verde orbindu-l, nu reparând codul.
4. **Măsurătoare de consumatori făcută prin grep pe exemple**, nu pe clasă: am zis „trei fișiere de
   test", erau cinci, iar suita mi-a arătat-o cu 23 de teste roșii.
5. **Ambalaj „pentru brevitate" care orbește un instrument** — un `_resp` local a făcut scanul de
   confruntare să nu mai găsească codurile. Scos.

### Datorie deschisă, declarată
- **17 afirmații netipate reale** rămase, în 13 fișiere.
- `unde` NU verifică că referentul EXISTĂ în bază — cere conexiune, e altă gardă.
- Sonda de default-uri e grea (~10 min, învelește la import); locul ei e lângă scanul de constante,
  nu în pre-commit. **Prima ei formă a stricat un test** (funcția învelită returna sursa spionului la
  `inspect.getsource`); reparat cu `functools.wraps`.

## 22.08.2026 — P11 construit: interpretarea ca obiect + confruntarea registrului

### Ce s-a măsurat (confruntare ARHITECTURA_NORMATIV, interdicțiile 1, 2, 16, 17, 21, 22, 23)

Toate cinci cazurile de calibrare cerute de Costin **găsite înainte de orice cifră**.

| # | brut | real |
|---|---|---|
| 1 valoare fiscală în afara registrului | 131 | ~100 (≈23% zgomot) |
| 2 interogare fără dată | 3 | 3 |
| 16 nomenclator din sursă secundară | 39 din 93 | 39 |
| 17a valoare de registru re-declarată | 42 | ~34 |
| 17b formulă de registru în ≥2 module | 1 formulă, 3 module | 1 |
| 21 interpretare care apare ca lege | 15 | **2** |
| 22 interpretare fără variante | — | **nemăsurabilă** |
| 23 dezacord stins prin aliniere | 0 | 0, deja gardat |

**#2 are o cauză unică:** `cota(nume, la_data=None)` — defaultul e *azi*. Interdicția 2 e posibilă doar
fiindcă interdicția 14 e prezentă în punctul de intrare al registrului.

**Codurile de boală, patru straturi, cu o contradicție:** interfața oferă 16/17/51, validarea din
`d112` cade pe `1..15` când XSD-ul nu se poate citi.

**Tensiune de plan, semnalată:** P8 spune „arbitrul decide", interdicția 16 spune „nu deriva din sursă
secundară". `d390.TIPURI/TARI_UE` au ales conștient validatorul, cu proba scrisă. Planul nu spune care
câștigă.

### Gărzi noi
| gard | ce face imposibil |
|---|---|
| `core/test_interpretare.py` | o interpretare cu o singură variantă · alesul din afara listei · dezacordul ca flag stins prin apăsare · arbitrul care contrazice fără să spună ce zice · o formă de incertitudine inventată |
| `core/test_comparatii_clasificate.py` | o comparație NOUĂ neclasificată pe o valoare de registru · un marcaj către o cheie inexistentă · un registru cu dicționar liber · detectorul care orbește |

RED-probat pe **opt** direcții, toate roșii, cu curățare de `__pycache__`.

### Ce NU face garda, scris în capul ei
Nu verifică că temeiul **chiar determină** comparația. Întrebarea lui Costin a schimbat construcția:
o gardă care ar citi un `text_citat` ar fi a cincea instanță de gardă-care-citește-proză. Marcajul e
un **link verificabil** (cheia se rezolvă sau nu), iar gardul închide clasa **NECLASIFICAT**, nu clasa
*greșit clasificat*.

### Greșeală proprie, consemnată
Am raportat „le-am privit pe toate 15" despre egalitățile stricte. Era **la nivel de linie**. La
re-citire pe context, trei dintre cele numite „zgomot" merită a doua privire (`d223:159` regula
„100% doar cu un singur asociat", `d406:1338/1367` alegerea codului fiscal pentru cota zero). Cifra
„2 reale" rămâne un **plafon inferior**, nu un rezultat.

Și a patra oară azi am insistat pe editarea din shell până s-au rupt escapările, în loc să scriu
fișierul din prima.

---

### CONFORMITATE.md — registrul confruntării cu planul normativ (22.08.2026)

`core/test_conformitate.py` — **o interdicție din `PLAN_ARHITECTURA.md` fără secțiune în
`CONFORMITATE.md` nu trece poarta.** Cerut de Costin: *„Cifrele confruntării nu au voie să existe
doar în raport. Raportul se citește o dată; registrul rămâne."*

Ce face imposibil: o interdicție nouă în plan fără secțiune (planul a crescut 25 → 48 într-o zi) ·
un câmp obligatoriu gol — *„«Investigată» nu e o stare"* · o stare din afara celor patru · o secțiune
orfană · o stare MĂSURATĂ fără cifră sau fără caz de calibrare GĂSIT · o PARȚIAL care nu spune că
cifra e un plafon inferior · o NEMĂSURABILĂ fără motiv.

**Ce NU face, declarat:** nu verifică dacă cifra e CORECTĂ. Verifică forma și completitudinea;
adevărul unei cifre se probează prin calibrare, nu prin gardă.

**Anti-vacuu, două:** (1) `test_planul_chiar_se_citeste` — dacă parsarea planului se rupe, toate
celelalte ar trece pe zero interdicții, exact interdicția 19; (2) `test_citirea_campurilor_se_
opreste_la_capatul_randului` — anti-vacuu pe INSTRUMENT. Prima formă a gardului citea valorile cu
`\s*`, iar `\s` cuprinde linia nouă: un câmp golit împrumuta textul rândului următor și mutația
„câmp obligatoriu gol" **trecea**. Prins de RED-proof, reparat cu `[ \t]*`. Un gard care citește
peste marginea rândului măsoară alt fișier decât cel scris.

**Falsificat** (9 mutații, cu curățare de `__pycache__` între ele): interdicție nouă fără secțiune ·
câmp golit · stare inventată („Investigată") · MĂSURATĂ fără calibrare · secțiune orfană · capul de
tabel al planului redenumit · PARȚIAL fără plafon · NEMĂSURABILĂ fără motiv. Toate pică.

---

## 22.08.2026 — I1: instrumentele + codurile de boală

### `core/test_cod_boala_nomenclator.py` — codul de indemnizație vine din Nomenclatorul 9
Sursa e NORMATIVĂ (`core/nomenclator_cm.py`, 20 de coduri cu temei per cod), nu enumerarea XSD.
Garda probează **poarta folosită de generator** (`_d112_genereaza` → `_cod_boala_acceptat`) și
interzice a doua cale (`_ncm.accepta` chemat direct oriunde altundeva în `d112`).

**Prima formă a gărzii a picat proba.** Extrăsesem `_cod_boala_acceptat()` dar lăsasem `genereaza` să
cheme `_ncm.accepta` direct: mutația care întorcea `d112` la enumerarea XSD **trecea verde**. Adică
făcusem exact logica paralelă împotriva căreia scrisesem testul. A doua slăbiciune: pragul `len >= 18`
lăsa ștergerea unui cod legal să treacă — acum e clichet pe 20.

**Falsificat** (7 mutații, cu curățare de `__pycache__`): întoarcerea la enumerarea XSD · ocolirea
porții pe o a doua cale · codul 51 scos · un cod fără temei · un cod inventat, nenumit în documentul
ANAF · XSD-ul redevenit autoritate · nomenclatorul golit. Toate pică.

### `core/scan_garzi.py` — instrumentul rundei I1 (interdicțiile 18 și 19)
Patru sub-instrumente, toate pe arbore sintactic sau pe EXECUȚIA tiparului, niciunul pe proză:
**A** tipare moarte (fiecare regex dintr-o gardă, rulat pe tot corpusul; MORT se afirmă doar dacă
subiectul e sursă din repo) · **B** teste care culeg fără nicio aserțiune de existență · **C** gărzi
care citesc sursă fără să scoată proza · **D** gardă scrisă odată cu fixul sau singură.

**Calibrat pe trei cazuri din istoric, toate găsite, toate verificate și în direcția negativă:**
octetul `0x08` din `test_temei_termene` (rev. `29bd752`, dispare pe HEAD) · `test_verificarea_nu_scrie_
nimic` (reconstruit — nu există ca revizie) · `test_schema_coloane` (rev. `5d46d4f`, dispare pe HEAD).

**De trei ori o rafinare a ORBIT instrumentul, și de fiecare dată calibrarea a prins-o:**
1. tracerul de subiect căuta citirea de fișier pe loc, dar ea vine prin trei salturi de variabile →
   cazul `0x08` a dispărut. Reparat cu rezolvare tranzitivă.
2. „controlul pozitiv în modul" era o EXCEPȚIE tăcută → a înghițit cazul B, fiindcă modulul era plin
   de teste bune și unul singur număra pe o lună curată. Acum e atenuare raportată, nu excepție.
3. `tokenize` și `ast.parse` erau în lista de scutiri de la C → cazul canonic n-a apărut. Amândouă
   sunt scutiri false: tokenizarea COLECTEAZĂ string-urile, iar `ast.parse` lasă docstringurile ca
   noduri `Constant`. Chiar asta era natura bug-ului.

**Regula care iese:** o listă de scutiri prea largă orbește exact ca un tipar mort, iar calibrarea se
reface DUPĂ FIECARE atingere a instrumentului, nu o dată la început.


## 22.08.2026 — registrul confruntarii nu poate imbatrani tacut (`core/test_conformitate.py`, +12 teste)

**De ce (Costin):** *„un antet cu date vechi e mai rau decat niciunul"* si *„o cifra adevarata azi se
citeste peste doua saptamani ca stare curenta, desi codul s-a miscat. Nu e o afirmatie gresita — e una
care imbatraneste, iar data o face vizibila."*

**Trei clase inchise:**

1. **Antetul de etapa** — `test_antetul_exista_si_e_complet`, `test_etapa_e_dintre_cele_cinci`,
   `test_criteriul_si_ce_lipseste_nu_sunt_aceeasi_fraza`, `test_antetul_nu_e_stale`. Prospetimea se
   verifica pe ISTORICUL GIT, nu pe mtime (mtime se schimba la checkout si ar da verde fals): registru
   modificat fata de HEAD -> antetul poarta data de AZI; registru curat -> data >= ziua ultimului commit
   care l-a atins. Asa prinde INAINTE de commit, nu dupa.
2. **Cand, si de pe ce cod** — `test_fiecare_sectiune_are_cand_si_de_pe_ce_cod`,
   `test_o_cifra_poarta_data_si_commitul`, `test_neinceputa_nu_pretinde_masuratoare`,
   `test_commiturile_din_registru_exista`, `test_antetul_numeste_cel_mai_vechi_commit`. Ambele directii:
   o cifra MASURATA fara ancora pica, dar si o sectiune NEINCEPUTA care PRETINDE o masuratoare.
   Hash-urile se rezolva cu `git cat-file` — un commit inventat arata exact ca unul adevarat.
3. **Efectul e al interdictiei, nu al grupului** — `test_efectul_e_al_interdictiei_nu_al_grupului`.
   Defectul, gasit de Costin: campul „unde ajunge efectul" fusese completat pe GRUPURI de principii
   (13 purta efectul lui 15, 14 pe al lui 2). Auditul complet al celor 48 a scos **13 grupuri de text
   partajat + 2 sectiuni cu text-substituent**; 26 de sectiuni au fost rescrise.

**Anti-vacuu pe INSTRUMENT, nu doar pe date:** `test_cititorul_de_antet_chiar_vede_antetul` probeaza ca
regexul de antet chiar gaseste blocul si intoarce None cand lipseste. Fara el, un regex rupt ar face
toate cele patru teste de antet sa treaca pe un fisier fara antet — interdictia 19.

**RED-proof: 14 mutatii, 14 rosii**, din copie de siguranta, cu curatare de `__pycache__` intre ele.
Una a fost refacuta: prima forma a mutatiei „criteriul copiat in ce lipseste" nu facea campurile egale,
deci gardul trecea corect — **mutatia era gresita, nu gardul**.

**CE NU FAC, declarat:** nu verifica daca ce scrie in antet e ADEVARAT (ca etapa e chiar cea in care
suntem), nu verifica daca masuratoarea a fost chiar facuta la acea data si pe acel arbore, si nu se
aprind cand distanta fata de HEAD creste — vechimea se CITESTE, nu se blocheaza. Un prag ar transforma
harta in poarta si ar opri lucrul tocmai cand e mai mult de facut.

**Proxy-ul de la clasa 3 e slab prin natura lui:** prinde COPIEREA (text identic), nu parafrazarea.
Cifra lui e un plafon inferior — dar prinde exact forma prin care s-a produs clasa.


### Addendum, aceeasi zi: `pasul curent` si sectiunea B derivata

Antetul a primit un camp nou, **`pasul curent`**, si el e obligatoriu ca restul. Motivul e mecanic, nu
estetic: sectiunea „UNDE SUNTEM" a raportului **nu se mai scrie de mana** — se deriva din antet cu
`scripts/raport_b.py`. Costin: *„daca B s-ar scrie separat, ar deveni al doilea loc unde traieste
aceeasi stare — si s-ar invechi, exact clasa pe care o inchidem."*

Un camp de care depinde un raport, dar pe care nicio garda nu-l cere, dispare la prima rescriere. De-aia
a intrat in `ANTET_CAMPURI`, nu doar in fisier.

**Ce NU deriva din antet: cifrele.** Numarul de interdictii masurate/partiale/nemasurabile/neincepute si
cel mai vechi commit se NUMARA din sectiuni, la fiecare rulare. O stare scrisa de mana despre propriile
sectiuni ar fi aceeasi clasa de defect, mutata cu un rand mai jos. Prima rulare a si aratat de ce: eu
spusesem „8 masurate + 1 nemasurabila"; numaratoarea da **6 MASURATE + 2 PARTIAL + 1 NEMASURABILA**.


## 22.08.2026 — RESTANTELE devin obiect gardat, nu observatie in raport

**De ce (Costin):** *„daca restantele nu apar nicaieri in B, B spune ca nimic nu blocheaza."*
Consecinta era vizibila chiar in raportul care a produs observatia: antetul spunea „decizii care
blocheaza: niciuna" intr-un moment in care categoria de marime bloca o familie intreaga din 1a. Formal
corect — e restanta, nu decizie — si tocmai de aceea invizibil.

**Sectiunea `## RESTANTE` din CONFORMITATE.md**, cu patru intrari deschise (R1 acte partiale in corpus ·
R2 vigoarea pe punct · R3 categoria de marime · R4 forme vechi citite ca la zi). Fiecare poarta felul
blocajului (SURSA / VERIFICARE / ARTEFACT), starea, commitul de deschidere, ce blocheaza si **conditia de
deblocare scrisa**. O restanta fara conditie de deblocare e o notita; una cu conditie e o poarta.

**Contorul nu se scrie: se DERIVA din git** — cate commituri au atins registrul de cand s-a deschis
restanta (`scripts/raport_b.py`). Un numar scris de mana ar fi chiar defectul pe care restantele il
masoara, mutat cu un rand mai jos.

**Patru teste + anti-vacuu pe instrument**, RED-proof **7 mutatii, 7 rosii**: sectiunea dispare · un camp
obligatoriu golit · fel din afara celor trei · stare inventata · REZOLVATA fara `rezolvata pe commit` ·
hash inventat · parserul rupt.

**CE NU FAC, declarat:** nu judeca daca felul ales e cel potrivit, nici daca conditia de deblocare e
realista. Verifica forma si existenta.

**Plus, in antet:** `avertisment la cifre` — obligatoriu, fiindca „66 NEINCEPUTE" e adevarat si inselator
in acelasi timp: cel putin zece interdictii au masuratori in campaniile din iulie-august, netransferate
(transferul e la 3a). Cifra arata mai multa munca ramasa decat e.


## 22.08.2026 — interdictia 52 primeste, in sfarsit, un mecanism (`core/test_corpus_amprenta.py`)

**De ce.** Interdictia 52 — *„un act din corpus al carui text s-a modificat dupa aducere"* — avea un
artefact (`<nume>.sha256`, 177 de bucati) si **niciun test care sa-l compare cu fisierul**. Amprenta era
o declaratie, nu o proba. S-a vazut cand `legea_82_1991_consolidat.html` a aparut modificat fata de
commit, cu 1629 de linii, **fara ca vreun script al turei sa-l scrie**: nimic nu s-ar fi aprins daca nu
ma uitam din intamplare la `git status`.

**Patru teste, pe toate cele 177 de perechi** (0,35 s): amprenta are forma de amprenta · nicio amprenta
orfana · continutul nu s-a schimbat sub amprenta · plus **anti-vacuu**, care are DOUA mutatii, nu una:
domeniul inexistent SI domeniul care exista dar e gol. A doua e cea care conteaza — un director gol nu
arunca exceptie, doar trece.

**RED-proof: 5 mutatii, 5 rosii.**

**CE NU FACE, declarat:** nu spune ca textul de pe SURSA s-a schimbat — pentru asta ar trebui
re-descarcat, iar pagina portalului nu e reproductibila octet cu octet. Raspunde la intrebarea
dinauntru: *„fisierul din corpus e cel caruia i-am luat amprenta?"*. **Cine** l-a schimbat, nu spune —
spune doar CA s-a schimbat, ceea ce e exact ce lipsea. Cauza ramane restanta R6.


## 22.08.2026 — un defect gasit are UN LOC: felul ORDINE, fluxul in cinci pasi, si doua garzi noi

**De ce (Costin):** *„un defect care nu e nici instanta de interdictie, nici restanta blocata ramane
doar in raport, adica se pierde."* Auditul a masurat cat de mare era gaura: din **opt** defecte
reconstituibile de pe disc, **cinci** n-aveau niciun loc cu stare.

**Al patrulea fel de blocaj: ORDINE** — nimic tehnic nu blocheaza, doar nu e momentul; conditia de
deblocare e un MOMENT din plan. E felul care lipsea si e cel mai des intalnit: fara el, singurele
variante erau „repar acum" sau „ramane in raport", iar a doua inseamna pierdut.

**Garzi noi in `core/test_conformitate.py`** (5 teste, RED-proof 5/5):
- `test_felurile_de_blocaj_sunt_cele_patru` — ORDINE intra in nomenclator;
- `test_fiecare_restanta_spune_unde_intra_si_de_cate_ori_a_fost_reluata` — `unde intra` numeste o
  etapa E1..E5, `reluari` e numar;
- `test_trei_reluari_fara_rezultat_cer_rescrierea_conditiei` — a patra reluare pe aceeasi conditie nu
  trece („conditia e scrisa gresit, nu restanta e grea");
- `test_o_etapa_nu_se_inchide_peste_restantele_ei` — cerinta din PLAN_LUCRU care statea neimplementata;
- `test_cititorul_de_etape_terminate_chiar_vede` — ANTI-VACUU, fiindca azi nicio etapa nu e declarata
  terminata, deci garda de mai sus ar trece pe zero randuri.

**Gard in `scripts/githooks/commit-msg`: un defect mentionat are un loc.** Daca mesajul semnaleaza un
defect LASAT NEREPARAT, trebuie sa spuna unde e consemnat — `#n`, `Rn`, `CONFORMITATE.md` — sau sa
poarte escape-ul motivat `# fara-consemnare-ok:`.

**CALIBRAT INAINTE DE LIVRARE, pe 81 de mesaje reale (20-22.08).** Prima forma se aprindea pe **10 din
81**, dar dintre ele trei erau chiar CONSEMNARI („DECIZII: divergenta podelei part-time") sau
REPARATII („10 defecte reparate", „D1 implementat"). **Un gard care se aprinde pe consemnarea insasi
invata pe cineva sa nu mai scrie „defect" in mesaj — exact invers decat scopul.** Ingustat la „gasit si
lasat asa": **1 din 81**.

**Proba pe hook, sase cazuri, toate corecte** — si a prins un defect al gardului insusi: `grep -E` e
ERE, iar `R[0-9]\{1,2\}` (sintaxa BRE) nu potrivea „R8", deci un mesaj care CITA corect restanta era
respins. Un tipar care nu poate potrivi ce trebuia — chiar clasa interdictiei 19, in gardul scris
pentru consemnare. L-a prins proba, nu norocul.

**CE NU FAC, declarat:** hook-ul pazeste MESAJUL DE COMMIT — singurul artefact de tip raport care ramane
pe disc. **Rapoartele din conversatie nu se pot garda de aici**; ele raman in seama disciplinei.


## 22.08.2026 — un fisier NORMATIV nu se comite pana nu e citit (`commit-msg`, garda A)

**De ce (Costin):** *„Un fisier normativ e o COMANDA SCRISA, nu un artefact de sincronizat. Diff-ul se
citeste si se rezuma in mesajul de commit: ce s-a schimbat, ce cerinte noi contine, ce trebuie facut cu
ele."*

**Instanta care a produs regula** — cea mai scumpa de azi: sectiunea „Restantele" din `PLAN_LUCRU.md`
a intrat in repo prin commitul `45f15ab`, NECITITA. 70 de linii scrise de Costin, sub mesajul meu.
**Patru cerinte au stat opt commituri neimplementate**, iar o a doua taxonomie a fost derivata in
paralel pentru un obiect deja definit.

**Ce face imposibil:** un commit care atinge `PLAN_*.md`, `CONFORMITATE.md`, `METODA_VERIFICARE.md`,
`CLAUDE.md`, `MEMORY.md` sau `ARHITECT.md` fara un rand `# diff-citit: <rezumat>` in mesaj.

**CE NU FACE, declarat:** verifica doar ca mesajul POARTA un rezumat. Nu poate verifica daca diff-ul a
fost inteles — aia ramane disciplina. Dar face imposibil sa treaca TACUT, si asta lipsea.

**Impreuna cu garda de ieri** („un defect mentionat are un loc"), hook-ul `commit-msg` are acum trei
porti: fisiere noi peste prag, defect fara loc, fisier normativ fara rezumat. Toate cu escape motivat,
niciuna care sa se poata ocoli tacand.


## 22.08.2026 — cele doua reparatii de PRAG 1, cu garzile lor

**1.1 — starile unei facturi intr-un singur loc** (`core/nomenclator_status_factura.py`,
`core/test_status_factura_un_loc.py`). `de_preluat` era clasat *staging* in d300 si EXCLUS din decont,
desi `facturi_api.emite_factura` il produce ca stare a unei facturi EMISE si **nimic din repo nu-l
scoate de acolo**. Masurat inainte: 4 facturi emise, 3 platitori, **3.052,00 lei TVA colectata** in
afara decontului. Dupa: t003 0 → 889,00 · t005 0 → 2.100,00 · t013 315,00 → 378,00.

Decizia de interpretare (P11) e scrisa in antetul nomenclatorului, cu **varianta respinsa numita** si cu
ce se intampla daca ea e cea corecta (atunci defectul e in `emite_factura`, nu in d300). **De confirmat.**

**A doua cale citeste ACELASI registru, nu constanta celeilalte cai** — nu e o incalcare a lui P7:
`d300_reconciliere` nu importa `d300`, ci amandoua importa nomenclatorul. Asta e P1.

**Calibrarea gardului a prins doua forme de orbire, in constructie:**
1. prima forma citea si DOCSTRINGURILE — se aprindea pe `export_winmentor.py:162` si `export_saga.py:157`,
   care DESCRIU regula in proza. Reparat cu `scan_ancore.domenii_docstring`, instrumentul care exista
   deja pentru clasa asta (nu unul nou);
2. a doua clasifica NUMELE, nu OBIECTUL: `ciorna` si `descarcata` sunt si stari ale tabelei
   `efactura_primite` — alt obiect, alt nomenclator. Trei false pozitive. Discriminatorul corect e
   `de_preluat`, care apare numai la facturi.

**RED-proof 5 mutatii / 5 rosii** — a cincea a picat abia dupa ce am reparat testul: prima forma cerea
doar ca NUMELE modulului sa apara in fisier, iar o mutatie care alia importul trecea. **Un import
nefolosit nu e o citire.** Iar prima mutatie era ea insasi gresita — o mutatie gresita si un gard slab
arata la fel din afara.

**1.2 — codurile de concediu medical vin din registru** (`core/coduri_cm_api.py`,
`core/test_coduri_cm_din_registru.py`). Lista scrisa de mana omitea 11/91/92 — coduri legale, acceptate
de aplicatie — deci **bloca un contabil sa introduca un cod valid**. Acum: denumirea din nomenclator,
procentul din `salarizare.procent_cm` (doua variante DATATE ale OUG 158/2005 art.17(1)), eticheta
compusa la randare. Proba ca eticheta urmeaza registrul, nu un sir: **cod 01 = 55/65/75% azi si 75% pe
o data dinainte de Legea 141/2025**.

Scara „55/65/75" nu e scrisa nicaieri: se obtine INTEROGAND registrul pe duratele care schimba
rezultatul (7/14/15/30 zile) si pastrand valorile distincte. Daca legea se schimba, eticheta se
schimba singura.

**Si o a doua instanta prinsa de gard**: textul de ajutor al ecranului scria „la 75%" — tot un procent
in JS. Scos; trimite acum la eticheta codului.

**Unealta care aduce acte nu mai poate scrie un artefact gol** (`scripts/portal_legislativ.py`
`_scrie_text`, `core/test_portal_nu_scrie_gol.py`, 23.08.2026). Gard **la producător**, nu la poartă.
`adu` scria `<nume>.txt` necondiționat: `t = text(brut)` și scria, oricare ar fi `t`. Așa au intrat în
corpus cele opt artefacte de un octet din **R20** — extragerea a produs gol și n-a spus-o. Acum se
oprește, cu numele fișierului în mesaj, și **nu lasă în urmă nici `.txt`, nici `.txt.sha256`**: o
amprentă rămasă fără fișier ar fi la fel de rea, o amprentă pe un act inexistent. Pagina (`.html` +
`.html.sha256`) rămâne — ea chiar există.

**De ce e nevoie de el deși clichetul e pe 0.** `test_provenienta.py` a coborât clichetul de artefacte
goale la zero, deci orice gol pică poarta. Dar **un clichet pe 0 fără gard la sursă spune doar CĂ a
apărut un gol, nu de unde** — ar fi căzut la prima aducere, iar întrebarea „e regresie sau
comportament normal?" n-ar fi avut răspuns. Cauza s-a dovedit, nu s-a presupus: corpusul are **9**
fișiere `.xsd`, iar cele opt goale erau **exact opt dintre ele** — extractorul le-a trecut prin ramura
de HTML, iar un strip de etichete peste un XSD nu lasă nimic. Al nouălea (`d402`) a scăpat fiindcă
fusese derivat sub alt nume. Nu opt accidente: o ramură greșită aplicată de opt ori.

**RED-proof 4 mutații / 4 roșii** — mutația `if False:` pe gardă lasă cele două teste de formă verzi
și **le pică pe toate patru cele de gol**, inclusiv cel care verifică *zero fișiere rămase pe disc*.
Al treilea test e **anti-vacuu**: citește sursa lui `adu` cu `inspect.getsource` și cere ca garda să
fie chiar pe drum (`_scrie_text(` prezent, `".txt"` absent) — altfel garda ar fi decorativă, ocolită
de o a doua scriere de alături.

**`JournalID` din D406 poartă jurnalul de ORIGINE, nu o constantă** (`core/d406.py` `_JURNALE` +
`_gl_entries`, `core/test_d406_jurnal_origine.py`, 23.08.2026). **Prag 1**: nu o absență, o **afirmație
falsă** trimisă autorității. Până azi se scria literalul `GENERAL` pe fiecare înregistrare, deși
OMFP 2634/2015 Anexa 1 **pct. 58 lit. i)** cere *„jurnalul de origine în care se regăsesc înregistrările
contabile"* — elementul exista și nu purta nicio informație.

**Ce a decis construcția, citit la sursă** (`anaf_surse/d406_schema_anaf.xlsx`): `Journal` e **`0..*`**
(deci mai multe jurnale sunt permise), iar `JournalID` e **`SAFshorttextType`, maxLength 18 — text
liber, NU nomenclator închis**. Deci maparea nu e cerută de schemă; e cerută de noi, fiindcă
`inregistrari.sursa` poartă **nume interne** (interdicția 13) și fiindcă `migrare`/`iconta`, care există
în coloană, **nu sunt jurnale** ci proveniența unui import.

**Default DECLARAT, nu tacit:** o notă fără sursă intră în `DIVERSE` (Nota de contabilitate, cod
14-6-2/A); o sursă **nemapată** e numită în avertisment, cu nota și valoarea — tiparul `[B17]`.

**RED-proof 2 mutații / 2 roșii**: constanta readusă în `_gl_entries` → trei teste roșii, printre care
cel care verifică *un `<Journal>` per origine, cu tranzacțiile care nu se amestecă*; `pull` care nu mai
trece sursa prin mapare → testul **anti-vacuu** roșu, cel care citește sursa lui `pull`/`genereaza` cu
`inspect.getsource`. **Arbitru extern**: structura cu patru jurnale a trecut validatorul **oficial ANAF**
(DUKIntegrator, D406, reguli 2026.1) pe `tenant_013`/2026-08 — `valid`, zero erori.

**O funcție partajată între clustere nu e proprietatea niciunuia** (`core/agenda.py`
`proprietari_unici`, `core/test_graf_clustere_proprietar.py`, 23.08.2026). **R19, închisă mecanic.**
Filtrul vechi era `if f in own: continue` — excludea partajarea **cu sine**, nu partajarea **între
alții**. Regula nouă nu mută proprietatea, o **ridică**: partajata nu primește alt proprietar, ci
niciunul. Măsurat: funcții deținute **154 → 84**, muchii **960 → 111**, muchii pe funcții
multi-proprietar **0**, cicluri **321 → 3**.

**Anti-vacuu, pe inventarul real**: garda cere să existe **cel puțin 10 funcții partajate** de exclus
— fără ele ar raporta verde despre o lume pe care n-o vede. **Clichet în ambele direcții** pe 111
muchii: nu poate crește tăcut (regula slăbită) și nu poate ajunge la zero (un graf vid n-ar ordona
nimic — R18). **RED-proof 1 mutație / 5 teste roșii din 6.**

---

**Felurile de jurnal din D406 sunt VERBATIM din normă, nu denumiri proprii** (`core/d406.py`
`_FELURI` + `TEMEI_JURNALE`, 23.08.2026). Corectare la întrebarea lui Costin: le pusesem ca decizie de
produs, dar **Anexa 1 pct. 45 și 52 le numesc** — deci partea aceea e nomenclator oficial, iar
scrierea lui ca literal e **interdicția 28**. Gardul **nu citește proză**: caută fiecare fel **literal
în corpus** (`anaf_surse/omfp_2634_2015_anexa1_norme_generale.txt`). O reformulare îl face roșu.
Anti-vacuu propriu: corpusul trebuie să fie nenul, iar o reformulare de probă trebuie să LIPSEASCĂ din
act. Ce rămâne al nostru — `JournalID`, splitul CASA/BANCA, AMORTIZARE la „alte operațiuni" — e scris
ca decizie de produs, lângă temei.

---

**Antetul nu mai poate acumula narațiune** (`core/test_conformitate.py`
`test_pasul_curent_nu_devine_naratiune`, 23.08.2026). Plafon **mecanic de 300 de caractere** pe
`pasul curent`. Gardul **nu citește proza** — numără caractere; nu judecă ce scrie, face imposibilă
acumularea. Motivul e măsurat: în două zile antetul a rămas în urma corpului de **două ori**, de
fiecare dată pe partea **numărabilă**. Regula scrisă în registru: *dacă o propoziție se poate confrunta
cu o cifră, nu e a antetului — e a derivatorului.* RED-probat: `pasul curent` umflat la 400 de
caractere → roșu.

**Și `felul limitei` pe PARȚIAL** (`test_partialele_declara_FELUL_limitei`). PARȚIAL acoperea două
lucruri cu consecințe diferite: **DOMENIU** (regiune cunoscută lăsată afară) și **ORBIRE** (instrument
fără calibrare pe propriul mod de eșec). Nu e o stare nouă — cele patru stări descriu ce s-a întâmplat
cu MĂSURĂTOAREA, orbirea e o proprietate a INSTRUMENTULUI. **Cifra, acum derivabilă: 7 ORBIRE / 7
DOMENIU** din 14. RED-probat: o secțiune PARȚIAL fără câmp → roșu.

**`scan_constante` nu mai vede doar o listă de nume** (`core/scan_constante.py` `in_domeniu` +
`_citeaza_legea`, `core/test_constante_nesursate.py`, 23.08.2026). **Calibrare NEGATIVĂ**, cerută
explicit: *dacă instrumentul vede mai puțin decât crede, clichetul păzește un prag fals, iar direcția
aia e tăcută.* Gardul avea **patru calibrări**, toate pozitive sau contra-direcții ale clasei E;
niciuna nu întreba ce rămâne **afară**.

**Gaura 1 — DOMENIUL.** `FIS` acoperea **79 din 289** de module `core/`. Dintre cele 210 rămase, **50**
aveau semnal fiscal, iar **4 construiesc `Temei`** — fiscale prin propria mărturisire. Domeniul e acum
*nume fiscal SAU modulul citează legea*: criteriu **mecanic**, care se întreține singur. **Clasa C:
93 → 104.** Datoria n-a crescut — a devenit vizibilă. Clichetul s-a **lărgit** cu cele 4 module, nu s-a
ridicat.

**Gaura 2 — BOTEZUL.** Un nume care se potrivește cu `NOM` trimite valoarea în B, tăcut: `TIP_COTA = 21`
→ B, `CATEG_PLAFON = 300000` → B. **Nu s-a schimbat regula** — ar fi mutat 15 clasificări corecte în C.
S-a făcut **vizibilă**: `BOTEZ_BASELINE` numește cele 7 coliziuni reale (toate coduri de categorie); a
opta pică. Gaura e reală și **azi goală** — de aceea calibrarea ei e **sintetică**, pe cod construit
anume: un test care ar aștepta o instanță reală n-ar prinde-o niciodată.

**RED-proof 1 mutație / 2 roșii**, dintre care `test_baseline_nu_e_stat` — adică chiar clichetul, nu
doar testul de domeniu.

**O restanță al cărei declanșator s-a produs nu poate rămâne nereluată** (`core/test_reaprindere.py`,
23.08.2026). `PLAN_LUCRU.md` cere reaprinderea la fiecare tură; măsurat la cerere, **contorul de
`reluări` era 0 pe toate cele 25 de restanțe** — de la prima până la ultima. Regula era **scrisă și
nepăzită, deci se citea ca respectată**.

Gardul închide clasa în care declanșatorul e **mecanic**: o condiție care numește un fișier și verbul
*„atinge"*. Pentru fiecare restanță deschisă, compară `deschisă pe commit` cu istoricul fișierului; dacă
s-a atins și `reluări` e încă 0, pică. Plus: contorul trebuie să fie un **număr** (altfel pragul de trei
din plan nu se poate compara) și nu poate depăși **3** fără rescrierea condiției.

**Nu e RED-probat pe o mutație inventată — a fost roșu de la prima rulare, pe cazul real:** R8, a cărei
condiție (*„la primul commit care atinge `d223.py` ori `d406.py`"*) se declanșase de **două ori în
aceeași zi**, prin commituri proprii. **Ce nu acoperă, declarat:** declanșatoarele care nu sunt fișiere
(*„la punctul de decizie 2"*, *„când există iar clustere"*) rămân de citit de om — gardul închide clasa
mecanică, nu clasa întreagă.

**Importurile nefolosite nu mai pot crește** (`core/test_importuri_nefolosite.py`, 23.08.2026).
**Clichet la 90**, per fișier, pe `ruff --select F401`. Motivul din `ruff.toml` (18.08) — *„prea
zgomotoase ca să fie poartă blocantă pe cod existent"* — **rămâne valabil pentru o poartă și e greșit
pentru un clichet**: un clichet nu cere curățenie acum, împiedică doar creșterea. Cifra scăzuse de la
~115 la 90 **incidental**, deci nimic nu garanta că nu urcă la loc. Anti-vacuu: dacă parsarea se rupe,
contorul devine 0 și clichetul ar trece pe gol — gardul cere **cel puțin 40** de constatări și prezența
lui `main.py`. Primul lucru pe care l-a prins a fost **importul mort din propriul meu test de o oră
înainte** (`pytest` în `test_reaprindere.py`), scos pe loc — nu baseline-at.

---

**Domeniul lui `scan_constante` are acum a treia regulă** (23.08.2026, a doua lărgire din aceeași zi).
După sondajul COMPLET pe cele 46 de module rămase: **48 de constante de clasă C**, clasificate una câte
una înainte de decizie — **17 fiscale · 20 de algoritm · 11 operaționale**. Cele 20 de algoritm au ieșit
**corect**, nu prin excepție: `CHEIE` a intrat în `NOM`, unde îi era locul (vectorul de ponderi al
checksum-ului CNP e aceeași clasă cu `_CNP_W`). Rămân 30, din care **17 fiscale — peste jumătate**, deci
lărgirea s-a decis **pe compoziție, nu pe teamă**. **C: 104 → 135**, module văzute **60 → 85**. Zgomotul
operațional nu se aruncă: intră în clichet pe fișierul lui, vizibil și blocat la creștere.

**Fișa de cont nu poate redeveni o balanță** (`core/fisa_cont.py`, `core/test_fisa_cont.py`,
23.08.2026). Primul artefact construit din pragul 3. Gardul apără exact ce pierdea `motor.carte_mare`:
**contul corespondent pe fiecare rând** și **cronologia**, plus soldul purtat cu **sensul** lui (D/C),
plus refuzul unei fișe pe un cont nenumit — o fișă goală arată ca *„acest cont n-a avut mișcare"*.

**RED-proof 2 mutații — și a doua e lecția.** Prima (contul corespondent devine contul însuși, adică
fișa redevine agregare) a picat imediat. **A doua (soldul își pierde sensul, `sens_sold = "D"` fix) a
TRECUT** — fiindcă toate rândurile din fixtura mea aveau sold debitor. Gardul a fost completat cu cazul
în care soldul trece prin zero D→C și cu cel de sold zero; abia atunci mutația a picat. **Propria
mutație a găsit gaura propriei gărzi** — de asta se probează în ambele direcții, nu doar pe cea care
pare evidentă.

**Adăugire la fișa de cont (aceeași tură):** poarta a respins-o **de două ori** pe reguli existente,
înainte de a intra. Prima: `test_afirmatii_tipate` — fișa întorcea un dict de proză, deși e o afirmație
despre datele firmei; tipată ca `fapt`, cu `temei_completitudine`. A doua: **rândul** era tot un dict;
devenit `RandFisa` (dataclass), cu conversia la dict mutată la margine. **Gărzile vechi au făcut
artefactul nou mai bun decât îl scrisesem** — și au prins exact clasa pentru care fuseseră construite.

**Codul fiscal al partenerului se cere la introducere** (`core/facturi_api.cere_cod_partener`,
`core/test_cod_partener.py`, 23.08.2026). **Prag 2.** Până azi `tert_cui` era **default de parametru**
(`None`) în amândouă funcțiile de creare, iar nimic nu-l verifica. Măsurat: 2 din 42 de facturi fără
cod, una către un **SRL**, intrată **prin aplicație**.

**Ce urcă defectul la prag 2**, cu vorbele deciziei: *o factură fără CUI de partener nu intră în D394 și
nu se poate corela în VIES — nu e o coloană goală, e o declarație incompletă la prima firmă reală.* Iar
codul nu se poate completa retroactiv de nimeni altcineva decât cel care a emis factura, deci momentul
e **introducerea**, nu un raport de mai târziu.

**Excepția e DECLARATĂ, nu dedusă**: `tert_pf=True`. Nu se ghicește din nume și nici din lipsa codului —
a ghici ar readuce exact tăcerea pe care o înlocuiește. Singurul apelant legitim fără cod (importul
WooCommerce) o declară, cu motivul scris lângă apel.

**RED-proof 2 mutații**: garda scoasă din `emite_factura` → anti-vacuu roșu (citește sursa ambelor căi,
nu doar existența funcției); excepția devenită tăcută (`tert_pf or True`) → 7 teste roșii. Mesajul e
gardat separat: poartă **consecința** (D394, VIES), **ieșirea** (persoană fizică) și **temeiul**
(art. 319 alin. 20), fără niciun nume intern de câmp.

**A patra regulă de domeniu la `scan_constante`: un modul care POARTĂ o valoare din registru e fiscal**
(`_poarta_valoare_de_registru`, 23.08.2026). Măsurat la întrebarea lui Costin: **după două lărgiri în
aceeași zi, 15 din cele 25 de funcții cu `cota = 21` ca default erau ÎNCĂ în afara domeniului** —
`avansuri`, `comodat_chirii`, `intracomunitar`, `inventariere`, `leasing`, `obiecte_inventar`,
`productie`, `sgr`. Niciunul nu se numește fiscal, niciunul nu citează legea, toate vorbesc prea puțin
pentru pragul de densitate — **dar fiecare ține o cotă de TVA**.

Criteriul e mecanic și **se întreține singur**: valorile se citesc din `common.COTE`, nu se scriu în
scan (altfel ar fi chiar constanta nesursată pe care o caută), iar când se schimbă o cotă în registru
domeniul se mută cu ea. **C: 135 → 162**, module văzute **85 → 97**. Calibrare în ambele direcții, pe
sursă construită anume (`cota=21` intră, `n=7` nu), plus anti-vacuu că registrul nu e gol.

**Lecția, a treia oară azi:** fiecare lărgire a părut completă. Prima a prins modulele care se numesc
fiscale, a doua pe cele care citează legea, a treia pe cele care vorbesc mult. **A patra a prins pe cele
care nu fac niciuna — dar poartă valoarea.** Un domeniu se măsoară pe ce caută, nu pe cât pare de larg.

**Cota de TVA nu mai are valoare implicită nicăieri** (25 de funcții din 14 module, 23.08.2026, R26).
Parametrul devine `None`, iar funcția **refuză** cu motivul scris: *o cotă scrisă în cod se rupe tăcut
de lege la prima schimbare, iar o operațiune veche are altă cotă decât una de azi.*

**Alegerea de a REFUZA, nu de a rezolva din registru pe dată, urmează o decizie deja scrisă în casă:**
`common.cota_ceruta` spune, din iulie, că *„NU se ghiceste o cota implicita, nici macar cota standard
(un default cu common.cota() ar fi tot o valoare inventata, doar actualizata)"*. Cele 25 contraziceau o
regulă existentă, nu doar buna practică.

**Ce a scos reparația:** **11 teste picau pe default** — adică îl testau (`test_stocuri` 9,
`test_versionare_formule` 2, `test_operatiuni_speciale` 1). Toate declară acum cota. Un test care se
sprijină pe o valoare implicită verifică defaultul, nu regula. Și **clichetul s-a coborât singur**:
`test_baseline_nu_e_stat` a picat imediat, fiindcă datoria devenise mai mică decât pragul. **C: 162 → 134.**

**Refuzul de cotă chiar se produce, nu doar se scrie** (`core/test_cota_fara_default.py`, 23.08.2026).
Întrebarea lui Costin după reparația R26: *„testele acoperă căile, sau doar confirmă că defaultul a
dispărut din semnătură?"* Răspunsul era **a doua** — cele 15 fișiere actualizate **dau** cota. Gardul
nou cheamă fiecare funcție care poartă refuzul **fără** cotă și cere `ValueError`. Ținta se citește din
**cod** (parametru `None` **și** `raise` în corp), nu din nume: funcțiile care tratează `None` ca „nu se
aplică" (`d101`, `facturi.calcul_tva`) sunt altă clasă și ar fi fals-pozitive.

**Și a găsit un al 26-lea caz în prima rulare**: `deconturi.nota_decont(cota_tva=0)`. **`0` e o cotă
validă (scutit)**, deci un default de 0 e aceeași clasă — pe care propria mea listă de excluderi o
ascundea (scosesem `0, 1, -1, 2, 100` ca „structurale"). **Și e singurul VIU din toată clasa**: ruta
punea `corp.get("cota", 0)` fără să cheme `cota_ceruta`, deci un decont cu cazare pe factură trimis
fără cotă primea tăcut 0% → **zero TVA deductibilă**. *Un default de 0 nu adaugă o cifră greșită — o
șterge pe cea corectă, ceea ce e mai greu de văzut.*

**Golden pe EFECT, nu pe formă, pentru cotele reparate** (`core/test_cota_efect.py`, 23.08.2026).
Costin: *„o cotă corectă care nu e verificată nu e reparată, e mutată. Nu «ce cotă a folosit», ci ce
iese."* Trei căi, alese fiindcă cota schimbă cifra în feluri **diferite**: `nota_decont` (cota decide
dacă apare linia 4426 și cu ce sumă — **singura cale vie**) · `tva_beneficiar` (cota apare de două ori,
4426=4427, se anulează în total dar **nu** în declarație) · `vanzare_marja` (cota intră în **formulă**,
prin suta mărită, nu se aplică pe preț).

**Cifrele sunt verificate și de mână, nu doar de cod**: 400 × 21/121 = 69,42 · 400 × 19/119 = 63,87 ·
333,33 × 21% = 70,00. Un golden care se calculează la fel ca funcția pe care o păzește e un ecou.
**Și măsura defectului e ea însăși un test**: diferența dintre decontul la 21% și cel la 0% e
**126,00 lei** — exact TVA-ul pe care tăcerea îl ștergea.

---

**Al doilea contor pe restanțe: `încercări`** (`core/test_reaprindere.py`, 23.08.2026). `reluări`
răspunde la *„câte s-au blocat de mai multe ori"*; `încercări` la *„câte au fost atinse vreodată"*.
Cele două nu se confundă: **R10 a fost încercată o dată și închisă în două minute, fără să fi fost
vreodată reluată** — cu un singur contor, munca aia era invizibilă. Gardat: câmpul e obligatoriu pe
fiecare restanță, e număr, iar `reluări > încercări` e incoerent și pică.

**Primul instrument care citește JavaScript** (`core/scan_js_texte.py`, `core/test_scan_js_texte.py`,
23.08.2026). Punctul orb declarat la interdicția 16 — 37 de fișiere, 15.125 de rânduri pe care niciun
instrument nu le citea — are de azi un scan. Măsoară frazele care ajung la om, grupate pe textul
normalizat: **1.785 de fraze, 143 în mai multe locuri**.

**Ce e nou la felul cum a fost construit: calibrarea negativă s-a scris ÎNAINTE de prima măsurătoare.**
Interdicția 76 avea patru instanțe, toate prinse târziu. Cele **șase moduri** pe care un scan de
JavaScript le poate greși sunt enumerate în antetul instrumentului, iar fiecare are un caz în gardă
(17 teste): backtick · comentariu · **`//` dintr-un șir care NU începe un comentariu** (un regex
greșește aici pe orice URL) · ghilimele dintr-un comentariu · zgomotul · anti-vacuu.

**Trei moduri sunt NEACOPERITE — și fiecare e probat printr-un test, nu doar declarat:** concatenarea,
eticheta de un cuvânt, textul din `.html`. *Un mod de eșec declarat și demonstrat e o limită; unul
declarat și nedemonstrat e o speranță.*

**Și euristica s-a strâns înainte de a raporta cifra, nu după:** prima formă lăsa să treacă fragmente
de markup (`> <div class=`, `).forEach((b) => ...`) — 214 „duplicări" din care o parte era zgomot.
După scoaterea învelișului HTML și a sintaxei de cod: **143**, toate fraze reale.

**Ecranul nu mai arată alt TVA decât factura salvată** (`core/test_aritmetica_in_prezentare.py`,
23.08.2026). **Prag 1, măsurat cu numere:** serverul rotunjește **pe linie**, ecranul aduna în `float`
și rotunjea o singură dată. Pe o factură obișnuită de **50 de rânduri × 3 × 19,99 la 21%**: serverul
**629,50**, ecranul **629,69** — **19 bani** pe care contabilul îi vedea și factura nu-i avea.

**Gardul are trei straturi**, fiindcă niciunul singur n-ar ajunge: (1) reproduce **ambele aritmetici**
pe aceleași date și cere să dea la fel; (2) **anti-vacuu pe cazuri** — păstrează forma veche și cere ca
datele de probă să **chiar despartă** cele două aritmetici, altfel testul ar trece fiindcă niciun caz
nu discriminează (`METODA` §15); (3) verifică pe **sursa JS** că rotunjirea pe linie e chiar acolo — o
reproducere rămasă verde peste o sursă schimbată ar minți. Plus clichet: o a treia formulă de cotă
apărută în prezentare, fără rotunjire, pică.

**Ce NU face, scris:** nu scoate regula fiscală din prezentare. Oprește **cifra greșită**, nu
**duplicarea** — pentru a doua e nevoie de o cale prin server.

**Calibrarea DETECTORULUI de formule fiscale din JS, prin relaxarea fiecărui filtru** (23.08.2026).
Interdicția 76 aplicată instrumentului, nu doar reparației — și de data asta cu **cifre pe fiecare
filtru**, nu cu o listă de temeri:

| filtrul relaxat | candidate | ce aduce |
|---|---|---|
| *(bază)* | **3** | cele trei formule |
| fără cotă literală | 34 | **+30, niciuna formulă** — dar scoate o clasă nouă |
| fără nume fiscal | 11 | +7, aritmetică generică |
| fără limita de lungime | 3 | **zero** |
| inclusiv `.html` | 3 | **zero** |

**Două rezultate care nu s-ar fi văzut altfel.** (1) Lungimea liniei și fișierele `.html` **nu ascund
nimic** — măsurat, nu presupus; două temeri scoase din listă. (2) Relaxarea pe cotă a scos o **clasă
structurală nouă**: `rip_ecran.js:148–150` scrie cotele ca **text în etichetă** — «CAS (25%)»,
«CASS (10%)», «Impozit (10%)» — lângă valori venite calculate de la server. Corecte azi, verificate
contra registrului, dar la o schimbare de cotă **cifra vine corectă și eticheta de lângă ea minte**.

**Și un fals pozitiv propriu, numit:** tiparul include `121` (suta mărită 21/121) și prinde codul de
obligație `121`. Îl taie filtrul pe numărul de ghilimele — care **nu e o regulă fiscală, e o
euristică**, și ar putea ascunde o formulă scrisă într-un șablon.

**Domeniul unui gard e o afirmație, la fel ca cifra lui** (24.08.2026). `DEFAULT_FISCAL_TACIT` citește
**Python**. Pe 23.08 a confirmat că cele 25 de valori implicite de cotă au dispărut din `core/` și
`main.py`; pe 24.08 s-a văzut că aceeași valoare implicită era scrisă de **trei ori** în
`static/js/ecrane/firme.js` și că **ea** era cea care rula. Gardul n-a greșit — n-a fost întrebat.
**Un gard cu domeniul pe un singur limbaj raportează verde despre limbajul pe care nu-l vede**
(`METODA` §17). Până când domeniul lui include `static/js/`, diferența e ținută de **R29**.

**Și o aserțiune anti-derapaj pe instrumentele care citesc JS** (24.08.2026): scoaterea comentariilor
și a șirurilor trebuie să **păstreze numărul de linii**. Prima rulare a calibrării pe nume neutre le
colapsa, deci raporta numere de linie ale **altor** linii — un instrument care trimite omul la locul
greșit. Acum sursa curățată se compară cu originalul, linie cu linie, înainte de orice măsurătoare.

**Un AN scris în cerere îngheață ecranul în trecut** (`core/test_an_hardcodat.py`, 24.08.2026).
Întrebarea lui Costin era despre **valori** îmbătrânite în JS. Măsurat: **niciuna** — nicio cotă
depășită (19%, 9%, 5%) nu apare de sine stătătoare în textul ecranelor, iar cele prezente se
potrivesc cu registrul. Ce s-a găsit e o formă **vecină și mai tăcută**: `rip_ecran.js:142` cere
`/rip/d212/2025`, cu anul în URL. Nu afișează o cifră greșită — o afișează pe cea de anul trecut,
corect etichetată, și nu poate ajunge la anul curent. Clichet **1**, ancorat pe fișier: dacă se
repară ăla și apare altul, cifra ar rămâne 1 și gardul ar tăcea — de-aia se verifică și **care**.

**Și un fals negativ al propriului meu scan, prins pe cazul cunoscut** (24.08.2026). Prima formă a
lui `core/scan_valori_afisate.py` arunca șirurile care conțin `class=` sau `style=`, ca zgomot de
CSS. În codul ăsta **textul afișat trăiește înăuntrul șabloanelor HTML**, deci filtrul a aruncat
chiar singurul caz pe care îl știam dinainte — eticheta cu salariul minim din `rip_ecran.js`. Corectat:
se scot **etichetele**, rămâne **textul**. Cifra a urcat de la 25 la **46**. Calibrarea pe un caz
cunoscut nu e o formalitate: aici a fost singura care a arătat că instrumentul măsura altceva.

**Cotele din ecrane se confruntă cu registrul, nu cu memoria** (`core/test_valori_fiscale_js.py`,
24.08.2026). Nouă teste: șase perechi ecran↔`COTE` (CAS 25% · CASS 10% · impozit 10% din `rip_ecran`;
TVA 11% și 21% din Raportul Z al `firme.js`), plus anti-vacuu pe ancore, calibrare negativă, și
verificarea că fiecare cheie confruntată chiar există în registru cu temei. **RED-proof prin mutație:
cu `CAS (24%)` în ecran, gardul cade și scrie ce zice registrul.** Când o cotă se schimbă, testul
numește ecranul rămas în urmă — vezi `METODA` §18.

**Calibrarea pe nume neutre a devenit clichet** (`core/test_aritmetica_in_prezentare.py`, +4 teste).
Măsurat: **2**, ambele aritmetică pe date calendaristice, **zero fiscale**. Cifra nu mai trăiește
într-un raport, ci într-un test care cade dacă apare a treia. Include o calibrare **pe propriul mod de
eșec**: curățarea comentariilor trebuie să păstreze numărul de linii, altfel tot ce raportează gardul
trimite omul la locul greșit.

**Și o greșeală proprie, în chiar fișierul de gărzi:** am definit `_JS` peste un `_JS` care exista deja
în `test_aritmetica_in_prezentare.py` și arăta spre `static/js/ecrane`. Redefinirea a mutat tăcut
domeniul a două gărzi vechi, care au picat cu *«fișier inexistent»*. **Un nume reciclat într-un fișier
de gărzi nu e o scăpare de stil — mută domeniul altui gard.** Redenumit `_JS_TOT`, cu motivul scris
acolo.

**Predarea își arată vechimea, iar avertismentul nu poate dispărea tăcut**
(`core/test_predare_proaspata.py` + `scripts/githooks/pre-commit`, 24.08.2026). Versiunea de atunci a
lui `PREDARE_LANT.md` era din **22.08** și purta **trei afirmații false** — starea pe alt commit,
cifra `131` (invalidată între timp) și un front deja rezolvat. Costin: *«un PREDARE_LANȚ care
instruiește sesiunea nouă să-l citească primul și conține trei afirmații false e mai rău decât unul
absent — cine îl citește n-are cum să știe care rând mai e adevărat.»*

**Ce s-a construit.** Predarea are acum **antet cu dată și commit**, ca `CONFORMITATE`. Poarta
**avertizează** când `HEAD` a plecat cu peste **10** commituri de la ultima rescriere — măsurat la
instalare: era în urmă cu **68**. Șase teste țin de mecanism: data există și e o dată reală · regula
*«se rescrie înainte de fiecare oprire»* e scrisă · blocul din hook nu poate fi șters · **nu poate
deveni blocaj** (decizia a fost avertisment: un blocaj pe vechime ar face din predare un impozit pe
reparațiile mici) · anti-vacuu pe hook · cifra 131 nu poate reapărea nemarcată. **RED-proof pe trei
direcții**, toate cu restaurare verificată identic.

**Ce NU face, declarat:** nu verifică dacă ce scrie în predare e **adevărat** — asta nu se măsoară. Și
**un `/clear` nu se poate garda deloc** din git; se gardează doar commitul.

**Traseele nu mai sunt proză, iar harta nu poate rămâne în urma codului**
(`scripts/scan_trasee.py` + `core/test_trasee.py`, 25.08.2026). Până azi, „câte trasee sunt", „câte se
pot scrie din cod" și „care firmă poate parcurge care traseu" erau **amintiri**: comanda numea 25,
`TRASEE.md` Partea X numea 9, și nimic nu le putea reface. *O cifră care nu se poate recalcula nu e o
măsurătoare.*

**Ce s-a construit.** Inventarul e declarat în instrument — **35 de trasee** — iar instrumentul
verifică **acoperirea**: fiecare dintre cele **400 de rute** din `main.py` intră fie într-un traseu,
fie într-una din suprafețele declarate ne-documentare (91). **Orfane: 0**, iar o rută nouă care nu
intră nicăieri **pică testul**. Clasificarea e mecanică, din două fapte măsurate — atinge o margine?
scrie într-o tabelă? — și dă **MECANIC 27 · PARȚIAL 3 · MANUAL 5**, clichet.

**Marginea NU e „modulul cheamă rețeaua".** `requests` nu deosebește o trimitere de o citire, iar
închiderea tranzitivă peste toate modulele de rețea face din `observare` (email) o margine și trage
după el jumătate din aplicație — clasa n-ar mai deosebi nimic. Deci `MARGINI` e **enumerată, cu
motivul lângă fiecare**, și există `NEMARGINI` care spune de ce celelalte nu sunt: `duk` rulează local
prin `subprocess`, `curs_bnr` are istoric local, `observare` trimite o **copie**, nu artefactul.

**Trei greșeli ale instrumentului, toate în direcția „lipsește" sau „e altceva", toate prinse prin
citire directă înainte de a ajunge în document:**
1. „fără gardă" pentru rute păzite prin argument (`Depends(cere_cabinet)`);
2. „nu verifică rolul" pentru rute care îl verifică **în corp** sau printr-un **ajutor**
   (`_cer_admin_cabinet`) — prinsă citind `/asistenti/{uid}/permisiuni`;
3. **atribuia ruta de NIR modulului `salarizare`.** Multe rute își importă modulul **în corp**
   (`from core import stocuri_api as _s`), iar `_s` e refolosit în zeci de locuri. **O atribuire falsă
   e mai rea decât o absență** — trece verde. Are test propriu.

**Și o a patra, în măsurătoarea de firme, nu în instrument:** zece tabele au ieșit „absente pe toate
cele 17 firme". **Nouă dintre ele existau** — trei în `public`, partajate cu `tenant_id` (de-aia
traseul declarației arăta „nicio firmă" pe o instalare cu 55 de declarații depuse), șase sub alt nume
(`factura_linii`, `state_plata`, `perioada_confirmata`, `clienti`+`furnizori`, `notificari_scadenta`,
`contracte_sabloane`). **Nume ghicite, necăutate la sursă.** De aceea lista de tabele se **regenerează
din bază** (`--tabele`), nu se scrie în cod.

**Ce NU face, declarat:** nu spune că un traseu e **corect**. Spune că harta acoperă codul, nu că
drumul e bun. Nu vede „ce trebuie să fie adevărat după fiecare pas" — aia e decizie, nu cod.

**Cele 35 de trasee sunt SCRISE în document, dar generate din cod** (`TRASEE.md` Partea XII +
`scan_trasee.py --md`, 25.08.2026). Alternativa era să le scriu de mână — și ar fi fost **al doilea
loc în care trăiește starea**, exact ce interzice `PLAN_LUCRU.md` („Unde stau"). Așa, documentul
poartă conținutul (pașii cu gardă și rol, modulele, tabelele, stările, refuzurile, marginea, firmele
care îl pot exercita), iar `core/test_trasee.py` verifică să fie **identic**, caracter cu caracter, cu
ce produce instrumentul. **RED-proof prin mutație**, cu restaurare verificată prin amprentă: o cifră
schimbată cu mâna în bloc pică testul și îi spune omului linia.

**Numerele de firme trăiesc ca fișier** (`scripts/trasee_firme.json`, regenerat cu `--firme`), nu ca
apel la bază — altfel redarea n-ar fi determinist comparabilă la poartă, iar testul doc↔cod n-ar putea
rula fără DB. Cu trei gărzi pe el: fișierul există și acoperă toate cele 17 firme · nicio firmă nu e
complet goală fără să se vadă · **un traseu fără tabelă proprie NU poate raporta „zero firme"**
(interdicția 32 aplicată instrumentului: un necunoscut rotunjit la zero ar umfla exact cifra care
contează).

**Ecranul nu mai poate numi „de depus" ce serverul refuză** (`core/test_coada_gata_de_depus.py`,
R41 partea II, 25.08.2026). Reparația nu e o etichetă schimbată: e că **nu mai există două
definiții**. `_poarta_verdict` — care refuză depunerea — și `lista_coada` — care alimentează
ecranul — cheamă **aceeași funcție**, `gata_de_depus`. Gardul asertează **pe structură** (AST:
cine cheamă ce), fiindcă o condiție rescrisă inline în poartă ar arăta identic la citire și ar
putea diverge tăcut.

**RED-proof pe două mutații**, amândouă restaurate cu amprentă verificată: condiția rescrisă
inline în poartă → roșu; `gata_de_depus` care întoarce mereu `True` → roșu. A doua e chiar
calibrarea pe propriul mod de eșec: un instrument care spune „gata" despre orice ar fi trecut
toate celelalte aserțiuni.

**Ce a prins proba comportamentală și niciun test nu prindea:** prima formă a cardului de pe
tabloul cabinetului număra **toate** rândurile din răspuns — deci includea o declarație **deja
depusă** — iar cifra de pe card (3) nu era despre aceeași populație ca cifra de pe ecran (2).
*Două cifre sub aceeași etichetă, despre populații diferite: aceeași clasă cu R41, cu un nivel
mai sus.* Proba are acum o aserțiune care compară chiar cele două cifre.

**Ce NU acoperă, declarat:** ecranul cozii nu e în `nav_ecrane.ECRANE`, deci scanul vizual/a11y
**nu-l atinge** — `test_acoperire_vizuala` trece pe el **vacuu**. Comportamentul și consola sunt
probate cu `frontend_test/proba_r41_coada.py` (desktop + Pixel 5), nu axe/contrast pe toată
suprafața. Gaură numită, nu descoperită mai târziu.

**O declarație nu mai poate intra în coadă legată de o firmă care nu există**
(`core/test_coada_firma_exista.py`, R44 reluată, 25.08.2026). Măsurat: **1 din 3** elemente din
coadă avea `tenant_id` = 13245, care nu e în `public.tenants` și n-are schemă. Refuzul stă în
`adauga_in_coada`, nu ca cheie străină — `declaratii_coada` e tabelă **partajată**, iar firmele
trăiesc și ca **scheme**; o cheie străină ar lega două modele de date diferite. Trei teste, pe
structură: interogarea există · codul de refuz există · **refuzul e ÎNAINTEA `INSERT`-ului**,
fiindcă unul scris după n-ar refuza, ar curăța. Clichet **1** pe orfanii existenți: rândul de azi
rămâne până se decide ce se face cu el, dar al doilea nu mai poate apărea.

**Reaprinderea a funcționat, prima dată de când e gardată.** R44 avea condiția *„la primul commit
care atinge `core/coada_api.py`"*; R41 partea II l-a atins, iar `core/test_reaprindere.py` a **oprit
commitul** până la reluare. Nu e o observație de proces — e prima dovadă că garda din 23.08 chiar
prinde momentul, pe o restanță care altfel ar fi așteptat.

**Cele 187 de locuri de verificare nu pot rămâne fără pas** (`TRASEE_VERIFICARI.md` +
`core/test_trasee.py`, 25.08.2026). Documentul e **singurul care nu se generează**: scheletul se
produce o dată cu `--verificari`, conținutul îl scrie omul. Gardul cere ca **fiecare pas care schimbă
ceva** să aibă un loc, și ca locurile să nu dispară. **Nu** rescrie fișierul — regenerarea peste el ar
șterge tot, și scrie asta în capul documentului.

**De ce locuri doar pe acte, nu pe rute:** pe un `GET`, *„ce trebuie să fie adevărat după"* e vid prin
construcție — n-a schimbat nimic. Prima formă a scheletului avea **309** locuri, din care o treime
fără sens; a doua are **187**, câte unul per act.

**O mutație care dezactivează un REFUZ transformă un test care nu scrie într-unul care scrie**
(25.08.2026, instanța: RED-proof-ul lui R44). Testul cheamă `adauga_in_coada` cu o firmă inventată
și verifică refuzul — pe cod sănătos nu scrie nimic, fiindcă refuzul e înaintea `INSERT`-ului.
Cât mutația ținea garda pe `if False`, aceeași chemare a **inserat**: două rânduri orfane în
`public.declaratii_coada`, într-o tabelă partajată. Prinse imediat (clichetul de orfani a sărit de la
1 la 3) și șterse — dar numai cele cu id-ul inventat de mine; rândul real, subiectul lui R44, n-a fost
atins.

*E aceeași clasă cu „sonda de citire scrie până n-o dovedești", cu o față nouă: nu sonda scria, ci
**mutația** a făcut-o să scrie. Consecința practică: un RED-proof pe un refuz curăță după el, sau
rulează pe schemă efemeră. Verificarea nu e „testul a picat", ci „testul a picat ȘI n-a rămas nimic în
urmă".*

**Un artefact produs se păstrează, iar producerea lui e un ACT** (`core/artefacte.py` +
`core/migrare_artefacte.py` + `core/test_artefacte_pastrate.py`, R45, 25.08.2026). Cele cinci
câmpuri decise de Costin — artefactul, momentul, autorul, amprenta conținutului, numărul
exemplarului — plus verdictul cu amprenta fișierului validat, la declarații. **Un singur loc,
nu patru**: aceeași cauză, aceeași reparație; patru implementări ar fi însemnat patru
vocabulare pentru același lucru.

**Obstacolul, care e partea instructivă.** Trei din cele patru artefacte se produceau pe
**GET**, iar un GET n-are voie să scrie (interdicția 6, `core/test_get_fara_scriere.py` — garda
ieșită din cele 24 de rânduri lăsate în `state_plata` de o simplă deschidere de ecran). Deci
*„se păstrează"* n-a fost o adăugare de coloane: a cerut ca **producerea lor să devină un act**.
Cele trei rute au trecut pe POST, împreună cu apelurile din ecran. Erau deja declanșate de un
buton — **doar metoda le contrazicea fapta**.

**Ce a prins gardul, în chiar commitul lui:** `export-winmentor` trecuse pe POST și **nu păstra
nimic**. *O rută care și-a schimbat metoda fără să capete fapta e mai rea decât una nemodificată
— arată reparată.*

**Și două aserțiuni de-ale mele, mutate de pe text pe structură** (METODA §23): verificau
`"UNIQUE (fel, cheie, exemplar)" in DDL` — un șir în textul DDL-ului. O constrângere comentată
ar fi trecut, iar o reordonare de coloane ar fi picat degeaba. Acum se citesc din
`information_schema`: coloanele și constrângerea, așa cum există în bază.

**Al patrulea artefact NU s-a construit, deliberat:** auditul de preluare se randează la
deschiderea ecranului, deci un POST ar produce un exemplar **la fiecare privire**. Îi trebuie un
act propriu în ecran — o decizie de design, nu una de-a mea.

**Cifra care se schimbă când o citești altfel: 3 vs 77** (R42, reclasificare pe fapt,
25.08.2026). Prima clasificare a rutelor fără rol a folosit **tipare pe calea rutei** și a găsit
**trei** care ies către un om. A doua nu se uită la nume, ci la ce **scrie** și pe unde **ajunge**:
`SE_DEPUNE` = scrie într-o tabelă pe care o citește un modul `core/d*.py`; `SE_PREDĂ` = scrie
într-o tabelă de artefact dat unui om; `IESE_AFARĂ` = ajunge la un modul-margine sau trimite un
email, detectat din AST. Rezultat: **77 din 134**.

*Nu e o corectură de cifră, e diferența dintre a citi eticheta și a citi fapta.* Aceeași clasă cu
„nomenclatorul derivat dintr-o sursă secundară": un criteriu aplicat pe nume măsoară cum și-a
numit cineva rutele, nu ce fac ele.

**Și o consecință proprie, prinsă doar la remăsurare:** reparația lui R45 a **înrăutățit** cifra
lui R42 cu trei. Trei rute care produceau artefacte pe `GET` au trecut pe `POST` — devenind acte
— și au intrat în populația „schimbă date, fără rol". *O reparație care schimbă populația altei
măsurători trebuie s-o remăsoare, nu să presupună că n-a atins-o.*

**A treia absență falsă afirmată citind un singur loc, în două zile.** Scrisesem că auditul de
preluare *„se randează la deschiderea ecranului"* — dedus din `api.get`, fără contextul lui. E
deja în spatele unui buton (`ruleazaAudit`). Predecesoarele: „rută fără gardă" pentru rute păzite
prin argument, și „modulul nu scrie nimic" pentru tabele necalificate. **Toate trei în aceeași
direcție: lipsește.**

**Un câmp trimis și necerut e ignorat TĂCUT, iar ruta răspunde 200**
(`scripts/scan_contract_ecran.py` + `core/test_contract_ecran_ruta.py`, R51, 25.08.2026).
Ipoteza pusă în față era *„ecranul trimite un câmp, ruta cere altul, iar diferența e o
literă"*. Măsurat pe **67 de perechi** ecran↔rută: **una** singură diferea — și nu în direcția
bănuită. Nu un 422, ci o **scriere care nu se întâmplă**: ecranul de salariați trimitea
`data_incetare`, `SalariatEdit` n-o avea, pydantic o arunca înainte ca ruta s-o vadă, iar
răspunsul era `{"ok": true, "neschimbat": true}`.

**Probat pe ruta reală**, nu dedus: `PUT /tenants/4784/salariati/49` cu `{"data_incetare":
"2026-08-31"}` → **200**, coloana rămâne `NULL`. Ecranul spune chiar acolo *„la plecare NU se
șterge salariatul — se completează data încetării"*: singura cale corectă era cea care nu
funcționa, iar salariatul plecat rămânea în serviciu și în D112.

**Instrumentul a raportat întâi 30 de diferențe, și toate primele trei verificate erau false.**
Extractorul de chei vedea doar `cheie: valoare` și rata **prescurtarea ES6** (`{ an, luna }`) —
forma cea mai des folosită în ecrane. Calibrarea pe cazuri cunoscute a prins-o **înainte** ca
cifra să ajungă într-un raport. Rescris, cifra e **1**, iar după reparație **0**. Gardul are
teste pe chiar modul ăsta de eșec, plus unul anti-vacuu: dacă extractorul se strică și nu mai
citește nimic, „zero diferențe" ar trece — deci se cere ca numărul de perechi comparate să
rămână ≥ 60.

**Ce NU vede, declarat:** 62 de apeluri merg spre rute **fără model pydantic** (`corp: dict`),
unde nu există contract de verificat; 18 au corpul într-o variabilă sau cu răspândire. Alea se
numără ca domeniu neatins, nu ca fiind în regulă.

**Punctul orb al măsurătorilor mele de rol, găsit tot azi:** am numărat mereu doar rutele care
**schimbă date**. Un document care ajunge la un om poate pleca și pe un **GET** — un PDF, un
atașament. Măsurat: **25** de rute predau un document, **17** fără niciun rol, toate GET; scăzând
paginile publice, rămân **9 documente ale firmei** predate fără verificare de rol, între care
`GET /tenants/{}/fluturas/{salariat_id}` — fluturașul unui salariat. *„Iese către un om" nu e
totuna cu „scrie ceva", iar clasificarea mea le confundase.*

---

## Nomenclatoarele se iau din NORMĂ; validatorul e constrângere (25.08.2026, C6)

`core/nomenclatoare.py` + `core/test_nomenclator_pe_norma.py` — **8 teste, 12 mutații prinse.**

Decizia lui Costin: *„Norma câștigă. Validatorul e constrângere, nu sursă."* Răspunsul era deja
scris în `PLAN_ARHITECTURA`, Partea 0, Pasul 4, iar restanța îl ceruse de cinci ture. Vezi METODA
§25.

**Ce s-a găsit citind cele patru nomenclatoare la sursă, nu în comentariile lor:**

| | Ce spune NORMA | Ce spunea codul despre sine |
|---|---|---|
| `d390.TIPURI` | OPANAF 705/2020 **enumeră** exact cele șase (L, T, A, P, S, R) | „confirmat pe validatorul D390_11" |
| `d394.TIPURI` | **enumeră** exact cele opt — dar norma în vigoare e **OPANAF 2194/2025** (MO 852/17.09.2025), nu 77/2022 din cod | „tool-ul urmează validatorul, ca la D101" |
| `d390.TARI_UE` | **NU enumeră** — trimite la „codul țării care a emis codul de TVA" | „nomenclator oficial țări" |
| `d301.VALUTE` | **NU enumeră** — „tipul valutei (**de exemplu**: USD, euro…)" | „ancorat pe validatorul instalat D301_9" |

Două dintre patru aveau normă deschisă și lista închisă tăcut de arbitru. Una cita o formă depășită
a ordinului — iar OPANAF 2194/2025 era **în corpus**, necitit. Eliminarea lui `ASI`, decisă în
08.2026 pe autoritatea validatorului, e de fapt **susținută de normă**; nimeni nu verificase,
fiindcă validatorul închisese discuția.

**Consecința pe care o scrie acum codul, și n-o scria:** o operațiune făcută legal într-o valută
din afara celor 20 **nu se poate depune** prin acest instrument. Nu e o regulă fiscală — e limita
arbitrului, și nu se poate repara în cod. Se poate doar numi.

**Perechea de gărzi = ierarhia.** `test_nomenclatoare_ancorate.py` (04.08) rămâne exact ce era —
proba de nivel 3, pe validatorul instalat — dar titlul lui („ancorat pe validator, **nu pe un
document**") inversa ierarhia și de aceea a câștigat tăcut împotriva METODA §13, scrisă cu două zile
înainte în sens opus. Gardul nou cere sursa; împreună cer amândouă niveluri și **consemnarea
diferenței**.

**Dezacordul e obiect, nu proză** (`Dezacord(cine, ce, consecinta)`): legătura cu arbitrul se
asertează prin **identitate**, nu căutându-i numele în text — prima formă a gardului făcea exact
ce interzice METODA §23 și a fost prinsă de `test_garzi_pe_text`. Câmpul `consecinta` e obligatoriu
și lung: partea incomodă — *ce nu se mai poate face* — lipsea din toate comentariile vechi.

**Clichet: 6** nomenclatoare probate pe validator n-au încă sursă normativă. Coboară prin citire,
una câte una — o citire copiată ar trece verde și ar fi mai rea decât absența.

---

## R42, cele patru răspunsuri — și clasa care era mai mare decât întrebarea (25.08.2026)

`core/test_r42_criteriu.py` — **16 teste, 5 mutații probate**, plus trei probe funcționale pe
schemă efemeră.

**Ce a ieșit peste întrebare.** Costin a decis despre *„cele 24 de rute `nota-*`"*: nu
`admin_firma`, ci verificarea de perioadă de la P15. Am scris gardul pe **structură** — orice rută
care inserează în `inregistrari` — și el a găsit **încă 19** care scriu note și nu verificau
nimic: operațiunile de regim special, amortizarea, contabilizarea unei facturi, raportul Z,
aprobarea unui bon. Motivul deciziei (*„o notă care a intrat în evidență nu se șterge, se
stornează"*) le acoperă pe toate. **39 de rute** au primit verificarea.

**Ce lipsea, exact.** `_cere_perioada_deschisa` păzea **editarea, ștergerea și validarea** unei note
care există. **Crearea intra pe altă ușă.** O notă nouă datată într-o lună închisă e tot o
modificare a perioadei închise — doar că nu trecea pe unde se uita nimeni.

**Trei gărzi au căzut pe codul meu nou, și una a scos un defect mai vechi:**

1. **Atribuire falsă, a doua față.** `main.py` are `from core import casa_api as _c` la nivel de
   modul. Am scris `with conn.cursor() as _c:` într-o rută, iar instrumentul a raportat că ruta
   cheamă `casa_api` — și, prin el, **trei tabele în care nu scrie**. Reparația din tura trecută
   acoperea aliasurile locale de **import**; aici numele e legat de o **variabilă**. Reparat în
   ambele locuri (codul meu **și** instrumentul), cu calibrare în ambele direcții.
   **La regenerare au dispărut DOUĂ atribuiri false, nu una:** a mea, plus
   `rapoarte_comerciale_api` (cu tabela `rapoarte_salvate`) pe traseul statului de plată, care era
   în inventar de la început. *O absență s-ar fi văzut; o atribuire falsă trece verde și intră în
   document.*
2. **Nume de tabel inventate.** Generatorul de loturi arăta `factur (UPDATE)` și
   `validata (UPDATE)` — fragmente scoase de regexul de SQL, una fiind o **valoare de stare** luată
   drept nume de tabel. `construieste` filtra deja pe tabelele cunoscute; `pasii_ordonati` nu.
   *Un nume de tabel inventat într-o listă de verificat cere să se verifice ceva ce nu există.*
3. **Prima formă a detectorului vedea ZERO.** Căuta `insert into {schema}.inregistrari` într-un
   f-string, unde `{schema}` e un `FormattedValue`, nu text — deci textul real e
   `insert into .inregistrari`. Anti-vacuul a prins-o: *„detectorul vede doar 0 rute — s-a stricat?"*

**Ce NU s-a schimbat, cu cifra gardată: 7.** Operațiunile de regim special rămân la `cere_cabinet`
— sunt **introducere**, iar criteriul spune explicit că introducerea o poate face un asistent.

## R52 — clichetul, și confruntarea celor două instrumente

Măsurătoarea din R52 a dat **25** de rute care predau un document, **17** fără rol. Gardul, cu
**aceleași marcaje** dar citind doar **corpul rutei**, găsește **18** și **8**. Diferența nu e
progres — e **raza**: măsurătoarea a urmărit și ce livrează modulele chemate. Clichetul e pus pe
**8**, cifra pe care instrumentul o poate recalcula; restul până la 17 **nu sunt păzite acolo**, și
scrie asta. *Un clichet pe o cifră care nu se poate reproduce ar fi o amintire.*

---

## R33 — semnalul notă-vs-D112: la propunere, și semnalează (25.08.2026)

`core/test_coerenta_salarii.py` — **10 teste, 6 mutații probate**, plus o probă pe procesul viu,
desktop și Pixel 5.

**Ce a ieșit legând verificarea: modulul era nelegat în întregime.** `note_lunare` —
contabilizarea statului de plată — n-avea niciun apelant. Salariile nu deveneau niciodată notă
contabilă. Restanța număra funcții publice fără importatori; lipsea **actul**, nu doar verificarea.

**A doua instanță de R16 în același fișier.** Docstringul promitea *„nota se scrie DOAR dacă
totalul coincide… refuzăm să scriem"*. Nimic nu scria și nimic nu refuza. Prima instanță era
comentariul din `salarizare.py:296`; a doua e chiar promisiunea de garanție a modulului. Amândouă
verzi, fiindcă testele cheamă funcțiile direct.

**Semnalul arată AMBELE cifre.** Divergențele sunt obiecte — `{eticheta, cont, nota, declaratie,
diferenta, toleranta}` — nu fraze: cifrele nu se pot compune înapoi dintr-o propoziție. Pe firma de
probă, semnalul a găsit o divergență reală: **impozit pe venit, nota 161,12 în 444 vs D112 204,00,
diferență 42,88.**

**Prima probă a dat zero, fals.** Înlocuia intrări în `sys.modules`, dar `from core import d112`
citește atributul de pe pachet — deci măsura funcția reală pe o bază inexistentă. Rescrisă cu
`monkeypatch` pe funcții.

**Ce NU face gardul, declarat:** nu verifică plasarea pe ecran (asta e proba vizuală), și nu spune
nimic despre celelalte trei module nelegate — `echilibru_perioada` rămâne nelegată, decizie de prag 2.
**CORECTAT 25.08.2026:** nu e „logică paralelă". Rulate amândouă pe aceleași date, `echilibru_perioada`
și `verificatoare.verifica_balanta` au moduri de eșec **disjuncte** — fiecare prinde exact ce cealaltă
ratează. Măsurătoarea, calibrarea pe ambele direcții și ce nu vede: `CONFORMITATE.md`, R33.

## R33, varianta b′′ — echilibrul e UN verdict din DOUĂ verificări (26.08.2026)

**Categoria: Integritate în timp (C3) + Verificare care nu se întâmplă.**

`core/echilibru_perioada` e **legat** din `main._verificari_contabile`. Nu înlocuiește
`verificatoare.verifica_balanta` și nu e înlocuit de ea: modurile lor de eșec sunt **disjuncte**,
măsurat 25.08 pe aceleași date. Cele două se compun într-un singur verdict `echilibru`, la
**construcție** (`verdict_echilibru`, pură), iar contabilul vede **un rând** cu ce a găsit fiecare.

**Ce a ieșit din `verifica_balanta`: ramura `BALANTA_INEGALA`.** Era tautologică pe intrarea reală
— `balanta()` adaugă aceeași sumă pe ambele părți, deci totalurile sunt egale prin construcție
(0 din 2000 de seturi aleatoare o puteau face să pice). Motivul e scris pe locul ramurii, iar codul
e scos și din `common.CODURI`, ca să nu poată fi rechemat de cineva care n-are de unde ști.

**GARDĂ NOUĂ: `core/test_echilibru_legat.py`** — 14 teste, **5 mutații** probate.
Ce face imposibil: reîntoarcerea ramurii tautologice · o ramură a verdictului care nu poate deveni
roșie · pierderea vreunuia din cele trei moduri de eșec · reîntoarcerea orbirii la contul din
spații · rotunjirea unei verificări care n-a rulat la „în regulă".
**Ce NU face, declarat:** nu atinge baza (readerul e testat separat), nu verifică randarea, și nu
pretinde că cele trei moduri de eșec sunt TOATE modurile posibile.

**LIMITA DECLARATĂ a feliei de ledger:** luna curentă, doar notele `validata`. O ciornă cu contul
rupt se vede abia după validare, când devine evidență.

## R54 — contul din corpul cererii trece prin `strip()` (26.08.2026)

**Categoria: Intrare date.** Tiparul `str(corp.get("cont_x") or "<implicit>")` **pare gardă și e
mască**: `or` transformă `None` și `""` în implicit, dar lasă `"   "` să treacă verbatim. 19 situri
reparate cu tiparul deja corect din același cod.

**GARDĂ NOUĂ: `core/test_cont_din_corp_normalizat.py`** — pe **AST**, nu pe text: se cere ca nodul
care citește contul să aibă un strămoș `.strip()` care îl conține. Clichet **gol**. RED-probată.
**Calibrare găsită de gard pe el însuși la prima rulare:** `corp.get("continut")` — conținutul unui
mesaj — trecea drept cont. Prefixul „cont" era prea larg; cheia e `cont` exact sau `cont_<ceva>`.
**Ce NU face, declarat:** oprește contul **alb**, nu contul **greșit**. `"7O7"` cu litera O trece.
Confruntarea cu `plan_conturi` e decizie deschisă — R54.

## Cele patru decizii din 26.08.2026, și ce garduri au lăsat în urmă

**R54 — contul din corpul cererii se REFUZĂ dacă nu e în planul firmei.** Un singur loc:
`core/cont_valid.py`. Legat în **19** din 27 de citiri; **8** rămân în clichet, fiecare cu motivul
**citit la sursă**, nu presupus. Gard: `core/test_cont_din_corp_normalizat.py`, 8 teste, clichet
bidirecțional ancorat pe **fișier + funcție + expresie** (nu pe linie — liniile se mută).
**Ce NU face, declarat:** oprește contul care nu există; nu spune dacă e contul *potrivit* pentru
operațiune. Aia rămâne judecata contabilului.

**Poarta de coadă s-a mutat la INTRARE.** `POST /coada` validează cu DUK înainte de a insera, iar
verdictul se scrie odată cu elementul, cu amprenta. `gri` nu trece drept favorabil (P6); portița e
`motiv_trecere`, aceeași ca la aprobare și depunere, și se păstrează cu autorul.
**Ce NU face:** nu împiedică o declarație validă să devină stătută după aceea — aia rămâne treaba
lui `verdict_din_rand`, care marchează `statut` când amprenta diferă.

**Baseline-urile vizuale NU se urmăresc în git.** `.gitignore` acoperă tot directorul; cele 5
urmărite s-au scos din index (rămân pe disc). Iar `baseline_scan` spune acum, în modul implicit,
dacă referința e **NOUĂ** sau **RESCRISĂ**, și scrie în antet că `FLAKINESS` e self-diff, nu
comparație. Motivul lui Costin: *„azi absența ar da vid, iar vidul arată ca stabilitate."*
**Instanța e a mea:** am raportat „STABIL 0px" pentru un ecran nou ca și cum ar fi fost o
comparație, și era self-diff.

## Lanțul plan-conturi → jurnal → validare, închis (26.08.2026)

**Ce a arătat măsurătoarea, și e mai important decât rolurile puse:** din **40** de rute care scriu
în `inregistrari_linii` în corpul lor, **36 scriu `ciorna`** — propun, nu produc evidență. Doar
**3** scriau `validata` direct, sărind peste validare: `amortizare`, `bonuri/{id}/aproba`,
`horeca/raport-z`. Toate trei au primit `admin_firma`.

**Deci poarta reală nu e pe cele 36, e la VALIDARE** — `POST /jurnal/{id}/valideaza`, care cere de
azi `admin_firma`. Plus `POST /plan-conturi`, fiindcă cine adaugă un cont poate face să treacă
orice refuz al lui `cont_valid` (R54).

**Nu e o clasă nouă:** cele trei sunt exact bugul reparat de R33 la nota de salarii pe 25.08
(*„status='validata' direct — ocolea patru-ochi"*), rămas negeneralizat în trei locuri.

**Ce NU face, declarat:** nu există încă un test care să asertea pe **nume** că exact rutele care
scriu `validata` cer rol. Azi e o măsurătoare, nu un clichet — și se spune.

## Ruta de API nu mai primește un fapt al firmei din corpul cererii (26.08.2026)

`POST /api/v1/firme/{id}/facturi` lua **`platitor_tva` din corpul cererii**, implicit `True`, în
timp ce ruta din ecran îl citește din `firma_profil`. Valoarea decide **cota de pe liniile
facturii** (`_potriveste_linii` → `cote_tva.potriveste_cota`): un integrator care n-o trimitea ar
fi facturat cu TVA o firmă **neplătitoare**. Interdicția **45** (P20). Reparat: se citește din
firmă. Plus numele beneficiarului, care nu era cerut.

**Măsurat înainte de reparație: `public.api_chei` = 0** — nicio cheie n-a fost creată vreodată,
deci efectul n-a fost produs. **Ce rămâne diferit, declarat:** poarta „pleacă marfa acum?" nu se
poate pune pe o cale neinteractivă fără să alegem în locul integratorului — R57.

## Rolul se cere după CE FACE ruta, nu după cum se numește (26.08.2026)

**`core/test_rol_pe_efect.py`** — 8 teste, **3 mutații** probate. Cerut de Costin după ce
măsurătoarea manuală s-a înșelat de trei ori în trei zile, de fiecare dată pe un **proxy**: numele
funcției (R33), numele grupului (R55), calea fără metodă (R56).

**Ce face imposibil:** o rută care scrie o înregistrare `validata` **direct** (deci produce
evidență, sărind peste validare) fără rol · o rută care atinge credențiale externe fără rol ·
dispariția tăcută a mulțimii (anti-vacuu pe ambele sonde).

**Cum e construit, și de ce așa:** mulțimea se **derivă din AST**, nu dintr-o listă — o listă n-ar
vedea a 41-a rută. Aserțiunea e pe **mulțime**, nu pe cardinal — un clichet pe număr ar trece la o
inversare. Cheia e **calea + metoda**, nu numele funcției.

**Cele șase moduri de eșec sunt scrise în antet, înaintea primei măsurători** (interdicția 76),
inclusiv cele pe care NU le închide: **E3** rol calculat dinamic (măsurat azi: 0 apeluri, dar dacă
apare unul e numit, nu înghițit) și **E6** stare scrisă din parametru — cazul `salarii-contare`,
pinat cu motivul. **E2** (rol verificat în corp, nu în decorator) e închis: sonda îl citește.

**Ce NU face, declarat:** nu spune dacă `admin_firma` e rolul POTRIVIT — spune că există un rol
acolo unde efectul îl cere. Alegerea rolului rămâne decizia lui Costin.

## Închiderea perioadei verifică, iar redeschiderea lasă urmă (26.08.2026, R58)

**Poarta.** `POST /perioade-blocate` refuză 422 dacă perioada are note `ciorna` sau dacă
`inchidere_luna.blocaj` întoarce ceva. Verificarea de e-Facturi **nu se duplică** — se cheamă
funcția existentă din 21.08, mutată de pe **afirmație** pe **poartă**.

**Urma.** `perioade_inchideri`, append-only, cu constrângerea de motiv **în bază**:
`CHECK (actiune <> 'redeschisa' OR btrim(coalesce(motiv,'')) <> '')`. Probat pe schemă efemeră:
baza refuză o redeschidere fără motiv, nu doar ruta. Migrare 17/17 + oglindă în template.

**Ce NU face, declarat:** nu verifică echilibrul și nici orfanii — Costin le-a amânat explicit
până la o măsurătoare pe ce s-ar bloca pe firme reale. Și **nu există încă un clichet** care să
asertea că poarta refuză: azi e o probă funcțională, nu un gard.

## Un modul atribuit unei rute trebuie să fie VIZIBIL ei (26.08.2026, R60)

**`scripts/scan_trasee.py` reparat + `core/test_trasee.py` — 2 gărzi noi.** Harta de aliasuri de nivel-modul se construia cu `ast.walk(tree)`, care intră **și** în corpurile funcțiilor: `from core import stocuri_cv_api as _cv` dintr-o rută îl suprascria pe `from core import cont_valid as _cv` de la linia 30. **Măsurat: 1 alias umbrit, 14 rute** care primeau `articole` și `miscari_stoc` pe care nu le ating.

**Ce face imposibil:** un alias legat corect la nivel de modul, umbrit de importul din corpul **altei** funcții · un modul atribuit unei rute fără să fie importat de unde ruta îl poate vedea (anti-vacuu pe `main.py` real, nu pe fișier sintetic) · adnotarea `ce face` din `TRASEE_VERIFICARI.md` care nu mai spune ce măsoară instrumentul.

**A treia față a aceleiași greșeli**, și de-aia sunt trei teste, nu unul: prima era un nume legat local de un **import** (ruta de NIR, 25.08), a doua un nume legat local de o **variabilă** (`with conn.cursor() as _c`, 25.08), a treia e un nume legat **corect**, stricat din altă parte. Fiecare are și direcția inversă probată, ca o reparație prea largă să nu golească inventarul.

**Direcția tăcută e cea care a cerut gardul (METODA §22).** Pe cele 14 instrumentul **adăuga** tabele — zgomotos, se vede. Dar ruta care chiar cheamă `stocuri_cv_api` primea răspunsul corect **dintr-un accident**, iar direcția care ar fi **scos** un modul real n-ar fi produs zgomot, ci tăcere.

**Și o gardă doc↔cod care lipsea de tot:** `TRASEE_VERIFICARI.md` cerea doar ca rândul `ce face` să **existe**, nu să coincidă cu instrumentul. Măsurat la construcție: **121 din 192 difereau**, din care doar 4 din reparația de azi — restul de **117** stătute din ziua în care `scrie X` s-a despărțit de `poate atinge, prin modul X`. Verificările se scriau pe o afirmație mai tare decât măsurătoarea.

**Ce NU face, declarat:** garda spune când adnotarea diverge de instrument; **nu** spune dacă propoziția scrisă sub ea mai are obiect. Cele două verificări rămase fără obiect (`nota-inventariere`, `achizitie-neinregistrat`) au fost găsite citind, nu măsurând. Iar `main.py` e singurul fișier în care se caută umbrirea.

## Raportul Z nu se poate înregistra de două ori (26.08.2026, R61)

**`core/test_raport_z_unic.py`** — 4 teste, calibrare pe **ambele** forme ale greșelii.

**Ce face imposibil:** o rută de raport Z care scrie în `inregistrari` **înainte** de a fi întrebat dacă raportul există deja · una care scrie fără poarta de perioadă închisă · o verificare de unicitate care se uită **într-o singură sursă** (tastate da, importate nu — adică jumătate de poartă, care arată exact ca o poartă întreagă).

**Cheia nu e data, e casa de marcat.** Decizia lui Costin: `Z-{NUI}-{nr_raport}`, ca la `import-amef` — *„o firmă cu două case de marcat are două rapoarte Z pe zi, legitim”*. Cheia comună face ca un raport importat să nu mai poată fi tastat, și invers.

**Ordinea, nu doar prezența.** Gardul cere ca apelul să fie **înaintea** scrierii, comparând liniile din AST. Forma insidioasă a greșelii e a doua: codul conține numele gărzii, deci un gard scris pe text ar fi trecut verde pe o verificare făcută **după** INSERT. Calibrarea negativă probează exact asta.

**Ce NU face, declarat:** nu probează pe date că baza refuză — e o gardă pe structura rutei, nu o probă funcțională. Și nu spune că totalurile sunt corecte; spune că nota nu se poate dubla.

## Portalul nu mută identitatea fără confirmare, și nu trece un cont dintr-un cabinet în altul (26.08.2026, R62)

**`core/test_portal_acces.py`** — 6 teste. Ordinea reparației e a lui Costin, iar ea e argumentul: **izolarea între cabinete întâi** (P12), abia apoi confirmarea și urma.

**Ce face imposibil:** reactivarea unui cont de client al **altui** cabinet, pe **oricare** din cele două căi — a clientului și a cabinetului · scrierea directă a adresei de autentificare din ruta de portal · un act de acces sau de identitate fără urmă · o confirmare care aplică adresa fără s-o reconfrunte cu `users`.

**Gardul repară CLASA, nu instanța, și calibrarea e chiar pe asta:** fișierul sintetic are una din cele două căi gardată și cealaltă nu. Un gard scris doar pe ruta din care a ieșit constatarea ar fi trecut verde pe el.

**Unde stă ruta de confirmare:** `POST /public/confirma-email`, lângă `activare`, `magic-login` și `reset-parola/seteaza` — familia rutelor care se dovedesc cu un **token**, nu cu o sesiune. Sub `/portal/`, unde tot restul e pe `cere_client`, ar fi fost a patra instanță în șapte loturi a aceleiași forme: aceeași clasă, tratament diferit.

**Ce NU face, declarat:** e o gardă pe cod, nu o probă pe date.

*(Nota de dinainte spunea că rutele nu se pot exercita, fiindcă `principal_client_id` e 0 din 17. Nu mai e adevărată, și de-aia se rescrie: coloana s-a scos, iar titularul e acum **primul cont de client** — regula pe care citirea o folosea deja. Cu ea, rutele SE POT exercita pe firma #8396.)*

## Docstringul nu e cod (26.08.2026)

**`scan_trasee._siruri` nu mai citește docstringurile ca SQL**, iar `core/test_trasee.py` are calibrarea. **Instanța e proprie**: docstringul rutei de confirmare a adresei spunea *„un UPDATE orb ar sparge unicitatea”*, iar instrumentul a extras din proza aia o tabelă pe care a numit-o `oarb` și a scris-o în inventar ca **scriere proprie a rutei**.

E aceeași regulă pe care o ține gardul de la R61 — *un comentariu care pomenește INSERT n-are voie să treacă drept scriere* — doar că acolo era în gard, iar aici în **instrumentul pe care stau toate celelalte măsurători**. Direcția e zgomotoasă, deci se vede — **atâta timp cât numele inventat nu seamănă cu unul real**. `oarb` sărea în ochi; `facturi` n-ar fi sărit.

**Ambele direcții probate:** proza nu produce tabelă, SQL-ul din corp produce. Fără a doua, o reparație care ar tăia toate șirurile ar fi golit inventarul de scrieri proprii.

## Cele patru rute răspund LA FEL la „cine e titularul” (26.08.2026, R62 b, PRAG 1)

**`core/test_portal_acces.py`, test nou.** Regula era scrisă în **două** locuri și era **diferită**: citirea cădea pe primul cont de client când `tenants.principal_client_id` era NULL, cele trei scrieri comparau direct cu coloana — iar coloana n-avea nicio cale de scriere.

**Ce a produs:** ecranul îi spunea omului *„ești titularul”* și îi arăta butoanele, iar rutele îi răspundeau **403**. Nu o funcționalitate care așteaptă date — o **afirmație falsă pe ecran**, la un om real (#8284, firma #8396). Costin a ridicat-o la **PRAG 1**: *ecranul spune una, serverul face alta* — P13, în forma cea mai directă.

**Ce face imposibil:** ca cele patru rute să ia răspunsul din locuri diferite. Toate cheamă `_titular_client`, iar citirea și-a pierdut fallback-ul — helperul **este** regula, deci n-are pe ce să cadă.

**Și coloana s-a scos**, nu doar ocolit: *o coloană cu drum de citire și fără drum de scriere e a treia cale prin care întrebarea s-ar putea pune altfel mâine*.

**Ce NU face, declarat:** spune că cele patru iau răspunsul din același loc, **nu** că nu mai există niciun alt loc din care s-ar putea lua.

## Un document nu se produce cu un gol în locul administratorului (26.08.2026, R66)

**`core/firma_profil_api.cere_administrator`**, chemat din `adeverinta` și din `contracte_api`, convertit în **422** de rute. Nu e un test — e o **poartă în cod**, iar asta se spune: clichetul lipsește deocamdată.

**De ce a apărut abia acum:** `patron_nume` avea drum de citire și **niciun** drum de scriere. Adeverința și contractul îl tipăreau, iar aplicația nu-l putea completa. Refuzul singur ar fi fost necinstit; de aceea câmpul din **Date firmă** și refuzul au intrat în aceeași tură — *coloana și calea ei intră împreună*.

**Refuzul numește documentul și locul:** *„Adeverința nu se poate emite: lipsește numele administratorului. Completează-l în Date firmă › Nume administrator.”* Fără partea a doua, un refuz mută munca fără s-o îndrume.

**Ce a prins în aceeași zi:** un test care emitea adeverință pe o schemă fără `patron_nume`, și care avea un `pytest.raises(ValueError)` pe **altceva**. Fără fixtura completată, ar fi trecut verde pe refuzul greșit.

**Ce NU face, declarat:** apără două documente, nu clasa. Alte artefacte care tipăresc date de firmă nu sunt verificate, iar mulțimea lor n-a fost măsurată.

## Refuzul NUMEȘTE documentul și locul, nu doar refuză (26.08.2026, R66)

**`core/test_document_fara_administrator.py`** — 6 teste. Poarta exista de dimineață în cod; ce lipsea era clichetul, iar lipsa era **declarată**, nu ascunsă. Costin: *azi poarta e probată de faptul că a picat un test existent — adică de un accident, nu de o probă*.

**Ce face imposibil:** un producător de document care nu mai cere administratorul · un apel care nu spune CE document se refuză · o rută care lasă `ValueError` să iasă ca **500** în loc de 422 · un mesaj care nu mai e compus din `UNDE_ADMINISTRATOR`, adică nu mai spune unde se completează.

**Calibrarea e pe partea care contează**, cerută de el: *probează că refuzul NUMEȘTE documentul și locul, nu doar că refuză. Un refuz generic ar trece un test care verifică doar codul 422.* Fișierul sintetic are apelul **prezent**, dar documentul vine dintr-o variabilă — deci un gard care ar verifica doar prezența apelului ar trece verde.

**Locul a devenit o VALOARE cu nume**, `mesaje.UNDE_ADMINISTRATOR`, iar gardul asertează că mesajul e **compus din ea** — nu că fraza conține un anumit șir. Același tipar ca `cont_valid.UNDE_SE_CREEAZA` (clichetul 50 / METODA §23).

**Ce NU face, declarat:** apără două documente, nu clasa; mulțimea artefactelor care tipăresc date de firmă n-a fost măsurată. Și nu probează pe date că ruta întoarce 422.

## Ce decide ce se datorează nu se schimbă peste o lună închisă (26.08.2026, R46)

**`core/test_regim_peste_perioada_inchisa.py`** — 5 teste. Poarta: `firma_profil_api.cere_perioade_deschise`, un loc unic, chemat din **cele trei** căi care ating câmpuri ce decid — vectorul, regimul de TVA, CUI-ul.

**De unde vine:** R46 s-a **reaprins mecanic**. Condiția ei numea `firma_profil_api.py`, iar `test_reaprindere` a oprit un commit care atingea fișierul pentru altceva. Prima reaprindere reală de când mecanismul există.

**Ce face imposibil:** una din cele trei căi care scrie fără să întrebe de perioade închise · lărgirea tăcută a mulțimii `CAMPURI_CARE_DECID` peste `CAMPURI_FISCALE`, sau golirea ei · un refuz care nu spune pe ce cale se face totuși schimbarea.

**Jumătatea care contează la fel de mult:** refuzul se aplică **doar** câmpurilor care decid. Un telefon corectat pe o firmă cu ianuarie închis trece mai departe — altfel poarta ar bloca munca de zi cu zi ca să apere trecutul.

**Măsurat, și măsurătoarea a fost un plafon:** 14 din 16 câmpuri sunt citite de generatoarele de declarații — dar *citit* nu e *decide*. Aplicând criteriul lui Costin a ieșit că **vectorul și regimul nu sunt în `CAMPURI_FISCALE`**, iar de acolo rămâne unul singur: `cui`.

**Ce NU face, declarat:** nu acoperă a doua jumătate a condiției lui R46 — *declarații depuse pe regimul vechi* fără perioadă închisă. Poarta e pe perioada închisă, care e proxy-ul mecanic.

## O rută NOUă fără apelant nu trece poarta (26.08.2026, R70)

**`core/test_ruta_fara_apelant.py`** — 5 teste. Instanța: am scris o rută, i-am construit gardul, a trecut toată suita — și nimic n-o chema. Un **prag 1** pe cod gardat în aceeași zi, găsit de exercitarea pe date, nu de un instrument.

**Domeniul e îngust, deliberat:** clichet pe **mulțime**, nu poartă retroactivă. Cele existente stau într-un `_BASELINE` descris ca **fotografie, nu listă de vinovați**.

**Antetul scrie toate cele patru detectoare încercate și cum greșește fiecare.** Întrebarea *cine cheamă ruta asta* nu are răspuns textual: UI-ul compune căi la rulare și dispeceriză prin tabele. Cifrele succesive: 13, 6, zeci, 32 — iar cea verificată prin citire e **5**. *A patra regulă e cea mai puțin greșită, nu cea corectă.*

**Calibrare pe ambele direcții, cu instanțe reale:** dispecerizarea prin tabel NU e raportată; o rută inventată fără ecran E raportată.

**Ce NU face, declarat:** nu spune că baseline-ul e curat. Spune că nu crește.

**Baseline-ul s-a despărțit în două, 27.08.2026:** jumătatea **derivată** (`declarate()` — rutele al căror decorator poartă `[api_intern_v1]`, citit ca nod de AST) și jumătatea **de mână** (`_ARTEFACTE` — 25 de cazuri în care greșește detectorul, grupate pe felul greșelii). *Ieri gardul verifica o listă, azi verifică un marcaj.* Clichetul rămâne doar pe artefacte: cele declarate ies singure când marcajul dispare.

**Al șaselea test, adăugat 27.08.2026:** cele **cinci** rute fără ecran își declară lipsa în cod, cu marcajul `[api_intern_v1]` pe linia decoratorului — *o declarație care se poate șterge tăcut e o promisiune, nu o declarație*. Asertează pe prezența marcajului, nu pe textul motivului. Corectat cu ocazia asta: **3 din 5 erau declarate dinainte**, nu 1 — registrul se contrazicea singur, la două locuri distanță.

## Patru trimiteri de email nu mai eșuează tăcut (26.08.2026, R73)

**Nu e o gardă, e o reparație — și se spune.** Cele patru `except Exception: pass` din jurul lui `trimite_email_html` au trecut pe `observare.esec_secundar`, cu **`alerta=True`** pe cele trei căi de **acces** și fără alertă pe emailul de bun venit.

**Remediul exista din 27.07** și era folosit în zeci de locuri; nu fusese aplicat exact unde tăcerea costă cel mai mult. Măsurat: 32 de `except …: pass` în producție, 5 în jurul unei operațiuni externe, **4 reale**. După reparație: **28**.

**Și mesajul nu mai afirmă trimiterea:** din *„ai primit linkul de logare”* în *„Am primit cererea. Dacă adresa e în sistem, linkul ajunge în câteva minute.”* Costin: *„e diferența dintre a afirma și a presupune.”*

**~~Ce NU face, declarat: niciun clichet nu ține cele patru pe `esec_secundar`. O revenire la `pass` ar trece.~~ — ÎNCHIS 27.08.2026, mai jos.**

## Un eșec de trimitere a emailului nu se mai stinge tăcut (27.08.2026, R73)

**`core/test_esec_trimitere_email.py`** — 12 teste, structural pe AST (`Try`/`ExceptHandler`), nu pe text. Construit pe argumentul lui Costin: *„o lipsă declarată rămâne lipsă. Reparația e o schimbare de apel — o revenire la `except: pass` n-ar pica nimic."*

**Ce face imposibil:** un `except` care prinde un `trimite_email_html` și nu cheamă `esec_secundar` — gol, cu `print`, sau cu `log` · una din cele trei căi de **acces** care pierde `alerta=True` · o alertă pusă pe bun-venit, care ar face alertele să nu mai fie citite · dispariția tăcută a domeniului, dacă subiectul unui email se schimbă.

**Regula se aplică peste tot fiindcă a fost măsurată întâi:** din **17** apeluri `trimite_email_html`, **4** sunt prinse de un `try` cu `except` (exact cele patru reparate), **12** lasă excepția să urce, **1** e într-un `try/finally`. **Zero excepții de declarat** — deci nicio listă de baseline.

**Calibrarea cerută, cu forma subtilă:** `except Exception: log(...)` fără `esec_secundar` e prinsă — *arată ca disciplină și tace la fel*. Direcția inversă, ca gardul să nu raporteze tot: forma reparată, un `except:` fără tip dar cu urmă, și `try/finally`-ul din `sinteza_zilnica.py` nu sunt raportate.

**RED-proof pe SURSA REALĂ, nu doar pe șabloane:** `main.py` mutat în memorie, patru mutații, patru roșii.

**Ce NU face, declarat:** niciun clichet pe cele **28** de `except …: pass` rămase — n-au fost citite una câte una. Și nu verifică dacă emailul chiar pleacă; doar că, dacă nu pleacă, rămâne urmă.

## O decizie cerută de trei ori nu mai arată ca cerută o dată (27.08.2026)

**`core/test_reluari_decizie.py`** — 5 teste. Costin a întrebat de două ori în aceeași tură: *„dacă ți-am dat-o de două ori și tot apare ca deschisă, verifică de ce nu ajunge la restanță."*

**Răspunsul, măsurat:** din restanțele DESCHISE deblocate de DECIZIE, **19 aveau `reluări: 0`** deși registrul se mișcase sub ele — **R9 de 133 de commituri**, R18 de 122, R26 de 90. Câmpul există, garda lui există (sare la ≥3), dar **contorul nu urca niciodată — deci garda n-a putut să se aprindă nici o dată.**

**Și partea mai rea decât omisiunea:** clasa era **deja găsită și scrisă** în `CONFORMITATE.md` — *„regula era scrisă și nepăzită, deci se citea ca respectată"* — și lăsată ca **disciplină**. A rămas 0 pe 69 din 76.

**Ce NU face, declarat:** nu numără de câte ori am cerut eu — numără **commituri de registru supraviețuite**, un proxy. Și **nu știe dacă răspunsul a fost dat**: din afară, „n-a răspuns" și „n-am scris" arată la fel. Aia rămâne pe disciplină, și se spune.

## Procesul care servește ecranele intră în deadman (27.08.2026, R75)

**`core/sonda_web.py` + `core/test_sonda_web.py`** — 7 teste. Al 12-lea nume din `cron.RITMURI` nu e un job, e **procesul care le servește pe toate**. **Cere pagina** (viu **și** răspunde) și **compară ora de pornire** cu cea de la sonda precedentă.

**Afirmația mai slabă, scrisă ca atare:** prinde **repornirea**, nu **durata**. Între două sonde la 15 minute, o cădere de trei secunde și una de paisprezece minute arată identic.

**Calibrarea a prins un defect al meu:** constantele erau legate ca argument implicit, deci calea de eșec nu se putea proba. Reparat, și gardat împotriva formei.

## Denumirea de la ANAF stă lângă cea editabilă (27.08.2026)

**`core/test_nume_anaf.py`** — 4 teste. Instantaneul se captează **pe toate căile**, nu doar unde numele vine de la ANAF — structural, verificat că nu ajunge sub `if seteaza_nume`. **Ce NU face:** nu cere alegerea (slotul T36 o cere; azi se arată amândouă și se oferă o acțiune), nu reîmprospătează instantaneul, nu se aplică retroactiv.

## Verificările T36 sunt scrise — 197/197 (27.08.2026)

**`TRASEE_VERIFICARI.md`** — cele patru sloturi ale ciclului de viață al firmei, scrise de Costin. Locurile de verificare revin la **197 scrise / 0 goale**. Antetul, garda și rândul `*ce face:*` **nu s-au copiat** din fișierul lui: s-au luat de la instrument, ca garda de identitate să le compare cu ce măsoară el.

**Ce a scos scrierea lor**, și e mai mult decât o completare: două rute păreau să atingă tabele neașteptate (verificat — **artefacte de atribuire pe modul**, consemnate în R53 ca instanțe cu răspuns cunoscut), ecranul nu spunea care act e reversibil (**reparat**), iar întrebarea de fond — de ce se poate redenumi o firmă cu CUI validat — a rămas **decizie**.

## Un refuz la o scriere nu mai rămâne nevăzut (27.08.2026)

**`core/scan_refuz_tacut.py` + `core/test_refuz_tacut.py`** — 9 teste. Costin: *„am pierdut o jumătate de oră pe «butonul nu face nimic» […] consecința nu e neplăcerea, e că nu se poate diagnostica nimic din afară."*

**Măsurat ÎNTÂI, cum a cerut:** din **243** de `catch`-uri peste un apel `api.*`, **227 arată ceva**, **16 sunt scrieri mute**, **70 sunt citiri mute** (badge-uri, contoare). Prima măsurătoare dăduse 25 — citite una câte una, nouă foloseau `insertAdjacentHTML`, pe care detectorul nu-l știa. **Calibrat pe instanțe reale înainte de a scrie cifra.**

**Reparația e UNA, nu șaisprezece:** în `api.js`, după un refuz la o **scriere**, dacă mesajul nu apare nicăieri în pagină, îl arată stratul de prezentare. Verificarea e pe **DOM-ul randat**, nu pe cooperarea apelantului — niciun ecran n-a fost modificat.

**Probat în trei direcții**, cu răspunsuri servite din browser: scriere înghițită → banner cu mesajul serverului · scriere deja afișată → **fără dublură** · citire înghițită → **fără banner**.

**Ce NU face, declarat:** nu spune că mesajul e bun, doar că ajunge. Și **nu scade clasa** — cele 16 rămân mute la locul lor; un mesaj lângă buton e mai bun decât un banner. Clichetul e ca să nu crească.

## Două firme cu același nume nu mai încap în același cabinet (27.08.2026)

**`core/test_nume_firma_unic.py`** — 7 teste. O denumire de firmă e unică la Registrul Comerțului; două rânduri cu același nume sunt un fapt imposibil. **Costul era plătit deja:** pe duplicatul din 26.08 a căzut diagnosticul de la pasul 8 al probei R62.

**Poarta e pe AMÂNDOUĂ căile** — creare **și** redenumire. A doua întrebare a lui Costin a scos că `actualizeaza_tenant` era un `UPDATE` gol de orice poartă: nici cifra de control a CUI-ului, nici unicitatea lui, nici a numelui. **O regulă care se poate ocoli cu un `PUT` nu e o regulă.**

**Ce NU normalizează, declarat:** forma juridică (`SRL` ≠ `S.R.L.`). Refuzul fals e mai scump aici decât duplicatul. **Ce NU face:** nu e retroactivă — perechea existentă stă într-un clichet cu ambele direcții, care cere coborârea când e scoasă.

## Cititorul de șiruri JS greșea în amândouă direcțiile (27.08.2026)

**`core/test_aritmetica_in_prezentare.py`** — nu o gardă nouă, o **reparație de instrument**, și merită scrisă fiindcă e forma cea mai rea de orbire: cititorul care scoate comentariile și șirurile din JS **nu știa de `${…}`**. La un template imbricat, primul backtick **interior** închidea șirul, iar de acolo încolo era **defazat** — ce era text trecea drept cod și invers.

**Deci clichetul „2" nu era o măsurătoare, era o coincidență de sincronizare.** A ținut până când un ecran nou a schimbat parcursul cititorului.

**N-a găsit-o niciun instrument — a găsit-o POARTA**, făcută roșie de o linie de HTML din `firme.js`.

**Reparat de două ori, și a doua oară contează mai mult:** prima reparație albea și **interiorul** interpolării, adică exact codul — o cotă scrisă în `` `${suma * 21 / 100}` `` ar fi trecut nevăzută. A prins-o **calibrarea scrisă în aceeași tură**, pe direcția «ratează». Fără ea, o orbire ar fi fost înlocuită cu alta.

**Trei calibrări noi**, pe ambele direcții. După reparație cifra reală e **tot 2** — aceleași două calendaristice. Clichetul nu se mișcă; ce s-a schimbat e că acum e o măsurătoare.

## Calea de ștergere a unei firme nu poate rămâne în urma bazei (27.08.2026, R72 + R50)

**`core/test_tenant_stergere.py`** — 13 teste. E o gardă despre **liste**, nu despre ștergere: `gdpr_sterge` curăța 2 din 13 tabele nu fiindcă alesese cineva două, ci fiindcă **atâtea erau când s-a scris**. Pe 25.08 erau 12; pe 27.08 sunt 13 — a treisprezecea, `schimbari_email`, apăruse cu o zi înainte.

**Ce face imposibil:** o a paisprezecea tabelă cu `tenant_id` care intră fără să fie clasificată (ori curățată, ori declarată cu motivul) · o tabelă rămasă în listă după ce a dispărut din bază · **o a doua cale de ștergere** — `gdpr_sterge` trebuie să cheme aceeași funcție, verificat pe AST · o firmă cu evidență ștearsă pe calea de scoatere · **urma ștearsă de propriul act** · un `motiv` inventat, care ar ocoli și confirmarea, și verificarea evidenței · ordinea de ștergere schimbată (urmă → `public` → schemă → rândul firmei, citită ca **secvență de operații** din arborele funcției).

**Trei teste în plus, 27.08 noaptea:** urmele portalului supraviețuiesc scoaterii **dar nu** unei ștergeri GDPR (condiția se citește ca **nod de comparație**, nu ca text — un apel necondiționat ar copia date personale într-un log care trebuia să le vadă dispărând) · urma se poate **citi** de om (există rută) · previzualizarea numește conturile care rămân fără firmă.

**Ce NU face, declarat:** **nu șterge nimic ca să probeze.** Suita rulează pe baza de PRODUCȚIE (R67); un test care creează și șterge o firmă adevărată ar fi exact sonda-care-scrie din care am învățat o dată. Se probează **decizia**, nu efectul distructiv — iar efectul s-a probat separat, pe firme sintetice, o singură dată, cu curățare.

## Un job de fundal care nu pornește nu mai trece o lună neobservat (27.08.2026, R74)

**`core/test_joburi_supravegheate.py`** — 12 teste. Lista deadman-ului se compară cu **sistemul**, nu cu o copie a ei. Gardul de dinainte compara `cron.RITMURI` cu un set **scris de mână în test** — deci se compara cu propria copie a răspunsului și n-avea cum să vadă un job pe care nu-l știa deja. Rezultatul: trei timere systemd au rulat un interpretor inexistent **~31 de zile**, ~48 de porniri pe zi, toate cu status 203, în tăcere.

**Ce face imposibil:** un job din `crontab` sau dintr-un timer systemd fără prag în `RITMURI` · un prag rămas pentru un job care nu mai există (o alarmă care sună mereu nu mai e alarmă) · **o unitate care rulează un interpretor inexistent** — chiar defectul, prins de unde se putea vedea · un instrument care se uită în gol: dacă nu vede nici `crontab`, nici unități, **pică**.

**Aceeași clasă cu R70, un nivel mai jos:** acolo *o rută pe care n-o cheamă nimic*, aici *un job care nu pornește*. Amândouă verificau ce face lucrul **dacă** rulează; niciuna **dacă** rulează.

**Clichetul s-a aprins în a doua direcție la PRIMA reparație (27.08.2026):** Costin a corectat cele trei `ExecStart`, iar testul a devenit roșu cerând scoaterea lor din baseline. Baseline-ul e acum **gol, nu șters** — o mulțime goală afirmă *„azi nicio unitate nu e stricată"*; absența listei n-ar afirma nimic.

**Ce NU face, declarat:** nu verifică dacă jobul chiar a rulat (aia e treaba lui `verifica_batai`, la rulare) · nu vede dincolo de mașina asta · nu acoperă `iconta-backup` (shell, nu modul — motivul e scris în `cron.NESUPRAVEGHEATE`) · nu pornește și nu repară nimic: unitățile cer `sudo`.

## Un act distructiv nu-și mai lasă în urmă o referință moartă (27.08.2026, R79)

**`core/test_tenant_stergere.py::test_auditul_nu_mai_produce_orfani_dupa_stergere`** — citește **AST**-ul lui `main.py` și pică pe orice `INSERT INTO public.audit_log` care poartă `tenant_id` fără sub-interogarea care îl trece pe `NULL` când firma nu mai există.

**De unde vine:** calea de ștergere construită ieri **ca să repare** R44 și R50 producea exact clasa lor. Rândul de audit al cererii `DELETE /tenants/{id}` se scria la **78 de milisecunde după** ce tranzacția comisese — deci referința era moartă când se năștea. Legea era liniară: **fiecare firmă scoasă lăsa exact un orfan.** Orfanii au crescut 67 → 69 la primele două ștergeri reale.

**Ce n-a văzut niciun gard scris în aceeași zi:** `test_tenant_stergere` verifica ce rămâne **în momentul** ștergerii, nu ce se scrie **după**. Un gard poate fi complet despre actul pe care îl păzește și orb la ce urmează după el.

**De ce nu cheie străină cu `ON DELETE SET NULL`, deși aia s-a cerut** — măsurat, nu presupus, în ambele forme de coloană:
- pe cele **10** tabele cu `tenant_id NOT NULL`, `SET NULL` **se acceptă la definire** și rupe **la ștergere**: `NotNullViolation`, adică ștergerea de firmă ar deveni imposibilă;
  *(Cifra a fost scrisă întâi **8**, dintr-o numărare făcută pe drum. Recitită din `information_schema`: **10 NOT NULL, 3 nullable**. Concluzia nu se schimbă — se întărește — dar cifra greșită a apucat să intre în mesajul commitului `0963d7f`, unde rămâne. **O cifră scrisă fără instrument nu se poate recalcula, deci nu e o măsurătoare.**)*
- pe coloanele nullable **nu repară cazul**: `SET NULL` acționează la ștergerea părintelui, iar rândul nostru se scrie **după**. Cheia străină l-ar fi **respins** — linia de audit ar fi **dispărut**, nu ar fi devenit `NULL`.

**Ce NU face, declarat:** nu curăță cei **67** de orfani dinainte (R50). Îi îngheață — `test_niciun_orfan_NOU_dupa_ultima_stergere`, clichet pe date la **69** — fiindcă ștergerea lor ar șterge singura urmă că firmele alea au existat. Și nu vede scrierile de audit de după **alte** acte distructive decât ștergerea: doar ea a fost exercitată.

## „A păstra pe a ta" nu mai poate fi „a nu face nimic" (27.08.2026, R77)

**`core/test_nume_anaf.py::test_alegerea_are_AMANDOUA_ramurile_si_amandoua_SCRIU`** — citește arborele funcției `alege_denumirea` și cere ca **o singură** consemnare `UPDATE public.tenants SET nume_ales=…` să acopere **ambele** ramuri. Pică dacă consemnarea alunecă sub ramura „anaf" — adică dacă „păstrez denumirea mea" redevine tăcere.

**Ce păzește, ca principiu:** o alegere în care una din căi e „nu apăsa nimic" nu e o alegere. Cine nu apasă nu decide — moștenește ce era acolo și nu află niciodată că a fost o divergență. Gardul e pe **structura deciziei**, nu pe textul butoanelor.

**Perechea lui:** `test_o_citire_ANAF_mai_noua_REDESCHIDE_intrebarea` — întrebarea nu se pune nici la infinit, nici o singură dată. Se compară `nume_anaf_la` cu `nume_ales_la`: *alegerea de azi nu acoperă o denumire schimbată la registru mâine.*

**Al patrulea, și e despre a DOUA denumire** — `test_cele_doua_denumiri_ale_unei_firme_nu_divergeaza_mai_mult` (R81). O firmă are denumire în **două** locuri: `tenants.nume` (portofoliul — lista, bara de sus) și `firma_profil.nume` (**fiscala** — pleacă în D100/D101/D205/D301/D390/D394/D406 și pe bilanț). Nimic nu le confrunta. **4 din 17 diferă azi**, toate patru cu forma juridică prezentă în cea fiscală și lipsă în cea din portofoliu.

Găsit **nu căutându-l**: Costin a cerut ca „Date firmă" să primească un câmp de denumire, iar ecranul avea deja unul — care scrie în `firma_profil`. Al doilea câmp nu se putea adăuga fără două etichete distincte.

**Ce face imposibil:** o a cincea divergență care intră tăcut (clichet **4**, ambele direcții) · dispariția câmpului din ecran · dispariția blocului care le compară. **Ce NU face:** nu decide care e adevărul — asta e R81, și e a lui Costin.

**Al treilea, adăugat în aceeași zi** — `test_REDENUMIREA_libera_e_si_ea_o_alegere_consemnata`. Costin, la întrebarea lui de fond: *„denumirea firmei e un fapt al registrului, nu o preferință a cabinetului… editarea liberă, fără să treacă prin întrebare, nu mai are rost."* Deci **a tasta** o denumire diferită de cea de la ANAF e tot un act de alegere, nu doar **a apăsa** un buton. Gardul cere ca amândouă căile să treacă prin **aceeași** funcție de consemnare — nu două care se pot despărți în tăcere (instanța: R62, *„regula era în două locuri și diferită"*) — și ca redenumirea să **nu** consemneze nimic pe firmele fără `nume_anaf`, unde n-ar exista a doua denumire cu care să difere.

**RED-proof pe sursa reală**, mutată în memorie: **4 mutații, 4 roșii** — consemnarea devine necondiționată · redenumirea tace · ruta pierde autorul · consemnarea comună dispare.

## Verdele unui gard poartă acum numitorul (27.08.2026, R80, cerința lui Costin)

**`core/test_ruta_fara_apelant.py`** — două schimbări mici, cu efect asupra a ce se **citește** din verde.

Costin: *„un gard care spune «nicio rută fără apelant» trebuie să spună și «despre 88% din suprafață». Altfel cine îl citește mâine crede că e despre tot."*

**Verdele unui test e NUMELE lui.** De aceea testul se cheamă acum `test_nicio_ruta_NOUA_fara_apelant_DINTRE_CELE_VIZIBILE` — calificativul stă în nume, iar cifra **nu**, ca să nu îmbătrânească acolo. Cifra se recalculează: `test_gardul_isi_spune_NUMITORUL` compară `_OARBE` cu măsurătoarea și pică dacă au divergat. Doc↔cod pe propria orbire.

Iar la rulare, gardul **scrie** ce acoperă: *„acoperire reală: 360 din 411 rute (88%) — despre restul, gardul e mut."*

**Al doilea fel de anti-vacuu**, adăugat aici: nu *„vede ceva"*, ci *„nu se declară complet"*. Dacă vizibile == total, testul cere ca ștergerea declarației de orbire să fie **deliberată**.

## Un gard care nu poate vorbi despre 12% din suprafața lui (27.08.2026, R80)

**`scripts/scan_ancore_rute.py` + `core/test_ancore_rute.py`** — 4 teste, clichet **51**.

**Nu e un gard nou peste o clasă nouă. E măsura orbirii unui gard existent.** R70 verifică dacă o rută are apelant în `static/`. Regula lui caută bucățile literale ale căii. Pentru `PUT /tenants/{tenant_id}`, singura bucată literală e `tenants` — care apare de **235** de ori în JS. Deci pentru ruta aia, R70 răspunde **întotdeauna** „are apelant", indiferent de adevăr.

**Cum s-a aflat:** am mutat un buton de pe acea rută pe alta, în aceeași zi. Ruta veche a rămas cu **zero** apelanți — verificat direct. R70 n-a clipit.

**Cifra:** **51 din 411** rute au și cea mai rară ancoră apărând de peste 40 de ori. Toate cele cinci `/tenants` de nivel înalt, toate cele cinci `/coada`, `/portal/*`, `/api/v1/firme`.

**Ce face imposibil:** ca a 52-a să intre tăcut. Clichet în ambele direcții, anti-vacuu pe textul JS, și o **calibrare pe instanța cunoscută** — dacă `PUT /tenants/{tenant_id}` iese din clasă, ori i s-a dat o cale mai specifică, ori măsurătoarea s-a rupt; oricum, se citește.

**O greșeală a măsurătorii, prinsă de cazul cunoscut, nu de recitire:** prima versiune raporta **1 din 411**. `_static()` întoarce un **șir**, iar `"\n".join(șir)` îl sparge în caractere — toate frecvențele ieșeau 0. Cifra falsă era în direcția comodă.

**Ce NU face, declarat:** **nu spune care rute chiar n-au apelant** — spune despre care dintre ele detectorul e mut. O rută din listă poate fi chemată de zece ecrane; ce lipsește e capacitatea de a afla. Și nu repară detectorul: a patra regulă e deja *„cea mai puțin greșită, nu cea corectă"*, iar a cincea cere decizia lui Costin (R80).

**Ce NU face, declarat:** nu poate vedea divergența pe date reale — **0 din 17** firme au `nume_anaf`, fiindcă instantaneul se captează doar de la o precompletare ANAF încolo. Partea de ecran e probată pe un răspuns **fabricat** prin interceptare (`frontend_test/vizual_nume.py`): dovedește ce randează ecranul și ce trimite la apăsare, nu ce răspunde serverul pentru o divergență adevărată. Partea de server e probată separat, pe date reale, într-o tranzacție întoarsă la savepoint (`proba_r77.py`).


## 28.08.2026 — o captură comisă fără proprietar în registru pică poarta

**De ce (Costin):** convenția din `METODA §27` — *„o captură fără proprietar e suspectă"* — **devine
gard, nu doar principiu**.

**Instanța, și e din aceeași zi cu regula:** prima rulare a scanului a găsit **16 din 17** capturi
comise **nenumite**. Opt erau pomenite printr-un **glob** — o mențiune pentru un om și nimic pentru
un instrument; opt erau de dinainte ca regula să existe. Adică regula era încălcată de propriul ei
autor, în ziua în care a scris-o, iar fără gard n-ar fi aflat nimeni.

**Ce face imposibil:** un `.png` comis sub `frontend_test/` al cărui nume de fișier nu apare în
`CONFORMITATE.md`. Se citește din **index**, deci prinde captura la commitul care o aduce.

**CE NU FACE, declarat:** nu judecă dacă e baseline sau probă — distincția e o judecată (§27), iar
gardul cere doar un **proprietar scris**. Nu verifică dacă mențiunea e **adevărată**; aia rămâne
citire. Și nu se aplică retroactiv: cele opt de pe 20.08 stau într-o listă declarată, cu clichet în
ambele direcții — nu are voie nici să crească, nici să păstreze morți.

**Calibrare, două direcții:** o captură inexistentă e raportată; una numită nu e; iar un **glob** în
registru **nu ține loc de nume** — chiar forma greșelii găsite.

`core/test_capturi_numite.py`


# ─────────────────────────────────────────────────────────────────────────────
# BACKFILL 23–28.08.2026 (scris pe 28.08.2026, la cererea lui Costin: „rămâne viu, nu se îngheață")
# ─────────────────────────────────────────────────────────────────────────────

## 28.08.2026 — de ce registrul ăsta a stat șase zile, și ce s-a schimbat ca să nu mai stea

> **DE CE lipsește, la 23–26.08.2026: NU SE RECONSTITUIE.** *Decizie 28.08.2026, cerută de două ori,
> închisă definitiv.* Intrările de mai jos numesc **ce** a intrat în fiecare zi și **ce afirmă
> fiecare gardă despre sine** — amândouă verificabile (`git log`, docstringul propriu). **De ce** a
> fost construită fiecare, ce instanță a produs-o și ce anume nu face **nu se scriu retroactiv**:
> reconstruirea din numele fișierului ar fi **repovestire, nu mărturie**. Pentru zilele 27–28.08, pe
> care le pot atesta, narațiunea e în restanțele lor din `CONFORMITATE.md` și în mesajele de commit.
>
> **Nu mai e o restanță.** Dacă un gard de completitudine se plânge vreodată de absența „de ce"-ului
> pe fereastra asta, **nota asta e răspunsul**, nu o datorie de plătit.


**Constatarea:** ultima intrare din `GARZI.md` era din **22.08.2026**. În cele șase zile de după au
intrat **80 de gărzi și instrumente** — niciunul scris aici. Un registru cu șase zile în urmă nu se
citește ca incomplet: **se citește ca complet.** E chiar clasa pe care o numește `METODA §14` — *o
regulă scrisă și nepăzită se citește ca respectată* —, aplicată registrului care ține evidența
regulilor păzite.

**Decizia lui Costin, 28.08.2026:** *„rămâne viu, nu se îngheață."* Plus: `GARZI.md` intră în
`REGISTRE` ca **linie obligatorie** de-acum înainte (scris în `CLAUDE.md` §2.2.1).

**CE SE POATE SCRIE RETROACTIV, ȘI CE NU.** Intrările de mai jos numesc **ce a intrat** în fiecare
zi și **ce spune fiecare gardă despre ea însăși** — amândouă verificabile: prima din `git log`, a
doua din docstringul propriu. Ce **nu** se scrie retroactiv e *de ce* a fost construită fiecare,
instanța care a produs-o și ce anume nu face. Alea au fost adevărate într-o sesiune pe care n-o mai
pot citi, iar reconstruirea lor din numele fișierului ar fi exact greșeala pe care `METODA` o
numește: *un motiv scris din analogie transformă „n-am făcut" în „nu se poate".* Pentru zilele
27–28.08, pe care le pot atesta, narațiunea e scrisă în restanțele lor din `CONFORMITATE.md` și în
mesajele commiturilor.

**ȘI CE S-A CONSTRUIT CA SĂ NU SE MAI REPETE:** `scripts/scan_garzi_inventar.py` +
`core/test_garzi_inventar.py`. Inventarul de la coada fișierului e **generat**, iar garda îl compară
caracter cu caracter cu ce produce instrumentul — același tipar ca Partea XII din `TRASEE.md`. O
gardă nouă care intră fără să apară în inventar **pică poarta**. Partea narativă rămâne a omului;
partea care se poate deriva nu mai are voie să îmbătrânească.

## 2026-08-28 — 4 gărzi și instrumente

**Ziua celor două reguli de ecran și a simetriei de scriere.** `scan_ecran_reguli` sparge sursa în **noduri de randare** și în **blocuri de execuție** înainte de a aserta pe ea (E1/E2, DS cap.26–27); `scan_simetrie_denumire` citește din AST fiecare `UPDATE … SET nume=` și pică dacă o funcție scrie într-un singur loc din două (R81). A doua a găsit, la prima rulare, **o a patra cale asimetrică** pe care măsurătoarea de mână n-o văzuse.

- `core/scan_ecran_reguli.py` — Instrumentul celor două reguli de ecran scrise pe 28.08.2026 — E1 (două nume distincte) și
- `core/scan_simetrie_denumire.py` — Instrumentul simetriei de scriere a denumirii unei firme (R81, decis 28.08.2026).
- `core/test_reguli_ecran.py` — GARD [28.08.2026]: cele două reguli de ecran scrise azi — E1 și E2 (`DESIGN_SYSTEM.md` cap.26/27).
- `core/test_simetrie_denumire.py` — GARD [R81, DECIS 28.08.2026]: denumirea unei firme se scrie în AMÂNDOUĂ locurile sau în niciunul.

## 2026-08-27 — 11 gărzi și instrumente

**Ziua în care s-au deschis nouă restanțe într-una.** Ștergerea unei firme (R72), eșecul tăcut de email (R73), deadman-ul comparat cu SISTEMUL (R74), sonda web (R75), refuzul care nu ajunge la om, denumirea de la ANAF, unicitatea numelui, contorul de reluări al deciziilor — și `scan_ancore_rute`, care a măsurat **orbirea gardului de ieri** (R80). Un instrument construit ca să măsoare limitele altui instrument, în ziua următoare.

- `core/scan_refuz_tacut.py` — core/scan_refuz_tacut.py — cate refuzuri ale serverului nu ajung la om.
- `core/test_ancore_rute.py` — GARD [R80, 27.08.2026]: clasa de rute despre care detectorul din R70 nu poate afirma nimic
- `core/test_esec_trimitere_email.py` — GARD [R73, 27.08.2026]: un eșec de trimitere a emailului nu se mai poate stinge tăcut.
- `core/test_joburi_supravegheate.py` — GARD [R74, 27.08.2026]: lista deadman-ului se compară cu SISTEMUL, nu cu o copie a ei.
- `core/test_nume_anaf.py` — GARD [27.08.2026]: denumirea de la ANAF se păstrează lângă cea editabilă, cu data ei.
- `core/test_nume_firma_unic.py` — GARD [27.08.2026]: două firme cu același nume, în același cabinet, sunt un fapt imposibil.
- `core/test_refuz_tacut.py` — GARD [27.08.2026]: un refuz al serverului la o SCRIERE nu poate rămâne nevăzut.
- `core/test_reluari_decizie.py` — GARD [27.08.2026]: o decizie cerută de mai multe ori nu mai poate arăta ca cerută o dată.
- `core/test_sonda_web.py` — GARD [R75 (b), 27.08.2026]: procesul care servește ecranele e supravegheat, și se știe cum.
- `core/test_tenant_stergere.py` — GARD [R72, 27.08.2026]: calea de scoatere a unei firme nu poate rămâne în urma bazei.
- `scripts/scan_ancore_rute.py` — Pentru cate rute e ORB PRIN CONSTRUCTIE detectorul de apelanti din R70.

## 2026-08-26 — 9 gărzi și instrumente

**Ziua rolurilor și a rutei fără apelant.** `scan_rol_pe_efect` a mutat întrebarea *cine are voie* de la numele rutei la **ce face** ruta. Iar `test_ruta_fara_apelant` (R70) s-a născut dintr-o rută scrisă, gardată și verde pe care **nu o chema nimic** — gărzile verificau ce face ruta *dacă* e chemată, niciuna nu întreba *dacă* e chemată.

- `core/scan_rol_pe_efect.py` — core/scan_rol_pe_efect.py — INSTRUMENT: ce face fiecare rută, ca să se poată cere rolul după
- `core/test_cont_din_corp_normalizat.py` — core/test_cont_din_corp_normalizat.py — un cont luat din CORPUL CERERII trece prin strip().
- `core/test_document_fara_administrator.py` — GARD [R66 (c), 26.08.2026]: un document care tipărește numele administratorului nu se produce
- `core/test_echilibru_legat.py` — core/test_echilibru_legat.py — GARDA R33 varianta b'' (26.08.2026).
- `core/test_portal_acces.py` — GARD [R62, 26.08.2026]: portalul nu mută identitatea fără confirmare, nu trece un cont dintr-un
- `core/test_raport_z_unic.py` — GARD [R61, 26.08.2026]: raportul Z nu se poate înregistra de două ori, iar niciuna din cele
- `core/test_regim_peste_perioada_inchisa.py` — GARD [R46, 26.08.2026]: un câmp care decide CE SE DATOREAZĂ nu se schimbă peste o perioadă închisă.
- `core/test_rol_pe_efect.py` — core/test_rol_pe_efect.py — GARD: rolul se cere după CE FACE ruta, nu după cum se numește.
- `core/test_ruta_fara_apelant.py` — GARD [R70, 26.08.2026]: o rută NOUĂ fără apelant nu trece poarta.

## 2026-08-25 — 12 gărzi și instrumente

**Ziua traseelor și a celor patru decizii ale lui Costin (R41–R49).** `scan_trasee` + `test_trasee` au făcut inventarul celor 35 de trasee **generat**, iar garda îl compară caracter cu caracter cu documentul. Restul sunt gărzile deciziilor din ziua aia: coada, artefactele păstrate, prăpastia salariului minim, nomenclatorul luat din NORMĂ.

- `core/test_artefacte_pastrate.py` — GARD [R45]: un artefact produs se păstrează, cu cele cinci câmpuri — și producerea lui e
- `core/test_coada_firma_exista.py` — GARD [R44]: o declarație nu poate intra în coadă legată de o firmă care nu există.
- `core/test_coada_gata_de_depus.py` — GARD [R41 partea II]: «gata de depus» are O SINGURĂ definiție, iar lista o poartă.
- `core/test_coerenta_salarii.py` — GARD [R33, decizia lui Costin 25.08.2026]: semnalul de coerență notă-vs-D112 apare LA PROPUNERE,
- `core/test_contract_ecran_ruta.py` — GARD: contractul ECRAN ↔ RUTĂ nu se rupe tăcut.
- `core/test_nomenclator_pe_norma.py` — GARD [C6, 25.08.2026]: un nomenclator se ia din NORMĂ; validatorul e constrângere, nu sursă.
- `core/test_prapastie_salariu.py` — GARD [R49, varianta (c)]: prăpastia salariului minim se spune CU CIFRE, și cifrele sunt ale
- `core/test_r42_criteriu.py` — GARD [R42, cele patru decizii ale lui Costin, 25.08.2026].
- `core/test_trasee.py` — GARD: inventarul traseelor nu îmbătrânește tăcut, iar instrumentul lui nu minte.
- `core/test_verdict_persistat.py` — GARD — verdictul de validare se păstrează, și un verdict stătut nu ține locul unuia proaspăt.
- `scripts/scan_contract_ecran.py` — scripts/scan_contract_ecran.py — contractul ECRAN ↔ RUTĂ, măsurat.
- `scripts/scan_trasee.py` — scripts/scan_trasee.py — INVENTARUL TRASEELOR, calculat, nu ținut minte.

## 2026-08-24 — 15 gărzi și instrumente

**Ziua clichetului 50 și a verdelui derivat.** `scan_garzi_pe_text` + `test_garzi_pe_text` au măsurat pentru prima oară câte gărzi asertează pe TEXT în loc de STRUCTURĂ — clichet **pe fișier**, nu global, ca un fișier nou să pornească de la zero. Tot azi: `test_verde_derivat` (verdele se derivă; unde nu se poate deriva, semaforul LIPSEȘTE) și `test_predare_proaspata`, care ține predarea de a îmbătrâni tăcut.

- `core/scan_garzi_pe_text.py` — Care gărzi asertează pe TEXT în loc de STRUCTURĂ — pe ASERȚIUNE, nu pe fișier.
- `core/scan_module_nelegate.py` — INSTRUMENT — module cu funcții publice și ZERO importatori în afara testelor.
- `core/scan_valori_afisate.py` — Valori FISCALE scrise literal in TEXTUL AFISAT de ecrane.
- `core/test_an_hardcodat.py` — Un AN scris literal intr-o cerere catre server ingheata ecranul in trecut.
- `core/test_cota_fara_default_fallback.py` — GARD (R29): o cotă de TVA absentă nu se completează singură, în niciun limbaj și în nicio formă.
- `core/test_d212_an_verificat.py` — Fișa D212 se produce pe anul CERUT, pe plafoanele verificate ale anului — nu pe unul înghețat.
- `core/test_document_ref_necunoscut.py` — GARD — un `0` care nu poate fi altceva decât `0` nu susține nicio cauză afirmată.
- `core/test_eticheta_conturi_ecran.py` — Eticheta din ECRAN și conturile din BACKEND nu pot diverge tăcut.
- `core/test_garzi_pe_text.py` — GARD PESTE GĂRZI — o gardă asertează pe STRUCTURĂ, nu pe text.
- `core/test_identitate_acte.py` — GARD — un act din corpus e ACTUL pe care îl spune numele lui, și e adus o singură dată.
- `core/test_module_nelegate.py` — CLICHET — module de producție din `core/` pe care nu le cheamă nimeni în afara testelor.
- `core/test_predare_proaspata.py` — PREDARE_LANT.md isi arata vechimea, iar avertismentul din poarta nu poate disparea tacit.
- `core/test_registru_jurnal_14_1_1.py` — GARD — Registrul-jurnal păstrează cele trei coloane cerute de norma 14-1-1.
- `core/test_valori_fiscale_js.py` — Valorile fiscale scrise in ECRANE se confrunta cu REGISTRUL, nu cu memoria mea.
- `core/test_verde_derivat.py` — Verdele de semafor se DERIVĂ; unde nu se poate deriva, semaforul LIPSEȘTE.

## 2026-08-23 — 29 gărzi și instrumente

**Ziua instrumentelor de MĂSURĂ**, nu a reparațiilor. Aici au intrat scanerele care au făcut posibile campaniile de după: proveniența corpusului, conflictele între surse, valoarea din citat, norma↔implementare, și — cel mai important — cele trei instrumente de FAZA 4 care măsoară **gărzile însele** (`scan_instrumente`, `scan_axa_garzi`, `scan_mutatie_garzi`). De aici vine §10.15 din METODA: *un instrument se calibrează pe modul în care POATE greși.*

- `core/scan_conflicte_sursa.py` — core/scan_conflicte_sursa.py — INTERDICȚIA 58, partea nemăsurată: conflictele NEÎNREGISTRATE.
- `core/scan_js_texte.py` — SCANNER de FRAZE DE INTERFATA din JavaScript (23.08.2026) — instrumentul pentru interdictiile
- `core/scan_norma_implementare.py` — core/scan_norma_implementare.py — INTERDICȚIA 60: elementul care implementează o normă îi poartă
- `core/scan_provenienta.py` — core/scan_provenienta.py — de unde vine fiecare fisier din corpus. (23.08.2026)
- `core/scan_valoare_in_citat.py` — core/scan_valoare_in_citat.py — INTERDICȚIA 53: citatul conține VALOAREA pe care o justifică?
- `core/test_aritmetica_in_prezentare.py` — GARD (interdicția 4): aritmetica fiscală din ecran nu diverge de cea din server.
- `core/test_cod_partener.py` — GARD (prag 2, 23.08.2026): codul fiscal al partenerului se CERE la introducere.
- `core/test_conflicte_sursa.py` — GARDĂ pentru partea deschisă a interdicției 58 — conflictele NEÎNREGISTRATE între surse.
- `core/test_cota_efect.py` — GOLDEN pe EFECT: ce cifră iese pe căile reparate la R26, nu ce cotă a intrat.
- `core/test_cota_fara_default.py` — GARD (R26): nicio funcție fiscală nu are cotă implicită, iar REFUZUL chiar se produce.
- `core/test_d406_jurnal_origine.py` — GARD (R22, prag 1): `JournalID` din D406 poartă jurnalul de ORIGINE, nu o constantă.
- `core/test_dependenti_act.py` — GARDĂ pentru interdicția 61 — lista dependenților unui articol, generabilă la cerere.
- `core/test_fisa_cont.py` — GARD: Fișa de cont pentru operațiuni diverse produce ce cere norma, nu o balanță deghizată.
- `core/test_graf_clustere_proprietar.py` — GARD (R19): o funcție partajată între clustere NU e proprietatea niciunuia.
- `core/test_importuri_nefolosite.py` — CLICHET pe importurile nefolosite (F401). Nu blochează codul existent; oprește creșterea.
- `core/test_norma_implementare.py` — GARDĂ pentru interdicția 60 — elementul care implementează o normă îi poartă articolul?
- `core/test_portal_ids.py` — GARDĂ: fiecare act citat de un Temei din registru are id-ul lui de portal, scris.
- `core/test_portal_nu_scrie_gol.py` — Unealta care aduce acte din portal NU are voie să scrie un `.txt` gol.
- `core/test_provenienta.py` — GARDA: fiecare fisier din corpus isi stie provenienta. (23.08.2026)
- `core/test_reaprindere.py` — GARD: o restanță al cărei DECLANȘATOR s-a produs nu poate rămâne nereluată.
- `core/test_scan_instrumente.py` — Garda instrumentului de FAZA 4 (`scripts/scan_instrumente.py`).
- `core/test_scan_js_texte.py` — CALIBRAREA instrumentului JS — scrisă ÎNAINTE de prima măsurătoare, nu după.
- `core/test_valoare_in_citat.py` — GARDĂ pentru interdicția 53: citatul conține VALOAREA pe care o justifică.
- `core/test_verificator_izolare.py` — GARDĂ PESTE VERIFICATOR: analizorul lui de izolare clasifică corect rute known-good / known-bad.
- `core/test_vigoare_articole_registru.py` — GARDĂ pentru interdicția 50 — confirmarea unei valori e ULTERIOARĂ ultimei modificări a articolului.
- `core/test_vigoare_punct.py` — Garda instrumentului de vigoare PE PUNCT (`scripts/vigoare_punct.py`, R2).
- `scripts/scan_axa_garzi.py` — FAZA 4, axa D despicata: „odata cu fixul" ascunde DOUA lucruri, iar „singura" ascunde alte doua.
- `scripts/scan_instrumente.py` — scripts/scan_instrumente.py - FAZA 4: pe ce instrument sta fiecare garda, si a fost calibrat.
- `scripts/scan_mutatie_garzi.py` — FAZA 4, pasul 5: mutatia care probeaza garda e REPRODUCTIBILA azi?



# ─────────────────────────────────────────────────────────────────────────────
# INVENTARUL GĂRZILOR — GENERAT. Nu se editează cu mâna.
# ─────────────────────────────────────────────────────────────────────────────

## 31.08.2026 — INVENTARUL REFUZURILOR: ce poartă un refuz al aplicației, și ce nu poartă

*Cerut de Costin ca inventar al locurilor unde aplicația refuză, **înaintea** normei de
blocaj-cu-temei. Măsurat pe mașină, cu `scripts/scan_refuzuri.py`; gardat de `core/test_refuzuri.py`.*

**Întrebarea, și de ce nu e cea pe care o pune deja alt instrument.** `core/scan_refuz_tacut.py`
întreabă dacă un refuz **ajunge** la om — dacă are un `catch` care afișează ceva. Ăsta întreabă dacă
refuzul **spune pe ce se sprijină**. Un refuz poate ajunge perfect la om și să fie, tot așa, o
afirmație fără autor: *„nu se poate"*, fără să spună cine zice asta. Populațiile se suprapun, dar
niciuna n-o cuprinde pe cealaltă.

### MĂSURĂTOAREA — 1134 de `raise` care opresc un act

| clasă | structurat | proză | fără | ce oprește |
|---|---|---|---|---|
| **acces** | 0 | 0 | 40 | cine ești (401/403). Un temei legal n-ar avea ce căuta: refuzul nu se sprijină pe o normă fiscală |
| **negăsit** | 0 | 0 | 235 | 404 — **amestecat prin construcție**: și „firmă inexistentă", și „fel necunoscut" dintr-un nomenclator închis |
| **refuz** | 16 | 30 | **813** | ce ai cerut (400/409/422 + excepțiile producătorilor) |

### DE CE CIFRA NU E 813 — și cum s-a aflat asta înainte, nu după

Eșantionul de 30, luat **înainte** de a crede totalul (regula din METODA), a confirmat exact modul
de eșec pe care instrumentul îl declarase în docstringul lui, scris înainte de prima rulare:
**aproape toate cele 813 sunt refuzuri de FORMĂ** — *„valoare invalidă"*, *„schema invalidă"*,
*„suma trebuie să fie pozitivă"*, *„stare necunoscută"*. Un temei legal n-are ce căuta acolo.

**813 nu e o datorie. E o cifră care amestecă două populații**, și dacă ar fi intrat direct într-un
clichet ar fi produs exact felul de plafon care nu constrânge nimic: prea mare ca să scadă, prea
amestecat ca să însemne ceva.

Dimensiunea care le desparte, decisă pe **structură**, nu pe cuvintele din mesaj: *modulul în care
stă refuzul citează legea undeva?* Un `Temei(...)` sau un nume `TEMEI*` în fișier înseamnă că
modulul chiar are de-a face cu norme.

| | cât | în câte fișiere | ce înseamnă |
|---|---|---|---|
| **DATORIE** | **64** | 13 | refuz într-un modul care **citează** legea, iar refuzul nu poartă temeiul. Aici temeiul e de așteptat și lipsește. **Cifra clichetului.** |
| **UMBRĂ** | **778** | 160 | module care refuză și **nu citează legea nicăieri**. Ori sunt generice (`db.py`, `bacsis.py`) și e în regulă, ori aplică o regulă pe care n-o pot numi |
| **ÎNTORC** | **88** | — | `return {"eroare": ...}` în loc de `raise` — umbra instrumentului însuși |

Cele 13 fișiere ale datoriei: `common.py` 14 · `stocuri.py` 9 · `tva_marja_turism.py` 7 ·
`d406.py` 6 · `contracte_speciale.py` 5 · `stocuri_cv.py` 5 · `deconturi.py` 4 · `salarizare.py` 3 ·
`sponsorizari.py` 3 · `tva_marja.py` 3 · `registre_art321.py` 2 · `scadente.py` 2 ·
`registru_inventar.py` 1.

*Ultimele două sunt ale mele, de ieri. Rămân în baseline, nu se repară în aceeași tură în care se
măsoară — altfel cifra de pornire ar fi una aleasă, nu una găsită.*

### DE CE UMBRA NU SE GARDEAZĂ, deși e de douăsprezece ori datoria

Fiindcă n-am cum să deosebesc mecanic un modul **generic** de unul care **aplică o regulă fără s-o
poată numi**. Un clichet pe o cifră pe care n-o înțeleg ar fi un plafon inventat: ar cădea la prima
mutare de cod și ar fi ridicat fără să se fi reparat nimic. Se scrie, se numără, **nu se plafonează**
— iar dacă vreodată scade, asta nu e automat o victorie: poate însemna și că s-a mutat codul.

### AMBELE DIRECȚII DE EȘEC, scrise (METODA §22)

Un modul care citează legea **o dată** face candidate *toate* refuzurile lui, inclusiv *„suma
trebuie să fie pozitivă"* → **DATORIE e plafon SUPERIOR**. Invers, un modul fără nicio citare scoate
din număr și refuzurile lui normative → **e plafon INFERIOR pe altă direcție**. Instrumentul
greșește în **amândouă** direcțiile — și de-aia UMBRA se numără **separat**, nu se adună la datorie:
un instrument care greșește în ambele direcții n-are **niciun** plafon dacă cifrele lui se adună.

**Ce NU măsoară, declarat:** dacă temeiul e **corect**. Doar dacă există și sub ce formă.

**RED-proof:** un refuz nou fără temei într-un modul care citează legea → ROȘU · un fișier nou care
citează legea și refuză fără temei → ROȘU · temeiul scos **cu totul** de pe un refuz care îl avea
(și `temei=`, și interpolarea din mesaj) → ROȘU.

*A patra mutație, încercată prima, a ieșit **verde** — și avea dreptate instrumentul, nu eu:
scosesem doar `temei=`, dar mesajul interpola în continuare `TEMEI[fel]`. Refuzul chiar purta
temeiul, pe alt drum. Mutația era proastă, nu gardul.*

### CE A DEVENIT INVENTARUL — norma, scrisă pe cifra lui *(31.08.2026, semnal de la Costin)*

Măsurătoarea a devenit **interdicția 77** din `CONFORMITATE.md`: *un blocaj fără temei — aplicația
oprește un act și nu spune pe ce se sprijină.* Perimetrul e **datoria de 64**, nu cele 813; norma
**își scrie singură limita** pe umbra de 778, cu motivul, ca să nu se citească drept plafon pe tot.

Două lucruri s-au adăugat odată cu norma, fiindcă fără ele plafonul s-ar fi putut ocoli fără
rea-intenție:

1. **Migrarea între populații.** Un modul care **începe** să citeze legea își aduce în datorie și
   refuzurile scrise **înainte** (păzit: fișierul nu e în baseline, deci n-are voie cu niciunul).
   Un modul care **încetează** să citeze legea **nu-și stinge datoria** — o mută în umbră, unde n-o
   mai numără nimeni. A doua direcție lipsea, și e cea periculoasă: cifra scade identic în amândouă
   cazurile, iar gardul de dinainte dădea, în cazul eludării, exact sfatul greșit — *„curăță
   baseline-ul"*. **Suprafața de migrare e măsurată: 160 de fișiere** sunt la un singur `Temei`
   distanță. *(Costin: „altfel clichetul se elude prin locul unde stă codul, nu prin conținut — fără
   rea-intenție, doar prin creștere".)*
2. **Confruntarea normei cu clichetul.** Cifra din registru și cifra din cod nu pot diverge tăcut.
   Dacă datoria scade, norma primește o linie nouă **cu data ei** — nu se lasă cifra veche să se
   citească drept curentă. E chiar regula de ieri („o proză care reafirmă un număr derivat"), aplicată
   pe a treia cale: aici nu se poate nici genera, nici șterge — `cifra` e un câmp **obligatoriu** al
   unei interdicții, pinat cu `măsurat la` + `pe commit`. Deci **se confruntă**.

### ÎNCHIS 31.08.2026 — `verificator_neconformitati.sh`, sub norma 77, ca FORMĂ

*Costin, 31.08, prima dată: intră sub aceeași normă «ca formă, nu ca reparație în tura
asta». A doua oară, în aceeași zi: **«repară-l acum»**. Reparat; gardul e mai jos.*

**Un blocaj care afirmă absența când de fapt n-a putut verifica este un blocaj fără temei.** Linia
`FAIL NC-07 JWT_SECRET lipsește din proces!` nu deosebește *„nu e"* de *„n-am putut vedea"* — iar
prima e o afirmație despre lume pe care instrumentul n-are cum s-o susțină.

- **ce se face**: un **al treilea rezultat, `NU S-A PUTUT VERIFICA`**, distinct de `PASS` și `FAIL`,
  pe fiecare pas care are nevoie de privilegiu.
- **ce NU se face, expres**: lărgirea setului îngust de `sudo`. *Un verificator care are nevoie de
  mai multe drepturi ca să spună adevărul cere să fie crezut pe încredere* — și ar desface tocmai
  îngustarea făcută pe 30.08.
- **de ce nu-l vedea instrumentul de refuzuri**: el vede doar Python (`raise`), iar ăsta e un
  script `bash` care **tipărește** un verdict. Era în umbra declarată a instrumentului, modul de
  eșec 3 — deci gardul a trebuit construit separat, pe clasificarea scriptului însuși.
- **REPARAT 31.08**, v. secțiunea gardului de mai jos. Cele două linii NC-07 spun acum
  `NEVERIF [sudo-indisponibil]`, cu motivul pe același rând; setul de `sudo` **n-a fost
  atins**.


## 31.08.2026 — SUPRAFAȚA DE IMPACT a două acte noi, și o constatare despre CLASIFICATOR

*Aduse la sursa oficială (`legislatie.just.ro`, prin `scripts/portal_legislativ.py adu`), cu amprentă
pe pagină **și** pe text, clasa ADUS. Măsurătoare, nu reparație.*

| act | adus ca | amprentă text |
|---|---|---|
| **Ordinul ANAF 603/2026** (MO 419/18.05.2026) | `opanaf_603_2026_recalculare_oficiu_cass` | `e257836e…` |
| **OPANAF 602/2026** (MO 416/15.05.2026) | `opanaf_602_2026_modificare_opanaf_587_2016_formulare` | `fef31fbb…` |

**O verificare care a contat înainte de a scrie ceva în corpus.** Căutarea după numărul 602 a dat
**două** acte: unul al ANAF din 12 mai, altul al Ministerului Transporturilor din 15 iunie, despre
tarife aeronautice. Le-am citit pe amândouă **fără să scriu pe disc**, și abia apoi l-am adus pe cel
potrivit. *Un act adus pe baza unui număr ghicit e mai rău decât unul lipsă* — METODA §30.

### 603/2026 — ZERO suprafață la noi, deși e etichetat **mare**

Ce face, citit la sursă: aprobă **procedura prin care ORGANUL FISCAL recalculează din oficiu CASS**,
plus două formulare — *„Referat privind recalcularea CASS"* și *„Decizie de recalculare din oficiu"*.
Declanșatorul e **decesul** contribuabilului. Temeiul: art. 122, art. 180 alin. (1) lit. b)-d),
art. 182^1, art. 183 CF. Abrogă **OPANAF 493/2022**.

| întrebarea | răspunsul, măsurat |
|---|---|
| e vreo citare a noastră superseded? | **nu**: `493/2022` — **zero** potriviri în tot repo-ul, corpus inclus |
| citează codul nostru art. 180 / 182^1 / 183 CF? | **nu**: singurele două potriviri pe „art. 183" sunt **Legea 31/1990** (rezerva legală), alt act |
| modifică D212? | **nu**. Actul **citește** declarația unică (capitolul II) ca *intrare* a recalculării; nu-i schimbă modelul. Zero apariții ale lui „212" în text |
| produce aplicația vreunul din cele două formulare? | **nu** — sunt acte pe care ANAF le emite **către** contribuabil |
| motorul nostru CASS e atins? | **nu**: `d212_engine` stă pe art. 154/170 CF + Legea 239/2025 art. XII pct. 19. Alt capitol |

**Structura registrului PF, comisă în `11514c2`, stă neatinsă** — dar măsurătoarea a făcut vizibilă o
graniță a ei, care nu e un defect introdus de act: registrul ține **veniturile** (art. 68), iar
capitolul II al D212 poartă **CASS declarată pe alte baze** (art. 180 lit. b)-d)), pentru care
registrul n-are și nu trebuie să aibă loc. Ordinul o arată; n-o creează.

### 602/2026 — suprafață REALĂ, deși e etichetat **medie**

| ce schimbă | unde ne atinge |
|---|---|
| adaugă **poziția 116, „Contribuție de solidaritate"** în Anexa 3, *Nomenclatorul obligațiilor de plată la bugetul de stat* (temei: OUG 24/2026) | `core/d100.py` cunoaște **două** coduri de obligație: `121` (impozit micro) și `103` (impozit profit). Poziția 116 nu există la noi |
| o declară **lunar**, literă nouă `ț)` la termenele D100 | termenele noastre de D100 nu cunosc obligația |
| extinde tabelul pct. II la pozițiile `…102-116` | plaja se oprea la 115 |
| **D710: neatins** — zero apariții ale lui „710" în act | — |

**Cine datorează, și dacă ne privește azi:** operatorii de la art. 2 alin. (1) din OUG 24/2026 —
comercializare de țiței și produse energetice din țiței extras în România. **Măsurat pe cele 19
firme: niciuna.** CAEN-urile lor sunt `0111, 1071, 2110, 4321, 4652, 4669, 4711, 4779, 4791, 6201,
6202, 6210, 7911, 9602` — nicio potrivire în zona `0610/0620/1920/4671/4730/3520`.

**O citare care a devenit incompletă.** `DECIZII.md` scrie *„D100/D710: OPANAF 57/2026 …, amendează
baza 587/2016"*. **602/2026 amendează aceeași bază, mai târziu** (mai 2026 față de ianuarie 2026).
Citarea nu e falsă — e **incompletă**, și asta e o stare mai greu de văzut decât o eroare: cine o
citește află un act curent care chiar e curent, fără să afle că mai există unul peste el.

### CONSTATAREA DESPRE CLASIFICATOR — etichetele s-au inversat

Costin: *«Etichetele [mare]/[medie] sunt judecata clasificatorului nostru, nu o măsurătoare. Dacă
impactul real le contrazice, e constatare despre clasificator.»* **Le contrazice, și pe amândouă:**

| act | eticheta clasificatorului | impactul măsurat |
|---|---|---|
| 603/2026 | **mare** | **zero** citări superseded, zero câmpuri, zero formulare produse de noi |
| 602/2026 | **medie** | o obligație nouă în nomenclatorul D100, un termen lunar nou, o citare devenită incompletă |

**Ce a greșit clasificatorul, mecanic:** a citit *„CASS"* și *„formulare"* în rezumat și a ridicat
relevanța. Amândouă cuvintele apar — dar formularele sunt ale **organului fiscal**, iar CASS-ul e din
**alt capitol** decât cel pe care îl calculăm noi. Invers, *„modificarea formularelor de declarare"*
sună generic și a primit **medie**, deși schimbă chiar nomenclatorul unei declarații pe care o
producem.

**Tiparul, scris ca să fie recunoscut a doua oară:** clasificatorul cântărește **vocabularul
rezumatului**, nu **cine emite** și **ce declarație atinge**. E aceeași formă de orbire ca la R80,
unde o cifră creștea fiindcă un cuvânt vechi apărea într-un ecran nou. *Un instrument care măsoară
vocabularul e orb la exact lucrurile pe care vocabularul nu le distinge.*

**Nereparat, deliberat** — s-a cerut măsurătoare. Ce ar cere reparația, ca să nu se redescopere:
clasificatorul ar avea nevoie de **emitent** (ANAF către contribuabil vs. contribuabil către ANAF) și
de **declarația atinsă**, nu de cuvintele din rezumat. Rămâne deschis aici.

*(Nota de acoperire: alerta **605/2026 — noul formular 112**, relevanță **mare**, din 24.08, e deja
absorbită — `DECIZII.md` o numește act curent pentru D112, cu discrepanța DUK consemnată. Nu e o
restanță; se scrie ca să nu fie confundată cu una.)*


## 31.08.2026 — REPARATE: clasificatorul de alerte și tăcerea D100 despre poziția 116

*Amândouă cerute de Costin după măsurătoarea de dimineață. Constatarea care le-a cerut e secțiunea
de mai jos.*

### 1. Eticheta devine PREDICȚIE CONFRUNTABILĂ, nu verdict

*«A greșit pe 2 din 2 acte, în direcții opuse — asta nu e o constatare, e **rata lui de eroare pe tot
eșantionul existent**. E pâlnia de intrare. Azi am aflat că minte doar fiindcă am măsurat de mână.»*

**Ce era greșit nu e „modelul a greșit", e FORMA întrebării.** Se cerea `relevanta: mare|medie` — o
judecată de ansamblu **fără motive**. O judecată fără motive **nu se poate contrazice**: când
impactul iese altfel, n-ai ce compara cu ce. De-aia a putut minți fără să se aprindă nimic.

**Ce s-a schimbat.** Nu se cere o judecată mai bună. Se cer **două fapte verificabile**, iar
relevanța se **derivă** din ele, în cod (`core/clasificator_alerte.relevanta_din`):

| faptul | de ce ăsta | valorile |
|---|---|---|
| **încotro merge documentul** | un act pe care ANAF îl emite *către* contribuabil nu ne atinge: nu-l producem noi | `catre_contribuabil` · `catre_anaf` · `necunoscut` |
| **ce declarații atinge** | singurul lucru care face un act scump pentru noi | listă de coduri, sau goală |

**Proba că nu e cosmetică:** din cele două fapte, **amândouă actele ies corect** — `603/2026` →
`zero`, `602/2026` → `mare` — fără nicio judecată de ansamblu.

**Nomenclatorul cerea el însuși minciuna.** `mare|medie` nu conținea răspunsul corect pentru un act
care nu ne atinge deloc; `603/2026` **trebuia** botezat `medie`. S-a adăugat `zero`.

**Confruntarea e acum vie și pinată**: cele două măsurători de azi sunt înregistrate în
`alerte_fiscale` cu impact, motiv, dată și commit. **Clichet: 2 măsurate, 2 greșite.** Greșelile nu
pot crește — *și proba nu poate fi ștearsă ca să scadă rata*, ceea ce e perechea regulii de migrare
de la interdicția 77: acolo datoria se muta în umbră, aici proba ar dispărea. Amândouă fac o cifră să
scadă fără ca nimic să se fi reparat.

**Ce NU păzește, declarat:** că faptele extrase sunt adevărate. Un model care spune „catre_anaf"
despre o decizie de impunere va produce în continuare o etichetă greșită — dar acum greșeala **are un
loc unde se vede**, fiindcă e o afirmație despre lume, nu un verdict.

### 2. Poziția 116 — absență DECLARATĂ, și D100 spune că nu poate

*«Zero din 19 firme o datorează; cod fără nicio instanță pe care să se probeze e clasa cu valori
implicite fabricate. Ce nu se acceptă e tăcerea de azi.»*

**Nu s-a construit**, și motivul e scris: un motor pentru o obligație fără nicio firmă purtătoare
n-ar avea niciun câmp verificat — fiecare ar fi o alegere fără probă.

**Dar nu se mai tace.** `d100.genereaza` cheamă acum `d100_pozitia_116.avertisment(prof)`: o firmă
care ar putea fi purtătoare primește o propoziție care spune **ce nu se poate, de ce, și cu ce
temei**. Legătura e gardată pe AST — un modul perfect scris și niciodată chemat e chiar clasa R70.

**Ce a scos citirea la sursă, și schimbă natura absenței.** Am adus **OUG 24/2026** în corpus ca să
pot cita criteriul, nu să-l parafrazez. Două lucruri:

- **cine datorează** (art. 2 alin. (1)): *titulari de acorduri petroliere* care extrag țiței din
  România. **Nu e un CAEN** — e un atribut pe care aplicația nu-l are sub nicio formă. CAEN-ul e un
  **proxy**, care poate **rata** un purtător, dar nu poate inventa unul: direcția erorii e scrisă și
  probată.
- **când se datorează** (art. 2 alin. (2)): **exclusiv în lunile cu Brent peste 70 USD/baril.** Deci
  obligația nu depinde doar de cine e firma, ci de un **preț de piață** pe care aplicația nu-l are și
  pentru care n-are sursă. *Chiar dacă mâine ar apărea un purtător, calculul ar rămâne neconstruibil
  fără cotație* — scris acum, ca să nu fie descoperit ca surpriză la construcție.

**Codul XML al poziției rămâne `None`**, deliberat: OPANAF 602/2026 numește **poziția**, iar în D100
poziția și codul de obligație sunt lucruri diferite (poz. 5 din tabel are `cod_oblig` 121). Un număr
pus „ca să fie" ar fi trecut de orice gardă de formă și ar fi picat **la depunere**.

**Garda de așteptare** trece cât timp nicio firmă nu e purtătoare și **pică în ziua în care apare
una** — cu ce lipsește, ca listă, în mesaj. *Se află atunci, nu la depunere.*

**RED-proof, șapte mutații, șapte roșii:** prompt-ul cere iar un verdict · relevanța nu se mai derivă
· necunoscutul rotunjit la zero · D100 tace iar · poziția 116 intră tăcut în nomenclator · codul XML
ghicit din poziție · proxy-ul începe să inventeze purtători.


## 31.08.2026 — EXERCIȚIUL DE INTRARE pe `tenant_013` și `tenant_014`: patru găuri, și o închidere

*Cerut de Costin: două serii, **invalidele primele**. Motivul lui, care s-a dovedit exact:
«dacă pornești cu cele valide și trece, nu știi dacă poarta funcționează sau e deschisă».*

### EXERCIȚIUL E CONSTRUIT, NU GĂSIT — se scrie, fiindcă altfel se citește ca observație

Notele de 2025 de pe cele două firme **le-am scris eu**, prin rutele vii, în tura asta. Ele nu
existau; exercițiul financiar precedent a fost **fabricat ca probă**, nu descoperit în date. Orice
cifră derivată din el — încadrarea `micro`, închiderea R3 — **atârnă de faptul ăsta**. Cine citește
mai târziu că „ALFA MICRO SRL e microentitate" trebuie să știe că e o firmă de test cu date puse de
mână pentru a exercita o poartă, nu o măsurătoare despre lume.

### O sondă oarbă, prinsă înainte de a produce o concluzie falsă

Prima rulare a dat **16 din 16 refuzuri fără temei** — și era **greșită**. Toate cele 16 erau
`404 tenant inexistent sau fără acces`: tokenul era al altui cabinet, iar cererile **n-au ajuns
niciodată la gărzile pe care le testam**. Am fi scris «niciun refuz nu poartă temei» despre un cod
care nici măcar nu s-a executat. *Un refuz de acces și unul de conținut arată identic într-un tabel
de coduri HTTP.* De-aia seria are acum o aserțiune anti-vacuu pe utilizator.

### SERIA I — INVALIDE: 16 cereri, patru clase de defect

| ce s-a cerut | ce s-a întâmplat |
|---|---|
| notă fără linii · linie fără cont · sumă zero · sumă negativă | **refuzate corect**, 400, cu mesaj în limba contabilului |
| **cont inexistent în planul firmei (`9999`)** | **ACCEPTAT**, 200, nota creată |
| **notă dezechilibrată** (debit 1000, credit 700) | **ACCEPTAT**, 200, nota creată |
| dată lipsă · dată în alt format | **500**, fără niciun mesaj |

**1. `9999` trece — și R54 e marcată REZOLVATĂ.** Nu e o închidere falsă; e o **gaură în domeniul
instrumentului**. `test_cont_din_corp_normalizat` caută citiri de cont după **numele cheii**:
`_e_cont()` acceptă `cont` și `cont_*`. Calea jurnalului — cea mai folosită cale de scriere în
`inregistrari_linii` — citește `l["debit"]` și `l["credit"]`. **Nu sunt în cele 27 de citiri
măsurate, nici în cele 8 declarate NELEGATE: n-au fost niciodată în domeniu.** R54 spune «toate
rutele care scriu în evidența contabilă cu un cont venit de la om» — afirmația e mai largă decât
măsurătoarea care o susține.

*A treia instanță din aceeași familie în trei zile: **R80** (o cifră creștea din vocabularul
ecranelor), **clasificatorul de alerte** (cântărea vocabularul rezumatului), și acum **R54** (își
definește domeniul după numele cheii). De fiecare dată instrumentul măsoară CUM SE NUMEȘTE ceva, nu
CE FACE.*

**2. Nota dezechilibrată intră ca ciornă și se validează.** Egalitatea debit = credit nu se
verifică la creare. `echilibru_perioada` există (R33), dar lucrează pe perioadă, nu pe notă — deci o
notă ruptă se vede abia agregat, dacă se vede.

**3. Data lipsă → 500.** Nu e un refuz: e o excepție neprinsă, fără mesaj. Un 500 nu spune nimic
omului și nu poate purta temei — e chiar forma pe care interdicția 77 o exclude.

**4. Cele 12 refuzuri reale nu poartă niciun temei.** *Interdicția 77, pe cea mai folosită cale de
scriere a aplicației.* Nu intră în clichetul de 61: `jurnal_api.py` **nu citează nicio normă**, deci
refuzurile lui sunt în UMBRĂ — populația de 778 despre care norma spune că nu se poate ști mecanic
dacă e generică sau aplică o regulă nenumită. **Aici s-a aflat, prin exercițiu, că a doua variantă e
adevărată**: „fiecare linie are nevoie de cont debit și credit" e partida dublă, adică o normă.

### SERIA II — VALIDE: ce confirmă, și ce nu

Opt note scrise și opt validate, toate `200`. **Toate cele 16 răspunsuri confirmă doar `ok`.**
Ruta nu spune ce a înregistrat, în ce perioadă, cu ce sold, nici că nota a intrat în evidență.
*Acceptarea tăcută e constatare* — iar aici tăcerea e simetrică cu găurile de mai sus: aceeași rută
nu spune nici când refuză de ce, nici când acceptă ce.

### CE S-A ÎNCHIS, prin date

`categorie_marime` pe 2026: **`nedeterminata` → `micro`**, pe amândouă firmele, cu motivul *„aceeași
încadrare în amândouă exercițiile consecutive"*. **R3 se închide pe probă**, nu pe cod — derivarea
era corectă din 30.08; îi lipsea exercițiul precedent.

Garda de așteptare a notelor explicative **a picat, cum a fost construită să facă**, și a numit ce
urmează. Am urmat pașii ei.

### CE A SCOS CITIREA LA SURSĂ — și ar fi fost o a treia concluzie inversată

Prima citire: **pct. 576 alin. (1)** — *„microentitățile nu au obligația elaborării notelor
explicative"*. Eram gata să scriu că pe amândouă firmele notele **nu se datorează**.

Punctul începe însă cu *«Cu respectarea prevederilor alin. (2)»*, iar **alin. (2) e ELIDAT în prima
apariție** a actului din corpus. Căutată a doua apariție — regula METODA §30, prima instanță — și
acolo e:

> **576. (2)** Microentitățile prezintă informațiile prevăzute la **pct. 468 lit. a), d) și e)** și
> **pct. 491 alin. (2) lit. c)**.

**Deci microentitățile NU sunt scutite integral.** Ce datorează, citit tot de la a doua apariție
(literele erau elidate și ele la prima):

| temei | ce se prezintă |
|---|---|
| pct. 468 lit. a) | politicile contabile adoptate, inclusiv bazele de evaluare |
| pct. 468 lit. d) | angajamente financiare, garanții, active și datorii contingente neincluse în bilanț |
| pct. 468 lit. e) | avansuri și credite acordate membrilor organelor de administrație, conducere și supraveghere |
| pct. 491 alin. (2) lit. c) | informații privind achizițiile propriilor acțiuni |

*A treia oară în trei zile când o citire oprită la primul nivel ar fi produs o concluzie inversată —
și a treia oară când a doua apariție a actului în același fișier a conținut ce lipsea.*


## 31.08.2026 — CE A RĂMAS DE FĂCUT, derivat din fișiere: **111 rânduri, șase surse**

*Cerut de Costin: «Derivă din fișiere lista a ce a rămas de făcut, cu sursă pe fiecare rând și cu
dimensiune probată. Unde două liste numesc același lucru diferit, e constatare. Măsurătoare, nu
construcție.» Instrument: `scripts/scan_ramas.py`.*

| fel | câte | sursa din care se derivă | dimensiune |
|---|---|---|---|
| **RESTANȚĂ** | 43 | `CONFORMITATE.md` · `### R<n>` cu `stare` ≠ REZOLVATĂ | contorul de commituri, per rând |
| **INTERDICȚIE** | 55 | `CONFORMITATE.md` · `## <n>` cu `stare` ≠ MĂSURATĂ | cifra, unde există |
| **INSTRUMENT** | 6 | `INSTRUMENTE_ROADMAP.md` · lista, stare ≠ CONSTRUIT/ACOPERIT | `?` |
| **CLICHET** | 4 | instrumentele vii, **recalculate acum** | blocul generat `CLICHETE-VII` din `PREDARE_LANT.md` |
| **ARTEFACT** | 1 | lista 3, prin `scan_lista3` | 1 rând |
| **CONSTATARE** | 2 | `GARZI.md` · titluri cu GRI sau DESCHIS | `?` |

**Singurele patru rânduri cu dimensiune SIGURĂ sunt clichetele** — ele se recalculează la fiecare
rulare. Restul poartă cifra scrisă în fișier, sau `?`. *Un rând cu `?` nu e o lipsă de raportare: e o
sarcină despre care nu se știe cât e de mare, iar asta e o informație.*

### O ORBIRE A INSTRUMENTULUI, prinsă înainte de a fi crezută

Prima rulare a dat **INSTRUMENT: 0**. Ar fi însemnat că din cele 11 nu mai e nimic de construit.
Roadmapul le ține ca **listă** (`- **#N titlu** — PROPUS: …`), iar parserul căuta un **tabel**.
**Un zero greșit e mai rău decât o lipsă**: se citește ca terminat. Prins fiindcă cifra contrazicea
ce știam, și am verificat **formatul** în loc să cred cifra. După reparație: **6**, dintre care
`#2` PARȚIAL și cinci PROPUSE.

### DIVERGENȚA DE NUME — găsită prin exercițiu, nu prin potrivire mecanică

Potrivirea automată a găsit **zero**, și asta e **modul de eșec 3 al instrumentului**, declarat: două
liste care numesc același lucru cu vocabular complet diferit **nu se pot potrivi mecanic** — exact
clasa căutată. Cifra e un plafon inferior.

Una reală a ieșit din exercițiul de intrare de azi:

> **Calea jurnalului scrie conturi venite de la om, și e invizibilă în AMÂNDOUĂ listele care ar
> trebui s-o vadă — din motive diferite.**

| lista | ce numără | de ce nu vede calea jurnalului |
|---|---|---|
| **R54** — „contul din corpul cererii nu e confruntat cu planul" | citiri de cont, recunoscute după **numele cheii** (`cont`, `cont_*`) | jurnalul citește `l["debit"]` și `l["credit"]` — **nu sunt în cele 27 măsurate, nici în cele 8 declarate NELEGATE** |
| **interdicția 77** — „blocaj fără temei" | refuzuri fără temei, împărțite după **dacă modulul citează legea** | `jurnal_api.py` nu citează nicio normă → refuzurile lui cad în **UMBRA**, populația declarat nedeplafonată |

**Același cod, două liste, niciuna nu-l vede.** R54 îl ratează fiindcă se uită la *cum se numește*
cheia; 77 îl lasă afară fiindcă se uită la *ce citează* modulul. Fiecare criteriu e apărabil singur;
împreună lasă o gaură pe care niciunul n-o raportează.

Iar exercițiul a arătat că **umbra chiar conține norme**: *„fiecare linie are nevoie de cont debit și
credit"* e partida dublă. Norma 77 spune că nu se poate ști mecanic dacă un modul din umbră aplică o
regulă nenumită — **aici s-a aflat că da**, și s-a aflat exercitând, nu măsurând.

*Nereparat, deliberat — s-a cerut măsurătoare. Ce ar cere reparația, ca să nu se redescopere: R54
și-ar defini domeniul după **unde ajunge valoarea** (`inregistrari_linii.cont_debit`), nu după numele
cheii din cerere. Atunci calea jurnalului ar intra în domeniu, iar refuzurile ei ar avea unde să fie
numărate.*


## 31.08.2026 — REPARATE cele trei găuri din calea jurnalului. **A patra era a sondei mele**

*Costin: «Cele patru găuri se repară, în ordinea gravității.» Sunt trei — a patra n-a fost o gaură.*

### A PATRA NU EXISTA — și se scrie primul, ca să nu fie „reparată"

Am numit un caz de probă *„notă dezechilibrată"*: două linii, `4111/704/1000` și `5121/4111/700`.
**Nu e dezechilibrată.** Schema ține `cont_debit`, `cont_credit` și `suma` **pe aceeași linie**,
amândouă `NOT NULL` — deci fiecare linie e o pereche echilibrată **prin construcție**, iar totalul
debitor egalează totalul creditor oricâte linii ar fi. Aplicația a avut dreptate s-o accepte;
**sonda mea a etichetat greșit cazul.**

*A doua oară azi când o sondă de-a mea a produs o concluzie falsă înainte de a fi verificată — prima
a fost tokenul altui cabinet, care dădea `404` pe toate cele 16.* Un cod care ar „verifica
echilibrul" aici ar fi **cod mort**, iar gardul îl împiedică: proba citește invariantul **din
schemă**, și cade dacă vreo coloană devine nullable — atunci el chiar ar trebui verificat în cod.

### 1. Contul din afara planului intra în evidență *(cea mai gravă)*

`9999` era acceptat. `cont_valid.cere_cont` există din 26.08 și e legat pe 19 din 27 de citiri —
dar **calea jurnalului nu era printre ele, și nici printre cele 8 declarate NELEGATE**: domeniul lui
R54 recunoaște citirile de cont după **numele cheii** (`cont`, `cont_*`), iar aici cheile se numesc
`debit` și `credit`. Legată acum, pe **amândouă** căile — `creeaza` **și** `editeaza`, care aveau
aceeași gaură, în cod duplicat. Refuzul numește contul, spune unde se adaugă, și sugerează vecinii.

### 2. O dată care nu e dată ieșea **500**, fără niciun mesaj

Nu era un refuz: era o excepție neprinsă. Cauza nu era poarta, ci **ordinea** — `_cere_luna_deschisa`
întreba *„e luna închisă?"* despre `"10.03.2025"`, iar driverul de bază ridica **înainte** ca
producătorul (care are refuzul scris) să fie chemat. Data se validează acum **înaintea** porții de
perioadă.

### 3. Cele 12 refuzuri fără temei — acum 0 din 14

Interdicția 77, pe cea mai folosită cale de scriere a aplicației. Două temeiuri **separate**, fiindcă
sunt două întrebări:

| refuzul | temeiul |
|---|---|
| lipsește o linie · lipsește un cont · contul nu e în plan | **Legea 82/1991 art. 5 alin. (1)** — obligația de a conduce contabilitatea în partidă dublă |
| lipsește data · data nu e o dată · suma nu e pozitivă | **art. 6 alin. (1)** — orice operațiune se consemnează **în momentul efectuării ei** |

*Un singur temei ar fi trimis cititorul la articolul greșit — greșeala făcută ieri la
registrul-inventar, unde un refuz de moment cita temeiul conținutului.*

**Ruta trece temeiul mai departe.** Până azi îl turtea într-un șir: producătorul putea spune sub ce
normă refuză, iar `_jurnal_rez` arunca partea aia.

### CE A CONFIRMAT REEXERCITAREA

Aceleași 16 cereri, după reparații: **14 refuzuri, 0 fără temei** (erau 12 din 12 fără). Singurul
`200` e cazul pe care l-am etichetat greșit. `9999` refuzat, data în alt format refuzată cu mesaj.

**RED-proof, cinci mutații, cinci roșii:** confruntarea cu planul scoasă · se verifică doar prima
linie · temeiul scos de pe refuzuri · data în alt format trece ca validă · `suma` devine nullable în
schemă (adică partida dublă **nu mai** e garantată de construcție).

### DATELE PUSE AZI RĂMÂN — scenariu declarat

*Costin: «Sunt scenariu declarat, iar ștergerea lor redeschide R3 și lasă registrele neprobate.»*

Cele **8 note validate de 2025** de pe `tenant_013` și `tenant_014` **rămân**. Nu sunt reziduu de
probă: sunt exercițiul financiar precedent, construit deliberat, iar pe el stau încadrarea `micro`,
închiderea R3 și delimitarea notelor explicative. **Cine le găsește mai târziu să nu le curețe.**

*Ce a fost reziduu s-a șters: cele 12 note ale seriei de invalide, în două runde — patru care
intraseră prin găurile de mai sus, și două care intră acum legitim, fiindcă erau valide.*


## Inventar (generat, 28.08.2026)

Blocul de mai jos e produs de `scripts/scan_garzi_inventar.py --md` și păzit de
`core/test_garzi_inventar.py`: dacă documentul și instrumentul diverg, poarta cade. Regenerare:
`./venv/bin/python scripts/scan_garzi_inventar.py --md`, rescris între marcaje.

**Ce e și ce nu e.** E răspunsul la *„ce gărzi există și ce afirmă fiecare"*. **Nu** e răspunsul la
*„sunt bune?"* — nu numără aserțiuni, nu spune dacă păzesc ceva viu, nu deosebește o gardă calibrată
de una care trece degeaba. Pentru aia sunt instrumentele de FAZA 4 (`scan_instrumente`,
`scan_axa_garzi`, `scan_mutatie_garzi`) și `scan_garzi_pe_text`.

## 30.08.2026 — CONSTATARE **ÎNCHISĂ 31.08.2026**: «Interactive authentication required» lângă `NOPASSWD: ALL` nu era o contradicție de identitate, era **absența oricărei identități**

*Formulată de Costin ca GRI, cu cuvintele lui: «cele două căi rulează sub identități diferite».
**Se închide cu temei, nu prin raționament**: sonda de debug a rulat pe 31.08, jurnalul n-a mai
fost gol, iar ce s-a citit acolo a schimbat concluzia — nu a confirmat-o.*

### TEMEIUL ÎNCHIDERII *(Costin, 31.08.2026, din jurnalul sondei)*

Restartul prin polkit se autorizează **ONE-SHOT ca `unix-user:costin`, exclusiv interactiv, prin
`pkttyagent`**. `pkcheck` refuză fără `-u`; **nicio regulă nu acordă acțiunea pe grup.**

Restartul care a eșuat rula **fără agent de autentificare**, deci autorizarea **nu se putea forma**.

**Nu era identitate greșită. Era absența oricărei identități.** Diferența nu e de nuanță: o
identitate greșită se repară schimbând-o pe cea potrivită — o autorizare care nu se poate FORMA nu
are ce identitate să primească, oricâte reguli s-ar scrie. Ipoteza «două căi, două identități» era
plauzibilă, se potrivea cu toate probele de ieri, **și era greșită**. A ținut exact până la prima
măsurătoare care putea s-o contrazică.

### OBSERVAȚIE SECUNDARĂ — se consemnează, NU se repară

Linia `Identity unix-group:admin is not valid, ignoring` rămâne în jurnal. **Costin, expres:** nu se
creează grupul, nu se rescrie spre `unix-group:sudo`, nu se adaugă regulă permisivă. **Nu se atinge
nimic din polkit** până nu se citește fișierul care declară identitatea și **până nu se stabilește
dacă e al nostru sau implicit de distribuție.**

*De ce ordinea asta și nu invers: o «reparație» pe o identitate declarată de distribuție ar fi o
modificare locală într-un fișier care se rescrie la următorul `apt upgrade` — adică o reparație care
dispare fără să anunțe. Iar dacă e a noastră, întrebarea nu mai e cum se repară, ci cine a scris-o
și pentru ce.*

### CE SE ȘTIE — dovedit azi, pe mașină, nu dedus

| ce | proba |
|---|---|
| `costin` avea `(ALL) NOPASSWD: ALL` | `sudo -n -l`, din `/etc/sudoers.d/costin-nopasswd` (14.06.2026) |
| **cu** `sudo`, repornirea merge fără parolă | `sudo -n systemctl restart iconta-nou` → exit 0; `ActiveEnterTimestamp` a sărit la 10:45:05 |
| **fără** `sudo`, aceeași comandă, același utilizator, aceeași mașină, **eșuează** | `systemctl restart iconta-nou` → `Failed to restart iconta-nou.service: Interactive authentication required.` |

**De aici, temeiul.** Sunt **două sisteme de autorizare, nu unul**: `sudo` întreabă **sudoers**;
`systemctl` chemat direct de un utilizator neprivilegiat întreabă **polkit**. *Polkit nu citește
sudoers.* Deci `NOPASSWD: ALL` nu spune absolut nimic despre calea fără `sudo` — iar mesajul
„Interactive authentication required" e răspunsul lui polkit, nu al lui sudo. Cele două afirmații nu
se contrazic: vorbesc despre identități diferite ale aceleiași persoane.

### CE NU SE ȘTIE, și de-aia rămâne GRI

**Sub ce identitate a rulat repornirea care a eșuat pe 30.08, în jur de 09:00.** Mecanismul de mai sus
o explică *dacă* a fost calea fără `sudo` — dar asta e o ipoteză care se potrivește, nu o măsurătoare.
Nu se poate afirma din urme.

**De ce nu se poate citi, măsurat:** dovada ar sta în `/var/log/auth.log` (`syslog:adm`, mod `0640`)
sau în jurnalul de sistem. Identitatea de deploy e în grupurile `costin sudo users` — **nu** în `adm`
și **nu** în `systemd-journal`. `journalctl` fără privilegii spune singur: *„You are currently not
seeing messages from other users and the system."* Deci exact identitatea care a executat actul e cea
care nu-i poate citi urma.

### CE S-A CITIT, DUPĂ CE IDENTITATEA DE DEPLOY A PRIMIT DREPTUL (30.08.2026, seara)

Costin a pus `costin` în grupul `adm` — **și a ținut `usermod` în afara setului îngust**, cu motivul:
*„apartenența la grupuri e schimbare de identitate, nu operațiune de deploy; în set, setul s-ar putea
lărgi singur."* Refuzul lui a fost, spune el, chiar dovada că îngustarea e reală.

Cu `auth.log` citibil, fereastra **08:30–10:50** conține **exact două** invocări `sudo`, amândouă
reușite, niciuna în jurul orei 09:00:

| ora | ce | de unde se vede cine |
|---|---|---|
| **08:47:02** | `costin : PWD=/home/costin/iconta_nou ; USER=root ; COMMAND=/usr/bin/systemctl restart iconta-nou` | `PWD` e **repo-ul** → `post-commit`, după commitul `4b6d664` |
| **10:45:05** | același, `PWD=/home/costin` | repornirea cerută de mine, prin `ssh` |

**Zero** intrări polkit. **Zero** `sudo` eșuat. **Zero** alt `systemctl`.

### CALIBRAREA CARE FACE ABSENȚA CITIBILĂ — și fără ea n-ar fi însemnat nimic

O absență din log nu spune nimic până nu se știe **ce anume s-ar fi văzut dacă s-ar fi întâmplat**.
Amândouă capetele s-au probat pe instanțe de azi, produse de mine:

- **un `sudo` REFUZAT SE LOGHEAZĂ**: `12:28:43 … costin : a password is required ; COMMAND=/usr/bin/journalctl -u iconta-nou --since …` — chiar `journalctl`-ul pe care regula îngustă mi l-a refuzat;
- **un refuz POLKIT NU se loghează**: refuzul pe care l-am provocat deliberat (`systemctl restart iconta-nou` fără `sudo`, care a răspuns *„Interactive authentication required"*) **n-a lăsat nicio urmă**. `polkit` are **0** apariții în `auth.log` și **0** în jurnalul întregii zile, deși `polkit.service` e `active`.

### CE SE ȘTIE ACUM — și e mai mult decât ieri

**Calea `sudo` e ELIMINATĂ PRIN DOVADĂ.** Orice încercare pe ea, reușită sau refuzată, ar fi fost
scrisă; în fereastră sunt doar cele două de mai sus. Deci repornirea despre care s-a spus *„repornit"*
**nu a trecut prin identitatea de deploy**.

**Ipoteza de ieri NU s-a confirmat ca instanță — și bine că n-a fost acceptată.** Mecanismul
sudoers-vs-polkit e real și dovedit, dar el explică *cum ar putea eșua*, nu *ce s-a întâmplat*. Ieri
se potrivea perfect cu faptele; azi se vede că potrivirea nu era o măsurătoare. *Exact de-aia
constatarea a fost ținută GRI.*

### CE A RĂMAS, și de ce nu se poate închide de tot

**Dacă a existat totuși o încercare pe calea fără `sudo`, ea nu poate fi nici confirmată, nici
exclusă** — fiindcă polkit nu scrie nimic pe mașina asta, dovedit mai sus. Cele două rămase sunt
indistingibile din urme:

1. nu s-a făcut nicio încercare pe server;
2. s-a făcut una pe calea fără `sudo`, și polkit a refuzat-o tăcut.

Nici sursa conexiunii nu desparte: **toate cele 223 de sesiuni** din fereastră vin de la **aceeași
adresă**, deci comenzile mele și cele tastate cu `!` arată identic.

### CONDIȚIA DE ÎNCHIDERE, acum mult mai mică

Nu mai e „citește logurile" — s-au citit. E: **fă calea fără `sudo` să lase urmă.** O regulă în
`/etc/polkit-1/rules.d/` care doar *loghează* verificarea de autorizare pentru
`org.freedesktop.systemd1.manage-units` și întoarce `undefined` (nu decide nimic) ar face întrebarea
decidabilă de aici încolo.

**INSTALATĂ de Costin (30.08.2026, seara)** — `install` a rămas afară din setul îngust, cu același
motiv ca `usermod`: *„scrie oriunde ca root, deci în set setul și-ar putea rescrie propriile reguli."*

**ȘI NU FUNCȚIONEAZĂ ÎNCĂ — măsurat, nu presupus.** `polkitd` a repornit la 19:20:29 și a încărcat
**5 reguli**, deci fișierul e citit. Verificările **chiar au loc**: `pkcheck --action-id
org.freedesktop.systemd1.manage-units` întoarce *„Authorization requires authentication"*, iar
`systemctl restart iconta-nou` fără `sudo` dă același *„Interactive authentication required"*.
**Dar `journalctl -t polkitd` n-are, după niciuna, altceva decât liniile de pornire.**

**Ce se poate deduce, și ce nu.** `pkcheck` a primit rezultatul implicit al politicii, nu unul dat de
o regulă — deci, cel mai probabil, **nicio regulă n-a decis**, iar a mea *a rulat* și n-a lăsat urmă.
Asta arată spre `polkit.log()` care nu ajunge în jurnal la nivelul implicit de log al lui `polkitd`
(versiunea 124), **nu** spre limita pe care o declarasem în comentariul regulii (o regulă anterioară
care decide prima). *Amândouă rămân posibile: `/etc/polkit-1/rules.d/` nu se poate citi fără root, deci
nu pot vedea ce mai e acolo și în ce ordine.*

**Următorul pas, mic și numit:** `polkitd` pornit cu log de debug — un drop-in cu
`Environment=SYSTEMD_LOG_LEVEL=debug` (sau `G_MESSAGES_DEBUG=all`) pe `polkit.service` —, apoi se
reface proba de mai sus. Dacă linia apare, cauza era nivelul de log; dacă nu, era ordinea regulilor,
și atunci discuția despre numerotare se redeschide **cu o măsurătoare în spate**, nu cu o preferință.

*Ce se închide până aici: trecutul (calea `sudo` e eliminată prin dovadă). Ce rămâne deschis: exact
capacitatea de a răspunde data viitoare — și acum se știe și de ce nu funcționează încă.*

### LIMITA DECLARATĂ a reparației care s-a făcut totuși

Regula îngustă (`/etc/sudoers.d/iconta-nou`) rezolvă **calea cu `sudo`** — singura pe care o folosește
`scripts/githooks/post-commit`. **Nu atinge polkit.** Dacă cineva reporneste serviciul **fără** `sudo`,
va primi același mesaj, iar regula nouă nu-l va ajuta cu nimic. *Un gard care rezolvă o cale și tace
despre cealaltă e citit ca acoperire totală — de-aia limita se scrie.*

### O A TREIA INSTANȚĂ, DIN ACEEAȘI ZI, A ACELUIAȘI TIPAR

Argumentele se potrivesc **literal** în sudoers, iar asta a lovit de trei ori pe 30.08:

1. `/etc/sudoers.d/iconta` era scrisă pe `iconta.service` — **unitate care nu există**. N-a acoperit
   niciodată nimic, și tăcerea ei a fost „rezolvată" cu `NOPASSWD: ALL`.
2. Prima formă a regulii noi acoperea `restart iconta-nou.service`, dar hook-ul cheamă
   `restart iconta-nou` — **fără sufix**. Prinsă înainte de a scoate blanket-ul; acum se acoperă
   amândouă formele.
3. `sudo -n journalctl -u iconta-nou --since ... --no-pager` e **refuzat**: regula fixează argumentele
   exact, iar orice argument în plus nu se mai potrivește. **Consecință: diagnosticul pentru care
   `journalctl` a fost pus în set nu se poate face cu el.** Nereparat deliberat — o extindere cu
   `*` ar lărgi ce tocmai s-a îngustat, în aceeași tură, fără să fie cerută.

*Partea generală: o regulă de autorizare care nu se potrivește **nu țipă** — pur și simplu nu se
aplică. Absența ei arată identic cu absența cererii, iar la capătul lanțului cineva astupă gaura cu
cea mai largă permisiune posibilă.*

### MĂSURĂTOAREA CERUTĂ ODATĂ CU ÎNCHIDEREA — cine, din lanț, presupune privilegiu fără parolă

*Costin, 31.08.2026: «De verificat, ca măsurătoare, nu ca reparație: dacă vreun pas din lanțul de
publicare presupune restart fără parolă. Acela eșuează tăcut.» Măsurat pe mașină, nu dedus.*

**Lanțul de publicare propriu-zis e curat.** Un singur restart în tot repo-ul —
`scripts/githooks/post-commit:80`, `sudo -n systemctl restart iconta-nou` — și e în setul îngust.
`-n` e prezent, deci **eșuează zgomotos**: scrie santinela `.git/RESTART_ESUAT` în loc să aștepte o
parolă care nu vine. Calea explicită rămâne `sudo systemctl restart iconta-nou`.

**Cele trei timere `iconta` rulează ca `User=costin` și nu repornesc nimic.** Singurul `sudo` din
`crontab` e `iconta-config-backup.sh` — în set, deci merge (fără `-n`, dar cum e NOPASSWD nu se
oprește să întrebe).

**Ce NU e acoperit, găsit căutând:**

| unde | ce cere | în set? | `-n`? | ce se întâmplă rulat neinteractiv |
|---|---|---|---|---|
| `mentenanta.sh:9,10,13` | `ln -sf` ×2 · `nginx -t` · `systemctl reload nginx` | **nu**, niciunul | nu | cere parolă → atârnă sau cade; e chemat doar de mână, dar e chiar comutatorul de intrare/ieșire din mentenanță |
| `verificator_neconformitati.sh:28,29` | `cat /proc/PID/environ` | **nu** | nu | **cel mai rău caz: nu tace, MINTE** |

**Instanța, probată pe mașină acum:** cu `sudo -n`, citirea mediului procesului e refuzată, iar
verificatorul tipărește `FAIL NC-07 JWT_SECRET lipsește din proces!`. **Secretul e acolo.** Ce
lipsește e dreptul de a te uita — iar linia nu deosebește «nu e» de «n-am putut vedea». E chiar
clasa pe care registrul o refuză în altă parte: *un necunoscut nu se rotunjește la «știu că nu»*.

**Nereparat, deliberat** — Costin a cerut măsurătoare, nu reparație. Ce ar însemna reparația, ca să
nu se redescopere: un al treilea rezultat, `NU S-A PUTUT VERIFICA`, distinct de `PASS` și de `FAIL`,
pe fiecare pas care are nevoie de privilegiu. Nu extinderea setului — un verificator care are nevoie
de mai multe drepturi ca să spună adevărul e un verificator care cere să fie crezut pe încredere.


## 30.08.2026 — CONSTATARE **GRI**: cei 0,2463% de pe ecranul `banca` NU erau o regresie vizuală, dar nu se știe ce erau

*Cerut de Costin: „se explică sau rămâne constatare cu temei". **Se explică pe jumătate**, iar
jumătatea care lipsește se scrie ca atare.*

### CE S-A MĂSURAT

`frontend_test/vizual/raport_baseline.json`, scris la **07:09**, dădea `banca` drept **SCHIMBAT**:
**5675 pixeli, 0,2463%** — de aproape cinci ori pragul de `0,05%`, și cu un ordin de mărime peste
restul ecranelor (toate între **0,0033%** și **0,0144%**, adică zgomot de antialiasing).

**Rulat din nou la 12:39, contra ACELUIAȘI baseline, neatins** (`baseline/banca.png`, 26.08 00:30):

| ecran | 07:09 | 12:39 |
|---|---|---|
| **banca** | **SCHIMBAT · 5675 px · 0,2463%** | **identic · 130 px · 0,0056%** |
| casa · rapoarte · declaratii | identic · 0,0056% | identic · 0,0056% |
| stat_plata | identic | **SCHIMBAT · 8,8397%** — asta e munca de azi (compoziția netului), deci unealta chiar vede o schimbare reală |

### CE SE POATE AFIRMA

**Nu era o regresie vizuală.** Referința n-a fost atinsă între cele două rulări, iar a doua o dă
identică. Ceva a fost altfel **la 07:09**, și nu mai e.

**Deci ecranul `banca` nu e determinist între rulări** — exact clasa pe care roadmap-ul o are deschisă
ca **#8, „baseline determinist (freezegun)"**, și pe care unealta însăși o numește în docstring:
*„dacă self-diff e mare, baseline-ul ar fi zgomotos → se propune prag / mascare, nu se impune tacit"*.

### CE NU SE POATE AFIRMA, și de-aia e GRI

**Ce anume varia.** Trei ipoteze se potrivesc la fel de bine cu ce s-a măsurat, iar a alege una ar fi
exact greșeala pe care registrul o refuză în altă parte:

1. **randare pe jumătate** — `capteaza()` așteaptă `400 ms` ficși, apoi fotografiază. Un panou care
   își încarcă datele mai lent apare gol. 5675 de pixeli e cam un bloc de conținut;
2. **date care s-au schimbat și au revenit** — sunt joburi la fiecare 15 minute în `crontab`;
3. **conținut dependent de timp** — o fereastră „ultimele N zile" care la 07:09 cădea altfel.

*Ipoteza 1 e cea mai economică, dar „se potrivește" nu e „s-a măsurat".*

### CE S-A MĂSURAT DUPĂ, când Costin a cerut regenerarea (30.08.2026, seara)

Modul implicit (self-diff: **două capturi în aceeași rulare**) a rulat pe toate cele 14 ecrane.
Rezultatul, uniform:

**`banca`: `STABIL` — 0 pixeli, 0,0000%.** La fel toate celelalte 13, inclusiv `stat_plata`.

### CE ELIMINĂ ASTA, și ce NU

**Eliminată: ipoteza 1 (randare pe jumătate din cauza celor 400 ms).** Dacă panoul s-ar încărca
uneori mai lent decât fereastra de așteptare, două capturi la câteva secunde una de alta ar diferi
măcar câteodată. Diferă cu **zero pixeli**. Deci pe rularea asta nu există nici intermitență, nici
zgomot de randare.

*Precizarea care contează, ca să nu se citească mai mult decât spune:* un panou care ar fi **mereu**
gol la 400 ms ar da tot self-diff 0 — și ar fi identic și cu referința, fiindcă și ea s-a capturat la
400 ms. Deci self-diff-ul nu exclude o lentoare **constantă**; exclude una **intermitentă**. Iar
diferența de la 07:09 a fost, prin definiție, intermitentă: a apărut o dată și n-a mai apărut.

**Rămân ipotezele 2 și 3** — date schimbate între rulări (sunt joburi la fiecare 15 minute în
`crontab`) sau conținut dependent de timp. Nu se pot despărți una de alta din ce avem.

### CE S-A SCHIMBAT ÎN PROBE, și e ireversibil

Modul implicit **rescrie referințele**. Toate cele 14 baseline-uri din **26.08 00:30** au fost
înlocuite cu capturi de acum. Deci:

- **`stat_plata` nu mai e vechi cu 8,84%** — asta a fost cererea lui Costin, și e făcută;
- **referința din 26.08, pe care stătea măsurătoarea de 0,2463%, nu mai există.** Cifrele acelei
  măsurători trăiesc **numai în tabelul de mai sus** — nici raportul nu e în git (`raport_*.json` e
  ignorat). *Se scrie aici pentru că altfel cineva care ar vrea s-o refacă ar găsi o lume în care
  întrebarea nu se mai pune, și ar crede că tabelul minte.*

### CONDIȚIA DE ÎNCHIDERE, ce a mai rămas din ea

Întrebarea „ce anume varia" **nu se mai poate pune despre 30.08**: referința a dispărut, iar starea
care a produs diferența nu se poate reconstitui. Ce rămâne e clasa, nu instanța — **#8 din roadmap,
„baseline determinist"**. Constatarea se închide când unealta capătă un mod care **măsoară fără să
rescrie** (ori `--doar <ecran>`, ori o referință secundară), fiindcă abia atunci o diferență
între rulări se poate investiga fără să fie ștearsă de investigație.

*Lecția, mai largă decât ecranul ăsta: o unealtă care rescrie referința ca să măsoare nu poate fi
folosită de două ori pe aceeași întrebare.*

### O CONTRADICȚIE GĂSITĂ PE DRUM, nereparată fiindcă e o decizie, nu o scăpare

Două documente spun invers despre același fișier:

- `frontend_test/vizual/.gitignore`, în clar: *„SE versionează (referință pentru comparație):
  `baseline/*.png` …"*, cu `!baseline/` care le scoate din ignorare;
- `frontend_test/vizual/baseline_scan.py`, în docstring: *„Baseline-urile NU sunt urmărite în git
  (decizia lui Costin, 26.08.2026): sunt referințe locale, regenerabile."*

**Starea reală e a doua**: `git ls-files frontend_test/vizual/baseline/` întoarce gol — deci
`!baseline/` a fost scris, dar fișierele n-au fost adăugate niciodată. *Regula scrisă nu e regula
păzită: `.gitignore` doar permite, nu adaugă.*

**Nereparată deliberat**: alinierea cere o decizie — ori se versionează (și atunci referința devine
reproductibilă pentru oricine, cu costul a ~5 MB de PNG-uri care se rescriu la fiecare rulare), ori
se scoate `!baseline/` și comentariul, ca documentul să spună ce se întâmplă. **Prima variantă ar fi
închis chiar constatarea de mai sus**, fiindcă referința de la 26.08 ar fi existat în istorie.

### DOUĂ OBSERVAȚII DE CITIRE, care nu sunt defecte dar induc în eroare

- **`"ok": true` lângă `"stare": "SCHIMBAT"` nu e o contradicție**: `ok` spune că scanul **a rulat
  fără excepție**, nu că ecranul e neschimbat. Verdictul e în `stare`. Citit repede, rândul pare să
  se contrazică singur.
- **Baseline-urile nu sunt în git** (decizia lui Costin, 26.08.2026): sunt referințe locale,
  regenerabile. Deci o comparație e reproductibilă doar cât timp nimeni nu rulează modul implicit —
  și nimic nu împiedică asta.
- **Nici raportul nu e în git**: `frontend_test/vizual/.gitignore` are `raport_*.json`. A doua rulare
  l-a suprascris, deci **cifrele de la 07:09 nu mai există în niciun fișier — trăiesc doar în tabelul
  de mai sus**. Se scrie fiindcă altfel constatarea asta ar trimite la o probă care nu se mai poate
  deschide, iar cine ar căuta-o ar găsi rularea de la 12:39 și ar crede că tabelul minte.

### BASELINE-UL LUI `stat_plata` — FĂCUT

Era vechi cu **8,84%**, fiindcă ecranul chiar s-a schimbat (compoziția netului). Regenerat odată cu
celelalte 13, la cererea lui Costin. *Ordinea a contat: întâi s-a citit ce se putea citi din
referința veche, apoi s-a rescris.*


## 31.08.2026 — Tabelul care scria «se recalculează, nu se citesc de aici» avea o cifră veche de trei zile. Cele plafonate erau corecte

**`core/test_clichete_generate.py` — NOU, 12 teste.** `PREDARE_LANT.md` purta un tabel de patru
clichete, fiecare cu numele instrumentului lui pe rând, sub propoziția *«se recalculează, nu se
citesc de aici»*. Recalculate toate patru:

| clichet | scris | acum | plafonat? |
|---|---|---|---|
| 77 — refuzuri fără temei, module care citează legea | 61 | 61 | **da**, contra `BASELINE` |
| 50 — aserțiuni ancorate pe text | 1222 | 1222 | **da**, clichetul 50 |
| R80 — rute despre care detectorul nu poate afirma nimic | 7 | 7 | **da** |
| 77u — UMBRA | 779 | **781** | **nu**, deliberat |

**Cele trei plafonate erau corecte. Singura greșită era singura fără clichet** — iar ea circula în
aceeași zi în **trei** valori, prin trei locuri: mesajul commitului `2200432` care a născut
instrumentul, predarea plus `GARZI.md`, și codul. Reconstituit mecanic, pe worktree-uri detașate:
valorile aparțin lui `2200432`, `edaada7^` și `edaada7`; creșterea vine din reparația căii
jurnalului, care a adăugat două refuzuri într-un modul ce nu citează legea. *Nimic n-a văzut
mișcarea, fiindcă ce vede o mișcare e un clichet, iar o populație fără clichet n-are ce.*

**Ce face imposibil:** o cifră de clichet scrisă în predare și nepotrivită cu codul (comparație pe
**structura** tabelului, cod cu cod — METODA §23 —, plus caracter cu caracter peste ea) · un clichet
**măsurat și nescris**, direcția pe care egalitatea de cifre n-o vede · un rând sau un marcaj șters
· o cifră a umbrei scrisă în **proza** predării, în afara blocului generat.

**Calibrare, în ambele direcții (METODA §22), pe forma reală:** cifra umbrei mutată înapoi cu două ·
rândul umbrei șters cu toate celelalte cifre corecte · marcajul de start șters · blocul probat că
**nu** poartă oră sau dată, altfel s-ar schimba la fiecare rulare și cineva l-ar scoate ca să poată
comite. **Anti-vacuu:** `scan_ramas.clichete()` înghite excepțiile de import, deci un rând lipsă e un
instrument rupt, nu un clichet închis — testul cere cele patru coduri și o cifră pe fiecare.

**RED-proof:** 5 roșii din 10 pe documentul nereparat, inclusiv cele 3 locuri cu cifră de mână. După
reparație, 12 verzi. **Garda m-a prins pe mine**: paragraful pe care îl scrisesem ca să povestească
derapajul purta chiar cifrele interzise. *Am rescris proza, nu garda* — istoria stă în `ISTORIC.md` și
în antetul gărzii, fiindcă predarea e fișier de **stare curentă** și orice cifră din ea pretinde că e
de acum.

**O SINGURĂ SCUTIRE, și e structurală:** tabelul **cifrelor invalidate** din predare. E, prin
construcție, locul unde valorile vechi trebuie să stea — *«o cifră ai cărei termeni nu se mai pot
reconstitui se INVALIDEAZĂ, nu se corectează; tabelul se POARTĂ»* —, iar apartenența la el **este**
declarația că cifra nu mai e curentă. Tăierea e pe structură (titlu → titlul următor), nu pe un
marcaj pus cu mâna. Are **anti-vacuu propriu** (secțiunea trebuie să existe, să fie una, iar tăierea
să nu înghită documentul) și **calibrare pe direcția care contează**: o cifră pusă în proza
obișnuită, cu tabelul scutit la locul lui, e tot prinsă. *Scutirea a fost cerută de a doua respingere
a gărzii — rândul de invalidare pe care tocmai îl scrisesem. Am îngustat-o structural, nu am scos
garda.*

**Ce NU face, declarat:** nu plafonează umbra (Costin, 31.08: *«rămân nemăsurate, definitiv»*) — un
plafon ar transforma o cifră deliberat nedeplafonată într-un clichet de facto, cu costul unuia și
fără protecția lui · nu acoperă naratiunea **datată** din `GARZI.md`, `ISTORIC.md`, `CONFORMITATE.md`
și `METODA_VERIFICARE.md`, unde o cifră e o afirmație despre CÂND s-a măsurat și are voie să
îmbătrânească · nu verifică dacă instrumentele numără **bine** — fiecare are calibrarea lui.

**Reparat în afara predării, în aceeași tură:** `GARZI.md` avea două locuri care pretindeau prezentul
(rândul „recalculate acum" din tabelul lui `scan_ramas`, și cifra umbrei de lângă divergența
`jurnal_api`) — amândouă trimit acum la blocul generat. `METODA_VERIFICARE.md` §23 și
`CONFORMITATE.md` 18 scriau **1341** și **119** lângă 1222: singurul plafonat rămăsese corect,
celelalte două crescuseră la 1342 și 120 fără ca nimeni să vadă. **S-au șters, nu s-au corectat** —
altfel ar îmbătrâni iar; argumentul (*«119 e plafon superior, 1222 plafon inferior»*) nu depindea de
ele.

**Al cincilea rând al tabelului — rata clasificatorului de alerte — a plecat în blocul de DATE**
(`scripts/scan_predare_cifre.py`), unde îi e locul: se derivă din confruntarea predicțiilor cu
faptele, nu din cod. Blocul de clichete rămâne derivat **numai din cod**, deci nu poate pica din
cauza unei firme create în timpul porții — limita operațională pe care blocul de date o are scrisă.

## 31.08.2026 — Verificatorul care nu tăcea, ci mințea: al treilea rezultat, plus trei orbiri latente și un cod de ieșire care contrazicea propriul rezumat

**`verificator_neconformitati.sh` reparat + `core/test_verificator_al_treilea_rezultat.py` — NOU,
18 teste.** Cerut de Costin: *«repară-l acum»*.

**Instanța, confirmată pe condiția reală, nu pe una sintetică:** `sudo -n true` chiar cere parolă pe
stația asta, deci linia `FAIL NC-07 JWT_SECRET lipseste din proces!` se producea **live**. Secretul
era acolo; lipsea dreptul de a te uita.

**GENERALIZAREA A FOST MĂSURATĂ, NU PRESUPUSĂ — și m-a contrazis.** Plecasem cu ipoteza că și
`psqlv` minte, fiindcă folosește `sudo`. Rulat: `sudo -n -u postgres psql` **merge** (setul îngust îl
conține), deci NC-01/02 erau oneste. *Un scan pe forma brută a codului supra-numără; citirea la sursă
a corectat clasa.* Ce a rămas, după măsurare:

| formă | stare | ce făcea |
|---|---|---|
| `sudo` indisponibil la `/proc/<pid>/environ` | **VIE**, 2 linii | raporta absența secretului |
| interogarea care nu rulează | LATENTĂ | șir gol ≠ `"0"` → FAIL despre date necitite |
| fișierul care lipsește | LATENTĂ | `grep` eșuează → FAIL despre un fișier nedeschis |
| globul care nu potrivește nimic | LATENTĂ | `wc -l` dă 0 → **PASS** pe mulțime goală |
| ancora ștearsă de o rescriere legitimă | **VIE**, 1 linie | FAIL pe vecie despre un obiect inexistent |
| `EXIT=0` peste `FAIL: 3` | **VIE** | rezumatul spunea roșu, codul de ieșire spunea verde |

**A patra formă greșește în direcția OPUSĂ** (METODA §22) și e cea mai rea: un zero pe mulțime goală
arată identic cu un zero real, deci orbirea se citea ca *conformitate*.

**Ancora moartă e o a patra stare, nu o neconformitate.** `fix_serie_contare_v1` a fost scos de
commitul `55a57f6` — o rescriere legitimă a contării. Verificarea și-a pierdut **obiectul**; codul
nu și-a pierdut conformitatea. Se raportează `NEVERIF [ancora-moarta]`, nu FAIL pe vecie. *Verificarea
comportamentală de deasupra ei — datele fără `MD-MD` — trece, deci ce voia să apere e apărat.*

**Ce face imposibil:** oricare dintre cele șase forme să se întoarcă. Fiecare `NEVERIF` poartă un
**cod stabil** (`sudo-indisponibil`, `proc-necitibil`, `ancora-moarta`, `fisier-ilizibil`,
`interogare-neexecutata`, `glob-gol`, `proces-negasit`), iar gardul asertează pe **codul parsat**, nu
pe proza mesajului — mesajul se poate rescrie fără să cadă nimic (METODA §23).

**Codul de ieșire nu mai contrazice rezumatul:** `1` la orice FAIL · **`2`** dacă zero FAIL dar există
NEVERIF · `0` doar când s-a verificat tot și tot e conform. *O rulare oarbă nu are voie să arate
verde pentru cine citește doar codul.* Gardat prin confruntarea cifrelor din rezumat cu codul întors.

**RED-PROOF: 8 mutații, 8 roșii** — fiecare apărare scoasă separat, pe o copie în `/tmp`, cu testul
ei cerut roșu. **Prima rulare a dat 5 din 7**, și de-aia sunt opt: două apărări erau acoperite de
ramuri vecine care ajungeau la același verdict din alt motiv. *Un verdict fără codul lui nu deosebește
două ramuri — de aici au ieșit codurile, și un test propriu pentru ramura portantă a citirii lui
`/proc`.* **Proba prin mutație a găsit un gol în GARD, nu în cod** — exact ce cere interdicția 76.

**ȘI A GĂSIT UN BUG AL MEU, în chiar garda asta:** prima formă folosea
`grep -rq -- "$m" "$RAD" --include='*.py'`. `--` oprește parsarea opțiunilor, deci `--include` devenea
**nume de fișier**, căutarea intra în `.git` și potrivea în packfile-uri — iar scriptul raporta
*„ancora s-a mutat"* despre un marker care nu mai există nicăieri. Prins **măsurând**, nu recitind.
Are test de regresie propriu, pe o rădăcină sintetică cu marker îngropat în `.git`.

**Ce NU face, declarat:** nu execută verificările reale (ar cere baza, procesul viu și sudo) — se
sursează funcțiile și se exercită **clasificarea**, partea care mințea · nu judecă dacă NC-urile în
sine sunt bine alese (judecată din 09.07) · nu apără codul de ieșire împotriva unui apelant care-l
ignoră, fiindcă azi **nu-l consumă nimic programatic** (măsurat: zero apelanți în `.py`/`.sh`).

**Seam-ul de probă (`VERIF_NC_SCRIPT`) are gardul lui:** dacă e setat în poartă, testul cade. Altfel
ar fi o cale prin care gardul păzește o copie, iar scriptul livrat rămâne neatins.

**ANCORA NC-02, RETRASĂ 31.08** (Costin, `DECIZII.md` 17.1), cu motivul scris **în script**, lângă
locul de unde s-a scos. Gardat în amândouă direcțiile: NC-02 trebuie să producă **exact un** rând —
dacă dispare și cel comportamental, retragerea rămâne fără temei; dacă apare un al doilea, ancora
pe marker s-a întors pe furiș. *Regula generală: o verificare ancorată pe PREZENȚA unei reparații
moare la prima rescriere legitimă; una ancorată pe EFECT nu.* Gardul are acum **20 de teste**.

**Rulare de după reparație:** `PASS: 18   FAIL: 0   NEVERIF: 2`, `EXIT=2`, cu avertismentul
*„rularea NU e completă"* scris în rezumat. *Cele trei NEVERIF nu sunt neconformități; sunt absența
unei probe — și nu se sting lărgind drepturile.*

## 31.08.2026 — Faza 2, prima operațiune: documentul pe care îl citează un temei conține articolul pe care îl numește?

**`core/articol_in_act.py` (NOU, extras) + `core/scan_pereche_act_articol.py` (NOU) +
`core/test_pereche_act_articol.py` — NOU, 12 teste.** Prima operațiune a fazei 2, pornită după ce
listele 3/4/5 s-au închis (`DECIZII.md` 12: *„faza 2 după ele"*).

**Cum a ieșit la iveală.** Măsuram interdicția **55** — categoria de reverificare, al cărei proiect
era deja decis pe 23.08 — și am vrut să verific premisa scrisă acolo: *„unealta le vede deja pe
fiecare"*. Regula planului cere exact asta (23.08: *fiecare „se măsoară trivial" se verifică înainte
de a fi transcris*). Unealta chiar le vede. **Ce nu se verificase e dacă DATELE îi dau documentul
potrivit.**

| | |
|---|---|
| temeiuri unice în registrul de cote | **34** |
| verificabile (au și `art`, și `url`) | **26** |
| **confirmate** — documentul citat conține articolul | **15** |
| **NEGĂSIT** — actul citat nu conține articolul | **6** → **R106** |
| **CIOT** — documentul citat are sub două titluri de articol | **5** |
| fără `art`, deci neverificabile | **8** |

**Cele șase au aceeași formă, confirmată la sursă:** articolul e al **Codului fiscal**, actul citat
e cel care l-a **modificat**. OG 16/2022 spune *„articolul 97 alineatul (7) … se modifică"*; OUG
8/2026 spune *„articolul 282, alineatul (3) se modifică"*. **`COTE.impozit_dividend` are patru
temeiuri și niciunul nu se confruntă.**

### CE A SCOS EXTRAGEREA, și e un defect VIU al uneltei

Logica de localizare trăia la nivel de script, sub `sys.argv` — **neimportabilă**. Am re-scris-o de
două ori într-o oră ca să pot măsura, și **amândouă copiile au dat cifre greșite**: prima a raportat
*0 caractere* pentru OUG 89/2025 art. III, unde unealta găsește **3700**; a doua *„fără fișier în
corpus"* despre Codul fiscal, care e acolo, sub `cod_fiscal_227_2015_consolidat`. *O logică
neimportabilă nu rămâne una singură — se multiplică prost.* Mutată în `core/articol_in_act.py`;
scriptul o importă, iar un test pe **AST** cere ca importul să existe.

**A cincea reparație, găsită DE extragere.** Scriptul aplica, peste tăierea la următorul titlu, o a
doua tăiere cu un tipar **lax** — fără excluderea `din`. Aceea potrivea forma de **citare**
dinăuntrul unui marcaj: *„… Articolul I ORDONANȚA DE URGENȚĂ nr. 79 **din** 8 noiembrie 2017 …"*.

| pereche | înainte | după |
|---|---|---|
| `CF art. 78` | 532 caractere · **1 an** (2021) | 16.719 caractere · **6 ani** (2018, 2020, 2021, 2023, 2024, 2026) |
| `CF art. 51` | 120 caractere · 1 an | 3.016 caractere · 4 ani |
| `CF art. 156` | 319 caractere | 2.693 caractere |
| `CF art. 138` | 799 caractere | 1.020 caractere |
| `Legea 201/2025 art. I` | 234 caractere | 289 caractere |

**5 din 26** de perechi își schimbă răspunsul. *Direcția greșelii e cea liniștitoare, și de-aia
contează: articolul părea mai **stabil** decât e — `CF art. 78` cu ultima modificare în 2021 în loc
de 2026 — deci ar fi primit pragul de reverificare cel mai **lung** exact acolo unde trebuie cel mai
scurt.* Probat că nu s-a înlocuit sub-raportarea cu supra-raportare: pe cele trei articole schimbate,
fragmentul nou nu conține **niciun** titlu de alt articol.

**Ce face imposibil:** o pereche neconfirmată nouă (clichet **6 NEGĂSIT / 5 CIOT**, plus identitatea
celor șase scrisă ca date — clichetul pe număr n-ar vedea una reparată și alta stricată în aceeași
tură) · dispariția tăcută a unei perechi confirmate (prag de JOS: **15**) · întoarcerea tăierii la
citare · o a doua implementare a localizării.

**Calibrare, ambele direcții:** cazul cunoscut **găsit** (CF art. 78/51/156/138 localizate corect,
deci „negăsit" nu vine din neputință) · negativ pe act sintetic, cu **cele trei feluri de «nu pot
spune» deosebite** — articol absent → `NEGASIT`, act cu un singur titlu → `CIOT`, fișier lipsă →
`FISIER_LIPSA`. Un singur „nu" le-ar topi într-unul.

**RED-PROOF: 3 mutații, 3 roșii.** Prima rulare a dat **2 din 3**: proba care cerea ca fragmentul să
nu înghită articolul următor căuta **titluri** în fragment, iar fragmentul e normalizat pe spații —
tiparul de titlu e ancorat pe linie, deci n-avea ce vedea. Rescrisă pe **efect**: articolul următor
din fixtură poartă un marcaj din **2030**, an care nu apare altundeva; dacă apare în anii articolului
verificat, s-a împrumutat. *Un gard care se uită la forma greșită nu e un gard.*

**Ce NU face, declarat:** nu spune că articolul găsit e **cel potrivit** — dacă actul citat conține
din întâmplare un articol cu același număr despre altceva, perechea trece; deci „confirmate" e
**plafon SUPERIOR** · nu deosebește vina: un `CIOT` e o problemă de **corpus**, nu de temei · **nu
repară** cele șase, fiindcă fiecare cere o verificare la sursă a actului care poartă azi valoarea.

## 31.08.2026 — R106 se RETRAGE: registrul scrisese defectul instrumentului meu cu opt zile înainte să-l construiesc

**Nu datele erau greșite. Instrumentul era.** Secțiunea de mai sus, din aceeași zi, declară șase
perechi (act, articol) ca defect de date și deschide **R106**. Erau **convenția de modelare
declarată la interdicția 50**, pe 23.08.2026 — care scrisese și convenția, și modul de eșec:

> *„`Temei` reține **actul care a schimbat regula** și **numărul articolului din actul schimbat** —
> `Legea 141/2025 art. 97` înseamnă «CF art. 97, așa cum l-a modificat Legea 141/2025». … **un
> instrument care le-ar lua literal ar căuta art. 97 în Legea 141/2025 și n-ar găsi nimic**."*

Am construit exact acel instrument și am raportat exact acel rezultat, ca descoperire. **Regula de
aur — caută pe tot înainte de a spune „absent" — am aplicat-o corpusului, nu propriului registru.**

### Ce a oprit reparația greșită: două gărzi care existau deja

Reparația pe date fusese scrisă, probată și verde pe instrumentul meu. Poarta a respins-o:

| garda | ce a spus |
|---|---|
| `test_forma_consolidata_nu_e_sursa_pentru_valoare_cu_succesor` | o formă consolidată **la zi** nu poate justifica o valoare care are **succesor** — `plafon_tva_incasare@2026-03-01` are unul la 2027 |
| `test_fiecare_articol_din_registru_e_masurat_la_sursa` | `('OG 16/2022','I')` și `('OUG 50/2015','I')` nu erau **măsurate la sursă** |

*Amândouă pe drept. Gărzile au apărat registrul de reparația mea* — și abia citind a doua, unde stă
`_ART_DE_COD_FISCAL`, am găsit convenția. **Poarta n-a prins o regresie de comportament; a prins o
încadrare greșită.**

### Reparația reală: instrumentul învață convenția

`core/scan_pereche_act_articol.document_tinta` rezolvă acum perechea **înainte** de a căuta: un
articol de Cod fiscal se caută în Codul fiscal, oricine l-ar cita alături. `url`-ul temeiului rămâne
ce a fost — actul care a schimbat regula, adică proba pentru **valoare**. *Două întrebări diferite au
voie să aibă răspunsuri în documente diferite.*

| | luat literal | după convenție |
|---|---|---|
| GĂSIT | 15 | **24** |
| NEGĂSIT | 6 | **0** |
| CIOT | 5 | **2** |

**Zero temeiuri schimbate.** Clichete: `CLICHET_NEGASIT = 0` · `CLICHET_CIOT = 2` ·
`PRAG_CONFIRMATE = 24`.

**O SINGURĂ IMPLEMENTARE A CONVENȚIEI.** Mulțimea articolelor de Cod fiscal trăia în
`core/test_vigoare_articole_registru.py` și — implicit — în capul celui care scria următorul
instrument. Al doilea n-a știut de ea. Acum e în `scan_pereche_act_articol.ART_DE_COD_FISCAL`, iar
garda veche o **importă**. *O convenție ținută în două locuri se desparte în tăcere; a doua copie a
fost capul meu.*

**Gardă nouă de regresie**, cu mutație: dacă `document_tinta` uită convenția, **4 teste cad** —
probat, apoi restaurat, 14 verzi. Plus direcția inversă: `OUG 89/2025 art. III` și
`OUG 156/2024 art. LXVI` sunt articole **proprii** și **nu** au voie să fie trimise la Codul fiscal;
fără proba aia, convenția ar putea înghiți tot și ar părea că merge.

**Ce rămâne adevărat din tura precedentă**, independent de încadrare: cele **2** perechi rămase
(`OUG 156/2024 art. LXVI`, document-ciot) sunt reale → **R107**. Iar defectul din `articol_in_act` —
tăierea la citare, care ascundea volatilitate — e real și reparat.

**REGULA CARE IESE:** *un instrument nou se confruntă cu câmpul „ce nu vede" al interdicțiilor pe
care le atinge, înainte de a raporta o descoperire.* Registrul scrie modurile de eșec **tocmai** ca
să nu fie redescoperite ca defecte.

## 31.08.2026 — Categoria de reverificare există și e CALCULATĂ. Iar axa „unde ajunge valoarea" a scos un prag fiscal cu trei copii

**`core/reverificare.py` (NOU) + `core/test_reverificare.py` — NOU, 11 teste.** Interdicția **55**
măsura, pe 23.08: *„53 din 53 fără categorie de reverificare — fiindcă **câmpul nu există**."* Exista
un prag global unic, 6 luni pentru tot: o cotă de TVA care se schimbă la fiecare rectificare și o
definiție neatinsă din 2015 se reconfirmau la fel de des.

**Cele două axe sunt mecanice** — asta face categoriile calculabile, nu atribuibile. A: frecvența
articolului, din marcajele lui de consolidare, citite în documentul pe care îl indică **convenția**
de la interdicția 50 — nu în actul citat literal. B: consecința, din unde ajunge valoarea.

| clasă | câte | prag |
|---|---|---|
| VOLATIL / DEPUS | **9** | 1 lună |
| STABIL / DEPUS | **12** | 6 luni |
| MISCATOR / CALCULAT | **2** | 6 luni |
| MISCATOR / NECUNOSCUT | **1** | — |
| NECUNOSCUT / NECUNOSCUT | **10** | — |

Față de pragul global: **9 mai strict · 0 mai larg · 14 la fel · 11 fără prag.** *Cele 9 sunt exact
valorile care s-au mișcat recent: cotele de TVA, dividendele, micro, impozitul pe venit. Toate intră
în declarații.*

**`NECUNOSCUT` NU E O CLASĂ DE REZERVĂ, E UN RĂSPUNS** *(Costin, 31.08: „orice implicit minte —
STABIL tăcut, VOLATIL zgomotos")*. O pereche fără axă nu primește prag, iar fiecare NECUNOSCUT își
scrie motivul. Amândouă gardate — plus direcția inversă: o pereche complet clasificată **trebuie** să
aibă prag, ca `NECUNOSCUT` să nu devină o scuză confortabilă.

**`INFORMATIV` e declarat VID, cu motivul:** `dependenti_act` vede funcții Python, nu ecrane. Gardul
cere clasa vidă — *ziua în care apare o cale de a o atribui, testul cade, și e corect să cadă.*

**O gaură a tabelului, astupată declarat:** trei modificări în același an nu intră în niciunul dintre
cele trei rânduri, cum sunt scrise. Se clasează **VOLATIL** — direcția care verifică mai des. Are test
propriu, ca alegerea să fie o decizie scrisă, nu un efect al ordinii de `if`-uri.

**Gardul cere și MONOTONIA tabelului**, pe structură: mai volatil trebuie să însemne mai des, mai grav
la fel. O rescriere care păstrează cifrele dar le încurcă ordinea trece un test de egalitate și pică
aici.

### CE A SCOS AXA B, și e o descoperire, nu o construcție

`plafon_mijloc_fix` a ieșit **NECUNOSCUT** pe consecință: *nimic din cod nu atinge valoarea*.
Verificat la sursă cu `grep` — apare doar în propria definiție și în eticheta raportului lunar.
**Consumatorii existau; își duplicaseră cifra.**

| unde | valoare | dată | folosit |
|---|---|---|---|
| `COTE["plafon_mijloc_fix"]` — canonic | 5.000 / 2.500 | era **01.01.2026**, greșit | **nu** |
| `obiecte_inventar.py` | 5.000 / 2.500 | **25.02.2026**, corect | da |
| `mijloace_fixe_import_api.py` | 5.000 | **fără dată** | da |

**Data din registru s-a corectat** — fapt verificat verbatim în forma consolidată: *„(la
**25-02-2026**, Litera b), Alineatul (2), Articolul 28 … a fost modificată de Punctul 7., Articolul 6
din ORDONANȚA DE URGENȚĂ …)"*. Unificarea celor trei pe `cota()` **nu** s-a făcut: **R108**.

**Cade între două instrumente**, și asta e partea de reținut: graful nu-l vede fiindcă nimic nu-l
consumă, iar `scan_constante` **nu-l numără** — `mijloace_fixe_import_api.py` are **zero** intrări în
inventarul constantelor nesursate. *O gaură de acoperire, nu doar o instanță.*

**Ce NU s-a legat, deliberat:** pragul calculat nu alimentează încă raportul lunar — ar schimba ce
raportează un job viu și cere `cote_neconfirmate` să primească prag per-articol. **R109**, cu efectul
deja măsurat.

## 31.08.2026 — A cincea direcție oarbă a domeniului: regula întreba doar despre valorile implicite ale parametrilor

**Întrebarea lui Costin:** *„Investighează de ce `scan_constante` nu vede constantele de modul din
`mijloace_fixe_import_api.py`. Dacă e gaură, clichetul de 93 e un plafon inferior necunoscut, iar
R108 a fost găsit din întâmplare, nu de instrument."*

**E gaură, și avea dreptate pe partea a doua.** `in_domeniu` are patru reguli; a patra —
`_poarta_valoare_de_registru`, adăugată 23.08 — întreabă *„fișierul poartă o valoare din registru?"*,
dar se uită **numai la valorile implicite ale parametrilor** (`a.defaults`, `a.kw_defaults`). Așa
fusese găsită clasa atunci: *„cota = 21 ca default"*. **O constantă de MODUL cu aceeași valoare îi
scapă** — și exact așa a scăpat `PLAFON_MF_2026 = 5000.0`, plafonul de mijloc fix, **chiar valoarea
curentă din registru**. Fișierul avea **zero** intrări în inventar. *R108 a fost găsit prin axa B a
interdicției 55, nu de instrumentul care ar fi trebuit să-l vadă.*

**Mărimea punctului orb, măsurată: 248 din 412 de fișiere `.py` sunt în afara domeniului.**

**DAR partea întâi a întrebării are alt răspuns decât părea, și e important:** lărgirea domeniului
adaugă **ZERO clasa C**. Cele patru valori fiscale nou-văzute sunt **clasa E** — sursate în proză,
nu nesursate: `bacsis.COTA_IMPOZIT`, `PLAFON_MF_2026`, `obiecte_inventar.PRAG_NOU/PRAG_VECHI`.
*Clichetul nu era subestimat; punctul orb ascundea valori care își citau temeiul pentru om, dar nu
pentru mașină.* C rămâne **133**; E urcă **46 → 50**, D **56 → 58**.

### DE CE DOUĂ SEMNALE, și nu doar valoarea — calibrat pe populația reală, înainte de a scrie regula

Prima formă a extinderii cerea doar *valoare din registru*, la orice constantă de modul. Aducea
`nucleu.py`: `_SCRYPT_N = 16`, `_SALT_BYTES = 16`, `PAROLA_MIN = 8` — parametri de **criptografie**
care se potrivesc din întâmplare cu cota de profit (16) și cu cea de dividende istorică (8).
**Șase constante ar fi intrat în clichet ca datorie fiscală permanentă, nereparabilă fiindcă nu e
fiscală.** Un clichet otrăvit e mai rău decât unul incomplet: primul nu se mai poate coborî niciodată.

Regula finală cere **nume fiscal ȘI valoare din registru**. Măsurat: 3 fișiere aduse, **0
fals-pozitive**, 0 clasa C.

| formă încercată | aduce | ținta 5 | fals-pozitive |
|---|---|---|---|
| doar valoare de registru | 4 fișiere | 4/5 | **6 constante** (`nucleu.py`) |
| doar nume fiscal | 6 fișiere | 5/5 | 2 (instrumente) |
| **nume ȘI valoare** | **3 fișiere** | **4/5** | **0** |

**CE NU PRINDE, scris ca afirmație:** o valoare fiscală care **nu e în registru**. Instanța rămasă:
`intrastat.PRAG_2026 = 1000000` — pragul Intrastat nu e în `COTE`, deci nicio regulă ancorată pe
registru nu-l poate vedea. *E altă clasă — o valoare fără temei, interdicția 57 — nu o scăpare a
acesteia.* Are test propriu: dacă într-o zi intră în registru, testul cade și cere actualizarea.

**Calibrare, ambele direcții:** cele trei fișiere trebuie să fie **în** domeniu · `nucleu.py`
trebuie să rămână **afară** · sintetic, o valoare fără nume fiscal nu aduce fișierul, iar un nume
fiscal cu o valoare care nu e în registru nu-l aduce nici el — *altfel regula ar deveni o euristică
pe nume.*

## 01.09.2026 — Trei copii ale unui prag fiscal, unificate pe registru. Iar graful a confirmat singur reparația

**Costin:** *„Unifică cele trei copii ale pragului de mijloc fix, cu registrul ca sursă. O lege
aplicată în trei locuri produce cifra validă și falsă; canonicul necitit e configurația cea mai
proastă."*

**`core/test_prag_mijloc_fix_unic.py` — NOU, 6 teste.** `obiecte_inventar.prag_mf(la_data)` e acum
**singura poartă** și citește `COTE["plafon_mijloc_fix"]`; `PRAG_NOU`, `PRAG_VECHI`, `DATA_PRAG_NOU`
și `PLAFON_MF_2026` **nu mai există**. Importul cere pragul **la data PIF a rândului**.

**Ce era greșit și acum nu mai e:** avertismentul de la import spunea *„sub plafon 5000 (2026)"*
pentru orice bun, inclusiv pentru cele intrate înainte de **25.02.2026**, când plafonul era 2.500.

**PROBA MECANICĂ A UNIFICĂRII, și e frumoasă fiindcă n-am scris-o eu:**
`dependenti_act.dependenti(OUG 8/2026, art. 28)` întorcea **zero** funcții. Acum întoarce **patru**.
Iar `core/reverificare.py` — construit ieri, pentru altceva — a mutat singur valoarea din
`MISCATOR/NECUNOSCUT` (fără prag) în `MISCATOR/CALCULAT` (prag 6 luni). *Nu s-a schimbat nici
articolul, nici legea: s-a schimbat faptul că valoarea canonică e citită de cineva.* Pinul
distribuției a căzut și a cerut actualizare — exact ce trebuia să facă.

**NECUNOSCUTUL A DEVENIT EXPRIMABIL, nu a dispărut.** Registrul n-are prag înainte de 01.01.2015; un
mijloc fix intrat în 2008 avea 1.800 lei (HG 105/2007), care nu e acolo. `prag_mf` întoarce mai
departe cea mai veche valoare cunoscută — **comportament neschimbat, deliberat** —, dar
`prag_mf_cunoscut()` spune dacă răspunsul e verificat la sursă sau moștenit, iar importul își scrie
avertismentul altfel în cele două cazuri. *Fără asta, unificarea ar fi mutat o minciună dintr-un loc
în altul.*

**Gardul asertează pe AST**, nu pe text: `5000`, `5000.0` și `Decimal("5000")` sunt aceeași valoare,
iar un test pe șiruri ar vedea trei lucruri diferite.

### DOUĂ GĂRZI VECHI AU REACȚIONAT LA REPARAȚIE, amândouă corect

1. **`test_domeniul_vede_CONSTANTA_DE_MODUL...`**, scrisă ieri, a picat: `mijloace_fixe_import_api.py`
   a **ieșit** din domeniul scanului de constante — fiindcă nu mai are constanta. *O calibrare care
   își pierde obiectul fiindcă defectul s-a reparat nu se șterge și nu se slăbește: se mută pe ce a
   rămas viu (`bacsis.COTA_IMPOZIT`), iar restul trece pe caz sintetic — METODA §29, a cincea
   instanță.*
2. **Clichetul 50, în forma lui cea mai simplă.** Prima formă a direcției inverse era
   `"PLAFON_MF_2026" not in sursa` — și a picat imediat, fiindcă numele apare în chiar comentariile
   care explică ștergerea lui. *Un `in` pe text păzește textul, nu proprietatea.* Mutată pe AST.

## 01.09.2026 — Pragul Intrastat intră în registru. Excepția cunoscută de un singur raport nu mai există

**Costin:** *„`intrastat.PRAG_2026` intră în registru. Cât timp e afară, «clichetul nu crește» are o
excepție pe care o cunoaște un singur raport — excepția nedeclarată e clasa închisă azi de patru
ori."*

**Ce s-a făcut, în ordinea în care contează:**

1. **S-a căutat actul la sursă**, nu s-a presupus. `portal_legislativ.py cauta ORDIN 1604 2025` →
   `id=303985, ORDIN 1604 27/10/2025`. Adus și **amprentat**.
2. **S-a citit ce s-a adus** — și pagina e un **ciot de 5.416 caractere**, care **nu conține
   pragul**. Deci actul **există** (verificat), dar valoarea **nu e confruntată** (nu se poate).
   Ambele se scriu; **R110**.
3. **Valoarea a intrat în registru** cu exact atât cât s-a verificat: `url` către actul adus,
   `lant_acte` care spune că e ciot. `scan_citate` îl va raporta `verbatim=False`, **pe drept** —
   incompletitudinea devine **măsurabilă** în loc să fie prozaică.
4. **Modulul citește din registru.** `intrastat.prag_intrastat(la_data)`; `PRAG_2026` nu mai există.
   **`PRAG_ATENTIE = 0.80` RĂMÂNE** — 80% nu e o valoare din lege, e pragul **nostru** de avertizare
   timpurie, iar o valoare de produs n-are ce căuta în registrul de cote.

**CLICHETUL A CRESCUT, 133 → 134, DECLARAT.** `intrastat.py` a intrat în domeniu, iar ce a devenit
vizibil e chiar `PRAG_ATENTIE`. *O creștere produsă de lărgirea domeniului nu e o regresie, dar nici
nu se strecoară: se scrie cu ce anume a crescut, și de ce coborârea ei nu e o reparație fiscală — nu
e nimic de reparat —, ci ar cere o clasă pentru valorile operaționale din `core/`, care azi nu
există.*

**A doua constantă nou-văzută NU a intrat în clichet, și de-aia merită scrisă:** `Decimal("0.1")` de
pe un `.quantize()`. Lista de precizie a scanului (clasa D) era **enumerată, nu derivată** —
`("0.01", "0.001", "0.005", "0.5")` — deși criteriul din chiar condiția ei e prezența lui
`quantize`. Completată cu `0.1`, după ce s-a măsurat că e **o singură instanță în tot repo-ul**, deci
fără efecte laterale. *O enumerare care nu-și derivă membrii îmbătrânește la prima valoare nouă.*

**TESTUL SCRIS CA SĂ CADĂ A CĂZUT.** Pe 31.08 scrisesem, ca limită declarată a regulii de domeniu, un
test care cerea ca `intrastat.py` să fie **în afara** domeniului, cu mesajul: *„dacă pragul Intrastat
a fost adăugat în registru, e o veste bună: scoate testul ăsta."* A picat azi, exact așa. Rescris:
păzește acum **limita** (o valoare fiscală scrisă direct în cod e invizibilă), și afirmă că **nu mai
există instanță cunoscută** — o afirmație, nu o presupunere.

## 01.09.2026 — R109: pragul calculat alimentează raportul lunar. Podeaua rămâne, necunoscutul rămâne în pază

**Costin:** *„R109 — leagă pragul calculat de raportul lunar, ca tură proprie, nu la coada alteia.
Schimbă un contract, nu o linie. Ce trebuie să rămână adevărat: nicio cotă nu se reconfirmă mai rar
decât azi. Riscul e volum de alerte — măsoară-l înainte și după."*

**`core/test_prag_per_articol.py` — NOU, 6 teste.**

**VOLUMUL, măsurat pe orizont de 12 luni** — fiindcă un job lunar nu se judecă într-o singură zi:

| la data | global | per articol | în plus |
|---|---|---|---|
| 2026-09-01 | 0 | **0** | — |
| 2026-10-01 … 2027-02-01 | 0 | **3** | dividende, micro, impozit pe venit |
| de la 2027-03-01 | 20 | 20 | — |

Cele trei sunt exact clasa **VOLATIL/DEPUS**: cotele care s-au mișcat de două ori în trei ani și
intră în declarații. *Costul operațional, scris ca să nu surprindă: cu prag de o lună și un cron
lunar, ele vor apărea în raport în fiecare lună în care nu sunt reconfirmate. Asta e proiectul, nu
un efect secundar.*

### Cele două capcane pe care le-a scos măsurătoarea

1. **`NECUNOSCUT` ar fi însemnat „fără pază".** Patru cote n-au prag calculabil; azi sunt
   monitorizate la 6 luni. Dacă „fără prag" ar fi însemnat „nu se raportează", s-ar fi reconfirmat
   **niciodată** — adică încălcarea regulii lui Costin **pe ușa din dos**, printr-o clasă care sună
   prudent. Rămân pe podea, iar rândul spune `global (prag necunoscut)`.
2. **Un prag mai larg ar fi slăbit paza în tăcere.** Azi tabelul nu produce așa ceva (`INFORMATIV` e
   clasă vidă), dar contractul îl acceptă. Se ignoră, cu motivul scris pe rând, și e probat **pe caz
   sintetic** — o apărare pentru care nu există instanță azi se probează sintetic, nu se presupune.

### Contractul nu se rupe pentru nimeni

`cote_neconfirmate(luni, la_data, prag_pentru=None)` — fără al treilea argument face **exact** ce
făcea. Gardat, ca niciun alt apelant să nu primească tăcut alt răspuns. Importul lui `reverificare`
în `expirare_cote` e **local**, nu de modul: instrumentul citește corpusul și graful, iar un job
lunar n-are voie să încarce asta la fiecare pornire a aplicației. Iar dacă el crapă, raportul **nu se
oprește** — cade pe podea, și se vede în `prag_sursa`.

**O CORECȚIE A MĂSURĂTORII MELE, a cincea de același fel:** prima formă prezisese **3 alerte azi**;
realitatea e **0**. Aproximasem cu aritmetică pe luni, iar codul compară **date**. *Re-implementasem
regula în loc s-o chem — exact tiparul care a produs R106.* Măsurătoarea corectă cheamă
`cote_neconfirmate`.

**Un test vechi a picat, corect:** cerea ca subiectul alertei să conțină pragul. Nu mai există **un**
prag — subiectul ar fi purtat o cifră care nu descrie nimic. Proba s-a mutat **pe rând**, unde pragul
chiar diferă, și cere să se vadă și **sursa** lui.

## 01.09.2026 — R110: actul adus de la emitent, și ce a ieșit la iveală aducându-l

**Ce s-a schimbat.** `plafon_intrastat` avea temei cu act existent dar **neconfruntabil** — pagina
servită de portal e un ciot de 5.416 caractere fără prag. Criteriul corectat de Costin — *sursa
emitentului, la adresă stabilă, amprentabilă; „doar portalul" nu decurgea din „neamprentat e mai rău
decât lipsa"* — a deschis calea către portalul propriu al INS, unde ordinul stă ca **scan al paginii
din MO Partea I nr. 1022/5.XI.2025**. Adus, amprentat pe fișier și pe text, confruntat pe **cinci
probe de conținut cerute înainte de scriere**. `scan_citate`: **verbatim 10 → 11**; clichetul urcat.

**Ce a ieșit la iveală, și e mai mare decât R110.** Ca să numesc articolul (`art="1"`, adevărat —
pragul e la art. 1), am măsurat întâi ce ar face axa frecvenței cu el. Răspunsul a fost `NECUNOSCUT`,
deci sigur — dar măsurătoarea de control, pe toate cele 26 de temeiuri cu articol, a arătat altceva:
**cele 4 temeiuri ale cotelor de TVA primesc STABIL dintr-un act modificator care nu poate purta
istoric de consolidare**, în timp ce același articol în Codul fiscal arată 8 marcaje = VOLATIL.
Direcția e cea largă. **Zero alerte pierdute** — podeaua ține —, dar câștigul lui R109 e anulat exact
acolo unde consecința e cea mai mare. **R111**, cu cele două cauze mecanice numite.

**Ce n-am reparat, cu motivul.** Garda de identitate a actelor a cerut clichetul 121 → 123: fișierele
poartă **așezarea Monitorului Oficial** (titlu fără număr în antet, numărul la picior), pe care
tiparul ei n-o citește. N-am scris un tipar pentru forma MO fiindcă am măsurat clasa: în tot corpusul
există **un singur** fișier cu antet de Monitor Oficial — al meu. *Un tipar calibrat pe unicul
exemplar care l-a cerut nu dovedește nimic despre acoperire.* Clichetul a urcat cu **cele două
fișiere numite în comentariu** — un clichet urcat fără nume e chiar excepția cunoscută de un singur
raport.

## 01.09.2026 (2) — R111: un instrument care nu întreabă dacă sursa lui poate răspunde

**Ce era stricat.** Axa frecvenței clasa `STABIL` orice articol fără marcaje de consolidare. Dar
„zero marcaje" înseamnă două lucruri: *nemodificat*, sau *documentul nu consemnează modificări*. A
doua se citea ca prima, și producea `STABIL` — adică **verificat mai rar** — dintr-o sursă care nu
putea răspunde. Instanța: cele patru cote de **TVA**, care luau `STABIL` din actul modificator, când
același articol în Codul fiscal are **8 marcaje**.

**Reparația nu e un tabel de excepții.** `inregistreaza_modificari(document)` întreabă o proprietate
**măsurată** a sursei: consemnează documentul vreo modificare, oriunde? Cod fiscal **1.400** ·
OUG 89/2025 **18** · Legea 201/2025 **0**. De aceea `OUG 89/2025 art. III` rămâne `STABIL` — decizia
din antetul lui `reverificare` se păstrează, iar criteriul nu înghite citirile reale. *Un gard care
ar fi făcut totul NECUNOSCUT ar fi trecut primul test și ar fi distrus clasificarea.*

**A doua cauză era o convenție despărțită în tăcere.** `291` era singurul articol rezolvat la Codul
fiscal **condiționat** de numărul actului care îl citează. Mulțimea fusese mutată într-un singur loc
pe 31.08 tocmai ca asta să nu se întâmple — dar **regula** rămăsese copiată, iar despărțirea s-a
produs pe jumătatea nemutată. Acum `_cheie` cheamă funcția, nu îi copiază corpul.

**Volum**, măsurat înainte și după pe 13 puncte: **3 → 7** la o lună, **zero pierdute**. Cele patru
în plus nu sunt volum nou — erau `VOLATIL` și înainte, mascate.

**O capcană găsită căzând în ea:** `marcaje()` avea o precondiție nescrisă (spațiile trebuie
colapsate). Pe Codul fiscal întorcea **1** marcaj din **2.020**. Am folosit-o greșit chiar eu, la
prima măsurătoare a clasei. Își normalizează acum singură intrarea.

**Cauza 2 s-a despărțit în R113**, cu cifra ei: **8** acte de corpus sunt CIOT doar fiindcă poartă
așezarea Monitorului Oficial, și **2** ar câștiga titluri false dintr-un tipar prea larg.

## 01.09.2026 (3) — Interdicția 3, măsurată: cine alege data unui calcul fiscal

**Pasul a fost ales din `scan_ramas.py`, pe criteriu, nu din vecinătate** — a doua oară când Costin
mă corectează pe asta. Criteriul: *ce poate produce o cifră validă și falsă.* Interdicția 3 e cea
mai literală potrivire din cele 114 rânduri, și era **NEÎNCEPUTĂ**: fără instrument, deci fără cifră.

**Două populații, fiindcă sunt două lucruri diferite.** **26** de funcții cad pe `date.today()` când
apelantul nu dă data — generatoare latente. **4** apeluri de producție chiar omit data, din care
**2** declarate cu motiv și **2** defecte. Contra-cifra dă scara: **88** de apeluri de producție dau
data. *Clasa e mică; ce lipsea era instrumentul.*

**Am măsurat-o greșit de trei ori înainte s-o măsor bine**, toate în aceeași direcție — numărând
forma, nu efectul. „1 apel" (numai pe nume, nu pe atribut) · „68 de apeluri" (poziționalele socotite
drept omisiuni) · o funcție de email clasată ca fiscală. Fiecare are acum probă proprie. Iar prima
formă a probei pentru atribut **era prea slabă** — trecea și cu sonda oarbă, fiindcă nu izola
proprietatea; mutația a arătat-o, și a fost ascuțită.

**Reparat aici:** `contracte_speciale.nota` primește data notei. Ruta o avea deja în cerere și o
folosea pentru „luna deschisă", dar n-o trimitea mai departe. **Rămâne R114:** ecranul Intrastat
compară fluxurile anului cerut cu pragul de azi — reparația schimbă ce se afișează, fiindcă pentru
2025 pragul nu se poate ști (R112), deci cere poartă vizuală.

## 01.09.2026 (4) — Două măsurători cerute: suprapunerea listelor, și ce e supervizorul azi

### 1. Listele nu se suprapun — sunt lumi diferite

*Comanda cerea suprapunerea. Măsurătoarea a dat inversul, și asta e rezultatul.*

**Trei dintre cele cinci „liste" sunt una singură.** Restanțele deschise (**39**) și interdicțiile
neîncepute (**33**) sunt **100% conținute** în cele 114 rânduri ale lui `scan_ramas.py`. Nu sunt
surse independente, sunt vederi. Rămân trei liste chiar distincte: **A** backlog (114 intrări, **224**
obiecte) · **D** `PLAN_INVESTIGATII` (29 secțiuni, **9** obiecte — e un plan de faze, nu de obiecte) ·
**E** checklistul de browser (**495** secțiuni, **252** obiecte).

**Potrivire pe obiect** — ce fișier, ce declarație, ce articol, ce rută, ce ecran. Din **453** de
obiecte distincte, **213** apar în cel puțin două liste:

    A ∩ D =  8   ( 4% din A · 89% din D)
    A ∩ E = 24   (11% din A · 10% din E)
    D ∩ E =  1
    în toate trei: 1   (D112)

  - **90% din ce atinge checklistul de browser nu apare nicăieri în backlog** (228 din 252).
  - **89% din ce atinge backlogul n-are nicio verificare de browser** (200 din 224).

*Cifrele de mai sus sunt A DOUA formă. Prima — «374 / 209 / 5% / 95%» — era greșită din două cauze,
amândouă tăcute: cheile dicționarului se ciocneau la trunchiere și **pierdeau 54 din 500 de
secțiuni** din E, iar cele două sonde pe care le rulasem defineau `A` **diferit** (una pe rândurile
lui `scan_ramas`, cealaltă pe toate restanțele și interdicțiile). Concluzia nu s-a mutat; cifrele,
da. Scriptul din repo produce acum un singur set.*

*Deci nu se dublează munca — se ratează. Backlogul și singurul lucru care chiar exercită aplicația
pe un ecran vorbesc despre lucruri aproape disjuncte.* Suprapunerea reală, cât e, e concentrată pe
**declarații**: D112, D300, D390, D301, D406, D394, D212, D101.

**Muncă numărată de două ori, în backlog:** puțină. Din 39 de restanțe deschise, **4 perechi** au ≥3
obiecte comune, iar **R37** e în toate patru. Obiecte numite de ≥4 restanțe: `main.py` (6), `D406`
(5), `D300` (5), `D390` (4).

**Istoric:** `main.py` **131** de commituri în 30 de zile, `static/js/ecrane/firme.js` **119** —
amândouă numite de doar 2 liste. Din 130 de fișiere numite de liste, **10** n-au fost atinse deloc.

*Recalculabil: `./venv/bin/python scripts/masoara_suprapunerea.py`. **N-are gardă și n-are clichet**,
deliberat: e o cifră de decizie, o singură dată, nu o populație de păzit — iar axa de instrumente e
închisă.*

### 2. Supervizorul: ce există chiar rulează, dar confruntă aproape numai vertical

**`verifica_diferente_d394` NU EXISTĂ**, sub niciun nume. D394 apare o singură dată în
`control_incrucisat`, ca `_thunk_d394` — reconciliere cu propria sursă, nu confruntare cu altă
declarație.

**Ce rulează pe cont propriu, azi:** cronul de la 08:00 (`notificari_scadenta` →
`alerte_control_fiscal.ruleaza()`) trece portofoliul prin **patru** verificări — `verifica_tva`,
`verifica_d112`, `verifica_d390`, `verifica_cota_tva` — și împinge în clopoțel **doar roșul**,
agregat pe firmă. *Deci jumătatea „declanșator propriu" a supervizorului există deja și funcționează.*

**Ce rulează doar la cerere:** `reconciliaza_declaratii` — suprafața unificată pe **9** declarații
(D300, D394, D390, D301, D112, D406, D100, D101, D205) — se cheamă numai din
`control_fiscal_api.py`, adică atunci când contabilul deschide ecranul.

**PERECHILE CONFRUNTATE, numărate:**

    declarație ↔ evidență (VERTICAL)   D300↔rulaje · D112↔rulaje+note · D390↔facturi IC ·
                                       cotă TVA↔registru · plus 9 × recalcul din sursă
    declarație ↔ declarație (ORIZONTAL) UNA SINGURĂ: compara_d390_vs_d300

**Aia e gaura.** `reconciliaza_declaratii` are **zero** perechi orizontale: fiecare thunk cheamă
`dXXX_reconciliere.reconciliaza`, adică declarația față de **propria** sursă. Nimic nu confruntă
D394 cu D300, D101 cu D100, D205 cu profitul distribuit, D406 cu restul. *Nouă declarații verificate
fiecare pe verticala ei nu produc nicio afirmație despre coerența dintre ele.*

**Corectură la propria măsurătoare:** prima sondă a raportat 11 funcții „fără apelant de producție",
între care `verifica_d390` și `verifica_cota_tva` — care sunt chemate din `main.py`. Cerea o
paranteză după nume, iar `main.py` le pasează ca **referință** (`_incrucisat(_ci.verifica_d390, …)`).
Refăcută cu AST: **13 referite din afară, 9 interne** — toate cele 9 chemate din modul, niciuna
moartă. *A patra oară azi când o sondă a mea numără forma în loc de efect.*

## 01.09.2026 (5) — Supervizorul: axa orizontală, cu două tării

**Gaura măsurată în tura trecută:** din tot ce confruntă aplicația, **o singură** pereche e
orizontală (declarație contra declarație) — `compara_d390_vs_d300`. Restul e vertical: fiecare
declarație față de propria sursă. *Nouă declarații verificate fiecare pe verticala ei nu produc
nicio afirmație despre coerența dintre ele.*

**Ce s-a construit.** `core/supervizor.py` — locul unde stau perechile orizontale, cu:

  - **cele două tării** ale lui Costin, ca nomenclator ÎNCHIS (`EURISTICA` / `CERTA`);
  - **tabelul de tipuri**, care e **date, nu regulă**: tăria se atribuie pe tip, de Costin. Un tip
    necunoscut **ridică**; un tip cunoscut dar neatribuit **se vede și nu produce niciun efect**.
    *Propunerea mea stă în `propus`/`motiv_propunere` și n-are cum să devină regulă prin trecerea
    timpului* — **R115**;
  - **amprenta pe CIFRE, nu pe proză.** O reformulare nu invalidează o confirmare; o cifră schimbată
    o invalidează. Fără asta, „confirmare explicită" ar fi devenit o bifă permanentă;
  - `public.supervizor_confirmari`, cu **amprenta în cheia primară** și `motiv` NOT NULL — *„iar
    confirmarea rămâne scrisă"*;
  - culegere **după eticheta de tip**, nu după modul: orice funcție poate emite o constatare
    orizontală dacă o ștampilează cu un tip înregistrat. Perechile devin o mulțime de date.

**Ce NU face, și e scris în modul:** nu blochează nimic (nici certele — ele cer o confirmare, pe care
poarta de depunere o citește) · nu inventează identități fiscale (azi există **una**; restul se
adaugă când au temei, nu ca să pară plin) · nu compară recalculat cu recalculat pretinzând că e
„declarat".

**O măsurătoare care a schimbat designul:** din **55** de depuneri, doar **1** are rânduri
persistate. Am crezut întâi că perechea orizontală e moartă. Nu e: calea **actuală** persistă
rândurile (F163v2, `coada_api`), iar cele 54 sunt istorie dinainte. Deci perechea răspunde azi onest
*„n-am ce compara"*, și devine vie pe măsură ce se depune prin aplicație. *Diferența dintre „stricat"
și „gol" se vede doar citind calea de scriere, nu numărând rândurile.*

### Supervizorul, tura a doua (01.09.2026) — a cincea cale tăcută, și domeniul

**GARDĂ: axa orizontală are O SINGURĂ ieșire, ștampilată o singură dată.**
`core/control_incrucisat.orizontal_d390_vs_d300` (înveliș) + `_orizontal_d390_vs_d300` (corp).
Gărzile: `core/test_supervizor.py::test_a_cincea_cale_FARA_NICIO_DEPUNERE_e_stampilata_si_supervizorul_o_VEDE`
(schemă efemeră, firmă fără nicio depunere D300) și `::test_corpul_orizontal_nu_se_poate_chema_OCOLIND_invelisul`
(AST — corpul nu se poate chema ocolind învelișul, iar învelișul chiar ștampilează).

**CE A PRINS, măsurat pe cele 19 firme ale portofoliului:** supervizorul vedea **3** constatări
orizontale și pierdea **tăcut 13**. Comparația declarație-contra-declarație avea **cinci** căi de
ieșire, nu patru: a cincea — *nicio depunere D300 prin aplicație* — trăia în corpul lui
`verifica_d390`, chema `_absenta_libera` **direct**, fără `_stampileaza`, iar
`supervizor.constatari_firma` o socotea verticală și o sărea. *Gardul de dinainte proba cele patru
căi ale funcției PURE; a cincea era cu un nivel mai sus, unde nimeni nu se uita.* **Efect: 3 → 16
ștampilate, 13 → 0 pierdute.**

**De ce înveliș și nu petic pe ramura care lipsea:** peticul ar fi lăsat clasa în picioare — a șasea
cale s-ar fi născut la fel de tăcut. **Mutații probate (RED):** (1) învelișul întoarce corpul
nestampilat → cad amândouă gărzile; (2) `verifica_d390` cheamă corpul direct, ocolind învelișul →
cad amândouă.

**GARDĂ: o firmă nu poate dispărea dintr-o cifră de portofoliu.**
`core/supervizor.ruleaza_portofoliu` — trei rezultate EXCLUSIVE per firmă (`CONSTATARI` /
`FARA_SUBIECT` / `NEVERIFICAT`), iar rezumatul e **derivat** din listă, nu acumulat pe drum.
Gărzile: `::test_TOATE_CELE_TREI_rezultate_apar_si_SUMA_lor_e_domeniul` (cu anti-vacuu: proba
exercită toate trei, altfel invariantul ar trece pe o lume incompletă) ·
`::test_o_firma_care_RIDICA_e_NUMITA_nu_tacuta` · `::test_FARA_SUBIECT_nu_se_poate_citi_ca_VERIFICAT_SI_CURAT` ·
`::test_campul_ORIZONTAL_RULAT_lipsa_RIDICA_nu_cade_pe_implicit` · `::test_domeniul_se_DECLARA_in_raspuns` ·
`::test_supervizorul_pe_portofoliu_NU_SCRIE_nimic`.

**Ce face imposibil, și de ce are forma asta:** criteriul de prioritate dat de Costin —
*ce poate produce o cifră validă și falsă*. Un parcurgător scris firesc întoarce „19 firme, 0
constatări", strângând la un loc trei lucruri care nu seamănă: nimic găsit · nimic de comparat ·
**n-a rulat deloc**. **Tiparul e măsurat, nu presupus:** `core/alerte_control_fiscal.ruleaza()`
incrementează `tot["firme"]` **după** succes, deci o firmă care ridică nu apare în niciun contor al
dicționarului întors — **R116**. **Mutații probate (RED):** (3) firma care ridică e sărită cu
`continue`, ca în cron → cad două gărzi; (4) `FARA_SUBIECT` colapsează în `CONSTATARI` → cad două.

**Ce a rulat pe portofoliul viu, după reparație:** `CONSTATARI 16 · FARA_SUBIECT 0 · NEVERIFICAT 3`,
suma **19** = domeniul. Cele trei neverificate sunt **numite**, cu cauza: D390 nu se poate calcula
(profil incomplet). *Înainte, aceleași trei firme și celelalte treisprezece arătau identic: tăcere.*

**CE AU PRINS GĂRZILE CARE NU ȘTIAU CĂ VINE MODULUL** — patru, toate ale mele, în aceeași tură:
`ruff` (**F821** — importul local `_d390` s-a pierdut la extragerea blocului; efectul era o
degradare **tăcută** în gri, adică exact clasa reparată) · `test_afirmatii_tipate` (NEVERIFICAT era
proză într-o cheie `cauza`; e acum afirmație tipată `verificare_rupta`, felul al șaselea din
nomenclatorul închis, adăugat 21.08 pentru exact clasa asta) · `test_garzi_pe_text` (**trei**
aserțiuni ale mele erau pe text — rescrise pe structură, METODA §23) · `test_clichete_generate`
(umbra 77u crescuse cu 1, blocul regenerat).

### R115 închisă — și răspunsul a golit un gard, tăcut (01.09.2026)

**Costin a atribuit tăria:** `D390_VS_D300_IC` → **EURISTICA**, confirmat. Și a dat **criteriul**,
care contează mai mult decât valoarea: *„Tăria se dă după dacă diferența admite o explicație
legitimă, nu după cine sunt cele două părți. Certă = orice nepotrivire e eroare."*

**GARDĂ NOUĂ: o tărie atribuită poartă motivul ei scris.**
`core/test_supervizor.py::test_o_TARIE_ATRIBUITA_poarta_motivul_ei_scris` — câmpul `motiv_tarie` e
obligatoriu pe orice tip cu tărie. *Fără el, un tip nou ar putea primi o tărie prin analogie cu
vecinul din tabel — exact greșeala pe care am făcut-o eu propunând CERTA: m-am uitat la cine sunt
părțile, nu la dacă diferența admite o explicație legitimă. Criteriul trăiește ca DATE, nu ca proză
într-un antet.* **Mutație probată (RED):** `motiv_tarie` redenumit → gardul cade.

**GARDĂ NOUĂ: perechea reală e EURISTICA, deci nu cere NICIODATĂ confirmare.**
`::test_perechea_reala_e_EURISTICA_deci_nu_cere_NICIODATA_confirmare` — probat pe tipul **real**, nu
pe cel sintetic. **Mutație probată (RED):** tăria întoarsă la CERTA → cad două gărzi.

**ȘI PARTEA CARE CONTEAZĂ MAI MULT DECÂT AMÂNDOUĂ: RĂSPUNSUL A GOLIT UN GARD.**
`::test_un_tip_NEATRIBUIT_nu_cere_confirmare_si_nu_tace` parcurgea `tipuri_neatribuite()`. Cât timp
singurul tip n-avea tărie, bucla avea ce parcurge. **La atribuire, mulțimea a devenit vidă — iar un
`for` pe o mulțime goală trece.** Gardul ar fi rămas verde despre o regulă pe care n-o mai verifica.

**NU E O BĂNUIALĂ — E MĂSURAT, în amândouă direcțiile:** cu mutația care strecoară implicitul
(`cere_confirmare` întoarce `True` pe tărie neatribuită), **forma VECHE a testului TRECE** (`1 passed`),
iar forma nouă **cade** (`3 failed`). Reparat cu un tip **sintetic neatribuit** înregistrat în probă:
regula se probează chiar când tabelul real e complet, iar tipul următor pe care Costin nu l-a împărțit
încă găsește gardul viu.

**Clasa se numește, și e mai largă decât instanța: R117.** *Un gard al cărui subiect e o mulțime de
lucruri NEREZOLVATE se golește exact în ziua în care ultimul se rezolvă — adică în ziua în care
nimeni nu se mai uită la el.* Nu e „gardul e greșit": a fost corect toată viața lui, până la o
schimbare care nu l-a atins. **Consemnată, nu lucrată** (axa instrument/igienă e oprită), cu condiția
scrisă în `CONFORMITATE.md`.

### Supervizorul S-A LEGAT (01.09.2026) — și prima depunere reală a scos o afirmație falsă

**Costin a dat cele două lucruri rămase**, iar modulul a ieșit din `test_module_nelegate.PIN`:
*declanșare* = „extinde cronul de 08:00 care există. Plus rulare la cerere. Nu construi al doilea
mecanism" · *ieșire* = „constatările deschise pe firmele lui, cu temei, în ecran propriu. Clopoțelul
rămâne roșu agregat, nu o notificare pe constatare".

**MĂSURAT ÎNAINTE DE A CONSTRUI, și a scurtat lucrul: clopoțelul era DEJA cablat.** O constatare
orizontală roșie face `verifica_d390` să întoarcă `stare="rosu"`, iar `alerte_control_fiscal.
verificatori_rosii` o duce agregat pe firmă. Deci partea a treia se respectă **neatingând** nimic —
un push din supervizor ar fi fost chiar al doilea mecanism.

**GĂRZI NOI (4), cu mutație probată pe cinci direcții:**
`::test_supervizorul_NU_e_un_al_doilea_mecanism_de_cron` (AST: fără `__main__`, fără `cron.ruleaza`) ·
`::test_declansarea_sta_pe_slotul_de_08_care_EXISTA` (AST: cronul îl cheamă) ·
`::test_supervizorul_NU_impinge_nimic_in_clopotel` (AST: nu atinge `notificari_api`) ·
`::test_ruta_la_cerere_NU_scapa_schema_si_isi_NUMESTE_domeniul`.

**GARDĂ NOUĂ pe o capcană pe care ruta a creat-o:** `_domeniu_efectiv` — un domeniu **injectat**
trebuie NUMIT, altfel `ruleaza_portofoliu` **ridică**. `DOMENIU` spune, în text, *„nu se filtrează pe
cabinet"*; ruta rulează pe firmele cabinetului (14, nu 19). *Un domeniu nedeclarat se citește ca
„toate firmele"; unul declarat GREȘIT se citește ca o afirmație verificată — mai rău.*

### Ce a scos PRIMA DEPUNERE REALĂ (R40), și n-ar fi ieșit altfel

**Costin a depus D300 pe `tenant_017`, 08/2026, prin interfață.** Jurnalul: `(14769, 2026, 8, 'd300',
nr=1, randuri NENUL, 3 chei în R, xml 708 octeți)`. Perechea orizontală a vorbit prima oară:
**VERDE**, *„D390 și D300 depus coincid (8.000,00 lei)"*, tărie EURISTICA, `cere_confirmare=False`.

**DAR a spus că lasă rândurile IC goale, iar `R1_1` avea 8.000.** Citit la sursă
(`core/d300.py:403-424`): `R1_1` se derivă **AUTOMAT** din facturile emise către UE, `R5_1`/`R18_*`
din cele primite, iar introducerea manuală peste ele e **refuzată** ca dublă numărare.

**Deci textul afișat contabilului era FALS** — spunea că rândurile intracomunitare sunt „manual-only".
**Prag 1, reparat pe loc.** Și, mai important, ce confruntă perechea s-a scris cum e: cele două laturi
vin din **aceleași facturi**, deci nu sunt surse independente. Ce prinde comparația e **deriva** între
ce s-a depus ATUNCI și evidența de ACUM — nu o eroare pe care ambele motoare o fac la fel. *Un „verde"
citit ca „am verificat la sursă" e mai rău decât niciun verde.*

**Un gard PINUIA fraza falsă.** `test_dvsd_rosu_d390_livrare_d300_fara_R1_1` cerea cuvântul
„manual-only" în temei. A ținut minciuna în loc s-o prindă — *o aserțiune ancorată pe TEXT păzește
formularea, nu faptul* (METODA §23). Rescrisă pe ce contabilul chiar trebuie să afle: CARE rând lipsește.

### Poarta vizuală a prins ceva ce ar fi ajuns în producție

**Ecranul nou a rupt TOATE ecranele.** `„e în regulă"` scris cu ghilimea românească de deschidere și
închidere ASCII **termină șirul JS** — a șaptea instanță a aceleiași clase, prima în JS. Efectul nu
era local: `cabinet.js` importă `supervizor.js`, iar un modul care nu se parsează oprește tot
desktopul cabinetului. **Toate cele 15 ecrane au picat cu „waiting for `.cab-card`".**

**ȘI E MAI GRAV DECÂT O GREȘEALĂ DE SINTAXĂ: fișierele statice se servesc DE PE DISC.** Nu există
poartă între scrierea unui `.js` pe server și producție — nici commit, nici restart. Poarta verde
apără Python-ul; JS-ul e live din secunda în care îl scriu. **R118**, consemnată.

**Cele trei unelte, pe ecranul atins** (`frontend_test/vizual/nav_ecrane.py` — primul ecran de
**cabinet** din inventar; toate celelalte sunt de firmă):
`axe`: **0** reguli / 0 noduri / 0 contrast / 0 fără-etichetă / title 0-0-0 ·
`mobil`: **0** title cu info unică pierdută, 2 reguli `:hover` și 4 ținte <44px — **toate ale
învelișului** (`nav-ghid`, `nav-clopot`, `nav-iesire`, `nav-x`), niciuna a ecranului —, overflow-x **nu** ·
`baseline`: **STABIL, 0.0000%** self-diff.

**Și o măsurătoare pe care era să n-o fac.** Prima rulare `--compare` a dat SCHIMBAT pe toate cele 14
ecrane vechi — dar baseline-urile erau vechi de **2 commituri** pe `static/`, deci cifra nu spunea a
cui e vina. Am izolat: `git stash` pe `static/`, referințe refăcute pe codul din HEAD, `stash pop`,
comparație. **Diferența e a mea și e benignă:** desktopul rămâne în DOM sub fereastră (dovadă
independentă: scanul mobil a numărat **14** `.cab-card` cu fereastra deschisă), capturile sunt
`full_page`, iar cardul nou deplasează layoutul cu ~3%. *O cifră care nu separă contribuția ta de
deriva dinainte nu e o măsurătoare.*

### Perechi orizontale pe SURSE INDEPENDENTE (02.09.2026) — și trei verdicte de respingere

**Comanda lui Costin, verbatim:** *„Continuă cu perechile orizontale care confruntă surse
independente — perechea de azi nu o face, și tu ai scris de ce."* Plus regula de lucru: *„Verifică
fiecare identitate la sursă înainte s-o construiești"* și *„Ce nu se confirmă la sursă se
consemnează ca respins, cu motivul."*

**AVERTISMENTUL LUI, RESPECTAT ȘI MĂSURAT:** *„D300 a pierdut rândurile de 19% și 9% în ianuarie
2026, deci numerele de rând nu se iau din memorie."* Citit din cod: azi **R9 = 21%**, **R10 = 11%**.

**CE S-A CONSTRUIT — două perechi, ambele CERTE (tăria dată de el):**

| pereche | identitate | sursa, verificată VERBATIM |
|---|---|---|
| **D101 rd.50 ↔ Σ D100 «Suma de plată»** | ce a scris contabilul în D101 față de ce s-a declarat efectiv trimestrial | `opanaf_206_2025_d101.txt:875` |
| **D101 rd.48 ↔ rulaj debitor cont 691** | impozitul declarat față de cel înregistrat în contabilitate | `opanaf_206_2025_d101.txt:862` + OMFP 1802 pentru 691 |

**O CORECȚIE DE ANCORĂ, față de cum fusese numită.** Costin a spus *„impozitul din D101 = cel din
contul de profit și pierdere (F20)"*. **Nu se folosește F20 rd.35**, din două motive măsurate:
`core/bilant.py:245` pune acolo **`691 + 698`**, iar OMFP 1802 spune verbatim că **698 =
„Cheltuieli cu impozitul pe venit și cu alte impozite"** — altă taxă, care ar produce divergență
falsă pe o firmă cu trecere micro→profit; și antetul modulului își declară singur sursa formulelor
de rând ca **„VERSIUNE NECUNOSCUTĂ"**. Se compară cu **contul 691**, confirmat verbatim.

**GĂRZI NOI (6), toate CALIBRATE PE CAZ POZITIV FABRICAT** — portofoliul viu n-are nicio depunere
D101 cu rânduri, deci fără subiect fabricat perechile n-ar fi probate niciodată:
`::test_pereche_D101_vs_D100_COINCID_da_verde_si_DIVERG_da_rosu` ·
`::test_pereche_D101_vs_691_COINCID_da_verde_si_DIVERG_da_rosu` (amândouă în **ambele direcții**) ·
`::test_o_nota_in_CIORNA_pe_691_face_perechea_sa_TACA_nu_sa_acuze` ·
`::test_un_MEMBRU_DE_GRUP_fiscal_nu_e_confruntat_pe_randurile_care_nu_se_completeaza` ·
`::test_o_depunere_D100_FARA_randuri_nu_se_numara_ca_ZERO` ·
`::test_perechile_anuale_NU_se_ancoreaza_pe_anul_CURENT`.
**Mutații probate (RED), pe patru direcții:** ciorna ignorată · depunerea fără rânduri numărată ca
zero · excepția de grup scoasă · ancorarea pe anul curent.

**CRITERIUL LUI, APLICAT PÂNĂ LA CAPĂT — și a scos ceva.** *„Tăria se dă după dacă diferența admite
o explicație legitimă."* Am căutat explicațiile legitime pe fiecare pereche:
- **pe 691 am găsit una și am ÎNCHIS-O în cod:** o notă de regularizare încă în **ciornă** explică
  legitim diferența, iar `rulaje_interval` numără doar note validate. Cât timp există ciornă pe 691,
  perechea spune **GRI** și numește motivul, în loc să afirme o eroare.
- **pe rd.50 am găsit una pe care NU o pot închide din date:** un **D100 depus în afara aplicației**
  nu intră în suma din dreapta, iar diferența ar fi atunci a măsurătorii mele. Am închis ce se putea
  (depunere fără rânduri → GRI), dar asta nu. *Scrisă în `motiv_tarie` și ridicată ca întrebare —
  tăria rămâne cea dată de el, fiindcă atribuirea e a lui.*

**TREI VERDICTE DE RESPINGERE, cerute explicit:**
- **D300 ↔ P300 (RO e-TVA) — RESPINSĂ.** Nu există acces programatic la decontul precompletat.
  Aplicația documentează chiar contrariul premisei uzuale, în `core/d169n.py`: *„D169n NU este
  răspunsul la notificarea e-TVA (decont precompletat)"*, cu validatorul și actul ca temei. **R121.**
- **D394 ↔ e-Factura — sursa există, perechea nu.** `efactura_trimiteri` are `stare='ok'` și
  `mediu='prod'`, dar `core/d394.py` **nu expune id-urile facturilor** incluse. Nu e „compară două
  ieșiri", e clasa R105 (motorul nu-și poate desface cifra). **R119.**
- **D300 ↔ D394 — ancora e `lit. C`, nu „secțiunea C".** Confirmată verbatim
  (`opanaf_2194_2025_d394.txt:813`): *„C. Rezumatul declarației privind operațiunile desfășurate cu
  persoane impozabile înregistrate în scopuri de TVA"* — substanța numită de Costin e corectă,
  eticheta nu. Maparea rând-cu-rand D300 ↔ lit. C **nu e încă verificată**, deci nu se construiește.
  **R120.**

### Tăria descrie IDENTITATEA, nu calitatea datelor noastre (02.09.2026)

**Regula, dată de Costin după prima mea aplicare greșită a criteriului, verbatim:** *„Tăria descrie
identitatea, nu calitatea datelor noastre. Unde nu poți stabili că vezi tot, spui gri — ca la ciorna
pe 691."*

**Ce corectează.** Propusesem coborârea perechii D101 rd.50 la euristică, fiindcă un D100 depus în
afara aplicației ar face suma din dreapta mai mică. Greșit: **identitatea din ordin ține oricum** —
ce lipsește e **vederea** pe o latură. O lipsă de vizibilitate se răspunde cu **GRI și motivul
scris**, nu prin coborârea tăriei.

**GARDĂ NOUĂ:** `core/test_supervizor.py::test_un_TRIMESTRU_NEVAZUT_da_GRI_nu_ROSU`. Perechea rd.50
nu mai compară când nu vede tot anul: perioadele de raportare D100 ale unei obligații de impozit pe
profit sunt **citite la sursă** (`core/d100.py`, care citează `d100_struct_anaf.txt`: luna 12 e
„luna de sfârșit de an fiscal" cu scadență proprie, restul sunt trimestrele I/II/III — lunile 3, 6,
9). Dacă lipsește vreunul, perechea spune gri și **numește trimestrul**. **Mutație probată (RED):**
scoasă poarta de vizibilitate → 3.000 declarat față de 1.000 văzut devine ROȘU, adică un roșu al
orbirii mele. *Regula stă acum lângă criteriul de atribuire, în antetul `core/supervizor.py` — e mai
largă decât restanța care a produs-o.*

### R120, închisă ca verdict: corespondența există, perechea nu intră în brief

**Corespondența s-a stabilit**, din act și din cod: lit. C **pct. 17** (*„baza impozabilă aferentă
achizițiilor … pentru care se aplică taxarea inversă … art. 331"*) ↔ D300 `R12_1`/`R12_2` (rd.12,
colectat) și `R25_1`/`R25_2` (rd.25, deductibil), citite din `core/d300.py:386-396`.

**Și tot stabilind-o s-a văzut de ce nu se construiește:** `core/d394.py:969` și `core/d300.py:890`
citesc **amândouă `FROM facturi`**, cu **același** flag `taxare_inversa`. Deci ar fi a patra pereche
care confruntă aceeași realitate calculată de două motoare — exact slăbiciunea de la care a pornit
comanda. *Corespondența rămâne scrisă în R120, ca să nu fie re-dedusă dacă Costin o vrea totuși ca
verificare de derivă între două depuneri.*

### D300 ↔ D394 ca verificare de DERIVĂ — și un PRAG 1 găsit pe drum (02.09.2026)

**Costin a decis să se construiască, EURISTICĂ, cu motivul scris de el:** *„motivul e roșul, nu
verdele: două declarații depuse care nu se potrivesc între ele e expunere reală la ANAF, iar
corelația e una dintre cele pe care ANAF le rulează."* Ce prinde: **intervalul dintre cele două
depuneri**, când facturile se pot schimba, plus **intervenția manuală** într-una din ele.

**PRAG 1, GĂSIT ÎNCERCÂND SĂ CONSTRUIESC PERECHEA: un D394 cu operațiuni nu putea fi trimis în
coadă deloc.** `coada_api.randuri_din_res` face `json.dumps(dataclasses.asdict(res))`, iar
`Rezultat`-ul D394 are **chei TUPLU** în `op1`/`rezumat1`/`detaliu`. `json.dumps` ridică
`TypeError: keys must be str … not tuple`, iar apelul din `main.py:3446` (`POST /coada`) e
**negardat** — deci cererea ieșea **500**. *Se aprindea exact pe firmele care aveau ce declara: pe
`op1` gol serializarea trecea.* Măsurat pe `tenant_017`, 08/2026, înainte de reparație.

**Reparat**: cheile tuplu devin **JSON de listă**, nu șir lipit cu separator — componenta a cincea e
denumirea partenerului, iar orice separator ales ar putea apărea în ea. Așa cheia rămâne
**reversibilă**, iar cine confruntă două declarații poate întreba „ce tip de operațiune e" fără să
ghicească. Gardat de `::test_serializarea_unui_D394_cu_operatiuni_NU_MAI_RIDICA`, care probează chiar
cazul rău: un partener al cărui nume **conține** `|`.

**GĂRZI NOI (4), calibrate pe caz fabricat:**
`::test_deriva_D300_D394_COINCID_da_verde_SLAB_si_DIVERG_da_ROSU` (ambele direcții; **proba care
contează e roșul**) · `::test_deriva_numara_DOAR_achizitiile_cu_taxare_inversa` (o livrare «V» sau o
achiziție normală «A» n-au ce căuta în sumă) · `::test_o_cheie_op1_NECITIBILA_da_GRI_nu_divergenta` ·
`::test_serializarea_unui_D394_cu_operatiuni_NU_MAI_RIDICA`.
**Mutații probate (RED), patru direcții:** filtrul pe tip scos · cheia necitibilă ignorată ·
verdele fără declarația de slăbiciune · serializatorul întors la forma care ridică.

**VERDELE ÎȘI DECLARĂ SLĂBICIUNEA CA FAPT, nu doar în proză.** Constatarea poartă `verde_slab=True`,
iar garda asertează pe câmp, nu pe formulare — o gardă pe text ar fi păzit fraza, nu proprietatea
(METODA §23). Temeiul spune, ca la D390, că ambele laturi se derivă din aceleași facturi: coincidența
înseamnă *„cele două depuneri sunt de acord"*, nu *„declarația se potrivește cu realitatea"*.

**Perioada se alege singură** — cea mai recentă în care AMÂNDOUĂ sunt depuse cu rânduri. A treia oară
când se aplică tiparul (`_d300_depus_recent`, `_d101_depus_recent`, acum `_perioada_cu_ambele`):
ancorarea pe luna curentă ar fi făcut perechea gri prin construcție.

### R119 — e-Factura ↔ D394, singura pereche pe surse cu adevărat independente (02.09.2026)

**Costin:** *„e singura pereche care confruntă surse independente: ce a plecat la ANAF prin
e-Factura față de ce s-a declarat în D394. **Verdele ei ar însemna ceva**, spre deosebire de cele
patru existente."* Și constrângerea: *„Blocajul se ridică prin generator, nu pe lângă el … Nu
reimplementa regulile de eligibilitate — două motoare care se despart în tăcere e chiar clasa care
produce cifra validă și falsă."*

**BLOCAJUL S-A RIDICAT PRIN GENERATOR, ȘI A FOST IEFTIN.** Măsurat înainte de a atinge ceva: toate
cele **cinci** căi de acumulare din `d394.calcul_d394` trec prin **`_adauga`**, care întreține deja
un dicționar paralel (`categorii`) pe aceeași cheie și îl curăță la aceleași `del op1[k]`. Deci
expunerea e **încă un dicționar paralel**, nu o a doua implementare. *Am spus asta înainte de a
începe, fiindcă mi s-a cerut să mă opresc dacă e mai mare decât pare — nu era.*

`Rezultat` capătă **`facturi_incluse`** (cheia operațiunii → id-uri de facturi) și
**`manuale_fara_factura`**. `f.id` era deja selectat în SQL și se pierdea în `pull`, la construcția
dicționarului trimis la calcul.

**GARDA CARE APĂRĂ CHIAR CONSTRÂNGEREA LUI:**
`::test_ELIGIBILITATEA_ramane_a_generatorului_nu_se_reimplementeaza` — o factură pe care generatorul
o **exclude** nu poate apărea printre cele incluse. Proba folosește deliberat o excludere care trece
prin **`del op1[k]`** (achiziție cu taxare inversă fără categorie art. 331), nu una oprită de un
filtru dinainte — altfel n-ar prinde mutația care contează. **Mutație probată (RED):** scos
`incluse.pop(k, None)` → o factură exclusă apare ca declarată.

**CELELALTE GĂRZI (4):** `::test_o_factura_TRANSMISA_si_NEDECLARATA_da_ROSU_si_o_NUMESTE` (și o
**numește**, altfel e un reproș fără adresă) · `::test_toate_transmise_si_declarate_da_VERDE_si_verdele_ASTA_inseamna_ceva`
(constatarea **nu** poartă `verde_slab` — a-l slăbi ar șterge exact diferența pentru care perechea a
fost cerută) · `::test_o_trimitere_pe_TEST_sau_NEACCEPTATA_nu_conteaza_ca_plecata` ·
`::test_operatiunile_MANUALE_dau_GRI_nu_rosu`. **Mutații probate (RED):** trimiterile pe `test`
socotite plecate · operațiunile manuale ignorate.

**A PATRA APLICARE A REGULII „unde nu poți stabili că vezi tot, spui gri", și prima fără s-o cer:**
o operațiune **manuală** (bon, borderou) n-are factură în spate, deci o factură transmisă ar putea fi
acoperită de ea fără ca eu să pot ști. Perechea spune **gri** și numește câte sunt.

### STRATUL DE EFECT, cablat — și gardul care cade dacă apelantul dispare (02.09.2026)

**Costin:** *„O constatare CERTĂ pe firma și perioada care se depune cere confirmare explicită
înainte de depunere, iar confirmarea rămâne scrisă: cine, când, peste ce constatare. **Nu blochează
niciodată**. Cele EURISTICE nu cer nimic; rămân doar vizibile. **O gardă trebuie să cadă dacă
apelantul dispare** — `neconfirmate()` fără apelant e chiar starea de azi, și n-a semnalat-o nimic."*

**CE S-A CONSTRUIT.** `supervizor.poarta_confirmarii()` — scrie confirmările primite (fiecare peste o
constatare ANUME, prin **amprentă**) și întoarce **ce a rămas neconfirmat**. Nu ridică, nu refuză,
nu întoarce niciun blocaj: **cine cheamă decide**. Chemată din `main.py`, pe calea
`POST /coada/{id}/depune`, ÎNAINTE de `marcheaza_depusa`.

**„NU BLOCHEAZĂ NICIODATĂ" — INCLUSIV PRIN AVARIE.** Apelul stă într-un `try` al cărui `except`
**nu re-ridică**: dacă supervizorul crapă (schemă ruptă, profil incomplet), depunerea **continuă**, cu
eșecul logat. *Altfel motorul care „nu blochează" ar fi devenit exact poarta pe care contractul lui o
interzice — și ar fi blocat prin avarie, felul cel mai prost, fiindcă n-ar fi fost nici măcar o
decizie.* Iar când chiar există constatări neconfirmate, răspunsul **numește calea de trecere în
chiar corpul lui** (interdicția 47: un refuz fără ieșire pentru om).

**GARDA CERUTĂ, și de ce n-a existat până azi:**
`::test_EFECTUL_nu_poate_ramane_NELEGAT_fara_sa_semnaleze` — `poarta_confirmarii` trebuie să aibă
apelant de **producție**, și anume în `main.py`. **Starea de ieri era chiar gaura pe care o închide:**
`neconfirmate()` a stat fără niciun apelant, iar `test_module_nelegate` n-a semnalat-o fiindcă
lucrează la nivel de **MODUL** — iar modulul ERA chemat, prin `ruleaza_portofoliu`. *Absența trăia la
nivel de FUNCȚIE, unde nu se uita nimeni.* Anti-vacuu peste ea:
`::test_poarta_confirmarii_chiar_foloseste_cele_doua_functii_ale_efectului` — un apelant care cheamă
o carcasă ar fi trecut gardul.

**CELELALTE GĂRZI (4):**
`::test_supervizorul_care_CRAPA_nu_opreste_depunerea` (AST: `except` fără `raise`) ·
`::test_o_CERTA_ROSIE_cere_confirmare_iar_confirmarea_RAMANE_SCRISA` (probează **cine · când · peste
ce**, pe rândul scris) · `::test_o_EURISTICA_nu_cere_NIMIC_la_depunere` (inclusiv pe roșu) ·
`::test_o_confirmare_pe_ALTA_amprenta_nu_stinge_cererea`.

**Mutații probate (RED), trei direcții:** **apelantul dispare** din `main.py` → cad două gărzi ·
`except` re-ridică → avaria ar opri depunerea · amprenta ignorată → o confirmare ar nimeri oriunde.

**PERIOADA A DEVENIT SURSĂ UNICĂ ÎNAINTE SĂ APARĂ PARALELA.** Derivarea `(an, luna)` trăia doar în
`marcheaza_depusa`; poarta confirmării avea nevoie de ea **înainte** de depunere. În loc de a doua
derivare, `coada_api.perioada_din_payload()` + `firma_si_perioada()`. *Regula „nu construi paralel",
aplicată înainte ca paralela să existe.*

## 03.09.2026 — Garda care ține §27 să nu rămână o intenție, și două gărzi pe care curățenia le-a doborât

**Cerută de Costin în chiar tura în care §27 s-a rescris**, verbatim: *„Adaugă la curățenie: o gardă
care refuză introducerea de fișiere imagine ca probă vizuală. **Fără ea, §27 rescris rămâne o intenție
și capturile revin la prima tură de interfață.** Capturile pentru diagnostic, în timpul unei ture,
rămân permise — dar nu se salvează și nu devin bază de comparație."*

`core/test_fara_probe_imagine.py` — **7 teste**. Granița pe care o trage nu e *„ce e o probă"*, care e
o judecată, ci **„intră în index?"**, care e mecanic:

| ce | verdict |
|---|---|
| capturi făcute **în timpul** turei, ca să te uiți la ele | **permis** — așa s-au găsit defectele zilelor astea |
| aceleași capturi **salvate în repo** | **refuzat** — mulțimea imaginilor din index e pinată: 30 de probe + 5 de produs + 2 date încărcate |
| cod care compară două imagini | **refuzat** — pe **import**, structural (AST), nu pe numele funcției |

**Clichet în AMÂNDOUĂ direcțiile** (METODA §22): una nouă pică, dar și una **dispărută** pică, cerând
să fie scoasă din listă. *Un clichet care păstrează morții devine, în câteva luni, o afirmație despre
o lume pe care n-o mai vede.*

**Interdicția pe mecanism e pe IMPORT, nu pe nume.** `PIL` / `pixelmatch` / `imagehash` / `cv2` /
`skimage` în Python, citite din AST; `toHaveScreenshot` / `toMatchImageSnapshot` în JS, citite ca
text — *motivul scris lângă gardă, cum cere METODA §23: n-avem parser de JS în suită, iar riscul e
mic fiindcă sunt nume de API, nu cuvinte de proză.* Măsurat azi: **0** ocurențe în tot repo-ul.

**RED-PROOF PE MECANISMUL REAL, nu pe o listă fabricată** (regula 3, „se probează pe portofoliu"):
am creat o captură, am făcut `git add -f`, garda a devenit roșie cu mesajul ei — apoi am scos-o.
*Calibrarea pe listă fabricată e și ea acolo, în amândouă direcțiile, dar singură n-ar fi dovedit că
garda vede indexul adevărat.*

**Și ce a prins poarta, la prima încercare de commit:** una din aserțiunile de calibrare ale gărzii
noi era ea însăși ancorată pe text — `assert "…/proba_noua.png" in gasite - ADMISE` —, iar clichetul
**50** a urcat 1221 → 1222. *Ironia e utilă, nu amuzantă: o gardă scrisă ca să apere o regulă
structurală a intrat în repo cu o aserțiune pe apartenență.* Rescrisă pe **egalitate de mulțimi**, care
prinde și direcția opusă (un filtru prea lacom, care ar lua și un `.py` drept imagine) — clichetul a
coborât înapoi la **1221**, fără să fie ridicat. *Un clichet ridicat „doar cu unul" e felul obișnuit în
care o interdicție devine o statistică.*

---

**ȘI DOUĂ GĂRZI CARE AU PICAT PENTRU CĂ LUMEA S-A SCHIMBAT — amândouă aveau dreptate.**

- **`test_metoda_vie::test_fisierele_numite_de_metoda_exista`** cerea ca fiecare cale citată în
  METODA să existe pe disc. §27 rescris **numește**, pe drept, unealta scoasă. *Un document de metodă
  trebuie să poată scrie și ce a scos — altfel deciziile de arhitectură n-au unde trăi.* Reparat cu
  un **bloc declarat**, `CAI-SCOASE`, pentru care gardul cere **exact opusul**: căile din el trebuie
  să **lipsească**. Dacă `baseline_scan.py` reapare, blocul devine roșu. *Structural (delimitatori),
  nu textual — nu se caută cuvântul „scos" prin proză, ceea ce §23 interzice.*
- **`test_perimetru::test_ce_s_a_modificat_fata_de_HEAD_nu_include_fisierele_NEURMARITE`** avea un
  anti-vacuu care cerea `assert nt` — adică **se sprijinea pe sediment**: cele 299 de fișiere
  neurmărite pe care arborele le purta permanent. În ziua în care arborele s-a curățat, aserțiunea a
  picat. *Un anti-vacuu care depinde de dezordinea din jur măsoară dezordinea, nu instrumentul.*
  Acum testul **își produce singur** condiția: creează un fișier neurmărit, verifică amândouă
  direcțiile, îl șterge.

*Ce merită dus mai departe: curățarea unui arbore a doborât două gărzi, și niciuna nu era falsă. O
gardă poate fi corectă și totuși legată de o stare pe care n-a declarat-o — aici, „există dezordine"
și „metoda numește doar lucruri vii".*

### Ocolirea de curățenie — poarta se sare din INDEX, nu din etichetă (03.09.2026)

**Costin:** *„Adaugă în hook o cale de ocolire pentru commituri numai-curățenie: eticheta
`# doar-curatenie:` în mesaj, ca escape-ul existent. **Condiție:** eticheta e ignorată dacă commitul
atinge vreun fișier executabil sau vreun registru. Se aplică doar la ștergeri, `.gitignore` și
mutări. **Altfel devine cheia care deschide tot.**"*

**CE S-A CONSTRUIT.** `scripts/curatenie.py` — răspunde, din **index**, dacă un commit e numai
curățenie. `pre-commit` îl întreabă și, pe „da", sare `pytest` și verificatorul (cele ~22 de minute);
`commit-msg` cere eticheta când poarta a fost sărită, **și o respinge când nu i se aplică**.

**DE CE DECIDE INDEXUL ȘI NU ETICHETA — nu e o alegere de stil, e ordinea hook-urilor.** La
`pre-commit` mesajul **încă nu există**: cu `git commit -F`, `.git/COMMIT_EDITMSG` poartă mesajul
commitului **precedent** (dovedit 23.08.2026, scris în antetul hook-ului). O poartă care s-ar
deschide cu o etichetă n-ar avea ce citi. *Așa, „ignorată" din condiție e o proprietate a
construcției, nu o verificare care ar putea fi ocolită.* Etichetei îi rămâne **mărturia**: o poartă
sărită în tăcere n-ar lăsa nicio urmă în istorie.

**CELE TREI CONDIȚII.** *Formă:* numai `D`, `R100` (mutare identică) și `.gitignore`. *Clasă:* niciun
`.py`/`.js`, niciun registru — amândouă definițiile **împrumutate prin referință** de la
`scripts/perimetru.py`, ca să nu existe a doua definiție care diverge tăcut. *Referință (în plus față
de comandă, și e cea care contează):* niciun nume șters sau mutat nu e **numit în ce se comite** — un
`.xsd`, o fixtură, o captură citată într-un registru nu sunt nici executabile, nici registre, dar
dacă o gardă le deschide, ștergerea lor e o **modificare de cod prin absență**. *Fără ea, ocolirea
chiar ar fi putut strica o declarație.* Orice eșec al instrumentului înseamnă „nu e curățenie" —
**fail closed** —, iar căutarea de referință greșește deliberat spre refuz.

**GARDA:** `core/test_curatenie.py`, 10 teste, în **amândouă** direcțiile (METODA §22): o curățenie
adevărată **trece** — altfel instrumentul ar putea răspunde mereu „nu" și n-ar scurta niciodată
nimic —, iar fiecare dintre cele patru feluri de a nu fi curățenie **refuză**, numind fișierul care a
produs refuzul. Anti-vacuu pe căutarea de referințe: un nume care chiar e citat e găsit, unul
inventat nu — o căutare care întoarce mereu vid ar declara „curățenie" pe orice ștergere.
*Prima formă a picat la poartă, și pe drept:* numele „inexistent" era scris ca **literal** chiar în
testul care îl declara inexistent, iar după stagiere `git grep --cached` l-a găsit acolo. Acum se
construiește la rulare. **Un gard care se caută pe sine raportează despre o lume care îl conține.**

**Mutații probate (RED), patru direcții:** scoasă verificarea de **executabil** · de **registru** ·
de **referință** · **descablat** hook-ul `pre-commit`. Fiecare omoară exact testul care o păzește,
niciuna nu omoară altceva.

**CE NU ACOPERĂ, declarat:** ramura din `commit-msg` care cere eticheta când poarta **chiar** a fost
sărită nu se poate exercita din suită — dacă indexul ar fi numai-curățenie, suita n-ar rula deloc.
Și un nume construit din bucăți (`"cap" + "turi.png"`) scapă căutării de referință.

**Regula pe care o cablează:** `PLAN_LUCRU.md`, regula 7 de conducere a lucrului.

## 05.09.2026 — Lotul 15: un gard care cerea 16 ecrane din 18, și două datorii numite

**GĂRZI NOI: niciuna.** Campania cere explicit *„fără gărzi noi"*, iar lotul a respectat-o. Ce e
mai jos e o **reparație de gard** și două **datorii**, scrise ca să nu trăiască doar în raport.

### R160 — `ecrane_asteptate()` tăia lista la prima paranteză dreaptă din text

Cuplajul dintre unealta vizuală și gardul ei stă într-o funcție de patru rânduri:
`acoperire_hash.ecrane_asteptate()` citește `nav_ecrane.ECRANE` cu regex, ca să nu importe un
modul care are nevoie de browser. Regexul era `ECRANE\s*=\s*\[(.*?)\]` — **negreedy**, deci se
oprea la **prima** paranteză dreaptă. Iar prima nu e capătul listei: e cea din comentariul
`# [LOTUL 12, R142]`, scris deasupra intrării «emitere».

**Măsurat azi:** din 18 nume, gardul cerea **16**. `emitere` și `operatiuni` puteau lipsi din
artefactul vizual fără ca nimic să cadă — **din chiar tura care le adăugase**, fiindcă acea tură
adăugase și comentariul care taie lista. *A treia instanță a clasei „gardul care nu se verifică pe
sine": un gard care se uită exact unde nu e problema raportează verde despre o lume pe care n-o
vede.*

**Reparat:** blocul se ia până la un `]` la **început de rând** (așa se închide lista), iar
comentariile se scot **înainte** de căutarea numelor — altfel un nume citat într-un comentariu ar
intra în lista pe care gardul o cere. Plus **anti-vacuu**: dacă blocul nu se găsește sau iese gol,
funcția **ridică**. Un `[]` întors tăcut ar face gardul să nu ceară nimic.

**Calibrare:** înainte 16, după 21 (16 + `emitere` + `operatiuni` + cele trei mutate azi).

### Datoria 1 — `admin_raportari` are JS atins, dar nu poate intra în `ECRANE`

Regula casei, scrisă în `nav_ecrane.py`: *un ecran al cărui JS se ATINGE trece în `ECRANE`, cu cele
trei unelte rulate pe el.* Lotul a atins patru fișiere de ecran; **trei** au trecut (`magazin`,
`pachete`, `recomanda`). Al patrulea nu poate: `admin_raportari` trăiește pe desktopul de
**superadmin**, iar cele trei unelte vizuale sunt, **prin construcție**, pe un singur cont —
`interactiune_scan.py` face `ctx.add_init_script(INIT)`, o dată, iar `INIT` e sesiunea patronului de
cabinet.

**Ce ar cere:** un context per cont în cele trei unelte, exact tiparul pe care
`proba_ecrane_formular.py` îl are deja (`ECRANE_CABINET` poartă contul lângă fiecare ecran). E
**construcție**, nu campanie — și lista internă e închisă. Scrisă aici ca să nu se piardă:
*regula n-a fost respectată pe un ecran, iar motivul e o limită a uneltei, nu o scăpare.*

### Datoria 2 — un buton stins își spune motivul doar la survol

`fa-casa`: cu sumă negativă, «Adaugă (notă ciornă)» **rămâne dezactivat**, iar motivul —
*„Completează data și suma întâi"* — trăiește în atributul `title`. Pe desktop se vede la survol;
pe atingere, nu se vede deloc (clasa `title-only pe touch`, pe care scanul de interacțiune o
măsoară deja pe alte ecrane).

**Nu s-a reparat, și de ce:** nu e prag 1 — nimic fals, nimic acceptat greșit, iar refuzul EXISTĂ.
Mutarea motivului lângă câmp e o schimbare de așezare, iar aceea cere confirmare.

## 05.09.2026 — Etapa 2, lotul A: două reparații pe ecranul de casă, și o proprietate care ar putea deveni gardă

**GĂRZI NOI: niciuna.** Lotul a reparat două defecte (R161, R162) și a construit un instrument de
perimetru; niciunul nu cere o gardă nouă, iar lista internă rămâne închisă.

### Ce a scos la iveală reprobarea, și merită ținut minte

**R161 → R162, într-un singur pas.** Reparând un REFUZ (butonul stins al casei), reprobarea cu date
BUNE a arătat că **calea de reușită tăcea**: dispoziția intra, iar mesajul se ștergea în aceeași
clipă, fiindcă `deseneaza()` refăcea `corp.innerHTML` peste el. *Nimeni nu căuta acolo: campania
etapei 1 măsura ce spune aplicația la date GREȘITE, iar acolo tăcerea era pe calea bună.* Etapa 2,
prin construcție, calcă exact pe calea de reușită — și primul lucru pe care l-a găsit e un mesaj
care nu ajunge la om.

### O PROPRIETATE care ar putea deveni gardă, scrisă ca datorie

**TVA colectată din D394 == `R17_2` din D300**, pe aceeași firmă și aceeași perioadă. Verificată
manual în lotul A (1.121 = 1.121) și trecută de amândouă declarațiile prin DUK. E chiar felul de
defect pe care DUK nu-l poate vedea: *o cifră așezată în rândul greșit trece de validatorul de
formă în amândouă declarațiile, dar nu trece de egalitatea asta.*

Perechea EXISTĂ deja în supervizor, dar pe alt obiect: `EFACTURA_VS_D394` compară recipisa de la
ANAF cu ce a declarat generatorul. Asta ar fi a doua față a ei — **generator contra generator**, pe
lanțul de intrare. **Nu s-a construit**: lista internă e închisă, iar comanda etapei 2 cere probe,
nu gărzi. Scrisă aici ca să nu se piardă.

## 06.09.2026 — Trei gărzi lărgite, toate pentru același motiv: domeniul, nu criteriul

**GĂRZI NOI: una singură**, și ea trăiește într-un fișier existent — cele patru teste ale lui R167
din `core/test_c7_periodicitate_trimestriala.py`. Restul turei a **lărgit** gărzi care erau deja
acolo și dădeau verde despre o lume pe care n-o vedeau.

### 1. `core/test_diacritice_afisate.py` — două poziții de afișare în plus (R168)

Gardul scana patru poziții: cheia de obiect (`eticheta:`, `titlu:` …), atribuirea la `.innerHTML`,
primul argument al lui `nav.*`, și nodurile de text din template-literale. Etichetele formularelor
de operațiuni nu trăiesc în niciuna — sunt **al doilea argument, pozițional**, al unui constructor
de câmp, și **al doilea element al perechii de opțiune**.

**Clichetul era 0 peste 125 de șiruri ASCII.** Și defectul fusese **numit în scris** de lotul 13.
*O descriere nu e o gardă; un gard cu domeniul greșit dă verde despre ce nu vede.*

Selecția pozițiilor noi e **structurală**: la poziția 5 se cere ca primul argument să arate a nume
de câmp (snake_case, minuscule), nu ca funcția să se cheme `C` — altfel gardul ar fi legat de un
singur fișier. Iar `cond: { val: [...] }` e **exclus anume**: perechea de acolo e o listă de
VALORI, nu o pereche valoare-etichetă. Excluderea n-a fost ghicită — instrumentul de măsură a
raportat `regularizare_incasat` drept text afișat, adică o valoare trimisă la server. *Fără ea,
gardul ar fi cerut diacritice pe logică: a greși în cealaltă direcție.*

**Calibrare**: cinci aserțiuni de dinți pe pozițiile noi (două care trebuie să prindă, trei care
trebuie să tacă), plus o **mutație pe fișierul real** — o etichetă întoarsă la ASCII face gardul
roșu, restaurată îl face verde. Clichetul rămâne **0**.

### 2. `core/scan_citate.py` — domeniul, luat din structură (R169)

Culegea obiecte `Temei` numai din `core/common`. Dar **decizia 73** cere ca temeiul să stea în
**modulul regulii** — deci *cu cât repo-ul urmează mai bine propria politică, cu atât gardul vede
mai puțin*. `TEMEI_291_5` (R151, scris cu o zi înainte, exact după regulă) nu era verificat de
nimeni.

Domeniul se ia acum din **structură**: se importă `core/*.py` (fără `test_*`/`scan_*`) și se
păstrează modulele care chiar au un `Temei` la nivel de modul. *O listă de nume ar fi îmbătrânit
exact ca `common`-ul singur — adică ar fi reintrodus același defect, cu un pas întârziere.*

Măsurat la lărgire: citări văzute **36 → 60**, verbatim **12 → 26**.
`VERBATIM_BASELINE` urcă **11 → 26**, cu motivul scris lângă cifră: *nu s-a scris nicio citare nouă,
s-a lărgit domeniul.* `test_fiecare_citare_are_text_si_url` a rămas verde la lărgire — deci în cele
24 nou-văzute nu era neglijență, ci orbire în scan.

### 3. `core/test_c7_periodicitate_trimestriala.py` — patru teste pentru R167

Trei pe refuz — cele două care poartă temeiul se compară cu **constanta pe care o folosește codul**
(`endswith`), iar cele din afara setului TVA se cer prin **egalitate** cu mesajul de bază, nu prin
absența unui subșir. Al patrulea e **anti-vacuu**: leagă citarea de corpus prin
`scan_citate._verbatim`, plus o calibrare pe un citat inventat, care trebuie să pice.

**A treia formă a lui.** Prima căuta `Articolul 322` în corpus și **ateriza în cuprins**, unde 322 e
urmat de 323. A doua, cu ancora pe titlul propriu, a fost prinsă de **clichetul `apare_oricum`**
(1222 → 1225): un `"șir" in fișier` nu deosebește „e acolo" de „e acolo din alt motiv". *Gardul care
păzește gărzile și-a făcut treaba pe gardul scris în aceeași oră.*

### 4. Un instrument de probă, reparat pe structură (R170)

`frontend_test/vizual/proba_operatiuni.py` nu e o gardă din suită, dar produce cifre care ajung în
registre. Enumerarea culegea butoanele vizibile și le filtra pe TEXT — `t.length > 46 → sari` —,
deci raporta **32** peste un registru de **34**. Trece pe `data-op`. *Un prag mai mare ar fi fost
același defect, amânat.*

## 06.09.2026 (2) — Două gărzi care păzesc câte o DECIZIE, nu doar un comportament

### `core/test_ajutor_periodicitate_tva.py` — aceeași alegere, același criteriu (R172)

Periodicitatea decontului de TVA se cere în două ecrane; criteriul art. 322 era scris într-unul
singur. Textul s-a copiat **verbatim**, iar gardul face din „verbatim" o proprietate a codului, nu a
copierii mele: extrage textul din amândouă prin **ancore de câmp** și cere **egalitate** pe forma
randată.

Nu caută conținutul pe care îl păzește — un gard care își caută propriul text trece dintr-un motiv
străin. Anti-vacuu: lungime peste 120 de caractere și **exact două** citări ale articolului, cerute
cu `count()`, nu cu apartenență; plus o probă că extragerea **crapă** dacă ancora dispare, în loc să
întoarcă șirul gol și să treacă verde. Mutație pe fișierul real: cinci cuvinte scoase → roșu.

### `test_R171_tiparul_LARG_de_puncte_nu_a_fost_adoptat` — o decizie de a NU face, ținută de o gardă

Extinderea lui `articol_in_act` a avut două forme candidate de punct, măsurate pe tot corpusul
**înainte** de a atinge instrumentul: cea îngustă (`9. - `) scoate din refuz **11** documente, cea
largă (`52. Text`) scoate **80** — printre ele descrieri de structură XML și enumerări din proză.
Față de 24 de citări cunoscute, a doua e disproporționată, deci nu s-a implementat.

**Partea care contează pentru registrul ăsta:** decizia nu e o propoziție într-un fișier, e o
aserțiune. Garda cere ca `d101_struct_anaf.txt` și `d112_struct_anaf.txt` să rămână CIOT. Probat
prin mutație: lărgind tiparul, cad **cinci** teste — trei dintre ele fiind chiar clichetele care
măsoară perechile. *O decizie de a nu extinde, scrisă doar în proză, se erodează la prima tură care
n-o citește.*

### Ce a mai învățat `articol_in_act`

**Puncte** (`pct. N`), **anexe** (`anexa N`) și **norme** (`norme art. N` — reuniunea punctelor care
aplică un articol din Codul fiscal). Dispecerul e pe **forma citării**, deci o citare de articol
simplu merge pe calea dinainte, neatinsă — și asta are proba ei. Anexa **nu** se ghicește din numele
fișierului: se cere ca antetul actului să spună el însuși „(Anexa nr. 2)". De-aia anexa 1 a lui
OMFP 2634/2015 rămâne CIOT deși fișierul se numește așa.

Efect măsurat: perechi NEGĂSIT **11 → 1**, CIOT **7 → 5**, GĂSIT **34 → 46**; alerte **0 → 0**.

<!-- INVENTAR-GARZI:START (generat de scripts/scan_garzi_inventar.py --md) -->

**522 gărzi și instrumente.** Afirmația e prima frază a docstringului fiecăruia — ce spune garda despre ea însăși, nu ce cred eu despre ea. Un `—` înseamnă că fișierul n-are docstring de modul, iar lipsa se vede în loc să se piardă.

### `core/` — 502

- `core/scan_afirmatii.py` — core/scan_afirmatii.py — cate AFIRMATII despre datele firmei sunt inca netipate? (P8, 21.08.2026)
- `core/scan_ancore.py` — SCANNER de ANCORE: un gard care caută un șir într-un fișier sursă îl găsește în COD, sau doar în
- `core/scan_cai_factura.py` — CÂTE CĂI POT NAȘTE O FACTURĂ — instrumentul (HHH1, 29.08.2026).
- `core/scan_camp_blocant.py` — CE OPREȘTE EFECTIV FIECARE GENERATOR DE DECLARAȚIE — instrumentul lui R93, 30.08.2026.
- `core/scan_citate.py` — SCANNER de CITĂRI VERIFICABILE: `text_citat` chiar există în documentul citat? (21.08.2026)
- `core/scan_conflicte_sursa.py` — core/scan_conflicte_sursa.py — INTERDICȚIA 58, partea nemăsurată: conflictele NEÎNREGISTRATE.
- `core/scan_constante.py` — SCANNER de constante fiscale NESURSATE din codul de PRODUCTIE (20.08.2026).
- `core/scan_data_curenta.py` — INTERDICȚIA 3 — «Un calcul fiscal care citește data curentă», măsurată.
- `core/scan_descarcare_muta.py` — [R131, 04.09.2026] INSTRUMENT: un `fetch` direct care ARUNCA motivul serverului.
- `core/scan_ecran_reguli.py` — Instrumentul celor două reguli de ecran scrise pe 28.08.2026 — E1 (două nume distincte) și
- `core/scan_garzi.py` — I1 — instrumentul pentru interdictiile 18 (garda isi ia dovada din proza) si 19 (garda raporteaza
- `core/scan_garzi_culegere.py` — Rafinarea sub-instrumentului B.
- `core/scan_garzi_pe_text.py` — Care gărzi asertează pe TEXT în loc de STRUCTURĂ — pe ASERȚIUNE, nu pe fișier.
- `core/scan_garzi_subiect.py` — Rafinarea sub-instrumentului A: se separa tiparele dupa CE CAUTA, nu dupa cum arata.
- `core/scan_js_texte.py` — SCANNER de FRAZE DE INTERFATA din JavaScript (23.08.2026) — instrumentul pentru interdictiile
- `core/scan_module_nelegate.py` — INSTRUMENT — module cu funcții publice și ZERO importatori în afara testelor.
- `core/scan_norma_implementare.py` — core/scan_norma_implementare.py — INTERDICȚIA 60: elementul care implementează o normă îi poartă
- `core/scan_pereche_act_articol.py` — DOCUMENTUL PE CARE ÎL CITEAZĂ UN TEMEI CONȚINE ARTICOLUL PE CARE ÎL NUMEȘTE?
- `core/scan_provenienta.py` — core/scan_provenienta.py — de unde vine fiecare fisier din corpus. (23.08.2026)
- `core/scan_refuz_tacut.py` — core/scan_refuz_tacut.py — cate refuzuri ale serverului nu ajung la om.
- `core/scan_respingeri.py` — core/scan_respingeri.py — ce coduri de respingere sunt CHIAR FOLOSITE in module?
- `core/scan_rol_pe_efect.py` — core/scan_rol_pe_efect.py — INSTRUMENT: ce face fiecare rută, ca să se poată cere rolul după
- `core/scan_simetrie_denumire.py` — Instrumentul simetriei de scriere a denumirii unei firme (R81, decis 28.08.2026).
- `core/scan_valoare_in_citat.py` — core/scan_valoare_in_citat.py — INTERDICȚIA 53: citatul conține VALOAREA pe care o justifică?
- `core/scan_valori_afisate.py` — Valori FISCALE scrise literal in TEXTUL AFISAT de ecrane.
- `core/test_11_deducere_copii_gard.py` — GARD #11: deducerea de 100 lei/copil (CF art.77 alin.(10) lit.b) NU se acorda tacit — art.77 alin.(12)-(13)
- `core/test_12_salariu_minim_luna.py` — GARD #12: CF art.77 alin.(3) teza finala — cand in aceeasi luna se aplica mai multe valori ale
- `core/test_a11y_contrast_tokens.py` — core/test_a11y_contrast_tokens.py — GARD: token-urile de culoare trec contrastul WCAG AA (4.5:1).
- `core/test_a11y_landmarks.py` — [Regula 6 + Regula 13] GARD LANDMARKS app-wide (18.08.2026).
- `core/test_a11y_touch_target.py` — [Regula 6] GARD touch-target (AA 2.5.8, 18.08.2026) - ratchet pe stil.css (fara browser, ruleaza in poarta).
- `core/test_absenta_nu_e_neaplicabil.py` — GARD DE CLASĂ (21.08.2026): „niciun X înregistrat" nu poate deveni „nu se datorează".
- `core/test_achizitii_factura.py` — NECONFORMITATE ACTIVA reparata (04.08): operatiunile de achizitie (achizitie_ic, achizitie_taxare_inversa)
- `core/test_acoperire_vizuala.py` — [Regula 14 + metoda-ca-poarta, cerut de Costin 19.08.2026] GARD: o schimbare de UI cere un scan
- `core/test_activare_firma_inactiva.py` — GARD [R83/JJ2, 28.08.2026]: reactivarea e posibilă, iar excepția rămâne LOCALĂ.
- `core/test_afirmatii.py` — GARD (P3, 21.08.2026): o afirmație despre datele firmei își declară FELUL și poartă câmpurile
- `core/test_afirmatii_tipate.py` — CLICHET: afirmațiile despre datele firmei nu mai pot fi proză. (P8, 21.08.2026)
- `core/test_agenda.py` — Garda anti-stale a agendei: pica daca TESTE.md a ramas in urma codului. Diferenta fata de DE_FACUT.md
- `core/test_ai_incredere.py` — —
- `core/test_ajutor_periodicitate_tva.py` — GARD [06.09.2026, cerut de Costin]: aceeași alegere, pusă în două ecrane, poartă ACELAȘI criteriu.
- `core/test_ajutor_prelogin_fallback.py` — GARD ajutor_prelogin: handlerul global al semnului "?" nu depinde DOAR de _navGlobal (shell
- `core/test_alerte_control_fiscal.py` — Teste gardian pentru alerte_control_fiscal — stratul pull->push al controlului fiscal.
- `core/test_amortizare_ecran_metoda.py` — GARD amortizare pe METODA (Q6+Q15, tura import 16.08.2026).
- `core/test_amprenta_declaratie.py` — core/test_amprenta_declaratie.py — GARD C3 (snapshot+hash): regenerare-diff prinde editarea retroactiva.
- `core/test_an_hardcodat.py` — Un AN scris literal intr-o cerere catre server ingheata ecranul in trecut.
- `core/test_ancore_in_cod.py` — GARD PESTE GĂRZI (21.08.2026): ancora unui gard trăiește în COD, nu în PROZĂ.
- `core/test_ancore_rute.py` — GARD [R80, 27.08.2026]: clasa de rute despre care detectorul din R70 nu poate afirma nimic
- `core/test_api_public.py` — —
- `core/test_aritmetica_in_prezentare.py` — GARD (interdicția 4): aritmetica fiscală din ecran nu diverge de cea din server.
- `core/test_artefacte_pastrate.py` — GARD [R45]: un artefact produs se păstrează, cu cele cinci câmpuri — și producerea lui e
- `core/test_audit_campuri_oficiale.py` — GARD AUDIT SEMANTIC — numele campurilor emise = campuri OFICIALE (01.08.2026, Conditia 2 Costin).
- `core/test_audit_preluare.py` — Teste gardian F183 — audit_preluare (nucleele PURE, date minime construite manual).
- `core/test_audit_schema.py` — Teste F165 — auditor conformitate schema tenant vs tenant_template.sql.
- `core/test_b3_owner_drepturi.py` — GARD B3: proprietarul cabinetului (admin_firma creat la înregistrare) primește drepturile
- `core/test_balanta_pe_ecran.py` — GARD — balanța se poate CITI, nu doar descărca; iar „se închide" nu se afirmă pe gol.
- `core/test_banca_parser.py` — Test parser extras bancar CSV: delimitator robust (fara csv.Sniffer),
- `core/test_banca_parser_mt940.py` — Test gardian parser MT940 (SWIFT Statement Message).
- `core/test_base_nula_generatoare.py` — Poarta bazei nule (A, 31.07.2026): FIECARE generator de declaratie are erori_generare() si un
- `core/test_baza_cm.py` — GARDĂ: baza de calcul a indemnizației CM vine din statele EMISE, nu din recalcul. (22.08.2026)
- `core/test_bilant_regcom_poarta.py` — core/test_bilant_regcom_poarta.py - GARD: bilant_api.erori_generare blocheaza generarea cand
- `core/test_c1_pontaj_neconfirmat_gri.py` — C1 (audit tenant_003): starea 'pontaj neconfirmat' pe Stat de plata e o stare de PERIOADA
- `core/test_c2_migrare_revenire_firma.py` — C2 (audit tenant_003): dupa salvarea unui strat de import (salariati, solduri, parteneri, asociati,
- `core/test_c4_model_csv.py` — C4 (audit tenant_003): fiecare strat de import cu fisier ofera 'Descarca model (CSV)' cu formatul REAL
- `core/test_c6_c5_motiv_acord.py` — GARD C6 + C5 (audit vizual tenant_003, 16.08.2026).
- `core/test_c7_periodicitate_trimestriala.py` — GARD C7 — generarea TVA-decont (d300/d394/d406) urmeaza periodicitatea EFECTIVA a firmei (tip_decont),
- `core/test_cai_creare_factura.py` — GARDA inventarului de căi prin care se naște o factură (HHH1). Instrumentul:
- `core/test_cai_fisiere_date.py` — GARD CLASA "cale de fisier construita relativ la radacina" (01.08.2026).
- `core/test_cale_a_doua.py` — GARD (20.08.2026): a doua cale nu poate fi mutată peste prima în tăcere.
- `core/test_camp_blocant.py` — GARDĂ [R93, 30.08.2026]: un câmp declarat OBLIGATORIU trebuie să OPREASCĂ generatorul, nu să
- `core/test_capturi_numite.py` — GARD [HH, 28.08.2026]: o captură comisă fără proprietar în registru pică poarta.
- `core/test_cartea_mare.py` — GARD — Cartea mare ajunge la om, și fișa își poartă temeiul de completitudine.
- `core/test_cashflow.py` — —
- `core/test_catch_vizibil.py` — GARD DEFECT-3 (08.08.2026): (A) frontend - un catch{} GOL care inghite un api.* transforma un 500 intr-o
- `core/test_categorie_marime.py` — GARD — categoria de mărime nu se rotunjește la „micro", și pragurile citează actul.
- `core/test_cauza_precisa_business.py` — GARD cauza_precisa: cand un verificator din control_incrucisat prinde o eroare de BUSINESS
- `core/test_chei_duplicate.py` — GARDĂ: o cheie care apare de două ori în același dicționar e o intrare MOARTĂ. (21.08.2026)
- `core/test_citate_verbatim.py` — CLICHET CARE CREȘTE (21.08.2026): numărul de citări verificabile mecanic nu mai scade.
- `core/test_cititor_js.py` — GARD [04.09.2026]: cititorul comun de JS nu poate orbi tacut peste cod real.
- `core/test_clasificator_alerte.py` — CLICHET: eticheta unei alerte e o PREDICȚIE confruntabilă, iar greșelile ei nu mai pot crește.
- `core/test_clichete_generate.py` — GARD [31.08.2026]: tabelul clichetelor vii din predare se RECALCULEAZĂ, nu se citează.
- `core/test_cm_episod.py` — GARD CM-episod: indemnizatia CM se calculeaza pe EPISOD, nu pe certificat izolat (OUG 158/2005
- `core/test_cnp_control.py` — GARD DEFECT-2 (07.08.2026): CNP la orice cale de intrare DIRECTA valideaza cifra de control,
- `core/test_coada_firma_exista.py` — GARD [R44]: o declarație nu poate intra în coadă legată de o firmă care nu există.
- `core/test_coada_gata_de_depus.py` — GARD [R41 partea II]: «gata de depus» are O SINGURĂ definiție, iar lista o poartă.
- `core/test_coada_vizualizare.py` — GARD (audit patru-ochi): coada de validare are TRASEU de VIZUALIZARE a conținutului. Fără el,
- `core/test_cod_boala_nomenclator.py` — GARDĂ: codul de indemnizație se ia din NOMENCLATORUL 9, nu din enumerarea XSD. (22.08.2026)
- `core/test_cod_partener.py` — GARD (prag 2, 23.08.2026): codul fiscal al partenerului se CERE la introducere.
- `core/test_coduri_cm_din_registru.py` — GARDĂ: codurile de concediu medical vin din registru, nu dintr-o listă scrisă în JS. (22.08.2026)
- `core/test_coerenta_salarii.py` — GARD [R33, decizia lui Costin 25.08.2026]: semnalul de coerență notă-vs-D112 apare LA PROPUNERE,
- `core/test_compara_ce_s_a_depus.py` — GARD — D112 ȘI D300 se confruntă cu ce s-a DEPUS, când s-a păstrat; altfel o spun.
- `core/test_comparatii_clasificate.py` — GARDA PE DIRECTIA INVERSA: o comparatie pe o valoare de registru e CLASIFICATA. (P11, 22.08.2026)
- `core/test_compozitie_fluturas.py` — GARD — compoziția netului ajunge CHIAR la om, și e o singură sursă pentru hârtie și pentru ecran.
- `core/test_conflicte_sursa.py` — GARDĂ pentru partea deschisă a interdicției 58 — conflictele NEÎNREGISTRATE între surse.
- `core/test_conformitate.py` — GARDĂ: fiecare interdicție din plan are secțiune în CONFORMITATE.md, completă. (22.08.2026)
- `core/test_constante_nesursate.py` — CLICHET (20.08.2026): clasa constantelor fiscale nesursate din PRODUCȚIE nu mai crește.
- `core/test_cont_din_corp_normalizat.py` — core/test_cont_din_corp_normalizat.py — un cont luat din CORPUL CERERII trece prin strip().
- `core/test_cont_venit_linie.py` — core/test_cont_venit_linie.py — #11: contul de venit stabilit PE LINIE de factura.
- `core/test_contare_automata.py` — GARDA contării automate a facturii — blocurile DDD (cheia), EEE (emisă), FFF (primită).
- `core/test_contract_ecran_ruta.py` — GARD: contractul ECRAN ↔ RUTĂ nu se rupe tăcut.
- `core/test_control_fiscal.py` — Teste pentru semaforul de conformare fiscala (control_fiscal_api v2).
- `core/test_control_fiscal_diacritice.py` — core/test_control_fiscal_diacritice.py — GARD: mesajele de VERDICT ale controlului fiscal
- `core/test_control_incrucisat.py` — Teste gardian pentru control_incrucisat.compara_tva (functia PURA).
- `core/test_control_incrucisat_wiring.py` — core/test_control_incrucisat_wiring.py — GARD end-to-end pentru verifica_tva (cablaj, nu logica pura).
- `core/test_control_reconciliere_vizibila.py` — core/test_control_reconciliere_vizibila.py — GARD pentru SUPRAFATA UNIFICATA de reconciliere
- `core/test_cor.py` — Teste gardian pentru F137 (nomenclator COR).
- `core/test_corpus_amprenta.py` — GARDĂ: amprentele corpusului se verifică, nu doar se scriu. (22.08.2026)
- `core/test_corpus_surse.py` — Corpus (2): cele TREI garzi peste registrul de temeiuri COTE + manifestul anaf_surse/INDEX.json.
- `core/test_cota_efect.py` — GOLDEN pe EFECT: ce cifră iese pe căile reparate la R26, nu ce cotă a intrat.
- `core/test_cota_fara_default.py` — GARD (R26): nicio funcție fiscală nu are cotă implicită, iar REFUZUL chiar se produce.
- `core/test_cota_fara_default_fallback.py` — GARD (R29): o cotă de TVA absentă nu se completează singură, în niciun limbaj și în nicio formă.
- `core/test_cron.py` — Teste core/cron.py — ambalajul joburilor de fundal.
- `core/test_cui_cnp_test_valid.py` — [Date de test — CUI/CNP verificate] GARD: un CUI/CNP folosit ca date de test VALIDE (`cui=`/`cnp="..."`)
- `core/test_curatenie.py` — GARD [03.09.2026]: ocolirea de curatenie se deschide din INDEX, si numai pentru curatenie.
- `core/test_d100.py` — Teste gardian pentru D100 - modulul a fost REFACUT complet 16.07.2026.
- `core/test_d100_cota.py` — d100: rata default micro(1%)/profit(16%) vine din cota (impozit_micro/impozit_profit), NU din literalul
- `core/test_d100_cui_checksum.py` — Gard T1 (CATALOG_INVALIDITATE.md, D100 #7/#11/#19): CUI-ul firmei trebuie validat de app
- `core/test_d100_fapt.py` — [Regula 13 + Regula 6] GARDA: D100 micro pe FAPT (baza de venituri), simetric cu d390_fapt/d112_fapt.
- `core/test_d100_pozitia_116.py` — GARDĂ DE AȘTEPTARE: poziția 116 e o absență DECLARATĂ, și se află când încetează să fie posibilă.
- `core/test_d100_profit_baza.py` — GARD D100 (16.08.2026, campanie rețeta D300, pas 5/8) — baza impozitului pe PROFIT reparata.
- `core/test_d100_reconciliere.py` — core/test_d100_reconciliere.py — gardul A DOUA CALE D100 (pas 4/4 lant reconciliere).
- `core/test_d100_scadenta_trimiv.py` — Gard scadenta trim IV D100 (sursa: anaf_surse/d100_struct_anaf.txt + validator DUK R15.1).
- `core/test_d100_trunchiere.py` — Gard T6 (CATALOG_INVALIDITATE.md, D100 #12): denumirea/adresa firmei care depaseste limita
- `core/test_d101.py` — Teste gardian D101 - RECONSTRUIT 01.08.2026 pe formularul OFICIAL (OPANAF 206/2025, D101_A600 v10,
- `core/test_d101_cod_obligatie_caen.py` — GARD (TURA 3, 10.08.2026): D101 respinge PRE-DUK cod_obligatie in afara nomenclatorului
- `core/test_d101_cui_checksum.py` — GARD T1 (LANT legislatie TURA 3, 10.08.2026): D101 valideaza cifra de control a CUI-ului
- `core/test_d101_imca_ca_precedent.py` — core/test_d101_imca_ca_precedent.py — gard D101 IMCA eligibilitate (C-4 transa 3).
- `core/test_d101_impozit_nededus.py` — GARD [02.09.2026, PRAG 1]: cheltuiala cu impozitul pe profit ramasa NEDEDUSA se SEMNALEAZA.
- `core/test_d101_nr_evid_poz12.py` — core/test_d101_nr_evid_poz12.py — gard: nr_evid poz.1-2 = '11' (OPANAF 206/2025).
- `core/test_d101_reconciliere.py` — core/test_d101_reconciliere.py — gardul A DOUA CALE D101 (05.08.2026, pas 5/6).
- `core/test_d101_sponsorizare_075.py` — GARD D101 (16.08.2026, campanie rețeta D300, pas 6/8) — sponsorizare: limita 0.75% cifra de afaceri.
- `core/test_d101_valori_pre_duk.py` — GARD (TURA 3, 10.08.2026): D101 surfaceaza PRE-DUK, cu motiv EXACT, valorile fiscale invalide
- `core/test_d104.py` — Teste D104 (distribuire intre asociati a veniturilor/cheltuielilor - asocieri fara personalitate juridica).
- `core/test_d107.py` — Teste D107 (informativa beneficiari sponsorizari / mecenat / burse private).
- `core/test_d107_formular.py` — [Regula 4 + Regula 6] GARDA: formularul D107 gol NU produce declaratie.
- `core/test_d110.py` — Teste D110 (regularizare/restituire impozit pe venit retinut la sursa).
- `core/test_d112.py` — Teste gardian pentru D112 - reparat 16.07.2026 dupa testul agregat pe toate 9
- `core/test_d112_asiguratd_zerobase.py` — [d112 asiguratD zero-base] Un certificat de concediu medical caruia ii lipseste un camp
- `core/test_d112_avantaje.py` — Sectiunea 8.3 avantaje D112 (C4): bilete de valoare defalcate pe tip (E3_10/72/74/75 + E3_60).
- `core/test_d112_cadou.py` — GARD D112 (16.08.2026, campanie rețeta D300, pas 4/8) — CADOU TAXABIL -> D112 (pierdere tacuta reparata).
- `core/test_d112_caen_codboala.py` — [catalog D112 2.1/2.3] caen out-of-enum + cod boala out-of-enum refuzate PRE-DUK.
- `core/test_d112_carantina_c2.py` — Gard: carantina (cod 07) emite TOATE cele 6 coloane ale randului C2 Rd2.2 (C2_211-216),
- `core/test_d112_cert_overflow.py` — [T6, catalog D112 4.1-4.3] serie/numar/diagnostic (D_1/D_2/D_23) NETRUNCHIATE -> hard-block la overflow.
- `core/test_d112_cnp_angajat.py` — [T1] CNP salariat + CUI firma pre-validate PRE-DUK (checksum offline, core.identitate).
- `core/test_d112_deducere_suplimentara.py` — GARD D112 (16.08.2026, Task 2 exhaustiv) — DEDUCEREA PERSONALA SUPLIMENTARA cablata.
- `core/test_d112_mesaje_afisate.py` — GARD d112_mesaje_afisate: mesajele de business ridicate cu `raise ValueError(...)` din d112.py
- `core/test_d112_nume_dataang.py` — [catalog D112 1.8/1.9] numeAsig gol + data_angajare NULL refuzate PRE-DUK.
- `core/test_d112_reconciliere.py` — core/test_d112_reconciliere.py — gardul A DOUA CALE D112 (05.08.2026, campanie pas 3/6).
- `core/test_d177.py` — Teste D177 (redirectionare impozit pe profit catre entitati nonprofit).
- `core/test_d177_formular.py` — [Regula 4 + Regula 6] GARDA: formularul D177 gol NU produce declaratie.
- `core/test_d1_import_integritate.py` — core/test_d1_import_integritate.py — GARD: importul de salariati BLOCHEAZA CNP invalid, NU sare tacut.
- `core/test_d205.py` — Teste gardian pentru D205 - REFACUT A DOUA OARA 16.07.2026.
- `core/test_d205_cifr_obligatoriu.py` — Gard D205: campurile OBLIGATORII pe beneficiar (cifR, den1) nu pot fi emise vide.
- `core/test_d205_cnp_checksum.py` — Gard D205 c1 (TEMA T1, CATALOG_INVALIDITATE.md): CNP beneficiar pre-validat pe CIFRA DE
- `core/test_d205_cnp_duplicat.py` — Gard D205 c3 (TEMA T1, CATALOG_INVALIDITATE.md): (tip_venit1+cifR) UNIC per declaratie.
- `core/test_d205_cota_2025.py` — GARD D205 (16.08.2026, campanie rețeta D300, pas 7/8) — cota impozitului pe dividende 2025 = 10%.
- `core/test_d205_cui_checksum.py` — Gard D205 c2 (TEMA T1, CATALOG_INVALIDITATE.md): CUI platitor pre-validat pe CIFRA DE CONTROL
- `core/test_d205_divid_platit.py` — Gard D205: divid_D (dividend DISTRIBUIT) vs. divid_P (dividend PLATIT) - model corect.
- `core/test_d205_imp_manual.py` — core/test_d205_imp_manual.py — GARD d1 (CATALOG_INVALIDITATE): consistenta interna imp1 pt.
- `core/test_d205_reconciliere.py` — core/test_d205_reconciliere.py — gardul A DOUA CALE D205 (05.08.2026, pas 6/6).
- `core/test_d205_rezid_derivat.py` — Gard D205: Rezid (2.Rezident/Nerezident) DERIVAT din identitate, nu hardcodat "1".
- `core/test_d207.py` — Teste D207 (informativa impozit retinut la sursa - beneficiari nerezidenti).
- `core/test_d207_formular.py` — [Regula 4 + Regula 6] GARDA: formularul D207 gol NU produce declaratie.
- `core/test_d212_an_verificat.py` — Fișa D212 se produce pe anul CERUT, pe plafoanele verificate ale anului — nu pe unul înghețat.
- `core/test_d212_reper.py` — D212: salariul minim REPER vine din cota() (nu literal 4050) -> dependenta D212->salariu_minim VIZIBILA
- `core/test_d220.py` — Teste D220 (venit estimat / norma de venit - persoane fizice).
- `core/test_d221.py` — Teste D221 (venituri din activitati agricole impuse pe norme de venit - persoane fizice/asocieri).
- `core/test_d223.py` — Teste D223 (venituri estimate pentru asocieri fara personalitate juridica / transparenta fiscala).
- `core/test_d230.py` — Teste D230 (redirectionare pana la 3,5% din impozit catre ONG).
- `core/test_d300.py` — Teste gardian pentru D300 — lantul de calcul R27->R42 lipsea complet.
- `core/test_d300_b1_rutare.py` — Gard B1-B4 (15.08.2026): comportamentele NOI ale remedierii D300 nu aveau test de
- `core/test_d300_d394_paritate.py` — Gard de PARITATE d300 <-> d394 pe TVA pe cota. Ambele se depun la ANAF pe aceeasi luna.
- `core/test_d300_d394_trimestrial.py` — core/test_d300_d394_trimestrial.py — gard PERIOADA FISCALA TVA (06.08.2026, C-4 transa 2).
- `core/test_d300_drop_taxabil.py` — Gard: liniile TAXABILE cu cotă fără rând D300 valid pentru perioadă (ex. 19/5%) NU
- `core/test_d300_forfait_agricol.py` — core/test_d300_forfait_agricol.py — gard TVA ORFAN din antet la achizitii primite
- `core/test_d300_profil_identitate.py` — TURA 3 / T1: erori_generare verifica pana acum doar NON-GOL pentru cui/caen/pro_rata.
- `core/test_d300_r25_r12.py` — TURA 4 (CR-5/T8): oglinda rd.12 <-> rd.25 la taxare inversa PRIMITA (masuri de simplificare).
- `core/test_d300_reconciliere.py` — core/test_d300_reconciliere.py — gardul A DOUA CALE D300 (05.08.2026).
- `core/test_d300_taxare_inversa_beneficiar.py` — Gard Task2 (10.08.2026): achizitiile cu taxare inversa PRIMITA nu mai dispar tacit din D300.
- `core/test_d300_valideaza_wired.py` — TURA 3 / T2: valideaza(res) era COD MORT. genereaza() chema doar erori_generare(prof),
- `core/test_d300_zero_rate.py` — Gard Task1 (10.08.2026): liniile cu cotă 0% NU mai dispar tacit din D300.
- `core/test_d301.py` — Teste D301 — ancorarea nomenclatoarelor pe VALIDATORUL instalat (nu pe pdf-ul de structura 2013).
- `core/test_d301_an_guard.py` — TURA 3: genereaza() gardeaza doar LUNA (1..12), nu ANUL. D301 (formularul 301) se depune din
- `core/test_d301_cif_checksum.py` — TURA 3 / T1: CIF checksum + lungime NICIODATA pre-validat de app. erori_generare verifica doar
- `core/test_d301_coercitie_tacita.py` — TURA 3 / T3: coercitie TACITA enum-necunoscut -> default. calcul_d301 face `int(tip or 1)`
- `core/test_d301_cota.py` — Gard period-aware pe cota de TVA oferita la introducerea operatiunilor D301.
- `core/test_d301_curs.py` — Gard anti-fabricare a cursului de schimb in D301 (cluster "baza = val x curs").
- `core/test_d301_data_doc.py` — GARD: D301 data_doc emis in formatul OFICIAL ANAF ZZ.LL.AAAA (anaf_surse/d301_struct_anaf.txt poz.35, C(10)).
- `core/test_d301_nr_doc_c20.py` — TURA 3 / T6: nr_doc > C(20) passthrough NETRUNCHIAT nicaieri (leak pur). DUK NU impune lungimea,
- `core/test_d301_op_cere_neplatitor.py` — GARD (audit tenant_006): ecranul D301 (adauga operatiune -> d301_operatiuni) NU accepta operatiuni
- `core/test_d301_pers_inreg.py` — Gard pers_inreg (D301) — neconformitate: pers_inreg era hardcodat literal "1".
- `core/test_d301_reconciliere.py` — core/test_d301_reconciliere.py — gardul A DOUA CALE D301 (10.08.2026).
- `core/test_d301_rollup.py` — Regresie D301: serviciile intracomunitare (tip 5 = sectiunea 4.1) se preiau DIN sectiunea 4.
- `core/test_d301_temei_307_intrare.py` — GARD (audit tenant_006, temei_307): introducerea unei operatiuni D301 tip 4 (art. 307 alin. 3/5/6)
- `core/test_d301_valideaza_wired.py` — TURA 3 / T2: valideaza(res) era COD MORT. genereaza() chema doar erori_generare(prof), deci
- `core/test_d301_vies_la_introducere.py` — GARD (audit 006/R24.1, clasa preview↔salvare): la introducerea unei operațiuni D301 cu furnizor UE,
- `core/test_d301_zero_ruptura.py` — GARD D301 (16.08.2026, campanie rețeta D300, pas 3/8) — trei remedieri, verificate la sursă
- `core/test_d307.py` — Teste D307 (ajustare/corectie/regularizare TVA).
- `core/test_d307_formular.py` — [Regula 4 + Regula 6] GARDA: formularul D307 gol NU produce declaratie.
- `core/test_d311.py` — Teste D311 (TVA in situatii speciale dupa anularea codului de TVA).
- `core/test_d311_formular.py` — [Regula 4 + Regula 6] GARDA: formularul D311 gol NU produce declaratie.
- `core/test_d390.py` — Teste gardian pentru D390 — modulul n-avea niciunul.
- `core/test_d390_art317.py` — #4 (plimbare vizuala 14.08.2026): verdictul D390 la neplatitorul cu operatiuni IC era permanent-fals
- `core/test_d390_autoderivare.py` — [Regula 5 + Regula 10 + Regula 6] GARDA: auto-derivarea d301_operatiuni -> D390 (cod A/S).
- `core/test_d390_checksum_manual.py` — core/test_d390_checksum_manual.py — GARD: checksum-ul VIES se aplica pe TOATE liniile D390,
- `core/test_d390_d301_acoperire.py` — core/test_d390_d301_acoperire.py — ACOPERIRE C-4 transa 2, items (b) si (c).
- `core/test_d390_d301_semnal.py` — [Regula 4 + Regula 13] GARDA: D390 pe zero SEMNALEAZA achizitiile din d301_operatiuni.
- `core/test_d390_diagnostic_partener.py` — [TURA 3] D390 - diagnoza EU-VAT PER-PARTENER, pre-DUK (T1/T3/T2/T6).
- `core/test_d390_dubla_si_primita_fara_cui.py` — GARD (audit tenant_006): avertismente D390 pe două goluri reale de raportare.
- `core/test_d390_nota1.py` — GARD D390 (16.08.2026, campanie rețeta D300, pas 2/8) — trei remedieri:
- `core/test_d390_reconciliere.py` — core/test_d390_reconciliere.py — gardul A DOUA CALE D390 (10.08.2026).
- `core/test_d390_rotunjire_coerenta.py` — Gard D390 (10.08.2026): rezumatul (bazaL..bazaR, total_baza) trebuie sa fie suma bazelor
- `core/test_d390_ziua15.py` — D390 art.284 "ziua 15" (A2): incadrarea in perioada pe EXIGIBILITATE = MIN(data_emitere, ziua 15 a lunii
- `core/test_d394.py` — Teste gardian pentru d394 (functiile PURE).
- `core/test_d394_codpr_cereale.py` — GARD D394 codPR cereale (10.08.2026) - SPEC OFICIAL anaf_surse/d394_struct_anaf.txt poz.68-70:
- `core/test_d394_cuip_checksum.py` — GARD neconformitate T1/G-c1 (CATALOG_INVALIDITATE.md): checksum-ul CUI/CIF al partenerului NU
- `core/test_d394_manual_codpr.py` — GARD neconformitate: operatiune MANUALA C/V (art.331) trebuie sa emita op11(codPR).
- `core/test_d394_nrfact_multicota.py` — GARD D394 (16.08.2026, campanie rețeta D300) — doua neconformitati reparate:
- `core/test_d394_op1_fara_op11.py` — GARD neconformitate T4/G-bc1 + G-bc2 (CATALOG_INVALIDITATE.md): "avertizeaza-dar-emite-invalid".
- `core/test_d394_partener_cui_litere.py` — GARD neconformitate T3/G-d1 (CATALOG_INVALIDITATE.md - cea mai grava D394): un CUI de partener
- `core/test_d394_prsafiliat.py` — GARD: prsAfiliat (poz.6.a) trebuie sa fie SURSAT din profil, nu hardcodat "0".
- `core/test_d394_pull_ti_fara_linii.py` — GARD D394 - pull() nu mai da NameError la achizitie cu taxare inversa fara linii (10.08.2026).
- `core/test_d394_reconciliere.py` — core/test_d394_reconciliere.py — gardul A DOUA CALE D394 (05.08.2026, campanie pas 2/6).
- `core/test_d394_trimestrial_perioada.py` — GARD (audit tenant_003, misdiagnostic 'D394 perioada septembrie + cifre necorespunzatoare'):
- `core/test_d394_v_taxare_inversa_cota0.py` — GARD D394 - V (livrare cu taxare inversa) trebuie emis cu cota 0 (10.08.2026).
- `core/test_d402.py` — Teste D402 (declaratie informativa DAC1 - venituri salariale/asimilate platite in Romania
- `core/test_d406.py` — —
- `core/test_d406_accounttype_wired.py` — GARD D406 AccountType cablat in genereaza (T2, CATALOG_INVALIDITATE.md; 10.08.2026).
- `core/test_d406_active_duk.py` — Proba DUK pe tenant_013 pentru amortizarea D406/SAF-T pe metoda.
- `core/test_d406_amortizare.py` — Golden pe motorul de amortizare D406/SAF-T (core/d406_active.py), pe metoda.
- `core/test_d406_cnp_tert.py` — GARD D406 CNP in tert_cui -> tipul 03 (E3/E4, CATALOG_INVALIDITATE.md; 10.08.2026).
- `core/test_d406_coercitie_t3.py` — GARD D406 coercitie TACITA enum-necunoscut (T3, CATALOG_INVALIDITATE.md; 10.08.2026).
- `core/test_d406_cui_checksum.py` — GARD D406 checksum CUI/CNP partener + firma proprie (T1, CATALOG_INVALIDITATE.md; 10.08.2026).
- `core/test_d406_fereastra.py` — Garda R165/R166 — D406 raporteaza perioada pe care o ACOPERA, si o declara asa cum e.
- `core/test_d406_jurnal_origine.py` — GARD (R22, prag 1): `JournalID` din D406 poartă jurnalul de ORIGINE, nu o constantă.
- `core/test_d406_master_pf.py` — GARD D406 partener PF fara cod fiscal in MASTER (10.08.2026): un partener persoana
- `core/test_d406_partener_id_neconform.py` — Gard: D406 nu emite ID BRUT de nomenclator ca identitate de partener SAF-T.
- `core/test_d406_payment_method.py` — Gard: PaymentMethod (SD Payment) trebuie sa fie un cod de DOUA CIFRE din nomenclatorul
- `core/test_d406_reconciliere.py` — core/test_d406_reconciliere.py — gardul A DOUA CALE D406/SAF-T (05.08.2026, campanie pas 4/6).
- `core/test_d406_reg_number_header.py` — GARD D406 (16.08.2026, campanie rețeta D300, pas 8/8) — RegistrationNumber firma proprie (header) cu
- `core/test_d406_restrictii_metode.py` — Restrictii pe categorii de active la alegerea metodei de amortizare (CF art.28 alin.5 + alin.8^1).
- `core/test_d406_supplierid.py` — GARD D406 SupplierID (10.08.2026): SupplierID/CustomerID pe factura NU poate fi "0".
- `core/test_d406_taxcode_nota.py` — GARD D406 TaxCode nota contabila (10.08.2026): pe liniile din GeneralLedgerEntries
- `core/test_d710.py` — Teste gardian pentru D710 (Declaratie rectificativa - corectie D100).
- `core/test_d710_cod131_132.py` — GARD TURA 3 — D710 C5: cod_oblig 131/132 cer Data_I (data incheierii exercitiului financiar) pe care
- `core/test_d710_formular.py` — [Regula 4 + Regula 6] GARDA: formularul D710 gol NU produce declaratie.
- `core/test_d710_nomenclator_manual.py` — GARD TURA 3 — D710: valorile MANUALE cod_oblig / cod_bugetar / cota / scadenta erau acceptate raw si
- `core/test_d710_suma_ded.py` — Gardian J1/T7 (TURA 4): DEDUCEREA (suma_ded) in D710 - inchidere gol RECONCILIERE.
- `core/test_d710_sume_negative.py` — GARD TURA 3 — D710 B4: sume negative in obligatia manuala. PE HEAD (8b74ccb) o suma negativa era emisa
- `core/test_d710_t1_cui.py` — GARD TURA 3 — D710 T1: checksum CUI al firmei validat PRE-DUK in erori_generare (sursa canonica
- `core/test_d710_t9_parsare.py` — GARD TURA 3 — D710 T9: parsarea obligatiei MANUALE (contabil) ridica ValueError CLAR (camp + valoare)
- `core/test_data_curenta.py` — GARD [01.09.2026, interdicția 3]: un calcul fiscal nu citește data curentă în tăcere.
- `core/test_date_firma_alege_placeholder.py` — core/test_date_firma_alege_placeholder.py — GARD (jumatatea frontend a defectului „default fabricat"
- `core/test_datorie.py` — REGISTRUL DE DATORIE — ce e amanat, ca test care ruleaza.
- `core/test_declarant_oblig.py` — core/test_declarant_oblig.py — GARD: declarantul (nume + functie) e OBLIGATORIU in profil - se cere
- `core/test_declarant_warn.py` — core/test_declarant_warn.py — GARD: cand declarantul lipseste din profil, generatoarele AVERTIZEAZA
- `core/test_declaratii_componente.py` — GARD — fiecare dintre cele nouă declarații ori își arată componentele, ori spune de ce nu poate.
- `core/test_declaratii_depuse_randuri.py` — Teste F163v2 — persistarea declaratiei depuse (xml + randuri) in public.declaratii_depuse.
- `core/test_declaratii_lot2_duk.py` — Lot 2 de declaratii noi (10): proba DUK pe fiecare, cu validatorul OFICIAL ANAF.
- `core/test_declaratii_lot3_duk.py` — Lot 3 de declaratii noi (6): proba DUK pe fiecare, cu validatorul OFICIAL ANAF.
- `core/test_declaratii_lot4_duk.py` — Lot 4 de declaratii noi (6): proba DUK pe fiecare, cu validatorul OFICIAL ANAF.
- `core/test_declaratii_lot5_duk.py` — Lot 5 de declaratii noi (6): proba DUK pe fiecare (validator OFICIAL ANAF).
- `core/test_declaratii_lot6_duk.py` — Lot 6 (final): Declaratia Unica D212, proba DUK cu validatorul OFICIAL ANAF.
- `core/test_deconturi.py` — Gard pe plafonul neimpozabil al diurnei (motor pur core/deconturi.py).
- `core/test_deducere_generalizare.py` — GARD Fix 3 (Task 2 D112): GENERALIZAREA clasei fix 1 (deducere necablata) la CEILALTI apelanti de productie
- `core/test_dependenti_act.py` — GARDĂ pentru interdicția 61 — lista dependenților unui articol, generabilă la cerere.
- `core/test_depunere_contrazice.py` — GARD R6 (21.08.2026): o depunere care contrazice un „nu se datorează" nu mai e invizibilă.
- `core/test_descarcare_muta.py` — [R131, 04.09.2026] GARD: o descarcare care esueaza spune DE CE.
- `core/test_diacritice_afisate.py` — core/test_diacritice_afisate.py — GARD DE DIACRITICE PE TEXTUL AFIȘAT (#4, criteriul lui Costin).
- `core/test_dialog_nativ_frontend.py` — GARD (09.08.2026): dialoguri native alert()/prompt()/confirm() INTERZISE in TOT frontendul (DS cap.5:
- `core/test_document_fara_administrator.py` — GARD [R66 (c), 26.08.2026]: un document care tipărește numele administratorului nu se produce
- `core/test_document_ref_necunoscut.py` — GARD — un `0` care nu poate fi altceva decât `0` nu susține nicio cauză afirmată.
- `core/test_ds_verificator.py` — GARDĂ [R103, 30.08.2026]: legătura `DESIGN_SYSTEM.md` → `verificator_conformitate.py` nu mai
- `core/test_duk.py` — Teste gardian pentru duk (partea pura, fara java).
- `core/test_duk_severitate.py` — GARD A2: DUK distinge atentionare (A:, NU blocheaza depunerea) de eroare (E:, blocheaza). Fixturi REALE
- `core/test_echilibru_legat.py` — core/test_echilibru_legat.py — GARDA R33 varianta b'' (26.08.2026).
- `core/test_echilibru_perioada.py` — core/test_echilibru_perioada.py — GARD C3 (integritate in timp): partida dubla pe perioada + orfani.
- `core/test_edge_canonic_head.py` — GARD edge SEO/crawler (_edge_canonic_head din main.py):
- `core/test_efactura_send.py` — Teste generator e-Factura SEND (core/efactura_send.py) — pe date minime construite
- `core/test_emitere_randuri_dinamice.py` — GARD cap.24 batch 3b — randuri dinamice emitere factura, re-rulate IN POARTA prin chromium headless.
- `core/test_esec_trimitere_email.py` — GARD [R73, 27.08.2026]: un eșec de trimitere a emailului nu se mai poate stinge tăcut.
- `core/test_eticheta_conturi_ecran.py` — Eticheta din ECRAN și conturile din BACKEND nu pot diverge tăcut.
- `core/test_etransport_randuri_dinamice.py` — GARD cap.24 batch 3a — randuri dinamice e-Transport, re-rulate in POARTA prin chromium headless.
- `core/test_etransport_send.py` — Teste core/etransport_send.py (F121) — pe MOCK, niciodata pe ANAF real.
- `core/test_eveniment_public.py` — Garda de CONFIDENTIALITATE pentru analytics public (public.eveniment_public).
- `core/test_exces_vacanta_d112.py` — D3 (02.08.2026): excesul de tichete de vacanta peste plafonul anual (6 sm) = venit salarial in BRUTUL
- `core/test_existenta_activitate.py` — [Regula 13 + Regula 6] GARDA: existenta_firma_an numara TOATA activitatea reala datata.
- `core/test_expirare_cote.py` — Teste RAPORT INTERN de vechime a confirmarii (core/expirare_cote.py, Modelul de temei 01.08 pct.2).
- `core/test_expirare_cote_de_baza.py` — Gard: modelul de temei pe data_out (Modelul de temei 01.08, pct.1+2).
- `core/test_export_cota.py` — Export/PDF: linie fara cota TVA = intrare INCOMPLETA -> eroare, NU cota 0 (scutit) ghicita.
- `core/test_export_winmentor.py` — Teste F187 — export WinMENTOR. Verificare contra spec-ului OFICIAL (Facturi clienti.pdf Rev.1.2 +
- `core/test_facturi_recurente_randuri_dinamice.py` — GARD cap.24 — randuri dinamice facturi RECURENTE (sablon), re-rulate IN POARTA prin chromium headless.
- `core/test_faptul_bate_vectorul.py` — GARD (21.08.2026): FAPTUL BATE VECTORUL în selectorul de declarații, iar „lună închisă" nu mai
- `core/test_fara_probe_imagine.py` — GARDĂ (03.09.2026): **un fișier imagine nu mai intră în repo ca probă vizuală**, și **niciun cod
- `core/test_fereastra_focusabila.py` — [a11y WCAG 2.1.1 / Regula 14] GARD: corpul modal .fereastra-corp e focusabil din tastatura.
- `core/test_fieldmark.py` — [Regula 13 + Regula 6] GARDA: marcajul vizual al campului cu eroare de validare (Regula 14 pct.4).
- `core/test_firma_profil_api.py` — Teste pure pentru helper-ele F180 (regim TVA vs ANAF) din firma_profil_api.
- `core/test_fisa_cont.py` — GARD: Fișa de cont pentru operațiuni diverse produce ce cere norma, nu o balanță deghizată.
- `core/test_fixturi_shared_period.py` — [Verificare funcțională reală] GARD: o fixtură de test care scrie într-un tabel PARTAJAT period-keyed
- `core/test_flag_constatare.py` — GARDĂ: constatarea din semaforul de portofoliu e o afirmație VALIDĂ, pe toate cele trei stări.
- `core/test_fluturas_egal_stat.py` — GARDĂ: fluturașul TIPĂREȘTE statul, nu îl recalculează. (21.08.2026)
- `core/test_fluturas_eticheta.py` — O eticheta de pe fluturas nu are voie sa numeasca un lucru si sa arate altul.
- `core/test_frecventa_document_care_raspunde.py` — GARD [01.09.2026, R111]: frecvența nu se citește dintr-un document care nu poate răspunde.
- `core/test_front_e_editare_identitate.py` — core/test_front_e_editare_identitate.py — GARD Front E: identitatea/contractul salariatului
- `core/test_g10_eroare_langa_camp.py` — GARD G10 (DESIGN_SYSTEM cap.6 v2.30) — rollout mecanism A (eroare LANGA campul care a cauzat-o, via
- `core/test_g1_cod_mesaj.py` — core/test_g1_cod_mesaj.py — G1: codul-mașină de business nu mai ajunge brut la utilizator.
- `core/test_g9_oblig_backend.py` — core/test_g9_oblig_backend.py — GARD care ÎNCHIDE CLASA (nu doar instanțele): un câmp marcat
- `core/test_gard_masca_zero.py` — core/test_gard_masca_zero.py — GARD C5 (clasa oarba "mascarea erorii / zero tacut", GARZI cat.0).
- `core/test_garzi_inventar.py` — GARD [28.08.2026]: inventarul gărzilor din `GARZI.md` nu poate rămâne în urma codului.
- `core/test_garzi_mesaje_afisabile.py` — core/test_garzi_mesaje_afisabile.py — GARD STRUCTURAL (C-5, pct.5 Costin): niciun test nu asertează
- `core/test_garzi_pe_text.py` — GARD PESTE GĂRZI — o gardă asertează pe STRUCTURĂ, nu pe text.
- `core/test_garzi_tacere_ui.py` — core/test_garzi_tacere_ui.py — GARDURI STATICE anti tacere-la-esec + info-leak in UI (JS).
- `core/test_get_fara_scriere.py` — GARD (20.08.2026): o rută GET nu scrie în starea de business. GET trebuie să fie SAFE (RFC 9110 §9.2.1).
- `core/test_ghiduri_servite.py` — Gard: ghid/ e SURSA UNICA a paginilor publice de ghid.
- `core/test_golden_xsd.py` — GARD completitudine golden-XSD: fiecare XSD de declaratie din corpus (anaf_surse/*.xsd +
- `core/test_graf_clustere_proprietar.py` — GARD (R19): o funcție partajată între clustere NU e proprietatea niciunuia.
- `core/test_graf_temei.py` — Graful de dependente fiscale extras din cod (core/graf_temei.py, Modelul de temei 01.08 pct.3).
- `core/test_granite_cota.py` — Granite API — cota TVA lipsa = intrare INCOMPLETA -> eroare, nu default 21 ghicit.
- `core/test_harta_casete.py` — GARD — COMPARATORUL. Confruntă ce s-a randat cu ce spune harta că trebuie randat.
- `core/test_harta_ecrane.py` — [Regula 13 PERIMETRU + #3 din roadmap] GARD: harta ecranelor nu crește TĂCUT. Fiecare ecran de firmă
- `core/test_harta_temei.py` — GARD (R5, 20.08.2026): în harta casetelor, temeiul legal nu se amestecă cu regula de produs.
- `core/test_heartbeat.py` — Gard: heartbeat pentru joburile de fundal — jobul care NU porneste deloc.
- `core/test_identitate.py` — Gard pe validatorul de identitate PARTAJAT (core/identitate.py, LANT legislatie TURA 3, 10.08.2026).
- `core/test_identitate_acte.py` — GARD — un act din corpus e ACTUL pe care îl spune numele lui, și e adus o singură dată.
- `core/test_import_backend_corect.py` — GARD lot1 corectitudine import: preview↔salvare aliniate pe validarea reala + fara default tacit.
- `core/test_import_mesaje_afisate.py` — GARD import_mesaje_afisate: mesajele ridicate cu `raise ValueError/TypeError` din parserele de
- `core/test_import_migrare.py` — Teste gardian pentru importurile de migrare care nu aveau NICIUNA.
- `core/test_import_migrare_valideaza.py` — Gard COMPORTAMENTAL (unit) pentru clasa 'importul accepta orice fisier si declara succes'
- `core/test_import_motiv_vizibil.py` — [Regula 6 + Regula 14] GARD: motivul de refuz din preview-ul de IMPORT e VIZIBIL, nu doar in `title`.
- `core/test_importuri_nefolosite.py` — CLICHET pe importurile nefolosite (F401). Nu blochează codul existent; oprește creșterea.
- `core/test_impozit_dividend.py` — PAS 0 versionare formule: impozitul pe dividende (regim dividende + lichidare) = COTE period-aware,
- `core/test_inchidere_luna.py` — ACTUL DE ÎNCHIDERE a lunii pe domeniul `facturi` (21.08.2026) — DESIGN_SYSTEM cap.23.
- `core/test_infra_vizuala.py` — GARDĂ: infrastructura de testare vizuală (frontend_test/vizual) nu poate dispărea tăcut.
- `core/test_inlocuire_afirmata.py` — GARD [YY/METODA §28, 28.08.2026]: o inlocuire de text intr-un document AFIRMA ca a gasit potrivirea.
- `core/test_instrumente_roadmap.py` — [metoda-ca-poarta] GARD: INSTRUMENTE_ROADMAP.md nu minte — un instrument marcat CONSTRUIT trebuie sa
- `core/test_interpretare.py` — GARDĂ: o interpretare e un OBIECT declarabil, cu variantele obligatorii. (P11, 22.08.2026)
- `core/test_inventar_a.py` — Inventar A generat PARTIAL din common.COTE + overlay separat pentru judecatile umane.
- `core/test_inventar_randuri_dinamice.py` — GARD cap.24 regula 2 — inventar (sectiuneaCV), re-rulat IN POARTA prin chromium headless.
- `core/test_izolare_api_key.py` — core/test_izolare_api_key.py — GARD de izolare pe CHEIE API (namespace /api/v1/firme/{tenant_id}).
- `core/test_izolare_incrucisata.py` — Proba DINAMICA de izolare tenanti: acces incrucisat real prin HTTP.
- `core/test_izolare_raportari.py` — core/test_izolare_raportari.py — GARD structural de izolare pe /raportari (apararea de DATE, nu doar ruta).
- `core/test_izolare_structurala.py` — core/test_izolare_structurala.py — GARD STRUCTURAL de izolare (C-5 P1, clasele 5+6).
- `core/test_joburi_supravegheate.py` — GARD [R74, 27.08.2026]: lista deadman-ului se compară cu SISTEMUL, nu cu o copie a ei.
- `core/test_jurnal_refuz.py` — GARDĂ: calea jurnalului refuză cu TEMEI, și confruntă conturile cu planul firmei.
- `core/test_kpi_client.py` — —
- `core/test_limita_text_anaf.py` — Gard: niciun atribut de text din declaratii nu depaseste limita ANAF (75 caractere).
- `core/test_limite_verificarii.py` — GARD (P4, 21.08.2026): „Ce nu poate spune verificarea asta" e PERMANENTĂ și se COMPUNE.
- `core/test_lista3.py` — GARDĂ: titlul listei 3 e GENERAT, nu scris — a doua aplicare a regulii, pe propria listă.
- `core/test_live_accesibil.py` — [#6 plimbare 14.08.2026 / regula 9] Garda: o declaratie e LIVE DOAR daca e accesibila in selectorul UI
- `core/test_login_proba_metoda.py` — GARD "gaura de metoda" (09.08.2026, cerut de Costin): a PROBA un cont = prin calea de autentificare
- `core/test_manual_decl_cere_eligibil.py` — GARD (sweep audit tenant_006): rutele de intrare MANUALĂ de declarație verifică eligibilitatea față
- `core/test_masti.py` — Garda: nicio masca TACUTA peste un query.
- `core/test_matrice_control_fiscal.py` — Matrice de stari pe control fiscal - PURA, aserții pe FORMĂ (nu valori). NU testeaza UI, NU repara.
- `core/test_mesaj_commit_curat.py` — GARD [Z, 28.08.2026]: mesajul de commit nu poate purta octeți de control.
- `core/test_mesaje_fara_camp_intern.py` — core/test_mesaje_fara_camp_intern.py — GARD: mesaj user-facing FĂRĂ nume intern de câmp.
- `core/test_mesaje_generare_fara_camp_intern.py` — GARD (F5/Regula 14.4): mesajele de VALIDARE ale generatoarelor de declaratii (functiile
- `core/test_mesaje_valueerror_publicat.py` — GARD (D7/D8/D9, 20.08.2026): mesajele `ValueError` PUBLICATE contabilului sunt în limba lui.
- `core/test_metoda_vie.py` — GARD (20.08.2026): METODA_VERIFICARE.md nu descrie o lume care nu mai există.
- `core/test_migrare_cnp_ingrijit.py` — core/test_migrare_cnp_ingrijit.py — gard: fiecare schema de TENANT are coloana cnp_ingrijit (D_8/D_8a).
- `core/test_migrare_ignorate_vizibil.py` — [Regula 6 + Regula 14.4] GARD: intrarile ignorate la validarea CUI (strat firme) ajung VIZIBIL pe ecran.
- `core/test_migrare_program_national_cm.py` — core/test_migrare_program_national_cm.py — gard: fiecare schema de tenant are concedii_medicale.program_national (D_9a).
- `core/test_mijloace_fixe_import_categorie.py` — Import mijloace fixe: cont de imobilizare lipsă NU se mai completează tacit cu 2131.
- `core/test_module_nelegate.py` — CLICHET — module de producție din `core/` pe care nu le cheamă nimeni în afara testelor.
- `core/test_monitor_fiscal.py` — —
- `core/test_mutant_zero.py` — core/test_mutant_zero.py — GARD C5 (rest): mutant-zero pe generatoare.
- `core/test_nir_randuri_dinamice.py` — GARD cap.24 — randuri dinamice NIR (ecranStocuri), re-rulate IN POARTA prin chromium headless.
- `core/test_nomenclatoare_ancorate.py` — GARD DE CLASA (04.08.2026): fiecare nomenclator care ajunge la ANAF e PROBAT pe validatorul INSTALAT.
- `core/test_nomenclator_pe_norma.py` — GARD [C6, 25.08.2026]: un nomenclator se ia din NORMĂ; validatorul e constrângere, nu sursă.
- `core/test_norma_implementare.py` — GARDĂ pentru interdicția 60 — elementul care implementează o normă îi poartă articolul?
- `core/test_note_explicative_micro.py` — GARDĂ: ce datorează o microentitate la notele explicative — și de ce NU e „nimic".
- `core/test_numar_fiscal.py` — Teste core.common.numar_fiscal + garda pe generatoarele de declaratii.
- `core/test_nume_anaf.py` — GARD [27.08.2026]: denumirea de la ANAF se păstrează lângă cea editabilă, cu data ei.
- `core/test_nume_firma_unic.py` — GARD [27.08.2026]: două firme cu același nume, în același cabinet, sunt un fapt imposibil.
- `core/test_numere.py` — Teste gardian pentru core/numere.py — sursa UNICA de parsare a numerelor.
- `core/test_octeti_invizibili.py` — GARD (21.08.2026): niciun octet de CONTROL invizibil în codul sursă.
- `core/test_onboarding_ux.py` — GARD onboarding_ux: fereastra de bun venit (salut inaintea Suportului, firul spune unde se face
- `core/test_operatiuni_speciale.py` — Teste gardian pentru operatiuni speciale P2.7 (leasing, avansuri,
- `core/test_pas2_panou_editabil_pe_eroare.py` — GARD anti-regresie CHICKEN-AND-EGG (16.08.2026) — pas2 (declaratii.js).
- `core/test_pastila_gri.py` — GARD (20.08.2026): griul nu se falsifică niciodată în verde.
- `core/test_patru_ochi_efectiv.py` — core/test_patru_ochi_efectiv.py — GARD: patru-ochi = politica x aplicabilitate, aceeasi in UI si in enforcement.
- `core/test_pereche_act_articol.py` — GARD [31.08.2026, faza 2]: un temei nu numește un act care nu conține articolul lui.
- `core/test_perechi_citesc_generatorul.py` — GARD [R123, 02.09.2026]: fiecare pereche orizontala citeste CHEIA PE CARE GENERATORUL O SCRIE.
- `core/test_perimetru.py` — GARD [02.09.2026]: perimetrul portii SCURTE se DERIVA, si stie cand nu poate.
- `core/test_perimetru_calculat.py` — #11 — §5 CALCULAT (meta-gardul). Din registrul de fatete (MODEL_AUDIT_TENANT.md, F1..F9)
- `core/test_perimetru_firma_declarat.py` — core/test_perimetru_firma_declarat.py — GARD: perimetrul declarat al unei firme nu poate ramane
- `core/test_perioada.py` — Perioada confirmata (DESIGN_SYSTEM cap.23): ciclul CONFIRMAT/NECONFIRMAT + blocajul motivat.
- `core/test_perioada_indisponibila.py` — Blocaj MOTIVAT pentru cote de regula cu data_in tarzie (01.08.2026). O cota ceruta de un calcul pentru
- `core/test_plan_conturi_no_upsert.py` — [Regula 4 + Regula 14.4] GARD: adaugarea MANUALA de cont in plan NU suprascrie tacut un simbol existent.
- `core/test_plan_form_fieldmark.py` — [Regula 14.4 pct.4] GARD: formularul 'Adauga cont' (plan_conturi) semnaleaza obligativitatea INAINTE de
- `core/test_plata_salarii.py` — Teste gardian pentru F134 (plata salariilor pe card, SEPA pain.001).
- `core/test_plati.py` — —
- `core/test_plus_mf_registru.py` — #5 (ruptura mijloc-fix post-migrare, plimbare vizuala 14.08.2026): un mijloc fix corporal adaugat prin
- `core/test_poarta_citire_istorica.py` — GARD [R84/PP3, 28.08.2026]: poarta de citire-istorica are EXACT 13 apelanti, si sunt GET-uri.
- `core/test_poarta_gol.py` — Teste numar_operatiuni — puntea catre poarta de declaratie goala.
- `core/test_poarta_inainte_de_aprobare.py` — GARD [02.09.2026]: POARTA CONFIRMARII CADE INAINTE DE APROBARE, nu dupa.
- `core/test_poarta_inchidere.py` — GARDA porții de închidere a perioadei — R58, partea care lipsea.
- `core/test_poarta_profil.py` — Garda: verificarea de profil nu e decorativa — daca exista, blocheaza generarea.
- `core/test_portal_acces.py` — GARD [R62, 26.08.2026]: portalul nu mută identitatea fără confirmare, nu trece un cont dintr-un
- `core/test_portal_ids.py` — GARDĂ: fiecare act citat de un Temei din registru are id-ul lui de portal, scris.
- `core/test_portal_nu_scrie_gol.py` — Unealta care aduce acte din portal NU are voie să scrie un `.txt` gol.
- `core/test_prag_mijloc_fix_unic.py` — GARD [01.09.2026, R108]: pragul de încadrare ca mijloc fix are o SINGURĂ sursă.
- `core/test_prag_per_articol.py` — GARD [01.09.2026, R109]: pragul de reverificare e per articol, dar nicio cotă nu iese din pază.
- `core/test_prapastie_salariu.py` — GARD [R49, varianta (c)]: prăpastia salariului minim se spune CU CIFRE, și cifrele sunt ale
- `core/test_precizie_import.py` — Gard: float-ul din `numere.numar()` nu compromite verificarile de echilibru.
- `core/test_precompletare_anaf_unificata.py` — GARD precompletare_anaf_unificata: cele trei cai de creare a unei firme (register, add-firm,
- `core/test_predare_cifre.py` — GARD [Y, 28.08.2026]: cifrele despre DATE din predare se recalculează, nu se citează.
- `core/test_predare_proaspata.py` — PREDARE_LANT.md isi arata vechimea, iar avertismentul din poarta nu poate disparea tacit.
- `core/test_premisa_restanta.py` — [Regula 4 + Regula 6] TEST-GARDA: NICIO restanta fara premisa demonstrabila.
- `core/test_preview_salvare_poarta.py` — GARD Q5 — preview = salvare, O SINGURA POARTA (tura import CUBUS, 16.08.2026).
- `core/test_profil_blocaje.py` — GARD profil_blocaje: ecranul Date firma NU pretinde 'toate declaratiile se pot genera' cand un
- `core/test_proprietate_coaja.py` — GARD DE PROPRIETATE (P2, 21.08.2026): un ECRAN nu scrie în COAJĂ. DESIGN_SYSTEM cap.25.
- `core/test_provenienta.py` — GARDA: fiecare fisier din corpus isi stie provenienta. (23.08.2026)
- `core/test_publicare_restart_neconditionat.py` — Gard: pasul de restart din ritualul de publicare (scripts/githooks/post-commit) e NECONDITIONAT de continut.
- `core/test_pull_declaratii.py` — Teste pe pull() — granita COD <-> BAZA DE DATE pentru generatoarele de declaratii.
- `core/test_q16_cor.py` — GARD Q16 — preview salariati imbogateste COR cu denumirea ocupatiei (nu doar codul).
- `core/test_r42_criteriu.py` — GARD [R42, cele patru decizii ale lui Costin, 25.08.2026].
- `core/test_ramas.py` — GARDĂ anti-vacuu pe lista derivată a ce a rămas de făcut.
- `core/test_raport_z_unic.py` — GARD [R61, 26.08.2026]: raportul Z nu se poate înregistra de două ori, iar niciuna din cele
- `core/test_reaprindere.py` — GARD: o restanță al cărei DECLANȘATOR s-a produs nu poate rămâne nereluată.
- `core/test_reconciliere.py` — —
- `core/test_reconciliere_d100_wiring.py` — core/test_reconciliere_d100_wiring.py - GARD end-to-end pentru reconcilierea D100 pe semafor
- `core/test_reconciliere_vie.py` — META-GARD (LANT legislatie TURA 4, 10.08.2026): NICIO reconciliere sursa-vs-declaratie nu moare tacit.
- `core/test_refuz_generator_422.py` — GARD (D6, 20.08.2026): un generator care REFUZĂ motivat nu are voie să ajungă la contabil ca 500 gol.
- `core/test_refuz_tacut.py` — GARD [27.08.2026]: un refuz al serverului la o SCRIERE nu poate rămâne nevăzut.
- `core/test_refuzuri.py` — CLICHET: un refuz dintr-un modul care CITEAZĂ legea nu mai poate apărea fără temeiul lui.
- `core/test_regim_peste_perioada_inchisa.py` — GARD [R46, 26.08.2026]: un câmp care decide CE SE DATOREAZĂ nu se schimbă peste o perioadă închisă.
- `core/test_register_cabinet_cui.py` — GARD register_cabinet_cui: la inregistrarea self-service, CUI-ul validat (cel care a trecut
- `core/test_registre_art321.py` — GARD: cele doua registre ale art. 321 alin. (4) CF — ce le tine sa nu se strice tacut.
- `core/test_registru_evidenta_fiscala.py` — GARD: registrul de evidenta fiscala — si mai ales ca nu devine un AL DOILEA calcul al aceluiasi an.
- `core/test_registru_exceptii.py` — GARDĂ peste REGISTRUL DE EXCEPȚII al clichetului de afirmații. (P8, 22.08.2026)
- `core/test_registru_functionalitati.py` — Garda de integritate a FUNCTIONALITATI.csv (registrul canonic al functionalitatilor).
- `core/test_registru_inventar.py` — GARD: registrul-inventar (14-1-2) — si mai ales defectul care l-ar face sa arate perfect.
- `core/test_registru_jurnal_14_1_1.py` — GARD — Registrul-jurnal păstrează cele trei coloane cerute de norma 14-1-1.
- `core/test_reguli_ecran.py` — GARD [28.08.2026]: cele două reguli de ecran scrise azi — E1 și E2 (`DESIGN_SYSTEM.md` cap.26/27).
- `core/test_reluari_decizie.py` — GARD [27.08.2026]: o decizie cerută de mai multe ori nu mai poate arăta ca cerută o dată.
- `core/test_respingeri_import.py` — GARDĂ: o respingere de rând la import e o AFIRMAȚIE, cu regulă numită. (P8/C, 21.08.2026)
- `core/test_retete_randuri_dinamice.py` — GARD cap.24 — randuri dinamice RETETE (ingrediente HoReCa), re-rulate IN POARTA prin chromium headless.
- `core/test_reverificare.py` — GARD [31.08.2026]: categoria de reverificare se CALCULEAZĂ, iar necunoscutul rămâne necunoscut.
- `core/test_rol_pe_efect.py` — core/test_rol_pe_efect.py — GARD: rolul se cere după CE FACE ruta, nu după cum se numește.
- `core/test_rotunjire_fiscala.py` — [Rotunjire fiscală] GARD: în modulele de declarații (`core/d*.py`, `*engine*.py`) o sumă fiscală NU se
- `core/test_running_head.py` — GARD detector "running == HEAD" (DECIZII/GARZI iulie: detector vizibil, NU auto-restart).
- `core/test_ruptura_seed_control.py` — Garda anti-ruptura seed<->control (plimbare vizuala 14.08.2026).
- `core/test_ruta_fara_apelant.py` — GARD [R70, 26.08.2026]: o rută NOUĂ fără apelant nu trece poarta.
- `core/test_rute_autentificate.py` — Garda: fiecare ruta HTTP declara o dependenta de autentificare.
- `core/test_rute_model_body.py` — core/test_rute_model_body.py — GARD: un model Pydantic pe un handler e BODY, nu query.
- `core/test_salariati_blocaj_vizibil.py` — core/test_salariati_blocaj_vizibil.py — GARD: pe Stat de plata, butoanele dezactivate SEPA
- `core/test_salariati_import_iban.py` — core/test_salariati_import_iban.py — GARD: importul de salariati (stratul 4 migrare) aduce IBAN
- `core/test_salarii_contare.py` — Teste gardian pentru salarii_contare (partea pura).
- `core/test_salariu_scrieri.py` — Teste PASUL 2b: scrierile salariului trec pe salariu_istoric (SURSA UNICA); citirile pe curent.
- `core/test_salarizare.py` — Teste gardian pentru core/salarizare.py.
- `core/test_scadente.py` — Teste pentru scadentarul per declaratie (core/scadente.py), sursa unica de termene.
- `core/test_scan_instrumente.py` — Garda instrumentului de FAZA 4 (`scripts/scan_instrumente.py`).
- `core/test_scan_js_texte.py` — CALIBRAREA instrumentului JS — scrisă ÎNAINTE de prima măsurătoare, nu după.
- `core/test_schema_coloane.py` — Garda: coloanele referite in SQL EXISTA in schema reala a tabelelor tenant.
- `core/test_secrete_jwt.py` — Teste securitate JWT — default gol pe cheie HMAC = bypass complet de auth (tokenuri forjabile).
- `core/test_selector_vector.py` — S1 + #2 (plimbare 14.08.2026): selectorul de declaratii respecta vectorul TVA si periodicitatea firmei.
- `core/test_separa_cui.py` — [Regula 4 + Regula 14.4] GARD: intrarile care nu-s CUI NU dispar in tacere la validarea la ANAF.
- `core/test_simetrie_denumire.py` — GARD [R81, DECIS 28.08.2026]: denumirea unei firme se scrie în AMÂNDOUĂ locurile sau în niciunul.
- `core/test_smoke_duk.py` — SMOKE-SWEEP DUK (01.08.2026) — gardul care lipsea: fiecare declaratie generata cu date
- `core/test_solduri_api.py` — Teste gardian pentru solduri_api (partea PURA).
- `core/test_solduri_parteneri_api.py` — Teste gardian pentru solduri_parteneri_api (partea PURA).
- `core/test_sonda_web.py` — GARD [R75 (b), 27.08.2026]: procesul care servește ecranele e supravegheat, și se știe cum.
- `core/test_spv_conector.py` — Teste core/spv_conector.py — pe MOCK, niciodata pe ANAF real (brief BRIEF_CODE_CONECTOR_SPV.md).
- `core/test_spv_poll.py` — Teste core/spv_poll.py (F178) — pe MOCK, niciodata pe ANAF real.
- `core/test_spv_receive.py` — Teste core/spv_receive.py (F179) — pe MOCK (retea + parser), niciodata pe ANAF real.
- `core/test_stat_plata_emis.py` — GARDĂ: statul de plată e un DOCUMENT EMIS, nu o vedere recalculată. (21.08.2026)
- `core/test_status_factura_un_loc.py` — GARDĂ: stările unei FACTURI trăiesc într-un singur loc. (22.08.2026, după reparația de prag 1)
- `core/test_stergere_salariat_completa.py` — GARD (D5, 20.08.2026): stergerea unui salariat nu lasa jumatate din inregistrare in urma.
- `core/test_stocuri.py` — —
- `core/test_stocuri_cv.py` — —
- `core/test_supervizor.py` — GARD [01.09.2026]: supervizorul — cele două tării, și confirmarea care rămâne scrisă.
- `core/test_temei_structurat.py` — Temei fiscal STRUCTURAT (act/nr/an/art/alin/lit/data_in/data_out/url) + garda de EXPIRARE.
- `core/test_temei_termene.py` — GARD (R4, 20.08.2026 — refăcut 21.08): fiecare termen de depunere își poartă actul, ca DATE.
- `core/test_temeiuri.py` — Gardul temeiurilor (PASUL 4): impune forma canonica de citare a REGULILOR de validator din
- `core/test_tenant_stergere.py` — GARD [R72, 27.08.2026]: calea de scoatere a unei firme nu poate rămâne în urma bazei.
- `core/test_termene.py` — core/test_termene.py — plasa de regresie pentru scadentele viitoare (termene_api).
- `core/test_teste_decuplate.py` — Garda PERMANENTA (29.07.2026): niciun test nu depinde de o firma PERSISTENTA din baza.
- `core/test_tichet_2025.py` — GARD B1/tichet 2025: valorile nominale ale tichetului de masa in 2025, verificate VERBATIM la sursa.
- `core/test_tichet_cresa.py` — Tichete de cresa (Legea 165/2018 art.19). Tratament fiscal IDENTIC cu tichetul cultural: impozit 10% pe
- `core/test_tichet_cultural.py` — Tichete culturale (Legea 165/2018 cap.V). Temeiuri VERDE: anaf_surse/RAPORT_verificare_temeiuri.md.
- `core/test_tichete_pontaj.py` — D2 (02.08.2026): tichetele de masa pe zile EFECTIV lucrate (HG 1045/2018 art.10 alin.3). Zilele de
- `core/test_tip_decont_lung.py` — core/test_tip_decont_lung.py — GARD: periodicitatea decont TVA ajunge la UI in forma LUNGA.
- `core/test_trasee.py` — GARD: inventarul traseelor nu îmbătrânește tăcut, iar instrumentul lui nu minte.
- `core/test_tva_incasare.py` — Teste gardian pentru core/tva_incasare.py (art. 282 CF, OUG 8/2026).
- `core/test_tva_incasare_291_5.py` — Garda R151 — cele două ramuri ale art. 291 alin. (5) se CER, nu se ghicesc.
- `core/test_unde.py` — GARDĂ: `unde` e o REFERINȚĂ citabilă mecanic, nu proză. (P8, 22.08.2026)
- `core/test_upsert_motivat.py` — [Regula 4 — fara mutatie tacuta] GARD: orice INSERT ... ON CONFLICT DO UPDATE din codul de PRODUCTIE
- `core/test_valoare_in_citat.py` — GARDĂ pentru interdicția 53: citatul conține VALOAREA pe care o justifică.
- `core/test_valori_fiscale_js.py` — Valorile fiscale scrise in ECRANE se confrunta cu REGISTRUL, nu cu memoria mea.
- `core/test_vector_camp_marcat.py` — [Regula 14.4 pct.4] GARD: eroarea de camp obligatoriu la vectorul fiscal NUMESTE campul vinovat ('camp'),
- `core/test_vector_platitor_tva_oblig.py` — core/test_vector_platitor_tva_oblig.py — GARD: `platitor_tva` necompletat (None) la salvarea
- `core/test_verde_derivat.py` — Verdele de semafor se DERIVĂ; unde nu se poate deriva, semaforul LIPSEȘTE.
- `core/test_verde_peste_necunoscut.py` — GARD [R35/XX3, 28.08.2026]: un verdict nu poate fi VERDE peste un necunoscut pe care il are in mana.
- `core/test_verdict_persistat.py` — GARD — verdictul de validare se păstrează, și un verdict stătut nu ține locul unuia proaspăt.
- `core/test_verdict_stare.py` — —
- `core/test_verificator_al_treilea_rezultat.py` — GARD [31.08.2026, cerut de Costin]: verificatorul de neconformități nu mai afirmă absența când
- `core/test_verificator_izolare.py` — GARDĂ PESTE VERIFICATOR: analizorul lui de izolare clasifică corect rute known-good / known-bad.
- `core/test_versionare_assets.py` — core/test_versionare_assets.py -- GARD pentru disciplina ?v= (versionare asseturi front-end).
- `core/test_versionare_formule.py` — Versionarea formulelor pe la_data (PAS 1 tipar). Cotele sunt period-aware (cota); formulele devin
- `core/test_versiune_publicata.py` — GARD [R118 + R129, 03.09.2026]: poarta de sintaxa a publicarii, si anuntul care NU intrerupe.
- `core/test_vigoare_articole_registru.py` — GARDĂ pentru interdicția 50 — confirmarea unei valori e ULTERIOARĂ ultimei modificări a articolului.
- `core/test_vigoare_punct.py` — Garda instrumentului de vigoare PE PUNCT (`scripts/vigoare_punct.py`, R2).
- `core/test_woocommerce.py` — —
- `core/test_zero_base_declaratii.py` — GARD ZERO-BASE (10.08.2026): un zero care POATE fi defect nu arata ca un nil legal.

### `scripts/` — 20

- `scripts/scan_1b_regimuri.py` — CE PRODUCE APLICAȚIA PE FIECARE REGIM REAL — pasul 1b, 29.08.2026.
- `scripts/scan_1c_verificabil.py` — SE POATE VERIFICA CE IESE? — pasul 1c, 29.08.2026.
- `scripts/scan_ancore_rute.py` — Pentru cate rute e ORB PRIN CONSTRUCTIE detectorul de apelanti din R70.
- `scripts/scan_axa_garzi.py` — FAZA 4, axa D despicata: „odata cu fixul" ascunde DOUA lucruri, iar „singura" ascunde alte doua.
- `scripts/scan_contract_ecran.py` — scripts/scan_contract_ecran.py — contractul ECRAN ↔ RUTĂ, măsurat.
- `scripts/scan_ds_verificator.py` — RAZA VERIFICATORULUI: fiecare regulă din DESIGN_SYSTEM.md, față în față cu ce verifică el — 30.08.2026.
- `scripts/scan_forme_punct.py` — scripts/scan_forme_punct.py — CÂT DE LARG prinde un tipar de punct, pe TOT corpusul.
- `scripts/scan_functionalitati.py` — scripts/scan_functionalitati.py — LISTA FUNCTIONALITATILOR, derivata din cod.
- `scripts/scan_garzi_inventar.py` — Inventarul gărzilor, DERIVAT din cod — blocul generat din `GARZI.md`.
- `scripts/scan_instrumente.py` — scripts/scan_instrumente.py - FAZA 4: pe ce instrument sta fiecare garda, si a fost calibrat.
- `scripts/scan_lanturi_declaratie.py` — ETAPA 2 — CARE unitate alimentează CARE declarație, derivat din cod.
- `scripts/scan_lista3.py` — scripts/scan_lista3.py — lista 3, DERIVATA din registru, nu numarata cu mana.
- `scripts/scan_mutatie_garzi.py` — FAZA 4, pasul 5: mutatia care probeaza garda e REPRODUCTIBILA azi?
- `scripts/scan_predare_cifre.py` — Cifrele despre DATE din `PREDARE_LANT.md`, interogate din bază — blocul generat.
- `scripts/scan_r97_livrat_tacut.py` — CÂT DE MARE E CLASA „RUTA LIVREAZĂ, ECRANUL TACE" — măsurarea lui R97, 29.08.2026.
- `scripts/scan_ramas.py` — scripts/scan_ramas.py — CE A RAMAS DE FACUT, derivat din fisiere, cu sursa pe fiecare rand.
- `scripts/scan_refuzuri.py` — scripts/scan_refuzuri.py — CE POARTA un refuz al aplicatiei, si ce nu poarta.
- `scripts/scan_regimuri.py` — CÂTE REGIMURI FISCALE EXERCITĂ PORTOFOLIUL — prima operațiune din E1 (1a), 29.08.2026.
- `scripts/scan_rute_clasificate.py` — CLASIFICAREA rutelor fără apelant — R70, blocul SSS (29.08.2026).
- `scripts/scan_trasee.py` — scripts/scan_trasee.py — INVENTARUL TRASEELOR, calculat, nu ținut minte.

<!-- INVENTAR-GARZI:STOP -->
