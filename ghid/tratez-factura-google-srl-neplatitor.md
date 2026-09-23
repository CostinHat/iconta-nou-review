---
title: Cum tratez o factură Google la un SRL neplătitor de TVA?
description: Depinde de țara de stabilire a entității Google care emite factura — dacă e din UE, achiziția merge la D301 secțiunea 4.1 (tip 5); verificați acest lucru direct pe factură.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum tratez o factură Google la un SRL neplătitor de TVA?

Mecanismul general e clar, dar pasul care decide exact ce secțiune din D301 se aplică depinde de o informație pe care trebuie să o verificați chiar pe factura primită: țara de stabilire a entității Google care a emis-o (Google poate factura din diverse entități, în funcție de serviciu și țară).

## Temeiul legal

::: ghid-temei
"Locul de prestare a serviciilor către o persoană impozabilă (...) este locul unde respectiva persoană care primește serviciile își are stabilit sediul activității sale economice." — Codul fiscal, Legea nr. 227/2015, art. 278 alin. (2)
:::

::: ghid-temei
"Taxa este datorată de orice persoană impozabilă (...) care este beneficiar al serviciilor care au locul prestării în România conform art. 278 alin. (2) și care sunt furnizate de către o persoană impozabilă care nu este stabilită pe teritoriul României (...)" — Codul fiscal, art. 307 alin. (2)
:::

Un serviciu de publicitate online sau cloud cumpărat de un SRL neplătitor de TVA are locul prestării în România (art. 278 alin. (2)), deci firma română e obligată la plata taxei prin taxare inversă. Rămâne de stabilit **unde** e stabilit furnizorul, pentru că asta decide secțiunea din D301:

- dacă entitatea care emite factura e stabilită într-un stat membru UE → achiziția se declară la secțiunea 4.1 (tip 5) din D301, ceea ce înseamnă că apare automat și în D390, cu codul S;
- dacă entitatea e stabilită în afara UE → achiziția se declară la secțiunea 4 generală (art. 307 alin. (6)), care **nu** intră în D390.

Înainte de a face achiziția, SRL-ul trebuie să fie înregistrat special art. 317 (dacă nu e deja înregistrat ca plătitor de TVA).

## Ce se greșește în practică

- Se presupune automat "Google = UE", fără să se verifice pe factură entitatea și țara de stabilire ale furnizorului — pot fi diferite, în funcție de serviciu.
- Se ignoră obligația D301 pentru că "e doar o factură mică" — legea nu prevede un plafon pentru această categorie de operațiune.
- Se declară operațiunea și în D390 fără să se verifice mai întâi dacă furnizorul e stabilit efectiv în UE.

## Ce face iConta.eu

Aplicația nu deduce automat țara de stabilire a unui furnizor extern după numele lui — contabilul alege tipul de operațiune (4 sau 4.1) la introducere, pe baza documentului. Dacă țara și codul de TVA ale furnizorului sunt completate, operațiunea e trecută automat și în D390 cu codul corespunzător; dacă tipul introdus e 4 (nu 4.1), operațiunea rămâne exclusă din D390, conform regulii din normă.

[iConta.eu](/)
