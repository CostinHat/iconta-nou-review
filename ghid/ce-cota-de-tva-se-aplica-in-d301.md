---
title: Ce cotă de TVA se aplică în D301?
description: În D301 se aplică, în funcție de tipul operațiunii, cota standard (21% de la 01.08.2025) sau cota redusă (11% de la 01.08.2025), determinată de perioada în care ia naștere exigibilitatea taxei.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Ce cotă de TVA se aplică în D301?

Cota de TVA folosită la completarea decontului special D301 nu este fixă — depinde de natura bunului sau serviciului achiziționat și de data la care ia naștere exigibilitatea taxei, nu de data facturii sau a plății. Legea nr. 141/2025 a modificat cotele începând cu 01.08.2025, ceea ce face ca alegerea corectă a perioadei să fie esențială.

## Temeiul legal

::: ghid-temei
**Art. 291 alin. (1)**: Cota standard se aplică asupra bazei de impozitare pentru operațiunile impozabile care nu sunt scutite de taxă sau care nu sunt supuse cotei reduse, iar nivelul acesteia este **21%**. *(modificat de la 01-08-2025 prin Legea nr. 141/2025)*

**Art. 291 alin. (2)**: Cota redusă de **11%** se aplică asupra bazei de impozitare pentru [lista limitativă de bunuri/servicii: medicamente, alimente, apă/canalizare, îngrășăminte, cărți/manuale, acces muzee, lemn de foc, energie termică, locuințe sociale, cazare hotelieră, restaurant/catering]. *(modificat de la 01-08-2025 prin Legea nr. 141/2025)*

**Art. 291 alin. (8)**: Cota aplicabilă pentru achiziții intracomunitare de bunuri este cota aplicată pe teritoriul României pentru livrarea aceluiași bun și care este în vigoare la data la care intervine exigibilitatea taxei.
:::

## Cota standard vs. cota redusă și perioada de referință

Pentru achizițiile intracomunitare de bunuri (Secțiunea 1), art. 291 alin. (8) impune o regulă clară: se aplică aceeași cotă ca la livrarea internă a bunului respectiv, valabilă la data exigibilității taxei — nu cota din statul membru de origine.

Pentru servicii cu taxare inversă (Secțiunea 4/4.1), aceeași logică period-aware se aplică: până la 31.07.2025 cota standard a fost 19%, iar cotele reduse au fost 9%/5%; de la 01.08.2025 cota standard a devenit 21%, iar cotele reduse s-au comasat în 11%. Există și opțiunea de operațiune scutită/0%, pentru cazurile prevăzute de lege.

::: ghid-exemplu
O factură de servicii software cu exigibilitatea taxei în septembrie 2025 (deci după 01.08.2025) se declară la cota standard de 21%, chiar dacă factura a fost emisă în iulie 2025 la vechea cotă de 19% în alt stat membru — cota românească aplicabilă contează, la data exigibilității, nu data facturii.
:::

## Ce se greșește în practică

- Se aplică automat cota din factura furnizorului extern (ex. cota TVA irlandeză), în loc de cota românească corespunzătoare.
- Se folosește cota veche (19%/9%/5%) pentru operațiuni a căror exigibilitate cade după 01.08.2025.
- Se confundă data facturii cu data exigibilității taxei, deși perioada relevantă pentru determinarea cotei este cea din urmă.
- Se alege manual o cotă redusă fără verificarea explicită că serviciul sau bunul se încadrează în lista limitativă din art. 291 alin. (2).
- Se presupune că sistemul recalculează automat TVA dacă se schimbă ulterior cota aleasă la introducerea operațiunii.

## Ce face iConta.eu

Cota standard și cotele reduse sunt determinate automat, în funcție de perioadă, prin funcția care citește cota validă pentru anul și luna operațiunii — period-aware, cu pragul de 01.08.2025 (Legea 141/2025) implementat explicit: 19% până la 31.07.2025, 21% de la 01.08.2025 pentru cota standard, respectiv cotele reduse comasate în 11% de la aceeași dată. Există și opțiunea de operațiune la cotă 0%/scutită.

TVA-ul calculat (`baza × cotă / 100`) este stocat la momentul introducerii operațiunii și nu este recalculat automat la generarea declarației — doar baza (în lei) se recalculează. Dacă la introducere a fost aleasă o cotă greșită pentru perioada respectivă, TVA-ul persistat rămâne greșit, iar corectarea revine în responsabilitatea contabilului, aplicația nu re-verifică ulterior alegerea cotei.

[iConta.eu](/)
