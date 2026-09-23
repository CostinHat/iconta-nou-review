---
title: "Cum se calculează impozitul pe profit la un SRL cu venituri mari"
description: "Firmele cu cifră de afaceri peste 50 de milioane de euro pot datora, pe lângă impozitul standard, impozitul minim pe cifra de afaceri (IMCA)."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se calculează impozitul pe profit la un SRL cu venituri mari

Peste un anumit prag de cifră de afaceri, impozitul pe profit standard de 16% nu mai e singurul calcul relevant — se poate adăuga impozitul minim pe cifra de afaceri (IMCA).

## Temeiul legal

::: ghid-temei
"Art.18^1 alin.(16) (introdus de OUG 89/2025 art.I pct.1, MO 1203/24.12.2025, în vigoare 01.01.2026): «Pentru anul fiscal 2026/anul fiscal modificat care începe în anul 2026, cota de impozit din cadrul formulei prevăzute la alin.(3) este 0,5%.»" — Legea 227/2015, citată în dosarul de cercetare F027.
:::

Regulile de bază: dacă cifra de afaceri a anului precedent (VT − Vs, la cursul de închidere a exercițiului) depășește pragul de 50.000.000 EUR (art.18^1 alin.(1)), firma poate datora IMCA, calculat după formula IMCA = cotă × (VT − Vs − I − A) (art.18^1 alin.(3)). Cota generală e 1%, dar pentru anul fiscal 2026 legea stabilește explicit 0,5% (art.18^1 alin.(16)); regimul IMCA e temporar, aplicabil până la 31 decembrie 2026 inclusiv (art.18^1 alin.(17)).

**Discrepanță critică de semnalat:** motorul D101 din iConta (`core/d101.py`, funcția `impozit_minim_cifra_afaceri`) calculează în prezent IMCA fix la 1% (`Decimal("0.01") * baza`), fără actualizarea la 0,5% cerută de lege pentru anul fiscal 2026 — practic dublează valoarea IMCA pentru firmele eligibile în 2026.

## Ce se greșește în practică

Cea mai costisitoare greșeală, pentru firmele mari eligibile în 2026, este preluarea directă a valorii IMCA calculate de aplicație fără recalculare manuală la cota legală de 0,5%.

## Ce face iConta.eu

`genereaza()` cere explicit completarea manuală a P47 dacă cifra de afaceri a anului precedent depășește pragul IMCA și P47 nu a fost furnizat manual, pentru a nu subevalua tacit impozitul. Calculul IMCA în sine este însă cablat la 1% în cod, neactualizat pentru anul fiscal 2026 — recomandăm recalcularea manuală la 0,5% până la corectarea aplicației.

[iConta.eu](/)
