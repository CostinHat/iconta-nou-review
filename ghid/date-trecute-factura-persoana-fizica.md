---
title: "Ce date trebuie trecute în e-Factura pentru o persoană fizică?"
description: "Regula RO e-Factura pentru relația B2C: identificarea beneficiarului persoană fizică se face prin codul numeric personal sau, în lipsa lui, printr-un cod convențional de 13 zerouri."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Ce date trebuie trecute în e-Factura pentru o persoană fizică?

Spre deosebire de facturile către alte firme (B2B), unde identificarea se face prin CUI, facturile către persoane fizice ridică o întrebare specifică: ce cod de identificare fiscală se trece, dacă persoana nu are (sau nu vrea să comunice) un CIF? Legea are un răspuns exact.

## Temeiul legal

::: ghid-temei
„Livrările de bunuri/Prestările de servicii efectuate către o persoană fizică care nu se identifică în relația cu furnizorul/prestatorul prin niciun cod de identificare fiscală sau optează să se identifice prin codul numeric personal se consideră efectuate în relația B2C. Dacă beneficiarul, persoană fizică, nu se identifică prin niciun cod de identificare fiscală, facturile se emit utilizând un cod format din 13 cifre de zero în locul codului de identificare fiscală a beneficiarului."
— OUG nr. 120/2021, art. 10^1 alin. (3), astfel cum a fost modificat prin OUG nr. 138/2024 (sursă: anaf_surse/oug_138_2024.txt)
:::

Ce rezultă concret pentru datele obligatorii ale unei facturi electronice către o persoană fizică:

- Dacă persoana fizică **optează** să se identifice cu **codul numeric personal (CNP)**, acesta se trece în factura electronică în locul codului de identificare fiscală.
- Dacă persoana fizică **nu se identifică prin niciun cod** de identificare fiscală (nici CNP, nici altul), factura se emite folosind un **cod convențional de 13 cifre de zero** („0000000000000") în locul codului de identificare fiscală a beneficiarului — nu se lasă câmpul necompletat.
- Restul câmpurilor obligatorii ale facturii (denumire/nume beneficiar, adresă, descrierea bunurilor/serviciilor, valori, TVA) rămân cele generale, aplicabile oricărei facturi, conform art. 319 din Codul fiscal.
- Excepție: bonurile fiscale emise conform OUG 28/1999, care îndeplinesc condițiile unei facturi simplificate, nu intră sub această obligație de transmitere prin RO e-Factura.

## Ce se greșește în practică

- Se lasă câmpul de identificare a beneficiarului gol sau se completează cu date incorecte, în loc să se folosească fie CNP-ul (dacă persoana îl comunică voluntar), fie codul convențional de 13 zerouri.
- Se solicită insistent CNP-ul persoanei fizice, deși legea spune explicit că declararea lui e opțională din partea beneficiarului — furnizorul nu poate condiționa emiterea facturii de comunicarea CNP-ului.
- Se confundă obligația de identificare fiscală (CNP sau cod convențional) cu datele de contact ale clientului — sunt cerințe diferite, ambele necesare pe factură, dar reglementate separat.

## Ce face iConta.eu

La data acestui ghid, iConta.eu **nu captează încă CNP-ul beneficiarului persoană fizică** pe factură — motorul intern de generare a facturilor electronice e construit în jurul identificării prin cod fiscal (CUI), specific relației B2B. Pentru facturile către persoane fizice, aplicarea codului convențional de 13 zerouri (sau, opțional, a CNP-ului, dacă e comunicat) rămâne, la acest moment, o completare pe care utilizatorul trebuie să o asigure manual.

[iConta.eu](/)
