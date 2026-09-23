---
title: "Se depune D101 pentru o firmă cu pierdere?"
description: "Explică obligația de depunere a D101 pentru o firmă cu pierdere fiscală și regimul de plată trimestrial obligatoriu în anul următor."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Se depune D101 pentru o firmă cu pierdere?

## Temeiul legal

::: ghid-temei
Art.13 alin.(1) CF: "Sunt obligate la plata impozitului pe profit... a) persoanele juridice române... b) persoanele juridice străine care desfășoară activitate prin intermediul unui sediu permanent... c) persoanele juridice străine rezidente în România potrivit locului conducerii efective... e) persoanele juridice cu sediul social în România, înființate potrivit legislației europene..."
— Legea 227/2015 (Codul fiscal) consolidată, `anaf_surse/cod_fiscal_227_2015_consolidat.txt`, dosar de cercetare F027.

Art.41 alin.(6) CF: sistemul trimestrial (fără posibilitatea de a opta pentru cel anual) este obligatoriu, în anul imediat următor schimbării, pentru contribuabilii nou-înființați, cei cu pierdere fiscală în anul precedent, cei aflați în inactivitate temporară sau cei care au fost, anterior, plătitori de impozit pe veniturile microîntreprinderilor.
— Legea 227/2015 (Codul fiscal) consolidată, `anaf_surse/cod_fiscal_227_2015_consolidat.txt`, dosar de cercetare F027.
:::

Da — o firmă plătitoare de impozit pe profit rămâne obligată la depunerea anuală a D101 (art.13 alin.(1), art.42) indiferent dacă exercițiul s-a încheiat cu profit sau cu pierdere fiscală. În plus, art.41 alin.(6) prevede o consecință practică importantă: firma care înregistrează pierdere fiscală într-un an este obligată, în anul imediat următor, la sistemul trimestrial de calcul/plată, fără a putea opta pentru sistemul anual cu plăți anticipate.

## Ce se greșește în practică

Greșeala tipică e omiterea depunerii D101 pentru anul cu pierdere, sub asumpția că nefiind impozit de plată, declarația nu mai e necesară — vezi și GH-00717.

## Ce face iConta.eu

iConta.eu nu generează D101 fără CUI valid (verificat prin checksum, `core.identitate.valideaza_cui`), denumire, adresă și cod CAEN pe 4 cifre, plus datele de declarant complete (`erori_generare`, `core/d101.py`). În aplicație: Declarații → D101 → anul → Generează (ecranul mapează codul `d101` la fișa de ajutor F027, `static/js/ecrane/declaratii.js`).

[iConta.eu](/)
