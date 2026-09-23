---
title: "Ce faci dacă ai ales un cod de clasificare greșit pentru mijlocul fix?"
description: "iConta.eu nu validează codul de clasificare (catalogul HG 2139/2004), dar contul de imobilizare ales chiar afectează ce metode de amortizare sunt permise — cum corectezi o alegere greșită."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Ce faci dacă ai ales un cod de clasificare greșit pentru mijlocul fix?

Aici trebuie separate două lucruri diferite: codul de clasificare din catalogul oficial (care determină plaja de durată) și contul de imobilizare din registru (care determină categoria fiscală și metodele permise).

## Temeiul legal

::: ghid-temei
"Regimul de amortizare pentru un mijloc fix amortizabil se determină conform următoarelor reguli: a) în cazul construcțiilor, se aplică metoda de amortizare liniară; [...] b) în cazul echipamentelor tehnologice [...] contribuabilul poate opta pentru metoda de amortizare liniară, degresivă sau accelerată; [...]" — Codul fiscal, art. 28 alin. (5)
:::

Un cod de clasificare greșit (poziția din catalogul HG 2139/2004) înseamnă, de regulă, o durată normală de funcționare aleasă în afara plajei corecte — se corectează manual, prin actualizarea duratei pe activ. Un cont de imobilizare greșit e mai grav: schimbă categoria fiscală a activului și, implicit, ce metode de amortizare sunt permise pentru el.

## Ce se greșește în practică

Se corectează doar codul de clasificare "cosmetic", fără să se verifice dacă și contul de imobilizare (cel care contează fiscal) reflectă corect categoria reală a activului.

## Ce face iConta.eu

Catalogul HG 2139/2004 nu e integrat în aplicație — durata normală de funcționare e un câmp liber, fără validare automată a intervalului corect, deci o corecție a codului de clasificare înseamnă doar actualizarea manuală a duratei pe activul respectiv. În schimb, contul de imobilizare e verificat activ la fiecare calcul de amortizare: dacă metoda aleasă nu mai e permisă după corectarea contului, motorul refuză calculul și arată eroare pe rând, în loc să continue cu o cifră greșită.

[iConta.eu](/)
