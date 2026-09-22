---
title: Cum tratez comisionul Booking din punct de vedere TVA?
description: Comisionul reținut de Booking.com B.V. (Olanda) este o achiziție de serviciu intracomunitar de la un furnizor stabilit în UE și se declară, prin taxare inversă, în Secțiunea 4.1 a D301.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Cum tratez comisionul Booking din punct de vedere TVA?

Structurile de cazare (pensiuni, hoteluri mici, apartamente în regim hotelier) care listează unități pe platforma Booking.com plătesc un comision reținut de Booking.com B.V., entitate stabilită în Olanda. Pentru o firmă română neplătitoare de TVA, acest comision este o achiziție de serviciu intracomunitar, supusă acelorași reguli de taxare inversă ca orice alt serviciu cumpărat din UE.

## Temeiul legal

::: ghid-temei
**Articolul 307 alin. (2)**: Taxa este datorată de orice persoană impozabilă [...] care este beneficiar al serviciilor care au locul prestării în România conform art. 278 alin. (2) și care sunt furnizate de către o persoană impozabilă care nu este stabilită pe teritoriul României [...]

**Articolul 278 alin. (2)**: Locul de prestare a serviciilor către o persoană impozabilă care acționează ca atare este locul unde respectiva persoană care primește serviciile își are stabilit sediul activității sale economice. [...]

Instrucțiuni OPANAF 592/2016 — Secțiunea 4.1: se completează de către [...] persoanele juridice neimpozabile care sunt înregistrate conform art. 317 [...], care sunt beneficiare ale serviciilor [...] furnizate de către persoane impozabile care nu sunt stabilite pe teritoriul României conform art. 266 alin. (2) din Codul fiscal, **dar care sunt stabilite în Comunitate** [...]
:::

## De ce comisionul Booking intră la Secțiunea 4.1

Comisionul Booking este, din punct de vedere fiscal, contravaloarea unui serviciu de intermediere/publicitate prestat de Booking.com B.V. către structura de cazare din România. Pentru că beneficiarul (structura de cazare românească) își are sediul activității economice în România, locul prestării este considerat România (art. 278 alin. (2)), iar firma română este obligată la plata TVA prin taxare inversă (art. 307 alin. (2)).

Pentru că Booking.com B.V. este stabilit în Olanda — stat membru UE —, operațiunea se încadrează în Secțiunea 4.1 a D301, nu în Secțiunea 4 generică. Această încadrare este specifică furnizorului: dacă platforma prin care se intermediază rezervări ar fi o entitate stabilită în afara UE, tratamentul corect ar fi Secțiunea 4 generică, nu 4.1.

::: ghid-exemplu
Comision Booking reținut de 30 EUR dintr-o rezervare, curs BNR la data exigibilității 4,9700 lei/EUR.

Baza = 30 × 4,9700 = 149,10 lei
TVA (21%, cotă standard din 01.08.2025) = 149,10 × 21% = 31,31 lei

Suma se declară în Secțiunea 4.1 a D301, pentru luna exigibilității taxei, indiferent de valoarea comisionului.
:::

## Ce se greșește în practică

- Comisionul este tratat doar ca o reducere a încasării (net de comision), fără a se sesiza obligația separată de taxare inversă și declarare în D301.
- Se folosește cursul valutar de la data extrasului de cont sau al decontului lunar Booking, în loc de cursul valabil la data exigibilității taxei.
- Se omite solicitarea codului special de TVA (art. 317) înainte de primul comision reținut de Booking.
- Se presupune că, sub un anumit prag valoric, comisionul nu trebuie declarat — la servicii nu există un plafon similar celui de 10.000 EUR aplicabil bunurilor.

## Ce face iConta.eu

Pentru operațiunile de Secțiunea 4.1, aplicația calculează automat baza de impozitare din valoarea în valută și cursul introdus, cu rotunjire aritmetică (`ROUND_HALF_UP`), aplică cota validă pentru perioadă și face rollup-ul cerut de instrucțiunile OPANAF 592/2016 în totalul Secțiunii 4. Generarea declarației este refuzată dacă lipsește cursul valutar.

Aplicația nu validează automat că furnizorul introdus (Booking.com B.V.) este efectiv stabilit în UE — câmpul de țară al partenerului este opțional și liber, regula fiind confirmată doar prin instrucțiunile OPANAF 592/2016, nu printr-o verificare automată în cod. Încadrarea corectă a comisionului Booking în Secțiunea 4.1 (și nu 4) rămâne, astfel, responsabilitatea contabilului.

[iConta.eu](/)
