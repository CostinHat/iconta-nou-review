# C-1. MATRICEA OBLIGAȚIILOR DECLARATIVE — an fiscal 2026 + ianuarie 2027 (VALIDAT Costin 05.08.2026; confirmări la sursă 05.08.2026)

**Scop:** ce declarații/raportări datorează o firmă, după regim, cu periodicitate + termen + condiție de declanșare.
**Metodă:** derivată din LEGISLAȚIE (Cod fiscal L227/2015 consolidat + acte modificatoare + OPANAF + Legea 82/1991 +
Legea 296/2023 e-Factura/e-Transport), NU din codul aplicației. Perioada: 01.2026–12.2026 (an complet) + 01.2027
(anuale + tranziția de an). Parametrii 2026 diferă de 2025.
**Nivel de sursă:** `[CF✓]` verificat în anaf_surse/cod_fiscal_227_2015_consolidat.html (text în vigoare) · `[HG✓]`/`[OG✓]`
din hotărâre/ordonanță verificată la sursă · `[OPANAF]` din ordin ANAF (confirmat, unele secundar) · `[L296]`/`[L82]`
din lege · `[expert-CONF]` cunoaștere expertă, de confirmat.

> **★ CELE 8 CONFIRMĂRI + a 9-a (D392) SUNT REZOLVATE LA SURSĂ — vezi secțiunea E.** Patru s-au dovedit **CORECȚII**,
> nu simple confirmări (cota micro, excluderile micro, atribuirea pragului TVA 395k, data tranziției TVA la încasare,
> statutul D392). Parametrii din tabelul A de mai jos sunt deja actualizați cu rezultatele. **Așteaptă validarea Costin
> pe cele 9 înainte de C-2.**

---

## A. PARAMETRII DE REGIM 2026 (dimensiunile matricei)

| parametru | valoare 2026 | sursă | notă |
|---|---|---|---|
| Prag microîntreprindere (CA an anterior) | **100.000 EUR** | `[CF✓]` art.47(1)(c) | modif. OUG 8/2026 (MO 147/25.02.2026), art.6 pct.15; aplicabil inclusiv încadrării ca micro în anul fiscal 2026 (era 250k în 2025) |
| Micro: condiție salariați | **≥1 salariat** (excepție art.48(3)) | `[CF✓]` art.47(1)(g) | micro nou-înființată: cond. în 90 zile; altfel → profit din trim. următor (art.48(3)) |
| **Cotă micro** | **1% UNIC** | `[CF✓]` art.51(1) | **CORECȚIE:** cota 3% (fostul art.51 alin.(1^1)) **ABROGATĂ de la 01.01.2026** prin OUG 89/2025 (MO 1203/24.12.2025). **Nu mai există split 1%/3% și nici pragul 60.000 EUR pe 2026.** |
| Cotă profit | 16% | `[CF✓]` art.17 | |
| Prag înregistrare TVA (scutire) | **395.000 lei** | `[CF✓]` art.310(1) | **CORECȚIE atribuire:** modif. **OG 22/2025** (MO 806/29.08.2025), art.I pct.11 (NU Legea 141/2025); în vigoare ~01.09.2025 (art.III OG 22/2025), stabil pe 2026 |
| Prag TVA la încasare | **4.500.000 lei (ian–feb 2026) → 5.000.000 lei (de la 1 martie 2026)** | `[CF✓]` art.282(3) | **CORECȚIE dată:** tranziția 4,5M→5M = **1 martie 2026**, nu ianuarie; modif. **OUG 8/2026** (MO 147/25.02.2026), art.6 pct.38 (NU Legea 141/2025). 5.500.000 lei de la 01.01.2027 |
| Perioadă TVA | trim. dacă CA an ant. < 100.000 EUR ȘI fără achiziție IC în an; altfel lunar | `[CF✓]` art.322(2) | achiziția IC în anul precedent → lunar |
| SAF-T (D406) | **toate firmele** (mici de la 01.01.2025) | `[OPANAF]` 1783/2021 | confirmat: mici depun D406 de la 01.01.2025 (Anexa 5 pct.1; temei art.59^1(1) L207/2015); grație mici: lunar 6/5/4/3/2 luni primele 5 raportări, trim. 3 luni |
| Cote TVA 2026 | **21% / 11% / 0%** | `[CF✓]` art.291 | Legea 141/2025 de la 01.08.2025; NU 19/9/5 |
| Salariu minim brut 2026 | **4.050 lei (ian–iun) / 4.325 lei (iul–dec)** | `[HG✓]` | H1: HG 1506/2024 (MO 1185/28.11.2024) art.1 (4.050 de la 01.01.2025). H2: HG 146/2026 (MO 196/13.03.2026) art.1 (4.325 de la 01.07.2026) |

