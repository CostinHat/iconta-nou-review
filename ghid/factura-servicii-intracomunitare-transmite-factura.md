---
title: "Factura pentru servicii intracomunitare se transmite în e-Factura?"
description: "De ce facturile de servicii B2B intracomunitare, cu locul prestării în alt stat membru, ies în afara sferei obligației RO e-Factura."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Factura pentru servicii intracomunitare se transmite în e-Factura?

Obligativitatea RO e-Factura pentru relația B2B nu se aplică tuturor facturilor emise de o firmă din România — se aplică doar celor pentru care locul livrării/prestării e în România, conform regulilor Codului fiscal. Pentru serviciile B2B intracomunitare, unde locul prestării e la sediul beneficiarului din alt stat membru, criteriul de sferă nu e îndeplinit.

## Temeiul legal

::: ghid-temei
„Operatorii economici - persoane impozabile stabilite în România [...], pentru livrările de bunuri și prestările de servicii care au locul livrării/prestării în România conform art. 275 și art. 278-279 din Legea nr. 227/2015 [...], efectuate în relația B2B [...] au obligația [...] să transmită facturile emise în sistemul național privind factura electronică RO e-Factura [...]"
— Legea 296/2023, art. LIX alin. (1) (sursă: anaf_surse/legea_296_2023_masuri_fiscal_bugetare_asigurarea_sustenabilitatii.txt)
:::

- Criteriul care decide sfera obligației RO e-Factura B2B e **locul livrării/prestării în România**, stabilit conform art. 275 (bunuri) și art. 278-279 (servicii) din Codul fiscal — nu simplul fapt că furnizorul e stabilit în România.
- Pentru un serviciu B2B intracomunitar (art. 278 alin. (2) CF), locul prestării e la sediul beneficiarului din alt stat membru — deci operațiunea nu are locul prestării în România, iar acest criteriu de sferă nu e îndeplinit.
- Acest text a fost introdus pentru perioada 1 ianuarie–30 iunie 2024, dar criteriul de sferă (locul livrării/prestării în România, conform art. 275 și 278-279 CF) e cel folosit consecvent și în textele ulterioare care extind obligativitatea B2B; el rămâne testul de aplicat pentru a stabili dacă o operațiune intră sau nu în domeniul RO e-Factura.

## Ce se greșește în practică

- Se presupune că orice factură emisă de o firmă românească trebuie transmisă în RO e-Factura, indiferent de unde e locul prestării — criteriul relevant e locul operațiunii, nu naționalitatea furnizorului.
- Se confundă „serviciu prestat de o firmă din România" cu „operațiune cu locul prestării în România" — pentru serviciile B2B intracomunitare, cele două nu coincid.
- Se transmite eronat în SPV o factură de serviciu intracomunitar doar din prudență, fără să se verifice dacă operațiunea intră efectiv în sfera obligației — ceea ce nu e interzis, dar nu e nici cerut de lege pentru acest tip de operațiune.

## Ce face iConta.eu

Modulul de e-Factura al iConta.eu (transmiterea automată a facturilor emise în SPV) nu conține nicio ramură de cod specifică operațiunilor intracomunitare — generatorul de facturi electronice tratează exclusiv structura tehnică UBL/CIUS-RO pentru SPV, fără să distingă separat o factură de servicii intracomunitare de o factură obișnuită. Această absență e, de fapt, consecventă cu regula legală: din moment ce o astfel de operațiune are locul prestării în alt stat membru, ea iese oricum din sfera RO e-Factura B2B, deci nu are nevoie de un tratament special în modulul de transmitere. Rămâne responsabilitatea contabilului să nu includă în fluxul de transmitere SPV facturi de servicii intracomunitare care nu intră, prin natura lor, în domeniul de aplicare al obligației.

[iConta.eu](/)
