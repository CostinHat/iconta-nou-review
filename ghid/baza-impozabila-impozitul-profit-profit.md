---
title: "Baza impozabilă la impozitul pe profit: de la profit contabil la profit fiscal"
description: "Baza impozabilă a impozitului pe profit rezultă din profitul contabil ajustat cu deduceri, add-back-uri și rezerva legală."
published: 2026-09-26
modified: 2026-10-13
poarta: v1
---

# Baza impozabilă la impozitul pe profit: de la profit contabil la profit fiscal

Baza impozabilă (P40 în D101) nu este profitul contabil — este rezultatul unor ajustări specifice, aplicate în ordine.

Traseul, confirmat în motorul D101:

- **Deduceri** — amortizarea fiscală (P11) se scade din baza impozabilă, intrând în totalul deducerilor (P16).
- **Add-back-uri** — cheltuiala cu amortizarea contabilă (P2x/P28) și alte cheltuieli nedeductibile se adaugă înapoi, în rollup-ul P34; inclusiv cheltuiala cu impozitul pe profit (cont 691), dacă are sold debitor pozitiv (CF art.25 alin.(4) lit.a)).
- **Rezerva legală (P13)** — se scade din bază, calculată automat (dacă nu e dată manual) din profitul contabil brut + cheltuiala cu impozitul, plafonată la min(5% × bază; 20% × capital social − rezervă existentă), conform CF art.26 alin.(1) lit.a).
- **Sponsorizarea (P43)** — dedusă cu dublă limită: 20% din impozit și 0,75% din cifra de afaceri (CF art.25 alin.(4) lit.i)).

Rezultatul (P40) se înmulțește cu 16% (art.17), obținând impozitul final (P411).

## Temeiul legal

::: ghid-temei
„Rezultatul fiscal se calculează ca diferență între veniturile și cheltuielile înregistrate conform reglementărilor contabile aplicabile, din care se scad veniturile neimpozabile și deducerile fiscale și la care se adaugă cheltuielile nedeductibile. [...] Rezultatul fiscal pozitiv este profit impozabil, iar rezultatul fiscal negativ este pierdere fiscală.”
— Codul fiscal (Legea nr. 227/2015), art. 19 alin. (1) (sursă: [Legea nr. 227/2015 privind Codul fiscal](https://legislatie.just.ro/Public/DetaliiDocument/171282))

„Următoarele cheltuieli nu sunt deductibile: a) cheltuielile proprii ale contribuabilului cu impozitul pe profit datorat, inclusiv cele reprezentând diferențe din anii precedenți sau din anul curent, precum și impozitele pe profit sau pe venit plătite în străinătate.”
— Codul fiscal (Legea nr. 227/2015), art. 25 alin. (4) lit. a) (sursă: [Legea nr. 227/2015 privind Codul fiscal](https://legislatie.just.ro/Public/DetaliiDocument/171282))

„Contribuabilul are dreptul la deducerea rezervelor și provizioanelor/ajustărilor pentru depreciere, numai în conformitate cu prezentul articol, astfel: a) rezerva legală este deductibilă în limita unei cote de 5% aplicate asupra profitului contabil, la care se adaugă cheltuielile cu impozitul pe profit, până ce aceasta va atinge a cincea parte din capitalul social subscris și vărsat sau din patrimoniu, după caz”
— Codul fiscal (Legea nr. 227/2015), art. 26 alin. (1) lit. a) (sursă: [Legea nr. 227/2015 privind Codul fiscal](https://legislatie.just.ro/Public/DetaliiDocument/171282))
:::

## Ce se greșește în practică

Greșeala frecventă e omiterea unuia dintre add-back-uri (mai ales cel legat de contul 691), ceea ce reduce artificial baza impozabilă și, implicit, impozitul declarat.

## Ce face iConta.eu

Amortizarea fiscală și contabilă sunt intrări manuale ale contabilului. Rezerva legală se calculează automat dacă lipsește, iar aplicația emite avertisment explicit pe contul 691 când acesta indică o posibilă subevaluare.

[iConta.eu](/)
