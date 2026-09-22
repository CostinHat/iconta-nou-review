---
title: Valoarea rămasă neamortizată este deductibilă la vânzarea activului?
description: Când un mijloc fix se vinde înainte de a fi complet amortizat, valoarea neamortizată trecută pe cont 6583 continuă mecanismul de recuperare fiscală a costului prin care a fost cumpărat activul — costul rămas se deduce la momentul cedării.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Valoarea rămasă neamortizată este deductibilă la vânzarea activului?

Un mijloc fix vândut la jumătatea duratei lui normale de utilizare lasă în urmă o parte din cost care nu a apucat să treacă prin amortizare lunară. Întrebarea practică e simplă: acea parte rămasă se pierde fiscal sau se recuperează totuși, dintr-o dată, la momentul vânzării?

## Temeiul legal

::: ghid-temei
**Art. 28 alin. (1) din Codul fiscal (Legea 227/2015)**: *„Cheltuielile aferente achiziționării, producerii, construirii mijloacelor fixe amortizabile, precum și investițiile efectuate la acestea se recuperează din punct de vedere fiscal prin deducerea amortizării potrivit prevederilor prezentului articol."*
:::

Textul stabilește principiul: costul unui mijloc fix se recuperează fiscal **integral**, prin amortizare — mecanismul prin care se face recuperarea e eșalonarea în timp, nu limitarea sumei recuperabile. Când activul iese din evidență înainte ca amortizarea eșalonată să fi ajuns la capăt, partea de cost care nu a apucat să treacă prin cheltuiala lunară cu amortizarea (6811) se înregistrează dintr-o dată, la cedare, tot ca o cheltuială legată de acel activ — cont **6583** „Cheltuieli privind activele cedate și alte operațiuni de capital".

## Regula concretă

La cedarea (vânzarea sau casarea) unui mijloc fix neamortizat integral, scoaterea din evidență se face în două părți:

```
2813 = 21x    (partea deja amortizată)
6583 = 21x    (valoarea rămasă neamortizată)
```

Valoarea trecută pe 6583 continuă, la momentul cedării, aceeași logică din alin. (1): costul activului se recuperează fiscal, iar partea care nu a fost încă dedusă prin amortizarea lunară se deduce acum, integral, ca o singură cheltuială legată de operațiunea de cedare — cu condiția generală, valabilă pentru orice cheltuială, ca activul să fi fost folosit efectiv în scopul activității economice a firmei.

## Ce se greșește în practică

- **Se consideră valoarea neamortizată „pierdută" fiscal** la vânzarea anticipată a unui activ, și nu se trece deloc pe cheltuială — de fapt ea se deduce, prin 6583, exact ca o continuare a recuperării de cost început prin amortizare.
- **Se confundă valoarea rămasă neamortizată cu o pierdere din vânzare.** Cele două sunt lucruri diferite: 6583 e costul rămas al activului (parte a operațiunii de scoatere din evidență), separat de rezultatul comercial al vânzării, care se vede din compararea venitului obținut (7583) cu valoarea contabilă netă a activului la acea dată.
- **Se calculează manual, aproximativ, valoarea rămasă**, în loc de amortizarea cumulată reală la data ieșirii — pe metoda degresivă sau accelerată, valoarea rămasă la o dată intermediară nu e o simplă proporție liniară din valoarea de intrare, ci depinde de algoritmul specific metodei.

## Ce face iConta.eu

Registrul de mijloace fixe calculează amortizarea cumulată și valoarea rămasă a unui activ la orice dată, pe metoda reală înregistrată pentru acel activ — liniară, degresivă, accelerată sau superaccelerată — nu pe o aproximare simplificată. La scoaterea din evidență, această valoare rămasă nu se introduce manual, ci se preia direct din calcul, la data exactă a operațiunii.

[iConta.eu](/)
