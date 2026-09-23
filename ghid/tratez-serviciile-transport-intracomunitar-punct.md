---
title: "Cum tratez serviciile de transport intracomunitar din punct de vedere TVA?"
description: "Regula generală de TVA (locul beneficiarului) aplicabilă serviciilor de transport de marfă prestate/primite în relația cu firme din UE."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum tratez serviciile de transport intracomunitar din punct de vedere TVA?

Serviciile de transport de marfă în relația cu firme din alte state membre UE — fie că le prestezi, fie că le primești — urmează regula generală a serviciilor B2B: locul prestării e considerat la beneficiar, nu la prestator.

## Temeiul legal

::: ghid-temei
CF art. 278 alin. (2): „Locul prestării serviciilor B2B = locul beneficiarului (bază pentru neimpozabilitate în RO + declarare D390 cod S).” (sursă: `cod_fiscal_227_2015_consolidat.txt`, L17303-17420)

CF art. 307 alin. (2): „Taxa este datorată de orice persoană impozabilă… care este beneficiar al serviciilor care au locul prestării în România conform art. 278 alin. (2) și care sunt furnizate de către o persoană impozabilă care nu este stabilită pe teritoriul României…” (sursă: `cod_fiscal_227_2015_consolidat.txt`, L19334-19342)
:::

Dacă **prestezi** un serviciu de transport unei firme din UE cu cod de TVA valid în VIES, factura se emite fără TVA românesc — serviciul e neimpozabil în România, se declară D390 cod P.

Dacă **primești** un serviciu de transport de la un furnizor cu cod de TVA valid într-un alt stat membru UE, firma din România datorează TVA prin taxare inversă (beneficiarul e obligat la plata taxei), cu formula contabilă 4426 = 4427, și declară D390 cod S.

În ambele cazuri, condiția esențială e verificarea, în VIES, a codului de TVA al partenerului — nu doar prezumția că „e din UE”.

## Ce se greșește în practică

- Se aplică regula de transport intracomunitar și unor curse efectuate integral în afara UE sau de către un transportator fără cod de TVA UE — regula descrisă aici e specifică operațiunilor cu parteneri înregistrați în VIES.
- Se confundă regimul serviciilor de transport (art. 278 alin. 2, servicii B2B) cu regimul bunurilor transportate — sunt lucruri diferite; transportul e mereu tratat ca serviciu, indiferent de natura mărfii transportate.
- Se omite declararea D390 pentru serviciile de transport prestate/primite, considerând eronat că doar bunurile intră sub incidența declarației recapitulative.

## Ce face iConta.eu

Pentru servicii de transport prestate unei firme din UE, folosești formularul de vânzare intracomunitară (`vanzare_ic`), tip „servicii”, cu verificare VIES a codului de TVA al clientului la emitere.

Pentru servicii de transport primite de la un furnizor din UE, folosești formularul de achiziție intracomunitară (`achizitie_ic`), tip „servicii”, cu codul de TVA al furnizorului, valoarea și cota TVA aplicabilă. Aplicația calculează taxarea inversă (4426 = 4427) și clasifică automat operațiunea pentru D390 (cod P sau cod S, după caz).

[iConta.eu](/)
