---
title: "Cum regularizez impozitul pe profit la sfârșitul anului?"
description: "Regularizarea anuală a impozitului pe profit se face prin D101, declarația exclusiv anuală de definitivare."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum regularizez impozitul pe profit la sfârșitul anului?

Regularizarea de final de an a impozitului pe profit este exact rolul declarației D101 — declarația anuală de definitivare, distinctă de plățile trimestriale din D100.

## Temeiul legal

::: ghid-temei
"D101 [...] e exclusiv declarația ANUALĂ de definitivare." — dosarul de cercetare F027, pe baza `core/d100.py` și `core/d101.py`.
:::

Definitivarea aplică cota de 16% (CF art.17) pe profitul impozabil final (P40 → P411), după parcurgerea deducerilor (amortizare fiscală, P11), add-back-urilor (amortizare contabilă și alte cheltuieli nedeductibile, P34) și a rezervei legale (P13). Dacă cifra de afaceri a anului precedent depășește pragul de 50.000.000 EUR, funcția `genereaza()` cere explicit completarea manuală a P47 (dacă nu a fost deja furnizat), tocmai pentru a nu subevalua tacit impozitul unei firme mari eligibile la IMCA.

La generare, aplicația rulează și o reconciliere independentă a bazei contabile (`core/d101_reconciliere.py`) și verifică `totalPlata_A` emis (`core/reconciliere_emis.py`).

## Ce se greșește în practică

Greșeala tipică e ignorarea avertismentului legat de contul 691 (cheltuiala cu impozitul pe profit) la finalul anului, ceea ce poate subevalua impozitul definitivat, sau necompletarea manuală a P47 pentru firmele eligibile la IMCA.

## Ce face iConta.eu

Motorul D101 calculează automat rezerva legală dacă lipsește, avertizează pe contul 691, cere P47 pentru firmele mari eligibile IMCA și rulează reconciliere independentă la generare. Termenul legal de depunere este 25 iunie a anului următor — vedeți ghidul dedicat termenului pentru o discrepanță activă documentată pentru anul fiscal 2026.

[iConta.eu](/)
