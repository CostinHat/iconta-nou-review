---
title: "Cum corectez o operațiune intracomunitară înregistrată în luna greșită?"
description: "Regula exigibilității TVA la achiziția intracomunitară și cum influențează ea luna în care apare operațiunea în D390."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum corectez o operațiune intracomunitară înregistrată în luna greșită?

Înainte de a corecta o operațiune, e util să înțelegi exact ce stabilește luna în care ea trebuie declarată — pentru că D390 nu se depune pe orice lună, ci strict pe lunile în care ia naștere exigibilitatea taxei.

## Temeiul legal

::: ghid-temei
CF art. 284 alin. (1)-(2): „Faptul generator la AIC = data la care ar interveni la o livrare similară în statul membru al achiziției; exigibilitatea = data facturii furnizorului (sau autofactura art. 319 alin. 9), cel târziu a 15-a zi a lunii următoare celei a faptului generator.” (sursă: `cod_fiscal_227_2015_consolidat.txt`, L17785-17793)

OPANAF 705/2020, pct. 1.2: „Persoanele impozabile înregistrate în scopuri de TVA depun declarația recapitulativă numai pentru luna de raportare în care ia naștere exigibilitatea taxei pentru livrările/achizițiile/prestările intracomunitare (...).” (sursă: `anaf_surse/opanaf_705_2020_d390.txt`, L619-623)
:::

Practic, luna în care o achiziție intracomunitară trebuie declarată e determinată de exigibilitate: data facturii furnizorului, dar nu mai târziu de a 15-a zi a lunii următoare faptului generator. Dacă o operațiune a fost înregistrată cu o dată greșită (de exemplu data facturii, în loc de data corectă a faptului generator, sau invers), ea poate ajunge clasificată în luna greșită pentru D390.

Corecția presupune, în esență, editarea datelor operațiunii astfel încât exigibilitatea să reflecte corect regula de mai sus. Dacă operațiunea greșit datată a fost deja inclusă într-un D390 deja depus, corectarea presupune și rectificarea declarației pentru luna respectivă (și, dacă e cazul, declararea pe luna corectă) — un aspect de procedură declarativă generală, nedetaliat punctual în cercetarea care stă la baza acestui ghid.

## Ce se greșește în practică

- Se completează data operațiunii cu data facturii, fără să se ia în calcul câmpul opțional al datei faptului generator, atunci când acesta ar schimba luna de exigibilitate.
- Se lasă câmpul „dată faptul generator” necompletat, deși operațiunea reală are o dată a faptului generator diferită de data facturii — implicit, gol înseamnă încadrare pe data facturii, ceea ce poate să nu corespundă realității.
- Se corectează operațiunea în evidența internă, dar se omite rectificarea D390 deja depus pentru luna greșită.

## Ce face iConta.eu

Formularul de achiziție intracomunitară (`achizitie_ic`) are un câmp opțional pentru data faptului generator, cu explicație directă în interfață: „Gol = încadrare pe data facturii. Completat = exigibilitate MIN(dată factură, ziua 15 luna următoare) — art. 284.” Corectarea unei operațiuni datate greșit înseamnă, practic, editarea acestor câmpuri (data facturii și/sau data faptului generator) astfel încât exigibilitatea calculată să corespundă realității, ceea ce mută automat operațiunea în luna corectă pentru D390.

Cercetarea care stă la baza acestui ghid nu a identificat o funcționalitate separată, dedicată exclusiv „mutării” unei operațiuni deja declarate dintr-o lună în alta — corectarea se face la nivelul datelor operațiunii, iar orice declarație deja depusă greșit urmează regulile generale de rectificare a D390.

[iConta.eu](/)
