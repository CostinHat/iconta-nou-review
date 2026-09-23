---
title: "D101 cu pierdere fiscală: cum se completează corect"
description: "Explică, strict pe temei legal, natura pierderii fiscale la impozitul pe profit, cu o precizare onestă asupra limitei acestui dosar."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# D101 cu pierdere fiscală: cum se completează corect

## Temeiul legal

::: ghid-temei
Art.49 + art.53 CF: baza impozabilă a impozitului pe veniturile microîntreprinderilor este VENITUL (cu ajustările de la art.53), nu profitul; conceptul de „pierdere fiscală” (art.31, Titlul II) nu apare nicăieri în art.47–56 (Titlul III, regimul micro).
— Legea 227/2015 (Codul fiscal) consolidată, `anaf_surse/cod_fiscal_227_2015_consolidat.txt`, dosar de cercetare F027.

Art.41 alin.(6) CF: sistemul trimestrial (fără posibilitatea de a opta pentru cel anual) este obligatoriu, în anul imediat următor schimbării, pentru contribuabilii nou-înființați, cei cu pierdere fiscală în anul precedent, cei aflați în inactivitate temporară sau cei care au fost, anterior, plătitori de impozit pe veniturile microîntreprinderilor.
— Legea 227/2015 (Codul fiscal) consolidată, `anaf_surse/cod_fiscal_227_2015_consolidat.txt`, dosar de cercetare F027.
:::

Pierderea fiscală e specifică regimului de impozit pe profit (art.31); firma care înregistrează pierdere fiscală rămâne obligată la depunerea anuală a D101 (art.13, art.42) și, în anul imediat următor, la sistemul trimestrial de plată, fără opțiune pentru sistemul anual (art.41 alin.(6)).

## Ce se greșește în practică

Se greșește prin omiterea depunerii D101 pentru anul cu pierdere, sub asumpția că declarația nu mai e necesară fără impozit de plată.

## Ce face iConta.eu

iConta.eu nu generează D101 fără CUI valid (verificat prin checksum, `core.identitate.valideaza_cui`), denumire, adresă și cod CAEN pe 4 cifre, plus datele de declarant complete (`erori_generare`, `core/d101.py`). În aplicație: Declarații → D101 → anul → Generează (ecranul mapează codul `d101` la fișa de ajutor F027, `static/js/ecrane/declaratii.js`). Sursele verificate în acest dosar nu detaliază rândul exact din structura P1–P53 folosit de iConta.eu pentru reportarea pierderii fiscale — confirmați rândul cu contabilul, pe baza instrucțiunilor oficiale OPANAF 206/2025.

[iConta.eu](/)
