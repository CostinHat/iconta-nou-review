---
title: "Cum se înregistrează factura Meta Ads?"
description: "Factura de publicitate Meta Ads e operațiune intracomunitară doar dacă e emisă cu un cod de TVA UE valid, verificat în VIES."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se înregistrează factura Meta Ads?

Factura de publicitate online (Meta Ads sau orice alt furnizor similar) intră sub regimul operațiunilor intracomunitare doar dacă e emisă de o entitate cu cod de TVA valid într-un alt stat membru UE — nu automat, doar pentru că serviciul e „digital” sau „străin”.

## Temeiul legal

::: ghid-temei
CF art. 278 alin. (2): „Locul prestării serviciilor B2B = locul beneficiarului (bază pentru neimpozabilitate în RO + declarare D390 cod S).” (sursă: `cod_fiscal_227_2015_consolidat.txt`, L17303-17420)
:::

Dacă furnizorul de publicitate facturează cu un cod de TVA valid, verificabil în VIES, într-un stat membru UE, achiziția e un serviciu B2B intracomunitar: firma din România datorează TVA prin taxare inversă și declară operațiunea în D390 (cod S). Dacă factura vine cu TVA local sau de la o entitate fără cod de TVA UE (de exemplu o entitate din afara Uniunii Europene), acest mecanism nu se aplică — tratamentul TVA e altul, neacoperit de acest ghid.

Recomandarea practică: verifică efectiv codul de TVA afișat pe factura primită, la fiecare facturare (poate diferi în timp, dacă furnizorul își schimbă entitatea de facturare).

## Ce se greșește în practică

- Se presupune automat că orice factură de publicitate online de la un furnizor mare, internațional, e „intracomunitară”, fără verificarea codului de TVA efectiv de pe factură.
- Se aplică taxare inversă fără să se verifice VIES, doar pe baza faptului că factura „nu are TVA pe ea”.
- Se omite declararea D390, chiar dacă operațiunea a fost corect identificată ca achiziție intracomunitară de servicii.

## Ce face iConta.eu

Verifică pe factura primită codul de TVA al emitentului. Dacă are prefix de stat membru UE, folosește formularul de achiziție intracomunitară (`achizitie_ic`), tip „servicii”, din categoria „Extern”: data, valoarea în RON, codul de TVA al furnizorului, numărul facturii și cota de TVA aplicabilă (declarată explicit, fără valoare implicită fixă în motor).

Aplicația calculează TVA prin taxare inversă (4426 = 4427) și clasifică automat operațiunea pentru D390, cod S. Dacă factura vine de la o entitate fără cod de TVA UE valid, operațiunea nu intră prin acest formular.

[iConta.eu](/)
