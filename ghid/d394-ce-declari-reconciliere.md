---
title: D394 — ce operațiuni declari și reconcilierea cu decontul
description: Ce operațiuni intră în D394, cum se grupează pe parteneri și cote și cum trebuie să se potrivească totalurile cu decontul de TVA (D300).
published: 2026-08-12
modified: 2026-08-12
---
# Ce operațiuni declari în D394, cum se grupează pe parteneri și cum se potrivesc cu decontul de TVA?

Declarația informativă D394 confruntă tranzacțiile B2B de pe teritoriul național cu ce declară partenerii tăi. Fiecare livrare și fiecare achiziție între persoane înregistrate în scopuri de TVA apare de două ori în sistemul ANAF: o dată la tine, o dată la celălalt. Când cele două nu se potrivesc — CUI greșit, cotă diferită, o factură scăpată — diferența nu rămâne ascunsă: ANAF o vede prin confruntarea automată a declarațiilor și îți cere lămuriri. În plus, totalurile pe cotă din D394 trebuie să fie coerente cu ce ai raportat în decontul de TVA (D300) pe aceeași perioadă.

## Temeiul legal / structura declarativă

::: ghid-temei
**D394 — „Declarație informativă privind livrările/prestările și achizițiile efectuate pe teritoriul național de persoane înregistrate în scopuri de TVA".** Ordinul de bază: **OPANAF 3769/2015**, actualizat prin **OPANAF 2194/2025** (cotele de TVA 21% și 11% de la 01.08.2025). Lista tipurilor de operațiune curentă provine din **OPANAF 77/2022** (M.Of. 95 din 31.01.2022).

**Structura fișierului XML:** elementul rădăcină poartă perioada (`luna`, `an`), **`tip_D394`** = tip declarație (`L` lunar / `T` trimestrial / `S` semestrial / `A` anual — aceeași periodicitate ca decontul de TVA), **`sistemTVA`** (`0` = sistem normal, `1` = TVA la încasare) și **`op_efectuate`** (`0` = fără operațiuni, `1` = cu operațiuni). Urmează identificarea, informațiile, apoi secțiunile de sinteză `rezumat1`, `rezumat2` și liniile detaliate `op1`.

**`tip_partener` — clasificarea partenerului:**
- **`=1` persoane impozabile înregistrate în scopuri de TVA în România**
- **`=2` persoane neînregistrate în scopuri de TVA**
- **`=3` persoane nestabilite în România, stabilite în alt stat membru**, neînregistrate și neobligate să se înregistreze în RO
- **`=4` persoane nestabilite în România și în afara UE**

**`cota`** ia valori în **(0, 5, 9, 11, 19, 20, 21, 24)** — cotele **21** și **11** au fost adăugate prin OPANAF 2194/2025 (aplicabile de la 01.08.2025).

**Tipurile de operațiune `op1.tip` (din OPANAF 77/2022):** A, L, C, V, AI, LS, AS, N.

**`rezumat1`** este unic pe perechea **(tip_partener, cota)** și se calculează din liniile `op1`. **`rezumat2`** agregă pe **cotă**, la nivel de firmă: livrarea (`L`) și achiziția (`A`) au câmpuri proprii, iar achiziția cu taxare inversă (`C`) se pliază pe achiziție (`A`).

**Nomenclatorul `codPR`** (produse pentru taxare inversă, `tip_partener = 1`): 21 Cereale și plante tehnice, 22 Deșeuri, 23 Masă lemnoasă, 24 Certificate emisii gaze, 25 Energie electrică, 26 Certificate verzi, 27 Construcții/terenuri, 28 Aur de investiții, 29 Telefoane mobile, 30 Microprocesoare, 31 Console/tablete/laptopuri, **36 Gaze naturale** (adăugat prin OPANAF 77/2022, aplicabil de la 01.04.2022, CF art. 331 alin. (2) lit. l).

**Notă istorică:** câmpurile pentru livrări către persoane fizice cu valoare individuală **mai mică sau egală cu 10.000 lei** există în structură, dar sunt **„Obligatoriu 0 începând cu 01.01.2017"**.
:::

## Regula concretă

Intră în D394 **livrările/prestările și achizițiile efectuate pe teritoriul național** — tranzacțiile interne, nu cele intracomunitare (acelea merg în D390). Fiecare factură devine o linie `op1`, clasificată pe două axe:

