---
title: "Cum completez D101 pentru prima dată?"
description: "Prima completare a D101 pornește de la validarea datelor de identitate ale firmei, apoi trece prin balanță și ajustările fiscale."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum completez D101 pentru prima dată?

Pentru prima D101, aplicația nu generează declarația decât după ce datele de identitate ale firmei sunt complete și valide.

## Temeiul legal

::: ghid-temei
"D101 nu se poate genera fără CUI valid (checksum verificat prin `core.identitate.valideaza_cui`), denumire, adresă, cod CAEN pe 4 cifre; plus erorile de declarant din `core.firma_profil_api.erori_declarant`." — dosarul de cercetare F027, pe baza `core/d101.py`, funcția `erori_generare(prof)`, liniile 366–388.
:::

După ce identitatea firmei e validă, `pull()` citește balanța (conturile 76/66 ca financiar, 7x/6x ca exploatare, plus 1012/1061/691 pentru rezerva legală). Contabilul introduce apoi manual amortizarea fiscală (P11) și add-back-ul contabil al amortizării (P2x/P28), iar aplicația calculează automat rezerva legală dacă nu e dată manual.

Dacă firma provine dintr-un regim de microîntreprindere trecut în cursul anului la impozit pe profit, regulile de tranziție sunt tratate separat — consultați ghidul dedicat acelei situații.

## Ce se greșește în practică

Greșeala tipică la prima completare e omiterea codului CAEN pe 4 cifre sau a unor date de adresă incomplete, ceea ce blochează generarea, ori tratarea amortizării ca pe un calcul automat, deși ambele valori (fiscală și contabilă) sunt introduse manual.

## Ce face iConta.eu

`erori_generare` blochează generarea declarației până la completarea corectă a datelor de identitate. După validare, `pull()` aduce automat balanța, iar rezerva legală se calculează automat dacă nu e introdusă manual.

[iConta.eu](/)
