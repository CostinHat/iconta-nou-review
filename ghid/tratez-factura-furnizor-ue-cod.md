---
title: "Cum tratez factura unui furnizor UE cu cod TVA de România?"
description: "Dacă furnizorul din UE facturează cu un cod de TVA de România (nu cu codul din statul lui membru), operațiunea nu e achiziție intracomunitară — se tratează ca achiziție internă, cu TVA românesc aplicat normal."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum tratez factura unui furnizor UE cu cod TVA de România?

Un furnizor dintr-un alt stat membru poate fi, în același timp, înregistrat în scopuri de TVA în România (sediu fix, înregistrare directă). Dacă factura e emisă cu codul de TVA românesc, nu cu cel din statul membru de origine, operațiunea nu urmează regimul de achiziție intracomunitară.

## Temeiul legal

::: ghid-temei
„`desparte_cod_tva(cod)` — separă prefixul de țară de restul codului (...); validează prefixul contra `TARI_UE` (cele 27 state + `XI` = Irlanda de Nord, post-Brexit)...” — `core/intracomunitar.py`, dosarul F050.
:::

Motorul de operațiuni intracomunitare lucrează cu prefixul de țară al codului de TVA de pe factură. Dacă acel cod are prefixul RO, furnizorul acționează, pentru operațiunea respectivă, ca persoană înregistrată în România — nu se mai verifică validitatea printr-un cod străin în VIES, iar operațiunea nu se încadrează ca achiziție intracomunitară de bunuri sau servicii conform art. 268 / art. 278 alin. (2).

## Ce se greșește în practică

- Se așteaptă automat factură fără TVA de la orice furnizor cu sediu în UE, ignorând faptul că, dacă a facturat cu cod TVA de România, tranzacția e supusă regimului intern.
- Se declară în D390 o operațiune facturată de fapt cu cod TVA românesc — D390 e declarația recapitulativă a operațiunilor intracomunitare, nu a facturilor de la furnizori străini în general.
- Se aplică taxare inversă pe o factură care conține deja TVA colectat de furnizor cu codul lui românesc — dublarea taxei prin taxare inversă peste TVA deja facturat.

## Ce face iConta.eu

Verificarea automată la emitere/introducere se face pe baza prefixului codului de TVA: dacă prefixul e RO, operațiunea nu intră în motorul de operațiuni intracomunitare (care validează prefixul contra listei celor 27 de state membre plus `XI`). Practic, o factură cu cod TVA românesc se introduce ca achiziție internă obișnuită, cu TVA-ul de pe factură, nu pe ecranul de achiziție intracomunitară.

[iConta.eu](/)
