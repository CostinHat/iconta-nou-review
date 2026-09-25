---
title: "Stocul negativ din erori de descărcare: cum îl corectez"
description: "Ce este stocul negativ, de ce apare din erori de descărcare de gestiune și cum se corectează prin inventariere, potrivit reglementărilor contabile."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Stocul negativ din erori de descărcare: cum îl corectez

Un stoc negativ (cantitate sau valoare sub zero pe o gestiune) nu e o stare economică reală — nu se poate vinde mai mult decât ai avut în gestiune — ci aproape întotdeauna semnul unei erori: o vânzare descărcată din gestiune înainte ca intrarea corespunzătoare să fi fost înregistrată, o factură de achiziție înregistrată cu întârziere sau o eroare de cantitate la o notă de recepție. Corectarea trece prin identificarea cauzei, nu doar prin „aducerea" soldului la zero.

## Temeiul legal

::: ghid-temei
„Registrul-inventar se completează pe baza inventarierii faptice a fiecărui cont de activ și de pasiv. [...] În cazul în care inventarierea are loc pe parcursul anului, în Registrul-inventar se înregistrează soldurile existente la data inventarierii, la care se adaugă rulajele intrărilor și se scad rulajele ieșirilor de la data inventarierii până la data încheierii exercițiului financiar."
— OMFP 2634/2015, Norme generale privind documentele financiar-contabile (sursă: anaf_surse/omfp_2634_2015.txt)
:::

Pașii de corectare a unui stoc negativ:

- **Se identifică sursa** — de regulă una din trei: o ieșire (vânzare, consum) înregistrată înaintea intrării corespunzătoare; o intrare care lipsește sau a fost introdusă cu o cantitate greșită; o eroare de articol (s-a descărcat codul greșit de produs).
- **Se verifică ordinea cronologică reală** a documentelor (facturi de achiziție, NIR-uri, facturi de vânzare, bonuri de consum) — stocul trebuie recalculat în ordinea datelor documentelor, nu în ordinea în care au fost introduse în aplicație.
- **Se corectează prin document, nu prin ajustare directă a soldului** — dacă lipsește o intrare, se înregistrează NIR-ul lipsă; dacă articolul e greșit, se corectează linia facturii/bonului, nu se „forțează" stocul la o valoare pozitivă printr-o notă manuală nejustificată.
- **Diferențele reale** (constatate la inventariere și care nu au explicație documentară) se tratează ca plus sau minus de inventar, cu procesul verbal de inventariere aferent.

## Ce se greșește în practică

- Se corectează stocul negativ cu o „intrare de ajustare" fără document justificativ, doar ca soldul să iasă pozitiv în aplicație — asta ascunde eroarea reală în loc s-o repare.
- Se ignoră stocul negativ pentru că „oricum se regularizează la inventarul anual", deși el distorsionează costul de vânzare (CMP sau FIFO) pentru toate tranzacțiile ulterioare pe acel articol.
- Se introduc facturile de achiziție cu întârziere sistematică față de facturile de vânzare, generând stocuri negative recurente pe aceleași articole, fără a se corecta fluxul de introducere a documentelor.

## Ce face iConta.eu

Modulul de stocuri din iConta.eu (`core/stocuri.py`, `core/inventariere.py`) ține evidența cantitativ-valorică pe gestiuni și articole, cu note contabile dedicate pentru plusuri de inventar (`nota_plus`) și minusuri de inventar (`nota_minus`), inclusiv pentru mijloace fixe. Reconcilierea automată dintre facturi și mișcările de stoc este acoperită de teste dedicate (`test_reconciliere_factura_stoc.py`). La data acestui ghid, aplicația **nu previne automat introducerea unei ieșiri care ar duce stocul pe negativ** dacă documentele nu sunt introduse în ordine cronologică — depistarea și corectarea cauzei rămân în sarcina contabilului, pe baza rapoartelor de stoc.

[iConta.eu](/)
