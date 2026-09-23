---
title: "Cum se înregistrează comisionul Booking.com?"
description: "Comisionul Booking.com e operațiune intracomunitară doar dacă factura vine cu un cod de TVA UE valid, verificat în VIES."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se înregistrează comisionul Booking.com?

Ca la orice comision reținut de o platformă străină, tratamentul TVA depinde de un singur lucru verificabil: **codul de TVA de pe factura de comision**, nu numele platformei.

## Temeiul legal

::: ghid-temei
CF art. 278 alin. (2): „Locul prestării serviciilor B2B = locul beneficiarului (bază pentru neimpozabilitate în RO + declarare D390 cod S).” (sursă: `cod_fiscal_227_2015_consolidat.txt`, L17303-17420)
:::

Dacă factura de comision e emisă de o entitate înregistrată în scopuri de TVA într-un alt stat membru UE, cu cod de TVA valid și verificabil în VIES, e o achiziție de serviciu B2B intracomunitar: firma din România datorează TVA prin taxare inversă și declară operațiunea în D390 (cod S). Dacă, în schimb, factura vine cu TVA local (de la o entitate stabilită sau înregistrată în România) sau de la o entitate fără cod de TVA UE, nu se aplică acest mecanism — e o achiziție obișnuită, respectiv un caz din afara sferei D390/VIES.

Recomandarea practică: verifică întotdeauna codul de TVA afișat pe factura primită, nu presupune tratamentul doar pe baza numelui furnizorului.

## Ce se greșește în practică

- Se tratează orice comision al unei platforme de rezervări ca fiind automat „taxare inversă UE”, fără verificarea codului de TVA de pe factura efectivă.
- Se ignoră obligația de declarare D390 atunci când factura chiar vine cu un cod de TVA UE valid.
- Se confundă comisionul (serviciu de intermediere) cu alte tipuri de cheltuieli, aplicând reguli greșite de contare.

## Ce face iConta.eu

Verifică pe factura primită codul de TVA al emitentului. Dacă are prefix de stat membru UE, folosește formularul de achiziție intracomunitară (`achizitie_ic`), tip „servicii”, din categoria „Extern”: completezi data, valoarea în RON, codul de TVA al furnizorului, numărul facturii și cota de TVA (aplicabilă explicit — motorul nu are o cotă implicită „înghețată”, tocmai ca să nu se rupă tăcut de lege la o schimbare de cotă).

Calculul TVA prin taxare inversă (4426 = 4427) și clasificarea pentru D390 (cod S) se fac automat pe baza datelor introduse — verificarea codului în VIES rămâne, aici, un pas manual al contabilului, la fel ca la orice altă achiziție intracomunitară de servicii. Dacă factura vine cu TVA local, operațiunea nu intră prin acest formular — e o achiziție obișnuită, în afara sferei F050.

[iConta.eu](/)
