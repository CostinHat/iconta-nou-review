---
title: Pot emite e-Factura în euro către un client din România?
description: Legea permite facturarea în orice monedă, inclusiv între două firme din România, dar suma TVA trebuie să apară obligatoriu în lei pe factură. Explicăm regula și cum gestionează iConta.eu conversia.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Pot emite e-Factura în euro către un client din România?

Da, puteți emite factura (și, implicit, e-Factura transmisă prin RO e-Factura) exprimată în euro către un client din România — legea nu interzice facturarea în valută între două firme românești. Există însă o cerință obligatorie care nu depinde de moneda aleasă: **suma TVA trebuie să apară în lei** pe factură.

## Temeiul legal

::: ghid-temei
Factura cuprinde în mod obligatoriu următoarele informații: [...] j) indicarea cotei de taxă aplicate și a sumei taxei colectate, exprimate în lei, în funcție de cotele taxei;

— Codul fiscal (Legea 227/2015), art.319 alin.(20) lit.j)
:::

::: ghid-temei
Dacă elementele folosite pentru stabilirea bazei de impozitare a unei operațiuni, alta decât importul de bunuri, se exprimă în valută, cursul de schimb care se aplică este ultimul curs de schimb comunicat de Banca Națională a României sau ultimul curs de schimb publicat de Banca Centrală Europeană ori cursul de schimb utilizat de banca prin care se efectuează decontările, valabil la data la care intervine exigibilitatea taxei pentru operațiunea în cauză [...]

— Codul fiscal (Legea 227/2015), art.290 alin.(2)
:::

Legea nu impune ca factura să fie emisă în lei — prețul, baza de impozitare și totalul pot fi exprimate în orice monedă convenită între părți, inclusiv euro, chiar și când ambele firme sunt din România. Singura cerință specifică de monedă e cea de la art.319 alin.(20) lit.j): suma TVA colectată trebuie indicată **în lei**, indiferent de moneda restului facturii, la cursul de schimb stabilit conform art.290 alin.(2) (cursul BNR, sau, după caz, cel al băncii prin care se face decontarea, valabil la data exigibilității taxei).

## Ce se greșește în practică

- Se emite factura integral în euro, inclusiv suma TVA, fără conversia obligatorie a taxei în lei — factura nu îndeplinește cerința art.319 alin.(20) lit.j).
- Se folosește un curs de schimb ales arbitrar (ex. cursul zilei plății) în loc de cursul valabil la data exigibilității taxei, conform art.290 alin.(2).
- Se presupune că, fiind vorba de o factură în valută, operațiunea ar fi automat scutită sau supusă altui regim de TVA — moneda facturii nu are nicio legătură cu regimul de TVA aplicabil unei operațiuni interne.

## Ce face iConta.eu

Facturile pot fi emise în orice monedă, inclusiv euro, către orice client — inclusiv unul din România. La crearea facturii, aplicația reține moneda aleasă și calculează automat echivalentul în lei (total și TVA), fie pe baza cursului introdus explicit, fie, dacă nu e furnizat, printr-o încercare automată de preluare a cursului BNR pentru data facturii; dacă niciun curs nu e disponibil, conversia rămâne necompletată și semnalată, nu ghicită cu o valoare implicită.

De reținut onest, verificat direct în codul care generează fișierul XML pentru RO e-Factura: suma de TVA din XML apare exprimată în moneda facturii (ex. euro), fără un bloc separat, explicit, cu suma TVA convertită în lei alături. Conversia în lei există și e corectă la nivelul înregistrării contabile interne (nota contabilă, evidența facturii), dar dacă emiteți facturi în valută către clienți din România și le transmiteți prin RO e-Factura, verificați manual că suma de TVA afișată corespunde cerinței legale de a fi exprimată în lei, înainte de a considera obligația de conținut a facturii îndeplinită integral.

[iConta.eu](/)
