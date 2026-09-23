---
title: "Cum facturez servicii către o firmă din Uniunea Europeană?"
description: "Ghid despre facturarea serviciilor B2B către clienți din UE: când sunt neimpozabile în România și cum se declară în D390."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum facturez servicii către o firmă din Uniunea Europeană?

Când prestezi un serviciu către o firmă (persoană impozabilă) dintr-un alt stat membru UE, regula de bază schimbă locul unde se plătește TVA: nu la tine, în România, ci la beneficiar, în țara lui.

## Temeiul legal

::: ghid-temei
CF art. 278 alin. (2): „Locul prestării serviciilor B2B = locul beneficiarului (bază pentru neimpozabilitate în RO + declarare D390 cod S).” (sursă: `cod_fiscal_227_2015_consolidat.txt`, L17303-17420)

CF art. 294 alin. (2) lit. a): „Scutire LIC cu drept de deducere — condiții: cod TVA valid al cumpărătorului comunicat furnizorului + dovada transportului în alt SM.” (sursă: `intracomunitar.py`, docstring)
:::

Pentru **servicii** către o firmă din UE, condiția esențială e ca partenerul să aibă un **cod de TVA valid, verificat în VIES**, într-un alt stat membru. Dacă această condiție e îndeplinită, factura se emite fără TVA românesc, iar operațiunea e neimpozabilă în România — se impozitează în statul beneficiarului, potrivit legislației lui.

Dacă partenerul NU are cod de TVA valid în VIES (de exemplu e persoană fizică sau firmă neînregistrată), operațiunea devine B2C: facturezi cu TVA românesc, ca la un client din România.

## Ce se greșește în practică

- Se emite factura fără TVA doar pe baza unui cod de TVA „introdus de client”, fără verificare efectivă în VIES la data facturării.
- Se confundă serviciile (regim B2B, art. 278 alin. 2) cu livrările de bunuri (regim LIC, art. 294 alin. 2 lit. a, care cere și dovadă de transport) — sunt reguli diferite, cu declarare diferită în D390.
- Se uită complet declararea D390 pentru cod S (servicii prestate), considerând că, odată ce factura e „fără TVA”, obligația declarativă a dispărut.

## Ce face iConta.eu

La emiterea unei facturi cu un cod de TVA cu prefix non-RO, iConta verifică automat, live, în VIES starea codului (valid/invalid) și afișează rezultatul direct în ecranul de emitere; dacă VIES e temporar indisponibil, afișează un avertisment explicit, nu ascunde problema.

Pentru operațiunea propriu-zisă, în categoria „Extern” a operațiunilor speciale există formularul de vânzare intracomunitară (`vanzare_ic`), cu câmpuri pentru data, valoarea, codul de TVA al clientului, tipul (bunuri/servicii) și, pentru bunuri, dovada transportului. Pe baza acestor date, operațiunea se clasifică pentru D390 (cod P pentru servicii prestate, verificat automat prin funcția care validează condițiile de neimpozabilitate: client non-RO + cod valid VIES).

[iConta.eu](/)
