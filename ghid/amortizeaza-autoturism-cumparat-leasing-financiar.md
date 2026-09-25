---
title: "Cum se amortizează un autoturism cumpărat prin leasing financiar?"
description: "Contabil se amortizează integral valoarea de intrare; fiscal, pentru autoturisme M1, deductibilitatea amortizării e plafonată la 1.500 lei/lună, cu excepții prevăzute de lege."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se amortizează un autoturism cumpărat prin leasing financiar?

Un autoturism preluat prin leasing financiar se amortizează la locatar, ca orice mijloc fix — dar pentru autoturisme există o limită fiscală suplimentară, distinctă de amortizarea contabilă: deductibilitatea la impozitul pe profit e plafonată.

## Temeiul legal

::: ghid-temei
**Legea 227/2015 (Codul fiscal), art. 28 alin. (14)**: „[...] pentru mijloacele de transport de persoane care au cel mult 9 scaune de pasageri, incluzând și scaunul șoferului, din categoria M1 [...], cheltuielile cu amortizarea sunt deductibile, pentru fiecare, în limita a 1.500 lei/lună. [...] Sunt exceptate situațiile în care mijloacele de transport respective se înscriu în oricare dintre următoarele categorii: a) vehiculele utilizate exclusiv pentru servicii de urgență, servicii de pază și protecție și servicii de curierat [...]."
— (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)

**OMFP 1802/2014, pct. 214 alin. (2)**: „În cazul leasingului financiar, achizițiile de către locatar de bunuri imobile şi mobile sunt tratate ca investiții în imobilizări, fiind supuse amortizării pe o bază consecventă cu politica normală de amortizare pentru bunuri similare ale locatarului."
— (sursă: anaf_surse/omfp_1802_2014.txt)
:::

- **Contabil**: se amortizează integral valoarea de intrare (capitalul recunoscut prin 2133=167, la primire), pe durata normală de utilizare din Catalogul mijloacelor fixe.
- **Fiscal**: cheltuiala deductibilă la calculul impozitului pe profit e plafonată la **1.500 lei/lună per autoturism**, indiferent cât de mare e amortizarea contabilă lunară — diferența devine element de reintegrare fiscală.
- Plafonul nu se aplică dacă mașina se încadrează într-una din excepțiile enumerate de lege (intervenție, pază, curierat, agenți de vânzări, taximetrie, servicii cu plată/școli de șoferi, vehicule-marfă) — aceeași listă folosită și la plafonul de 50% pentru cheltuielile de funcționare.

## Ce se greșește în practică

- Se aplică plafonul de 1.500 lei/lună și cheltuielilor de funcționare, întreținere și reparații — acelea au propriul plafon, de 50% (art. 25 alin. (3) lit. l)) — cele două limite sunt distincte și cumulative, nu una o înlocuiește pe cealaltă.
- Se uită că plafonul se aplică **per autoturism**, nu global pe toate mașinile firmei.
- Se presupune că amortizarea contabilă trebuie limitată direct la 1.500 lei/lună — greșit: contabil se amortizează integral, iar plafonul acționează doar la calculul rezultatului fiscal (impozitul pe profit).

## Ce face iConta.eu

F056 (Leasing financiar și operațional) înregistrează corect intrarea autoturismului (2133=167, cu dobânda ținută extracontabil pe 8051) și ratele lunare — dar calculul amortizării propriu-zise, inclusiv aplicarea plafonului fiscal de 1.500 lei/lună, nu e cod în acest modul. Amortizarea rulează prin registrul de Mijloace fixe, unde bunul e tratat identic cu orice alt autoturism al firmei, fără nicio distincție pentru că a intrat prin leasing.

[iConta.eu](/)
