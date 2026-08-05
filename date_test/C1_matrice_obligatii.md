# C-1. MATRICEA OBLIGAȚIILOR DECLARATIVE — an fiscal 2026 + ianuarie 2027 (VALIDAT Costin 05.08.2026)

**Scop:** ce declarații/raportări datorează o firmă, după regim, cu periodicitate + termen + condiție de declanșare.
**Metodă:** derivată din LEGISLAȚIE (Cod fiscal L227/2015 consolidat + Legea 141/2025 + OPANAF + Legea 82/1991 + Legea
296/2023 e-Factura/e-Transport), NU din codul aplicației. Perioada: 01.2026–12.2026 (an complet) + 01.2027 (anuale +
tranziția de an). Parametrii 2026 diferă de 2025.
**Nivel de sursă:** `[CF✓]` verificat în anaf_surse/cod_fiscal · `[OPANAF]`/`[L82]`/`[L296]` din ordin/lege (de confirmat
la structura oficială) · `[expert-CONF]` cunoaștere expertă, de confirmat. Comparația cu acoperirea aplicației (→ goluri
în GARZI) se face DUPĂ finalizarea celor 8 confirmări (secțiunea E), înainte de C-2.

---

## A. PARAMETRII DE REGIM 2026 (dimensiunile matricei)

| parametru | valoare 2026 | sursă | notă |
|---|---|---|---|
| Prag microîntreprindere (CA an anterior) | **100.000 EUR** | `[CF✓]` art.47 | de la 01.01.2026 (era 250.000 în 2025) |
| Micro: condiție salariați | **≥1 salariat** (excepție art.48(3)) | `[CF✓]` art.47 g | micro fără salariat → trece la profit |
| Cotă micro | 1% (≤ echiv. 60.000 EUR + fără activ. specifice) / 3% | `[expert-CONF]` art.51 | prag 60k + listă activități 3% de confirmat |
| Cotă profit | 16% | `[CF✓]` art.17 | |
| Prag înregistrare TVA (scutire) | **395.000 lei** | `[CF✓]` art.310 | Legea 141/2025 (de la 300.000 lei); data intrării de confirmat |
| Prag TVA la încasare | **4.500.000 → 5.000.000 lei** | `[CF✓]` art.282 | tranziție ianuarie 2026; data de fixat |
| Perioadă TVA | trim. dacă CA an ant. < 100.000 EUR ȘI fără achiziție IC în trim.; altfel lunar | `[CF✓]` art.322 | achiziția IC → lunar de la luna respectivă |
| SAF-T (D406) | **toate firmele** (mici de la 01.01.2025) | `[OPANAF]` 1783/2021 | calendar mici de confirmat |
| Cote TVA 2026 | **21% / 11% / 0%** | `[CF✓]` art.291 | Legea 141/2025 de la 01.08.2025; NU 19/9/5 |
| Salariu minim brut 2026 | de confirmat (HG) | `[expert-CONF]` | intră în plafoane CM/facilitate |

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
| **D112** contrib.+evidență salariați | CF Titlu V + OPANAF | lunar (trim. cu opțiune) | 25 | plătește venituri din salarii/asimilate |
| **D100** oblig. buget stat | OPANAF | lunar/trim. | 25 | are obligație de plată (impozit micro, dividend reținut, plăți anticipate profit…) |
| **D300** decont TVA | CF art.323 | lunar/trim. (param A) | 25 | înregistrat TVA (art.316) |
| **D301** decont special TVA | CF art.324 | pe operațiune | 25 | neînregistrat normal + achiziții IC >10.000 EUR / servicii B2B (art.317) |
| **D390** recapitulativă IC (VIES) | CF art.325 | lunar (lunile cu op.) | 25 | operațiuni intracomunitare (ROI) |
| **D394** op. naționale | OPANAF | urmează perioada D300 | 30 | înregistrat TVA, operațiuni interne |
| **D406 SAF-T** | OPANAF 1783/2021 | lunar/trim. (perioada TVA) + Active anual + Stocuri la cerere | ultima zi luna următoare | toate firmele |
| **D101** impozit profit | CF art.42 | anual | **25 iunie** an urm. (25 martie an modificat) | plătitor profit (NU micro) |
| **D205** impozit reținut sursă (rezidenți) | CF art.132 + OPANAF | anual | **ultima zi februarie** an urm. | a reținut la sursă (salarii, dividende…) |
| **D207** impozit reținut sursă **nerezidenți** — **ÎN VIGOARE** (rezolvat) | `[CF✓]` art.231 | anual | ultima zi februarie an urm. | plăți către nerezidenți cu reținere (dividende/dobânzi/redevențe/servicii) |
| **D710** rectificativă | OPANAF | la nevoie | — | corecție D100/D112/D300 |
| **Situații financiare anuale (bilanț)** | `[L82]` L82/1991 + OMFP 1802/2014 | anual | ~150 zile (≈30 mai) | toate societățile |
| ~~D392A/B~~ informativă CA (ne)plătitori | — | — | — | **ABROGAT (rezolvat)** — nu se mai depune; nicio firmă de test nu-l are |

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

Note: „(x)" = condiționat (doar dacă apare operațiunea). e-Factura B2B = obligatoriu la orice firmă care emite facturi
B2B. e-Transport = doar la transport de bunuri (marcat DA unde e caracteristic firmei, ex. S3 agricultor cu produse).

---

## D. NOTE PER-PERIOADĂ 2026
- Cote TVA **21/11/0 pe tot 2026** (nu 19/9/5). Prag micro **100k EUR de la 01.01.2026** (era 250k → celula T2). TVA la
  încasare 4.5M→5M ianuarie 2026.
- **Ianuarie 2027:** D406 lună 12/2026 → 31.01; D300/D112 → 25.01; D394 → 30.01; D205+D207(2026) → 28.02; D101(2026) →
  25.06; bilanț 2026 → ~30.05. e-Factura/e-Transport = pe flux, nu la termen fix.

---

## E. CELE 8 CONFIRMĂRI RĂMASE (la sursă, ÎNAINTE de C-2 — firmele se derivă din matrice, nu se presupun)
1. **Cota micro 1% vs 3%**: pragul 60.000 EUR + lista activităților la 3% (CF art.51, formă 2026). Sursă: CF consolidat art.51.
2. **Lista CAEN excluse de la micro 2026** (consultanță/management >20%, HoReCa etc.). Sursă: CF art.47 + OUG modificatoare.
3. **Data intrării pragului TVA 395.000 lei** + dacă e stabil pe tot 2026. Sursă: Legea 141/2025 art. + normă.
4. **Data tranziției TVA la încasare 4.5M→5M** în ianuarie 2026. Sursă: CF art.282 + Legea 141/2025.
5. **Salariul minim brut 2026** (HG salariu minim). Sursă: HG publicată în MO.
6. **Calendarul SAF-T firme mici** (confirmare 01.01.2025 + eventuale amânări). Sursă: OPANAF 1783/2021 + acte de amânare.
7. **D392** — confirmat ABROGAT (rezolvat aici); de re-verificat la sursă că nu a fost reintrodus.
8. **Periodicitatea D112 trimestrial** — care micro/mici pot opta. Sursă: CF Titlu V + OPANAF.
(D207 = confirmat ÎN VIGOARE, CF art.231.)

**Volum + CUI/CNP fictive (R1/R3):** NU se fixează în C-1 — se propun în C-2, unde CUI-urile fictive valide (cifra de
control OK) se verifică să NU aparțină firmelor reale înainte de a le fixa; coerența A↔B (facturi între firmele de test)
se asigură pe sume/CUI/date identice.
