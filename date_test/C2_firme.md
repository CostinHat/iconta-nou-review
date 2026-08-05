# C-2. SETUL MINIM DE FIRME DE TEST — derivat din matricea C-1 (VALIDAT Costin 05.08.2026, cu S4 adăugată)

**Scop:** setul minim de firme care acoperă TOATE celulele distincte ale matricei C-1 validate, cu regimuri, CUI-uri
fictive verificate, rețea de coerență (R3), volum propus (R1) și, per firmă, ce celule acoperă / ce declarații datorează
/ ce o face distinctă.
**Derivare număr:** matricea C-1 are **11 celule distincte** (M1, M2, P1, P2, N1, S1, S2, S3, NR1, T1, T2) ⇒ 11 firme
(„o firmă de test per celulă distinctă"). **+ S4** (completare Costin 05.08): salarizare în situații speciale — NU e o
celulă declarativă a matricei, ci **dimensiunea D112 complex** (zona cu cel mai mare istoric de bug-uri; toate cele 4
neconformități fiscale din 05.08 au fost acolo), pe care matricea celulară n-o izolează. **Total: 12 firme.** Numărul
IESE din matrice + dimensiunea de salarizare, nu e fixat dinainte. Obligațiile e-Factura/e-Transport se acoperă
TRANSVERSAL (nu adaugă firme): e-Factura la orice firmă B2B, e-Transport la S3 (+ opțional P1).

**Decizii Costin (VALIDATE 05.08.2026):** (1) CAEN — OK cum propus. (2) S1/S2 = profit (exercită D101). (3) T2 =
scenariul *depășire prag* (păstrează salariatul→D112); *pierderea de salariat* e acoperită de N1 (art.48(3)). (4)
Volume R1 — intervale validate (~1200–1800 doc/an set, P1 300–400, N1 20–40), fără ținte fixe. (5) CUI — re-verificare
ANAF v9 OBLIGATORIE la momentul seed-ului; dacă vreunul apare `gasit=True`, se înlocuiește din rezervă.

---

## A. CUI-URI FICTIVE — valide structural + VERIFICATE la ANAF că NU aparțin unor firme reale

**Metodă:** generate cu cifra de control oficială (cheia `[7,5,3,2,1,7,5,3,2]`, aceeași ca `core/solduri_parteneri_api.valideaza_cui`),
apoi **interogate la ANAF webservice v9** (`core/anaf_api.valideaza_cui`, endpoint `PlatitorTvaRest/v9/tva`) la data
**2026-08-05**. Toate cele 45 de candidate au întors `gasit=False` (notFound) — 0 firme reale. Cele 12 folosite mai jos
+ 2 rezervă sunt din acest lot verificat. Sunt CUI-uri de **8 cifre în plaja 95–96 milioane**, peste frontiera curentă
de alocare ANAF (~50 mil.) → structural valide, dar neatribuite.

> **Notă onestitate + decizia (5) Costin:** verificarea garantează „neatribuit la 2026-08-05". **Re-verificare ANAF v9
> OBLIGATORIE la momentul seed-ului** — dacă vreun CUI apare `gasit=True` atunci, se înlocuiește din rezervă. CUI-urile
> plătitorilor de TVA se afișează cu prefix `RO`.

| firmă | CUI (fictiv, verificat ANAF) | plătitor TVA |
|---|---|---|
| M1 | 95138914 | nu |
| M2 | RO95141537 | da |
| P1 | RO95275466 | da |
| P2 | RO95363126 | da |
| N1 | 95451848 | nu (dar cod special art.317 pt IC) |
| S1 | RO95687300 | da |
| S2 | RO95775518 | da |
| S3 | 95873249 | nu (regim forfetar agricol) |
| NR1 | RO95904434 | da |
| T1 | 96385785 → RO96385785 (dacă depășește pragul după înființare) | după caz |
| T2 | RO96516171 | da |
| **S4** | RO96653616 | da |
| *rezervă* | 96756476, 96939899 | — |

**CNP-uri (salariați/copii/persoane îngrijite):** NU se fixează în C-2 (firmele) — aparțin lui C-4 (datele). Se vor
genera cu cheia oficială `279146358279` (validator `core/salariati_import_api`), structură validă (dată naștere + județ
+ cifră control). **Caveat declarat:** spre deosebire de CUI, nu există registru public de verificare a non-existenței
unui CNP — un CNP valid structural POATE coincide cu o persoană reală. Se vor folosi date de naștere/secvențe implauzibile
și se va marca explicit „fictiv, nedeverificabil la sursă" (predare ★★: „dacă nu poți garanta, spune-o"). Numărul de
salariați per firmă e fixat mai jos (dimensiune de volum), CNP-urile concrete vin în C-4.

