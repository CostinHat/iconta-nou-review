---
title: Cum se tratează o încasare parțială în sistemul TVA la încasare?
description: La fiecare încasare parțială sub sistemul TVA la încasare, taxa exigibilă se calculează prin suta mărită pe suma efectiv încasată, nu pe toată factura — dar legea nu prescrie pe ce factură se alocă o încasare parțială când clientul are mai multe deschise (art. 282 Cod fiscal).
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Cum se tratează o încasare parțială în sistemul TVA la încasare?

Sub regimul normal de TVA, o încasare parțială nu schimbă nimic contabil — taxa era deja exigibilă integral la facturare. Sub TVA la încasare, fiecare leu încasat contează separat: taxa devine exigibilă treptat, pe măsură ce banii intră efectiv în cont, nu dintr-odată la data facturii.

## Temeiul legal

::: ghid-temei
**Art. 282 din Codul fiscal (Legea 227/2015) — Exigibilitatea taxei.**

**Alin. (3)**: *„... exigibilitatea taxei intervine la data încasării contravalorii integrale sau **parțiale** a livrării de bunuri ori a prestării de servicii, în cazul persoanelor impozabile care optează în acest sens, denumite în continuare persoane care aplică sistemul TVA la încasare."*

**Alin. (8)**: *„Pentru determinarea taxei aferente încasării contravalorii integrale sau parțiale a livrării de bunuri ori a prestării de servicii, care devine exigibilă potrivit prevederilor alin. (3), fiecare încasare totală sau parțială se consideră că include și taxa aferentă."*
:::

## Calculul pe fiecare încasare parțială

Legea tratează explicit încasarea parțială la egalitate cu cea integrală (alin. (3): „integrale sau parțiale"). Pentru fiecare sumă încasată — indiferent cât de mică față de totalul facturii — se aplică aceeași formulă din alin. (8): suma încasată se consideră că include deja taxa, deci taxa se extrage prin suta mărită:

```
TVA exigibil (din acea încasare) = suma încasată × cotă / (100 + cotă)
```

Dacă un client plătește 30% dintr-o factură, TVA-ul exigibil e 30% din TVA-ul total al facturii — nu tot TVA-ul dintr-odată și nu proporția din baza de impozitare fără taxă calculată separat. Restul TVA-ului rămâne neexigibil (în 4428, dacă factura e emisă), până la următoarea încasare.

## Ce NU rezolvă legea: pe ce factură se aplică încasarea, când clientul are mai multe deschise

Aici apare o problemă practică pe care art. 282 nu o tranșează: dacă un client are **mai multe facturi deschise** și plătește o sumă care nu acoperă exact vreuna dintre ele, pe care factură se consideră că s-a făcut încasarea?

Legea nu prescrie o ordine de alocare a unei încasări pe facturile multiple ale aceluiași partener. Asta e o decizie de organizare contabilă a fiecărei firme (sau a aplicației cu care lucrează), nu o obligație legală explicită — merită tratată ca atare, nu ca „așa scrie legea".

Practicile uzuale, niciuna impusă de art. 282:

- **alocare pe factura identificată explicit** de client (cel mai frecvent, prin mențiunea de pe ordinul de plată sau prin înțelegere directă) — soluția cea mai sigură, pentru că elimină orice ambiguitate;
- **alocare cronologică (FIFO)** — încasarea acoperă întâi cea mai veche factură deschisă, apoi următoarea, ș.a.m.d.;
- **alocare proporțională** pe toate facturile deschise, în funcție de soldul fiecăreia.

Oricare variantă e o **alegere de organizare**, nu o cerință a art. 282 — important e ca alocarea aleasă să fie documentată consecvent, pentru că de ea depinde exact pe ce sumă (și deci ce TVA) devine exigibilă la acea încasare.

## Ce se greșește în practică

- **Se calculează TVA-ul din încasarea parțială aplicând cota direct la sumă**, nu prin suta mărită. Alin. (8) spune clar că suma încasată include deja taxa — formula corectă e `suma × cotă/(100+cotă)`, nu `suma × cotă`.
- **Se presupune că legea impune o anumită ordine de alocare** (de exemplu, strict cronologică) când clientul are mai multe facturi deschise. Art. 282 nu prescrie nicio ordine — e o decizie de organizare, nu un text de lege, și trebuie tratată/documentată ca atare.
- **Se face transferul din TVA neexigibilă în TVA colectată pe toată factura**, la prima încasare parțială, în loc să se limiteze strict la suma efectiv încasată din acea tranșă.

## Ce face iConta.eu

Pentru fiecare încasare, motorul de calcul extrage TVA-ul exigibil din suma alocată prin suta mărită (`suma × cotă/(100+cotă)`, rotunjit la 2 zecimale), conform alin. (8) — indiferent dacă e o încasare integrală sau parțială.

Când o încasare trebuie repartizată pe mai multe facturi deschise ale aceluiași partener, reconcilierea încearcă întâi o potrivire exactă (o singură factură cu soldul identic, sau o combinație exactă de facturi), iar dacă nu găsește niciuna, alocă suma cronologic, pe facturile cele mai vechi întâi (FIFO) — cu alocarea parțială rămasă marcată pentru confirmare. **Această ordine FIFO e o alegere de organizare a aplicației, nu o cerință a art. 282** — legea nu prescrie ordinea de alocare a unei încasări pe facturi multiple, așa cum am arătat mai sus.

Pentru firmele marcate ca aplicând TVA la încasare, transferul contabil din 4428 în 4427 (pentru facturi emise) sau din 4428 în 4426 (pentru facturi primite) nu se face automat la contare — factura trebuie contată manual, de un om, tocmai pentru că suma exigibilă depinde de alocarea încasării pe factură. Menționăm și că, la data acestui ghid, mecanismul respectiv nu are încă nicio firmă reală în regim în portofoliu — e verificat prin teste, nu prin utilizare efectivă.

[iConta.eu](/)
