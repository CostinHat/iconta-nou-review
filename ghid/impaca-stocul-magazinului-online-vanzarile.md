---
title: "Cum se împacă stocul magazinului online cu vânzările"
description: "Ce obligă legea inventarierii atunci când stocul scriptic dintr-un magazin online nu mai corespunde cu vânzările efectiv înregistrate."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum se împacă stocul magazinului online cu vânzările

Un magazin online acumulează, în timp, diferențe între stocul „scriptic" (ce spune contabilitatea că mai există) și stocul faptic real — retururi neînregistrate corect, produse deteriorate, erori de sincronizare cu platforma de vânzare. Legea nu lasă aceste diferențe la latitudinea firmei: le tratează prin mecanismul general al inventarierii.

## Temeiul legal

::: ghid-temei
„2. - (1) [În temeiul prevederilor Legii contabilității nr. 82/1991, republicată,] entitățile au obligația să efectueze inventarierea elementelor de natura activelor, datoriilor și capitalurilor proprii deținute, la începutul activității, cel puțin o dată în cursul exercițiului financiar pe parcursul funcționării lor [...]
4. - (1) Inventarierea anuală a elementelor de natura activelor, datoriilor și capitalurilor proprii se face, de regulă, cu ocazia încheierii exercițiului financiar, avându-se în vedere și specificul activității fiecărei entități."
— OMFP nr. 2861/2009, pct. 2 alin. (1) și pct. 4 alin. (1) (sursă: anaf_surse/omfp_2861_2009.txt)
:::

Ce înseamnă concret pentru un magazin online:

- **Stocul de marfă e un element de natura activelor**, deci intră sub obligația generală de inventariere — cel puțin anual, la închiderea exercițiului financiar, indiferent cât de bine „pare" sincronizat stocul din platforma de vânzare cu evidența contabilă.
- „Împăcarea" stocului cu vânzările nu e o simplă comparație de cifre — e un proces formal: numărare faptică, comparare cu soldul scriptic, consemnare a diferențelor (plusuri sau minusuri) și, unde e cazul, regularizare contabilă.
- Diferențele constatate la inventariere trebuie **justificate**, nu doar corectate silențios — un plus sau un minus de stoc care nu poate fi explicat (retur, deteriorare, eroare de sincronizare) rămâne un semnal de risc, atât operațional, cât și fiscal.

## Ce se greșește în practică

- Se corectează stocul din sistemul de gestiune direct la valoarea din platforma de vânzare online, fără o inventariere faptică reală — diferența rămâne nejustificată, doar „ascunsă" în date.
- Se presupune că sincronizarea automată dintre magazinul online și evidența de stoc elimină nevoia de inventariere fizică — sincronizarea tehnică nu înlocuiește obligația legală de numărare faptică periodică.
- Se ignoră retururile procesate direct de platforma de curierat/marketplace, fără să fie reflectate corect în stocul intern — apar diferențe greu de explicat ulterior, la inventarierea anuală.

## Ce face iConta.eu

Verificat în cod: iConta.eu are o funcționalitate de inventariere (`core/stocuri_cv_api.py`, funcția `inventar`) care compară, articol cu articol, cantitatea faptică introdusă cu fișa de magazie construită din mișcările înregistrate, la cost mediu ponderat (CMP), și generează automat notele contabile de regularizare pentru plusuri (371=607) sau minusuri (607=371), cu temei citat din OMFP 1802/2014. Aplicația conține chiar un gard explicit împotriva „inventarierii fără linii" — un inventar fără articole numărate nu e acceptat ca „fără diferențe", pentru că absența numărătorii nu e același lucru cu un rezultat de zero diferențe. Recepția cantitativă a facturilor de marfă primite e de asemenea automatizată, printr-un modul de reconciliere factură-stoc.

[iConta.eu](/)
