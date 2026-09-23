---
title: "Se depune D101 dacă societatea a fost micro o parte din an?"
description: "Explică regula de trecere de la impozitul pe veniturile microîntreprinderilor la impozitul pe profit în cursul anului fiscal."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Se depune D101 dacă societatea a fost micro o parte din an?

## Temeiul legal

::: ghid-temei
Art.52 alin.(1) CF (modificat prin OUG 8/2026 art.6 pct.20, MO 147/25.02.2026): "Dacă în cursul unui an fiscal o microîntreprindere realizează venituri mai mari de 100.000 euro, aceasta datorează impozit pe profit începând cu trimestrul în care s-a depășit această limită."
— Legea 227/2015 (Codul fiscal) consolidată, `anaf_surse/cod_fiscal_227_2015_consolidat.txt`, dosar de cercetare F027.

Art.52 alin.(6) CF: "Calculul și plata impozitului pe profit de către microîntreprinderile care se încadrează în prevederile alin. (1), (2), (4) și (7) se efectuează luând în considerare veniturile și cheltuielile realizate începând cu trimestrul respectiv."
— Legea 227/2015 (Codul fiscal) consolidată, `anaf_surse/cod_fiscal_227_2015_consolidat.txt`, dosar de cercetare F027.
:::

Da. Dacă în cursul anului o microîntreprindere depășește plafonul de 100.000 EUR venituri, ea devine plătitoare de impozit pe profit începând cu trimestrul în care s-a depășit limita (art.52 alin.(1)) și, din acel moment, intră sub obligația de a depune D101 pentru definitivarea anuală a impozitului pe profit datorat pe partea de an în care a fost plătitoare de profit. Calculul se face luând în calcul veniturile și cheltuielile realizate începând cu trimestrul respectiv (art.52 alin.(6)), nu retroactiv pe tot anul.

## Ce se greșește în practică

Greșeala frecventă e recalcularea impozitului pe profit pentru întregul an, inclusiv perioada în care firma era încă la impozit micro — legea exclude explicit acest lucru (art.52 alin.(6)).

## Ce face iConta.eu

iConta.eu nu generează D101 fără CUI valid (verificat prin checksum, `core.identitate.valideaza_cui`), denumire, adresă și cod CAEN pe 4 cifre, plus datele de declarant complete (`erori_generare`, `core/d101.py`). În aplicație: Declarații → D101 → anul → Generează (ecranul mapează codul `d101` la fișa de ajutor F027, `static/js/ecrane/declaratii.js`). Restul completării (cota 16%, P11, P13, P23/P34, P43) urmează structura standard, aplicată doar perioadei de la trimestrul de trecere înainte.

[iConta.eu](/)
