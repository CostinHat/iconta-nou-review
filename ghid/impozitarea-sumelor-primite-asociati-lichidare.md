---
title: "Impozitarea sumelor primite de asociați la lichidare"
description: "Cota fixă de 10% aplicabilă câștigului obținut de asociații persoane fizice la lichidarea unei societăți, distinctă de impozitul pe dividende."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Impozitarea sumelor primite de asociați la lichidare

La lichidarea unei societăți, nu tot ce primește asociatul e impozabil, și nu tot ce e impozabil se impozitează cu aceeași cotă ca dividendele. Legea separă clar restituirea capitalului propriu (neimpozabilă) de câștigul efectiv distribuit (impozabil, cu o cotă fixă, distinctă de cota de dividend).

## Temeiul legal

::: ghid-temei
„Venitul impozabil obținut din lichidarea unei persoane juridice de către acționari/asociați persoane fizice sau din reducerea capitalului social, potrivit legii, care nu reprezintă distribuții în bani sau în natură ca urmare a restituirii cotei-părți din aporturi se impun cu o cotă de 10%, impozitul fiind final. Obligația calculării, reținerii și plății impozitului revine persoanei juridice. Impozitul calculat și reținut la sursă în cazul lichidării persoanei juridice se plătește până la data depunerii situației financiare finale la oficiul registrului comerțului, întocmită de lichidatori [...]"
— Cod fiscal (Legea 227/2015), art. 97 alin. (5) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

- **Neimpozabil**: partea din sumele primite de asociat care reprezintă strict **restituirea cotei-părți din aporturi** (adică restituirea capitalului social vărsat de asociat).
- **Impozabil, cu 10% fix**: tot ce depășește restituirea aporturilor — practic rezervele și profiturile distribuite asociatului la partaj.
- **Cota e fixă, 10%, impozit final** — nu se schimbă de la un an la altul, spre deosebire de cota de impozit pe dividende (istoric 5%, 8%, 10%, iar din 2026, 16%). Sunt două regimuri distincte, prevăzute la alineate diferite ale art. 97 (alin. (5) pentru lichidare, alin. (7) pentru dividende).
- **Obligația de calcul, reținere și plată** revine societății (practic lichidatorului), iar termenul de plată e legat de un eveniment procedural — depunerea situației financiare finale la registrul comerțului — nu de o dată calendaristică fixă.

## Ce se greșește în practică

- Se aplică din eroare cota de impozit pe dividende (16% din 2026), în loc de cota fixă de 10% specifică lichidării, prevăzută distinct la art. 97 alin. (5).
- Se impozitează și partea din sumă care reprezintă strict restituirea capitalului social vărsat de asociat, deși aceasta e explicit neimpozabilă.
- Se raportează plata impozitului la un termen calendaristic obișnuit (de exemplu 25 ale lunii următoare), fără să se verifice legătura lui cu depunerea situației financiare finale a lichidării la oficiul registrului comerțului.

## Ce face iConta.eu

Impozitarea sumelor primite de asociați la lichidare **nu e o funcție a F039 (Decontări asociați)**, deși folosește aceleași conturi de decontare (456) generate și de operațiunile curente cu asociații. Calculul aparține unui modul separat, de lichidare/radiere societate (`core/lichidare.py`, funcția `partaj()`), care aplică exact distincția de mai sus: capitalul social restituit e trecut neimpozabil (`1012=456`), iar rezervele și profiturile distribuite generează un câștig impozabil cu o cotă **fixă de 10%**, calculată separat de cota de dividend din F039 și citată explicit în cod ca fiind cea de la CF art. 97 alin. (5), distinctă de regimul dividendelor de la alin. (7). Rezultă liniile `106x/1171=456` (rezerve/profit), `456=446` (impozitul reținut) și `456=5121` (plata netă către asociat).

[iConta.eu](/)
