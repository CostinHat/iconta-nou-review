---
title: Ce produse beneficiază de cotă redusă de TVA în 2026?
description: Cota redusă de 11% se aplică unei liste limitative de bunuri — medicamente, alimente, cărți, îngrășăminte agricole, lemn de foc, energie termică — fiecare cu excepțiile ei exacte din Codul fiscal.
published: 2026-09-23
modified: 2026-09-23
poarta: v1
---

# Ce produse beneficiază de cotă redusă de TVA în 2026?

Cota redusă de 11% nu se aplică „produselor de bază" în general, ci unei liste închise de bunuri, enumerate explicit la art. 291 alin. (2) din Codul fiscal. Dacă un produs nu se regăsește pe listă, rămâne la cota standard de 21%, indiferent cât de esențial pare.

## Temeiul legal

::: ghid-temei
Cota redusă de 11% se aplică, printre altele, pentru „livrarea de manuale școlare, cărți, ziare și reviste [...], cu excepția celor care au, în totalitate sau în mod predominant, un conținut video sau un conținut muzical audio și a celor destinate exclusiv sau în principal publicității” — Codul fiscal, art. 291 alin. (2) lit. g).
:::

## Bunurile de pe lista redusă (11%)

- **Medicamente de uz uman** (lit. a).
- **Alimente și băuturi destinate consumului uman și animal** — cu excepțiile de mai jos (lit. b).
- **Apa pentru irigații în agricultură** (lit. d).
- **Îngrășăminte și pesticide** de tipul celor folosite în producția agricolă, plus **semințe și alte produse destinate însămânțării/plantării** (lit. e, f).
- **Manuale școlare, cărți, ziare și reviste**, pe suport fizic sau electronic (lit. g).
- **Lemn de foc** (trunchiuri, butuci, vreascuri) și **peleți/brichete din lemn**, livrate persoanelor fizice sau anumitor persoane juridice (școli, spitale, unități de asistență socială) (lit. i, j).
- **Energie termică în sezonul rece**, pentru populație și pentru anumite categorii instituționale (spitale, unități de învățământ, ONG-uri, culte) (lit. k).

## Excepții — par reduse, dar rămân la 21%

Chiar în interiorul categoriei „alimente și băuturi" (lit. b), legea exclude explicit de la cota redusă:

- băuturile alcoolice,
- băuturile nealcoolice încadrate la codul NC 2202 (ape minerale/gazoase îndulcite sau aromatizate, sucuri, băuturi răcoritoare, energizante),
- alimentele cu zahăr adăugat, cu conținut total de zahăr de minimum 10g/100g (cu excepția laptelui praf pentru sugari),
- suplimentele alimentare, așa cum sunt definite de Legea 56/2021.

Similar, la cărți/publicații (lit. g), sunt excluse cele cu conținut predominant video sau muzical, ori destinate exclusiv/în principal publicității.

## Ce se greșește în practică

Cea mai frecventă greșeală este aplicarea automată a cotei de 11% oricărui produs alimentar, fără verificarea excepțiilor — un suc îndulcit sau o ciocolată nu beneficiază de cota redusă, deși aparent „aliment" în sens larg. A doua: confundarea listei de produse cu lista de servicii (cazare, restaurant, acces cultural), care are reguli proprii.

## Ce face iConta.eu

`core/cote_tva.py` ține lista limitativă (`CATEGORII_11`) cu fiecare categorie legată explicit de litera din art. 291 alin. (2), plus lista separată a excepțiilor care rămân la 21% (`EXCEPTII_21`). Motorul de potrivire (`potriveste_cota`) folosește AI pentru a încadra denumirea unui produs în categoria corectă, dar dacă răspunsul nu e clar sau AI e indisponibil, linia rămâne **nedeterminată** și emiterea facturii se blochează — aplicația nu completează tăcut o cotă implicită.

[iConta.eu](/)
