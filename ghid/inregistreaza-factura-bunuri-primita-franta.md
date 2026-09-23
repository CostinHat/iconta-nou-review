---
title: "Cum se înregistrează o factură de bunuri primită din Franța?"
description: O factură de bunuri de la un furnizor din Franța e o achiziție intracomunitară de bunuri — mecanismul de înregistrare e identic indiferent de statul membru al furnizorului, doar codul de TVA are alt prefix (FR).
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum se înregistrează o factură de bunuri primită din Franța?

Mecanismul de înregistrare pentru o achiziție intracomunitară de bunuri nu depinde de statul membru al furnizorului — regulile din Codul fiscal sunt aceleași indiferent dacă furnizorul e din Franța, Germania sau orice alt stat UE. Ce diferă, practic, e doar prefixul codului de TVA (pentru Franța: „FR").

## Temeiul legal

::: ghid-temei
HG 1/2016, norme la CF art. 331, pct. 109 alin. (1): „beneficiarul înregistrează… suma taxei aferente în următoarea formulă contabilă: 4426 = 4427. Prevederile acestui alineat sunt valabile pentru orice alte situații în care se aplică taxarea inversă.” CF art. 308-309: obligat la plata taxei este beneficiarul, la achiziții intracomunitare și la serviciile primite conform art. 278 alin. (2).
:::

Fiind o achiziție de bunuri de la un furnizor stabilit și înregistrat în scopuri de TVA în Franța, cu transport în România, operațiunea e taxată prin autolichidare: valoarea bunurilor se înregistrează pe contul de destinație (marfă, materii prime etc.), iar TVA aferentă, calculată la cota corespunzătoare bunului, se înregistrează simultan pe 4426 și 4427.

## Ce se greșește în practică

- Se așteaptă o factură cu TVA francez pe ea — furnizorul francez, dacă e corect înregistrat pentru operațiuni intracomunitare, facturează fără TVA, cumpărătorul român fiind cel care autolichidează taxa.
- Se verifică doar existența firmei furnizoare, nu și validitatea codului ei de TVA în VIES la data facturii.
- Se lasă cota de TVA "implicită" pentru bunul respectiv, fără verificare punctuală pentru operațiunea concretă.

## Ce face iConta.eu

Ecranul de achiziție intracomunitară cere codul de TVA al furnizorului UE — pentru un furnizor francez, un cod cu prefixul „FR" — alături de data, valoarea în lei, numărul facturii, contul de destinație (sugestie 371), tipul (bunuri) și cota de TVA, fără valoare implicită. Din aceste date, aplicația generează automat formula 4426 = 4427 pentru TVA, iar factura de bunuri primită e mapată automat în D390, la tipul de operațiune corespunzător achizițiilor intracomunitare de bunuri.

[iConta.eu](/)
