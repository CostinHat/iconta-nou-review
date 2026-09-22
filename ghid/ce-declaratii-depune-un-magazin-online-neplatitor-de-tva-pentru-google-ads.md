---
title: Ce declarații depune un magazin online neplătitor de TVA pentru Google Ads?
description: Un magazin online neplătitor de TVA care cumpără publicitate Google Ads de la Google Ireland Limited trebuie să declare taxarea inversă în Secțiunea 4.1 a D301, indiferent de suma cheltuită — plafonul de 10.000 EUR nu se aplică serviciilor.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Ce declarații depune un magazin online neplătitor de TVA pentru Google Ads?

Campaniile de publicitate Google Ads sunt facturate, pentru clienții din România, de Google Ireland Limited — o entitate stabilită în alt stat membru UE. Pentru un magazin online neplătitor de TVA, aceste cheltuieli de marketing, oricât de mici, declanșează o obligație fiscală care se declară prin D301.

## Temeiul legal

::: ghid-temei
**Articolul 307 alin. (2)**: Taxa este datorată de orice persoană impozabilă [...] care este beneficiar al serviciilor care au locul prestării în România conform art. 278 alin. (2) și care sunt furnizate de către o persoană impozabilă care nu este stabilită pe teritoriul României [...]

**Articolul 268 alin. (4)**: Prin excepție de la prevederile alin. (3) lit. a), nu sunt considerate operațiuni impozabile în România achizițiile intracomunitare de **bunuri** care îndeplinesc următoarele condiții: [...] b) valoarea totală a acestor achiziții intracomunitare nu depășește pe parcursul anului calendaristic curent sau nu a depășit pe parcursul anului calendaristic anterior plafonul de 10.000 euro [...]

Instrucțiuni OPANAF 592/2016: În secțiunea 4.1 se preiau din secțiunea 4 doar achizițiile de servicii intracomunitare, pentru care beneficiarul este obligat la plata taxei pe valoarea adăugată conform art. 307 alin. (2) din Codul fiscal.
:::

## De ce plafonul de 10.000 EUR nu ajută aici

Mulți administratori de magazine online cred că, atâta timp cât cheltuiala lunară cu Google Ads rămâne sub anumite praguri, nu există nicio obligație de declarare. Acest raționament se bazează pe o confuzie: plafonul de 10.000 EUR prevăzut la art. 268 alin. (4) se aplică exclusiv achizițiilor intracomunitare de **bunuri**, nu serviciilor.

Google Ads este un serviciu de publicitate, nu un bun. Prin urmare, taxarea inversă conform art. 307 alin. (2) se aplică de la prima factură, indiferent de suma cheltuită — chiar și o campanie de câțiva euro generează obligația de declarare în Secțiunea 4.1 a D301.

::: ghid-exemplu
Factură Google Ads de 50 EUR, curs BNR la data exigibilității 4,9700 lei/EUR.

Baza = 50 × 4,9700 = 248,50 lei
TVA (21%, cotă standard din 01.08.2025) = 248,50 × 21% = 52,19 lei

Suma întreagă se declară în Secțiunea 4.1 a D301, chiar dacă este singura factură din UE a lunii respective.
:::

## Ce se greșește în practică

- Se presupune, eronat, că sub un anumit prag valoric (adesea confundat cu plafonul de 10.000 EUR de la bunuri) cheltuielile Google Ads nu trebuie declarate.
- Se contabilizează factura Google Ads doar ca o cheltuială de marketing, fără a sesiza obligația de taxare inversă.
- Se folosește cursul de schimb de la data plății campaniei publicitare, în loc de cursul valabil la data exigibilității taxei.
- Se omite solicitarea codului special de TVA (art. 317) înainte de prima factură Google Ads primită.
- Se depune D301 lunar din obișnuință, chiar și în lunile fără nicio factură cu exigibilitate în acea perioadă, deși legea cere depunere doar când există efectiv o astfel de operațiune.

## Ce face iConta.eu

Aplicația nu implementează nicio verificare automată a plafonului de 10.000 EUR — de altfel, acest plafon nu se aplică la achizițiile de servicii precum Google Ads, deci lipsa acestei verificări nu afectează corectitudinea declarării. Pentru operațiunile de Secțiunea 4.1, aplicația calculează automat baza de impozitare din valoarea în valută și cursul introdus, aplică cota validă pentru perioadă și face rollup-ul cerut de instrucțiunile OPANAF 592/2016 în totalul Secțiunii 4.

Introducerea operațiunii este blocată dacă firma este marcată drept plătitoare de TVA în vectorul fiscal. Aplicația refuză generarea declarației dacă lipsește cursul valutar, dar nu preia automat facturile Google Ads dintr-un cont conectat și nu validează automat că furnizorul (Google Ireland Limited) este stabilit în UE — introducerea corectă a fiecărei operațiuni rămâne responsabilitatea contabilului.

[iConta.eu](/)
