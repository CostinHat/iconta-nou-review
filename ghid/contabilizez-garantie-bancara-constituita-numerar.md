---
title: "Cum contabilizez o garanție bancară constituită în numerar?"
description: "O garanție bancară garantată integral cu bani depuși de firmă e o creanță imobilizată, nu un simplu angajament extrabilanțier — diferența contează contabil."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum contabilizez o garanție bancară constituită în numerar?

Uneori banca nu emite o scrisoare de garanție „pe încrederea" clientului, ci cere ca acesta să depună, în avans, o sumă de bani (cash collateral) care rămâne blocată drept acoperire pentru garanția emisă. Din perspectiva firmei, aici chiar există o mișcare reală de numerar — spre deosebire de o simplă scrisoare de garanție „pe hârtie" — ceea ce schimbă complet tratamentul contabil față de angajamentele extrabilanțiere descrise la alte tipuri de garanții.

## Temeiul legal

::: ghid-temei
„Contul 267 «Creanțe imobilizate» [...] Cu ajutorul acestui cont se ține evidența creanțelor imobilizate sub forma împrumuturilor acordate pe termen lung altor entități, a altor creanțe imobilizate, cum sunt depozite, garanții și cauțiuni depuse de entitate la terți, precum și a obligațiunilor achiziționate cu ocazia emisiunilor de obligațiuni efectuate de terți, care urmează a fi deținute pe o perioadă mai mare de un an. Contul 267 «Creanțe imobilizate» este un cont de activ."
— OMFP 1802/2014 pentru aprobarea Reglementărilor contabile privind situațiile financiare anuale individuale și situațiile financiare anuale consolidate, Clasa 2 „Conturi de imobilizări", Contul 267 (sursă: anaf_surse/omfp_1802_2014_reglementari_consolidat.txt)
:::

- Banii depuși de firmă drept colateral pentru o garanție bancară nu ies din patrimoniul ei — devin o **creanță** (un activ), pentru că firma are dreptul să-i recupereze la eliberarea garanției. Contabil, asta e complet diferit de o simplă evidență extrabilanțieră (801/802) folosită pentru garanțiile-angajament, fără mutare de bani.
- Textul citat vizează explicit depozitele/garanțiile deținute pe **o perioadă mai mare de un an** — pentru garanții constituite pe termen scurt, practica uzuală e să rămână evidențiate tot ca o creanță, dar clasificată pe termen scurt, nu în contul 267 destinat imobilizărilor financiare pe termen lung.
- Contul e de **activ**: crește la depunerea garanției (ieșire de bani din contul curent, intrare de creanță) și scade la restituirea ei (intrare de bani înapoi în cont).

## Ce se greșește în practică

- Se tratează garanția în numerar la fel ca o scrisoare de garanție „pe hârtie" — adică se înregistrează doar extrabilanțier (801/802), deși aici banii chiar au ieșit din conturile firmei și trebuie urmăriți ca o creanță reală.
- Se înregistrează suma direct ca o cheltuială, deși e recuperabilă.
- Se pierde din vedere reclasificarea garanției pe termen scurt vs. lung, dacă termenul de eliberare se apropie de un an.

## Ce face iConta.eu

Verificat în cod: funcția de garanții existentă în iConta.eu (`core/credite.py`, `nota_garantie`) tratează exclusiv cazul angajamentului extrabilanțier (8011/8021=891), fără mutare efectivă de numerar. Pentru cazul concret din acest ghid — bani chiar depuși de firmă drept colateral, care devin o creanță imobilizată — iConta.eu **nu are** o funcție dedicată care să genereze automat nota corespunzătoare (ieșire de trezorerie + creanță). Operațiunea trebuie înregistrată manual, printr-o notă contabilă obișnuită, cu contul de creanță potrivit termenului garanției.

[iConta.eu](/)
