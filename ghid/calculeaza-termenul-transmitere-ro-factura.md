---
title: "Cum se calculează termenul de transmitere în RO e-Factura?"
description: "Formula de calcul a termenului de 5 zile lucrătoare pentru RO e-Factura, pornind de la data emiterii sau de la data-limită legală de emitere, conform Legii 296/2023 și Codului fiscal."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se calculează termenul de transmitere în RO e-Factura?

Termenul de 5 zile lucrătoare pentru transmiterea unei facturi în RO e-Factura nu pornește mereu de la aceeași dată — calculul depinde de relația dintre data reală de emitere și data-limită legală de emitere a facturii.

## Temeiul legal

::: ghid-temei
„(6) Termenul-limită pentru transmiterea facturilor prevăzute la alin. (1)-(3) în sistemul național privind factura electronică RO e-Factura este de 5 zile lucrătoare de la data emiterii facturii, dar nu mai târziu de 5 zile lucrătoare de la data-limită prevăzută pentru emiterea facturii la art. 319 alin. (16) din Legea nr. 227/2015, cu modificările și completările ulterioare."
— Legea 296/2023, art. LIX alin. (6) (sursă: anaf_surse/legea_296_2023_masuri_fiscal_bugetare_asigurarea_sustenabilitatii.txt)

„(16) Pentru alte operațiuni decât cele prevăzute la alin. (15), persoana impozabilă are obligația de a emite o factură cel târziu până în cea de-a 15-a zi a lunii următoare celei în care ia naștere faptul generator al taxei, cu excepția cazului în care factura a fost deja emisă."
— Codul fiscal (Legea 227/2015), art. 319 alin. (16) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Algoritmul de calcul, cu cele două date de referință:

1. **Data-limită legală de emitere** a facturii, conform art. 319 alin. (16) Cod fiscal: cel târziu în a **15-a zi a lunii următoare** celei în care a luat naștere faptul generator de taxă.
2. **Data reală de emitere** a facturii — poate fi înainte de data-limită (factură emisă la timp) sau, dacă firma a întârziat, chiar mai aproape ori peste data-limită.
3. **Termenul de transmitere în RO e-Factura** e **minimul** dintre: (a) 5 zile lucrătoare de la data reală de emitere, și (b) 5 zile lucrătoare de la data-limită de emitere (a 15-a zi a lunii următoare). Formularea legii — „dar nu mai târziu de" — arată clar că a doua ancoră e un plafon, nu o alternativă la alegere.
4. Pentru o factură emisă la timp, cele două calcule converg practic la aceeași dată sau la una apropiată; pentru o factură emisă cu întârziere mare, plafonul de la data-limită legală devine cel determinant, iar termenul de transmitere poate fi deja depășit chiar din momentul emiterii tardive.

## Ce se greșește în practică

- Se calculează termenul doar de la data emiterii, ignorând plafonul absolut de la data-limită legală — pentru facturile emise cu întârziere, acest calcul poate păcăli firma cu un termen mai lung decât cel real.
- Se numără zile calendaristice, nu zile lucrătoare — un termen de "5 zile" trecut peste un weekend sau o zi de sărbătoare legală se calculează greșit dacă nu se exclud aceste zile.
- Se aplică regula generală de emitere din art. 319 alin. (16) și în cazurile speciale de la alin. (15) (pentru care legea prevede alt regim de emitere) — verificarea trebuie făcută pe tipul concret de operațiune, nu presupusă generic.

## Ce face iConta.eu

La data acestui ghid, `core/efactura_send.py` (`fctel`) generează și transmite XML-ul facturii către SPV prin `upload_ubl()`, cu confirmarea stării prin `stare_mesaj()`. Calculul automat al celor două ancore de termen (5 zile de la emitere / 5 zile de la data-limită legală, în zile lucrătoare) și semnalarea proactivă a riscului de depășire nu au fost identificate ca funcție distinctă în cod — verificarea încadrării în termen rămâne, azi, o responsabilitate a contabilului, la momentul transmiterii.

[iConta.eu](/)
