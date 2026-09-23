---
title: "Se depune D101 dacă firma nu are impozit pe profit de plată?"
description: "Explică de ce obligația de depunere a D101 nu depinde de existența unei sume de plată."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Se depune D101 dacă firma nu are impozit pe profit de plată?

## Temeiul legal

::: ghid-temei
Art.13 alin.(1) CF: "Sunt obligate la plata impozitului pe profit... a) persoanele juridice române... b) persoanele juridice străine care desfășoară activitate prin intermediul unui sediu permanent... c) persoanele juridice străine rezidente în România potrivit locului conducerii efective... e) persoanele juridice cu sediul social în România, înființate potrivit legislației europene..."
— Legea 227/2015 (Codul fiscal) consolidată, `anaf_surse/cod_fiscal_227_2015_consolidat.txt`, dosar de cercetare F027.

Art.42 alin.(1) CF (modificat prin OUG 8/2026 art.6 pct.12, MO 147/25.02.2026, aplicabil începând cu anul fiscal 2026): "Contribuabilii au obligația să depună o declarație anuală privind impozitul pe profit până la data de 25 iunie inclusiv a anului următor..."
— Legea 227/2015 (Codul fiscal) consolidată, `anaf_surse/cod_fiscal_227_2015_consolidat.txt` + `anaf_surse/d101_scadenta_conflict_lege_validator.md` + `core/d101.py` (liniile 193-232), dosar de cercetare F027.
:::

Da. Obligația de a depune D101 rezultă din calitatea de contribuabil la impozitul pe profit (art.13 alin.(1)), iar art.42 alin.(1) cere depunerea declarației anuale fără nicio condiționare legată de suma efectiv datorată. O firmă poate ajunge la impozit zero de plată (de exemplu din cauza deducerilor sau a unei pierderi fiscale) și tot rămâne obligată să depună D101 la termen.

## Ce se greșește în practică

Se greșește frecvent prin asimilarea „nu am impozit de plată” cu „nu am obligație de declarare” — sunt lucruri distincte în lege.

## Ce face iConta.eu

iConta.eu nu generează D101 fără CUI valid (verificat prin checksum, `core.identitate.valideaza_cui`), denumire, adresă și cod CAEN pe 4 cifre, plus datele de declarant complete (`erori_generare`, `core/d101.py`). În aplicație: Declarații → D101 → anul → Generează (ecranul mapează codul `d101` la fișa de ajutor F027, `static/js/ecrane/declaratii.js`). Generarea nu e condiționată de o sumă minimă de plată — motorul calculează P40/P411 chiar dacă rezultatul e zero.

[iConta.eu](/)
