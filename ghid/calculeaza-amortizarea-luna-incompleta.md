---
title: "Cum se calculează amortizarea pentru o lună incompletă"
description: "Legea nu prorează amortizarea pe zile — calculul se face în luni întregi, pornind din luna următoare punerii în funcțiune, indiferent de ziua din lună a PIF."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se calculează amortizarea pentru o lună incompletă

Nu există, de fapt, o "lună incompletă" de amortizare — regula fiscală lucrează exclusiv în luni calendaristice întregi.

## Temeiul legal

::: ghid-temei
"Amortizarea fiscală se calculează după cum urmează: a) începând cu luna următoare celei în care mijlocul fix amortizabil se pune în funcțiune, prin aplicarea regimului de amortizare prevăzut la alin. (5);" — Codul fiscal, art. 28 alin. (12) lit. a)
:::

Pentru că amortizarea începe abia din luna următoare PIF, ziua exactă din lună în care a avut loc punerea în funcțiune nu contează pentru calcul — fie că PIF e pe 2 sau pe 29 ale lunii, prima lună amortizată e tot luna imediat următoare, integral. Nu se calculează o fracțiune de lună proporțională cu numărul de zile rămase.

## Ce se greșește în practică

Se încearcă o proporționalizare manuală a amortizării pe numărul de zile din luna PIF sau din prima lună de folosință, deși legea nu cere și nu permite așa ceva — calculul e strict pe luni întregi.

## Ce face iConta.eu

Motorul unic de amortizare calculează numărul de luni scurse între PIF și data de referință ca număr întreg de luni calendaristice (funcția care determină intervalul e folosită identic de registru, notă lunară, casare și reevaluare) — nu există în aplicație o logică de proporționalizare pe zile.

[iConta.eu](/)
