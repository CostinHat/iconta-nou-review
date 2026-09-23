---
title: "Ce fac dacă furnizorul a trecut CUI-ul greșit pe factură?"
description: O factură primită cu CUI-ul tău greșit trecut de furnizor nu se corectează unilateral — remediul e ca furnizorul să storneze și să reemită documentul. Tot ce poți face din partea ta e să verifici CUI-ul corect și să ceri corectarea la sursă.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Ce fac dacă furnizorul a trecut CUI-ul greșit pe factură?

Spre deosebire de o factură emisă chiar de tine cu o greșeală, aici documentul greșit vine de la altcineva — furnizorul. Nu poți corecta unilateral un document emis de un terț; poți doar semnala eroarea și cere corectarea, la sursă, de către cel care a emis factura.

## Temeiul legal

::: ghid-temei
„Orice persoană sau entitate care este subiect într-un raport juridic fiscal se înregistrează fiscal primind un cod de identificare fiscală." — Legea nr. 207/2015 privind Codul de procedură fiscală, art. 82 alin. (1)
:::

O factură care te identifică greșit (CUI eronat) nu te leagă corect, ca subiect fiscal, de documentul respectiv — de aceea corectarea nu e opțională, indiferent cine a făcut greșeala.

## Ce faci concret

1. **Verifică CUI-ul tău corect** — confirmă exact codul care trebuie să apară pe factură, folosind aceleași date din certificatul de înregistrare fiscală.
2. **Anunță furnizorul** — cere corectarea documentului. Mecanismul corect, cel puțin în iConta.eu pentru facturile emise chiar din aplicație, e stornarea facturii greșite urmată de emiterea alteia noi, cu CUI-ul corect — nu editarea directă a documentului deja emis.
3. **Nu înregistra factura greșită ca atare în contabilitate** dacă CUI-ul eronat te împiedică să o asociezi corect ca document justificativ — așteaptă documentul corectat.

## Ce se greșește în practică

- Se acceptă și se înregistrează factura cu CUI greșit „ca atare", considerând eroarea neimportantă — un CUI greșit înseamnă că documentul, formal, nu te identifică drept beneficiar real al operațiunii.
- Se încearcă „corectarea" CUI-ului direct în evidența proprie, fără să se ceară un document nou de la furnizor — o asemenea corectare unilaterală nu schimbă factura originală emisă de furnizor.
- Se presupune că orice greșeală de CUI pe o factură primită se rezolvă la fel ca o greșeală pe o factură emisă chiar de tine — remediul depinde de sistemul folosit de furnizor pentru a-și corecta propriile documente, nu de aplicația ta.

## Ce face iConta.eu

Verificat: mecanismul de corectare din iConta.eu (stornare + reemitere) a fost confirmat pentru facturile emise chiar din aplicație de propria firmă (`POST /tenants/{tenant_id}/facturi/{factura_id}/storno`), cu mențiunea explicită din cod că „stornarea nu corectează documentul emis — emite AL DOILEA document". Pentru facturile primite de la un furnizor extern, cu eroare de CUI, corectarea depinde de sistemul de facturare al furnizorului respectiv — acest flux specific (corectarea unui document primit) nu a fost verificat punctual în acest context. Ce poți face în iConta.eu e să verifici CUI-ul corect al firmei tale sau al furnizorului direct la ANAF, înainte de a solicita documentul corectat.

[iConta.eu](/)
