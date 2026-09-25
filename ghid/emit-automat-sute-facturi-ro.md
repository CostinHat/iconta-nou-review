---
title: "Cum emit automat sute de facturi în RO e-Factura?"
description: "Ce înseamnă, legal, ca o factură să existe 'în RO e-Factura', și de ce emiterea automată în masă a facturilor nu înseamnă automat și transmiterea lor la SPV."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum emit automat sute de facturi în RO e-Factura?

Pentru un contabil cu multe facturi recurente lunare, întrebarea reală e dublă: pot fi emise automat sute de facturi dintr-un lot de șabloane, și ajung ele, tot automat, „în RO e-Factura"? Răspunsul e diferit pentru fiecare jumătate, iar diferența contează legal, nu doar tehnic.

## Temeiul legal

::: ghid-temei
„Prin excepție de la prevederile alin. (1), pentru operațiunile realizate între persoane impozabile stabilite în România conform art. 266 alin. (2), sunt considerate facturi numai facturile care îndeplinesc condițiile prevăzute de Ordonanța de urgență a Guvernului nr. 120/2021 privind administrarea, funcționarea și implementarea sistemului național privind factura electronică RO e-Factura [...]"
— Cod fiscal (Legea 227/2015), art. 319 alin. (1^1) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

- „A fi în RO e-Factura" nu e o formulare colocvială — e statutul legal al facturii pentru operațiuni B2B între persoane impozabile din România: fără transmiterea prin sistemul național, documentul nu e considerat factură validă în acest regim.
- Volumul (o factură sau sute) nu schimbă regula — fiecare document, individual, trebuie să treacă prin fluxul de validare/transmitere pentru a avea acest statut.
- Excepția a intrat în vigoare 01-07-2024, prin Legea 296/2023, deci se aplică integral operațiunilor curente.

## Ce se greșește în practică

- Se presupune că un job automat care „emite" facturi le și trimite automat la ANAF — fără să se verifice ce înseamnă efectiv „emitere" în acel sistem.
- Se lasă sute de facturi acumulate cu statusul „de trimis", nedescoperit decât la o verificare ulterioară sau la un control.
- Se caută în aplicație o singură acțiune „emite + trimite SPV pentru tot lotul", presupunând că există, fără să se verifice ce face de fapt mecanismul de facturare recurentă.

## Ce face iConta.eu

Emiterea în masă chiar există: modulul Facturi recurente procesează, într-o rulare zilnică, toate șabloanele active scadente dintr-un tenant, fiecare izolat (dacă un șablon eșuează, celelalte se emit oricum) — deci „sute de facturi" emise automat, dacă există sute de șabloane active, e realist. Ce **nu există** e transmiterea automată „în RO e-Factura": fiecare factură emisă astfel primește statusul „de preluat" și rămâne așa până la un pas separat, manual, per factură — un buton dedicat de trimitere la SPV, apăsat individual din ecranul de facturi. Nu există în acest modul niciun apel automat către sistemul RO e-Factura. Pentru sute de facturi, asta înseamnă sute de acțiuni manuale de trimitere, nu una automată pentru tot lotul.

[iConta.eu](/)
