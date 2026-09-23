---
title: "Cum facturez bunuri către o firmă din Uniunea Europeană?"
description: "Ghid despre livrarea intracomunitară de bunuri scutită de TVA: condițiile scutirii, dovada transportului și declararea în D390."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum facturez bunuri către o firmă din Uniunea Europeană?

Vânzarea de bunuri către o firmă înregistrată în scopuri de TVA în alt stat membru UE (livrare intracomunitară — LIC) poate fi scutită de TVA, dar scutirea nu e automată: depinde de două condiții cumulative.

## Temeiul legal

::: ghid-temei
CF art. 294 alin. (2) lit. a): „Scutire LIC cu drept de deducere — condiții: cod TVA valid al cumpărătorului comunicat furnizorului + dovada transportului în alt SM.” (sursă: `intracomunitar.py`, docstring; text complet `cod_fiscal_227_2015_consolidat.txt`, L18397+)
:::

Scutirea de TVA la o livrare intracomunitară de bunuri se aplică doar dacă, cumulativ: (1) clientul are un cod de TVA valid, verificat în VIES, în alt stat membru și (2) există dovadă că bunurile au părăsit efectiv România către acel stat membru. Dacă oricare dintre condiții lipsește, factura trebuie emisă cu TVA — sistemul e construit exact pe această regulă: fără cod valid sau fără dovadă de transport, operațiunea nu califică drept LIC scutită.

## Ce se greșește în practică

- Se emite factura fără TVA doar pentru că beneficiarul „e din UE”, fără verificarea efectivă a codului de TVA în VIES la momentul facturării.
- Se emite fără TVA fără a păstra dovadă de transport (CMR, aviz însoțit de dovada preluării la destinație, confirmare de la transportator etc.) — condiție obligatorie, nu opțională.
- Se confundă livrarea de bunuri (art. 294 alin. 2 lit. a) cu prestarea de servicii (art. 278 alin. 2) — regimuri diferite, cu coduri diferite în D390 (L pentru bunuri, P pentru servicii).

## Ce face iConta.eu

Formularul de vânzare intracomunitară (`vanzare_ic`), din categoria „Extern” a operațiunilor speciale, are câmpuri dedicate: data, valoarea, codul de TVA al clientului, tipul operațiunii (bunuri/servicii) și, pentru bunuri, un câmp opțional pentru dovada transportului. La emiterea facturii cu cod de TVA non-RO, sistemul verifică automat, live, statutul în VIES.

Pe baza acestor date, aplicația validează condițiile scutirii — client non-RO, cod valid VIES, dovadă de transport prezentă — și, dacă oricare lipsește, semnalează explicit că operațiunea trebuie facturată cu TVA. Operațiunea se clasifică automat spre D390 cod L (livrări intracomunitare de bunuri).

[iConta.eu](/)
