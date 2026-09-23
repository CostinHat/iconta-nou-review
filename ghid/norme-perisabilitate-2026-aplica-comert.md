---
title: "Norme de perisabilitate 2026: cum se aplică la comerț"
description: Normele de perisabilitate din HG 831/2004 se aplică la mărfuri în procesul de comercializare, cu un coeficient pe grupă de produse aplicat la valoarea intrărilor — coeficientul se caută în anexa hotărârii, nu se calculează.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Norme de perisabilitate 2026: cum se aplică la comerț

Normele privind limitele admisibile de perisabilitate vizează explicit mărfurile aflate în procesul de comercializare — vânzarea cu ridicata sau cu amănuntul, cu manipulare și depozitare specifice — nu producția sau prepararea de bunuri. Aplicarea lor înseamnă un coeficient pe grupă de marfă, stabilit prin anexă, aplicat la valoarea intrărilor din perioadă.

## Temeiul legal

::: ghid-temei
„HOTĂRÂRE nr. 831 din 27 mai 2004 pentru aprobarea Normelor privind limitele admisibile de perisabilitate la mărfuri în procesul de comercializare" — Publicat în Monitorul Oficial nr. 522 din 10 iunie 2004.

„Art. 1: Se aprobă Normele privind limitele admisibile de perisabilitate la mărfuri în procesul de comercializare, prevăzute în anexa care face parte integrantă din prezenta hotărâre."

*(HG nr. 831/2004, titlu și art. 1)*
:::

## Mecanismul de aplicare

1. **Se identifică grupa de marfă** din anexele hotărârii (de exemplu băuturi, legume-fructe, panificație etc.) — coeficientul de perisabilitate diferă pe grupă și trebuie verificat direct în anexa publicată în Monitorul Oficial, nu presupus sau reținut din memorie.
2. **Se aplică procentul la valoarea intrărilor** din perioadă (nu la stocul final, nu la valoarea pierderii constatate).
3. **Se compară pierderea constatată cu limita astfel calculată** — partea din limită e deductibilă fără ajustare de TVA; partea peste limită e nedeductibilă, cu ajustare de TVA aferentă (cu excepția degradării calitative dovedite prin distrugere).
4. **Se documentează**: verificare faptică (inventariere, recepție sau predare de gestiune), aprobarea administratorului, proces-verbal — condiții cerute pentru ca operațiunea să fie recunoscută ca perisabilitate, nu doar ca o cheltuială oarecare.

## Ce se greșește în practică

- Se aplică regimul HG 831/2004 la materii prime consumate în procesul de preparare (bucătărie, producție) — titlul hotărârii vizează explicit „mărfuri în procesul de comercializare", nu materii prime transformate.
- Se folosește un procent de perisabilitate „memorat" dintr-un alt an sau dintr-o altă grupă de marfă, fără verificare în anexa curentă.
- Se omit condițiile documentare, deși calculul valoric ar fi corect.

## Ce face iConta.eu

Ecranul Operațiuni speciale > „Perisabilități și scăzăminte" primește procentul de limită ca și câmp numeric liber, completat de contabil — aplicația nu are o listă de grupe de mărfuri legată de anexele HG 831/2004 și nu selectează automat coeficientul. Motorul (`core/perisabilitati.py`) calculează apoi limita, separarea deductibil/nedeductibil și eventuala ajustare de TVA, pe baza procentului astfel introdus.

[iConta.eu](/)
