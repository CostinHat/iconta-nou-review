---
title: "Cum verifici dacă un mijloc fix este complet amortizat?"
description: "Un mijloc fix e complet amortizat când valoarea rămasă calculată de iConta.eu ajunge la zero — vizibilă direct în coloana 'rămas' din registru."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum verifici dacă un mijloc fix este complet amortizat?

Valoarea rămasă (net book value) a unui activ scade lună de lună, pe metoda lui reală de amortizare, până ajunge la zero — acel moment marchează un activ complet amortizat.

## Temeiul legal

::: ghid-temei
"Amortizarea fiscală se calculează după cum urmează: a) începând cu luna următoare celei în care mijlocul fix amortizabil se pune în funcțiune, prin aplicarea regimului de amortizare prevăzut la alin. (5);" — Codul fiscal, art. 28 alin. (12) lit. a)
:::

Cât timp durata normală de funcționare nu e epuizată, valoarea rămasă se calculează pe metoda reală a activului (liniar, degresiv, accelerat, superaccelerat) — nu e o simplă scădere liniară pentru toate activele.

## Ce se greșește în practică

Se estimează "din ochi" dacă un activ e complet amortizat, pe baza duratei normale trecute de la PIF, fără să se ia în calcul eventuale reevaluări care au schimbat etapele amortizării.

## Ce face iConta.eu

Coloana "rămas" din registru afișează exact valoarea rămasă calculată de motorul unic de amortizare, pe metoda reală a activului, la data curentă — când această valoare ajunge la zero, activul e complet amortizat. Dacă durata normală s-a epuizat deja înainte de o eventuală reevaluare, aplicația refuză explicit operațiunea, în loc să ghicească o durată rămasă.

[iConta.eu](/)
