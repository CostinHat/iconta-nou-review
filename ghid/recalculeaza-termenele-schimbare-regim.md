---
title: "Cum se recalculează termenele după o schimbare de regim"
description: "Ce se întâmplă cu perioada fiscală de TVA a unei firme care raporta trimestrial, atunci când efectuează o achiziție intracomunitară de bunuri taxabilă în România."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum se recalculează termenele după o schimbare de regim

Firmele mici de TVA raportează, de regulă, trimestrial. Dar o singură achiziție intracomunitară de bunuri taxabilă în România schimbă automat perioada fiscală în lună calendaristică, iar momentul exact din care se aplică schimbarea depinde de luna trimestrului în care apare exigibilitatea taxei aferente achiziției.

## Temeiul legal

::: ghid-temei
„(7) Prin excepție de la prevederile alin. (2)-(6), pentru persoana impozabilă care utilizează trimestrul calendaristic ca perioadă fiscală și care efectuează o achiziție intracomunitară de bunuri taxabilă în România, perioada fiscală devine luna calendaristică începând cu: a) prima lună a unui trimestru calendaristic, dacă exigibilitatea taxei aferente achiziției intracomunitare de bunuri intervine în această primă lună a respectivului trimestru; b) a treia lună a trimestrului calendaristic, dacă exigibilitatea taxei aferente achiziției intracomunitare de bunuri intervine în a doua lună a respectivului trimestru. Primele două luni ale trimestrului respectiv vor constitui o perioadă fiscală distinctă, pentru care persoana impozabilă va avea obligația depunerii unui decont de taxă [...]; c) prima lună a trimestrului calendaristic următor, dacă exigibilitatea taxei aferente achiziției intracomunitare de bunuri intervine în a treia lună a unui trimestru calendaristic."
— Legea nr. 227/2015 (Codul fiscal), art. 322 alin. (7) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Regula are trei scenarii distincte, în funcție de luna în care apare exigibilitatea taxei pentru achiziția intracomunitară:

- Dacă exigibilitatea apare în **prima lună** a trimestrului, tot trimestrul „se rupe" în luni — perioada fiscală devine lunară chiar din acea primă lună.
- Dacă exigibilitatea apare în **a doua lună**, primele două luni ale trimestrului formează o perioadă fiscală distinctă (cu decont propriu), iar de la a treia lună firma raportează deja lunar.
- Dacă exigibilitatea apare abia în **a treia lună**, trimestrul curent rămâne neschimbat, iar perioada devine lunară abia din trimestrul următor.

## Ce se greșește în practică

- Se aplică schimbarea de perioadă doar din trimestrul următor, indiferent de luna în care apare exigibilitatea achiziției intracomunitare, pierzând termenul de declarare al perioadei intermediare.
- Se ignoră obligația de decont separat pentru primele două luni ale trimestrului, în cazul exigibilității apărute în a doua lună — o perioadă fiscală „ruptă" care are propriul termen de depunere.
- Se confundă schimbarea perioadei fiscale (cauzată de o achiziție intracomunitară) cu opțiunea de a trece de la trimestru la lună, care are alt temei (art. 322 alin. (5) și (6)) și alt termen de anunțare — 25 ianuarie.

## Ce face iConta.eu

La data acestui ghid, iConta.eu **nu detectează și nu recalculează automat** schimbarea perioadei fiscale de TVA la apariția unei achiziții intracomunitare. Aplicația generează deconturile D300 pe baza perioadei fiscale setate în profilul firmei (`core/d300.py`, `core/perioada_fiscala_tva.py`), dar contabilul este cel care trebuie să identifice apariția condiției de la art. 322 alin. (7) și să ajusteze manual perioada fiscală și termenele de declarare aferente.

[iConta.eu](/)
