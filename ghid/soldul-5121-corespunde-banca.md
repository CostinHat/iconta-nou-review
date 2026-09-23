---
title: "Ce fac dacă soldul din 5121 nu corespunde cu banca?"
description: Reconcilierea din iConta.eu potrivește linii individuale de extras cu facturi, nu solduri — verificarea soldului contului 5121 față de extras e o operațiune separată, de inventariere, pe care trebuie să o faci manual, urmărind cauzele descrise mai jos.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Ce fac dacă soldul din 5121 nu corespunde cu banca?

Modulul de reconciliere bancară din iConta.eu potrivește fiecare linie din extras cu facturile deschise ale unui partener — el nu calculează și nu compară niciodată soldul total al contului 5121 cu soldul din extras. Diferența de sold trebuie deci investigată separat, urmărind cauzele tehnice cele mai frecvente.

## Temeiul legal

::: ghid-temei
„Disponibilitățile aflate în conturi la bănci [...] se inventariază prin confruntarea soldurilor din extrasele de cont emise de acestea cu cele din contabilitatea entității." — OMFP nr. 2861/2009, pct. 29 alin. (2)
:::

Norma descrie confruntarea soldurilor ca operațiune de **inventariere**, nu ca procedură lunară obligatorie sub acest nume — disciplina de verificare frecventă a înregistrărilor se sprijină, separat, pe obligația din Legea contabilității nr. 82/1991, art. 22, de a întocmi lunar balanța de verificare.

## Cauze frecvente ale diferenței

Când soldul din 5121 nu corespunde cu soldul din extras, cauza e aproape întotdeauna una din următoarele:

- **Linii de extras nepotrivite sau neprocesate** — linii rămase pe stare „necontat" (fără potrivire găsită, cu potrivire parțială sau nou-importate) nu au generat notă contabilă, deci suma lor lipsește din 5121.
- **Linii marcate „ignorate"** — au fost excluse explicit din contabilizare (de exemplu, transferuri interne), dar dacă ignorarea a fost greșită, operațiunea reală lipsește din 5121.
- **Reimportarea aceluiași extras** — sistemul nu verifică duplicate la import; reimportarea unui fișier deja încărcat (sau a unui interval suprapus) creează linii duble, care, dacă sunt contate, dublează sume în 5121.
- **Format de extras necunoscut** — parserul de extrase e validat pe formatul unei bănci de referință; un extras cu format diferit poate fi citit incomplet sau greșit.

## Ce se greșește în practică

- Se presupune că orice diferență de sold e o eroare de contabilizare, fără să se verifice mai întâi dacă există linii de extras rămase necontate sau ignorate.
- Se reimportă extrasul „ca să fie sigur" fără să se verifice întâi dacă liniile există deja — riscul e dublarea sumelor, nu corectarea lor.
- Se face confruntarea soldurilor o singură dată, la sfârșit de an, deși erorile se acumulează lunar și devin mai greu de urmărit cu timpul.

## Ce face iConta.eu

iConta.eu nu are un instrument dedicat care compară automat soldul contului 5121 cu soldul din extrasul bancar la o dată — reconcilierea acoperă potrivirea pe linie (extras ↔ facturi), nu verificarea de sold. Ecranul Bancă îți arată însă, per linie, starea fiecărei operațiuni (necontată, contată, ignorată), ceea ce te ajută să identifici rapid liniile care lipsesc din contabilitate. Verificarea propriu-zisă a soldului 5121 față de extras rămâne o operațiune manuală, sprijinită de balanța de verificare.

[iConta.eu](/)
