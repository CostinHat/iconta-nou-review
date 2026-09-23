---
title: "e-Factura pentru facturarea în valută"
description: Factura electronică transmisă prin RO e-Factura poartă codul monedei facturii (de exemplu EUR), dar structura standard nu include cursul BNR sau un total de TVA convertit în lei — cursul folosit rămâne vizibil doar pe documentul local, nu în fișierul trimis către SPV.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# e-Factura pentru facturarea în valută

O factură emisă în valută (EUR, USD etc.) poate fi transmisă prin sistemul RO e-Factura la fel ca una în lei — structura standard a facturii electronice permite specificarea monedei documentului. Ce nu conține însă fișierul XML trimis către ANAF e cursul de schimb folosit pentru TVA: acela rămâne o informație de evidență internă, nu parte din structura obligatorie a facturii electronice.

## Temeiul legal

::: ghid-temei
„Structura facturii electronice respectă: a) specificațiile tehnice și de utilizare a elementelor de bază ale facturii electronice așa cum sunt prevăzute în standardul european SR EN 16931-1, care sunt aplicabile la nivel național; b) specificațiile tehnice și de utilizare a elementelor de bază ale facturii electronice - RO_CIUS - și regulile operaționale specifice aplicabile la nivel național." — OUG 120/2021, art. 4 alin. (1).
:::

## Ce apare și ce nu apare în fișierul transmis

Factura electronică generată pentru RO e-Factura scrie codul monedei documentului (de exemplu, EUR) și toate sumele — bază de impozitare, TVA, total — exprimate în acea monedă, conform standardului SR EN 16931-1/RO_CIUS. Structura standard **nu prevede** un câmp separat pentru cursul de schimb folosit la calculul TVA, nici un total de TVA convertit în lei alături de cel în valută.

Cursul BNR folosit efectiv la emiterea facturii (conform art. 290 CF) rămâne o informație păstrată la nivelul documentului local al emitentului — apare pe PDF-ul facturii (sursa cursului, valoarea lui și data), dar nu ajunge în fișierul XML transmis prin sistemul național.

## Ce se greșește în practică

- Se presupune că, odată transmisă prin e-Factura, ANAF are automat acces la cursul folosit și la baza de calcul convertită în lei — informația transmisă e doar în moneda facturii, conversia rămâne la nivel de evidență proprie a firmei.
- Se omite păstrarea dovezii cursului folosit (PDF-ul facturii, nota internă) considerând că fișierul trimis prin SPV e suficient ca justificare a cursului aplicat TVA.
- Se confundă codul monedei documentului (care apare corect în XML) cu o conversie automată în lei făcută de sistemul e-Factura — sistemul nu face această conversie, doar transmite factura în moneda ei originală.

## Ce face iConta.eu

Generatorul XML pentru RO e-Factura (`core/efactura_send.py`) scrie codul monedei facturii și toate sumele în acea monedă, conform standardului UBL 2.1/CIUS-RO — dar nu scrie cursul BNR folosit și nici un total de TVA convertit în lei în fișierul transmis prin SPV, deși câmpul de curs există pe factură la nivel intern. Cursul rămâne vizibil pe PDF-ul facturii (sursă, valoare, dată) și e folosit intern pentru celelalte declarații (D300, D390, D394, D406), dar nu ajunge în XML-ul e-Factura. La primirea unei facturi în valută prin e-Factura, aplicația citește codul monedei documentului, nu extrage însă vreo informație de curs de schimb din fișierul primit — cursul se atribuie ulterior, prin fluxul normal de introducere a facturii.

[iConta.eu](/)
