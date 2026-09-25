---
title: "e-Factura pentru operațiuni triunghiulare"
description: "De ce o livrare ulterioară efectuată în cadrul unei operațiuni triunghiulare iese, de regulă, din sfera RO e-Factura B2B."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# e-Factura pentru operațiuni triunghiulare

O operațiune triunghiulară implică trei firme din trei state membre diferite: bunurile pleacă direct din primul stat către al treilea, iar firma din mijloc (adesea cea din România) doar facturează, fără ca marfa să atingă vreodată teritoriul românesc. Aceasta schimbă complet analiza privind obligația RO e-Factura, față de o livrare internă obișnuită.

## Temeiul legal

::: ghid-temei
„Operatorii economici - persoane impozabile stabilite în România [...], pentru livrările de bunuri și prestările de servicii care au locul livrării/prestării în România conform art. 275 și art. 278-279 din Legea nr. 227/2015 [...], efectuate în relația B2B [...] au obligația [...] să transmită facturile emise în sistemul național privind factura electronică RO e-Factura [...]"
— Legea 296/2023, art. LIX alin. (1) (sursă: anaf_surse/legea_296_2023_masuri_fiscal_bugetare_asigurarea_sustenabilitatii.txt)
:::

- Criteriul de sferă al obligației RO e-Factura B2B rămâne locul livrării, stabilit conform art. 275 CF — locul unde se găsesc bunurile la momentul începerii transportului.
- Într-o operațiune triunghiulară „clasică" (firma din România cumpără dintr-un stat membru A și revinde către un stat membru C, iar bunurile merg direct din A în C, fără să treacă prin România), locul livrării ulterioare efectuate de firma română nu e în România — deci, prin același criteriu, factura respectivă iese din sfera obligației RO e-Factura B2B.
- Declararea acestei operațiuni ca „livrare triunghiulară" se face totuși în declarația recapitulativă D390, cu cod special **T**, distinct de codul „L" (livrare intracomunitară obișnuită de bunuri).

## Ce se greșește în practică

- Se transmite automat în SPV orice factură emisă de firma română, inclusiv cea aferentă unei livrări triunghiulare, fără să se verifice dacă locul livrării e efectiv în România.
- Se confundă codul „T" din D390 cu o obligație suplimentară de transmitere în e-Factura — cele două declarații (D390 și RO e-Factura) au reguli de sferă separate, iar clasificarea corectă în una nu implică automat vreo cerință în cealaltă.
- Se tratează operațiunea triunghiulară ca pe o livrare intracomunitară obișnuită (cod „L"), fără să se verifice dacă bunurile chiar au tranzitat România — distincția L/T depinde de traseul fizic al mărfii, nu doar de faptul că partenerii sunt din UE.

## Ce face iConta.eu

Pentru declararea D390, iConta.eu nu derivă niciodată automat codul „T" dintr-o factură — orice operațiune triunghiulară trebuie introdusă manual în panoul de clasificare D390 (fie prin reclasificarea unei operațiuni deja derivate ca „L", fie ca linie pur manuală), cu codul partenerului obligatoriu. Modulul de e-Factura al aplicației nu conține nicio ramură specifică operațiunilor triunghiulare — generatorul tratează exclusiv structura tehnică a facturii pentru SPV, fără să distingă o factură de livrare triunghiulară de o factură obișnuită. Verificarea dacă o astfel de factură intră sau nu în sfera obligației RO e-Factura rămâne o decizie a contabilului, pe baza locului efectiv al livrării.

[iConta.eu](/)