### A2. REGIMURI SPECIALE TVA (completare 1 — dimensiune nouă în matrice) — CF art.311–315
Fiecare are tratament TVA propriu și rânduri D300 proprii; o firmă de test dedicată per regim.

| regim special | temei | tratament | efect D300 / declarativ |
|---|---|---|---|
| **Agenții de turism** (regim marjă) | `[CF✓]` art.311 | TVA pe MARJĂ (nu pe preț total); suta mărită cotă/(100+cotă) | rânduri D300 pe marjă, nu pe bază integrală; scutire proporțională non-UE |
| **Bunuri second-hand / opere de artă / obiecte de colecție** (regim marjă) | `[CF✓]` art.312 | TVA pe MARJĂ per bun/global; marjă negativă→0 | rânduri D300 pe marjă |
| **Agricultori — regim special** | `[CF✓]` art.315^1 | procent forfetar de compensație; nu deduc/nu colectează normal | tratament forfetar; interacțiune D394 achiziție de la agricultor forfetar (exceptia numită din campanie) |

## A3. OBLIGAȚII DE RAPORTARE NON-DECLARATIVE (completare 2) — cu termene + sancțiuni

| obligație | temei | ce e | termen |
|---|---|---|---|
| **RO e-Factura (B2B)** | `[L296]` Legea 296/2023 + OUG 120/2021 | transmiterea facturilor B2B în sistemul național (SPV), obligatoriu | **5 zile lucrătoare** de la data emiterii (max data-limită legală de emitere); sancțiuni pe întârziere |
| **RO e-Transport** | `[L296]` OUG 41/2022 | cod UIT pentru transport bunuri (risc fiscal ridicat + internațional) ÎNAINTE de transport | înainte de punerea în mișcare a vehiculului; UIT valabil 5 zile |

---

## B. DECLARAȚIILE

| decl | temei | periodicitate | termen | condiție de declanșare |
|---|---|---|---|---|
| **D112** contrib.+evidență salariați | `[CF✓]` art.147 (+ art.80(2)) | lunar; **trim. cu opțiune** | 25 | plătește venituri din salarii/asimilate. Trim.: plătitorii de la art.80(2) — micro cu ≤3 salariați medii (an ant.), profit cu venituri ≤100k EUR ȘI ≤3 salariați, ONG, PFA angajatori; pot opta lunar până la 31 ian. (art.147(8)) |
| **D100** oblig. buget stat | OPANAF | lunar/trim. | 25 | are obligație de plată (impozit micro, dividend reținut, plăți anticipate profit…) |
| **D300** decont TVA | `[CF✓]` art.323 | lunar/trim. (param A) | 25 | înregistrat TVA (art.316) |
| **D301** decont special TVA | `[CF✓]` art.324 | pe operațiune | 25 | neînregistrat normal + achiziții IC >10.000 EUR / servicii B2B (art.317) |
| **D390** recapitulativă IC (VIES) | `[CF✓]` art.325 | lunar (lunile cu op.) | 25 | operațiuni intracomunitare (ROI) |
| **D394** op. naționale | OPANAF | urmează perioada D300 | 30 | înregistrat TVA, operațiuni interne |
| **D406 SAF-T** | `[OPANAF]` 1783/2021 | lunar/trim. (perioada TVA) + Active anual + Stocuri la cerere | ultima zi luna următoare (+ grație) | toate firmele (mici de la 01.01.2025) |
| **D101** impozit profit | `[CF✓]` art.42 | anual | **25 iunie** an urm. (25 martie an modificat) | plătitor profit (NU micro) |
| **D205** impozit reținut sursă (rezidenți) | `[CF✓]` art.132 + OPANAF | anual | **ultima zi februarie** an urm. | a reținut la sursă (salarii, dividende…) |
| **D207** impozit reținut sursă **nerezidenți** — **ÎN VIGOARE** | `[CF✓]` art.231 | anual | ultima zi februarie an urm. | plăți către nerezidenți cu reținere (dividende/dobânzi/redevențe/servicii) |
| **D710** rectificativă | OPANAF | la nevoie | — | corecție D100/D112/D300 |
| **Situații financiare anuale (bilanț)** | `[L82]` L82/1991 + OMFP 1802/2014 | anual | ~150 zile (≈30 mai) | toate societățile |
| **D392A/B** informativă CA (ne)plătitori TVA | `[CF✓]` art.324(4)-(6) | anual (când e activă) | — | **SUSPENDAT (NU abrogat)** — obligația (CF art.324(4)-(6)) e suspendată prin **OUG 115/2023 art.LXII** până la **31.12.2026 inclusiv**; reluare 2027. Nicio firmă de test 2026 nu-l depune (suspendat), motivul = suspendare, nu abrogare |

