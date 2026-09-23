---
title: "Cum se contabilizează costurile apărute în perioada de garanție a unei construcții?"
description: "Provizionul pentru garanții de bună execuție (1512) e singura categorie de provizion 151x deductibilă fiscal — constituit la nivelul cotelor din contract sau al procentelor de garantare din tarif, la data recepției lucrării."
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum se contabilizează costurile apărute în perioada de garanție a unei construcții?

Costurile așteptate pe perioada de garanție a unei lucrări de construcții se contabilizează printr-un provizion pentru garanții de bună execuție — singura categorie de provizioane pentru care legea acordă deducere fiscală, spre deosebire de restul provizioanelor (litigii, restructurare, dezafectare etc.), care rămân nedeductibile.

## Temeiul legal

::: ghid-temei
„Contribuabilul are dreptul la deducerea rezervelor și provizioanelor/ajustărilor pentru depreciere, numai în conformitate cu prezentul articol, astfel: [...] b) provizioanele pentru garanții de bună execuție acordate clienților. [...] se deduc trimestrial/anual numai pentru bunurile livrate, lucrările executate și serviciile prestate în cursul trimestrului/anului respectiv pentru care se acordă garanție în perioadele următoare, la nivelul cotelor prevăzute în convențiile încheiate sau la nivelul procentelor de garantare prevăzut în tariful lucrărilor executate ori serviciilor prestate."

*(Codul fiscal — Legea nr. 227/2015, art. 26 alin. (1) lit. b))*
:::

## Constituirea provizionului, la recepția lucrării

Provizionul se constituie trimestrial sau anual, doar pentru lucrările executate în perioada respectivă pentru care se acordă garanție ulterior — nivelul lui vine fie din cota prevăzută în convenția/contractul cu clientul, fie din procentul de garantare din tariful lucrării, nu dintr-o estimare liberă. Nota contabilă e 6812=1512, iar cheltuiala de constituire e deductibilă, spre deosebire de celelalte categorii de provizioane (litigii — 1511, dezafectare — 1513, restructurare — 1514, impozite — 1516, altele — 1518), pe care legea nu le include la art. 26 alin. (1) lit. b).

## Reluarea provizionului

Pe măsură ce garanția expiră sau costurile efective de service/reparație din perioada de garanție sunt acoperite, provizionul se reia (151x=7812) — venitul din reluare urmează regula simetrică de la art. 23 lit. d): dacă provizionul a fost dedus la constituire, reluarea e venit impozabil.

## Ce se greșește în practică

- Se constituie provizionul la o valoare estimată liber, fără legătură cu cotele din contract sau cu procentele de garantare din tariful lucrării.
- Se constituie provizion pentru lucrări care nu au fost încă recepționate/executate în perioada respectivă, deși legea îl leagă explicit de lucrările „executate în cursul trimestrului/anului".
- Se confundă provizionul pentru garanții (1512, singurul deductibil) cu un provizion pentru riscuri generale de construcție (fără temei la art. 26).

## Ce face iConta.eu

`nota_provizion(suma, tip="garantii", actiune)` din `core/provizioane.py` generează notele 6812=1512 (constituire) / 1512=7812 (reluare), marcate explicit ca deductibile în cod — singura categorie din dicționarul `PROVIZIOANE` cu acest tratament. Aplicația nu calculează automat suma provizionului (cota din contract sau procentul de garantare din tarif) — aceasta se introduce de contabil, ca parametru de intrare, iar costurile efective de service din perioada de garanție se înregistrează separat, prin cheltuielile obișnuite ale firmei.

[iConta.eu](/)
