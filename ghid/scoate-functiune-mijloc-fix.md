---
title: "Cum se scoate din funcțiune un mijloc fix?"
description: "Din registrul iConta.eu, acțiunea Casează generează automat amortizarea la zi și dezactivează activul, printr-o notă ciornă validată separat din Registrul jurnal."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se scoate din funcțiune un mijloc fix?

Scoaterea din funcțiune (casarea) e operațiunea prin care un mijloc fix își încetează folosirea și e retras din evidența activă.

## Temeiul legal

::: ghid-temei
"Câștigurile sau pierderile rezultate din vânzarea ori din scoaterea din funcțiune a acestor mijloace fixe se calculează pe baza valorii fiscale a acestora, diminuată cu amortizarea fiscală, cu excepția celor prevăzute la alin. (14)." — Codul fiscal, art. 28 alin. (17)
:::

Rezultatul fiscal al scoaterii din funcțiune se determină din valoarea fiscală a activului, diminuată cu amortizarea fiscală acumulată — adică valoarea rămasă la data operațiunii.

## Ce se greșește în practică

Se marchează activul ca inactiv doar "manual", fără calculul corect al amortizării la zi pe metoda reală, ceea ce distorsionează valoarea rămasă folosită la determinarea rezultatului.

## Ce face iConta.eu

Din registrul de mijloace fixe, acțiunea **Casează** de pe rândul activului pornește o notă de inventariere cu operațiunea de casare: aplicația calculează automat amortizarea la zi (pe metoda reală a activului) și dezactivează activul (`activ=false`). Nota generată e o ciornă, validată separat din Registrul jurnal, nu aplicată direct pe registrul de mijloace fixe.

[iConta.eu](/)
