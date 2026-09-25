---
title: "Ratele de leasing operațional sunt deductibile fiscal?"
description: "Ca regulă generală, da — dar pentru vehicule rutiere motorizate folosite și în scop personal, deductibilitatea chiriei de leasing scade la 50%, cu excepții expres prevăzute de lege."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Ratele de leasing operațional sunt deductibile fiscal?

Ca regulă generală, da — chiria (rata) de leasing operațional e o cheltuială deductibilă la calculul rezultatului fiscal. Dar dacă bunul e un vehicul rutier motorizat și nu e folosit exclusiv în scopul activității economice, deductibilitatea acestei cheltuieli scade la 50%, cu o listă de excepții în care rămâne 100%.

## Temeiul legal

::: ghid-temei
**Legea 227/2015 (Codul fiscal), art. 29 alin. (3)**: „În cazul leasingului financiar utilizatorul deduce dobânda, iar în cazul leasingului operațional locatarul deduce chiria (rata de leasing), potrivit prevederilor prezentului titlu."

**Legea 227/2015, art. 25 alin. (3) lit. l)**: „50% din cheltuielile aferente vehiculelor rutiere motorizate care nu sunt utilizate exclusiv în scopul activității economice, cu o masă totală maximă autorizată care să nu depășească 3.500 kg și care să nu aibă mai mult de 9 scaune de pasageri, incluzând și scaunul șoferului, aflate în proprietatea sau în folosința contribuabilului. Aceste cheltuieli sunt integral deductibile pentru situațiile în care vehiculele respective se înscriu în oricare dintre următoarele categorii: 1. vehiculele utilizate exclusiv pentru servicii de urgență, servicii de pază și protecție și servicii de curierat; 2. vehiculele utilizate de agenții de vânzări și de achiziții; 3. vehiculele utilizate pentru transportul de persoane cu plată, inclusiv pentru serviciile de taximetrie; 4. vehiculele utilizate pentru prestarea de servicii cu plată, inclusiv pentru închirierea către alte persoane sau pentru instruire de către școlile de șoferi; 5. vehiculele utilizate ca mărfuri în scop comercial. Cheltuielile care intră sub incidența acestor prevederi nu includ cheltuielile privind amortizarea."
— (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

- Pentru bunuri care nu sunt vehicule rutiere motorizate (utilaje, echipamente, spații) — chiria de leasing operațional rămâne integral deductibilă, atât timp cât e o cheltuială efectuată în scopul activității economice.
- Pentru vehicule rutiere motorizate ≤3.500 kg și ≤9 locuri, folosite și în scop personal — deductibilitatea chiriei scade la **50%**.
- Excepțiile care păstrează deductibilitatea de 100% sunt limitativ enumerate: vehicule de intervenție/pază/curierat, agenți de vânzări, taximetrie, servicii cu plată (inclusiv închiriere sau școli de șoferi), vehicule folosite ca marfă.
- Textul precizează explicit că plafonul de 50% **nu include cheltuielile cu amortizarea** — deci nu se confundă cu plafonul separat de amortizare al autoturismelor (1.500 lei/lună, art. 28 alin. (14)).

## Ce se greșește în practică

- Se aplică automat plafonul de 50% la orice chirie de leasing operațional, inclusiv la utilaje sau echipamente fără nicio legătură cu vehiculele rutiere.
- Se uită să se verifice dacă vehiculul se încadrează la vreuna din cele cinci excepții — caz în care chiria e integral deductibilă, nu la 50%.
- Se confundă plafonul de 50% pentru cheltuiala cu chiria cu plafonul (tot de 50%, dar de o natură diferită, de TVA) aplicat dreptului de deducere a taxei pentru aceleași vehicule — cele două limitări sunt distincte și se aplică separat.

## Ce face iConta.eu

Funcția `nota_rata_operational` din F056 (Leasing financiar și operațional) generează doar nota contabilă brută a chiriei — 612=401, plus TVA pe 4426 — fără nicio verificare sau aplicare automată a plafonului de 50% pentru vehicule. iConta.eu **nu automatizează** încadrarea unui vehicul la excepțiile de mai sus și nici calculul plafonului fiscal; aplicarea corectă a limitării, la calculul rezultatului fiscal, rămâne în sarcina contabilului.

[iConta.eu](/)
