---
title: "Cum tratez comisionul Airbnb din punct de vedere TVA?"
description: "Comisionul reținut de Airbnb este un serviciu primit de la o platformă stabilită în afara României, cu regim de TVA diferit după cum firma ta este sau nu plătitoare de TVA."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum tratez comisionul Airbnb din punct de vedere TVA?

Comisionul pe care Airbnb îl reține din suma încasată de la oaspeți este, din punct de vedere fiscal, o **prestare de servicii primită de la o platformă**. Locul unde se plătește TVA pentru acest serviciu nu este acolo unde e stabilită platforma, ci acolo unde ești stabilit tu, ca beneficiar.

## Temeiul legal

::: ghid-temei
„Locul de prestare a serviciilor către o persoană impozabilă (...) este locul unde respectiva persoană care primește serviciile își are stabilit sediul activității sale economice." — Codul fiscal, art. 278 alin. (2)

„Taxa este datorată de orice persoană impozabilă (...) care este beneficiar al serviciilor care au locul prestării în România conform art. 278 alin. (2) și care sunt furnizate de către o persoană impozabilă care nu este stabilită pe teritoriul României (...)" — Codul fiscal, art. 307 alin. (2)
:::

Practic, dacă firma ta din România primește un serviciu de comision de la o platformă care nu e stabilită în România, TVA-ul „se mută" la tine, prin **taxare inversă** — tu calculezi și declari taxa, nu platforma. Ce se întâmplă mai departe depinde de statutul tău de TVA:

- **Ești plătitor de TVA (înregistrat conform art. 316)** — operațiunea intră în **decontul de TVA (D300)**, la rândul de colectat și la rândul de deductibil, cu efect net zero (taxare inversă completă).
- **Nu ești plătitor de TVA** — trebuie să te înregistrezi special, conform **art. 317 Cod fiscal**, *înainte* de a primi acest tip de serviciu, fără prag valoric. După înregistrare, comisionul se declară prin **Declarația specială D301** (OPANAF 592/2016), la Secțiunea 4.1 (tip 5), **dar numai dacă furnizorul e stabilit în Uniunea Europeană** — instrucțiunile OPANAF 592/2016 vorbesc explicit despre persoane impozabile „nu sunt stabilite pe teritoriul României (...), dar care sunt stabilite în Comunitate". Dacă entitatea care facturează comisionul e stabilită în afara UE, operațiunea trece la tip 4 (art. 307 alin. (6)), nu la tip 5.

Termenul de declarare pentru D301, când e cazul, este **25 a lunii următoare** celei în care ia naștere exigibilitatea taxei.

## Ce se greșește în practică

- Se presupune că, fiindcă Airbnb nu emite factură cu TVA românesc, comisionul „scapă" de TVA — de fapt taxa se autolichidează la beneficiar (taxare inversă), nu dispare.
- Se completează D301 deși firma e plătitoare de TVA — pentru un plătitor, operațiunea merge în D300, nu în D301; cele două declarații nu se completează niciodată simultan pentru aceeași operațiune.
- Se presupune automat că orice platformă e „stabilită în UE" și deci intră la tip 5 (D390 cod S), fără să se verifice efectiv, pe factura primită, entitatea și țara de stabilire a furnizorului — dacă entitatea de facturare e din afara UE, tratamentul corect e tip 4, nu tip 5.
- Se amână înregistrarea specială la ANAF conform art. 317, deși aceasta trebuie făcută **înainte** de primirea serviciului, nu la momentul declarării.

## Ce face iConta.eu

Dacă firma ta e **plătitoare de TVA**, comisionul se înregistrează prin taxare inversă, pe același mecanism folosit pentru orice achiziție de servicii intracomunitare — rândul de colectat și cel de deductibil, net zero.

Dacă firma ta **nu e plătitoare de TVA**, aplicația oferă ecranul D301, cu tipurile de operațiune prevăzute de OPANAF 592/2016. Ecranul **blochează explicit** introducerea unei operațiuni D301 dacă firma e deja înregistrată ca plătitoare de TVA, cu mesajul: „Firma e înregistrată în scopuri de TVA (plătitoare) — D301 (decontul special) e pentru NEplătitori. Achizițiile intracomunitare ale unui plătitor se declară în D390/D300, nu în D301." Dacă completezi și țara/codul de TVA al furnizorului, operațiunea de tip 5 apare automat și în declarația D390.

O limitare de care trebuie să ții cont: **verificarea entității și a țării de stabilire a furnizorului nu se face automat de aplicație** — contabilul trebuie să o confirme pe baza facturii primite, înainte de a alege tip 4 sau tip 5. De asemenea, generarea D301 pe zero (fără nicio operațiune introdusă în perioadă) este blocată — declarația se depune numai când există efectiv operațiuni cu exigibilitate în lună.

[iConta.eu](/)
