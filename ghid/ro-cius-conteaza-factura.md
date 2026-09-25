---
title: "Ce este RO_CIUS și de ce contează la e-Factura?"
description: "Ce sunt specificațiile naționale RO_CIUS pentru factura electronică și de ce o factură validă tehnic poate fi totuși respinsă de sistemul RO e-Factura."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Ce este RO_CIUS și de ce contează la e-Factura?

O factură electronică nu ajunge validă în sistemul RO e-Factura doar pentru că respectă standardul european general (EN 16931). România a adăugat peste acest standard un set de reguli naționale suplimentare — RO_CIUS — iar o factură care nu respectă și aceste reguli specifice e respinsă de validatorul ANAF, chiar dacă e un XML corect din punct de vedere tehnic.

## Temeiul legal

::: ghid-temei
„k) specificațiile naționale de utilizare a facturii electronice - RO_CIUS - specificații tehnice de utilizare a elementelor de bază ale facturii electronice așa cum sunt prevăzute în standardul european SR EN 16931-1, aplicabile la nivel național"
— Ordonanța de urgență nr. 120/2021 privind sistemul național RO e-Factura, art. 2 alin. (1) lit. k) (sursă: anaf_surse/oug_120_2021.txt)
:::

- RO_CIUS („Core Invoice Usage Specification" pentru România) nu înlocuiește standardul european SR EN 16931-1, ci îl particularizează: stabilește care elemente sunt obligatorii, opționale sau interzise în contextul specific românesc (de exemplu formatul CUI-ului, codurile de TVA, structura adresei).
- Structura facturii electronice trebuie să respecte cumulativ trei niveluri: (a) specificațiile tehnice generale din SR EN 16931-1, (b) specificațiile și regulile operaționale RO_CIUS, și (c) sintaxele identificate în CEN/TS 16931-2, potrivit legii.
- Practic, RO_CIUS e implementat printr-un set de reguli Schematron (validare automată) pe care XML-ul facturii trebuie să le treacă la încărcarea în SPV, înainte ca factura să fie considerată validă și transmisă mai departe.
- O factură poate fi validă din punctul de vedere al software-ului de facturare (XML bine format, câmpuri completate) și totuși respinsă de ANAF pentru că nu respectă o regulă RO_CIUS specifică — de exemplu lipsa unui cod de oraș/sector cerut de particularizarea românească.

## Ce se greșește în practică

- Se presupune că orice generator de XML „compatibil UBL 2.1" produce automat facturi valide pentru RO e-Factura — respectarea UBL 2.1 e necesară, dar nu suficientă, fără particularizarea RO_CIUS.
- Se ignoră erorile de validare Schematron primite de la ANAF, considerându-se „probleme tehnice ale portalului", când de fapt indică o neconformitate reală cu RO_CIUS.
- Se folosește un identificator de standard (CustomizationID) învechit sau greșit în XML, ceea ce face ca factura să fie interpretată după alte reguli decât cele curente.

## Ce face iConta.eu

iConta.eu generează facturile electronice ca XML UBL 2.1, particularizat pentru RO_CIUS (customization ID conform specificației naționale curente), și le transmite/validează prin sistemul RO e-Factura. Structura XML respectă în mod explicit cerințele specifice românești suplimentare față de standardul european de bază — de exemplu, câmpul de oraș cerut de CIUS-RO chiar și când formularul de factură nu îl capturează separat.

[iConta.eu](/)
