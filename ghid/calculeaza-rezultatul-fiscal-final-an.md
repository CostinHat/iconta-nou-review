---
title: "Cum se calculează rezultatul fiscal la final de an 2026"
description: "Rezultatul fiscal pentru 2026 aplică cea de-a 16-a cotă standard, dar cere atenție la IMCA și la termenul de depunere, ambele cu discrepanțe active."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se calculează rezultatul fiscal la final de an 2026

Calculul de bază al rezultatului fiscal rămâne neschimbat pentru anul fiscal 2026, dar există două puncte specifice acestui an care merită atenție suplimentară.

## Temeiul legal

::: ghid-temei
"Art.17: Cota de impozit pe profit care se aplică asupra profitului impozabil este de 16%." — Legea 227/2015, citată în dosarul de cercetare F027, valabilă și pentru anul fiscal 2026.
:::

Calculul standard: profitul contabil ajustat cu deduceri (amortizare fiscală, P11), add-back-uri (amortizare contabilă și alte cheltuieli nedeductibile, P34, inclusiv contul 691 dacă are sold debitor pozitiv) și rezerva legală (P13) dă profitul impozabil (P40), înmulțit cu 16% pentru impozitul final (P411).

Pentru anul fiscal 2026, două puncte specifice, ambele documentate ca discrepanțe active între lege și aplicație:

1. **IMCA** — dacă cifra de afaceri a anului precedent depășește 50.000.000 EUR, legea stabilește pentru 2026 o cotă de 0,5% (art.18^1 alin.(16), introdus de OUG 89/2025) — dar motorul D101 din iConta calculează încă 1%, dublând practic valoarea IMCA pentru firmele eligibile.
2. **Termenul de depunere** — legal, 25 iunie 2027 pentru D101 aferent anului fiscal 2026 (art.42 alin.(1), modificat de OUG 8/2026) — dar aplicația poate afișa încă 25 martie 2027, aliniată unui validator intern nereactualizat, nu legii.

## Ce se greșește în practică

Preluarea necorectată a valorii IMCA sau a termenului de depunere direct din aplicație, fără verificare manuală, pentru firmele mari eligibile la anul fiscal 2026.

## Ce face iConta.eu

Aplicația calculează automat rezerva legală și avertizează pe contul 691. Pentru IMCA, cota folosită e încă 1% (necorectată la 0,5% pentru 2026) — recomandăm recalcularea manuală. Pentru termen, verificați manual data de 25 iunie 2027 până la actualizarea validatorului intern.

[iConta.eu](/)
