---
title: "Ce fac dacă am trecut o sumă pe rândul greșit în D300?"
description: Panoul manual din D300 nu are o rută de „editare" — corecția se face fie prin suprascriere (POST pe același cod de rând), fie prin ștergere urmată de o nouă introducere, dacă a fost ales alt cod de rând decât cel corect.
published: 2026-09-23
modified: 2026-09-23
poarta: v1
---

# Ce fac dacă am trecut o sumă pe rândul greșit în D300?

Panoul manual din D300 nu are o funcție de „mutare" a unei sume de pe un rând pe altul. Contractul e mai simplu decât atât, dar trebuie știut exact: suprascriere pe același cod de rând, sau ștergere plus reintroducere pe codul corect.

## Temeiul legal

::: ghid-temei
„Regularizări taxă colectată" — eticheta oficială a rândului R16, `d300_manual_api.py`, confirmată contra structurii ANAF D300 v12 (OPANAF 174/2026)
:::

Mecanismul de corecție de mai jos e identic pentru orice rând din allow-list-ul F251, nu doar pentru R16 — folosit aici ca exemplu.

## Dacă suma e greșită, dar rândul e corect

Un nou `POST /tenants/{id}/d300-manual`, pe **același** cod de rând, pentru aceeași perioadă (an, lună), suprascrie automat baza, TVA și descrierea existente — contractul e upsert pe `UNIQUE(an, luna, rand)`. Nu e nevoie de nicio ștergere prealabilă.

## Dacă rândul e greșit (ai ales alt cod decât cel corect)

Nu există o rută de „editare" sau „mutare" a codului de rând. Corecția are doi pași:

1. **DELETE** `/tenants/{id}/d300-manual/{rid}` — șterge intrarea de pe rândul greșit.
2. **POST** cu codul de rând corect — adaugă suma pe rândul potrivit.

Codul din UI nu oferă o rută separată de „move"/„redenumire" — schimbarea codului de rând e strict ștergere urmată de reintroducere.

## Gărzile rămân active la corecție

Dacă, după corecție, rândul ales ajunge să coincidă cu o sumă deja derivată automat dintr-o factură a perioadei, cererea de adăugare e respinsă cu eroare de câmp „rand" (dublă numărare) — indiferent că e prima introducere sau o corecție.

## Paritate garantată după corecție

Odată corectă, intrarea persistă în tabelul `d300_manual` și e recitită automat la generarea decontului, atât la preview cât și la depunerea efectivă — un test dedicat confirmă că XML-ul generat din baza de date e identic cu cel generat cu parametrul manual trimis explicit.

## Ce se greșește în practică

Se face un al doilea `POST`, pe alt cod de rând, sperând că vechea intrare greșită dispare automat — nu dispare. Ea rămâne în `d300_manual` până e ștearsă explicit prin `DELETE`, iar rezultatul e că ambele rânduri (cel greșit și cel corect) ajung să apară în decont, dacă nu se șterge întâi cel greșit.

## Ce face iConta.eu

Mecanismul de corecție e upsert (același cod de rând, aceeași perioadă = suprascriere automată) plus ștergere explicită (pentru schimbarea codului de rând) — fără o rută dedicată de „editare" sau „mutare", și fără ștergere silențioasă a intrărilor existente.

[iConta.eu](/)
