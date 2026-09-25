---
title: "Cum corectez o factură dintr-o lună anterioară în e-Factura?"
description: "Mecanismul legal de corectare a facturilor deja transmise prin e-Factura și limita actuală a acestei funcționalități în iConta.eu."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum corectez o factură dintr-o lună anterioară în e-Factura?

O eroare descoperită într-o factură deja transmisă printr-o lună fiscală închisă nu se rezolvă prin editarea facturii vechi — Codul fiscal impune un mecanism specific de corectare, prin emiterea unei facturi noi care face trimitere explicită la cea greșită.

## Temeiul legal

::: ghid-temei
„Corectarea informațiilor înscrise în facturi sau în alte documente care țin loc de factură se efectuează astfel: [...] b) în cazul în care factura a fost transmisă beneficiarului, fie se emite o nouă factură care trebuie să cuprindă, pe de o parte, informațiile din factura inițială, numărul și data facturii corectate, valorile cu semnul minus sau, după caz, o mențiune din care să rezulte că valorile respective sunt negative, iar, pe de altă parte, informațiile și valorile corecte, fie se emite o nouă factură conținând informațiile și valorile corecte și concomitent se emite o factură cu valorile cu semnul minus [...], în care se înscriu numărul și data facturii corectate."
— Legea 227/2015 (Codul fiscal), art. 330 alin. (1) lit. b) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Practic, există două variante permise de lege pentru factura deja transmisă:

- **O singură factură "mixtă"** — conține referința la factura greșită (număr, dată), anulează valorile ei (cu minus sau mențiune explicită) și, în același document, înscrie valorile corecte.
- **Două facturi separate** — una de stornare (cu valorile facturii greșite, cu minus) și una nouă, cu valorile corecte.

Ambele variante se transmit prin SPV/e-Factura ca facturi noi, cu data curentă, chiar dacă factura greșită aparține unei luni anterioare — corectarea nu presupune "redeschiderea" perioadei fiscale vechi, ci înregistrarea efectului corecției în luna curentă.

## Ce se greșește în practică

- Se încearcă modificarea facturii XML deja transmise în SPV — sistemul e-Factura nu permite editarea unei facturi validate; singura cale e emiterea unei facturi de corecție, conform art. 330.
- Se omite trimiterea explicită (număr și dată) la factura corectată în noua factură, ceea ce face dificilă urmărirea perechii factură greșită/factură de corecție la un control.
- Se înregistrează corecția doar în contabilitate, fără transmiterea facturii de corecție prin SPV, deși obligația de raportare prin e-Factura se aplică și facturilor de stornare/corecție.

## Ce face iConta.eu

La data acestui ghid, iConta.eu generează și trimite facturi prin e-Factura, dar **stornarea/nota de credit pentru facturi deja transmise nu este încă implementată** — codul aplicației marchează explicit acest flux ca netratat în versiunea curentă, urmând să fie adăugat după testare pe mediul de test ANAF. Corectarea unei facturi dintr-o lună anterioară trebuie, la data acestui ghid, gestionată manual, prin emiterea facturii de corecție conform art. 330 și transmiterea ei separată prin portalul SPV sau printr-un alt mijloc suportat, până la finalizarea acestei funcționalități în aplicație.

[iConta.eu](/)
