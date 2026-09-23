---
title: "Cum se declară veniturile din transport intracomunitar"
description: "Ghid despre tratamentul TVA (D390) al serviciilor de transport intracomunitar prestate unor clienți din UE; nu acoperă impozitul pe venit/profit."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se declară veniturile din transport intracomunitar

Acest ghid tratează strict latura de **TVA** a veniturilor obținute din prestarea de servicii de transport intracomunitar de mărfuri către firme din UE — nu tratamentul de impozit pe venit/profit al acestor venituri, care e o temă separată.

## Temeiul legal

::: ghid-temei
CF art. 278 alin. (2): „Locul prestării serviciilor B2B = locul beneficiarului (bază pentru neimpozabilitate în RO + declarare D390 cod S).” (sursă: `cod_fiscal_227_2015_consolidat.txt`, L17303-17420)
:::

Serviciul de transport intracomunitar prestat unei firme (persoană impozabilă) din alt stat membru UE urmează regula generală a serviciilor B2B: locul prestării e considerat la beneficiar. Dacă acesta are cod de TVA valid, verificat în VIES, factura se emite fără TVA românesc, iar operațiunea e neimpozabilă în România — impozitarea revine statului beneficiarului.

Din perspectivă declarativă, operațiunea nu dispare din obligațiile fiscale doar pentru că nu are TVA pe factură: se raportează în D390, cod P (servicii prestate intracomunitar).

## Ce se greșește în practică

- Se consideră că, odată emisă factura fără TVA, nu mai există nicio obligație declarativă asociată — D390 rămâne obligatoriu pentru lunile cu astfel de operațiuni.
- Se confundă venitul din transport intracomunitar (regim de servicii, art. 278 alin. 2) cu declararea lui în scopul impozitului pe venit/profit — sunt planuri diferite; acest ghid nu acoperă latura de impozit pe venit/profit.
- Se emite fără TVA fără verificarea efectivă, în VIES, a codului de TVA al clientului la data facturii.

## Ce face iConta.eu

Formularul de vânzare intracomunitară (`vanzare_ic`), categoria „Extern”, permite înregistrarea prestării către un client din UE, cu câmp pentru codul de TVA al acestuia. La emitere, aplicația verifică automat, live, în VIES starea codului.

Validarea neimpozabilității se face pe baza a două condiții — client non-RO + cod valid VIES — iar operațiunea validă se clasifică automat pentru D390, cod P. Pentru tratamentul de impozit pe venit/profit al acestor venituri, consultă un ghid dedicat acelei teme — nu e acoperit aici.

[iConta.eu](/)
