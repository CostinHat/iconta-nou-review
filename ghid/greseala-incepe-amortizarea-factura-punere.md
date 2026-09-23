---
title: "Greșeala de a începe amortizarea la factură nu la punere în funcțiune"
description: "Legea leagă startul amortizării de data punerii în funcțiune, nu de data facturii de achiziție."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Greșeala de a începe amortizarea la factură nu la punere în funcțiune

Una dintre cele mai des întâlnite greșeli e confundarea datei facturii cu data punerii în funcțiune (PIF) — cele două pot diferi semnificativ, mai ales pentru active care necesită instalare sau recepție.

## Temeiul legal

::: ghid-temei
"Amortizarea fiscală se calculează după cum urmează: a) începând cu luna următoare celei în care mijlocul fix amortizabil se pune în funcțiune, prin aplicarea regimului de amortizare prevăzut la alin. (5);"
— Codul fiscal, art.28 alin.(12) lit.a
:::

Textul e explicit: amortizarea începe cu luna următoare punerii în funcțiune, nu cu luna facturii. Dacă activul a fost facturat într-o lună, dar pus efectiv în funcțiune mai târziu (de exemplu după instalare sau montaj), calculul trebuie să pornească de la data reală a punerii în funcțiune.

## Ce se greșește în practică

Greșeala tipică apare la active care necesită timp de instalare (utilaje, echipamente complexe) — contabilul înregistrează PIF la data facturii pentru simplitate, ceea ce pornește amortizarea prea devreme.

## Ce face iConta.eu

Toate funcțiile motorului unic de amortizare (`amortizat_la_data`, `amortizare_luna`, folosite și de nota lunară, casare și reevaluare) calculează pornind strict de la câmpul de dată a punerii în funcțiune al activului, aplicând regula "luna următoare PIF" — corectitudinea calculului depinde direct de corectitudinea datei de PIF introduse, aplicația nu o deduce automat din altă sursă (cum ar fi data facturii).

[iConta.eu](/)
