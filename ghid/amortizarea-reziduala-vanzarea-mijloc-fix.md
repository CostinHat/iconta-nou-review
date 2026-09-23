---
title: "Amortizarea reziduală la vânzarea unui mijloc fix"
description: "La vânzare, rezultatul se calculează pe baza valorii fiscale rămase (după amortizare), pe care registrul din iConta.eu o calculează pe metoda reală a activului."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Amortizarea reziduală la vânzarea unui mijloc fix

"Amortizarea reziduală" nu e un termen legal separat — ceea ce contează la vânzare e valoarea fiscală rămasă a activului, adică valoarea de intrare diminuată cu amortizarea deja calculată.

## Temeiul legal

::: ghid-temei
"Câștigurile sau pierderile rezultate din vânzarea ori din scoaterea din funcțiune a acestor mijloace fixe se calculează pe baza valorii fiscale a acestora, diminuată cu amortizarea fiscală, cu excepția celor prevăzute la alin. (14)." — Codul fiscal, art. 28 alin. (17)
:::

Formula legală e simplă: rezultatul vânzării pornește de la valoarea fiscală a activului din care se scade amortizarea fiscală acumulată — adică exact valoarea rămasă (net book value) afișată în registru la data vânzării.

## Ce se greșește în practică

Se folosește pentru calculul rezultatului valoarea contabilă amortizată identic (liniar) pentru toate activele, deși metoda reală a activului (degresivă, accelerată etc.) dă o valoare rămasă diferită la aceeași dată.

## Ce face iConta.eu

Funcția centrală a motorului de amortizare calculează amortizarea cumulată "la zi" și valoarea rămasă pe metoda reală a fiecărui activ — aceeași funcție citită de registru și de casare. Pentru vânzare, aplicația nu are un flux dedicat, dar valoarea rămasă afișată în coloana "rămas" a registrului, la data vânzării, e cifra corectă de pornit pentru calculul manual al rezultatului.

[iConta.eu](/)
