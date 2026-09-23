---
title: Cum se emit facturi pentru vânzările B2C online
description: O factură către un client persoană fizică se contabilizează la fel ca orice altă factură emisă — clientul debitat cu totalul, venitul și TVA creditate separat — cu condiția ca firma să fie deja înregistrată în scopuri de TVA la data emiterii, dacă factura include TVA.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum se emit facturi pentru vânzările B2C online

Din punct de vedere al contării, o factură emisă către un consumator persoană fizică (B2C) urmează exact același mecanism ca oricare altă factură emisă — nu există un tratament contabil separat pentru vânzările către persoane fizice.

## Temeiul legal

::: ghid-temei
**Codul fiscal, art. 316 alin. (1^1)**: înregistrarea în scopuri de TVA se consideră valabilă începând cu data înregistrării fiscale, cu data depășirii plafonului de scutire, cu data solicitării sau, după caz, cu „a 5-a zi următoare" solicitării — în funcție de motivul concret al înregistrării.
:::

Mecanismul contabil pentru o factură emisă, indiferent de tipul clientului: contul de clienți (4111) se debitează cu suma totală a facturii; contul de venit corespunzător (701 mărfuri, 703/704/707 servicii sau producție, după natura vânzării) se creditează cu baza; TVA colectată se creditează separat, în 4427 sau, dacă firma aplică TVA la încasare, în 4428, urmând să treacă în 4427 la momentul încasării efective.

Condiția pentru ca factura să conțină TVA rămâne aceeași ca la orice altă vânzare: firma trebuie să fie deja înregistrată în scopuri de TVA la data emiterii, conform art. 316 alin. (1^1) — data exactă depinde de motivul înregistrării (obligatorie prin depășire de plafon, prin opțiune, sau odată cu înmatricularea).

## Ce se greșește în practică

- Se presupune că vânzările online către persoane fizice au un regim de TVA sau de contare diferit de restul facturilor emise — nu e cazul, mecanismul contabil e identic.
- Se emit facturi cu TVA fără verificarea prealabilă a datei de la care înregistrarea de TVA a firmei e efectiv valabilă.
- Se aplică o cotă de TVA greșită pe linii cu produse la cote reduse (de exemplu cărți, anumite alimente), din grabă la introducerea facturii, fără o verificare separată a cotei corecte per produs.

## Ce face iConta.eu

Motorul de contare al iConta.eu tratează orice factură emisă, B2C sau B2B, identic: clientul debitat cu totalul, venitul creditat cu baza, TVA colectată creditată separat (4427 sau 4428, după opțiunea de TVA la încasare), pe fiecare cotă introdusă pe liniile facturii.

Aplicația nu verifică automat, la contarea facturii, dacă firma e efectiv înregistrată în scopuri de TVA la data emiterii — corectitudinea cotelor introduse pe fiecare linie a facturii, inclusiv pentru cotele reduse, rămâne o verificare pe care o face contabilul.

[iConta.eu](/)
