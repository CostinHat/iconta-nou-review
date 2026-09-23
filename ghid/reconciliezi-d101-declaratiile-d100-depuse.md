---
title: "Cum reconciliezi D101 cu declarațiile D100 depuse în cursul anului?"
description: Dacă o microîntreprindere depășește plafonul în cursul anului, D100 (trimestrele de dinainte de depășire, la impozit micro) și D101 (impozitul pe profit, de la trimestrul depășirii înainte) acoperă perioade diferite ale aceluiași an — nu se „reconciliază" una cu alta, ci se însumează cronologic.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum reconciliezi D101 cu declarațiile D100 depuse în cursul anului?

Când o firmă începe anul ca microîntreprindere (declarând trimestrial D100, la 1%) și, la un moment dat în cursul anului, depășește plafonul de 100.000 euro venituri, trece la impozit pe profit — declarat prin D101, la finalul anului. Întrebarea „cum reconciliez D101 cu D100" pornește de la o presupunere greșită: cele două declarații nu se reconciliază, pentru că nu acoperă aceleași venituri.

## Temeiul legal

::: ghid-temei
„Dacă în cursul unui an fiscal o microîntreprindere realizează venituri mai mari de 100.000 euro, aceasta datorează impozit pe profit începând cu trimestrul în care s-a depășit această limită." — Codul fiscal, art. 52 alin. (1). „Calculul și plata impozitului pe profit de către microîntreprinderile care se încadrează în prevederile alin. (1) […] se efectuează luând în considerare veniturile și cheltuielile realizate începând cu trimestrul respectiv." — art. 52 alin. (6).
:::

## Cum se împart perioadele

- **Trimestrele de dinainte de depășirea plafonului** — rămân impozitate ca microîntreprindere, la 1%, declarate prin D100, așa cum au fost deja depuse. Nu se recalculează retroactiv la impozit pe profit.
- **De la trimestrul în care s-a depășit plafonul, până la finalul anului** — firma calculează și plătește impozit pe profit, luând în calcul **doar veniturile și cheltuielile realizate începând cu acel trimestru** (art. 52 alin. (6)) — nu veniturile/cheltuielile de la începutul anului. La final de an, această perioadă se raportează prin D101.

D101 nu „reface" ce a fost deja declarat prin D100 — acoperă strict perioada de după trecerea la impozit pe profit. Cele două declarații sunt complementare cronologic, nu suprapuse: împreună acoperă tot anul fiscal, fiecare cu regimul ei.

## Ce se greșește în practică

- Se încearcă recalcularea trimestrelor deja declarate ca micro (prin D100) în baza de calcul a impozitului pe profit raportat prin D101 — legea exclude explicit acest lucru (art. 52 alin. (6)): profitul se calculează doar din veniturile/cheltuielile de la trimestrul depășirii încolo.
- Se presupune că D101 trebuie să reflecte veniturile întregului an, inclusiv cele deja impozitate ca micro — ar duce la o dublă impunere a acelorași venituri, o dată prin D100 (1%), o dată prin D101 (16%).
- Se omite comunicarea către organul fiscal a ieșirii din sistemul de impunere micro, tratând schimbarea de regim ca automată doar pentru că depășirea plafonului a avut loc.

## Ce face iConta.eu

Fiecare trimestru se calculează independent, pe baza regimului fiscal (`regim_fiscal`) al firmei valabil la momentul rulării — verificat direct în cod, motorul de calcul D100 (`core/d100.py`) nu are nicio funcție de recalcul retroactiv al trimestrelor deja declarate ca micro. Practic, aplicația nu amestecă automat cele două regimuri într-o singură bază de calcul: trimestrele de micro rămân declarate prin D100 așa cum au fost, iar de la schimbarea de regim, firma trece pe fluxul de impozit pe profit pentru perioada rămasă din an.

[iConta.eu](/)
