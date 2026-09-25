---
title: "Ce mențiune se trece pe factura de servicii intracomunitare?"
description: "Mențiunea obligatorie pe factura de servicii B2B intracomunitare, atunci când TVA se datorează de beneficiar."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Ce mențiune se trece pe factura de servicii intracomunitare?

Când o firmă din România prestează un serviciu către o firmă dintr-un alt stat membru, iar operațiunea e neimpozabilă în România pentru că locul prestării e la sediul beneficiarului, factura nu iese fără TVA „pur și simplu" — trebuie să poarte o mențiune obligatorie, prevăzută explicit de Codul fiscal, care arată că TVA e datorată de client, nu de furnizor.

## Temeiul legal

::: ghid-temei
„Factura cuprinde în mod obligatoriu următoarele informații: [...] în cazul în care clientul este persoana obligată la plata TVA, mențiunea «taxare inversă»;"
— Codul fiscal (Legea 227/2015), art. 319 alin. (20) lit. m) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

- Pentru un serviciu B2B intracomunitar (locul prestării la sediul beneficiarului, art. 278 alin. (2) CF), beneficiarul din celălalt stat membru e persoana obligată la plata TVA în statul lui — deci factura românească trebuie să poarte mențiunea **„taxare inversă"**.
- Mențiunea e obligatorie ca element de conținut al facturii, alături de celelalte informații standard (numărul, data, datele părților, baza de impozitare, codurile de TVA) — nu e opțională sau la latitudinea furnizorului.
- Condiția pentru ca operațiunea să fie tratată astfel e ca beneficiarul să aibă un cod de TVA valid dintr-un alt stat membru (verificat prin VIES); altfel, operațiunea devine B2C, iar factura se emite cu TVA românesc (art. 278 alin. (3) CF).

## Ce se greșește în practică

- Se emite factura fără TVA, dar fără mențiunea „taxare inversă" — factura devine incompletă din punct de vedere legal, chiar dacă suma de TVA calculată corect ar fi zero.
- Se pune mențiunea „scutit de TVA" în loc de „taxare inversă" — sunt regimuri diferite (scutirea, cu trimitere la articolul aplicabil, e pentru alte tipuri de operațiuni; „taxare inversă" e specifică situației în care obligația de plată trece la client).
- Se aplică mențiunea de taxare inversă fără să se fi verificat întâi codul de TVA al clientului în VIES — dacă acesta nu e valid, operațiunea nu se poate încadra ca B2B intracomunitară scutită, iar factura trebuie să conțină TVA românesc, nu mențiunea de taxare inversă.

## Ce face iConta.eu

Motorul de operațiuni intracomunitare al iConta.eu validează serviciul B2B intracomunitar verificând dacă clientul are un cod de TVA valid în VIES: dacă da, operațiunea e tratată ca neimpozabilă în România, declarabilă în D390 (cod S/P), iar dacă nu, aplicația tratează factura ca B2C, cu TVA românesc, conform art. 278 alin. (3) CF. Pentru achizițiile de servicii intracomunitare primite de o firmă din România, aplicația generează automat formula contabilă de taxare inversă (4426=4427). Aplicația nu a fost confirmată, la nivel de cod verificat pentru acest ghid, ca scriind ea însăși textul mențiunii „taxare inversă" pe PDF-ul facturii de prestare emise către clientul din alt stat membru — contabilul trebuie să se asigure că această mențiune obligatorie apare pe documentul emis, indiferent de ecranul folosit.

[iConta.eu](/)
