---
title: "Comparație: micro vs profit pentru magazinele online"
description: "Condițiile legale de încadrare ca microîntreprindere, relevante pentru un magazin online care se apropie sau depășește plafonul de venituri."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Comparație: micro vs profit pentru magazinele online

Magazinele online au adesea cifre de afaceri care cresc rapid de la un an la altul, ceea ce face din alegerea între impozitul micro și impozitul pe profit o decizie recurentă, nu una făcută o singură dată la înființare. Condițiile de încadrare sunt cumulative — trebuie îndeplinite toate, nu doar plafonul de venituri, la care lumea se gândește de obicei prima.

## Temeiul legal

```
::: ghid-temei
„(1) În sensul prezentului titlu, o microîntreprindere este o persoană juridică română care îndeplinește cumulativ următoarele condiții, la data de 31 decembrie a anului fiscal precedent:
c) a realizat venituri care nu au depășit echivalentul în lei a 100.000 euro. Cursul de schimb pentru determinarea echivalentului în euro este cel valabil la închiderea exercițiului financiar în care s-au înregistrat veniturile;
d) capitalul social al acesteia este deținut de persoane, altele decât statul și unitățile administrativ-teritoriale;
e) nu se află în dizolvare, urmată de lichidare, înregistrată în registrul comerțului sau la instanțele judecătorești, potrivit legii."
— Legea nr. 227/2015 privind Codul fiscal, art. 47 alin. (1) lit. c), d) și e) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::
```

Ce înseamnă asta pentru un magazin online, concret:

- **Plafonul de 100.000 euro se verifică pe cifra de afaceri**, nu pe rulajul total de venituri contabile — o precizare care contează mai ales dacă magazinul are și venituri financiare (de exemplu, diferențe de curs din plățile în valută primite de la platforme de tip marketplace străine).
- **Dacă în cursul anului fiscal un magazin depășește 100.000 euro venituri**, el trece la impozit pe profit **din trimestrul în care a depășit plafonul**, nu retroactiv de la începutul anului și nu abia din anul următor — o regulă frecvent ignorată de firmele cu creștere rapidă, tipică magazinelor online în extindere.
- **Structura de capital** contează: dacă magazinul are ca acționar/asociat statul sau o unitate administrativ-teritorială, nu se poate încadra ca micro, indiferent de venituri — situație rară, dar posibilă în cazul unor parteneriate publice.
- **Firmele aflate în dizolvare/lichidare** nu pot rămâne micro, indiferent de venituri.

Pentru un magazin online tipic, decizia reală de business e alta: impozitul micro (procent din venituri) poate fi mai mare decât impozitul pe profit (16% din profit) atunci când marjele sunt mici și volumul de vânzări e mare — o comparație pe care fiecare magazin trebuie s-o facă pe cifrele proprii, nu doar pe încadrarea legală.

## Ce se greșește în practică

- Se compară doar cota de impozitare (micro vs. 16% profit), ignorând baza de calcul complet diferită — micro se aplică la venituri, profit la marjă.
- Se presupune că depășirea plafonului de 100.000 euro schimbă regimul abia din anul fiscal următor — de fapt, schimbarea e imediată, din trimestrul depășirii.
- Se ignoră faptul că veniturile din transferul mijloacelor fixe/terenurilor se adaugă la calculul cifrei de afaceri relevante pentru verificarea plafonului în cursul anului, dacă firma transferă mai mult de un activ din aceeași subgrupă.

## Ce face iConta.eu

Testele proprii (`core/test_a8_micro_baza.py`) confirmă funcționalitatea de verificare a condițiilor de încadrare micro; simularea comparativă „ce ar ieși ca impozit micro vs. ca impozit pe profit", pentru un magazin care ezită între cele două regimuri, **nu a fost găsită** ca funcționalitate dedicată în `core/` — aplicația calculează corect impozitul aferent regimului deja ales/aplicabil, dar decizia strategică de a opta pentru un regim sau altul rămâne o analiză pe care contabilul o face separat, pe cifrele reale ale firmei.

[iConta.eu](/)
