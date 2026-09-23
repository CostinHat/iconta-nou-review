---
title: "Cum se înregistrează comisionul Airbnb?"
description: "Comisionul Airbnb e operațiune intracomunitară doar dacă factura vine cu un cod de TVA UE valid, verificat în VIES."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se înregistrează comisionul Airbnb?

La fel ca la orice altă platformă de rezervări, tratamentul TVA al comisionului Airbnb depinde de codul de TVA afișat pe factura de comision, nu de numele platformei.

## Temeiul legal

::: ghid-temei
CF art. 278 alin. (2): „Locul prestării serviciilor B2B = locul beneficiarului (bază pentru neimpozabilitate în RO + declarare D390 cod S).” (sursă: `cod_fiscal_227_2015_consolidat.txt`, L17303-17420)
:::

Dacă factura de comision e emisă de o entitate cu cod de TVA valid, verificabil în VIES, într-un alt stat membru UE, e o achiziție de serviciu B2B intracomunitar: firma din România datorează TVA prin taxare inversă și declară operațiunea în D390 (cod S). Dacă factura vine cu TVA local sau de la o entitate fără cod de TVA UE, mecanismul de mai jos nu se aplică.

Verifică întotdeauna codul de TVA de pe factura efectiv primită — nu presupune tratamentul doar din numele furnizorului.

## Ce se greșește în practică

- Se tratează comisionul ca automat supus taxării inverse UE, fără verificarea codului de TVA de pe factura primită.
- Se omite declararea D390 atunci când factura chiar vine cu cod de TVA UE valid.
- Se aplică cota de TVA „din memorie”, în loc să se stabilească explicit cota corectă pentru operațiune.

## Ce face iConta.eu

Verifică pe factura primită codul de TVA al emitentului. Dacă are prefix de stat membru UE, folosește formularul de achiziție intracomunitară (`achizitie_ic`), tip „servicii”, din categoria „Extern”: data, valoarea în RON, codul de TVA al furnizorului, numărul facturii și cota de TVA aplicabilă — motorul cere cota introdusă explicit, fără o valoare implicită fixă, pentru a nu rămâne blocat la o cotă veche.

Aplicația calculează TVA prin taxare inversă (4426 = 4427) și clasifică automat operațiunea pentru D390, cod S. Dacă factura vine cu TVA local, operațiunea nu se înregistrează prin acest formular — e o achiziție obișnuită.

[iConta.eu](/)
