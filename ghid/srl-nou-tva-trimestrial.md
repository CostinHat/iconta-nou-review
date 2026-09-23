---
title: Un SRL nou poate avea TVA trimestrial?
description: Da — dacă cifra de afaceri estimată pentru restul anului, recalculată proporțional, nu depășește plafonul și firma nu are deja achiziții intracomunitare.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Un SRL nou poate avea TVA trimestrial?

Răspunsul scurt e da, dar condiționat: legea permite decontul trimestrial chiar din anul înregistrării TVA, pe baza unei cifre de afaceri estimate, nu doar firmelor cu istoric de activitate.

## Temeiul legal

::: ghid-temei
**Art. 322 alin. (3) CF**: „Persoana impozabilă care se înregistrează în cursul anului trebuie să declare, cu ocazia înregistrării conform art. 316, cifra de afaceri pe care preconizează să o realizeze în perioada rămasă până la sfârșitul anului calendaristic. Dacă cifra de afaceri estimată nu depășește plafonul prevăzut la alin. (2), recalculat corespunzător numărului de luni rămase până la sfârșitul anului calendaristic, persoana impozabilă va depune deconturi trimestriale în anul înregistrării."

**Art. 322 alin. (4) CF** (pentru întreprinderile mici care se înregistrează TVA opțional în cursul anului): „[...] trebuie să declare cu ocazia înregistrării cifra de afaceri obținută, recalculată în baza activității corespunzătoare unui an calendaristic întreg. Dacă această cifră de afaceri recalculată depășește plafonul [...], perioada fiscală va fi luna calendaristică [...]. Dacă [...] nu depășește plafonul [...], persoana impozabilă va utiliza trimestrul calendaristic [...], cu excepția situației în care a efectuat [...] una sau mai multe achiziții intracomunitare de bunuri înainte de înregistrarea în scopuri de TVA."

Sursă: `anaf_surse/cod_fiscal_227_2015_consolidat.txt`, liniile 21807-21819.
:::

Da, un SRL nou poate avea decont trimestrial de TVA încă din primul an de înregistrare — condiția e ca cifra de afaceri estimată pentru perioada rămasă din an (declarată chiar la înregistrarea TVA) să nu depășească plafonul de 100.000 euro, recalculat proporțional cu lunile rămase, și să nu fi efectuat deja achiziții intracomunitare de bunuri înainte de înregistrare.

Există o nuanță importantă între alin. (3) și alin. (4): alin. (3) vizează firmele care ajung la plafonul regimului de scutire și se înregistrează obligatoriu TVA — acolo contează cifra de afaceri estimată pentru restul anului; alin. (4) vizează întreprinderile mici care aleg să se înregistreze TVA opțional — acolo contează cifra de afaceri deja obținută, recalculată la un an calendaristic întreg. Formula de calcul diferă puțin, dar concluzia practică e aceeași: TVA trimestrial e posibil din primul an, dacă cifra e sub plafon și nu există achiziții intracomunitare anterioare.

## Ce se greșește în practică

- Se presupune că trimestrial e disponibil doar din al doilea an de activitate, ignorând opțiunea explicită oferită firmelor noi la art. 322 alin. (3)-(4).
- Se confundă baza de calcul: cifra de afaceri estimată pentru restul anului (alin. 3) cu cifra de afaceri obținută, recalculată la an întreg (alin. 4) — sunt formule diferite, aplicabile în situații diferite de înregistrare.
- Se ignoră excepția achizițiilor intracomunitare efectuate înainte de înregistrarea TVA, care blochează opțiunea trimestrială indiferent de cifra de afaceri.

## Ce face iConta.eu

Câmpul `tip_decont` din Vector fiscal permite alegerea „trimestrial" pentru orice firmă, inclusiv nou-înființată — aplicația nu impune automat „lunar" firmelor noi. Calculul specific al plafonului recalculat (proporțional cu lunile rămase, conform art. 322 alin. 3, sau la an calendaristic întreg, conform alin. 4) nu este automatizat — contabilul introduce direct periodicitatea aleasă, pe baza propriului calcul.

[iConta.eu](/)
