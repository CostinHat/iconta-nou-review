---
title: Impozitul micro se calculează la facturat sau la încasat?
description: Baza impozitului pe veniturile microîntreprinderilor este formată din veniturile înregistrate contabil (facturat/accrual), nu din sumele efectiv încasate.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Impozitul micro se calculează la facturat sau la încasat?

Confuzia e frecventă pentru că TVA la încasare există ca regim separat, iar mulți administratori presupun că și impozitul pe veniturile microîntreprinderilor „așteaptă" încasarea banilor. Nu e cazul: baza impozabilă se formează la momentul înregistrării contabile a venitului, indiferent dacă factura a fost sau nu achitată de client.

## Temeiul legal

::: ghid-temei
**CF art. 53 alin. (1):**
> „Baza impozabilă a impozitului pe veniturile microîntreprinderilor o constituie **veniturile din orice
> sursă**, din care se scad: a) veniturile aferente costurilor stocurilor de produse; b) veniturile
> aferente costurilor serviciilor în curs de execuție; ... j) valoarea reducerilor comerciale acordate
> ulterior facturării, înregistrate în contul «709»..."
— sursă: `anaf_surse/cod_fiscal_227_2015_consolidat.txt:6480-6519`

**CF art. 51 alin. (1):**
> „Cota de impozit pe veniturile microîntreprinderilor este de 1%."
— sursă: `anaf_surse/cod_fiscal_227_2015_consolidat.html`
:::

## Ce înseamnă în practică „facturat, nu încasat"

Baza de calcul se citește din rulajele conturilor de venituri — 70x (venituri din vânzarea de produse/mărfuri/servicii), 75x (alte venituri din exploatare), 76x (venituri financiare) — din care se scade contul 709 (reduceri comerciale acordate ulterior facturării). Aceasta este exact baza pe care legea o numește „venituri din orice sursă", minus excepțiile enumerate la art. 53 alin. (1) lit. a)-j).

Practic: o factură emisă și înregistrată în luna martie intră în baza trimestrului I, chiar dacă clientul o achită abia în mai. Nu contează data plății, contează data înregistrării venitului conform principiului contabilității de angajament.

::: ghid-exemplu
O microîntreprindere emite în trimestrul II facturi în valoare totală de 50.000 lei (cont 704), din care 12.000 lei rămân neîncasate la finalul trimestrului. Baza impozabilă a trimestrului II este tot 50.000 lei (presupunând că nu există alte deduceri din art. 53), iar impozitul datorat este 50.000 × 1% = 500 lei — indiferent că 12.000 lei nu au fost încă încasați.
:::

## Ce se greșește în practică

- Se scad din baza de calcul facturile neîncasate, tratând impozitul micro ca și cum ar fi „la încasare" — greșit, baza e la facturat.
- Se confundă regimul micro cu TVA la încasare (care e un regim de TVA, complet separat de impozitul pe venit).
- Se omite scăderea contului 709 (reduceri comerciale acordate ulterior facturării) din baza impozabilă.
- Se aplică o cotă veche (3%, pentru firme fără salariați) — de la 1 ianuarie 2026, cota este unic 1%, indiferent de numărul de salariați.
- Se cumulează veniturile de la începutul anului, deși fiecare trimestru se calculează independent.

## Ce face iConta.eu

Motorul de calcul (`core/d100.py`, funcția `deriva_obligatii`) determină baza impozitului micro (cod obligație 121) ca `venituri_trimestru × 1%`, unde veniturile trimestrului sunt citite din conturile 70x/75x/76x minus 709, pentru perioada exactă a trimestrului curent — nu cumulat de la 1 ianuarie. Datele sunt preluate de `d100.pull()` direct din înregistrările contabile ale firmei, deci suma calculată reflectă exact baza „la facturat" impusă de art. 53 alin. (1), nu sumele încasate.

[iConta.eu](/)
