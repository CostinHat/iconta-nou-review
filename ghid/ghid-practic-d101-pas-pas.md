---
title: "Ghid practic D101 pas cu pas pentru contabili"
description: "Parcursul complet al declarației D101 în iConta.eu, de la balanță la definitivarea anuală a impozitului pe profit."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Ghid practic D101 pas cu pas pentru contabili

D101 este declarația ANUALĂ de definitivare a impozitului pe profit — nu declarația trimestrială (aceea e D100, cod de obligație 103).

## Temeiul legal

::: ghid-temei
"Art.17: Cota de impozit pe profit care se aplică asupra profitului impozabil este de 16%." — Legea 227/2015, citată în dosarul de cercetare F027 pe baza `anaf_surse/cod_fiscal_227_2015_consolidat.txt`.
:::

Pașii, așa cum funcționează motorul din `core/d101.py`:

1. **Cine datorează** — persoanele juridice enumerate la art.13 alin.(1); Trezoreria Statului, instituțiile publice și alte entități enumerate la art.13 alin.(2) sunt exceptate.
2. **Balanța** — `pull()` citește profilul firmei și balanța, cu conturile 76/66 tratate ca financiar și restul 7x/6x ca exploatare, plus 1012/1061/691 pentru rezerva legală.
3. **Rezultatul fiscal** — amortizarea fiscală (P11) se deduce, cheltuiala cu amortizarea contabilă (P2x/P28) se adaugă înapoi în cheltuielile nedeductibile (P34); ambele valori se introduc manual de către contabil.
4. **Rezerva legală (P13)** — calculată automat dacă nu e dată manual, plafonată la min(5% × bază; 20% × capital social − rezervă existentă), conform CF art.26 alin.(1) lit.a).
5. **Sponsorizarea (P43)** — dublă limită: 20% din impozit și 0,75% din cifra de afaceri (CF art.25 alin.(4) lit.i)).
6. **Avertismentul cont 691** — dacă soldul debitor al contului 691 e pozitiv și P23 e 0, aplicația avertizează, pentru că altfel impozitul iese subevaluat.
7. **Cota finală** — 16% aplicată pe profitul impozabil (P40 → P411).
8. **IMCA** — dacă cifra de afaceri a anului precedent depășește 50.000.000 EUR, `genereaza()` cere explicit P47 dacă nu a fost furnizat manual.
9. **Termenul** — legal, 25 iunie a anului următor (vezi ghidul dedicat termenului pentru detalii și pentru o discrepanță activă între cod și lege pentru anul fiscal 2026).

## Ce se greșește în practică

Cele mai frecvente greșeli: tratarea D101 ca declarație trimestrială, ignorarea avertismentului de la contul 691, și necompletarea manuală a P47 pentru firmele mari eligibile la IMCA.

## Ce face iConta.eu

Aplicația validează identitatea firmei înainte de generare (`erori_generare`), calculează automat rezerva legală dacă lipsește, avertizează pe contul 691 și rulează reconciliere independentă a bazei contabile la generare. Nu generează, în schimb, o D101 rectificativă din interfață — flag-urile de rectificare din structura XML sunt hardcodate la „0" în cod, fără parametru de intrare care să le seteze.

[iConta.eu](/)
