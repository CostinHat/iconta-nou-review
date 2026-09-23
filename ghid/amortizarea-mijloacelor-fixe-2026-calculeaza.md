---
title: "Amortizarea mijloacelor fixe 2026: cum se calculează corect"
description: "Prezentare generală a celor patru metode de amortizare fiscală, a regulilor pe categorie și a noutăților aduse de 2026."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Amortizarea mijloacelor fixe 2026: cum se calculează corect

Amortizarea fiscală corectă depinde de trei lucruri: categoria activului, metoda aleasă și data punerii în funcțiune (PIF).

## Temeiul legal

::: ghid-temei
"Regimul de amortizare pentru un mijloc fix amortizabil se determină conform următoarelor reguli: a) în cazul construcțiilor, se aplică metoda de amortizare liniară; ... b) în cazul echipamentelor tehnologice... contribuabilul poate opta pentru metoda de amortizare liniară, degresivă sau accelerată; ... c) în cazul oricărui altui mijloc fix amortizabil, contribuabilul poate opta pentru metoda de amortizare liniară sau degresivă."
— Codul fiscal, art.28 alin.(5)
:::

Legea prevede patru metode posibile — liniară (alin.6), degresivă (alin.7, cu coeficienți de 1,5/2,0/2,5 după durata normală), accelerată (alin.8, max. 50% în anul 1) și, doar pentru 2026, superaccelerată (alin.8^1, OUG 8/2026, max. 65% în anul 1, doar pentru active noi din subgrupele 2.1 și 2.4). Dar nu orice metodă e permisă pentru orice categorie: construcțiile (cont 212) au doar liniară; terenurile (cont 211) nu se amortizează deloc; echipamentele tehnologice au toate cele trei metode "clasice"; restul activelor au liniară sau degresivă, fără accelerată. Amortizarea începe, în toate cazurile, cu luna următoare celei în care activul e pus în funcțiune (alin.12 lit.a).

## Ce se greșește în practică

Cele mai des întâlnite erori: calculul manual în Excel care nu urmărește corect trecerea de la degresiv la liniar când ratele se egalizează, aplicarea unei metode nepermise pe categorie, sau pornirea calculului de la data facturii în loc de data punerii în funcțiune.

## Ce face iConta.eu

Toate calculele de amortizare din aplicație — registrul de mijloace fixe, nota lunară de amortizare, casarea și reevaluarea — trec printr-un singur motor de calcul, verificat printr-un test dedicat care păzește exact împotriva regresiei "ecranul calculează mereu liniar" apărută în trecut. Motorul respectă restricțiile de metodă pe categorie și refuză cu eroare pe rând orice combinație nepermisă, în loc să producă o cifră fabricată.

[iConta.eu](/)
