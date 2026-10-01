# D212 (Declarația unică) — perimetru și sursă (Etapa 1)

Fundația pentru D212 complet, pentru **veniturile din 2025, depuse în 2026** (PFA/II/IF). Toate afirmațiile
de mai jos sunt verificate la sursă (1 oct. 2026), nu din memorie.

## 1. Sursa oficială în vigoare (verificată la sursă)

- **OPANAF nr. 2.736 din 23 decembrie 2025** — aprobă modelul, conținutul și modalitatea de depunere a
  formularului 212, pentru veniturile realizate **începând cu 2025**. Adus în corpus:
  `anaf_surse/opanaf_2736_2025_d212.txt` (+ `.sha256`, PROVENIENȚĂ ADUS).
- **Instrucțiuni de completare D212** (Instructiuni_D212_2736_2025) — adus:
  `anaf_surse/instructiuni_d212_2736_2025.txt` (+ `.sha256`, ADUS).
- **Structura DUK** = validatorul oficial `D212Validator.jar`, versiunea în vigoare **J13.0.1**
  (versiuni.xml ANAF: `<versiuneJ>J13.0.1</versiuneJ>`; JAR servit Last-Modified 01-Aug-2025; instalat
  identic, 1.706.852 B). `anaf_surse/D212_IstoriaVersiunilor.txt` = la zi (J13.0.1).
- **Reguli de fond** (cote/plafoane): Codul fiscal (în corpus) — art. 68-69 (venit net), art. 148-149 (CAS),
  art. 154/170 (CASS), art. 107 alin. (2) (activități agricole pe normă, din 2025 prin D212).

### Tensiune declarată (validator vs. ordin)
Validatorul publicat de ANAF (J13.0.1, 01-Aug-2025) **predatează** OPANAF 2736/2025 (23-Dec-2025); ANAF nu
a publicat încă un validator nou (D212_41+ = HTTP 404). Consecință asumată: **construim pe structura
J13.0.1** (singurul validator pe care-l servește ANAF și pe care-l rulează DUKIntegrator) + regulile de
fond din OPANAF 2736/2025 și Codul fiscal. Structura capitolelor DU e stabilă an-la-an; diferențele 2736
sunt de cote/plafoane (vin din CF, nu din structura validatorului). Dacă ANAF publică validatorul pentru
2736, re-verificăm structura și bump-ăm.

## 2. Perimetru (PFA/II/IF)

### În perimetru
- **2a. Venit în sistem real, din evidența aplicației** — motor EXISTENT `core/d212_engine.py`
  (`calculeaza_d212`/`calculeaza_cas`/`calculeaza_cass`, plafoane pe anul venitului), alimentat din RIP
  (`core/rip_api.py`, registrul de inventar/venituri PFA). GOL: cablarea completă RIP→engine→emitter→XML.
- **2b. Venit pe normă de venit, inclusiv agricol (CF art. 107 alin. (2))** — care înlocuiește D221 de la
  veniturile 2025. GOL: normă NU e în `d212_engine` (de construit); emitter-ul (`d212.py` cap12) acceptă deja
  valori de normă.
- **2c. CAS și CASS datorate** — EXISTENT în `d212_engine` (art. 148-149 / 154-170, praguri 12/24 sm CAS,
  6/60 sm CASS). GOL: cablarea în emitter (oblig_realizat) + probă pe lanț.
- **2d. Depunere inițială și rectificativă** — emitter-ul are bifele; GOL: fluxul explicit + proba.
- **Categoriile fără date în aplicație** (ex. chirii neținute în app, investiții, alte surse, venituri din
  străinătate cap14) — se introduc de contabil într-un **formular manual**, după tiparul formularelor
  manuale existente (D208/D230/D221), cu **regula 0 din DESIGN_SYSTEM.md** citată în patch la orice ecran nou.

### În afara perimetrului (declarat, cu motiv)
- **Precompletarea din SPV** (OPANAF 2719/2025, formular 212 precompletat de ANAF) — NU: aplicația nu are
  acces la SPV (vezi F127/F128, blocant structural mTLS/certificat). Contabilul preia precompletarea manual.
