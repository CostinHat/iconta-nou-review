---
title: "Cum tratez TVA la cumpărarea unui utilaj din UE?"
description: "Regulile de TVA pentru achiziția intracomunitară a unui utilaj de la un furnizor dintr-un alt stat membru UE: taxare inversă, D390 și verificarea VIES."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum tratez TVA la cumpărarea unui utilaj din UE?

Achiziția unui utilaj de la un furnizor dintr-un alt stat membru UE urmează regula generală a achiziției intracomunitare de bunuri — nu diferă de achiziția oricărui alt tip de bun (marfă, echipamente).

## Temeiul legal

::: ghid-temei
CF art. 268 alin. (1)-(3) lit. a): „Operațiuni impozabile; alin. (3) lit. a) — AIC de bunuri (altele decât mijloace de transport noi/accizabile) urmând unei LIC scutite.” (sursă: `cod_fiscal_227_2015_consolidat.txt`, L16593-16626)

CF art. 308-309: „Obligat la plata taxei = beneficiarul, la AIC/servicii primite.” (sursă: `cod_fiscal_227_2015_consolidat.txt`, L19405, L19418)
:::

Dacă firma din România e înregistrată în scopuri de TVA și furnizorul din statul membru UE are cod de TVA valid, verificabil în VIES, furnizorul facturează fără TVA local, iar firma din România datorează TVA prin taxare inversă (beneficiarul e obligat la plata taxei, art. 308-309), cu formula contabilă 4426 = 4427.

## Ce se greșește în practică

- Se acceptă factura fără verificarea codului de TVA al furnizorului în VIES la data operațiunii.
- Se confundă un utilaj cu un „mijloc de transport” (dacă e cazul unor utilaje autopropulsate, înmatriculabile) — mijloacele de transport noi au un regim special, diferit (excepție explicită de la regula generală AIC).
- Se omite declararea D390 pentru achiziția intracomunitară, chiar dacă taxarea inversă a fost calculată corect.

## Ce face iConta.eu

Formularul de achiziție intracomunitară (`achizitie_ic`), tip „bunuri”, din categoria „Extern”, are câmpuri pentru data, valoarea în RON, codul de TVA al furnizorului (verificabil automat în VIES), numărul facturii, furnizorul, contul de destinație (sugestie 371) și cota de TVA aplicabilă.

Aplicația calculează TVA prin taxare inversă (4426 = 4427) și clasifică automat operațiunea pentru D390, cod A. Dacă utilajul se încadrează la excepția „mijloc de transport nou”, verifică regulile specifice acelui regim — nu confirmate, în cercetarea care stă la baza acestui ghid, ca fiind acoperite de un formular dedicat separat.

[iConta.eu](/)
