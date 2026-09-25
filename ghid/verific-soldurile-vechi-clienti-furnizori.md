---
title: "Cum verific soldurile vechi de clienți și furnizori?"
description: "Procedura legală de verificare și confirmare a soldurilor de creanțe și datorii față de clienți și furnizori, cu ocazia inventarierii anuale."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum verific soldurile vechi de clienți și furnizori?

Soldurile de clienți și furnizori care „stau" ani la rând în balanță, neschimbate, sunt printre cele mai frecvente probleme găsite la un control sau la o cesiune de activitate. Legea nu lasă verificarea lor la latitudinea contabilului — inventarierea anuală a creanțelor și datoriilor este obligatorie și are o metodă precisă de confirmare.

## Temeiul legal

::: ghid-temei
„Creanțele și obligațiile față de terți sunt supuse verificării și confirmării pe baza extraselor soldurilor debitoare și creditoare ale conturilor de creanțe și datorii care dețin ponderea valorică în totalul soldurilor acestor conturi, potrivit «Extrasului de cont» (cod 14-6-3) sau punctajelor reciproce scrise. Nerespectarea acestei proceduri, precum și refuzul de confirmare constituie abateri de la prezentele norme și se sancționează potrivit legii."
— OMFP nr. 2861/2009 pentru aprobarea Normelor privind organizarea și efectuarea inventarierii elementelor de natura activelor, datoriilor și capitalurilor proprii, pct. 28 alin. (1) (sursă: anaf_surse/omfp_2861_2009.txt)
:::

Ce înseamnă în practică pentru soldurile vechi:

- Verificarea nu e opțională doar pentru soldurile „suspecte" — legea cere confirmarea conturilor de creanțe și datorii cu pondere valorică semnificativă în totalul soldurilor, ceea ce, de regulă, include exact soldurile mari și vechi.
- Confirmarea se face fie prin extrasul de cont (fișa de cont trimisă partenerului pentru confirmare), fie prin puncte de vedere/punctaje reciproce scrise — un simplu e-mail neconfirmat de partener nu e suficient ca document de inventariere.
- Dacă entitatea decontează pe bază de deconturi interne sau externe periodice confirmate de parteneri, acestea pot ține locul extraselor de cont — util pentru grupuri de firme sau relații contractuale cu decontare periodică.
- Refuzul partenerului de a confirma soldul nu scutește de obligație — trebuie documentat ca atare, iar soldul rămâne supus evaluării comisiei de inventariere.

## Ce se greșește în practică

- Se lasă soldurile vechi „așa cum sunt" în balanță, an după an, fără punctaj de confirmare, considerându-se că simpla lor prezență în extrasul de cont bancar acoperă obligația legală.
- Se confundă verificarea soldurilor bancare (extrase de cont de la bancă) cu verificarea soldurilor de clienți/furnizori (extrase de cont trimise partenerilor comerciali) — sunt proceduri diferite, cu documente diferite.
- Nu se ajustează pentru depreciere creanțele vechi neîncasate, deși inventarierea anuală ar trebui să declanșeze și analiza de recuperabilitate, nu doar confirmarea cifrei.

## Ce face iConta.eu

Da — iConta.eu are un modul de inventariere (`core/inventariere.py`), construit pe baza OMFP 2861/2009 și OMFP 1802/2014, care generează notele contabile pentru plusurile și minusurile constatate la inventar (stocuri, mijloace fixe). Modulul acoperă rezultatele inventarierii fizice și ale ajustărilor de valoare, dar procedura de trimitere și primire a confirmărilor de sold către/de la clienți și furnizori (extrasul de cont cod 14-6-3) rămâne, la acest moment, un proces manual, în afara aplicației.

[iConta.eu](/)
