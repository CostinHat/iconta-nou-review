---
title: "Factura emisă unei firme străine cu sediu în România se transmite în e-Factura?"
description: "Când o companie străină cu sediu sau punct de lucru în România e considerată «stabilită în România» și, deci, intră sub obligația RO e-Factura pentru operațiuni B2B."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Factura emisă unei firme străine cu sediu în România se transmite în e-Factura?

Naționalitatea firmei-client nu contează pentru obligația de e-Factura — contează unde are „sediul" în sensul TVA. O firmă înregistrată în altă țară, dar cu sediu de activitate economică sau sediu fix în România, e tratată exact ca o firmă românească.

## Temeiul legal

::: ghid-temei
„O persoană impozabilă care are sediul activității economice în România este considerată a fi stabilită în România; [...] o persoană impozabilă care are sediul activității economice în afara României se consideră că este stabilită în România dacă are un sediu fix în România, respectiv dacă dispune în România de suficiente resurse tehnice și umane pentru a efectua regulat livrări de bunuri și/sau prestări de servicii impozabile."
— Cod fiscal (Legea 227/2015), art. 266 alin. (2) lit. a) și b) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Ce rezultă pentru factura către o firmă străină cu sediu în România:

- **Definiția „stabilit în România" nu ține de naționalitatea firmei**, ci de existența unui sediu al activității economice sau a unui sediu fix (resurse tehnice și umane suficiente pentru operațiuni regulate) pe teritoriul României — art. 266 alin. (2) CF.
- **Obligația RO e-Factura pentru operațiuni B2B** se aplică „operatorilor economici — persoane impozabile stabilite în România conform art. 266 alin. (2) din [Codul fiscal], indiferent dacă sunt sau nu înregistrați în scopuri de TVA [...], pentru livrările de bunuri și prestările de servicii care au locul livrării/prestării în România" (Legea 296/2023, art. LIX alin. (1)).
- **Concluzie**: dacă firma-client străină are sediu sau punct de lucru (sediu fix) în România, e considerată stabilită în România — deci o factură emisă către ea, pentru o operațiune cu locul livrării/prestării în România, în relație B2B, intră sub obligația RO e-Factura, exact ca la orice client român.
- Regula e diferită dacă firma străină **nu** are niciun sediu în România, ci doar un cod de TVA de nerezident: atunci nu e „stabilită", ci cel mult „înregistrată în scopuri de TVA" — o categorie tratată separat de lege pentru RO e-Factura.

## Ce se greșește în practică

- Se presupune, din simplul fapt că firma-client e înregistrată în altă țară, că factura nu intră sub obligația RO e-Factura — greșit dacă firma are sediu în România.
- Se confundă „sediul social declarat la Registrul Comerțului din altă țară" cu absența oricărui sediu fiscal în România — o firmă poate fi înmatriculată în străinătate și, în același timp, să aibă un sediu fix în România, prin resurse tehnice și umane suficiente pentru operațiuni regulate.
- Se aplică regula B2G (relația cu instituții publice) sau regula pentru nerezidenți fără sediu, deși situația concretă e o relație B2B cu o firmă stabilită în România.

## Ce face iConta.eu

Subiectul nu ține de funcționalitatea **Link de plată pe factură** — aceasta e o cale de plată online (link Stripe/Netopia), complet închisă în aplicație la acest moment (decizie de produs din 06.09.2026: fluxul real de încasare e transferul bancar, confirmat din extras). N-are legătură cu transmiterea facturii în e-Factura.

Mecanismul de transmitere efectivă în RO e-Factura ține de alte funcționalități din aplicație (importul/trimiterea de facturi electronice către SPV). Verificarea dacă o factură concretă trebuie sau nu transmisă rămâne, pe cazul specific al unei firme străine cu sediu în România, o evaluare pe care contabilul o face pe baza criteriilor de mai sus (sediu/sediu fix, locul livrării) — aplicația nu clasifică automat firma-client drept „stabilită" sau „nestabilită" în România pe baza acestor criterii.

[iConta.eu](/)
