---
title: "Cum calculezi impozitul pe profit când firma trece de la micro la profit în 2026?"
description: "Detaliază regula legală de calcul al impozitului pe profit pentru firma care depășește plafonul de micro în cursul lui 2026."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum calculezi impozitul pe profit când firma trece de la micro la profit în 2026?

## Temeiul legal

::: ghid-temei
Art.52 alin.(1) CF (modificat prin OUG 8/2026 art.6 pct.20, MO 147/25.02.2026): "Dacă în cursul unui an fiscal o microîntreprindere realizează venituri mai mari de 100.000 euro, aceasta datorează impozit pe profit începând cu trimestrul în care s-a depășit această limită."
— Legea 227/2015 (Codul fiscal) consolidată, `anaf_surse/cod_fiscal_227_2015_consolidat.txt`, dosar de cercetare F027.

Art.52 alin.(6) CF: "Calculul și plata impozitului pe profit de către microîntreprinderile care se încadrează în prevederile alin. (1), (2), (4) și (7) se efectuează luând în considerare veniturile și cheltuielile realizate începând cu trimestrul respectiv."
— Legea 227/2015 (Codul fiscal) consolidată, `anaf_surse/cod_fiscal_227_2015_consolidat.txt`, dosar de cercetare F027.

Art.53 alin.(2) lit.b) CF: la trecerea la impozit pe profit, elementele de curs valutar sunt tratate ca „elemente similare veniturilor în primul trimestru pentru care datorează impozit pe profit" — confirmă aceeași logică pe trimestru, nu retroactiv pe an.
— Legea 227/2015 (Codul fiscal) consolidată, `anaf_surse/cod_fiscal_227_2015_consolidat.txt`, dosar de cercetare F027.
:::

Firma care depășește în cursul anului 2026 plafonul de 100.000 EUR venituri datorează impozit pe profit începând cu trimestrul în care a depășit limita (art.52 alin.(1)). Calculul și plata se fac luând în calcul doar veniturile și cheltuielile realizate începând cu acel trimestru (art.52 alin.(6)) — nu se recalculează retroactiv de la 1 ianuarie. Chiar și elementele de curs valutar la trecere sunt tratate ca venituri ale primului trimestru de impozit pe profit (art.53 alin.(2) lit.b)), confirmând aceeași logică pe trimestru.

## Ce se greșește în practică

Cea mai frecventă greșeală e considerarea firmei ca plătitoare de impozit pe profit pentru tot anul 2026, cu recalcularea perioadei anterioare (deja impozitată la venit, în regim micro) — legea interzice explicit acest lucru.

## Ce face iConta.eu

iConta.eu nu generează D101 fără CUI valid (verificat prin checksum, `core.identitate.valideaza_cui`), denumire, adresă și cod CAEN pe 4 cifre, plus datele de declarant complete (`erori_generare`, `core/d101.py`). În aplicație: Declarații → D101 → anul → Generează (ecranul mapează codul `d101` la fișa de ajutor F027, `static/js/ecrane/declaratii.js`). Cota aplicată rămâne 16% (art.17), pe profitul impozabil aferent perioadei de la trimestrul de trecere.

[iConta.eu](/)
