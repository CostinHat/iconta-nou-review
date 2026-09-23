---
title: "Cum se casează corect un mijloc fix uzat"
description: "Pașii casării unui mijloc fix în iConta.eu: calculul automat al amortizării la zi, dezactivarea activului și validarea notei ca ciornă."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se casează corect un mijloc fix uzat

Casarea unui mijloc fix uzat înseamnă scoaterea lui din folosință și din evidența activă, pe baza valorii rămase calculate corect la data casării.

## Temeiul legal

::: ghid-temei
"Câștigurile sau pierderile rezultate din vânzarea ori din scoaterea din funcțiune a acestor mijloace fixe se calculează pe baza valorii fiscale a acestora, diminuată cu amortizarea fiscală, cu excepția celor prevăzute la alin. (14)." — Codul fiscal, art. 28 alin. (17)
:::

Rezultatul casării se determină din valoarea fiscală a activului diminuată cu amortizarea fiscală acumulată la data casării — nu dintr-o estimare aproximativă.

## Ce se greșește în practică

Se casează activul fără să se recalculeze corect amortizarea la zi pe metoda lui reală, sau se lasă activul "activ" în registru după ce a fost efectiv scos din folosință.

## Ce face iConta.eu

Din registru, pe rândul activului, acțiunea **Casează** declanșează o notă de inventariere cu operațiunea de casare. Aplicația calculează automat amortizarea la zi (folosind aceeași funcție a motorului unic de amortizare, pe metoda reală a activului) și dezactivează activul din registru. Nota generată e o **ciornă**, validată separat din Registrul jurnal, nu aplicată direct pe registrul de mijloace fixe.

[iConta.eu](/)
