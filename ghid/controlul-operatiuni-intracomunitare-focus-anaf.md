---
title: Controlul pe operațiuni intracomunitare: focus ANAF
description: ANAF confruntă D390 cu VIES și cu decontul de TVA depus; cele mai frecvente ținte de control sunt codul de TVA nevalid, dovada transportului lipsă și încadrarea greșită a operațiunii — nu decalajul de exigibilitate, care de regulă e legitim.
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Controlul pe operațiuni intracomunitare: focus ANAF

Operațiunile intracomunitare sunt vizibile din exterior prin VIES, sistemul prin care statele membre își compară reciproc declarațiile. De aceea sunt o zonă cu control automatizat, nu doar cu inspecție clasică — o neconcordanță se vede la nivel european, nu doar în evidența ta.

## Temeiul legal

::: ghid-temei
„D390 baza … (facturi intracomunitare, auto — art. 325 Cod fiscal, declarația…)” — cod sursă `core/control_incrucisat.py`, funcția `compara_d390()`. Temeiul declarat pentru controlul încrucișat pe operațiuni intracomunitare: „art. 325 Cod fiscal (declarația recapitulativă); art. 294 alin. (2)/278; OMFP 1802/2014 (evidența)” (sursă: dosar F050, secțiunea „Control încrucișat / control fiscal”).
:::

Practic, controlul se face pe trei niveluri suprapuse, nu pe unul singur:

- **VIES vs. D390** — ce declari tu ca livrare sau achiziție intracomunitară trebuie să se regăsească, ca sumă și perioadă, la partenerul din celălalt stat membru;
- **D390 vs. evidența ta** — bazele din facturile intracomunitare trebuie să corespundă cu ce ai înregistrat contabil;
- **D390 vs. D300 depus** — sumele raportate în declarația recapitulativă trebuie să se regăsească în rândurile corespunzătoare din decontul de TVA.

## Ce se greșește în practică

Cele mai frecvente cauze reale de neconcordanță, distincte de diferențele legitime de exigibilitate (o factură emisă la finalul lunii poate cădea în luni diferite în cele două declarații, ceea ce nu e eroare):

- **codul de TVA greșit sau nevalid la data operațiunii** — verificarea trebuie făcută atunci, nu la data controlului;
- **operațiune omisă** — o achiziție intracomunitară ajunsă în contabilitate ca operațiune internă, pentru că factura nu a fost recunoscută ca atare;
- **încadrare greșită a tipului de operațiune** — un serviciu intracomunitar declarat ca operațiune internă, sau o operațiune care intră sub incidența art. 307 alin. (3)-(6) inclusă din greșeală în D390;
- **partener neînregistrat** — furnizorul nu avea cod valid la data operațiunii, deci nu exista livrare scutită, iar el trebuia să factureze cu TVA.

## Ce face iConta.eu

Controlul încrucișat compară automat bazele din facturile intracomunitare cu evidența validată și cu D300 depus, pe un semafor verde/gri/roșu (nu blocant, ca la validările de generare a declarației): roșu înseamnă o operațiune declarată la VIES fără acoperire în evidență sau în D300; gri, o diferență de investigat, de regulă un decalaj de exigibilitate legitim; verde, coincidență confirmată. Constatările roșii sunt împinse ca alerte în aplicație.

Nu există în iConta.eu un modul separat de „dosar de audit pentru operațiuni intracomunitare” — cel mai apropiat e exact acest control încrucișat, împreună cu alertele generate de el. Documentele care compun în practică un asemenea dosar (facturi validate, dovezi VIES cu dată, dovezi de transport, corelarea D301↔D390, rezultatul controlului încrucișat) există separat, dar nu se exportă printr-un singur buton dedicat — asta nu am găsit-o confirmată în cod și nu o afirmăm.

[iConta.eu](/)
