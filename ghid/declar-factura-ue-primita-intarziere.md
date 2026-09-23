---
title: "Cum declar o factură UE primită cu întârziere?"
description: "O factură intracomunitară primită cu întârziere se declară în luna exigibilității taxei, nu în luna primirii — dacă acea lună e deja închisă și depusă, se corectează prin rectificativă, nu prin înregistrare în luna curentă."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum declar o factură UE primită cu întârziere?

O factură care ajunge la contabilitate mult după livrare nu mută automat operațiunea în luna curentă — data care contează e cea a exigibilității, fixată de lege, nu data la care documentul a ajuns fizic.

## Temeiul legal

::: ghid-temei
„CF art. 284 alin. (1)-(2) — Faptul generator la AIC = data la care ar interveni la o livrare similară în statul membru al achiziției; exigibilitatea = data facturii furnizorului (sau autofactura art. 319 alin. 9), cel târziu a 15-a zi a lunii următoare celei a faptului generator.” — `cod_fiscal_227_2015_consolidat.txt` L17785-17793, dosarul F050.

„OPANAF 705/2020, pct. 1.2 — Persoanele impozabile înregistrate în scopuri de TVA depun declarația recapitulativă numai pentru lunile calendaristice în care ia naștere exigibilitatea taxei.” — `anaf_surse/opanaf_705_2020_d390.txt` L292-298, L619-623, dosarul F050.
:::

Exigibilitatea era deja fixată — cel târziu în a 15-a zi a lunii următoare livrării — indiferent când a sosit efectiv factura. Dacă luna exigibilității e deja închisă (declarații depuse), o factură întârziată nu se strecoară în luna curentă: operațiunea aparține lunii exigibilității, iar declarațiile aferente acelei luni se corectează prin rectificativă.

## Ce se greșește în practică

- Se înregistrează factura întârziată în luna în care a sosit fizic, nu în luna exigibilității reale — decalajul distorsionează atât D301, cât și D390.
- Se evită rectificativa din comoditate, deși operațiunea aparține unei luni deja declarate.
- Se ignoră faptul că D390 nu se depune „pe zero”: dacă rectificarea introduce prima operațiune intracomunitară dintr-o lună în care inițial nu exista niciuna, D390 pentru acea lună devine datorată și trebuie depusă (nu doar D301).

## Ce face iConta.eu

Data exigibilității se calculează din faptul generator și din data facturii, cu regula celor 15 zile aplicată automat, indiferent de momentul introducerii facturii în sistem. Front-ul D390↔D301 semnalează explicit situația în care D301 are achiziții intracomunitare într-o lună, dar D390 pentru aceeași lună iese pe zero — exact cazul unei operațiuni adăugate ulterior într-o lună deja închisă.

[iConta.eu](/)
