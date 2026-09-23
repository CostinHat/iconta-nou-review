---
title: "Cum transform profitul contabil în profit fiscal?"
description: "Trecerea de la profitul contabil la cel fiscal presupune add-back-uri obligatorii pe amortizare, cont 691 și rezerva legală."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum transform profitul contabil în profit fiscal?

Profitul fiscal nu este profitul contabil — este rezultatul unor ajustări precise, unele automate în aplicație, altele strict manuale.

## Temeiul legal

::: ghid-temei
"Avertisment cont 691 [...]: dacă soldul debitor al contului 691 (cheltuială cu impozitul pe profit) e >0 și rd.23 (P23, cheltuieli nedeductibile) e 0, se emite avertisment — cheltuiala e nedeductibilă (CF art.25 alin.(4) lit.a) și trebuie adăugată înapoi, altfel impozitul declarat iese subevaluat." — dosarul de cercetare F027, pe baza `core/d101.py` liniile 502–529.
:::

Cele trei ajustări principale confirmate în motorul D101:

1. **Amortizarea** — amortizarea fiscală (P11) se deduce din baza impozabilă; cheltuiala cu amortizarea contabilă (P2x/P28) se adaugă înapoi, ca parte din cheltuielile nedeductibile (P34). Ambele se introduc manual.
2. **Cheltuiala cu impozitul pe profit (cont 691)** — dacă are sold debitor pozitiv, e nedeductibilă (CF art.25 alin.(4) lit.a) și trebuie adăugată înapoi la baza impozabilă; altfel impozitul declarat iese subevaluat.
3. **Rezerva legală (P13)** — se scade din baza impozabilă, calculată automat (dacă nu e dată manual) din profitul contabil brut + cheltuiala cu impozitul, plafonată la min(5% × bază; 20% × capital social − rezervă existentă), conform CF art.26 alin.(1) lit.a).

Separat, sponsorizarea (P43) are o dublă limită de deducere: 20% din impozit și 0,75% din cifra de afaceri (CF art.25 alin.(4) lit.i).

## Ce se greșește în practică

Omiterea add-back-ului pentru cheltuiala cu impozitul pe profit (cont 691) este greșeala cu impactul cel mai concret măsurat: pe un portofoliu monitorizat, a scăzut impozitul declarat cu 2.432 lei, fără avertisment înainte de introducerea acestui gard în aplicație.

## Ce face iConta.eu

Aplicația calculează automat rezerva legală dacă nu e dată manual și emite avertisment explicit pe contul 691 când acesta indică o posibilă subevaluare. Amortizarea fiscală și add-back-ul contabil rămân, în schimb, introduse manual de contabil.

[iConta.eu](/)
