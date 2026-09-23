---
title: "Prima declarație D101 a unei firme noi: cum o depun"
description: "Detaliază termenul, obligația de plată trimestrială și cerințele minime pentru prima D101 a unei firme nou-înființate."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Prima declarație D101 a unei firme noi: cum o depun

## Temeiul legal

::: ghid-temei
Art.41 alin.(6) CF: sistemul trimestrial (fără posibilitatea de a opta pentru cel anual) este obligatoriu, în anul imediat următor schimbării, pentru contribuabilii nou-înființați, cei cu pierdere fiscală în anul precedent, cei aflați în inactivitate temporară sau cei care au fost, anterior, plătitori de impozit pe veniturile microîntreprinderilor.
— Legea 227/2015 (Codul fiscal) consolidată, `anaf_surse/cod_fiscal_227_2015_consolidat.txt`, dosar de cercetare F027.

Art.42 alin.(1) CF (modificat prin OUG 8/2026 art.6 pct.12, MO 147/25.02.2026, aplicabil începând cu anul fiscal 2026): "Contribuabilii au obligația să depună o declarație anuală privind impozitul pe profit până la data de 25 iunie inclusiv a anului următor..."
— Legea 227/2015 (Codul fiscal) consolidată, `anaf_surse/cod_fiscal_227_2015_consolidat.txt` + `anaf_surse/d101_scadenta_conflict_lege_validator.md` + `core/d101.py` (liniile 193-232), dosar de cercetare F027.
:::

O firmă nou-înființată, plătitoare de impozit pe profit, depune D101 ca declarație anuală de definitivare, până la 25 iunie inclusiv a anului următor celui pentru care se raportează. În cursul anului însă, legea o obligă la sistemul trimestrial de calcul/plată (fără opțiune pentru sistemul anual), în anul imediat următor înființării — la fel ca firmele cu pierdere fiscală anul precedent, cele în inactivitate temporară sau cele venite din regimul micro.

## Ce se greșește în practică

Confuzia frecventă e între termenul de depunere a D101 (anual, 25 iunie) și regimul de plată din timpul anului (trimestrial, obligatoriu pentru firma nouă). Sunt două lucruri diferite, reglementate de articole diferite (art.42, respectiv art.41 alin.(6)).

## Ce face iConta.eu

iConta.eu nu generează D101 fără CUI valid (verificat prin checksum, `core.identitate.valideaza_cui`), denumire, adresă și cod CAEN pe 4 cifre, plus datele de declarant complete (`erori_generare`, `core/d101.py`). În aplicație: Declarații → D101 → anul → Generează (ecranul mapează codul `d101` la fișa de ajutor F027, `static/js/ecrane/declaratii.js`).

[iConta.eu](/)
