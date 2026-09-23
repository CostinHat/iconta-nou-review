---
title: "Cum tratez o achiziție de echipamente din Germania?"
description: "Regulile de TVA pentru achiziția intracomunitară de echipamente de la un furnizor din Germania: taxare inversă, D390 și verificarea VIES."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum tratez o achiziție de echipamente din Germania?

Achiziția de echipamente de la un furnizor cu cod de TVA valid în Germania urmează regula generală a achiziției intracomunitare de bunuri.

## Temeiul legal

::: ghid-temei
CF art. 268 alin. (1)-(3) lit. a): „Operațiuni impozabile; alin. (3) lit. a) — AIC de bunuri (altele decât mijloace de transport noi/accizabile) urmând unei LIC scutite.” (sursă: `cod_fiscal_227_2015_consolidat.txt`, L16593-16626)

CF art. 308-309: „Obligat la plata taxei = beneficiarul, la AIC/servicii primite.” (sursă: `cod_fiscal_227_2015_consolidat.txt`, L19405, L19418)
:::

Dacă firma din România e înregistrată în scopuri de TVA și furnizorul german are cod de TVA valid, verificabil în VIES, furnizorul facturează fără TVA german, iar firma din România datorează TVA prin taxare inversă (beneficiarul e obligat la plata taxei, art. 308-309), cu formula contabilă 4426 = 4427.

## Ce se greșește în practică

- Se acceptă factura fără verificarea codului de TVA german în VIES la data operațiunii.
- Se tratează echipamentele „speciale” sau scumpe ca având un regim TVA diferit de restul bunurilor achiziționate intracomunitar — nu există o asemenea distincție în regula generală citată.
- Se omite declararea D390 pentru achiziția intracomunitară.

## Ce face iConta.eu

Formularul de achiziție intracomunitară (`achizitie_ic`), tip „bunuri”, din categoria „Extern”, are câmpuri pentru data, valoarea în RON, codul de TVA al furnizorului (verificabil automat în VIES), numărul facturii, furnizorul, contul de destinație (sugestie 371) și cota de TVA aplicabilă.

Aplicația calculează TVA prin taxare inversă (4426 = 4427) și clasifică automat operațiunea pentru D390, cod A.

[iConta.eu](/)
