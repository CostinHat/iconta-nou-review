---
title: "Cum verific calculul impozitului pe profit înainte de închiderea trimestrului?"
description: "Verificarea trimestrială a impozitului pe profit se face prin D100, nu prin D101, care rămâne exclusiv declarația anuală de definitivare."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum verific calculul impozitului pe profit înainte de închiderea trimestrului?

Un lucru trebuie clarificat de la început: D101 nu este instrumentul pentru verificarea trimestrială — aceasta se face prin D100.

## Temeiul legal

::: ghid-temei
"Art.41 alin.(1): calcul/declarare/plată trimestrială, «până la data de 25 inclusiv a primei luni următoare încheierii trimestrelor I-III», cu definitivare la termenul art.42." — Legea 227/2015, citată în dosarul de cercetare F027 pe baza `anaf_surse/cod_fiscal_227_2015_consolidat.txt`.
:::

Plățile trimestriale/anticipate de impozit pe profit (cod de obligație 103) se depun prin D100, nu prin D101 — confirmat de nomenclatorul `COD_BUGETAR` din `core/d100.py`. D101 este, în toate cazurile, exclusiv declarația ANUALĂ de definitivare.

Dacă firma a optat pentru sistemul anual cu plăți anticipate trimestriale (art.41 alin.(2)), plățile anticipate reprezintă 1/4 din impozitul anului precedent, actualizat cu indicele prețurilor de consum (art.41 alin.(8)) — nu un calcul recalculat de la zero în fiecare trimestru.

## Ce se greșește în practică

Greșeala tipică e căutarea unei funcții de „verificare trimestrială" în motorul D101 — aceasta nu există, pentru că D101 nu operează la nivel trimestrial. Verificarea propriu-zisă a sumei datorate trimestrial ține de fluxul D100.

## Ce face iConta.eu

Pentru definitivarea anuală, D101 validează identitatea firmei (`erori_generare`) și rulează reconciliere independentă a bazei contabile la generare. Pentru verificări trimestriale, fluxul relevant din aplicație este D100, cu codul de obligație 103.

[iConta.eu](/)
