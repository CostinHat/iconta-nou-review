---
title: "Se recalculează impozitul pe profit de la începutul anului după ieșirea din regimul micro?"
description: "Răspunde direct, pe temei legal, dacă ieșirea din regimul micro impune recalcularea retroactivă a impozitului pe profit."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Se recalculează impozitul pe profit de la începutul anului după ieșirea din regimul micro?

## Temeiul legal

::: ghid-temei
Art.52 alin.(6) CF: "Calculul și plata impozitului pe profit de către microîntreprinderile care se încadrează în prevederile alin. (1), (2), (4) și (7) se efectuează luând în considerare veniturile și cheltuielile realizate începând cu trimestrul respectiv."
— Legea 227/2015 (Codul fiscal) consolidată, `anaf_surse/cod_fiscal_227_2015_consolidat.txt`, dosar de cercetare F027.

Art.52 alin.(1) CF (modificat prin OUG 8/2026 art.6 pct.20, MO 147/25.02.2026): "Dacă în cursul unui an fiscal o microîntreprindere realizează venituri mai mari de 100.000 euro, aceasta datorează impozit pe profit începând cu trimestrul în care s-a depășit această limită."
— Legea 227/2015 (Codul fiscal) consolidată, `anaf_surse/cod_fiscal_227_2015_consolidat.txt`, dosar de cercetare F027.
:::

Nu. Art.52 alin.(6) este explicit: calculul și plata impozitului pe profit, pentru microîntreprinderile care depășesc plafonul în cursul anului, „se efectuează luând în considerare veniturile și cheltuielile realizate începând cu trimestrul respectiv” — nu de la începutul anului fiscal. Perioada anterioară trimestrului de depășire rămâne impozitată conform regulilor de impozit micro (pe venit, cota corespunzătoare), fără recalculare retroactivă.

## Ce se greșește în practică

Greșeala tipică e tocmai recalcularea pe tot anul, dintr-o asumpție intuitivă că „odată depășit plafonul, redevii plătitor de profit din ianuarie” — legea spune contrariul, explicit.

## Ce face iConta.eu

iConta.eu nu generează D101 fără CUI valid (verificat prin checksum, `core.identitate.valideaza_cui`), denumire, adresă și cod CAEN pe 4 cifre, plus datele de declarant complete (`erori_generare`, `core/d101.py`). În aplicație: Declarații → D101 → anul → Generează (ecranul mapează codul `d101` la fișa de ajutor F027, `static/js/ecrane/declaratii.js`).

[iConta.eu](/)
