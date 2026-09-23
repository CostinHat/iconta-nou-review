---
title: Cum se completează D301 pentru servicii cumpărate din UE?
description: Serviciile intracomunitare de la prestatori stabiliți în UE se declară la secțiunea 4.1 (tip 5) — document, valută, valoare, curs și cotă, cu datele furnizorului opționale dar recomandate.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum se completează D301 pentru servicii cumpărate din UE?

Un serviciu cumpărat de la un prestator stabilit într-un alt stat membru UE, pentru care beneficiarul din România e obligat la plata taxei, se declară la secțiunea 4.1 din D301 — tipul 5 de operațiune.

## Temeiul legal

::: ghid-temei
Secțiunea 4.1 „Achiziții de servicii intracomunitare, pentru care beneficiarul este obligat la plata TVA conform art. 307 alin. (2)" — OPANAF nr. 592/2016, Anexa 1
:::

::: ghid-temei
"Taxa este datorată de orice persoană impozabilă (...) care este beneficiar al serviciilor care au locul prestării în România conform art. 278 alin. (2) și care sunt furnizate de către o persoană impozabilă care nu este stabilită pe teritoriul României (...)" — Codul fiscal, Legea nr. 227/2015, art. 307 alin. (2)
:::

Secțiunea 4.1 vizează exclusiv prestatorii **stabiliți în Comunitate** (UE) — un prestator din afara UE nu intră aici, ci la secțiunea 4 generală (art. 307 alin. (6)). Câmpurile de completat, per operațiune: tipul (5), numărul și data documentului, valuta, valoarea în valută, cursul de schimb, cota aplicabilă. Baza de impozitare se calculează prin înmulțirea valorii în valută cu cursul de schimb. Țara și codul de TVA al furnizorului sunt opționale pe formular, dar dacă sunt completate, operațiunea intră automat și în D390, cu codul S (achiziție intracomunitară de servicii).

## Ce se greșește în practică

- Se lasă necompletate țara/codul TVA al furnizorului "fiindcă sunt opționale" — fără ele, operațiunea nu e trecută automat și în D390, deși obligația D390 poate exista separat.
- Se aplică secțiunea 4.1 și pentru servicii de la prestatori din afara UE — aceștia intră la secțiunea 4 generală, nu la 4.1.
- Se calculează baza folosind un curs aproximativ sau curs=1, în loc de cursul de schimb real la data operațiunii.

## Ce face iConta.eu

La introducere, TVA-ul se calculează din baza indicată și cota aleasă de contabil și se stochează; baza propriu-zisă nu se stochează, ci se recalculează la generarea declarației, direct din valoarea în valută și curs — nu se acceptă un curs absent sau ≤ 0. Aplicația nu oferă automat o cotă redusă dacă niciuna nu e configurată pentru perioadă, ca să nu apară o valoare falsă în listă.

[iConta.eu](/)
