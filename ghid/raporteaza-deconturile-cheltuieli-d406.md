---
title: "Cum se raportează deconturile de cheltuieli în D406?"
description: "Cum se reflectă avansurile spre decontare și deconturile de cheltuieli ale angajaților în fișierul standard de control fiscal (SAF-T/D406)."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum se raportează deconturile de cheltuieli în D406?

Deconturile de cheltuieli ale angajaților (avansuri spre decontare, justificate ulterior cu bonuri și facturi) nu au o secțiune separată, dedicată, în structura SAF-T — ele intră în fișierul D406 ca orice altă înregistrare contabilă, prin conturile de avansuri și cheltuieli aferente, atâta timp cât documentul justificativ care le susține respectă regula generală a evidenței contabile.

## Temeiul legal

::: ghid-temei
„Articolul 6 (1) Orice operațiune economico-financiară efectuată se consemnează în momentul efectuării ei într-un document care stă la baza înregistrărilor în contabilitate, dobândind astfel calitatea de document justificativ."
— Legea 82/1991 (Legea contabilității), art. 6 alin. (1) (sursă: anaf_surse/legea_82_1991_consolidat.txt)
:::

Ce presupune, concret, raportarea deconturilor în SAF-T:

- Un decont de cheltuieli, odată aprobat, generează înregistrări contabile (descărcarea avansului, recunoașterea cheltuielii pe conturile analitice corespunzătoare) care ajung în `GeneralLedgerEntries`-ul SAF-T-ului la fel ca orice altă tranzacție contabilă a lunii — nu există un tip special de linie SAF-T doar pentru deconturi.
- Avansurile spre decontare intră și sub incidența plafoanelor de numerar din Legea 70/2015: plățile din avansuri spre decontare sunt limitate la 5.000 lei zilnic, per persoană care a primit avansul, iar la data acordării avansului suma intră deja în calculul plafonului zilnic aplicabil.
- Documentele justificative ale decontului (bonuri fiscale, facturi pe numele firmei) rămân baza legală a înregistrării — fără ele, cheltuiala recunoscută din decont riscă recalificarea ca nedeductibilă, indiferent cum apare ea în SAF-T.

## Ce se greșește în practică

- Se așteaptă o secțiune sau un cod special în structura SAF-T pentru deconturile de cheltuieli — acestea se raportează prin conturile contabile obișnuite (avansuri de trezorerie, cheltuieli), nu printr-un tip de document separat.
- Se ignoră plafonul de 5.000 lei zilnic pentru plățile din avansuri spre decontare, tratându-l ca fiind mai permisiv decât plafonul aplicabil altor plăți în numerar.
- Se raportează decontul în perioada în care a fost depus de angajat, nu în perioada în care a fost efectiv aprobat și înregistrat contabil — cele două momente pot să nu coincidă, mai ales la finalul lunii.

## Ce face iConta.eu

iConta.eu oferă un modul de casierie și avansuri de trezorerie, cu contracte de justificare și note cu urmă pentru fiecare operațiune, inclusiv avansurile spre decontare, calculate cu respectarea plafonului de 5.000 lei zilnic din Legea 70/2015. Fișierul SAF-T (D406) generat de aplicație include aceste înregistrări prin conturile contabile aferente, alături de restul evidenței — aplicația **nu are** însă o secțiune separată de raportare „decont de cheltuieli" în SAF-T, pentru că structura oficială ANAF nu prevede una.

[iConta.eu](/)
