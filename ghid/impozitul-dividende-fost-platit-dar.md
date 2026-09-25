---
title: "Ce faci dacă impozitul pe dividende a fost plătit, dar beneficiarul lipsește din D205?"
description: "Ce prevede legea pentru dividendele distribuite dar neplătite până la sfârșitul anului, și de ce un beneficiar poate lipsi din D205 deși impozitul a fost efectiv achitat."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Ce faci dacă impozitul pe dividende a fost plătit, dar beneficiarul lipsește din D205?

D205 e declarația informativă prin care se raportează, pe fiecare beneficiar, dividendul distribuit, cel plătit și impozitul reținut. Când un dividend a fost distribuit într-un an dar plătit abia în ianuarie anul următor — sau plătit chiar în același an, dar aproape de final —, apar situații în care impozitul ajunge corect la buget, dar beneficiarul nu apare în declarația la care contabilul se aștepta.

## Temeiul legal

::: ghid-temei
„(7) Veniturile sub formă de dividende [...] se impozitează cu o cotă de 16% din suma acestora, impozitul fiind final. Obligația calculării și reținerii impozitului pe veniturile sub formă de dividende revine persoanelor juridice, odată cu plata dividendelor [...] Termenul de virare a impozitului este până la data de 25 inclusiv a lunii următoare celei în care se face plata. În cazul dividendelor/câștigurilor obținute ca urmare a deținerii de titluri de participare, distribuite, dar care nu au fost plătite acționarilor/asociaților/investitorilor până la sfârșitul anului în care s-a aprobat distribuirea acestora, impozitul pe dividende/câștig se plătește până la data de 25 ianuarie inclusiv a anului următor distribuirii."
— Codul fiscal (Legea 227/2015), art. 97 alin. (7) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)

„Impozitul aferent dividendelor distribuite, dar care nu au fost plătite acționarilor sau asociaților până la sfârșitul anului în care s-a aprobat distribuirea acestora se cuprinde în declarația aferentă perioadei în care s-a aprobat distribuirea dividendelor."
— OPANAF 179/2022 (instrucțiunile de completare D205/D207), Cap. V (sursă: anaf_surse/opanaf_179_2022_d205_d207_baza.txt)
:::

Ce spun cele două texte, puse cap la cap:

- Legea leagă scadența plății impozitului de **momentul plății efective** a dividendului către beneficiar — dacă plata are loc anul următor distribuirii, impozitul se plătește până la 25 ianuarie, nu în anul distribuirii.
- Instrucțiunile D205 spun însă, explicit, că impozitul aferent unui dividend **distribuit dar neplătit** până la 31 decembrie **se raportează în declarația anului în care s-a aprobat distribuirea** — adică beneficiarul trebuie să apară în D205 al anului distribuirii, chiar dacă plata (și, deci, reținerea/virarea impozitului) se face abia anul următor.
- Dacă un beneficiar lipsește din D205 în ciuda faptului că impozitul a fost plătit, cauza cea mai probabilă e că declarația a fost generată luând în calcul doar dividendele **efectiv plătite** în anul de raportare, fără să adauge separat beneficiarii cu dividend distribuit dar neplătit la 31 decembrie — exact situația pe care instrucțiunea de mai sus o cere inclusă.

## Ce se greșește în practică

- Se generează D205 exclusiv din sumele plătite efectiv în anul de raportare, ignorând dividendele distribuite dar neplătite până la 31 decembrie, care ar trebui incluse separat, conform instrucțiunii citate mai sus.
- Se presupune că „impozitul a fost plătit" înseamnă automat că beneficiarul e corect reflectat în D205 — cele două lucruri (plata la buget și raportarea informativă a beneficiarului) urmează reguli de temporizare diferite.
- Se lasă declarația anului distribuirii „goală" pentru beneficiarul respectiv și se speră că apare automat în declarația anului următor, cel al plății — riscând ca obligația să nu fie raportată corect în niciunul din cei doi ani.

## Ce face iConta.eu

Generatorul D205 (`core/d205.py`) construiește baza de impozitare **strict din dividendul plătit** din contul 457 (`baza1 = platit`), nu din cel distribuit — deci un dividend distribuit, de exemplu, în decembrie, dar neplătit până la 31 decembrie, **nu produce niciun beneficiar** în D205-ul acelui an. Asta contrazice direct regula de mai sus din instrucțiunile D205, care cere includerea lui în declarația anului distribuirii. Situația inversă — dividend distribuit într-un an, plătit eșalonat sau integral anul următor — e tratată corect: aplicația atribuie fiecărei tranșe de plată cota de impozit de la data distribuirii corespunzătoare (nu cota din anul plății), prin motorul de atribuire FIFO al distribuirilor.

Concret, dacă impozitul a fost plătit dar beneficiarul lipsește din D205, verificați dacă acel dividend a fost distribuit într-un an și beneficiarul urma să fie raportat, conform normei, în declarația anului distribuirii, nu al plății — pentru acest caz, aplicația nu adaugă automat beneficiarul. Funcția internă `d205.genereaza()` acceptă, tehnic, un parametru `manual` pentru suprascrierea listei de beneficiari, dar adaptorul din `core/declaratii_api.py` care generează efectiv D205 din aplicație **nu îl transmite** (spre deosebire de D101, D300, D390 sau D212, unde `manual` chiar ajunge din cerere la generator) — deci, la acest moment, nu există nicio cale prin aplicație de a introduce manual acel beneficiar în D205. Obligația trebuie urmărită și raportată separat de contabil, în afara fluxului D205 al aplicației, până când acest gol e acoperit.

[iConta.eu](/)
