---
title: "Cum se completează D101 dacă firma nu a avut activitate?"
description: "Clarifică obligația de a depune D101 și modul de completare pentru o firmă plătitoare de impozit pe profit fără activitate în anul fiscal."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se completează D101 dacă firma nu a avut activitate?

## Temeiul legal

::: ghid-temei
Art.13 alin.(1) CF: "Sunt obligate la plata impozitului pe profit... a) persoanele juridice române... b) persoanele juridice străine care desfășoară activitate prin intermediul unui sediu permanent... c) persoanele juridice străine rezidente în România potrivit locului conducerii efective... e) persoanele juridice cu sediul social în România, înființate potrivit legislației europene..."
— Legea 227/2015 (Codul fiscal) consolidată, `anaf_surse/cod_fiscal_227_2015_consolidat.txt`, dosar de cercetare F027.

Art.42 alin.(1) CF (modificat prin OUG 8/2026 art.6 pct.12, MO 147/25.02.2026, aplicabil începând cu anul fiscal 2026): "Contribuabilii au obligația să depună o declarație anuală privind impozitul pe profit până la data de 25 iunie inclusiv a anului următor..."
— Legea 227/2015 (Codul fiscal) consolidată, `anaf_surse/cod_fiscal_227_2015_consolidat.txt` + `anaf_surse/d101_scadenta_conflict_lege_validator.md` + `core/d101.py` (liniile 193-232), dosar de cercetare F027.
:::

Obligația de a depune D101 decurge din calitatea de contribuabil plătitor de impozit pe profit (art.13 alin.(1)), nu din nivelul activității desfășurate. Art.13 alin.(2) exceptează explicit doar categorii precise (Trezoreria Statului, instituții publice pentru activitatea neeconomică, Academia Română etc.) — lipsa de activitate a unei firme obișnuite nu figurează printre aceste excepții. Art.42 alin.(1) obligă la depunerea declarației anuale, fără condiționare de existența unui rezultat impozabil.

## Ce se greșește în practică

Greșeala tipică e presupunerea că, fără activitate, firma e scutită de depunere. Legea nu prevede o astfel de scutire pentru contribuabilii plătitori de impozit pe profit — doar categoriile enumerate expres la art.13 alin.(2) sunt exceptate.

## Ce face iConta.eu

iConta.eu nu generează D101 fără CUI valid (verificat prin checksum, `core.identitate.valideaza_cui`), denumire, adresă și cod CAEN pe 4 cifre, plus datele de declarant complete (`erori_generare`, `core/d101.py`). În aplicație: Declarații → D101 → anul → Generează (ecranul mapează codul `d101` la fișa de ajutor F027, `static/js/ecrane/declaratii.js`). Structura declarației rămâne P1–P53, completată cu valori zero pe rândurile fără mișcare.

[iConta.eu](/)
