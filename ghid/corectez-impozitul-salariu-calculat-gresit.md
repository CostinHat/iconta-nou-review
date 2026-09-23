---
title: "Cum corectez impozitul pe salariu calculat greșit?"
description: "Ordinea corectă de calcul a impozitului de 10% pe venitul din salarii și cele mai frecvente cauze ale unei baze impozabile greșite."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum corectez impozitul pe salariu calculat greșit?

Impozitul pe venitul din salarii pare simplu — o cotă unică de 10% — dar baza pe care se aplică depinde de mai mulți pași anteriori: facilitatea fiscală, CAS, CASS și deducerea personală. O eroare la oricare dintre aceștia se propagă direct în impozit.

## Temeiul legal

::: ghid-temei
Codul fiscal, art.64 alin.(1) / art.78: impozitul pe venitul din salarii se calculează cu cota de **10%**, aplicabilă din 01.01.2018, asupra bazei de calcul rămase după reținerile legale (CAS, CASS) și deducerea personală.
:::

Ordinea de calcul, așa cum e implementată în motorul de calcul: **facilitate (dacă se aplică) → CAS 25% → CASS 10% → deducere personală → impozit 10% pe baza impozabilă → net**. Dacă vreunul dintre acești pași e inversat sau omis, impozitul rezultat e greșit chiar dacă cota de 10% a fost aplicată corect aritmetic.

Când se aplică facilitatea pentru salariul minim (OUG 89/2025 art.III, respectiv OUG 156/2024 art.LXVI pentru prima jumătate a lui 2026), suma scutită — 300 lei/lună până la 30.06.2026, apoi 200 lei/lună — nu intră deloc în calculul impozitului, dacă sunt îndeplinite cumulativ 4 condiții: normă întreagă, funcție de bază, salariul de bază contractual egal cu salariul minim, venitul brut total (fără tichete) sub plafonul aferent (4.300 lei, respectiv 4.600 lei).

Deducerea personală (Codul fiscal art.77) reduce, la rândul ei, baza impozabilă — scara variază de la 20% la 45% în funcție de numărul de persoane în întreținere, degresivă cu 0,5 puncte procentuale la fiecare tranșă de 50 lei peste salariul minim, până la un prag egal cu salariul minim + 2.000 lei.

## Ce se greșește în practică

Din categoria "greșeli frecvente" confirmate pentru acest tip de calcul: **brutul sub salariul minim pe normă întreagă** (care ar trebui să blocheze generarea declarației D112 ca dată suspectă) și **facilitățile fiscale nemarcate** — angajatul se califică pentru scutire, dar aceasta nu e bifată, deci impozitul se calculează pe o bază mai mare decât trebuie.

O greșeală conexă, frecventă manual: aplicarea impozitului înainte de scăderea deducerii personale, sau folosirea unei deduceri personale calculate pentru o altă lună (deducerea depinde de salariul minim valabil la data respectivă, iar în 2026 există două valori diferite ale salariului minim, cu ferestre distincte).

## Ce face iConta.eu

Motorul de calcul urmează strict ordinea de mai sus, iar toate valorile (cote, salariu minim, facilitate, plafoane) vin dintr-un registru intern "period-aware" — fiecare cifră e valabilă doar pentru intervalul ei de timp, cu temeiul legal atașat. Funcția care calculează deducerea personală cere obligatoriu data de referință a calculului și refuză explicit să ghicească luna curentă, tocmai pentru că deducerea (și salariul minim din spatele ei) diferă de la o lună la alta în 2026.

La generarea D112, aplicația refuză ca date suspecte un brut sub salariul minim pe normă întreagă — un control util pentru a prinde din timp o eroare care ar denatura și impozitul calculat.

[iConta.eu](/)
