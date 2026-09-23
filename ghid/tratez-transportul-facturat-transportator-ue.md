---
title: "Cum tratez transportul facturat de un transportator din UE?"
description: "Serviciul de transport primit de la un transportator cu cod de TVA valid în alt stat membru UE se taxează invers, conform art. 278 alin. (2) și art. 308-309."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum tratez transportul facturat de un transportator din UE?

Când primești o factură de transport de la un transportator înregistrat în scopuri de TVA într-un alt stat membru UE, se aplică regula generală a achiziției de servicii B2B intracomunitare — nu regimul mai general al vreunei „achiziții din UE”.

## Temeiul legal

::: ghid-temei
CF art. 278 alin. (2): „Locul prestării serviciilor B2B = locul beneficiarului (bază pentru neimpozabilitate în RO + declarare D390 cod S).” (sursă: `cod_fiscal_227_2015_consolidat.txt`, L17303-17420)

CF art. 307 alin. (2): „Taxa este datorată de orice persoană impozabilă… care este beneficiar al serviciilor care au locul prestării în România conform art. 278 alin. (2) și care sunt furnizate de către o persoană impozabilă care nu este stabilită pe teritoriul României…” (sursă: `cod_fiscal_227_2015_consolidat.txt`, L19334-19342)
:::

Dacă transportatorul are cod de TVA valid, verificabil în VIES, într-un alt stat membru UE, iar firma din România e beneficiarul serviciului, locul prestării e considerat la beneficiar — factura ar trebui emisă fără TVA de către transportator, iar firma din România datorează TVA prin taxare inversă (obligat la plată = beneficiarul, art. 307 alin. (2)), cu formula contabilă 4426 = 4427. Operațiunea se declară în D390, cod S.

## Ce se greșește în practică

- Se acceptă TVA-ul aplicat de transportatorul din alt stat membru pe factură, deși regula ar trebui să conducă la o factură fără TVA plus taxare inversă la beneficiar în România.
- Se omite verificarea codului de TVA al transportatorului în VIES înainte de a aplica taxarea inversă.
- Se omite declararea D390 pentru achiziția de servicii de transport, deși taxarea inversă a fost înregistrată corect în contabilitate.

## Ce face iConta.eu

Folosești formularul de achiziție intracomunitară (`achizitie_ic`), tip „servicii”, din categoria „Extern”, cu câmpuri pentru data, valoarea în RON, codul de TVA al furnizorului (transportatorului), numărul facturii și cota de TVA aplicabilă, declarată explicit.

Aplicația calculează TVA prin taxare inversă (4426 = 4427) și clasifică automat operațiunea pentru D390, cod S.

[iConta.eu](/)
