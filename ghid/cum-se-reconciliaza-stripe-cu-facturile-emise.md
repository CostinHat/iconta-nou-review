---
title: Cum se reconciliază Stripe cu facturile emise?
description: Legea cere document justificativ pentru fiecare operațiune; un payout Stripe e un transfer agregat, fără CUI-ul fiecărui client plătitor, așa că matching-ul automat pe factură nu se poate face pentru aceste linii — cad sistematic pe status roșu.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Cum se reconciliază Stripe cu facturile emise?

Firmele care încasează prin Stripe primesc în extrasul bancar nu plăți individuale de la fiecare client, ci un payout periodic agregat — o singură sumă netă, care cumulează mai multe tranzacții și scade comisioanele Stripe. Această structură are un efect direct asupra motorului de matching din F073.

## Temeiul legal

::: ghid-temei
**Articolul 6 (1)** Orice operațiune economico-financiară efectuată se consemnează în momentul efectuării ei într-un document care stă la baza înregistrărilor în contabilitate, dobândind astfel calitatea de document justificativ. **(2)** Documentele justificative care stau la baza înregistrărilor în contabilitate angajează răspunderea persoanelor care le-au întocmit, vizat și aprobat, precum și a celor care le-au înregistrat în contabilitate, după caz.
:::

## De ce payout-ul Stripe cade pe roșu

Motorul de matching caută facturi deschise ale unui partener pe baza CUI-ului extras din descrierea liniei bancare. Un payout Stripe apare în extras cu textul agregatorului (de exemplu "STRIPE PAYOUT"), nu cu CUI-ul fiecărui client final ale cărui plăți individuale compun acea sumă. Fără CUI detectat, linia primește automat status roșu, motiv "fără CUI în descriere" — indiferent de câte facturi individuale sunt de fapt acoperite de acel payout.

Trebuie spus clar, ca să nu se creeze o așteptare greșită: motorul de matching din F073 nu are un mecanism de "matching pe lot" care să lege un singur payout de N facturi individuale. Pentru a identifica exact ce facturi acoperă un payout, e nevoie de raportul de settlement al Stripe (disponibil în dashboard-ul Stripe, în afara ariei `core/reconciliere.py`), urmat de alocare manuală în iConta.eu.

## Ce se greșește în practică

- Se așteaptă ca sistemul să identifice automat clienții din spatele unui payout Stripe — motorul nu are acces la detaliile tranzacțiilor individuale procesate de Stripe, doar la suma și descrierea liniei bancare.
- Se contabilizează suma netă a payout-ului direct ca încasare pe o singură factură, fără separarea comisionului Stripe reținut ca cheltuială distinctă.
- Se lasă liniile de payout Stripe necontate pe termen lung, considerându-se eronat că matching-ul se va rezolva automat mai târziu.
- Se ignoră decalajul temporal dintre data facturii (emisă la livrare/prestare) și data payout-ului (de regulă câteva zile mai târziu, cumulat pe o perioadă) la momentul confirmării alocării.

## Ce face iConta.eu

Motorul de matching (`core/reconciliere.py`) cere un CUI identificat în descrierea fiecărei linii de extras înainte de a căuta facturi deschise ale partenerului. Liniile de payout Stripe, fără CUI individual, primesc automat status roșu. Pentru aceste linii, sistemul poate propune o sugestie de cont pe baza istoricului deja contat de utilizator (`core.ai_incredere.sugestie`) — fără nicio bază legală atribuită, doar confort de utilizare.

Alocarea sumei payout-ului pe facturile individuale rămâne un pas manual, prin parametrul `alocari` la contare, pe baza raportului de settlement obținut separat din Stripe.

[iConta.eu](/)
