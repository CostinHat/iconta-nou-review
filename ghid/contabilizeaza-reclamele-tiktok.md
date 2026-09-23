---
title: "Cum se contabilizează reclamele TikTok?"
description: "Factura de publicitate TikTok e operațiune intracomunitară doar dacă e emisă cu un cod de TVA UE valid, verificat în VIES."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se contabilizează reclamele TikTok?

Ca la orice factură de publicitate online, tratamentul TVA al facturii TikTok Ads depinde de codul de TVA de pe factura efectiv primită, nu de numele platformei sau de faptul că e „străină”.

## Temeiul legal

::: ghid-temei
CF art. 278 alin. (2): „Locul prestării serviciilor B2B = locul beneficiarului (bază pentru neimpozabilitate în RO + declarare D390 cod S).” (sursă: `cod_fiscal_227_2015_consolidat.txt`, L17303-17420)
:::

Dacă factura e emisă de o entitate cu cod de TVA valid, verificabil în VIES, într-un alt stat membru UE, achiziția e un serviciu B2B intracomunitar: firma din România datorează TVA prin taxare inversă și declară operațiunea în D390 (cod S). Dacă factura vine cu TVA local, sau de la o entitate fără cod de TVA UE (de exemplu o entitate din afara Uniunii Europene), regimul de mai jos nu se aplică.

Verifică efectiv codul de TVA de pe factură, la fiecare facturare.

## Ce se greșește în practică

- Se presupune automat regimul de taxare inversă UE pentru orice platformă de social media, fără verificarea codului de TVA efectiv de pe factură.
- Se omite declararea D390 pentru achiziții de servicii corect identificate ca intracomunitare.
- Se contabilizează cheltuiala de publicitate fără să se stabilească dacă e sau nu o operațiune intracomunitară din perspectiva TVA.

## Ce face iConta.eu

Verifică pe factura primită codul de TVA al emitentului. Dacă are prefix de stat membru UE, folosește formularul de achiziție intracomunitară (`achizitie_ic`), tip „servicii”, din categoria „Extern”: data, valoarea în RON, codul de TVA al furnizorului, numărul facturii și cota de TVA aplicabilă (declarată explicit, fără valoare implicită fixă în motor).

Aplicația calculează TVA prin taxare inversă (4426 = 4427) și clasifică automat operațiunea pentru D390, cod S. Dacă factura vine de la o entitate fără cod de TVA UE valid, operațiunea nu intră prin acest formular.

[iConta.eu](/)
