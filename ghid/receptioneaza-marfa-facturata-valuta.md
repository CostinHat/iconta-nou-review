---
title: "Cum se recepționează marfa facturată în valută?"
description: Dacă marfa sosește cu factura, cursul folosit e cel BNR de la data facturii; dacă sosește doar cu aviz de însoțire, urmând ca factura să vină ulterior, cursul folosit la recepție este cel BNR de la data recepției bunurilor, nu cel de la data facturii.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum se recepționează marfa facturată în valută?

Recepția unei mărfi achiziționate în valută ridică o întrebare simplă, dar cu răspuns diferit în funcție de documentul care însoțește marfa: dacă marfa vine cu factura, cursul e cel al facturii; dacă vine doar cu avizul de însoțire, iar factura sosește ulterior, cursul folosit la recepție e altul.

## Temeiul legal

::: ghid-temei
„În cazul bunurilor achiziționate însoțite de factură sau de aviz de însoțire a mărfii, urmând ca factura să sosească ulterior, cursul valutar utilizat la înregistrarea în contabilitate este cursul de la data recepției bunurilor." — OMFP 1802/2014 (Reglementările contabile), pct. 314 alin. (4).
:::

## Cele două situații

- **Marfa sosește însoțită de factură** — recepția și înregistrarea în gestiune se fac la cursul BNR de la data facturii (respectiv, conform art. 290 CF, cursul valabil la data exigibilității taxei pentru operațiune, care de regulă coincide cu data facturii).
- **Marfa sosește cu aviz de însoțire, factura urmând să sosească ulterior** — recepția se înregistrează la **cursul de la data recepției bunurilor**, nu la un curs estimat sau la cursul din ziua în care sosește ulterior factura. Când factura ajunge, ea confirmă cantitățile și prețurile, dar cursul de recepție rămâne cel stabilit la intrarea efectivă a mărfii în gestiune.

Diferența dintre valoarea recepționată (la cursul de la data recepției) și valoarea facturată ulterior (la cursul propriu al facturii, dacă diferă) se tratează ca diferență de curs valutar, nu ca o corecție a costului de achiziție al mărfii.

## Ce se greșește în practică

- Se așteaptă sosirea facturii pentru a înregistra recepția, deși marfa a intrat deja fizic în gestiune pe bază de aviz — recepția trebuie înregistrată la cursul zilei ei, nu amânată.
- Se folosește, la sosirea facturii întârziate, cursul din ziua facturii pentru a rectifica valoarea mărfii deja recepționate — costul de achiziție rămâne cel de la data recepției; diferența de curs se contabilizează separat, nu prin modificarea valorii stocului.
- Se confundă regula aceasta (recepție pe aviz, curs de la data recepției) cu regula generală de la art. 290 CF (curs la exigibilitatea taxei) — cele două reguli coexistă și se aplică în situații diferite: art. 290 CF privește baza de TVA a facturii, pct. 314 alin. (4) privește momentul contabil al recepției mărfii fără factură.

## Ce face iConta.eu

Cursul BNR folosit pentru orice operațiune valutară introdusă în aplicație se determină pentru data operațiunii, prin motorul de curs (`core/curs_bnr.py`), cu regula „ultimul curs BNR comunicat, valabil cel târziu la data cerută". Aplicația nu presupune tăcut un curs dacă acesta nu poate fi determinat pentru data respectivă (curs indisponibil, prea vechi sau monedă necotată) — semnalează explicit situația, în loc să folosească implicit cursul altei date apropiate.

[iConta.eu](/)
