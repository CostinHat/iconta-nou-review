---
title: "Cum se calculează impozitul pe profit pentru primul trimestru după ieșirea din regimul micro?"
description: "Explică baza de calcul a primului trimestru de impozit pe profit după depășirea plafonului de micro."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se calculează impozitul pe profit pentru primul trimestru după ieșirea din regimul micro?

## Temeiul legal

::: ghid-temei
Art.52 alin.(1) CF (modificat prin OUG 8/2026 art.6 pct.20, MO 147/25.02.2026): "Dacă în cursul unui an fiscal o microîntreprindere realizează venituri mai mari de 100.000 euro, aceasta datorează impozit pe profit începând cu trimestrul în care s-a depășit această limită."
— Legea 227/2015 (Codul fiscal) consolidată, `anaf_surse/cod_fiscal_227_2015_consolidat.txt`, dosar de cercetare F027.

Art.53 alin.(2) lit.b) CF: la trecerea la impozit pe profit, elementele de curs valutar sunt tratate ca „elemente similare veniturilor în primul trimestru pentru care datorează impozit pe profit" — confirmă aceeași logică pe trimestru, nu retroactiv pe an.
— Legea 227/2015 (Codul fiscal) consolidată, `anaf_surse/cod_fiscal_227_2015_consolidat.txt`, dosar de cercetare F027.
:::

Impozitul pe profit se datorează începând chiar cu trimestrul în care s-a depășit plafonul de 100.000 EUR venituri (art.52 alin.(1)). Pentru acel prim trimestru, legea tratează inclusiv elementele de curs valutar generate la trecere ca „elemente similare veniturilor” ale acestui prim trimestru de impozit pe profit (art.53 alin.(2) lit.b)) — confirmând că baza de calcul e strict cea a trimestrului respectiv, nu o reconstituire a întregului an.

## Ce se greșește în practică

Se greșește prin excluderea elementelor de curs valutar din baza primului trimestru de profit, deși legea le include explicit ca venituri similare.

## Ce face iConta.eu

iConta.eu nu generează D101 fără CUI valid (verificat prin checksum, `core.identitate.valideaza_cui`), denumire, adresă și cod CAEN pe 4 cifre, plus datele de declarant complete (`erori_generare`, `core/d101.py`). În aplicație: Declarații → D101 → anul → Generează (ecranul mapează codul `d101` la fișa de ajutor F027, `static/js/ecrane/declaratii.js`).

[iConta.eu](/)
