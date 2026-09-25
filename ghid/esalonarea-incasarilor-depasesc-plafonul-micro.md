---
title: "Eșalonarea încasărilor ca să nu depășesc plafonul micro"
description: "De ce amânarea încasării facturilor nu ajută la evitarea depășirii plafonului de 100.000 euro pentru regimul micro, pentru că plafonul se verifică pe venituri, nu pe încasări."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Eșalonarea încasărilor ca să nu depășesc plafonul micro

O idee frecventă la finalul anului: dacă firma se apropie de plafonul de venituri pentru regimul micro, se amână încasarea unor facturi pentru anul următor, ca să nu „intre" venitul în anul curent. Problema e că plafonul micro nu se calculează pe încasări, ci pe venituri recunoscute contabil — adică pe facturare, nu pe plată.

## Temeiul legal

::: ghid-temei
„c) a realizat venituri care nu au depășit echivalentul în lei a 100.000 euro. Cursul de schimb pentru determinarea echivalentului în euro este cel valabil la închiderea exercițiului financiar în care s-au înregistrat veniturile"
— Legea 227/2015 (Codul fiscal), art. 47 alin. (1) lit. c) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Ce înseamnă asta, concret:

- Plafonul de 100.000 euro (valabil pentru verificarea condițiilor de microîntreprindere inclusiv pentru anul fiscal 2026, conform OUG 8/2026) se verifică pe **veniturile înregistrate**, adică pe cifra de afaceri contabilă, nu pe sumele efectiv încasate.
- Dacă în cursul anului o microîntreprindere realizează venituri mai mari de 100.000 euro, ea datorează impozit pe profit **începând cu trimestrul în care s-a depășit limita** (art. 52 alin. 1) — indiferent dacă facturile respective au fost sau nu încasate.
- Amânarea încasării unei facturi deja emise nu mută venitul în anul următor — venitul se recunoaște la livrarea bunului/prestarea serviciului, nu la încasare.

## Ce se greșește în practică

- Se amână emiterea facturilor (nu doar încasarea lor) pentru anul următor, ceea ce poate crea alte probleme — TVA la exigibilitate, corelarea cu contractul, riscul de a nu respecta termenele de facturare legale.
- Se crede greșit că plafonul micro funcționează ca plafonul de TVA la încasare — cele două sunt reguli complet diferite, cu baze de calcul diferite (venituri vs. încasări).
- Se ignoră faptul că depășirea plafonului schimbă regimul fiscal **din trimestrul depășirii**, nu de la 1 ianuarie anul următor — trecerea la impozit pe profit poate fi imediată.

## Ce face iConta.eu

iConta.eu calculează obligațiile fiscale ale regimului micro (D100) pe baza veniturilor introduse de utilizator pentru trimestrul respectiv (`core/d100.py`, funcția `deriva_obligatii`), nu pe baza încasărilor din casă sau bancă. Aplicația nu are, la acest moment, o alertă automată care să semnaleze apropierea de plafonul de 100.000 euro cumulat de la începutul anului — verificarea acestui plafon rămâne o responsabilitate a contabilului, urmărind veniturile cumulate raportate în declarațiile trimestriale.

[iConta.eu](/)
