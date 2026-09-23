---
title: "Greșeala de a nu valida codul de TVA al partenerului UE"
description: "Ce se întâmplă când o operațiune intracomunitară se tratează ca scutită/neimpozabilă fără verificare VIES a codului de TVA al partenerului."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Greșeala de a nu valida codul de TVA al partenerului UE

Una dintre cele mai frecvente greșeli la operațiunile intracomunitare este tratarea unei facturi ca scutită de TVA (livrare de bunuri) sau neimpozabilă (servicii B2B) fără verificarea efectivă, în VIES, a codului de TVA al partenerului.

## Temeiul legal

::: ghid-temei
CF art. 294 alin. (2) lit. a): „Scutire LIC cu drept de deducere — condiții: cod TVA valid al cumpărătorului comunicat furnizorului + dovada transportului în alt SM.” (sursă: `intracomunitar.py`, docstring)

CF art. 278 alin. (2): „Locul prestării serviciilor B2B = locul beneficiarului (bază pentru neimpozabilitate în RO + declarare D390 cod S).” (sursă: `cod_fiscal_227_2015_consolidat.txt`, L17303-17420)
:::

Legea nu scutește o operațiune „pentru că partenerul e din UE” — scutirea/neimpozitarea depinde strict de existența unui cod de TVA **valid, la acea dată, în VIES**. Fără el, motorul de validare pentru livrări (LIC) cere explicit codul valid + dovada transportului, iar pentru servicii cere codul valid pentru a stabili că operațiunea e neimpozabilă în România; în lipsa lui, sistemul întoarce eroare explicită — echivalentul practic: „facturează cu TVA”.

## Ce se greșește în practică

- Se preia codul de TVA comunicat de partener „ca atare”, fără o verificare independentă în VIES la data facturii.
- Se verifică o singură dată codul, la începutul colaborării, și nu se repetă verificarea la fiecare factură ulterioară — un cod valid azi poate fi anulat mâine.
- Se confundă verificarea în VIES cu verificarea unui CUI/CIF în registrul comerțului al altui stat — sunt registre diferite, cu scopuri diferite.
- Consecința practică: dacă la un control se constată că un cod nu era valid la data operațiunii, scutirea/neimpozitarea cade, iar TVA devine datorat retroactiv de furnizor.

## Ce face iConta.eu

La emiterea unei facturi cu cod de TVA de prefix non-RO, aplicația verifică automat, live, în VIES (nu în registrul ANAF de CUI-uri) starea codului și afișează rezultatul — valid/invalid — direct în ecranul de emitere; dacă VIES e temporar indisponibil, afișează avertisment explicit, în loc să presupună tacit validitatea.

Pentru livrări (`vanzare_ic`), validarea scutirii cere explicit: client non-RO + cod valid VIES + dovadă de transport prezentă; pentru servicii, validarea neimpozabilității cere client non-RO + cod valid VIES. În lipsa oricărei condiții, sistemul semnalează explicit că operațiunea trebuie tratată ca impozabilă în România (cu TVA), nu ca scutită/neimpozabilă „implicit”.

[iConta.eu](/)
