---
title: "Cum se înregistrează o factură emisă de o platformă străină de food delivery?"
description: "Comisionul unei platforme de food delivery e operațiune intracomunitară doar dacă platforma facturează cu un cod de TVA UE valid — altfel e o factură obișnuită."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se înregistrează o factură emisă de o platformă străină de food delivery?

Înainte de a decide cum se tratează fiscal comisionul reținut de o platformă de food delivery (indiferent de nume), primul pas e să verifici **cine emite efectiv factura** — pentru că răspunsul schimbă complet tratamentul TVA.

## Temeiul legal

::: ghid-temei
CF art. 278 alin. (2): „Locul prestării serviciilor B2B = locul beneficiarului (bază pentru neimpozabilitate în RO + declarare D390 cod S).” (sursă: `cod_fiscal_227_2015_consolidat.txt`, L17303-17420)
:::

Acest ghid (F050) tratează strict cazul în care factura de comision vine de la o entitate **înregistrată în scopuri de TVA în alt stat membru UE**, cu cod de TVA valid, verificabil în VIES. În acest caz, e o achiziție de serviciu B2B intracomunitar: firma din România datorează TVA prin taxare inversă, indiferent de cota aplicabilă serviciului, iar operațiunea se declară în D390.

Există însă și alte două situații frecvente, care **nu** intră sub acest regim:
- platforma facturează prin filiala ei românească, cu TVA românesc pe factură — atunci nu e o operațiune intracomunitară, e o achiziție locală obișnuită (contarea facturii se face ca la orice furnizor din România, nu prin mecanismul descris aici);
- platforma facturează dintr-o entitate din afara UE (fără cod de TVA UE) — atunci nu e „intracomunitar” în sensul VIES/D390, chiar dacă taxarea inversă poate rămâne relevantă printr-un alt mecanism, neacoperit de acest ghid.

## Ce se greșește în practică

- Se aplică automat taxare inversă și declarare D390 pentru orice factură „de la o platformă străină”, fără să se verifice dacă emitentul are efectiv cod de TVA valid într-un stat membru UE.
- Se ignoră complet taxarea inversă atunci când factura chiar vine cu un cod de TVA UE valid, tratând-o ca o simplă cheltuială fără nicio obligație declarativă suplimentară.
- Se confundă comisionul (serviciu) cu o achiziție de bunuri — sunt regimuri diferite (servicii: art. 278 alin. 2; bunuri: art. 294 alin. 2 lit. a, pentru vânzări, respectiv art. 268 pentru achiziții).

## Ce face iConta.eu

Primul pas practic: verifică pe factura primită codul de TVA al emitentului. Dacă are prefix de stat membru UE, folosește formularul de achiziție intracomunitară (`achizitie_ic`), tip „servicii”, din categoria „Extern” a operațiunilor speciale — completezi data, valoarea în RON, codul de TVA al furnizorului, numărul facturii și cota de TVA aplicabilă (sugestie implicită 21%, dar cota nu are valoare fixă în motor — trebuie declarată explicit, tocmai pentru a nu rămâne „înghețată” la o cotă veche).

Aplicația calculează TVA prin taxare inversă (formula contabilă 4426 = 4427) și clasifică operațiunea pentru D390, cod S. Dacă factura vine, în schimb, cu TVA românesc de la o filială locală, operațiunea nu se înregistrează prin acest formular — e o achiziție obișnuită, în afara sferei F050.

[iConta.eu](/)