---

## B. FIRMELE — spec per celulă

Legendă declarații: cf. matricea C-1 secțiunea B/C. „TVA per." = perioada fiscală TVA (art.322).

### M1 — Micro, neplătitor TVA, cu salariat, fără IC, an complet
- **CUI** 95138914 · **regim_fiscal** micro · **platitor_tva** nu · **CAEN** 9602 (coafură/înfrumusețare) · **salariați** 1 · **an** complet 2026.
- **Declarații:** D112 (lunar), D100 (impozit micro 1%), D406 (SAF-T — obligatoriu toate firmele), D205 (reținut la sursă salarii), bilanț. e-Factura la facturile B2B emise. **FĂRĂ** D300/D394/D390/D101/D301.
- **Distinctă prin:** cel mai simplu regim micro — sub pragul TVA (neplătitor) DAR cu salariat + SAF-T obligatoriu. Testează firma fără TVA care totuși datorează D112+D406.

### M2 — Micro, plătitor TVA trimestrial, cu salariat, fără IC
- **CUI** RO95141537 · **micro** · **platitor_tva** da · **TVA per.** trimestrial (CA an ant. < 100.000 EUR, fără IC — art.322(2)) · **CAEN** 4711 · **salariați** 1.
- **Declarații:** D112, D100, D300 (trim), D394 (trim), D406, D205, bilanț, e-Factura. **FĂRĂ** D390 (fără IC)/D101.
- **Distinctă prin:** micro CU TVA **trimestrial** → testează perioada TVA trimestrială + D394 fără componentă IC. Perechea M1↔M2 izolează efectul „plătitor vs neplătitor" la același regim micro.

### P1 — Profit, plătitor TVA lunar, cu salariați, CU achiziții IC, an complet
- **CUI** RO95275466 · **profit** · **platitor_tva** da · **TVA per.** lunar (are achiziții IC — art.322) · **CAEN** 4669 · **salariați** 3.
- **Declarații:** D112, D100 (plăți anticipate/impozit), D300 (lunar), **D390** (VIES), D394 (lunar), D406, **D101** (profit, 25 iunie 2027), D205, bilanț, e-Factura. e-Transport dacă transportă bunuri (opțional).
- **Distinctă prin:** SINGURA cu achiziții IC + TVA lunar → testează D390 (recapitulativă IC), D300 achiziții IC/taxare inversă, D394 lunar cu volum. Nodul central al rețelei de coerență (vinde către M2/P2, cumpără de la M1/NR1/S3).

### P2 — Profit, plătitor TVA trimestrial, cu salariați, fără IC
- **CUI** RO95363126 · **profit** · **platitor_tva** da · **TVA per.** trimestrial (CA < 100.000 EUR, fără IC) · **CAEN** 4321 · **salariați** 2.
- **Declarații:** D112, D100, D300 (trim), D394 (trim), D406, D101, D205, bilanț, e-Factura. **FĂRĂ** D390.
- **Distinctă prin:** profit DAR sub pragul TVA (perioadă trimestrială) → izolează „profit cu D300 trimestrial" de P1 (profit lunar). Perechea P1↔P2 = efectul perioadei TVA la același regim de profit.

### N1 — Neplătitor TVA, micro fără salariat (art.48(3)), achiziții IC > 10.000 EUR
- **CUI** 95451848 · **micro fără salariat** (art.48(3)) · **platitor_tva** nu (normal) DAR cod special TVA pt IC (art.317) · **CAEN** 4791 · **salariați** 0.
- **Declarații:** D100, **D301** (decont special TVA — achiziții IC > 10.000 EUR de la neplătitor, art.317+324), D406. **FĂRĂ** D112 (fără salariat), D300, D205, D101.
- **Distinctă prin:** SINGURA fără salariat + SINGURA cu D301 → testează art.48(3) (micro fără salariat) + art.317 (achiziție IC de neplătitor > 10k EUR → înregistrare specială + D301). Nu emite D390 (nu e plătitor normal).

### S1 — Regim special TVA agenție de turism (art.311), plătitor TVA, cu salariați
- **CUI** RO95687300 · **profit** · **platitor_tva** da (regim marjă) · **TVA per.** lunar · **CAEN** 7911/7912 · **salariați** 2.
- **Declarații:** D112, D100, **D300 pe MARJĂ** (art.311 — TVA pe marjă, nu pe preț total; suta mărită cotă/(100+cotă); scutire proporțională non-UE), D394, D406, D101, D205, bilanț, e-Factura.
- **Distinctă prin:** TVA pe **marjă** (art.311) → rânduri D300 pe marjă, nu pe bază integrală. Testează regimul special turism.

