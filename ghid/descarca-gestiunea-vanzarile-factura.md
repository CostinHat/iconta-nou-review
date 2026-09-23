---
title: "Cum se descarcă gestiunea pentru vânzările cu factură?"
description: La emiterea unei facturi cu marfă din stoc, la o firmă cu gestiune cantitativ-valorică, aplicația cere obligatoriu confirmarea "pleacă marfa acum?" — proformele și avizele nu declanșează această întrebare.
published: 2026-09-23
modified: 2026-09-23
poarta: v1
---

# Cum se descarcă gestiunea pentru vânzările cu factură?

Poarta de descărcare a gestiunii se activează strict la emiterea unei facturi propriu-zise (nu la proformă, nu la aviz), la o firmă cu gestiune cantitativ-valorică, și doar dacă factura conține cel puțin o linie legată de un articol de stoc. La emitere, aplicația cere o confirmare obligatorie: "pleacă marfa acum?" DA sau NU. Fără un răspuns, factura nu poate fi emisă.

## Temeiul legal

::: ghid-temei
"441. - (1) Veniturile din vânzarea bunurilor se recunosc în momentul în care sunt îndeplinite următoarele condiții: a) entitatea a transferat cumpărătorului riscurile şi avantajele semnificative care decurg din proprietatea asupra bunurilor;"
— OMFP 1802/2014, pct. 441 alin. (1)
:::

Recunoașterea vânzării (și, cu ea, ieșirea mărfii din gestiune) e legată de transferul riscurilor și avantajelor asupra bunului, nu automat de emiterea facturii. Poarta DA/NU e felul în care operatorul declară, la fiecare factură, dacă acest transfer are loc chiar atunci.

## Ce se greșește în practică

- Se emite o factură cu articole și se așteaptă ca stocul să scadă automat, fără nicio confirmare — la firma cu gestiune cantitativ-valorică, fără un răspuns explicit la poartă, factura nici nu poate fi emisă.
- Se emite o proformă sau un aviz și se așteaptă aceeași poartă ca la factură — poarta nu apare la aceste tipuri de document, indiferent câte linii de articol conțin.
- Se răspunde "DA" la poartă pentru o factură de avans sau pentru marfă care rămâne, de fapt, la vânzător — răspunsul trebuie să reflecte realitatea fizică a livrării, nu automatismul de a bifa "da" la orice factură cu articole.

## Ce face iConta.eu

La emiterea unei facturi (nu proformă, nu aviz), pentru o firmă cu gestiune cantitativ-valorică, dacă factura conține cel puțin o linie legată de un articol de stoc, iConta.eu afișează o fereastră obligatorie: "Pleacă marfa acum? DA / Nu, doar factură". La alegerea "DA", gestiunea se descarcă automat, în aceeași operațiune cu emiterea, cu mișcarea de stoc rezultată legată explicit de factura respectivă (util, printre altele, pentru calculul ulterior al profitului pe produs); nota contabilă asociată rămâne ciornă, spre validare separată. La alegerea "Nu, doar factură", factura se emite ca document pur fiscal, iar stocul nu se modifică la acel moment.

Menționăm onest: dacă factura are cel puțin o linie fără stoc suficient, emiterea nu e blocată — linia respectivă apare raportată separat, ca eroare de descărcare, în rezultatul operațiunii.

[iConta.eu](/)
