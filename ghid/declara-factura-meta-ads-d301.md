---
title: Cum se declară factura Meta Ads în D301 și D390?
description: O factură Meta Ads e servicii de publicitate cumpărate din străinătate — dacă furnizorul e stabilit în UE, operațiunea e tip 5 și intră automat și în D390, dar entitatea de facturare trebuie verificată pe fiecare factură, nu presupusă.
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum se declară factura Meta Ads în D301 și D390?

Campaniile de publicitate rulate prin Meta Ads (Facebook, Instagram) sunt facturate lunar, pe baza bugetului cheltuit. Fiscal, e o achiziție de servicii, cu locul prestării în România pentru firma care cumpără — dar declarația concretă (D301 secțiunea 4 sau secțiunea 4.1, cu sau fără D390) depinde de unde e stabilită entitatea emitentă a facturii.

## Temeiul legal

::: ghid-temei
Secțiunea 4.1 din formular: „Achiziții de servicii intracomunitare, pentru care beneficiarul este obligat la plata TVA conform art. 307 alin. (2)" — OPANAF 592/2016, Anexa 1. Instrucțiunile de completare precizează că se aplică serviciilor de la prestatori „stabiliți pe teritoriul (...) dar care sunt stabilite în Comunitate" — OPANAF 592/2016, Anexa 2, Instrucțiuni.
:::

Tip 5 (secțiunea 4.1) e rezervat explicit prestatorilor stabiliți în UE. Dacă entitatea care emite factura Meta Ads nu e stabilită în UE, operațiunea se încadrează la tip 4 (art. 307 alin. (6)) — declarată tot în D301, dar **fără** intrare în D390.

**Nu presupune** entitatea de facturare — verific-o pe fiecare factură Meta Ads primită. Nu există o regulă generală care să garanteze aceeași entitate pentru toți clienții sau pentru toate perioadele.

### Cum se declară, în funcție de statutul TVA

- **Firmă plătitoare de TVA (art. 316):** taxare inversă în D300, rd. 7 + rd. 20, net zero. D301 nu se completează pentru acest profil.
- **Firmă neplătitoare de TVA, furnizor stabilit în UE:** D301 secțiunea 4.1 (tip 5) + D390 cod S. Necesită înregistrare prin art. 317 înainte de prima campanie plătită, fără plafon.
- **Firmă neplătitoare de TVA, furnizor stabilit în afara UE:** D301 secțiunea 4 (tip 4), fără D390.

### Exemplu de calcul

Factură Meta Ads, 180,00 EUR, curs zilei exigibilității 4,9773 lei/EUR:

baza = round(180,00 × 4,9773; 0) = round(895,914; 0) = **896 lei**

Baza intră în declarație rotunjită la leu întreg, nu la bani. TVA-ul se calculează din bază, la cota aplicabilă perioadei.

## Ce se greșește în practică

- Se clasifică toate facturile de publicitate online la fel, indiferent de furnizor, fără verificarea entității emitente pe fiecare factură.
- Se lasă necompletate câmpurile de țară și cod TVA ale furnizorului, iar operațiunea rămâne, din greșeală, în afara D390.
- Se calculează baza cu zecimale de bani, în loc de rotunjire directă la leu întreg.

## Ce face iConta.eu

La introducerea unei operațiuni tip 5, câmpurile de țară și cod TVA ale furnizorului declanșează automat includerea în D390, cu cod S; pentru tip 4, aceleași câmpuri există, dar operațiunea rămâne exclusă din D390 — cu motivul afișat explicit în diagnostic. Baza se recalculează la generare, rotunjită la leu întreg, iar fiecare operațiune de tip 5 se adaugă și la totalul secțiunii 4, conform regulii formularului.

[iConta.eu](/)
