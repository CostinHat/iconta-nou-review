---
title: "D390 zero: când depun declarație fără operațiuni"
description: "D390 nu se depune în fiecare lună ca D300 — regula exactă din OPANAF 705/2020 pentru lunile în care se depune declarația recapitulativă."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# D390 zero: când depun declarație fără operațiuni

Spre deosebire de decontul de TVA, declarația recapitulativă D390 (VIES) nu e o obligație fixă, lunară sau trimestrială. Se depune **doar** pentru perioadele în care ia naștere exigibilitatea unei operațiuni intracomunitare — dacă într-o lună nu există nicio astfel de operațiune, declarația pur și simplu nu se depune „pe zero".

## Temeiul legal

::: ghid-temei
„1.2. Persoanele impozabile înregistrate în scopuri de TVA depun declaraţia recapitulativă numai pentru lunile calendaristice în care ia naştere exigibilitatea taxei pentru: a) livrările intracomunitare scutite de taxă în condiţiile prevăzute la art. 294 alin. (2) lit. a) şi d) din Codul fiscal, pentru care exigibilitatea taxei a luat naştere în luna calendaristică respectivă; b) livrările de bunuri efectuate în cadrul unei operaţiuni triunghiulare prevăzute la art. 276 alin. (5) din Codul fiscal efectuate în statul membru de sosire a bunurilor şi care se declară drept livrări intracomunitare cu cod T, pentru care exigibilitatea de taxă a luat naştere în luna calendaristică respectivă; c) prestările de servicii prevăzute la art. 278 alin. (2) din Codul fiscal efectuate în beneficiul unor persoane impozabile nestabilite în România, dar stabilite în Uniunea Europeană, altele decât cele scutite de TVA în statul membru în care acestea sunt impozabile, pentru care exigibilitatea de taxă a luat naştere în luna calendaristică respectivă; d) achiziţiile intracomunitare de bunuri taxabile, pentru care exigibilitatea de taxă a luat naştere în luna calendaristică respectivă; e) achiziţiile de servicii prevăzute la art. 278 alin. (2) din Codul fiscal, efectuate de persoane impozabile din România care au obligaţia plăţii taxei conform art. 307 alin. (2), pentru care exigibilitatea de taxă a luat naştere în luna calendaristică respectivă, de la persoane impozabile nestabilite în România, dar stabilite în Uniunea Europeană; f) livrările intracomunitare de bunuri prevăzute la art. 315^1 alin. (8) lit. c) şi d) din Codul fiscal, pentru care exigibilitatea taxei a luat naştere în luna calendaristică respectivă."
— OPANAF 705/2020, Anexa 2, Instrucțiuni pct. 1.2 (sursă: anaf_surse/opanaf_705_2020_d390.txt)
:::

Practic, D390 se datorează pentru o lună anume doar dacă în luna respectivă a apărut una din cele șase situații de mai sus:

- livrare intracomunitară de bunuri scutită (cod L);
- livrare ulterioară în operațiune triunghiulară (cod T);
- prestare intracomunitară de servicii către o persoană stabilită în UE (cod P);
- achiziție intracomunitară de bunuri taxabile (cod A);
- achiziție de servicii de la o persoană stabilită în UE, cu taxare inversă (cod S);
- livrare intracomunitară în regimul special pentru agricultori (cod R).

Dacă niciuna dintre acestea nu s-a produs în luna respectivă, nu există obligația de depunere pentru acea lună — nu se completează un formular „fără operațiuni", ca la decontul de TVA.

## Ce se greșește în practică

- Se tratează D390 ca pe o obligație fixă, lunară, indiferent dacă a existat sau nu vreo operațiune intracomunitară — la fel ca D300 sau D112.
- Se depune declarația „din prudență", pe zero, deși legea leagă obligația strict de exigibilitatea taxei, nu de simpla existență a unui cod de TVA activ pentru operațiuni intracomunitare.
- Se confundă data facturii cu data exigibilității — o factură emisă într-o lună poate avea exigibilitatea taxei într-o altă lună (de exemplu la achizițiile intracomunitare), ceea ce mută obligația de declarare în luna corectă, nu în luna facturii.

## Ce face iConta.eu

Obligația de depunere D390 e calculată **pe fapt, lunar**, nu ca bifă fixă. Aplicația citește efectiv facturile intracomunitare, liniile manuale și operațiunile derivate din D301 ale lunii respective; dacă nu găsește nicio operațiune, marchează explicit luna ca „D390 nu se datorează... nicio operațiune intracomunitară în lună. Se depune numai pentru lunile în care ia naștere exigibilitatea", cu trimitere directă la instrucțiunile de completare citate mai sus.

Când se încearcă totuși generarea unei declarații pe o lună fără operațiuni, poarta de generare a declarației (funcția care produce XML-ul final) blochează depunerea „pe zero" — dar, dacă în paralel există în ecranul D301 achiziții intracomunitare fără țara furnizorului completată, mesajul de blocare îndrumă explicit contabilul să completeze acel câmp, pentru cazul în care operațiunea există de fapt, dar nu poate fi identificată automat.

[iConta.eu](/)
