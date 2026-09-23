---
title: Cum refac SAF-T pentru perioade contabile vechi
description: Regenerarea unui fișier SAF-T (D406) pentru o lună veche nu e blocată de „Blocare perioade" în iConta.eu — generarea citește evidența așa cum e la momentul rulării. Dacă lipsesc înregistrări din luna veche, ele se corectează separat, prin mecanismul obișnuit de corecție.
published: 2026-09-23
modified: 2026-09-23
poarta: v1
---

# Cum refac SAF-T pentru perioade contabile vechi

Funcția „Blocare perioade" din iConta.eu oprește scrierile pe o lună — nu citirile. Generarea unui fișier SAF-T pentru o lună veche, chiar blocată, funcționează normal, pentru că citește exact ce există deja în evidență la momentul rulării, fără să încerce vreo modificare.

## Temeiul legal

::: ghid-temei
„Contribuabilul/Plătitorul are obligația de a depune la organul fiscal central o declarație cuprinzând informații din evidența contabilă și fiscală, denumită în continuare fișierul standard de control fiscal." — Legea nr. 207/2015 privind Codul de procedură fiscală, art. 59^1 alin. (1)

„Nu se sancționează contravențional: a) persoanele care corectează fișierul standard de control fiscal până la termenul legal de depunere a următorului fișier; b) persoanele care, ulterior termenului legal de depunere, corectează fișierul standard de control fiscal ca urmare a unui fapt neimputabil persoanei impozabile." — art. 337^1 alin. (3)
:::

Legea însăși prevede explicit că un SAF-T se poate corecta — și scutește de sancțiune corecția făcută înainte de termenul următoarei depuneri, sau ulterior, dacă motivul nu ține de contribuabil (de exemplu, o factură de furnizor sosită cu întârziere, descoperită după depunere).

## Ce se întâmplă, tehnic, în iConta.eu

Refacerea unui SAF-T pentru o lună veche nu are nicio verificare legată de „Blocare perioade" — motorul de generare primește pur și simplu anul și luna cerute și citește rulajele reale ale conturilor pentru acea lună, indiferent dacă e blocată sau deschisă. Regenerarea unei luni închise funcționează la fel ca a uneia deschise: nu blochează nimic, nu modifică nimic în evidență, doar produce fișierul din starea curentă a datelor.

Dacă motivul pentru care refaci SAF-T e o lipsă în evidență (o factură nu apărea în luna respectivă), regenerarea în sine **nu rezolvă lipsa** — SAF-T-ul citește ce există, nu completează ce lipsește. Factura trebuie mai întâi înregistrată, cu mecanismul obișnuit pentru facturi vechi uitate: dacă luna e blocată prin „Blocare perioade", nota de contare se scrie cu data descoperirii, nu cu data facturii. Abia după ce înregistrarea există, regenerarea SAF-T o include.

## Ce se greșește în practică

- Se presupune că regenerarea SAF-T „recuperează" automat o factură uitată — de fapt, dacă factura nu e încă înregistrată, SAF-T-ul refăcut arată exact aceeași lipsă ca cel vechi.
- Se încearcă deblocarea lunii doar pentru a regenera SAF-T-ul — inutil, pentru că regenerarea nu depinde de starea blocajului.
- Se amână corectarea unui SAF-T vechi de teama unei sancțiuni, deși legea scutește explicit corecțiile făcute până la termenul următoarei depuneri, și pe cele ulterioare, dacă motivul nu e imputabil contribuabilului.

## Ce face iConta.eu

Generarea SAF-T pentru orice lună, indiferent de starea ei în „Blocare perioade", produce fișierul din datele existente la momentul rulării — nicio verificare de perioadă blocată nu intervine la citire. Dacă lipsește o înregistrare din luna veche, ea trebuie adăugată separat, prin mecanismul standard de corecție (notă datată la momentul descoperirii, cu motivul consemnat), iar regenerarea ulterioară a SAF-T-ului o include automat, pentru că citește evidența reală, actualizată.

[iConta.eu](/)
