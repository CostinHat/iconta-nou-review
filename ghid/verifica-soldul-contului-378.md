---
title: Cum se verifică soldul contului 378?
description: Soldul contului 378 se verifică prin fișa de cont (sold inițial + rulaj credit − rulaj debit, cumulat de la 1 ianuarie) și trebuie să corespundă cu adaosul comercial aferent mărfurilor rămase efectiv în stoc la data verificării.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum se verifică soldul contului 378?

Soldul contului 378 „Diferențe de preț la mărfuri” nu e o cifră abstractă — el trebuie să corespundă mereu cu adaosul comercial „ascuns” în mărfurile rămase fizic în stoc. Verificarea lui e utilă mai ales înainte de un inventar sau de o descărcare de gestiune, ca să prindeți din timp o eroare de calcul acumulată în lunile anterioare.

## Temeiul legal

::: ghid-temei
„Contul 378 «Diferențe de preț la mărfuri» ... Soldul contului reprezintă valoarea adaosului comercial aferent mărfurilor existente în stoc la sfârșitul perioadei.”

— *OMFP 1802/2014, Capitolul 16, funcțiunea contului 378.*
:::

## Cum se calculează și se verifică soldul

1. **Soldul contabil** se obține din fișa de cont (Cartea mare pentru 378, sau înlocuitorul ei legal, fișa de cont): sold inițial + total intrări (credit, adaos aferent recepțiilor) − total ieșiri (debit, adaos descărcat la vânzări), cumulat de la 1 ianuarie.
2. **Verificarea de coerență**: soldul contului 378 trebuie să reprezinte, la un anumit moment, adaosul comercial cuprins în mărfurile aflate încă în stoc — dacă îl raportați la soldul contului 371 (mărfuri la preț de vânzare, inclusiv TVA neexigibilă), procentul obținut ar trebui să fie apropiat de coeficientul de adaos folosit de firmă pe categoria respectivă de mărfuri.
3. **Semnal de eroare**: un sold negativ pe 378, sau un sold care crește nejustificat de la o lună la alta fără recepții noi cu adaos, indică de regulă o descărcare de gestiune calculată greșit într-o lună anterioară (adaos descărcat prea puțin sau prea mult față de vânzările reale).

## Ce se greșește în practică

- Se verifică soldul contului 378 izolat, fără a-l raporta la stocul fizic real (371) — un sold „plauzibil” contabil poate ascunde o eroare compensată de o eroare pe 371 sau 4428.
- Se ignoră faptul că soldul se calculează cumulat de la începutul exercițiului financiar, nu doar din ultima lună — o eroare dintr-o lună anterioară rămâne în soldul cumulat până e corectată explicit.
- Se presupune că soldul contului 378 trebuie să fie mereu pozitiv și „rotund” — un sold mic sau chiar aproape de zero e normal dacă marfa cu adaos mare s-a vândut aproape integral.

## Ce face iConta.eu

Soldul contului 378, ca al oricărui alt cont, se verifică prin ruta `/tenants/{tenant_id}/fisa-cont` (motor `core/fisa_cont.py`), care permite filtrarea pe cont (378) și interval de an/lună — echivalentul funcțional al Cărții mari pentru acest cont, conform OMFP 2634/2015 (Registrul Cartea mare poate fi înlocuit cu Fișa de cont pentru operațiuni diverse).

Soldul e alimentat de motorul de gestiune global-valorică (`core/stocuri.py`): la recepție, prin `nir_gv` (linia `371=378`), la descărcarea lunară, prin `descarcare_gv` (linia `378=371`, cu suma calculată din coeficientul K). Funcția `coeficient_k(si_378, rc_378, si_371, rd_371, si_4428, rc_4428)` refuză explicit să calculeze dacă numitorul (stocul la preț de înregistrare, fără TVA neexigibilă) ajunge la zero sau negativ — deci o eroare gravă de sold pe 371/378/4428 oprește calculul, cu mesaj explicit, în loc să producă tăcut un coeficient greșit.

O atenție de reținut: `descarca_luna` citește rulajele 371/378/4428 **fără filtrare pe sursă** — dacă firma folosește și un mecanism manual separat pe contul 4428 (de exemplu, TVA la încasare), acele mișcări s-ar aduna la rulajul folosit pentru calculul coeficientului K, denaturând soldul rezultat pe 378. Dacă soldul verificat pe 378 nu se leagă cu stocul fizic, verificați întâi dacă firma are și alte note manuale pe 4428, în afara descărcării de gestiune.

[iConta.eu](/)