---

## C. MATRICEA regim → declarații datorate (o firmă de test per celulă distinctă în C-2)

| # | Regim firmă | D112 | D100 | D300 | D301 | D390 | D394 | D406 | D101 | D205 | Bilanț | e-Fact | e-Trans |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **M1** | Micro, neplătitor TVA, cu salariat, fără IC, an complet | DA | DA | — | — | — | — | DA | — | DA | DA | DA(B2B) | (x) |
| **M2** | Micro, plătitor TVA trim., cu salariat, fără IC | DA | DA | DA(trim) | — | — | DA(trim) | DA | — | DA | DA | DA | (x) |
| **P1** | Profit, plătitor TVA lunar, cu salariați, **cu IC**, an complet | DA | DA | DA(lunar) | — | DA | DA(lunar) | DA | DA | DA | DA | DA | (x) |
| **P2** | Profit, plătitor TVA trim., cu salariați, fără IC | DA | DA | DA(trim) | — | — | DA(trim) | DA | DA | DA | DA | DA | (x) |
| **N1** | Neplătitor TVA, micro fără salariat (art.48(3)), **achiziții IC >10k EUR** | — | DA | — | **DA** | (x) | — | DA | — | (x) | DA | DA | (x) |
| **S1** | **Regim special TVA — agenție turism** (art.311), plătitor TVA, cu salariați | DA | DA | DA(marjă) | — | — | DA | DA | DA/— | DA | DA | DA | (x) |
| **S2** | **Regim special — second-hand/opere artă** (art.312), plătitor TVA | DA/— | DA | DA(marjă) | — | (x)IC | DA | DA | DA/— | DA | DA | DA | (x) |
| **S3** | **Agricultor regim special** (art.315^1) | (x) | DA | — | — | — | (x) | DA | — | (x) | DA | (x) | **DA** (transport produse) |
| **NR1** | Profit, plătitor TVA, cu **plăți către nerezidenți** (redevențe/servicii) | DA | DA | DA | — | (x) | DA | DA | DA | DA | **D207** | DA | (x) |
| **T1** | Înființată la mijloc de an (**an parțial**), micro cu salariat | DA(din angajare) | DA | (după înreg.) | — | — | — | DA | — | DA | DA(parțial) | DA | (x) |
| **T2** | **Micro→profit în cursul lui 2026** (depășire 100k / pierdere salariat) | DA | DA | (după caz) | — | (x) | (x) | DA | DA(de la trecere) | DA | DA | DA | (x) |

Note: „(x)” = condiționat (doar dacă apare operațiunea). e-Factura B2B = obligatoriu la orice firmă care emite facturi
B2B. e-Transport = doar la transport de bunuri (marcat DA unde e caracteristic firmei, ex. S3 agricultor cu produse).

**Efect al corecției cotei micro asupra matricei:** cota micro fiind **1% unic pe 2026**, dimensiunea „1% vs 3%” DISPARE —
nu mai e nevoie de firmă de test dedicată pentru bracket-ul 3%. M1/M2 rămân valide (regim micro), doar cota aplicată se
simplifică la 1%.

---

## D. NOTE PER-PERIOADĂ 2026
- Cote TVA **21/11/0 pe tot 2026** (nu 19/9/5). Cotă micro **1% unic** (3% abrogat 01.01.2026). Prag micro **100k EUR de
  la 01.01.2026** (era 250k → celula T2). Prag scutire TVA **395.000 lei** din ~01.09.2025.