### S2 — Regim special second-hand / opere de artă / obiecte de colecție (art.312), plătitor TVA
- **CUI** RO95775518 · **profit** · **platitor_tva** da (regim marjă) · **TVA per.** lunar · **CAEN** 4779 · **salariați** 1.
- **Declarații:** D112, D100, **D300 pe MARJĂ** (art.312 — TVA pe marjă per bun/global; marjă negativă → 0), D394, D406, D101, D205, bilanț, e-Factura.
- **Distinctă prin:** marjă per bun cu regula marjă-negativă→0 (art.312), diferită de marja turism (art.311). Perechea S1↔S2 = cele două regimuri de marjă distincte.

### S3 — Agricultor regim special (art.315^1)
- **CUI** 95873249 · **regim forfetar agricol** (art.315^1 — procent forfetar de compensație; nu deduce/nu colectează normal) · **platitor_tva** nu · **CAEN** 0111 · **salariați** 0 (sezonieri tratați în C-4 dacă e cazul).
- **Declarații:** D100 (după caz), D406, **e-Transport** (transport produse agricole — risc fiscal ridicat). Interacțiune cheie: **D394 achiziție de la agricultor forfetar** la CUMPĂRĂTOR (P1/S2) — exceptia numită a campaniei (achiziția orfană de factură, GARZI l.~1026). **FĂRĂ** D300 (forfetar), D390.
- **Distinctă prin:** regim forfetar agricol + e-Transport pe transport de produse → singura care declanșează e-Transport caracteristic + latura „achiziție de la agricultor forfetar" în D394 la partenerul din set.

### NR1 — Profit, plătitor TVA, cu plăți către nerezidenți (redevențe/servicii)
- **CUI** RO95904434 · **profit** · **platitor_tva** da · **TVA per.** lunar · **CAEN** 6201 (IT) · **salariați** 2.
- **Declarații:** D112, D100, D300, D394, D406, D101, D205, **D207** (impozit reținut la sursă NEREZIDENȚI — art.231, ultima zi februarie 2027), bilanț, e-Factura.
- **Distinctă prin:** SINGURA cu **D207** → plăți către nerezidenți cu reținere la sursă (dividende/dobânzi/redevențe/servicii). Testează calea D207 (în vigoare, art.231), distinctă de D205 (rezidenți).

### T1 — Înființată la mijloc de an (an PARȚIAL), micro cu salariat
- **CUI** 96385785 (→ RO96385785 dacă depășește pragul de înregistrare TVA după înființare) · **micro** · **înființare** ~2026-07-01 · **CAEN** 6201 · **salariați** 1 (angajat după înființare).
- **Declarații:** D112 (din luna angajării), D100, D406, D205, bilanț (parțial), e-Factura. TVA (D300/D394) DOAR dacă se înregistrează după înființare. **FĂRĂ** D101 (micro).
- **Distinctă prin:** an fiscal **PARȚIAL** → testează luni parțiale (angajare la mijloc), praguri recalculate proporțional (art.322(3)-(4) TVA, plafon micro pe perioada rămasă), bilanț parțial. Complementul lui M1 pe axa timp.

### T2 — Micro → profit în cursul lui 2026 (depășire 100.000 EUR / pierdere salariat)
- **CUI** RO96516171 · **regim** micro → profit (trecere ex. de la trim. IV 2026, la depășirea plafonului de 100.000 EUR sau pierderea unicului salariat — art.52) · **platitor_tva** da · **CAEN** 4652 · **salariați** 1 (→ scenariul de depășire prag, nu pierdere salariat, pentru a păstra D112).
- **Declarații:** D112, D100 (impozit micro până la trecere), D300, D394, D406, **D101 de la trecere** (pro-rata profit din trimestrul trecerii), D205, bilanț, e-Factura.
- **Distinctă prin:** TRANZIȚIE de regim în cursul anului → testează comutarea micro→profit (D100 micro se oprește, D101 profit începe de la trimestrul trecerii), art.52. Singura cu două regimuri CIT în același an. Pereche pe axa timp cu M2 (micro TVA) → arată ce se schimbă la trecere.