- **Tipul operațiunii** — dedus din direcția facturii și statutul partenerului: o factură emisă către un plătitor de TVA din RO e livrare (`L`, sau `V` la taxare inversă); o achiziție de la un plătitor RO e `A` (sau `C` la taxare inversă); o achiziție de la un neînregistrat sau o persoană fizică e `N`.
- **`tip_partener`** — din statutul TVA al partenerului: CUI valid RO + plătitor → `1`; neplătitor ori persoană fizică → `2`; partener din alt stat membru → `3`; din afara UE → `4`.

**Gruparea** se face în două trepte: fiecare partener apare cu CUI-ul lui (`cuiP`) în liniile `op1`, apoi `rezumat1` însumează pe perechea **(tip_partener, cota)**, iar `rezumat2` centralizează pe **cotă** la nivel de firmă.

**Legătura cu decontul de TVA (D300):** D394 se depune pe **aceeași perioadă fiscală** ca decontul. Totalurile pe cotă din `rezumat2` trebuie să fie coerente cu rândurile din decont. Atenție: **D394 este subsetul raportabil** (operațiunile interne între plătitori), iar decontul cuprinde TVA-ul total al firmei — relația e de incluziune, nu întotdeauna de egalitate strictă.

## Un exemplu

::: ghid-exemplu
**SC Exemplu SRL**, plătitoare de TVA cu regim lunar, luna iulie 2026 (cota standard 21%). Două achiziții interne, de la doi furnizori plătitori de TVA în România:

- **Furnizor A SRL** (`tip_partener = 1`, achiziție → `A`): bază **50.000 lei**, TVA 21% = **10.500 lei**.
- **Furnizor B SRL** (`tip_partener = 1`, achiziție → `A`): bază **30.000 lei**, TVA 21% = **6.300 lei**.

**În `op1`** apar două linii distincte, fiecare cu `cuiP`-ul furnizorului ei. **În `rezumat1`** se contopesc într-o singură linie pe (tip_partener = 1, cota = 21): **2 facturi**, bază = **80.000 lei**, TVA = **16.800 lei**. **În `rezumat2`**, pe cota 21%: bază **80.000 lei**, TVA **16.800 lei**.

Acest total de achiziții trebuie să se regăsească în TVA-ul deductibil din decontul lunii iulie 2026. Dacă în decont apare mai puțin, ai o factură nedeclarată în D394 sau invers; dacă apare mai mult, restul provine din operațiuni care nu intră în D394 (de exemplu achiziții intracomunitare) — de verificat, nu neapărat o eroare.
:::

## Ce se greșește în practică

::: ghid-procedura
- **CUI partener greșit → neconcordanță.** Un cod tastat greșit, sau un partener trecut ca plătitor când e neplătitor, schimbă `tip_partener` și `cuiP`; operațiunea nu se mai potrivește cu ce raportează partenerul, iar confruntarea automată ANAF scoate diferența.
- **Cotă greșită pe linie.** O factură pusă pe altă cotă (19% în loc de 21% după 01.08.2025) migrează în alt rezumat pe cotă — iar totalul nu mai corespunde rândului din decont.
- **Nedeclararea unei facturi.** O factură scăpată din D394 apare totuși la partener; la tine lipsește. Diferența se vede imediat la confruntarea încrucișată, chiar dacă TVA-ul din decont e corect.
:::

## Ce face iConta.eu

iConta.eu generează D394 direct din facturile emise și primite ale perioadei: clasifică fiecare factură pe `tip_partener` (din statutul TVA înghețat pe factură — cel de la momentul operațiunii, nu cel de azi) și pe tip de operațiune, calculează `rezumat1` pe (tip_partener, cota) și `rezumat2` pe cotă, atribuie `codPR`-ul la taxarea inversă și scrie XML-ul pe structura oficială ANAF. Generatorul **validează fără erori pe validatorul oficial ANAF (DUK)**.

Peste asta rulează o **a doua cale de reconciliere**: totalurile pe cotă sunt recalculate independent, din liniile brute ale facturilor, printr-un cod separat de generator. Dacă cele două căi diferă, generarea se **blochează** și îți sunt numite ambele valori și câmpul divergent — instrumentul nu alege singur cine are dreptate, ci îți semnalează să verifici. D394 e conectată și în semaforul de conformare fiscală. Depunerea o faci tu din SPV, cu XML-ul deja verificat.

[Deschide-ți cont pe iConta.eu](/) și lasă D394 să se genereze din facturi, cu totalurile reconciliate înainte de depunere.