- **TVA la încasare:** 4.500.000 lei (ian–feb 2026) → **5.000.000 lei de la 1 martie 2026** (OUG 8/2026); 5.500.000 lei
  de la 01.01.2027. Salariu minim: 4.050 (ian–iun) → 4.325 (iul–dec).
- **Ianuarie 2027:** D406 lună 12/2026 → 31.01; D300/D112 → 25.01; D394 → 30.01; D205+D207(2026) → 28.02; D101(2026) →
  25.06; bilanț 2026 → ~30.05. e-Factura/e-Transport = pe flux, nu la termen fix. D392 pentru 2026 = NU se depune
  (suspendat până 31.12.2026); ar reveni pentru activitatea 2027 dacă suspendarea nu se prelungește.

---

## E. CONFIRMĂRILE — REZOLVATE LA SURSĂ (05.08.2026)
Fiecare cu actul, articolul și textul citat. Extras din `anaf_surse/cod_fiscal_227_2015_consolidat.html` (text în
vigoare, consolidat just.ro) și HG-urile locale; #6 și istoricul suspendării D392 confirmate suplimentar din surse
secundare (marcat). **4 din 9 sunt CORECȚII, nu simple confirmări.**

### 1. Cota micro 1% vs 3% — **CORECȚIE: cotă UNICĂ 1% pe 2026; 3% + pragul 60.000 EUR ABROGATE**
- **CF art.51 alin.(1):** „Cota de impozit pe veniturile microîntreprinderilor este de 1%.”
- **CF art.51 alin.(1^1):** „Abrogat.”
- Ambele **la 01-01-2026**, prin **OUG nr. 89 din 23 decembrie 2025** (MO 1203/24.12.2025), art.I pct.4 (alin.1) și
  pct.5 (abrogarea alin.1^1). Fostul alin.(1^1) conținea cota de 3% (peste 60.000 EUR / anumite activități).
- **Concluzie:** pe 2026 NU mai există split 1%/3% și nici pragul de 60.000 EUR. Cotă micro = **1% unic**. Nivel: `[CF✓]`.

### 2. Lista CAEN/activități excluse de la micro 2026 — **CORECȚIE: regula „consultanță/management >20%” NU mai există**
- **CF art.47 alin.(3)** — „Nu intră sub incidența prezentului titlu următoarele persoane juridice române:” a) Fondul de
  garantare a depozitelor bancare; b) Fondul de compensare a investitorilor; c) Fondul de garantare a pensiilor private;
  d) Fondul de garantare a asiguraților; e) entitatea transparentă fiscal cu personalitate juridică; **f)** „persoana
  juridică română care desfășoară activități în domeniul bancar”; **g)** „…în domeniul asigurărilor și reasigurărilor, al
  pieței de capital, precum și …intermediere/distribuție în aceste domenii, cu excepția intermediarilor secundari …până
  la 15% inclusiv din veniturile totale”; **h)** „…în domeniul jocurilor de noroc”; **i)** „…activități de explorare,
  dezvoltare, exploatare a zăcămintelor de petrol și gaze naturale.”
- **CF art.47 alin.(1) lit.g):** „are cel puțin un salariat, cu excepția situației prevăzute la art. 48 alin. (3);”
- **Condiția consultanță/management ELIMINATĂ:** **CF art.54 alin.(3)** (introdus de OUG 156/2024, art.LXIV pct.6): „Condiția
  referitoare la ponderea veniturilor din consultanță și/sau management în veniturile totale, de la data de 31 decembrie
  2024, nu se aplică…”. Nu apare nici în lista de excluderi art.47(3).
- **HoReCa NU e excludere:** codurile CAEN 5510–5630 (art.48 alin.(2^2)) și 5611/5612/5622 (art.54 alin.(4)) sunt o
  regulă de **reîncadrare** (să nu mai fi fost micro), nu o excludere de la micro.
- **Concluzie:** excluderile micro 2026 = art.47(3) lit. a)–i) [fonduri de garantare, bancar, asigurări/piață de capital,
  jocuri de noroc, petrol&gaze]. Nivel: `[CF✓]`.

### 3. Data intrării pragului TVA 395.000 lei — **CORECȚIE atribuire (OG 22/2025, nu Legea 141/2025)**
- **CF art.310 alin.(1):** „Persoana impozabilă stabilită în România …, a cărei cifră de afaceri anuală, declarată sau
  realizată, nu depășește **plafonul de 395.000 lei**, poate aplica scutirea de taxă…”.
