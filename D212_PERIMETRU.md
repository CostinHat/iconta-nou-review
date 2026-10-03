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
  veniturile 2025. **Construit 02.10.2026 (Etapa 3, §6)**: `d212.cap12_norma` + lista de pe ecran; agricolul pe normă
  rămâne refuzat numit până la validatorul ANAF pentru OPANAF 2736/2025 ([EXTERN]).
- **2c. CAS și CASS datorate** — EXISTENT în `d212_engine` (art. 148-149 / 154-170, praguri 12/24 sm CAS,
  6/60 sm CASS). **Cablat 02.10.2026 (Etapa 4, §7)**: `d212.oblig_realizat` + probă F4; CASS sub 6 sm reparată
  (baza minimă, art.174 alin.(6)).
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
- **Etapa 3** — normă de venit (incl. agricol art.107(2)) în engine + emitter cap12, lanț-probă. **FĂCUTĂ 02.10.2026**
  (calculul în emitter, `d212.cap12_norma`, nu în engine — DECIZII 02.10) — v. §6. Agricolul: [EXTERN], fără loc în validator.
- **Etapa 4** — CAS/CASS în oblig_realizat (cablare + probă), inițială/rectificativă. **FĂCUTĂ 02.10.2026** — v. §7 (opțiunea
  CAS sub 12 sm: [EXTERN]).
- **Etapa 5** — formular manual pentru categoriile fără date (regula 0 DESIGN_SYSTEM). **5a FĂCUTĂ 02.10.2026** (I.1.1 pe
  categorii, CAS cu DPI, CASS 2.2, Secțiunea 5) — v. §8; **5c-1 FĂCUTĂ 03.10.2026** (cap14, 12 categorii) — v. §9; rămâne 5c-2
  (premii, jocuri de noroc, pensii, transferul proprietăților, moștenire, remunerații administratori).
- **Etapa finală** — ~~alinierea F246~~ (făcută 02.10 în Etapa 3) + mesajul din d221.py + ghidurile care spun „D212 doar identificare".

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

## 6. Etapa 3 — ce s-a aflat la sursă și ce s-a construit (02.10.2026)
- **Validatorul în vigoare (v9 / J13.0.1)**: clasa `Cap12` = 15 atribute, TOATE opționale (`norma_forma_org` [1,2], `norma_caen`,
  `norma_descriere_sediu_bun`, `norma_nr_doc_autoriz`, `norma_data_doc_autoriz`, `norma_data_incep`, `norma_data_sf`,
  `norma_data_susp`, `norma_nr_zile_scutite`, `real_norma_venit`, `real_ajustare`, `real_venit_net_anual`,
  `real_venit_impozit`, `real_impozit` + forma); element REPETABIL; `validateCap12` goală; R8: bifa112=1 ⇒ cap12 există.
  cap12 e Subsecțiunea a 2-a lit.A a capitolului I (venit REALIZAT pe normă), nu „estimat" (eticheta veche din lot 6, corectată).
- **Rândurile** (OPANAF 2736/2025, Subsec.2 lit.A): rd.9 = rd.7 sau rd.8; la început/încetare/întrerupere „raportarea … la 365
  de zile, iar rezultatul se înmulțește cu numărul zilelor de activitate"; rd.9.1 = rd.9 redus cu zilele scutite; impozit 10%
  (CF art.69^2 alin.(1)).
