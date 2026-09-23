---
title: Cum se calculează TVA într-un restaurant în 2026?
description: Calculul TVA într-un restaurant pornește de la o distincție simplă — e serviciu de restaurant sau livrare de bunuri la pachet? — apoi separă alimentele (11%) de băuturile alcoolice/NC 2202 (21%), linie cu linie.
published: 2026-09-23
modified: 2026-09-23
poarta: v1
---

# Cum se calculează TVA într-un restaurant în 2026?

TVA într-un restaurant nu se calculează cu o singură cotă aplicată la tot bonul, ci separat, pe fiecare tip de produs vândut — pentru că, în funcție de ce vinzi și cum îl servești, cota corectă poate fi 11% sau 21%.

## Temeiul legal

::: ghid-temei
„Serviciile de restaurant și de catering reprezintă servicii care constau în furnizarea de produse alimentare și/sau de băutură [...] însoțită de servicii conexe suficiente care să permită consumul imediat al acestora [...] Furnizarea de produse alimentare și/sau de băuturi [...] fără vreun alt serviciu conex, nu se consideră a fi servicii de restaurant sau catering” — HG 1/2016, normele de aplicare a art. 291 Cod fiscal, pct. 18.
:::

## Pașii de calcul

1. **Stabilește dacă e serviciu de restaurant sau livrare de bunuri.** Dacă mâncarea e servită la masă, cu deservire, în spațiul restaurantului sau la eveniment (catering) — e serviciu de restaurant/catering, la cota de 11% (art. 291 alin. (2) lit. n), cu excepția de mai jos. Dacă e vândută la pachet, fără servicii conexe, e livrare de bunuri, la cota alimentului respectiv.
2. **Separă băuturile alcoolice și NC 2202.** Indiferent dacă sunt servite la masă sau la pachet, băuturile alcoolice (inclusiv orice amestec cu băuturi nealcoolice) și băuturile nealcoolice îndulcite/aromatizate de tip NC 2202 (sucuri, cola, energizante) rămân la cota standard de 21% — sunt excepția explicită din lege.
3. **Calculează separat baza și TVA pentru fiecare cotă.** Un bon cu meniu (11%) și o bere (21%) generează două linii de TVA distincte, nu o cotă „medie" sau dominantă.

## Un exemplu simplu

Un client comandă un meniu de prânz (masă servită, 40 lei) și o bere (masă servită, 12 lei):

- Meniul: bază 40 lei × 11% = 4,40 lei TVA.
- Berea: bază 12 lei × 21% = 2,52 lei TVA.
- Total TVA de colectat pe bon: 6,92 lei, nu 52 lei × o cotă unică.

## Ce se greșește în practică

Cea mai frecventă greșeală este aplicarea unei singure cote pe tot bonul, de obicei 11%, inclusiv pe băuturile alcoolice — situație în care TVA colectat e subevaluat. A doua: tratarea unui suc îndulcit sau a unui energizant ca „băutură nealcoolică obișnuită" la 11%, deși intră explicit la excepția NC 2202.

## Ce face iConta.eu

Motorul de potrivire cotă (`core/cote_tva.py`) distinge explicit categoria `restaurant_catering` (11%) de excepțiile `bauturi_alcoolice` și `bauturi_nc2202` (21%), astfel încât fiecare linie de bon/factură primește cota corectă în funcție de denumirea produsului, nu o cotă unică aplicată global pe document.

[iConta.eu](/)
