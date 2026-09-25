---
title: "Cum verifici ultima D112 validă depusă la ANAF?"
description: "Diferența dintre «ultima D112 trimisă din contabilitate» și «ultima D112 confirmată de ANAF», și ce anume păstrează iConta.eu din fiecare depunere."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum verifici ultima D112 validă depusă la ANAF?

D112 se poate corecta oricând, din proprie inițiativă, prin depunerea unei declarații rectificative — iar fiecare rectificativă înlocuiește **integral** declarația anterioară, nu doar diferențele. Asta înseamnă că „ultima D112 valabilă" pentru o lună nu e neapărat prima trimisă, ci ultima rectificativă acceptată. E o distincție importantă și una separată: „valabilă în sistemul propriu de contabilitate" nu e automat totuna cu „confirmată de ANAF" — cele două se verifică diferit.

## Temeiul legal

::: ghid-temei
„2.1. Declaraţia privind obligaţiile de plată a contribuţiilor sociale, impozitului pe venit şi evidenţa nominală a persoanelor asigurate poate fi corectată de contribuabili din proprie iniţiativă, prin depunerea unei declaraţii rectificative.
2.4. Declaraţia rectificativă se completează integral, înscriindu-se toate datele şi informaţiile prevăzute de formular, inclusiv cele care nu diferă faţă de declaraţia iniţială."
— OPANAF 605/2026, Instrucțiuni de completare, pct. 2.1, 2.4 (sursă: anaf_surse/opanaf_605_2026_d112.txt)

„Data depunerii declarației fiscale prin mijloace electronice de transmitere la distanță este data înregistrării acesteia pe portal, astfel cum rezultă din mesajul electronic transmis de sistemul de tranzacționare a informațiilor, cu condiția validării conținutului declarației."
— Legea 207/2015 (Codul de procedură fiscală), art. 103 alin. (4) (sursă: anaf_surse/legea_207_2015_consolidat.txt)
:::

- Rectificativa D112 se completează **integral** (pct. 2.4) — dacă o secțiune corectă din declarația inițială nu e reluată în rectificativă, ea dispare din evidență, nu rămâne „moștenită" de la versiunea anterioară.
- Motivele pentru care se depune o rectificativă sunt explicit enumerate în instrucțiuni (pct. 2.2): corectarea impozitului/contribuțiilor, a elementelor de identificare a asiguratului, a datelor de stagiu de cotizare, a informațiilor despre concediile medicale etc.
- Confirmarea legală a depunerii vine din **mesajul electronic al portalului**, nu din faptul că declarația a fost „trimisă" dintr-un program de contabilitate — art. 103 alin. (4) leagă explicit data depunerii de mesajul de validare al sistemului de tranzacționare.

## Ce se greșește în practică

- Se crede că a doua rectificativă „completează" prima — de fapt o **înlocuiește** integral; o secțiune omisă din greșeală în rectificativă se pierde din evidența declarată, chiar dacă era corectă inițial.
- Se confundă „am trimis declarația" cu „ANAF a validat-o" — fără mesajul electronic de confirmare a validării conținutului, data depunerii legală nu e stabilită.
- Se verifică doar ce arată programul de contabilitate intern, fără a controla și recipisa/mesajul primit efectiv din portalul SPV/ANAF pentru acea depunere.

## Ce face iConta.eu

La fiecare depunere reușită (inclusiv D112), iConta.eu persistă intern XML-ul trimis și rândurile calculate, într-un jurnal append-only, versionat corect: fiecare depunere nouă pentru același tenant/an/lună/tip primește un număr de depunere incrementat, iar declarația anterioară rămâne păstrată alături de cea nouă, nu suprascrisă. Acest mecanism garantează că motoarele interne de control (control încrucișat D-vs-D) folosesc mereu versiunea corectă și completă, calculată la ultima depunere.

Important de spus onest: acest jurnal **nu confirmă acceptarea la ANAF**. Starea „depusă" înseamnă, la nivel de cod, doar că declarația a trecut prin coada internă de procesare a cabinetului — nu că a fost validată de portalul ANAF. Există în cod un câmp rezervat pentru un index de confirmare din partea conectorului SPV, dar nu s-a putut confirma că el e populat sistematic la fiecare depunere reală. Ce poți vedea în aplicație — tipul, anul, luna și data ultimei depuneri pentru fiecare declarație — e expus prin listele destinate portalului clienților și prin rapoartele de documente generate pentru portal, construite pe baza acestei evidențe interne (fără să afișeze vreodată XML-ul sau rândurile calculate ale declarației). Verificarea propriu-zisă a acceptării la ANAF rămâne de făcut separat, în portalul SPV.

[iConta.eu](/)
