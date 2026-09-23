---
title: "Cum se completează D101 pentru o firmă înființată în cursul anului?"
description: "Explică regimul aplicabil unei firme înființate în cursul anului fiscal la completarea D101."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se completează D101 pentru o firmă înființată în cursul anului?

## Temeiul legal

::: ghid-temei
Art.41 alin.(6) CF: sistemul trimestrial (fără posibilitatea de a opta pentru cel anual) este obligatoriu, în anul imediat următor schimbării, pentru contribuabilii nou-înființați, cei cu pierdere fiscală în anul precedent, cei aflați în inactivitate temporară sau cei care au fost, anterior, plătitori de impozit pe veniturile microîntreprinderilor.
— Legea 227/2015 (Codul fiscal) consolidată, `anaf_surse/cod_fiscal_227_2015_consolidat.txt`, dosar de cercetare F027.

Art.17 CF: "Cota de impozit pe profit care se aplică asupra profitului impozabil este de 16%."
— Legea 227/2015 (Codul fiscal) consolidată, `anaf_surse/cod_fiscal_227_2015_consolidat.txt`, dosar de cercetare F027.
:::

O firmă nou-înființată care e plătitoare de impozit pe profit (nu a optat sau nu se încadrează la impozitul pe veniturile microîntreprinderilor) completează D101 ca declarație anuală de definitivare, la cota standard de 16% aplicată profitului impozabil (P40 → P411). Particularitatea unei firme nou-înființate ține însă de modul de plată din timpul anului, nu de structura D101 în sine: legea o obligă la sistemul trimestrial de calcul/plată, fără posibilitatea de a opta pentru sistemul anual cu plăți anticipate, în anul imediat următor înființării.

## Ce se greșește în practică

Cea mai frecventă greșeală e încercarea de a opta direct pentru sistemul anual din primul an, deși art.41 alin.(6) o interzice explicit pentru firmele nou-înființate. A doua greșeală e completarea D101 cu date de identificare incomplete sau CUI netransmis corect — declarația nu poate fi generată în acest caz.

## Ce face iConta.eu

iConta.eu nu generează D101 fără CUI valid (verificat prin checksum, `core.identitate.valideaza_cui`), denumire, adresă și cod CAEN pe 4 cifre, plus datele de declarant complete (`erori_generare`, `core/d101.py`). În aplicație: Declarații → D101 → anul → Generează (ecranul mapează codul `d101` la fișa de ajutor F027, `static/js/ecrane/declaratii.js`). Restul completării (cota 16%, deduceri P11, rezerva legală P13 calculată automat conform CF art.26, cheltuieli nedeductibile P23/P34) urmează structura standard P1–P53, reconstruită după OPANAF 206/2025.

[iConta.eu](/)
