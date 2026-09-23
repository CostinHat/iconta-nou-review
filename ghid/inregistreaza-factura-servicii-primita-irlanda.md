---
title: "Cum se înregistrează o factură de servicii primită din Irlanda?"
description: Un serviciu cumpărat de la un prestator din Irlanda, pentru o firmă din România, e impozabil în România — locul prestării e locul beneficiarului —, iar TVA se autolichidează prin 4426 = 4427, declarat în D390 cu clasificare manuală.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum se înregistrează o factură de servicii primită din Irlanda?

Pentru serviciile B2B intracomunitare, regula de bază schimbă complet locul de impozitare: nu contează unde e stabilit prestatorul (în acest caz, Irlanda), ci unde e stabilit beneficiarul serviciului. Dacă beneficiarul e o firmă din România, serviciul e impozabil în România, iar TVA se calculează și se înregistrează aici, prin taxare inversă.

## Temeiul legal

::: ghid-temei
Antetul modulului de operațiuni intracomunitare citează, printre temeiurile motorului de calcul, art. 278 alin. (2) (servicii B2B, locul beneficiarului) și art. 308-309 (obligat la plată = beneficiarul la AIC/servicii primite) — verificat în dosarul F050, `core/intracomunitar.py`.
:::

::: ghid-temei
HG 1/2016, norme la CF art. 331, pct. 109 alin. (1): „beneficiarul înregistrează… suma taxei aferente în următoarea formulă contabilă: 4426 = 4427. Prevederile acestui alineat sunt valabile pentru orice alte situații în care se aplică taxarea inversă.”
:::

Fiindcă locul prestării e locul beneficiarului (firma din România), serviciul cumpărat din Irlanda e neimpozabil în Irlanda și impozabil în România. Prestatorul irlandez, corect, nu facturează TVA irlandez pe acest serviciu — firma din România e cea obligată la plata taxei, prin autolichidare, la cota corespunzătoare serviciului. Servicii tipice cumpărate din Irlanda intră frecvent în această categorie — de exemplu servicii digitale sau de publicitate online — dar regula se aplică identic, indiferent de natura exactă a serviciului.

## Ce se greșește în practică

- Se primește o factură cu TVA irlandez pe ea și se acceptă ca atare, fără să se clarifice cu prestatorul că locul prestării e România.
- Se tratează serviciul ca pe o achiziție de bunuri intracomunitară, la nivel de clasificare în D390 — sunt tipuri de operațiune diferite, cu coduri distincte.
- Se omite declararea în D390 a achiziției de servicii, considerând (greșit) că formula contabilă 4426=4427 acoperă și obligația declarativă.

## Ce face iConta.eu

Ecranul de achiziție intracomunitară permite selectarea tipului „servicii", alături de codul de TVA al furnizorului irlandez (prefix „IE"), data, valoarea în lei și cota de TVA aplicabilă serviciului, fără valoare implicită. Aplicația generează automat formula 4426 = 4427 pentru TVA. Spre deosebire de achizițiile de bunuri, care se mapează automat în D390, achizițiile de servicii intracomunitare necesită clasificare manuală, printr-un panou dedicat din aplicație, pentru a fi declarate corect.

[iConta.eu](/)
