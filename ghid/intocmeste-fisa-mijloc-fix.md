---
title: "Cum se întocmește fișa unui mijloc fix?"
description: "Câmpurile obligatorii și cele opționale pe care le cere iConta.eu la introducerea unui mijloc fix nou, și validările aplicate la import."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se întocmește fișa unui mijloc fix?

Completarea evidenței unui mijloc fix nou presupune un set de câmpuri care alimentează direct motorul de amortizare.

## Temeiul legal

::: ghid-temei
"Amortizarea fiscală se calculează după cum urmează: a) începând cu luna următoare celei în care mijlocul fix amortizabil se pune în funcțiune, prin aplicarea regimului de amortizare prevăzut la alin. (5);" — Codul fiscal, art. 28 alin. (12) lit. a)
:::

Câmpurile care contează fiscal sunt: cod (identificator unic), denumire, cont de imobilizare (stabilește categoria și metodele permise), cont de amortizare, valoare de intrare, valoare reziduală, durata normală de funcționare (în luni) și metoda de amortizare.

## Ce se greșește în practică

Se completează codul duplicat, o valoare reziduală mai mare decât valoarea de intrare, sau o durată de zero luni — toate blocate la import, dar posibile ca eroare de tastare la introducere manuală dacă nu sunt verificate.

## Ce face iConta.eu

La import (CSV/XLSX), aplicația blochează: cod lipsă sau duplicat, durată ≤0, valoare ≤0, rezidual mai mare decât valoarea de intrare. Avertizează, dar nu blochează: valoare sub pragul de încadrare ca mijloc fix la data PIF, sau cont de imobilizare lipsă — în acest ultim caz, activul rămâne cu "categorie neclasificată", ceea ce permite doar metodele liniară/degresivă, urmând ca accelerata/superaccelerata să fie refuzate la calcul până se completează contul.

[iConta.eu](/)
