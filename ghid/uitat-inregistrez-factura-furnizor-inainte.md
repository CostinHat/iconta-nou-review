---
title: Ce fac dacă am uitat să înregistrez o factură de furnizor înainte de închiderea lunii
description: iConta.eu refuză să blocheze o lună dacă mai există e-Facturi primite și neînregistrate — dar o factură sosită pe alt canal decât e-Factura poate scăpa acestei verificări. Ce se întâmplă în fiecare caz.
published: 2026-09-23
modified: 2026-09-23
poarta: v1
---

# Ce fac dacă am uitat să înregistrez o factură de furnizor înainte de închiderea lunii

Aplicația are o poartă construită special pentru acest scenariu — dar poarta acoperă un singur canal de sosire a facturii, e-Factura. Ce se întâmplă depinde de pe unde a intrat factura.

## Temeiul legal

::: ghid-temei
„Corectarea erorilor se efectuează la data constatării lor." — OMFP 1802/2014, Anexa 1 – Reglementări contabile (formă consolidată), pct. 65 alin. (2)
:::

Indiferent de canalul pe care a sosit factura, principiul din spatele corecției rămâne același: eroarea (omisiunea) se rezolvă la data la care e observată, nu retroactiv, cu falsificarea unei date vechi.

## Cazul obișnuit: factura există în e-Factura

Înainte de a permite blocarea unei luni, iConta.eu verifică dacă mai există e-Facturi primite și neînregistrate (nici ciornă, nici validate, nici respinse) cu data în luna respectivă. Dacă da, **blocarea lunii e refuzată motivat**, cu mesajul care spune câte documente sunt în așteptare și unde se rezolvă.

Cu alte cuvinte: dacă factura de furnizor a intrat prin e-Factura, sistemul **te oprește să închizi luna** înainte s-o fi înregistrat — problema din titlul acestui ghid, în principiu, nu ar trebui să apară deloc pentru facturile primite prin SPV.

## Cazul care scapă verificării: factura n-a sosit prin e-Factura

Verificarea de mai sus se uită strict la ce a coborât din e-Factura. O factură primită pe alt canal — hârtie, e-mail, un document dat de furnizor direct — nu apare în această sondă, deci **nu blochează închiderea lunii**. Luna se poate închide fără ca omisiunea să fie semnalată.

Dacă se ajunge în această situație — luna deja blocată, factura de furnizor găsită ulterior — se aplică exact mecanismul general pentru facturi vechi uitate: nota de contare se scrie cu o dată explicită, la momentul descoperirii, cu motivul consemnat, nu la data (retroactivă) a facturii.

## Ce se greșește în practică

- Se crede că verificarea la închiderea lunii acoperă *orice* factură de furnizor neînregistrată — de fapt acoperă doar ce a coborât din e-Factura. O factură primită altfel (hârtie, e-mail) nu declanșează niciun refuz de închidere.
- Se ignoră mesajul de refuz la blocarea lunii („există e-Facturi primite neînregistrate") și se caută o cale de a forța închiderea, în loc să se înregistreze mai întâi documentele semnalate.
- Se presupune că, odată luna închisă, factura găsită ulterior „nu mai are ce căuta acolo" — de fapt se înregistrează oricând, doar cu data mutată la momentul descoperirii.

## Ce face iConta.eu

Blocarea unei luni verifică, printre altele, dacă mai există e-Facturi primite și neînregistrate cu data în acea lună, și refuză motivat închiderea dacă da — deci pentru facturile care circulă prin SPV, omisiunea e prinsă înainte de închidere, nu după. Pentru o factură sosită pe alt canal și găsită după ce luna a fost deja blocată, corectarea nu se face prin editare retroactivă: nota de contare intră cu data descoperirii, cu mențiunea explicită a legăturii cu factura originală și a motivului întârzierii — niciodată printr-o rescriere tăcută a trecutului.

[iConta.eu](/)
