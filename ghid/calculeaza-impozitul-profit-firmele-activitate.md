---
title: Cum se calculează impozitul pe profit la firmele cu activitate mixtă
description: Cum separă D101 veniturile și cheltuielile de exploatare de cele financiare, și ce regim special există pentru anumite activități mixte (baruri, cluburi de noapte, cazinouri).
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum se calculează impozitul pe profit la firmele cu activitate mixtă

„Activitate mixtă" înseamnă, cel mai adesea, o firmă care are atât venituri/cheltuieli de exploatare, cât și financiare — separarea corectă a acestora contează direct la calculul impozitului pe profit. Există și un caz special, de activitate mixtă în sensul tipului de activitate (nu al naturii financiare/operaționale), reglementat separat.

## Temeiul legal

::: ghid-temei
D101 „citește profilul firmei + balanța, cu split exploatare/financiar (clasele 76/66 = financiar, restul 7x/6x = exploatare)"
— sursă: `core/d101.py`, funcția `pull()`, liniile 448–467, dosar de cercetare F027.

„Art.18: regim special 5% pentru baruri/cluburi de noapte/discoteci/cazinouri, dacă impozitul normal ar fi sub 5% din venituri."
— sursă: dosar de cercetare F027, secțiunea „Temei legal".
:::

Pentru marea majoritate a firmelor, „activitatea mixtă" înseamnă coexistența veniturilor și cheltuielilor de exploatare (clasele 7x/6x, cu excepția 76/66) cu cele financiare (clasele 76/66) — ambele categorii intră în calculul profitului impozabil, dar separarea lor corectă e necesară pentru subtotalurile din declarație.

Separat, Codul fiscal prevede la art.18 un regim special de 5% pentru anumite activități specifice — baruri, cluburi de noapte, discoteci, cazinouri — aplicabil dacă impozitul calculat în regim normal (16%) ar rezulta sub 5% din veniturile realizate din aceste activități. Acesta e un caz distinct de „activitate mixtă" (tip de activitate, nu natură financiară/operațională a rezultatului) și nu trebuie confundat cu separarea exploatare/financiar din bilanț.

## Ce se greșește în practică

Greșeala frecventă e amestecarea veniturilor/cheltuielilor financiare cu cele de exploatare la completarea manuală a unor rânduri din declarație, ceea ce distorsionează subtotalurile. O a doua greșeală, la firmele cu activități specifice (baruri, cluburi de noapte etc.), e ignorarea completă a regimului special de 5%, aplicând direct cota standard de 16% fără a verifica dacă impozitul minim de 5% din venituri e mai mare.

## Ce face iConta.eu

La generarea D101, iConta.eu separă automat, din balanță, veniturile și cheltuielile financiare (clasele 76/66) de cele de exploatare (restul claselor 7x/6x), pe baza datelor citite direct din profilul firmei și din balanța de verificare. Cercetarea funcțională a dosarului D101 nu documentează, însă, o funcționalitate dedicată pentru aplicarea automată a regimului special de 5% pentru activitățile enumerate la art.18 (baruri, cluburi de noapte, discoteci, cazinouri) — dacă firma dumneavoastră desfășoară astfel de activități, verificarea acestui calcul special rămâne, la acest moment, manuală.

[iConta.eu](/)
