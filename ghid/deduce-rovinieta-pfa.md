---
title: "Pot deduce rovinieta la PFA?"
description: "Condițiile în care rovinieta este cheltuială deductibilă pentru un PFA care folosește un autoturism în activitatea independentă."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Pot deduce rovinieta la PFA?

Rovinieta e o cheltuială legată de folosirea unui autovehicul pe drumurile publice, deci deductibilitatea ei la PFA urmează aceeași logică precum orice altă cheltuială cu autoturismul: se deduce dacă vehiculul e afectat activității independente, cu documentele care dovedesc asta, și în limitele generale aplicabile cheltuielilor cu autoturismele.

## Temeiul legal

::: ghid-temei
„Condițiile generale pe care trebuie să le îndeplinească cheltuielile efectuate în scopul desfășurării activității independente, pentru a putea fi deduse, în funcție de natura acestora, sunt: a) să fie efectuate în cadrul activităților independente, justificate prin documente [...] j) cheltuielile de funcționare, întreținere și reparații, aferente autoturismelor folosite de contribuabil sau membru asociat sunt deductibile limitat potrivit alin. (7) lit. k), la cel mult un singur autoturism aferent fiecărei persoane."
— Legea 227/2015, art. 68 alin. (4) lit. a) și alin. (5) lit. j) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Ce rezultă practic pentru rovinietă la PFA:

- Rovinieta e o cheltuială de **funcționare** a autoturismului (alături de combustibil, revizii, asigurare RCA), deci intră sub incidența literei j) — deductibilă **limitat**, pentru cel mult un singur autoturism pe persoană, potrivit regulilor de la alin. (7) lit. k) din același articol.
- Condiția de bază rămâne cea generală: autoturismul trebuie să fie **afectat activității** (înregistrat ca bun al afacerii, folosit dovedit în scop profesional), nu doar deținut de titularul PFA.
- Dacă autoturismul are utilizare mixtă (personală și profesională), rovinieta se deduce doar pentru partea aferentă activității, la fel ca orice altă cheltuială cu utilizare mixtă (art. 68 alin. (5) lit. i)).
- Documentul justificativ e chitanța/dovada de plată a rovinietei pe numărul de înmatriculare al autoturismului afectat activității — legată, ca și celelalte cheltuieli auto, de foaia de parcurs sau de alt document care arată folosirea în scop profesional.

## Ce se greșește în practică

- Se deduce rovinieta pentru mai multe autoturisme ale aceleiași persoane, deși legea limitează deducerea cheltuielilor de funcționare la un singur autoturism pe persoană.
- Se deduce integral rovinieta unui autoturism cu utilizare evident mixtă (personală și de afacere), fără nicio proporționare sau documentare a procentului de utilizare profesională.
- Se presupune că rovinieta e „taxă", deci automat deductibilă integral ca orice impozit sau taxă datorată statului — de fapt e o cheltuială de funcționare a autoturismului, supusă acelorași limitări ca celelalte cheltuieli auto.

## Ce face iConta.eu

Pentru PFA, iConta.eu permite înregistrarea plăților în registrul de încasări și plăți și clasificarea lor pe categorii de deductibilitate — deductibilă, limitată sau nedeductibilă (`core/rip_api.py`, categoria `cheltuiala_limitata`). La data acestui ghid, aplicația **nu aplică automat plafonul „un singur autoturism pe persoană"** din art. 68 alin. (5) lit. j) și nu verifică dacă rovinieta introdusă corespunde unui vehicul deja afectat activității — încadrarea corectă a cheltuielii rămâne responsabilitatea celui care operează în cont.

[iConta.eu](/)
