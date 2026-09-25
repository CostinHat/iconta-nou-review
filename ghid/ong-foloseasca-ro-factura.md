---
title: "Un ONG trebuie să folosească RO e-Factura?"
description: "Obligația RO e-Factura depinde de calitatea de persoană impozabilă stabilită în România, nu de forma juridică — un ONG cu activitate economică B2B intră sub aceeași obligație ca orice altă entitate."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Un ONG trebuie să folosească RO e-Factura?

Legea RO e-Factura nu face nicio excepție pe forma juridică a emitentului. Ce contează e dacă entitatea are calitatea de „persoană impozabilă stabilită în România" pentru operațiunea respectivă — o calitate care ține de faptul că desfășoară o activitate economică, nu de statutul de organizație nonprofit.

## Temeiul legal

::: ghid-temei
„(1) În relația comercială B2B, între persoane impozabile stabilite în România conform art. 266 alin. (2) din Legea nr. 227/2015, cu modificările și completările ulterioare, emitentul facturii electronice are obligația de transmitere a acesteia către destinatar utilizând sistemul național privind factura electronică RO e-Factura, cu respectarea prevederilor art. 4 alin. (1). Fac excepție facturile simplificate emise conform art. 319 alin. (12) din Legea nr. 227/2015, cu modificările și completările ulterioare."
— art. 10 alin. (1) din OUG 120/2021, astfel cum a fost modificat prin Legea 296/2023 (sursă: anaf_surse/legea_296_2023_masuri_fiscal_bugetare_asigurarea_sustenabilitatii.txt)
:::

- Obligația de transmitere prin RO e-Factura privește relația **B2B**, între „persoane impozabile stabilite în România" — indiferent dacă sunt sau nu înregistrate în scopuri de TVA.
- „Persoană impozabilă" e, potrivit Codului fiscal, orice entitate care desfășoară de o manieră independentă o activitate economică — deci un ONG devine „persoană impozabilă" **pentru operațiunile din activitatea sa economică** (vânzări, servicii, chirii facturate), nu pentru operațiunile din sfera statutară (cotizații, donații), pentru care oricum nu se emite factură comercială.
- Nu există în lege nicio excepție dedicată organizațiilor nonprofit de la obligația RO e-Factura — dacă emit facturi B2B pentru activitatea economică, intră sub aceeași obligație ca orice societate comercială.

## Ce se greșește în practică

- Se presupune că un ONG e scutit de RO e-Factura pentru simplul motiv că nu e o societate comercială — obligația nu ține de forma juridică, ci de faptul că emite facturi B2B pentru activitate economică.
- Se emit facturi „pe hârtie" sau prin alte canale pentru vânzări/servicii ale activității economice a ONG-ului, fără transmitere prin sistemul RO e-Factura, considerându-se greșit că doar „firmele" au această obligație.
- Se confundă operațiunile din sfera economică (facturate, supuse RO e-Factura) cu cele din sfera fără scop patrimonial (cotizații, donații), pentru care nu se emit facturi comerciale și deci nu se pune problema RO e-Factura.

## Ce face iConta.eu

Funcționalitatea de contabilitate ONG din iConta.eu (`core/ong.py`) nu emite facturi și nu are nicio legătură cu modulul de facturare sau cu RO e-Factura al aplicației — se ocupă exclusiv de înregistrarea veniturilor fără scop patrimonial pe conturile din grupa 73 și de calculul scutirii de impozit pe profit pentru veniturile economice, potrivit art. 15 Cod fiscal. Dacă ONG-ul desfășoară activitate economică și emite facturi, acestea se gestionează prin modulele generale de facturare ale iConta.eu, la fel ca la orice altă entitate — subiectul RO e-Factura nu ține de această funcționalitate dedicată contabilității ONG.

[iConta.eu](/)