- **Construit**: `d212.cap12_norma`, `genereaza(manual.norma)` (o secțiune pe activitate, eroarea numește activitatea),
  `bifa112`, ecranul (lista „Venit pe normă de venit", DS cap.24). Gărzi `core/test_d212_cap12.py`,
  `core/test_manual_chei_consumate.py`; probe `frontend_test/proba_d212_etapa3.py` (F4, cod vechi vs nou),
  `frontend_test/proba_d212_norma_ui.py` (ecran, pe 8011).
- **Agricolul pe normă (Subsecțiunea a 4-a, CF art.107 alin.(2))**: fără loc în structura instalată (niciun atribut agricol,
  fără bifa114) → refuz numit + datorie strictă [EXTERN] `test_datorie_d212_venit_agricol_pe_norma`.
- **În afara Etapei 3**: repartizarea venitului din asociere (contabilul dă norma atribuibilă), impozit/CAS/CASS în
  `oblig_realizat` (Etapa 4).

## 7. Etapa 4 — ce s-a aflat la sursă și ce s-a construit (02.10.2026)
- **Validatorul în vigoare (v9)**: `Oblig_realizat` fără reguli încrucișate (doar intervale); numele XML ale atributelor diferă
  pe alocuri de numele câmpurilor interne (`cass_retinut_platitor_alin6_ai` vs `_cass_ret_plat_alin6_ai`) — seturile din
  `d212._CAMPURI` sunt acum confruntate cu jar-ul (`core/test_d212_campuri_validator.py`).
- **Atribut -> rând** (D212Pdf Pdf_v8): I.3.1 CAS rd.1–5 + `bifa_cas_real` (doar A1 12–24 sm / A2 ≥ 24 sm); I.3.2.1 CASS
  rd.1–5; I.4 rd.1, rd.4, rd.6 (rd.2/rd.3 = rd.5 din 4.1 / rd.6 din 4.2); 4.1 / 4.2 cu ponderea; I.7.1–I.7.4.
- **Construit**: `d212.oblig_realizat` (din cap11 + cap12, CAS/CASS și cota impozitului din `d212_engine`), bifa131/132/14,
  lista „Excepție de la baza minimă CASS” pe ecran. Gărzi `core/test_d212_oblig_realizat.py`, `core/test_d212_campuri_validator.py`;
  probă `frontend_test/proba_d212_etapa4.py` (F4, cod vechi vs nou).
- **Neconformitate reparată înainte (același front):** CASS sub 6 sm — baza minimă (CF art.174 alin.(6)), v. DECIZII 02.10.
- **[EXTERN]:** opțiunea CAS sub 12 sm (lit.B) — fără căsuță în formularul instalat; refuz numit + datorie strictă.
- **În afara Etapei 4**: reținerile la sursă, bonificația (Secțiunea 8), drepturile de proprietate intelectuală și celelalte
  categorii fără date (Etapa 5), Capitolul II (CASS opțională pe anul curent).

## 8. Etapa 5 (5a) — ce s-a aflat la sursă și ce s-a construit (02.10.2026)
- **Validatorul (J13.0.1)**: `cap11` fără reguli încrucișate, secțiune REPETABILĂ (probat DUK: șase secțiuni = valid); refuzul
  vechi „o singură secțiune” era neprobat — scos. Codurile alte surse: 1021 lit.k^1, 1022 lit.l, 1023 lit.m, 1024 celelalte
  (D212Pdf Pdf_v5/v6). Atribute: I.3.2.2 `bifa_cass_real` 1/2/3, `cass_ven_dpi/asc/cfb/inv/asp/alt`, `cass_total_ven`,
  `cass_baza`, `cass_datorat`, `cass_retinut`, `cass_dif_plus`; I.5 `real_*_dpi` + bifa15; I.7.3 rd.4 `oblcass_real_difPlus_dpi`.
- **Construit**: `d212.cap11_categorie` (DPI forfetar/real, cedarea folosinței, turistic, agricole, investiții, alte surse),
  `oblig_realizat` cu CAS pe DPI, Secțiunea 5, CASS 2.2 pe trepte (`d212_engine.calculeaza_cass_alte_venituri`), excepția 2.1
  din date, sumarul complet; scutirea pentru handicap pe zile (INTERPRETARE, DECIZII 02.10); lista „Alte venituri” pe ecran.
  Gardă `core/test_d212_categorii.py`; probă `frontend_test/proba_d212_etapa5.py` (F4, cod vechi vs nou).
- **Doar veniturile 2025**: de la veniturile 2026, Legea 239/2025 art.XII pct.7–14 schimbă cedarea folosinței și alte surse;
  formularul pentru 2026 nu e publicat -> refuz numit.
- **[EXTERN]**: CASS 2.2 reținută peste cea datorată (fără rând „în minus” în formular); dobânzile pentru obligațiuni pe piețe
  externe (pct.8) — fără căsuță în formularul instalat.
- **Rămâne (5c)**: cap14 — veniturile din străinătate (Secțiunea 2) și includerea lor în CAS/CASS.

## 9. Etapa 5c-1 — veniturile din străinătate (03.10.2026)
- **Validatorul**: `cap14` repetabil, fără reguli încrucișate; țara din `Parameters_v7._nomenclatorTari` (ISO alfa-2, Grecia = EL,
  fără România) — `d212.TARI_STRAINATATE`, confruntat cu jar-ul; codurile categoriilor din D212Pdf Pdf_v8; `dubla_impunere`
  1 credit / 2 scutire / 4 acord internațional.
- **Construit**: `d212.cap14_sectiune` (12 categorii: activități, DPI, cedare, agricole, titluri, dobânzi, dividende, alte venituri,
  lichidare, salarii plătite din România), credit plafonat (CF art.131 alin.(4)), cap14 în CAS / CASS 2.1 (INTERPRETARE) / CASS 2.2
  și rd.11 în I.7; bifa „fără CAS/CASS în România (asigurat în alt stat)”; lista „Venituri din străinătate” pe ecran. Gardă
  `core/test_d212_cap14.py`; probe `frontend_test/proba_d212_etapa5c.py` (F4) și `proba_d212_strainatate_ui.py`.
- **5c-2a FĂCUTĂ 03.10.2026**: premii 2025, jocuri de noroc 2013 (barem pe data plății: OG 16/2022 până la 31.07.2025, Legea
  141/2025 de la 01.08.2025), transferul proprietăților 2029/2030, moștenire 2024 — DECIZII 03.10.
- **Rămâne (5c-2b)**: pensii 2020 (CF art.130 alin.(2^1)), remunerații administratori 2015 + I.2.2 (`str_cas_*`, `str_cass_*`).
