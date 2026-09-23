---
title: "Cum calculez impozitul pe profit de 16% pentru un SRL în 2026?"
description: "Cota de 16% se aplică pe profitul impozabil final, calculat prin definitivarea anuală din D101."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum calculez impozitul pe profit de 16% pentru un SRL în 2026?

Cota standard de impozit pe profit rămâne, și în 2026, cea din 2005: 16%, aplicată pe profitul impozabil, nu pe venit.

## Temeiul legal

::: ghid-temei
"Art.17: Cota de impozit pe profit care se aplică asupra profitului impozabil este de 16%." (stabilă din 2005) — Legea 227/2015, citată în dosarul de cercetare F027 pe baza `anaf_surse/cod_fiscal_227_2015_consolidat.txt`.
:::

În motorul D101 (`core/d101.py`, linia 46), această cotă e cablată explicit ca `COTA_STANDARD = Decimal("16")` și se aplică pe profitul impozabil (P40), rezultând impozitul final (P411). Există o excepție punctuală, nelegată de un SRL obișnuit: art.18 prevede un regim special de 5% pentru baruri, cluburi de noapte, discoteci și cazinouri, dacă impozitul calculat normal ar fi sub 5% din veniturile realizate.

Pentru firmele mari, cu cifră de afaceri a anului precedent peste 50.000.000 EUR, se poate adăuga separat impozitul minim pe cifra de afaceri (IMCA) — un calcul distinct de cota de 16%, detaliat în ghidul dedicat firmelor cu venituri mari.

## Ce se greșește în practică

Greșeala tipică e confuzia dintre profitul contabil și profitul impozabil: cota de 16% nu se aplică direct pe rezultatul contabil, ci pe profitul impozabil rezultat după deduceri (ex. amortizare fiscală), add-back-uri (ex. amortizare contabilă, cheltuieli nedeductibile) și rezerva legală.

## Ce face iConta.eu

Motorul D101 aplică automat cota de 16% pe profitul impozabil final (P40 → P411), după ce profilul firmei și balanța sunt citite prin `pull()` și după validările de identitate din `erori_generare`.

[iConta.eu](/)