- Modificat de **ORDONANȚA nr. 22 din 28 august 2025** (MO 806/29.08.2025), art.I pct.11.
- **Data intrării + stabilitate:** **art.III OG 22/2025** — cei care au depășit în august 2025 plafonul vechi de 300.000
  lei „nu trebuie să solicite înregistrarea …decât la depășirea plafonului anual de scutire de 395.000 lei”; dacă în
  august 2025 s-a depășit și 395.000 lei → înregistrare până la 10.09.2025. Deci pragul de 395.000 lei e operativ din
  ~01.09.2025 și **stabil pe tot 2026**. Legea 141/2025 consolidat nu conține art.310/plafonul (verificat). Nivel: `[CF✓]`.

### 4. Data tranziției TVA la încasare 4,5M→5M — **CORECȚIE: 1 martie 2026 (nu ianuarie); OUG 8/2026, nu Legea 141/2025**
- **CF art.282 alin.(3):** „Plafonul pentru aplicarea sistemului TVA la încasare este de: a) **5.000.000 lei, în perioada
  1 martie–31 decembrie 2026**; b) **5.500.000 lei, începând cu data de 1 ianuarie 2027**.” Modificat de **OUG nr. 8 din 24
  februarie 2026** (MO 147/25.02.2026), art.6 pct.38.
- **Valoarea ian–feb 2026 = 4.500.000 lei:** **art.9 OUG 8/2026** — „Persoanele impozabile care aplică sistemul TVA la
  încasare și care depășesc în cursul lunii ianuarie 2026 plafonul de 4.500.000 lei, dar nu depășesc plafonul de
  5.000.000 lei, nu vor fi radiate…” (idem februarie 2026, alin.(2)).
- **Concluzie:** tranziția 4,5M→5M s-a produs la **1 martie 2026** (OUG 8/2026), nu în ianuarie. Legea 141/2025 nu atinge
  art.282 (verificat în consolidat). Nivel: `[CF✓]`.

### 5. Salariul minim brut 2026 — CONFIRMAT
- **H1 2026 = 4.050 lei:** **HG nr. 1.506 din 27 noiembrie 2024** (MO 1185/28.11.2024), art.1: „Începând cu data de 1
  ianuarie 2025, salariul de bază minim brut pe țară garantat în plată …la suma de 4.050 lei lunar…” (în vigoare și în
  prima jumătate a lui 2026).
- **H2 2026 = 4.325 lei:** **HG nr. 146 din 12 martie 2026** (MO 196/13.03.2026), art.1: „Începând cu data de 1 iulie
  2026, salariul de bază minim brut pe țară garantat în plată …se stabilește …la suma de 4.325 lei lunar, pentru un
  program normal de lucru în medie de 166,667 ore pe lună, reprezentând 25,949 lei/oră.”
- **Concluzie:** 2026 = 4.050 lei (ian–iun) / 4.325 lei (iul–dec). Nivel: `[HG✓]`.

### 6. Calendarul SAF-T firme mici — CONFIRMAT (01.01.2025)
- **OPANAF nr. 1783/2021** (Anexa 5 pct.1; temei **art.59^1 alin.(1) din Legea 207/2015** – Cod procedură fiscală):
  contribuabilii mici au obligația să depună Declarația informativă D406 SAF-T **începând cu 1 ianuarie 2025**.
- **Perioadă de grație (mici):** lunar — 6/5/4/3/2 luni pentru primele 5 raportări; trimestrial — 3 luni pentru prima
  raportare (calculate de la ultima zi a perioadei de raportare).
- Nivel: `[OPANAF]`. **Caveat:** textul primar al OPANAF 1783/2021 NU e stocat în anaf_surse/; confirmat din surse
  secundare de încredere (CECCAR Business Magazine, ghidul ANAF D406). Data 01.01.2025 = concordantă între surse.

### 7. + 9. D392 — **CORECȚIE: SUSPENDAT, NU abrogat; nu există act de abrogare**
- **Temeiul obligației (intact):** **CF art.324 alin.(4)-(6)** — declarațiile informative 392A (plătitori TVA) / 392B
  (neplătitori) / 393.
