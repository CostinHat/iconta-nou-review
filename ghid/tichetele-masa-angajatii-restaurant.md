---
title: "Tichetele de masă pentru angajații din restaurant"
description: Regulile fiscale pentru tichetele de masă nu depind de domeniul de activitate al angajatorului — un angajat dintr-un restaurant primește tichete de masă după exact aceleași reguli ca oricare alt salariat.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Tichetele de masă pentru angajații din restaurant

Nu există o regulă fiscală distinctă pentru tichetele de masă acordate angajaților care lucrează într-un restaurant sau, mai general, în HoReCa — mecanismul de acordare, plafonul și taxarea sunt identice cu cele aplicabile oricărui alt salariat, indiferent de domeniul de activitate al angajatorului.

## Temeiul legal

::: ghid-temei
Legea 201/2025, art. I pct. 1: „valoarea nominală a unui tichet de masă nu poate depăși suma de 45 lei"; art. II alin. (1): se aplică începând cu drepturile aferente lunii noiembrie 2025.
:::

Plafonul de 45 lei/tichet e valabil pentru toate lunile din 2026 (a intrat în vigoare din noiembrie 2025 și nu s-a modificat de atunci). Dreptul la tichet se stabilește pe **zile efectiv lucrate** (HG 1045/2018, art. 10 alin. (1)) — nu se acordă pentru zile de concediu de odihnă, delegație/detașare, absențe motivate/nemotivate sau învoire. Legea nu face nicio distincție în funcție de sectorul de activitate al angajatorului: un angajat de restaurant care lucrează efectiv o zi are dreptul la tichet exact ca un angajat de birou.

## Ce se greșește în practică

- Se presupune că angajații din HoReCa nu au dreptul la tichete de masă pentru că, oricum, au acces la mâncare la locul de muncă — nu există niciun temei legal pentru o astfel de excludere; dreptul la tichet de masă e independent de accesul practic la hrană la locul de muncă.
- Se confundă tichetul de masă (Legea 165/2018 + HG 1045/2018) cu masa oferită efectiv angajatului în natură sau cu indemnizația de hrană în bani — acestea din urmă au un regim fiscal separat, cu reguli proprii, și nu se cumulează automat cu tichetele de masă pe aceleași zile.
- Se acordă tichet și pentru zilele de concediu de odihnă sau pentru absențe, ignorând excluderile explicite de la art. 10 alin. (1) din HG 1045/2018.

## Ce face iConta.eu

Motorul de salarizare (`core/pontaj.py` + `core/d112.py`) calculează numărul de tichete de masă din zilele efectiv lucrate conform pontajului confirmat al lunii, scăzând automat zilele de concediu de odihnă, delegație/detașare, absențe și învoire — mecanismul e identic pentru toți angajații, fără vreo condiționare de domeniul de activitate al firmei. Plafonul de 45 lei/tichet e ținut ca valoare unică validă pentru tot 2026. Dacă firma acordă direct masă sau indemnizație de hrană în bani, în loc de sau pe lângă tichete de masă, acel beneficiu se configurează separat — F133 acoperă strict fluxul tichetelor de masă, nu regimul indemnizației de hrană.

[iConta.eu](/)
