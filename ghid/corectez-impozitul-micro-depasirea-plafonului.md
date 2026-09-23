---
title: "Cum corectez impozitul micro după depășirea plafonului?"
description: Dacă depășirea plafonului de 100.000 euro a fost descoperită după ce trimestrele următoare au fost greșit declarate tot ca impozit micro, corectarea nu recalculează trimestrele dinainte de depășire — ci schimbă regimul, de la trimestrul depășirii, la impozit pe profit, declarat separat.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum corectez impozitul micro după depășirea plafonului?

Dacă se descoperă, la un moment dat, că firma a depășit plafonul de 100.000 euro venituri într-un trimestru anterior și a continuat totuși să declare impozit micro (D100) pentru trimestrele următoare, corectarea nu înseamnă recalcularea tuturor trimestrelor anului la impozit pe profit — legea desparte explicit ce se recalculează și ce rămâne neschimbat.

## Temeiul legal

::: ghid-temei
„Dacă în cursul unui an fiscal o microîntreprindere realizează venituri mai mari de 100.000 euro, aceasta datorează impozit pe profit începând cu trimestrul în care s-a depășit această limită." — Codul fiscal, art. 52 alin. (1). „Calculul și plata impozitului pe profit […] se efectuează luând în considerare veniturile și cheltuielile realizate începând cu trimestrul respectiv." — art. 52 alin. (6).
:::

## Ce se recalculează și ce nu

- **Trimestrele de dinainte de depășire** — rămân la impozit micro, exact cum au fost declarate; legea nu prevede recalcularea lor retroactivă.
- **Trimestrul depășirii și cele următoare, declarate greșit tot ca micro** — acestea trebuie corectate: impozitul micro declarat pentru ele (prin D100) a fost incorect, pentru că de la acel trimestru firma datora impozit pe profit, nu impozit micro. Corecția presupune, pentru fiecare astfel de trimestru: anularea/rectificarea impozitului micro declarat greșit (prin formularul 710) și calcularea/declararea impozitului pe profit corect pentru perioada respectivă.

## Pașii practici

1. Stabiliți exact trimestrul în care s-a depășit plafonul (verificarea se face cumulat de la începutul anului, la cursul de schimb valabil la închiderea exercițiului financiar precedent).
2. Comunicați ieșirea din sistemul de impunere micro către organul fiscal competent.
3. Corectați, prin formularul 710, impozitul micro declarat greșit pentru trimestrele de după depășire.
4. Calculați și declarați impozitul pe profit pentru perioada de la trimestrul depășirii încolo, luând în calcul doar veniturile și cheltuielile din acea perioadă (art. 52 alin. (6)), nu pe tot anul.
5. Verificați dacă din corecție rezultă o plată suplimentară cu întârziere față de scadențele inițiale — se calculează dobânzi și penalități de la acele scadențe, nu de la data corecției.

## Ce se greșește în practică

- Se recalculează greșit inclusiv trimestrele de dinainte de depășire, deși legea le lasă neschimbate.
- Se continuă declararea trimestrială prin D100 pentru perioada de după depășire, în loc de trecerea la fluxul de impozit pe profit.
- Se omite comunicarea oficială a ieșirii din regimul micro către organul fiscal, tratând schimbarea de regim ca implicită doar din depășirea plafonului.

## Ce face iConta.eu

Fiecare trimestru se calculează independent, pe baza regimului fiscal (`regim_fiscal`) setat pentru firmă — verificat direct în cod, aplicația nu recalculează automat trimestrele anterioare când regimul se schimbă. Schimbarea regimului fiscal, o dată constatată depășirea plafonului, rămâne o decizie și o acțiune manuală a contabilului; corectarea trimestrelor deja declarate greșit ca micro se face prin formularul 710 (`core/d710.py`), iar calculul impozitului pe profit pentru perioada corectă urmează fluxul specific acelui regim, separat de D100.

[iConta.eu](/)
