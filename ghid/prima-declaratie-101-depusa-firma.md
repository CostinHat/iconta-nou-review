---
title: "Prima declarație 101 depusă pentru firma nouă: cum procedez"
description: "Explică pașii și obligațiile specifice primei D101 depuse de o firmă nou-înființată, plătitoare de impozit pe profit."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Prima declarație 101 depusă pentru firma nouă: cum procedez

## Temeiul legal

::: ghid-temei
Art.41 alin.(6) CF: sistemul trimestrial (fără posibilitatea de a opta pentru cel anual) este obligatoriu, în anul imediat următor schimbării, pentru contribuabilii nou-înființați, cei cu pierdere fiscală în anul precedent, cei aflați în inactivitate temporară sau cei care au fost, anterior, plătitori de impozit pe veniturile microîntreprinderilor.
— Legea 227/2015 (Codul fiscal) consolidată, `anaf_surse/cod_fiscal_227_2015_consolidat.txt`, dosar de cercetare F027.

Art.42 alin.(1) CF (modificat prin OUG 8/2026 art.6 pct.12, MO 147/25.02.2026, aplicabil începând cu anul fiscal 2026): "Contribuabilii au obligația să depună o declarație anuală privind impozitul pe profit până la data de 25 iunie inclusiv a anului următor..."
— Legea 227/2015 (Codul fiscal) consolidată, `anaf_surse/cod_fiscal_227_2015_consolidat.txt` + `anaf_surse/d101_scadenta_conflict_lege_validator.md` + `core/d101.py` (liniile 193-232), dosar de cercetare F027.
:::

Pentru firmele nou-înființate care sunt plătitoare de impozit pe profit, prima D101 urmează aceleași reguli de fond ca oricare alta — declarație anuală de definitivare, la termenul legal de 25 iunie inclusiv a anului următor. Diferența reală apare la modul de plată în cursul anului: firma nu poate opta pentru sistemul anual cu plăți anticipate trimestriale (art.41 alin.(3)) — legea o obligă la sistemul trimestrial (calcul, declarare și plată trimestrială, cu definitivare la termenul art.42) chiar din primul an fiscal.

## Ce se greșește în practică

O greșeală tipică e presupunerea că, fiind la primul an, firma poate alege direct opțiunea anuală — nu poate, conform art.41 alin.(6). O alta e depunerea D101 fără toate datele de identificare complete și corecte.

## Ce face iConta.eu

iConta.eu nu generează D101 fără CUI valid (verificat prin checksum, `core.identitate.valideaza_cui`), denumire, adresă și cod CAEN pe 4 cifre, plus datele de declarant complete (`erori_generare`, `core/d101.py`). În aplicație: Declarații → D101 → anul → Generează (ecranul mapează codul `d101` la fișa de ajutor F027, `static/js/ecrane/declaratii.js`).

[iConta.eu](/)
