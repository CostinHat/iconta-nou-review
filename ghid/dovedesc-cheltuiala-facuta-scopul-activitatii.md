---
title: "Cum dovedesc că o cheltuială este făcută în scopul activității PFA?"
description: "Condițiile generale din Codul fiscal pentru ca o cheltuială a unei persoane fizice autorizate să fie deductibilă la venitul net anual, determinat în sistem real."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum dovedesc că o cheltuială este făcută în scopul activității PFA?

Pentru o PFA care determină venitul net în sistem real, pe baza datelor din contabilitate, deductibilitatea unei cheltuieli nu se stabilește după cât de „rezonabilă" pare, ci după condițiile explicite din Codul fiscal — prima și cea mai importantă fiind legătura documentată cu activitatea independentă.

## Temeiul legal

::: ghid-temei
„Venitul net anual din activități independente se determină în sistem real, pe baza datelor din contabilitate, ca diferență între venitul brut și cheltuielile deductibile efectuate în scopul realizării de venituri [...].
(4) Condițiile generale pe care trebuie să le îndeplinească cheltuielile efectuate în scopul desfășurării activității independente, pentru a putea fi deduse, în funcție de natura acestora, sunt: a) să fie efectuate în cadrul activităților independente, justificate prin documente."
— Legea 227/2015, art. 68 alin. (1) și alin. (4) lit. a) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Practic, pentru a demonstra că o cheltuială e făcută în scopul activității PFA:

- Prima condiție, cea de bază: cheltuiala **să fie efectuată în cadrul activității independente** și **justificată prin documente** — factură, chitanță, contract, orice document care leagă cheltuiala de activitatea desfășurată, nu doar de o nevoie personală coincidentă.
- Cheltuiala trebuie **cuprinsă în exercițiul financiar al anului în care a fost plătită** (lit. b)) — nu poate fi „mutată" artificial dintr-un an în altul pentru optimizare fiscală.
- Dacă e vorba de active (mijloace fixe, echipamente), deducerea trebuie să respecte **regulile de amortizare** de la Titlul II (lit. d)) — nu se deduce integral, dintr-o dată, o investiție amortizabilă.
- Pentru cabinetele medicale specific, investițiile în mijloace fixe au o regulă proprie de deducere, la art. 28 alin. (20) (lit. e)) — un caz particular, util dacă PFA e din domeniul medical.
- Veniturile care **nu** constituie venit brut (deci nu intră în calculul de la art. 68) includ aporturile în numerar/natură la începerea activității, despăgubirile primite și sponsorizările/donațiile primite (art. 68 alin. (3)).

## Ce se greșește în practică

- Se deduce o cheltuială pe baza unei simple bonuri fiscale, fără alt document care să lege explicit achiziția de activitatea PFA — condiția de la lit. a) cere justificare prin documente, dar și legătura cu activitatea, nu doar existența unui bon.
- Se deduce integral, într-un singur an, o investiție care ar trebui amortizată conform regulilor de la Titlul II — încălcând condiția de la lit. d).
- Se include în venitul brut, la calculul venitului net, o sumă primită ca aport propriu la începerea activității sau ca despăgubire — aceste sume sunt expres excluse din venitul brut (art. 68 alin. (3)), deci nu ar trebui să majoreze baza impozabilă.

## Ce face iConta.eu

La data acestui ghid, pentru PFA în sistem real (partidă simplă) iConta.eu oferă registrul de încasări și plăți cu clasificare pe categorii de deductibilitate — deductibilă, limitată sau nedeductibilă (`core/rip_api.py`) — și motorul de calcul al Declarației unice/D212 (`core/d212_engine.py`), care determină venitul net anual și baza CAS/CASS din operațiunile introduse. Aplicația **nu verifică automat** dacă o cheltuială îndeplinește condițiile de la art. 68 alin. (4) (legătura cu activitatea, justificarea prin documente) — încadrarea fiecărei cheltuieli în categoria corectă de deductibilitate rămâne o judecată profesională a contabilului sau a titularului PFA, aplicația doar înregistrează și totalizează categoria aleasă.

[iConta.eu](/)
