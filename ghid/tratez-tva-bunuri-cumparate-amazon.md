---
title: "Cum tratez TVA pentru bunuri cumpărate de pe Amazon Business din UE?"
description: "O achiziție de pe Amazon Business e intracomunitară doar dacă vânzătorul facturează cu un cod de TVA UE valid și bunurile vin din alt stat membru."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum tratez TVA pentru bunuri cumpărate de pe Amazon Business din UE?

O achiziție prin Amazon Business urmează aceleași reguli ca orice altă achiziție de bunuri dintr-un alt stat membru UE — regula nu depinde de faptul că marketplace-ul e Amazon, ci de cine emite efectiv factura și de unde vin bunurile.

## Temeiul legal

::: ghid-temei
CF art. 268 alin. (1)-(3) lit. a): „Operațiuni impozabile; alin. (3) lit. a) — AIC de bunuri (altele decât mijloace de transport noi/accizabile) urmând unei LIC scutite.” (sursă: `cod_fiscal_227_2015_consolidat.txt`, L16593-16626)
:::

Dacă factura primită prin Amazon Business arată un cod de TVA valid al vânzătorului dintr-un alt stat membru UE (nu al României) și bunurile sunt expediate dintr-un depozit din alt stat membru, achiziția e, din perspectivă TVA, o achiziție intracomunitară de bunuri: se aplică taxare inversă la beneficiar (firma din România), cu declarare în D390.

Dacă, în schimb, factura arată TVA românesc (de exemplu, vânzătorul e înregistrat prin regim special de vânzare la distanță/OSS, sau bunurile sunt expediate dintr-un depozit din România), operațiunea **nu** e o achiziție intracomunitară — e o achiziție obișnuită, în afara sferei acestui ghid.

## Ce se greșește în practică

- Se presupune că orice cumpărătură de pe un marketplace „internațional” e automat o achiziție intracomunitară, fără verificarea efectivă a codului de TVA de pe factură și a țării de expediere.
- Se ignoră taxarea inversă atunci când factura chiar arată un cod de TVA valid dintr-un alt stat membru.
- Se confundă factura emisă de vânzătorul terț (marketplace) cu factura emisă de platforma însăși pentru comisionul de serviciu — pot avea tratamente diferite.

## Ce face iConta.eu

Verifică pe fiecare factură primită codul de TVA al vânzătorului și țara de expediere a bunurilor. Dacă e o achiziție intracomunitară reală (cod de TVA UE valid al furnizorului, bunuri din alt stat membru), folosește formularul de achiziție intracomunitară (`achizitie_ic`), tip „bunuri”: data, valoarea în RON, codul de TVA al furnizorului, numărul facturii, furnizorul, contul de destinație (sugestie 371) și cota de TVA aplicabilă.

Aplicația calculează TVA prin taxare inversă (4426 = 4427) și clasifică operațiunea pentru D390, cod A. Dacă factura arată TVA românesc, operațiunea se înregistrează ca achiziție obișnuită, nu prin acest formular.

[iConta.eu](/)
