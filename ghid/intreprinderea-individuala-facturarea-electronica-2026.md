---
title: "Întreprinderea individuală și facturarea electronică 2026"
description: "II e obligată la e-Factura B2B ca orice alt operator economic, deși e exclusă necondiționat din obligația SAF-T — cele două reguli au sfere diferite."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Întreprinderea individuală și facturarea electronică 2026

Forma juridică nu scutește de obligația de facturare electronică. Legea RO e-Factura definește sfera obligației prin natura activității economice, nu prin forma de organizare — o întreprindere individuală (II) e „operator economic" în același sens ca un SRL.

## Temeiul legal

::: ghid-temei
„operator economic - orice entitate care desfăşoară o activitate economică constând în executarea de lucrări, livrarea de bunuri/produse şi/sau prestarea de servicii."
— OUG 120/2021, art. 2 lit. b) (sursă: anaf_surse/oug_120_2021.txt)
:::

Ce rezultă concret pentru o II în 2026:

- **Obligația de e-Factura B2B** se aplică oricărei entități care desfășoară o activitate economică, fără distincție de formă juridică — o II care emite facturi către alți operatori economici intră sub incidența OUG 120/2021 la fel ca orice SRL.
- **Contrast cu SAF-T**: spre deosebire de e-Factura, obligația de depunere a fișierului standard de control fiscal (D406) exclude expres întreprinderile individuale: „Următoarele categorii de contribuabili nu au obligația de depunere a fișierului standard de control fiscal (SAF-T): a) persoanele fizice autorizate (PFA); b) întreprinderile individuale (II)" (OPANAF 407/2025, Anexa 5 pct. 4 lit. a și b).
- **Concluzia**: cele două obligații (e-Factura și SAF-T) au sfere diferite — forma juridică „II" nu conferă scutire generală de digitalizare fiscală, ci doar de obligația specifică SAF-T.

## Ce se greșește în practică

- Se presupune că excluderea de la SAF-T (confirmată explicit pentru PFA/II) se extinde și la e-Factura — cele două obligații sunt reglementate de acte diferite, cu sfere de aplicare diferite.
- Se amână înregistrarea în Registrul RO e-Factura pe motiv că firma e „doar o II mică", deși obligația legală nu distinge după cifra de afaceri sau forma juridică, ci după calitatea de operator economic.
- Se ignoră faptul că emitentul și destinatarul trebuie să fie amândoi înregistrați în Registrul RO e-Factura pentru ca utilizarea facturii electronice să fie considerată acceptată (OUG 120/2021, art. 10-11) — o II care nu se înregistrează complică tranzacțiile cu partenerii ei.

## Ce face iConta.eu

iConta.eu trimite și primește facturi prin sistemul RO e-Factura (`core/efactura_send.py`) fără o ramificare de cod pe forma juridică a firmei — fluxul e identic pentru II, PFA sau SRL. Pentru SAF-T, aplicația respectă corect excluderea legală: PFA/II/PFL sunt excluse necondiționat din obligația D406, conform OPANAF 407/2025, Anexa 5 pct. 4 lit. a) și b), citat explicit în codul care determină declarațiile datorate (`core/control_fiscal_api.py`).

[iConta.eu](/)
