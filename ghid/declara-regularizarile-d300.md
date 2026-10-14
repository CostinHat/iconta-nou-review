---
title: "Unde se declară regularizările în D300?"
description: Regularizările D300 se introduc printr-un panou manual dedicat, separat de motorul care generează rândurile din facturi — cu o listă fixă de rânduri acceptate și gărzi împotriva dublei numărări.
published: 2026-09-23
modified: 2026-10-13
poarta: v1
---

# Unde se declară regularizările în D300?

Regularizările de TVA nu rezultă automat din facturile perioadei — se introduc explicit, printr-un panou manual dedicat, separat de motorul de calcul al decontului. Mai jos, exact ce rânduri acceptă panoul și cum funcționează mecanismul.

## Temeiul legal

::: ghid-temei
„Datele înscrise incorect într-un decont de taxă se pot corecta prin decontul unei perioade fiscale ulterioare și se vor înscrie la rândurile de regularizări.”
— Codul fiscal, art. 323 alin. (3) (sursă: [Legea nr. 227/2015 privind Codul fiscal](https://legislatie.just.ro/Public/DetaliiDocument/171282))

„În cazul taxei pe valoarea adăugată, corectarea erorilor din deconturile de taxă se realizează potrivit prevederilor Codului fiscal.”
— Legea nr. 207/2015 privind Codul de procedură fiscală, art. 105 alin. (4) (sursă: [Legea nr. 207/2015 privind Codul de procedură fiscală](https://legislatie.just.ro/Public/DetaliiDocument/170007))
:::

## Rândurile de regularizare acceptate

Panoul manual acceptă o listă fixă (allow-list) de coduri de rând. Pentru regularizări, cele relevante sunt:

- **rândul 16** — „Regularizări taxă colectată" — se oglindește automat în totalul taxei colectate (rândul 19), la generarea decontului.
- **rândul 33** — „Regularizări taxă dedusă" — intră direct în calculul totalului taxei deduse (rândul 35).
- **rândurile 2, 4, 6, 8** — regularizări specifice operațiunilor intracomunitare (livrări bunuri, prestări servicii, achiziții bunuri, achiziții servicii), fiecare cu oglinda ei deductibilă unde e cazul (rândul 21 pentru rândul 6, rândul 23 pentru rândul 8).

Toate aceste coduri apar, în motorul D300, **doar** în formulele de însumare (rândurile 19 și 30, totalurile de taxă colectată și deductibilă) — niciodată ca țintă a unei atribuiri automate din facturi. Sunt 100% manuale.

## Ce NU e o regularizare manuală

Rândurile computate — 19, 30, 31, 34, 35, 36, 37, 40, 43, 44, 45 — nu sunt în allow-list, indiferent de context. Nu pot fi introduse manual prin acest panou, chiar dacă tema pare de „ajustare" sau „regularizare" a unei sume.

## Mecanismul tehnic

Rândurile se introduc prin aplicația (an, lună, rând, bază, TVA, descriere), cu validare că rândul e în allow-list și nu e deja derivat automat din facturile perioadei. Se persistă în tabelul „rândurile D300 completate manual (Declarații)” și se recitesc automat la generarea decontului — atât la preview, cât și la depunerea efectivă, cu paritate garantată între cele două căi (test dedicat confirmă XML identic generat din baza de date și din parametru).

## Ce se greșește în practică

- Se încearcă introducerea manuală a unui rând computat (ex. rândul 34, ajustarea pro-rata) crezând că e o formă de „regularizare" — rândul nu apare în lista de rânduri disponibile, pentru că nu e permis manual.
- Se introduce manual o sumă care e deja derivată automat dintr-o factură a perioadei — aplicația respinge cererea (dublă numărare).

## Ce face iConta.eu

Panoul din ecranul de declarații oferă exact lista rândurilor de regularizare acceptate (rândurile 2, 4, 6, 8, 16, 21, 23 și 33), cu etichetele oficiale ANAF, validare împotriva dublei numărări cu facturile deja înregistrate și persistență cu paritate garantată între preview și depunere.

[iConta.eu](/)
