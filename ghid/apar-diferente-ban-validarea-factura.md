---
title: "De ce apar diferențe de un ban la validarea e-Factura"
description: "Diferențele de un ban la validarea RO e-Factura vin, de regulă, din rotunjirea TVA calculată pe fiecare linie a facturii, comparată cu TVA calculată pe totalul documentului."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# De ce apar diferențe de un ban la validarea e-Factura

O factură pare corectă — totalul, cota de TVA, sumele adunate manual dau bine — și totuși sistemul RO e-Factura semnalează o diferență de un ban între suma TVA din antet și suma rezultată din liniile facturii. Cauza e aproape întotdeauna aceeași: modul în care se face rotunjirea.

## Temeiul legal

::: ghid-temei
„Cota standard se aplică asupra bazei de impozitare pentru operațiunile impozabile care nu sunt scutite de taxă sau care nu sunt supuse cotei reduse, iar nivelul acesteia este 21%."; regula generală de determinare a bazei de impozitare a TVA rezultă din art. 286-290 din Codul fiscal, fără ca legea sau normele metodologice să stabilească explicit o toleranță de rotunjire pentru facturile electronice. Standardul tehnic de rotunjire (calcul pe linie vs. calcul pe total document) e o regulă de structură a facturii electronice (EN 16931 / RO_CIUS), nu o normă fiscală de sine stătătoare.
— Legea 227/2015 (Codul fiscal), art. 291 alin. (1) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt); structura tehnică a facturii electronice, OUG 120/2021
:::

De ce apare, tehnic, diferența de un ban:

- Standardul european de facturare electronică (pe care se bazează specificațiile RO_CIUS din RO e-Factura) calculează TVA **pe fiecare linie** a facturii, rotunjind la doi zecimali, apoi însumează liniile pentru totalul TVA din document.
- Dacă softul de facturare calculează TVA **o singură dată, pe totalul bazei de impozitare** a documentului (nu linie cu linie), suma poate diferi cu un ban față de suma liniilor rotunjite individual — ambele metode sunt corecte matematic, dar produc rezultate diferite din cauza rotunjirilor succesive.
- Legea fiscală nu stabilește ea însăși o toleranță pentru astfel de diferențe — validarea e o regulă de structură tehnică a fișierului XML transmis către sistemul RO e-Factura, nu o normă de drept fiscal material.
- Practic, soluția e alinierea metodei de calcul (pe linie, cu rotunjire per linie, apoi însumare) la specificația așteptată de validatorul RO e-Factura, nu „forțarea" totalului să coincidă printr-o ajustare manuală ulterioară.

## Ce se greșește în practică

- Se corectează manual totalul facturii ca să „dispară" diferența de un ban, fără să se identifice și să se corecteze metoda de calcul care a generat-o — problema reapare la fiecare factură cu mai multe linii la cote diferite.
- Se presupune că diferența de un ban e o eroare de conținut fiscal (cotă greșită, bază de impozitare greșită), când de fapt e aproape întotdeauna o chestiune de rotunjire pe linie vs. pe total.
- Nu se verifică dacă softul de facturare rotunjește TVA per linie sau per document, ceea ce face imposibilă diagnosticarea rapidă a cauzei quando apare eroarea de validare.

## Ce face iConta.eu

La data acestui ghid, iConta.eu calculează TVA la emiterea facturilor conform structurii standard așteptate de sistemul RO e-Factura; pentru diferențele de rotunjire semnalate la validare, contabilul trebuie să verifice manual liniile facturii cu cote de TVA diferite — aplicația nu oferă, la acest moment, un diagnostic automat al cauzei exacte a unei respingeri de validare.

[iConta.eu](/)