- **Generarea PDF** (D212Pdf.jar) — NU: livrăm XML validat DUK pentru depunere, nu PDF printabil.
- **Veniturile anului 2026 (estimat) pe plafonul CASS 72 sm** (Legea 239/2025 art.XII pct.19) — NU în
  această etapă: se aplică veniturilor 2026 (D212 depusă 2027); perimetrul cerut e venituri 2025/depunere 2026.
- **Validatorul pentru OPANAF 2736** (nepublicat de ANAF) — în afara controlului nostru; v. tensiunea de mai sus.

## 3. Starea codului (inventar, 1 oct. 2026)
- `core/d212.py` — emitter structură-completă (cap11/cap12/cap14/oblig_realizat/oblig_estimat/coasigurat),
  azi emite doar cazul minim de identificare; capitolele populate se emit din `manual` (valori gata calculate).
- `core/d212_engine.py` — motor sistem real (CAS/CASS/impozit/venit net), plafoane pe anul venitului; FĂRĂ normă.
- `core/rip_api.py` — registrul PFA (RIP), consumă `d212_engine`.
- Declarații înrudite PFA: d204 (asociere), d220 (venit estimat), d221 (normă, ≤2024 — înlocuit de D212 din 2025).

## 4. Planul pe etape (următoarele)
- **Etapa 2** — venit real cap-coadă: RIP→engine→emitter cap11→XML→DUK, lanț-probă pe portofoliu
  (invalid→valid), gardă+mutație pe sume. **FĂCUTĂ 02.10.2026** — v. §5.
- **Etapa 3** — normă de venit (incl. agricol art.107(2)) în engine + emitter cap12, lanț-probă.
- **Etapa 4** — CAS/CASS în oblig_realizat (cablare + probă), inițială/rectificativă.
- **Etapa 5** — formular manual pentru categoriile fără date (regula 0 DESIGN_SYSTEM).
- **Etapa finală** — alinierea F246 + mesajul din d221.py + ghidurile care spun „D212 doar identificare".

## 5. Etapa 2 — ce s-a aflat la sursă și ce s-a construit (02.10.2026)
- **Validatorul în vigoare (v9 / Parameters_v7)**: `validateCap11` e goală — cap11 se validează doar structural.
  `categ_venit` ∈ {1016, 1003, 1015, 1006, 1009, 1010, 1011, 1012, 1021–1024}; `det_ven_net` [1,2]; `forma_org` [1,3];
  sume întregi [0, 10^15); niciun atribut cap11 obligatoriu.
- **Semnificația codurilor** (D212Pdf.jar, Pdf_v8, URL din `anaf_surse/versiuni.xml`): 1016 = activități independente,
  1003 = drepturi de proprietate intelectuală, 1015/1006 = cedarea folosinței / scop turistic, 1009–1011 = agricol /
  silvicultură / piscicultură, 1012 = transfer titluri, 1021–1024 = alte surse (art.114 CF); `det_ven_net` 1 = sistem
  real, 2 = cote forfetare; `forma_org` 1/2/3 = individual / asociere / transparență fiscală.
- **R4** (citit integral): pentru CNP, `totalPlata_A` = suma celor 13 cifre, MEREU (nu suma de plată). Corectat în emitter.
- **Rândurile** (instrucțiuni pct.3.5.11): rd.6 = min(rd.5, 70% × rd.3) (CF art.118 alin.(4)); rd.8 și rd.9 nu se
  completează la venit net — impozitul e în secțiunea 4 a capitolului I (`oblig_realizat`, **Etapa 4**).
- **Construit**: `d212.cap11_sistem_real`, `d212.cap11_din_rip`, `genereaza(manual.din_rip)`, ecranul (bifa RIP + pierdere
  reportată + CAEN). Gărzi `core/test_d212_cap11.py`; probe `frontend_test/proba_d212_etapa2.py`, `proba_d212_formular_ui.py`.
- **În afara Etapei 2**: asocieri (§3.5.12), cote forfetare, normă (Etapa 3), impozit/CAS/CASS (Etapa 4).
