---
title: "Cum se înregistrează contabil o achiziție intracomunitară de bunuri în 2026?"
description: Contabil, o achiziție intracomunitară de bunuri înseamnă două operațiuni în oglindă — valoarea bunurilor pe contul de destinație, în corespondență cu furnizorul, și TVA autolichidată prin formula 4426 = 4427.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum se înregistrează contabil o achiziție intracomunitară de bunuri în 2026?

Din punct de vedere strict contabil, o achiziție intracomunitară de bunuri presupune două seturi de înregistrări: valoarea bunurilor propriu-zisă, pe contul potrivit destinației lor (marfă, materii prime, ambalaje etc.), și TVA aferentă, calculată și înregistrată de cumpărător, nu preluată de pe factura furnizorului.

## Temeiul legal

::: ghid-temei
HG 1/2016, norme la CF art. 331, pct. 109 alin. (1): „beneficiarul înregistrează… suma taxei aferente în următoarea formulă contabilă: 4426 = 4427. Prevederile acestui alineat sunt valabile pentru orice alte situații în care se aplică taxarea inversă.” CF art. 308-309: obligat la plata taxei este beneficiarul, la achiziții intracomunitare și la serviciile primite conform art. 278 alin. (2).
:::

Concret, apar două linii distincte: valoarea bunurilor din factura furnizorului, convertită în lei, pe contul de destinație (de exemplu 371 pentru mărfuri) în corespondență cu furnizorul (401); și, separat, TVA calculată la cota corespunzătoare bunului, înregistrată simultan pe 4426 (deductibilă) și 4427 (colectată) — nu apare nicio sumă de plătit efectiv către furnizor pentru TVA, pentru că el nu a facturat-o.

## Ce se greșește în practică

- Se înregistrează doar valoarea bunurilor, fără linia de TVA prin 4426=4427, ca și cum operațiunea ar fi scutită sau neimpozabilă — de fapt taxa se autolichidează, nu dispare.
- Se calculează TVA la o cotă "presupusă" sau moștenită dintr-o achiziție anterioară similară, fără să se verifice cota corectă pentru bunul concret.
- Se confundă data facturii furnizorului cu data exigibilității taxei, ignorând regula "cel târziu a 15-a zi a lunii următoare faptului generator" atunci când factura sosește cu întârziere.
- Se omite includerea operațiunii în D390 pentru luna în care taxa a devenit exigibilă, deși formula 4426=4427 a fost înregistrată corect.

## Ce face iConta.eu

La completarea ecranului de achiziție intracomunitară — data, valoarea în lei, codul de TVA al furnizorului, numărul facturii, contul de destinație (sugestie 371), tipul (bunuri/servicii) și cota de TVA — aplicația generează automat cele două linii contabile: valoarea bunurilor pe contul de destinație în corespondență cu furnizorul, și TVA pe formula 4426 = 4427. Cota de TVA nu are valoare implicită, trebuie declarată explicit la fiecare operațiune. Dacă se completează și data faptului generator, exigibilitatea se calculează automat ca minimul dintre data facturii și a 15-a zi a lunii următoare (art. 284); dacă se lasă gol, se folosește data facturii.

[iConta.eu](/)
