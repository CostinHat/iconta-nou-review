---
title: "Cum se facturează serviciile IT către clienți din România?"
description: "Regulile de conținut al facturii pentru servicii IT prestate către alți operatori economici din România și obligația de transmitere prin sistemul RO e-Factura."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se facturează serviciile IT către clienți din România?

Facturarea unor servicii IT (dezvoltare software, mentenanță, consultanță tehnică) către un client din România, între doi operatori economici, e o operațiune obișnuită de TVA la nivel intern — locul prestării e România, se aplică TVA cu cota standard, iar de câțiva ani se adaugă și obligația de transmitere a facturii prin sistemul național RO e-Factura.

## Temeiul legal

::: ghid-temei
„În relația comercială B2B, între persoane impozabile stabilite în România conform art. 266 alin. (2) din Legea nr. 227/2015, cu modificările și completările ulterioare, emitentul facturii electronice are obligația de transmitere a acesteia către destinatar utilizând sistemul național privind factura electronică RO e-Factura, cu respectarea prevederilor art. 4 alin. (1). Fac excepție facturile simplificate emise conform art. 319 alin. (12) din Legea nr. 227/2015, cu modificările și completările ulterioare."
— Ordonanța de urgență nr. 120/2021, art. 10 alin. (1) (formă în vigoare de la 01.07.2024, astfel cum a fost modificat prin Legea nr. 296/2023, art. LXV pct. 4, și prin OUG nr. 115/2023) (sursă: anaf_surse/legea_296_2023_masuri_fiscal_bugetare_asigurarea_sustenabilitatii.txt)
:::

Ce înseamnă asta pentru o firmă de IT:

- Prestarea de servicii IT către un client persoană juridică din România intră în definiția „relației B2B" de la OUG 120/2021 — factura trebuie transmisă prin sistemul RO e-Factura, indiferent dacă clientul e sau nu înregistrat activ în registrul RO e-Factura.
- Structura facturii electronice trebuie să respecte standardul european SR EN 16931-1 și specificațiile naționale RO_CIUS, nu doar formatul liber PDF — elementele obligatorii includ identificarea părților, data, poziții de pe factură, defalcarea TVA și totalul facturii.
- Persoana impozabilă trebuie să emită factură către fiecare beneficiar la prestarea de servicii, conform regulilor generale de facturare din Codul fiscal (art. 319) — termenul de emitere, momentul exigibilității TVA și conținutul obligatoriu rămân cele generale, la care se adaugă obligația de transmitere electronică.
- Factura primită de destinatar fără respectarea acestor prevederi (adică transmisă în afara sistemului RO e-Factura, când era obligatoriu) poate atrage sancțiuni atât pentru emitent, cât și pentru beneficiar, conform legislației aplicabile RO e-Factura.

## Ce se greșește în practică

- Se emite factura pentru servicii IT către un client din România direct pe PDF/email, fără transmitere prin sistemul RO e-Factura, presupunând că obligația privește doar produsele fizice sau doar firmele mari.
- Se ignoră structura tehnică standardizată (SR EN 16931-1 / RO_CIUS) și se generează un XML necorespunzător, care e respins de sistem — factura „transmisă" nu contează ca depusă corect până nu primește semnătura electronică a Ministerului Finanțelor.
- Se confundă momentul emiterii facturii cu momentul acceptării ei în sistem — o factură cu erori de structură primește mesaj de eroare și trebuie corectată și retransmisă, nu rămâne valabilă „așa cum a fost trimisă prima dată".

## Ce face iConta.eu

iConta.eu emite facturi de servicii și le transmite prin conectorul e-Factura direct către sistemul RO e-Factura, cu formatul XML structurat cerut de standard — funcționalitate reală, testată în aplicație (module dedicate de trimitere, import și reconciliere a statusului facturilor). Ce rămâne responsabilitatea utilizatorului este conținutul comercial al facturii (descrierea serviciului, prețul, cota de TVA aplicabilă) — aplicația nu evaluează dacă serviciul prestat justifică o anumită cotă de TVA sau o scutire, ci reflectă exact ce introduce contabilul.

[iConta.eu](/)
