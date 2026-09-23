---
title: "Cum tratez achiziția unui autoturism din UE?"
description: "Regula AIC pentru un autoturism cumpărat din UE, cu excepția specială pentru mijloacele de transport noi (art. 268 alin. 3 lit. a)."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum tratez achiziția unui autoturism din UE?

Tratamentul TVA al unui autoturism cumpărat dintr-un alt stat membru UE depinde, în primul rând, de un singur criteriu: este sau nu „mijloc de transport nou”, în sensul Codului fiscal.

## Temeiul legal

::: ghid-temei
CF art. 268 alin. (1)-(3) lit. a): „Operațiuni impozabile; alin. (3) lit. a) — AIC de bunuri (altele decât mijloace de transport noi/accizabile) urmând unei LIC scutite.” (sursă: `cod_fiscal_227_2015_consolidat.txt`, L16593-16626)
:::

Textul citat exclude explicit mijloacele de transport noi din regimul obișnuit al AIC care urmează unei LIC scutite — pentru un autoturism nou (criteriile de noutate, de vechime/kilometraj, țin de un regim special, nedetaliat în cercetarea care stă la baza acestui ghid), se aplică o regulă separată de impozitare la destinație.

Pentru un autoturism care **nu** e „mijloc de transport nou”, se aplică regula generală AIC: dacă firma din România e înregistrată în scopuri de TVA și vânzătorul are cod de TVA valid în alt stat membru, achiziția e taxată prin taxare inversă la beneficiar, cu declarare în D390.

**Notă de sferă:** acest ghid acoperă doar tratamentul TVA la achiziția intracomunitară. Alte reguli fiscale specifice autoturismelor (de exemplu limitări de deducere a TVA aferentă cumpărării/utilizării unui autoturism) sunt o temă separată, neacoperită aici.

## Ce se greșește în practică

- Se tratează orice autoturism cumpărat din UE la fel, fără a distinge dacă e sau nu „mijloc de transport nou” — regim cu reguli diferite de AIC obișnuită.
- Se aplică taxare inversă fără verificarea codului de TVA al vânzătorului în VIES.
- Se confundă tratamentul de AIC (recunoașterea și declararea operațiunii) cu regulile de deductibilitate a TVA — acestea sunt independente și nu sunt tratate în acest ghid.

## Ce face iConta.eu

Pentru un autoturism achiziționat intracomunitar și care nu se încadrează la excepția „mijloc de transport nou”, folosești formularul de achiziție intracomunitară (`achizitie_ic`), tip „bunuri”, cu câmpurile: data, valoarea în RON, codul de TVA al furnizorului (verificabil în VIES), numărul facturii, furnizorul, contul de destinație și cota de TVA.

Aplicația calculează TVA prin taxare inversă (4426 = 4427) și clasifică operațiunea pentru D390, cod A. Pentru cazul particular al unui mijloc de transport nou, cercetarea care stă la baza acestui ghid nu a confirmat un formular sau tratament dedicat în aplicație.

[iConta.eu](/)
