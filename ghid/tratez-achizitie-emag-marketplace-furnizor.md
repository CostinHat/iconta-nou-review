---
title: "Cum tratez o achiziție eMAG Marketplace de la un furnizor din UE?"
description: "O achiziție de pe eMAG Marketplace de la un furnizor din UE e intracomunitară doar dacă furnizorul facturează cu un cod de TVA UE valid și bunurile vin din alt stat membru."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum tratez o achiziție eMAG Marketplace de la un furnizor din UE?

O achiziție printr-un marketplace precum eMAG Marketplace urmează aceleași reguli ca orice altă achiziție de bunuri dintr-un alt stat membru UE — contează cine emite factura și de unde vin bunurile, nu platforma prin care s-a făcut comanda.

## Temeiul legal

::: ghid-temei
CF art. 268 alin. (1)-(3) lit. a): „Operațiuni impozabile; alin. (3) lit. a) — AIC de bunuri (altele decât mijloace de transport noi/accizabile) urmând unei LIC scutite.” (sursă: `cod_fiscal_227_2015_consolidat.txt`, L16593-16626)
:::

Pe un marketplace, factura poate fi emisă fie de operatorul platformei, fie direct de vânzătorul terț (furnizorul din market place). Dacă factura primită arată un cod de TVA valid al furnizorului dintr-un alt stat membru UE, iar bunurile sunt expediate din acel stat membru, achiziția e o achiziție intracomunitară de bunuri: se aplică taxare inversă la beneficiar, cu declarare în D390.

Dacă factura arată TVA românesc (de exemplu vânzătorul e înregistrat în România sau bunurile sunt expediate dintr-un depozit local), operațiunea nu e intracomunitară — e o achiziție obișnuită.

## Ce se greșește în practică

- Se presupune automat regimul intracomunitar pentru orice achiziție de pe un marketplace, fără verificarea codului de TVA de pe factura efectivă și a țării de expediere.
- Se ignoră faptul că, pe același marketplace, unii furnizori pot factura cu TVA românesc, alții cu regim intracomunitar — tratamentul se stabilește per factură, nu per platformă.
- Se omite declararea D390 atunci când achiziția e, într-adevăr, intracomunitară.

## Ce face iConta.eu

Verifică pe fiecare factură primită codul de TVA al furnizorului și țara de expediere a bunurilor. Dacă e o achiziție intracomunitară reală, folosește formularul de achiziție intracomunitară (`achizitie_ic`), tip „bunuri”: data, valoarea în RON, codul de TVA al furnizorului, numărul facturii, furnizorul, contul de destinație (sugestie 371) și cota de TVA aplicabilă.

Aplicația calculează TVA prin taxare inversă (4426 = 4427) și clasifică operațiunea pentru D390, cod A. Dacă factura arată TVA românesc, achiziția se înregistrează obișnuit, în afara acestui formular.

[iConta.eu](/)
