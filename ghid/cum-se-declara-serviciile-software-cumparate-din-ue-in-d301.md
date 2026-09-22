---
title: Cum se declară serviciile software cumpărate din UE în D301?
description: Licențele și abonamentele software cumpărate de la un furnizor stabilit în UE se declară în Secțiunea 4.1 a D301, prin taxare inversă conform art. 307 alin. (2), indiferent de valoarea achiziției.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Cum se declară serviciile software cumpărate din UE în D301?

Licențele software, abonamentele SaaS sau serviciile de mentenanță IT cumpărate de la un furnizor stabilit într-un alt stat membru UE reprezintă, pentru o firmă română neplătitoare de TVA, achiziții de servicii intracomunitare. Ele se declară în Secțiunea 4.1 a D301, prin mecanismul taxării inverse.

## Temeiul legal

::: ghid-temei
**Articolul 307 alin. (2)**: Taxa este datorată de orice persoană impozabilă [...] care este beneficiar al serviciilor care au locul prestării în România conform art. 278 alin. (2) și care sunt furnizate de către o persoană impozabilă care nu este stabilită pe teritoriul României [...]

**Articolul 278 alin. (2)**: Locul de prestare a serviciilor către o persoană impozabilă care acționează ca atare este locul unde respectiva persoană care primește serviciile își are stabilit sediul activității sale economice. [...]

Instrucțiuni OPANAF 592/2016 — Secțiunea 4.1: se completează de către [...] persoanele juridice neimpozabile care sunt înregistrate conform art. 317 [...], care sunt beneficiare ale serviciilor [...] furnizate de către persoane impozabile care nu sunt stabilite pe teritoriul României conform art. 266 alin. (2) din Codul fiscal, **dar care sunt stabilite în Comunitate** [...]

**Articolul 268 alin. (4)**: Prin excepție de la prevederile alin. (3) lit. a), nu sunt considerate operațiuni impozabile în România achizițiile intracomunitare de **bunuri** care îndeplinesc următoarele condiții: [...] b) valoarea totală a acestor achiziții intracomunitare nu depășește pe parcursul anului calendaristic curent sau nu a depășit pe parcursul anului calendaristic anterior plafonul de 10.000 euro [...]
:::

## Indiferent de valoare — nu există plafon la servicii

O confuzie frecventă vine din suprapunerea cu regulile de la achiziții de bunuri: plafonul de 10.000 EUR de la art. 268 alin. (4) se aplică strict achizițiilor intracomunitare de **bunuri**, nu de servicii. Licențele software, abonamentele sau serviciile de suport IT sunt servicii — taxarea inversă conform art. 307 alin. (2) se aplică de la prima factură, indiferent de sumă, atât timp cât furnizorul este stabilit în alt stat membru UE.

Condiția pentru încadrarea în Secțiunea 4.1 (și nu în Secțiunea 4 generică) este ca furnizorul de software să fie stabilit în Comunitate — de exemplu, o companie cu sediul în Irlanda, Olanda sau Germania. Dacă furnizorul ar fi din afara UE, operațiunea ar trebui declarată la Secțiunea 4 generică, cu alt temei legal (art. 307 alin. (6)).

::: ghid-exemplu
Licență software anuală de 200 EUR, cumpărată de la un furnizor stabilit în UE, curs BNR la data exigibilității 4,9700 lei/EUR.

Baza = 200 × 4,9700 = 994,00 lei
TVA (21%, cotă standard din 01.08.2025) = 994,00 × 21% = 208,74 lei

Suma se declară integral, la prima achiziție, în Secțiunea 4.1 a D301 — nu există un prag valoric sub care obligația să nu existe.
:::

## Ce se greșește în practică

- Se aplică, din eroare, plafonul de 10.000 EUR (valabil doar pentru bunuri) și la achizițiile de licențe sau abonamente software.
- Se declară achiziția de software în Secțiunea 1 (rezervată bunurilor) în loc de Secțiunea 4.1 (servicii).
- Se folosește cursul de schimb de la data plății, în loc de cursul valabil la data exigibilității taxei.
- Se omite obținerea codului special de TVA (art. 317) înainte de prima achiziție de software din UE.

## Ce face iConta.eu

Pentru operațiunile de tip servicii intracomunitare (Secțiunea 4.1), aplicația calculează automat baza de impozitare din valoarea în valută și cursul introdus, aplică cota validă pentru perioada exigibilității și face rollup-ul cerut de instrucțiunile OPANAF 592/2016 în totalul Secțiunii 4. Aplicația refuză generarea declarației dacă lipsește cursul valutar.

Aplicația nu implementează nicio verificare automată a plafonului de 10.000 EUR — de altfel, acest plafon nu se aplică la servicii, deci nu afectează achizițiile de software. Aplicația nu validează nici țara furnizorului împotriva unei liste de state membre UE la introducerea operațiunii; câmpul rămâne opțional și liber, iar încadrarea corectă a operațiunii (Secțiunea 4.1 vs. Secțiunea 4) rămâne responsabilitatea contabilului.

[iConta.eu](/)