### S4 — Salarizare în situații speciale (dimensiunea D112 complex) — completare Costin 05.08
- **CUI** RO96653616 · **regim_fiscal** profit · **platitor_tva** da · **TVA per.** lunar · **CAEN** 1071 (fabricarea pâinii — forță de muncă numeroasă, ture, part-time) · **salariați** 8–12.
- **De ce profit (nu micro):** 8–12 salariați → CA realistă > 100.000 EUR (numai salariile brute la minim ≈ 78k EUR/an) → profit e regimul COERENT cu volumul (R1). Salarizarea — focusul S4 — e independentă de regimul de impozitare, cum ai spus; reversibil la micro dacă preferi (nu schimbă testarea D112).
- **Matricea de situații de salarizare** (distribuite pe cei 8–12 salariați, se detaliază numeric în C-4):
  - **CM pe toate codurile** cerute: 01 (boală obișnuită, progresiv 55/65/75), 07 (carantină 100%), 08 (maternitate/sarcină), 09 (îngrijire copil bolnav), 10 (risc maternal), 15, **17 (boli cardiovasculare 75%)**, 91/92. Cotele/procentele = `core/salarizare._procent_cm_l141_2025`.
  - **salariat cu MAI MULTE certificate CM în aceeași lună** → testează Σ(round per certificat) vs round(Σ) (datoria „2b rotunjire") + baza CM realizată pe zile lucrate.
  - **part-time cu bază minimă CASS** (suprataxare art.146 alin.(5^6): baza ridicată la max(brut, sm−facilitate)).
  - **tichete**: masă, vacanță (cu exces peste plafon 6 SM → INTRĂ în bază), culturale, creșă.
  - **facilitate salariu minim** (construcții/IT/agroalimentar: baza_contrib = sm − facilitate).
  - **luni parțiale de angajare** (angajare la mijloc de lună → proratare).
- **Declarații:** D112 (lunar — FOCUS), D100, D300 (lunar), D394, D406, D101, D205, bilanț, e-Factura.
- **Distinctă prin:** concentrează TOATĂ complexitatea D112 — zona cu cel mai mare istoric de bug-uri (cele 4 neconformități fiscale din 05.08 au fost aici: baza CM = câștig realizat, poarta cale2 pe valorile emise, impozit CM neimpozabil, suprataxare part-time). Singura cu 8–12 salariați și matrice completă CM/tichete/facilitate/part-time/luni parțiale. Restul firmelor au 0–3 salariați cu situații simple; S4 e „stresul" pe salarizare.

---

## C. R3 — REȚEAUA DE COERENȚĂ (facturi între firme din set: CUI + sume + date IDENTICE pe ambele laturi)

„Coloana vertebrală" de tranzacții A→B cu ambele firme în set. Pe fiecare, emitentul și primitorul înregistrează
**exact** aceleași CUI/sumă/dată → controlul încrucișat (D394 vânzări↔cumpărări, control_incrucisat) și e-Factura B2B se
verifică din DATE, nu din cod. (Valorile de mai jos sunt schema de coerență; sumele exacte finale + volumul se așează în
C-4, dar perechile și regula „identice pe ambele laturi" sunt fixate aici.)

| # | emitent → primitor | natură | efect testat |
|---|---|---|---|
| T-1 | **P1 → M2** | marfă (import revândut) | D394 P1(vânzare) ↔ M2(achiziție); e-Factura B2B; TVA lunar↔trimestrial pe aceeași factură |
| T-2 | **P1 → P2** | marfă | D394 profit↔profit; perioade TVA diferite (lunar↔trim) pe aceeași tranzacție |
| T-3 | **M1 → P1** | servicii (înfrumusețare/protocol) | furnizor NEPLĂTITOR TVA → P1 achiziție fără drept de deducere; D394 latura „achiziție de la neplătitor" (tip document/partener neplătitor) |
| T-4 | **NR1 → P1** | servicii IT | prestator intern plătitor → P1; bază pt D394; (NR1 separat are latura nerezident pt D207 — furnizor EXTERN, nu în set) |
| T-5 | **S3 → P1** (sau S2) | produse agricole | **achiziție de la agricultor forfetar** în D394 la P1 (exceptia numită) + **e-Transport** la S3; procent forfetar compensare art.315^1 |
| T-6 | **P2 → S1** | amenajare (construcții) | S1 (marjă turism) primește achiziție normală cu TVA deductibilă — arată că regimul de marjă e doar pe VÂNZARE, nu pe achiziții |
| T-7 | **P1 → S4** | materii prime / utilaje (făină, echipamente) | leagă S4 în rețea; D394 P1(vânzare)↔S4(achiziție); e-Factura B2B; S4 = cumpărător cu TVA deductibilă normală |

**IC (intracomunitar) NU poate fi coerent intern** — o achiziție IC cere furnizor din alt stat membru. P1 (și N1) fac IC
de la un **furnizor UE EXTERN setului** (CUI/VAT dintr-un alt SM, marcat explicit ca extern). D390/D301 se verifică
structural, nu prin coerență A↔B. Declarat ca limită.

---

## D. R1 — VOLUM PROPUS per firmă/an (de justificat + validat de Costin)

Volumul e propus pe „câtă activitate reală are regimul", nu simbolic. Exersează paginare, reconciliere bancară, D394 cu
zeci de rânduri, D300 multi-rând, D406 SAF-T. „Documente" = facturi emise + facturi primite + extrase bancare/linii +
state de plată + chitanțe/bonuri.

| firmă | doc/an propus | justificare |
|---|---|---|
| **P1** | 300–400 | nod activ cu import: ~150 facturi emise + ~120 primite + ~30 extrase + 12 state; D394 lunar cu volum, D390, reconciliere bancară |
| **S4** | 200–320 | 8–12 salariați × 12 state + certificate CM multiple + activitate comercială panificație (vânzări zilnice); volumul de PAYROLL e miza, nu cel comercial |
| **T2** | 150–220 | activ pe tot anul + comutare de regim la mijloc (dublă contabilizare micro/profit) |
| **S1** | 150–220 | agenție turism: multe vânzări pe marjă + achiziții pachete |
| **NR1** | 130–200 | IT: facturi servicii recurente + plăți externe (nerezidenți) |
| **S2** | 120–180 | second-hand: volum de bunuri per marjă |
| **P2** | 120–180 | construcții local, TVA trimestrial |
| **M2** | 90–140 | comerț micro cu TVA trimestrial |
| **M1** | 50–90 | servicii micro mici, neplătitor |
| **T1** | 40–70 | jumătate de an (înființare 07.2026) |
| **S3** | 30–60 | agricol sezonier + transporturi (e-Transport) |
| **N1** | 20–40 | fără salariat, doar achiziții IC ocazionale + D301 |
| **TOTAL** | **~1.400–2.100 doc/an** (11 firme ~1.200–1.800 + S4 200–320) | volum realist pentru paginare/reconciliere/perf la nivel de platformă |

Fiecare tip de document își va marca în C-4 **calea de intrare** (R4): ecran vs seed (e-Factura, upload manual, OCR bon,
import bancă, tastare directă — fiecare cale distinctă exersată prin ecran cel puțin o dată; volumul intră prin seed).

---

## E. ACOPERIRE + DECIZII (VALIDATE)

**Acoperire celule matrice:** M1✓ M2✓ P1✓ P2✓ N1✓ S1✓ S2✓ S3✓ NR1✓ T1✓ T2✓ (11/11) **+ S4** (dimensiunea D112
complex). Regimuri speciale TVA art.311/312/315^1 = S1/S2/S3. e-Factura = toate firmele B2B (T-1…T-7). e-Transport = S3
(+ opțional P1 pe transport marfă). D207 = NR1. D301 = N1. Tranziții: T1 (an parțial), T2 (micro→profit). Salarizare
completă (CM toate codurile / tichete / facilitate / part-time / luni parțiale / multi-certificat) = S4.

**Decizii Costin — VALIDATE 05.08.2026:**
1. **CAEN** (9602/4711/4669/4321/4791/7911/4779/0111/6201/4652 + **1071** pt S4) — OK cum propus.
2. **S1/S2 = profit** — validat (exercită D101).
3. **T2 = depășire prag** (păstrează salariatul→D112) — validat; *pierderea de salariat* e acoperită de N1 (art.48(3)), deci nu se pierde nimic.
4. **Volume R1** — intervale validate (~1.200–1.800 doc/an set + S4; P1 300–400, N1 20–40), fără ținte fixe.
5. **CUI** — re-verificare ANAF v9 la seed OBLIGATORIE; `gasit=True` → înlocuire din rezervă (96756476, 96939899).

**Limite declarate:** pragul de înregistrare TVA (395.000) nu e enforced în aplicație (GARZI secțiunea D, decizie de
produs) — pentru T1/T2 statutul de plătitor se fixează manual, coerent cu scenariul. Achiziția IC nu are coerență A↔B
(furnizor UE extern). Achiziția de la agricultorul forfetar (T-5) atinge exceptia numită a campaniei (D394 orfan) — se
tratează ca atare, nu se forțează. CNP-urile (inclusiv cei 8–12 salariați ai lui S4) rămân pentru C-4 cu caveatul de
non-verificabilitate.

**C-2 VALIDAT (12 firme, cu S4). Următorul: C-3 (cabinetele/asistenții/clienții).**
