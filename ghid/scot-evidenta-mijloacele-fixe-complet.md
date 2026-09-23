---
title: "Cum scot din evidență mijloacele fixe complet amortizate înainte de radiere?"
description: "Scoaterea din registru a activelor complet amortizate folosește aceeași acțiune de Casare, indiferent de valoarea rămasă."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum scot din evidență mijloacele fixe complet amortizate înainte de radiere?

Un mijloc fix complet amortizat (valoare rămasă zero) se scoate din registru la fel ca oricare altul — nu există un flux separat pentru active ajunse la finalul duratei de amortizare.

## Temeiul legal

::: ghid-temei
"Câștigurile sau pierderile rezultate din vânzarea ori din scoaterea din funcțiune a acestor mijloace fixe se calculează pe baza valorii fiscale a acestora, diminuată cu amortizarea fiscală..."
— Codul fiscal, art.28 alin.(17)
:::

Pentru un activ complet amortizat, valoarea fiscală rămasă e deja zero, deci scoaterea din evidență nu mai generează, de regulă, un rezultat fiscal semnificativ din diferența valoare-amortizare — dar activul tot trebuie dezactivat formal în registru pentru ca evidența să reflecte corect situația reală.

## Ce se greșește în practică

Greșeala frecventă e lăsarea activelor complet amortizate active în registru "pentru că oricum nu mai generează amortizare" — ceea ce menține evidența incompletă și poate complica pregătirea unei radieri sau lichidări.

## Ce face iConta.eu

Ecranul de Casare dezactivează activul (`activ=false`) indiferent de valoarea rămasă calculată — inclusiv pentru active complet amortizate, unde `amortizat_la_data` va calcula automat valoarea rămasă la zero. Nota generată e ciornă, validată separat din Registrul jurnal.

[iConta.eu](/)
