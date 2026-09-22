---
title: Cum se înregistrează o factură Microsoft primită din Uniunea Europeană?
description: Facturile Microsoft 365 sau alte licențe Microsoft emise de Microsoft Ireland Operations Limited generează, pentru o firmă română neplătitoare de TVA, obligația de taxare inversă și declarare în Secțiunea 4.1 a D301.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Cum se înregistrează o factură Microsoft primită din Uniunea Europeană?

Licențele Microsoft 365 și alte servicii Microsoft sunt facturate, pentru clienții din România, de Microsoft Ireland Operations Limited — o entitate stabilită în Irlanda, deci în Comunitate (UE). Pentru o firmă română neplătitoare de TVA, această factură declanșează aceleași obligații ca orice altă achiziție de serviciu intracomunitar.

## Temeiul legal

::: ghid-temei
**Articolul 307 alin. (2)**: Taxa este datorată de orice persoană impozabilă [...] care este beneficiar al serviciilor care au locul prestării în România conform art. 278 alin. (2) și care sunt furnizate de către o persoană impozabilă care nu este stabilită pe teritoriul României [...]

**Articolul 278 alin. (2)**: Locul de prestare a serviciilor către o persoană impozabilă care acționează ca atare este locul unde respectiva persoană care primește serviciile își are stabilit sediul activității sale economice. [...]

Instrucțiuni OPANAF 592/2016 — Secțiunea 4.1: se completează de către [...] persoanele juridice neimpozabile care sunt înregistrate conform art. 317 [...], care sunt beneficiare ale serviciilor [...] furnizate de către persoane impozabile care nu sunt stabilite pe teritoriul României conform art. 266 alin. (2) din Codul fiscal, **dar care sunt stabilite în Comunitate** [...]

**Articolul 290 alin. (2)**: Dacă elementele folosite pentru stabilirea bazei de impozitare a unei operațiuni, alta decât importul de bunuri, se exprimă în valută, cursul de schimb care se aplică este ultimul curs de schimb comunicat de Banca Națională a României sau ultimul curs de schimb publicat de Banca Centrală Europeană ori cursul de schimb utilizat de banca prin care se efectuează decontările, **valabil la data la care intervine exigibilitatea taxei** pentru operațiunea în cauză [...]
:::

## De la primirea facturii la declararea în D301

Pentru că beneficiarul (firma română) își are sediul activității economice în România, locul prestării serviciului Microsoft este considerat România (art. 278 alin. (2)), iar firma română, nu Microsoft Ireland Operations Limited, este obligată la plata TVA prin taxare inversă (art. 307 alin. (2)). Pentru că furnizorul — Microsoft Ireland Operations Limited — este stabilit în Comunitate, operațiunea se încadrează în Secțiunea 4.1 a D301, nu în Secțiunea 4 generică.

Baza de impozitare se determină în lei, folosind cursul de schimb valabil la data exigibilității taxei, iar TVA se calculează la cota validă pentru perioadă. Această obligație apare indiferent de valoarea abonamentului sau a licenței cumpărate — nu există un plafon minim sub care Secțiunea 4.1 să nu se aplice.

::: ghid-exemplu
Licență Microsoft 365 de 8 EUR/lună, curs BNR la data exigibilității 4,9700 lei/EUR.

Baza = 8 × 4,9700 = 39,76 lei
TVA (21%, cotă standard din 01.08.2025) = 39,76 × 21% = 8,35 lei

Suma se declară în Secțiunea 4.1 a D301, pentru luna exigibilității.
:::

## Ce se greșește în practică

- Factura Microsoft este introdusă doar ca o cheltuială operațională, fără a se sesiza obligația de taxare inversă.
- Se folosește cursul valutar de la data facturii sau a plății cardului, în loc de cursul valabil la data exigibilității taxei.
- Se declară operațiunea în Secțiunea 4 generică, deși Microsoft Ireland Operations Limited este stabilit în UE, deci operațiunea aparține Secțiunii 4.1.
- Se omite solicitarea codului special de TVA (art. 317) înainte de primirea primei facturi Microsoft, ceea ce poate duce la înregistrare din oficiu de către ANAF.

## Ce face iConta.eu

Baza de impozitare se calculează automat de aplicație (`baza = round(val_valuta × curs, 0)`), cu rotunjire aritmetică (`ROUND_HALF_UP`), pe baza cursului introdus manual de contabil — nu există o integrare automată cu cursul BNR sau BCE, iar generarea declarației este refuzată explicit dacă lipsește cursul valutar sau acesta este introdus ca zero. Pentru operațiunile de Secțiunea 4.1, aplicația face rollup automat al bazei și TVA în totalul Secțiunii 4, conform instrucțiunilor OPANAF 592/2016.

Aplicația nu validează automat că furnizorul introdus (de exemplu Microsoft Ireland Operations Limited) este efectiv stabilit în UE — câmpul de țară al partenerului este opțional și liber, iar încadrarea corectă a operațiunii în Secțiunea 4.1 rămâne responsabilitatea contabilului.

[iConta.eu](/)
