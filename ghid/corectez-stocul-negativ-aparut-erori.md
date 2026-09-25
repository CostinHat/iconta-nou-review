---
title: "Cum corectez stocul negativ apărut din erori"
description: "De ce stocul negativ e mereu semnul unei erori de înregistrare și ce document justificativ e necesar pentru a corecta situația, în lipsa unei reglementări dedicate stocului negativ."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum corectez stocul negativ apărut din erori

Un stoc negativ (o cantitate de marfă înregistrată contabil sub zero) nu e o situație pe care legislația contabilă românească o reglementează explicit ca fenomen distinct — pentru că, fizic, un stoc negativ nu poate exista. Dacă apare în evidența contabilă, e mereu simptomul unei erori de secvență a înregistrărilor: o ieșire de gestiune (vânzare, consum) a fost înregistrată înaintea intrării corespunzătoare, sau o intrare a fost omisă. Corectarea nu e o operațiune specială, ci aplicarea regulii generale privind documentul justificativ care stă la baza fiecărei înregistrări.

## Temeiul legal

::: ghid-temei
„Orice operațiune economico-financiară efectuată se consemnează în momentul efectuării ei într-un document care stă la baza înregistrărilor în contabilitate, dobândind astfel calitatea de document justificativ."
— Legea 82/1991 (legea contabilității), art. 6 alin. (1) (sursă: anaf_surse/legea_82_1991_consolidat.txt)
:::

Limitare clară: sursele verificate nu conțin un act normativ care să reglementeze explicit „stocul negativ" ca situație distinctă — regula generală de mai sus (fiecare mișcare de stoc are la bază un document justificativ, înregistrat cronologic) e temeiul pe care se sprijină orice corectare:

- **Cauza tehnică** a unui stoc negativ e aproape întotdeauna cronologică: o factură de vânzare sau un bon de consum a fost înregistrat(ă) înainte ca intrarea de marfă corespunzătoare (factura de achiziție, NIR) să fi fost introdusă în sistem, deși fizic marfa exista deja în gestiune.
- **Corectarea** presupune identificarea documentului justificativ de intrare care lipsește sau care a fost înregistrat cu întârziere și reordonarea cronologică a înregistrărilor, nu o „ajustare" artificială a cantității pentru a aduce stocul la zero sau pozitiv.
- **Dacă discrepanța e reală** (nu doar o eroare de secvență, ci o lipsă efectivă de marfă), corectarea corectă trece prin inventariere — constatarea unei lipse în gestiune, cu proces-verbal de inventariere, nu prin modificarea directă a soldului contabil.

## Ce se greșește în practică

- Se „forțează" stocul la zero printr-o înregistrare manuală de ajustare, fără document justificativ, doar pentru ca programul de gestiune să nu mai afișeze eroare — asta ascunde problema reală, nu o rezolvă.
- Se ignoră cauza (secvența greșită a înregistrărilor) și se repetă eroarea la fiecare lună, pentru că nu s-a corectat fluxul de introducere a documentelor (facturi de achiziție introduse după facturile de vânzare aferente).
- Se confundă stocul negativ apărut din eroare de secvență cu o lipsă reală de gestiune constatată la inventariere — primul se corectează prin reordonarea documentelor, al doilea se tratează ca minus de inventar, cu proces-verbal.

## Ce face iConta.eu

iConta.eu oferă contabilitate generală de gestiune a stocurilor, pe baza documentelor introduse de utilizator (facturi de achiziție, facturi de vânzare, NIR); aplicația nu are, la data acestui ghid, un mecanism automat de detectare sau corectare a stocului negativ — identificarea cauzei (de regulă o intrare introdusă cu întârziere) rămâne în responsabilitatea contabilului.

[iConta.eu](/)
