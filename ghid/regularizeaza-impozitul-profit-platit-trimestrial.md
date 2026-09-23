---
title: "Cum se regularizează impozitul pe profit plătit trimestrial?"
description: "Explică relația dintre plățile trimestriale de impozit pe profit (D100) și definitivarea anuală (D101)."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se regularizează impozitul pe profit plătit trimestrial?

## Temeiul legal

::: ghid-temei
Art.41 alin.(1) CF: calculul, declararea și plata impozitului pe profit se fac trimestrial, „până la data de 25 inclusiv a primei luni următoare încheierii trimestrelor I-III", cu definitivare la termenul de la art.42.
— Legea 227/2015 (Codul fiscal) consolidată, `anaf_surse/cod_fiscal_227_2015_consolidat.txt`, dosar de cercetare F027.

Art.42 alin.(1) CF (modificat prin OUG 8/2026 art.6 pct.12, MO 147/25.02.2026, aplicabil începând cu anul fiscal 2026): "Contribuabilii au obligația să depună o declarație anuală privind impozitul pe profit până la data de 25 iunie inclusiv a anului următor..."
— Legea 227/2015 (Codul fiscal) consolidată, `anaf_surse/cod_fiscal_227_2015_consolidat.txt` + `anaf_surse/d101_scadenta_conflict_lege_validator.md` + `core/d101.py` (liniile 193-232), dosar de cercetare F027.
:::

Impozitul pe profit se calculează, declară și plătește, ca regulă, trimestrial (art.41 alin.(1)), „până la data de 25 inclusiv a primei luni următoare încheierii trimestrelor I-III”, dar plățile trimestriale/anticipate propriu-zise (cod_oblig 103) se depun prin D100, nu prin D101. Regularizarea (definitivarea) impozitului pentru întregul an fiscal se face exclusiv prin D101, la termenul de la art.42 (25 iunie inclusiv a anului următor).

## Ce se greșește în practică

Confuzia frecventă e tratarea D101 ca instrument de regularizare trimestrială — D101 e strict anuală; regularizările din timpul anului (plăți anticipate trimestriale, corectarea lor) se gestionează prin D100/D710, nu prin D101.

## Ce face iConta.eu

Plățile trimestriale/anticipate de impozit pe profit (cod_oblig 103) se depun prin D100 (F026), nu prin D101 — D101 este exclusiv declarația ANUALĂ de definitivare, generată la finalul exercițiului fiscal. În aplicație: Declarații → D101 → anul → Generează (ecranul mapează codul `d101` la fișa de ajutor F027, `static/js/ecrane/declaratii.js`). D101 rulează cota standard de 16% (art.17) pe profitul impozabil anual (P40 → P411), consolidând întregul exercițiu fiscal.

[iConta.eu](/)