- **Suspendarea curentă:** notă în CF consolidat, art.324: „Potrivit **art. LXII din ORDONANȚA DE URGENȚĂ nr. 115 din 14
  decembrie 2023** (MO 1139/15.12.2023), aplicarea prevederilor **art. 324 alin. (4)-(6)** din Legea nr. 227/2015 …se
  suspendă începând cu data de **1 ianuarie 2024 și până la data de 31 decembrie 2026 inclusiv**.”
- **Istoric suspendare (fără întrerupere):** OUG 84/2016 (2017–2019) → OG 6/2020 art.II (până 31.12.2022) → OUG 168/2022
  art.XXXV (2023) → OUG 115/2023 art.LXII (2024–2026). Reluare 2027 dacă nu se prelungește.
- **Concluzie (a 9-a întrebare):** NU există un act care să fi ABROGAT D392 — marcajul „ABROGAT (nicio firmă nu-l are)”
  era un argument din matrice, greșit juridic. Corect: **obligație SUSPENDATĂ până la 31.12.2026** (OUG 115/2023 art.LXII).
  Efect practic identic pentru campania 2026 (nicio firmă nu-l depune), dar **motivul e suspendarea, nu abrogarea**, iar
  obligația ar reveni pentru activitatea din 2027. Nivel: `[CF✓]` (notă consolidat) + secundar pentru istoric.

### 8. Periodicitatea D112 trimestrial — CONFIRMAT (cine poate opta)
- **CF art.147 alin.(4):** „Prin excepție de la prevederile alin. (1), plătitorii de venituri din salarii și asimilate
  salariilor prevăzuți la **art. 80 alin. (2)** …depun **trimestrial** Declarația …aferentă fiecărei luni a trimestrului,
  până la data de 25 inclusiv a lunii următoare trimestrului.”
- **CF art.80 alin.(2)** — plătitorii cu regim trimestrial: a) asociații/fundații/entități fără scop patrimonial; b)
  „persoanele juridice plătitoare de impozit pe profit care, în anul anterior, au înregistrat venituri totale de până la
  100.000 euro și au avut un număr mediu de până la 3 salariați exclusiv”; c) „persoanele juridice plătitoare de impozit
  pe veniturile microîntreprinderilor care, în anul anterior, au avut un număr mediu de până la 3 salariați exclusiv”;
  d) PFA/întreprinderi individuale/profesii liberale/persoane fizice angajator.
- **Opțiune pentru lunar:** **CF art.147 alin.(8)** — pot opta pentru depunerea lunară dacă depun declarația de opțiune
  până la 31 ianuarie inclusiv.
- **Concluzie:** micro pot depune D112 trimestrial dacă în anul anterior au avut nr. mediu ≤3 salariați (art.80(2)(c));
  profit — dacă venituri ≤100.000 EUR ȘI ≤3 salariați (art.80(2)(b)). Nivel: `[CF✓]`.

---

## F. CE A RĂMAS NECONFIRMABIL LA SURSĂ PRIMARĂ (cu motivul)
- **#6 SAF-T (textul primar OPANAF 1783/2021):** data 01.01.2025 și perioadele de grație sunt confirmate, dar din surse
  **secundare** (CECCAR, ghid ANAF D406) — ordinul primar nu e stocat în `anaf_surse/`, iar PDF-ul ghidului ANAF nu s-a
  putut parsa ca text. Recomandare: descărcare OPANAF 1783/2021 consolidat (just.ro) pentru anexarea la nivel `[OPANAF✓]`.
- **#7/#9 istoric suspendare D392 (OUG 84/2016 / OG 6/2020 / OUG 168/2022):** suspendarea CURENTĂ (OUG 115/2023 art.LXII,
  până 31.12.2026) e confirmată din **nota primară** a CF consolidat; lanțul istoric complet e parțial din notele CF
  (OG 6/2020, OUG 168/2022 apar) + secundar pentru OUG 84/2016. Nu afectează concluzia (suspendat, nu abrogat).
- Restul (cotă micro, excluderi micro, prag 395k, TVA la încasare, salariu minim, D112 trim.) = confirmate la **sursă
  primară** (`[CF✓]`/`[HG✓]`), toate cu articol + text citat mai sus.

**Volum + CUI/CNP fictive (R1/R3):** NU se fixează în C-1 — se propun în C-2, unde CUI-urile fictive valide (cifra de
control OK) se verifică să NU aparțină firmelor reale înainte de a le fixa; coerența A↔B (facturi între firmele de test)
se asigură pe sume/CUI/date identice.
