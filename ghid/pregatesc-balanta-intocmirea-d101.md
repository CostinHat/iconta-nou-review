---
title: "Cum pregătesc balanța pentru întocmirea D101"
description: "D101 se construiește dintr-o balanță cu conturi separate corect pe exploatare/financiar și cu datele necesare rezervei legale."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum pregătesc balanța pentru întocmirea D101

Înainte de a genera D101, balanța trebuie să conțină, corect încadrate, câteva categorii de conturi pe care aplicația le citește automat.

## Temeiul legal

::: ghid-temei
Rezerva legală (P13) este "calculată automat când nu e dată manual [...], din profitul contabil brut + cheltuiala cu impozitul (cont 691), plafonată la min(5% × bază; 20% × capital social − rezervă existentă), temei CF art.26 alin.(1) lit.a)." — dosarul de cercetare F027, pe baza `core/d101.py` liniile 264–275.
:::

Funcția `pull()` din `core/d101.py` (liniile 448–467) citește profilul firmei și balanța, cu o separare clară: conturile din clasele 76 și 66 sunt tratate ca financiar, iar restul conturilor din clasele 7x și 6x ca exploatare. Tot `pull()` aduce și datele necesare rezervei legale: capitalul social (cont 1012), rezerva deja constituită (cont 1061) și cheltuiala cu impozitul pe profit (cont 691).

## Ce se greșește în practică

Greșelile frecvente la această etapă: încadrarea greșită a unor conturi financiare (76/66) în categoria de exploatare, sau invers; omiterea soldului contului 691 din balanța pregătită, ceea ce afectează atât calculul rezervei legale, cât și avertismentul de nedeductibilitate; lipsa datelor de capital social (1012) sau rezervă existentă (1061), care blochează calculul automat corect al plafonului rezervei legale.

## Ce face iConta.eu

`pull()` citește automat balanța firmei conform separării de mai sus. Dacă rezerva legală nu e introdusă manual, aplicația o calculează automat pe baza acelorași conturi, respectând plafonul legal. Aplicația emite și un avertisment separat legat de contul 691 (detaliat în ghidul dedicat verificării D101), tocmai pentru a semnala când soldul acestui cont nu a fost tratat corect.

[iConta.eu](/)
