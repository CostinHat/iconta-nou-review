---
title: "Când este un provizion deductibil fiscal?"
description: "Diferența dintre categoriile de provizioane recunoscute contabil, neexhaustive, și lista limitativă a celor deductibile fiscal."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Când este un provizion deductibil fiscal?

Contabil, provizioanele se constituie pentru orice datorie incertă, generată de un eveniment anterior și estimabilă credibil — o listă de categorii deschisă. Fiscal, dreptul de deducere e mult mai restrâns.

## Temeiul legal

::: ghid-temei
„Contribuabilul are dreptul la deducerea rezervelor și provizioanelor/ajustărilor pentru depreciere, numai în conformitate cu prezentul articol, astfel:” — Cod fiscal, art. 26 alin. (1)
:::

::: ghid-temei
„provizioanele pentru garanții de bună execuție acordate clienților. […] se deduc trimestrial/anual numai pentru bunurile livrate, lucrările executate și serviciile prestate în cursul trimestrului/anului respectiv pentru care se acordă garanție în perioadele următoare, la nivelul cotelor prevăzute în convențiile încheiate sau la nivelul procentelor de garantare prevăzut în tariful lucrărilor executate ori serviciilor prestate” — Cod fiscal, art. 26 alin. (1) lit. b)
:::

::: ghid-temei
„Provizioanele se constituie pentru elemente cum sunt: a) litigii, amenzi și penalități, despăgubiri, daune și alte datorii incerte; b) cheltuielile legate de activitatea de service în perioada de garanție și alte cheltuieli privind garanția acordată clienților; c) dezafectare imobilizări corporale și alte acțiuni similare legate de acestea; d) acțiunile de restructurare; e) pensii și obligații similare; f) impozite; g) terminarea contractului de muncă; h) prime ce urmează a se acorda personalului în funcție de profitul realizat […]” — OMFP 1802/2014, pct. 377 alin. (1)
:::

Textul OMFP 1802/2014 citat mai sus enumeră categoriile de provizioane cu formula „elemente **cum sunt**” — deci lista nu este limitativă; ea acoperă și alte situații similare, dincolo de cele opt puncte enumerate explicit. Fiscal, situația e inversă: art. 26 alin. (1) din Codul fiscal acordă dreptul de deducere „numai în conformitate cu prezentul articol” — o enumerare limitativă. Dintre toate categoriile de provizioane recunoscute contabil, **singura** deductibilă fiscal este cea pentru garanții de bună execuție acordate clienților (lit. b), și doar la nivelul cotelor din convenții sau al procentelor de garantare din tarif. Toate celelalte — litigii, dezafectare, restructurare, impozite, pensii, prime sau orice altă categorie constituită contabil conform OMFP — rămân nedeductibile, oricât de corect ar fi constituite din punct de vedere contabil.

## Ce se greșește în practică

Greșeala tipică este confuzia dintre „recunoscut contabil” (orice provizion constituit conform OMFP 1802/2014, indiferent de categorie) și „deductibil fiscal” (doar garanțiile de bună execuție, conform art. 26 alin. (1) lit. b) din Codul fiscal). Tratarea tuturor provizioanelor ca deductibile de la constituire duce la o bază impozabilă subevaluată.

## Ce face iConta.eu

Motorul F071 acceptă mai multe categorii de provizioane (litigii, garanții, dezafectare, restructurare, impozite, altele), dar marchează deductibil fiscal **doar** provizionul de tip „garanții” (cont 1512) — toate celelalte categorii sunt generate explicit ca nedeductibile, indiferent de nume sau de cât de bine justificată e constituirea lor contabilă.

[iConta.eu](/)
