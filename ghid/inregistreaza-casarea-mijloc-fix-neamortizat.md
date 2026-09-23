---
title: "Cum se înregistrează casarea unui mijloc fix neamortizat integral?"
description: "Când activul nu e complet amortizat, iConta.eu calculează automat amortizarea la zi și valoarea rămasă, folosite pentru determinarea rezultatului fiscal al casării."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se înregistrează casarea unui mijloc fix neamortizat integral?

Dacă activul mai are valoare rămasă la data casării, aceasta intră direct în calculul rezultatului fiscal al operațiunii.

## Temeiul legal

::: ghid-temei
"Câștigurile sau pierderile rezultate din vânzarea ori din scoaterea din funcțiune a acestor mijloace fixe se calculează pe baza valorii fiscale a acestora, diminuată cu amortizarea fiscală, cu excepția celor prevăzute la alin. (14)." — Codul fiscal, art. 28 alin. (17)
:::

Formula rămâne aceeași indiferent de gradul de amortizare: valoare fiscală minus amortizare fiscală acumulată la data casării = valoare rămasă, folosită în calculul rezultatului.

## Ce se greșește în practică

Se ignoră faptul că activul are încă valoare rămasă la casare, sau se calculează greșit amortizarea până la acea dată dacă metoda nu e liniară.

## Ce face iConta.eu

Indiferent de gradul de amortizare al activului, acțiunea de casare calculează automat, pe metoda reală a activului, amortizarea la zi și, implicit, valoarea rămasă la data casării — folosind aceeași funcție a motorului unic de amortizare citită de registru. Un detaliu de graniță notat în cod: pragul de încadrare ca mijloc fix (5.000 lei) nu mai e reverificat la casarea manuală a unui activ deja existent în registru — verificarea pragului se face doar la intrarea inițială ca obiect de inventar, nu și la casare.

[iConta.eu](/)
