---
title: Cum se declară serviciile SaaS către clienți din alte state UE?
description: O firmă din România care prestează servicii SaaS/software către o firmă înregistrată în scop de TVA în alt stat membru UE raportează operațiunea cu codul P în D390, dar numai dacă factura este marcată explicit ca „servicii", altfel aplicația o clasifică implicit ca livrare de bunuri (L).
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Cum se declară serviciile SaaS către clienți din alte state UE?

Firmele care vând abonamente SaaS sau licențe software unor clienți business din alte state UE trebuie să raporteze aceste venituri în D390, dar cu o capcană tehnică des întâlnită: dacă factura nu e marcată explicit ca serviciu, ea poate ajunge greșit clasificată drept livrare de bunuri.

## Temeiul legal

::: ghid-temei
**Art. 278 alin. (2)**: „Locul de prestare a serviciilor către o persoană impozabilă care acționează ca atare este locul unde respectiva persoană care primește serviciile își are stabilit sediul activității sale economice. [...]"

**OPANAF 705/2020, anexa 2**: „d) «Prestări intracomunitare de servicii» - se înscrie suma totală a prestărilor de servicii pentru care se aplică prevederile art. 278 alin. (2) din Codul fiscal, altele decât cele scutite de TVA în statul membru în care acestea sunt impozabile, pe fiecare client în parte, stabilit în Uniunea Europeană, pentru care exigibilitatea taxei ia naștere în luna calendaristică respectivă. Nu vor fi declarate prestările de servicii prevăzute la art. 278 alin. (2) din Codul fiscal dacă beneficiarul serviciului este o persoană impozabilă care nu este stabilită pe teritoriul Uniunii Europene;"
:::

## Regula B2B și codul P

Pentru servicii SaaS vândute unei firme (B2B) dintr-un alt stat membru UE, locul prestării e la sediul clientului (art. 278 alin. (2)) — deci operațiunea se raportează în D390 cu codul **P** (prestări intracomunitare de servicii), nu cu TVA colectat în România. Condiția esențială: clientul trebuie să fie stabilit **în Uniunea Europeană** și înregistrat valid în scopuri de TVA acolo. Dacă abonatul SaaS e stabilit în afara UE, operațiunea nu intră deloc în D390.

Capcana tehnică ține de modul în care factura e clasificată: implicit, orice factură emisă e tratată ca livrare de bunuri (cod L), nu ca prestare de servicii (cod P). Pentru ca o factură SaaS să ajungă corect ca P, trebuie fie marcată explicit ca „servicii" la introducere, fie reclasificată manual în ecranul D390 — altfel apare greșit alături de livrările de bunuri.

::: ghid-exemplu
Firmă românească de software emite o factură de abonament SaaS către o firmă din Polonia, înregistrată în scop de TVA acolo. Dacă factura e marcată corect ca „servicii", operațiunea apare automat cu codul P în D390 pentru luna facturării. Dacă nu e marcată, aceeași factură apare implicit ca livrare de bunuri (L) — clasificare greșită, care trebuie corectată manual de contabil în ecranul D390.
:::

## Ce se greșește în practică

- Se emit facturile SaaS fără să se marcheze explicit natura de „serviciu", iar operațiunea rămâne clasificată implicit ca bunuri (L).
- Se raportează ca P și abonamente către clienți din afara UE (de ex. SUA, UK ca regulă generală), deși aceștia sunt excluși explicit din D390.
- Se confundă locul prestării (sediul clientului, art. 278 alin. (2)) cu locul unde e găzduit serverul sau platforma SaaS — irelevant pentru D390.
- Nu se verifică periodic validitatea codului de TVA al clientului UE, deși e un abonament recurent, lunar.

## Ce face iConta.eu

Direcția documentului (factură emisă) admite doar codurile L, T, P, R — niciodată A sau S; reclasificarea manuală a unei facturi emise nu poate produce un cod „de achiziție". Implicit, orice factură emisă e tratată ca bunuri (cod L). Dacă pe factură există câmpul „axa" marcat explicit ca „servicii", tipul devine automat P și reclasificarea manuală nu mai are ce suprascrie. Dacă axa lipsește, factura rămâne cu clasificarea implicită L, iar contabilul trebuie să o reclasifice manual în P din ecranul D390 (`reclasificari`).

[iConta.eu](/)
