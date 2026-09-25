---
title: "Cum tratez o comandă WooCommerce anulată după facturare?"
description: "O comandă anulată după ce factura a fost deja emisă și transmisă nu se rezolvă prin ștergere, ci prin factură de stornare — corectarea e o operațiune manuală, generică, aceeași indiferent de sursa facturii."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum tratez o comandă WooCommerce anulată după facturare?

Când o comandă e anulată în magazinul online după ce a fost deja transformată în factură, problema nu mai ține de sincronizarea cu magazinul, ci de regula generală de corectare a facturilor: o factură emisă nu se șterge, se stornează.

## Temeiul legal

::: ghid-temei
„Corectarea informațiilor înscrise în facturi [...] se efectuează astfel: a) în cazul în care factura nu a fost transmisă către beneficiar, aceasta se anulează și se emite o nouă factură; [...] b) în cazul în care factura a fost transmisă beneficiarului, fie se emite o nouă factură care trebuie să cuprindă [...] valorile cu semnul minus [...], iar, pe de altă parte, informațiile și valorile corecte, fie se emite o nouă factură conținând informațiile și valorile corecte și concomitent se emite o factură cu valorile cu semnul minus [...], în care se înscriu numărul și data facturii corectate."
— Codul fiscal (Legea nr. 227/2015), art. 330 alin. (1) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

- Regula depinde de un singur criteriu: dacă factura a ajuns sau nu la cumpărător (a fost transmisă). O comandă WooCommerce anulată după ce factura a fost deja emisă și trimisă cade aproape întotdeauna în situația de la lit. b) — trebuie stornată, nu ștearsă.
- Stornarea nu e o simplă „anulare" în evidența internă — ea produce efecte fiscale în perioada în care se emite, nu în perioada facturii inițiale, și trebuie declarată corespunzător (decont de TVA, declarații informative, e-Factura, dacă factura inițială a fost transmisă acolo).
- Motivul corecției trebuie documentat — pentru un retur sau o anulare de comandă, dovada e utilă la un eventual control (comunicare cu clientul, confirmare de anulare din platforma magazinului).

## Ce se greșește în practică

- Se șterge sau se editează direct factura deja emisă, ca și cum comanda n-ar fi existat — dacă factura a fost deja transmisă cumpărătorului sau la e-Factura, acest lucru nu mai e permis legal.
- Se așteaptă ca sistemul de facturare conectat la magazinul online să detecteze singur schimbarea de status a comenzii (din „finalizată" în „anulată") și să stornize automat — de regulă, un conector care doar importă comenzi noi nu urmărește ce se întâmplă ulterior cu o comandă deja transformată în factură.
- Se ignoră partea de TVA: dacă factura inițială a generat TVA colectată deja raportată, stornarea trebuie reflectată în perioada curentă, nu prin refacerea declarației vechi.

## Ce face iConta.eu

Conectorul WooCommerce din iConta.eu **nu are niciun mecanism de reconciliere sau stornare automată** pentru o comandă anulată după facturare — verificat direct în cod, modulul conectorului nu conține nicio logică legată de anulare sau stornare. Odată ce o comandă a fost importată și transformată în factură, ea e marcată ca „deja importată" și e ignorată definitiv la orice sincronizare ulterioară, indiferent ce se întâmplă cu ea în magazinul online — inclusiv dacă între timp e anulată sau rambursată acolo.

Practic, dacă o comandă WooCommerce e anulată după ce factura a fost deja emisă, corectarea rămâne o operațiune manuală, făcută exact ca pentru orice altă factură din aplicație, conform regulii de la art. 330 de mai sus — conectorul nu detectează și nu semnalează singur aceste cazuri.

[iConta.eu](/)
