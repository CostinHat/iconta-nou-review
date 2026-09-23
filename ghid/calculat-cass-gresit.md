---
title: "Ce fac dacă am calculat CASS greșit?"
description: "Cum se calculează corect CASS (10%) în raport cu facilitatea salariului minim și podeaua de contribuții, și cum recuperezi o eroare de calcul."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Ce fac dacă am calculat CASS greșit?

Contribuția de asigurări sociale de sănătate (CASS) e una dintre cele mai frecvente surse de erori la stat de plată, mai ales când intervin facilitatea fiscală pentru salariul minim sau regula "podelei" de contribuții. Iată ce spune legea și unde apar cel mai des greșelile.

## Temeiul legal

::: ghid-temei
Codul fiscal, art.156: CASS se calculează cu cota de **10%**, aplicabilă din 01.01.2018.

Codul fiscal, art.146 alin.(5^6): *„...contribuția CAS nu poate fi mai mică decât CAS calculat pe salariul minim, în baza unui contract individual de muncă cu normă întreagă SAU cu timp parțial”* — condiția legală e venitul sub minim, nu tipul de normă. Regula echivalentă se aplică și CASS, conform art.146 alin.(5^6)-(5^9) coroborat cu art.168 alin.(6^1).
:::

CASS se aplică asupra bazei rămase după eventuala scădere a facilității pentru salariul minim (dacă angajatul se califică), **înainte** de deducerea personală și de impozitul de 10%. Ordinea din motorul de calcul e: facilitate (dacă se aplică) → CAS 25% → CASS 10% → deducere personală → impozit 10% pe baza impozabilă → net.

Exemplu simplu, fără facilitate aplicată: pentru un brut de 4.325 lei (salariul minim valabil din 1 iulie 2026), CASS = 10% × 4.325 = **432,50 lei**. Atenție: în 2026 există două valori ale salariului minim — 4.050 lei (ianuarie–iunie) și 4.325 lei (iulie–decembrie) — cu facilități și plafoane diferite pe fiecare fereastră, așa că orice exemplu trebuie legat de perioada concretă.

Separat de CAS/CASS, angajatorul datorează CAM (contribuția asiguratorie pentru muncă) de 2,25% — aceasta e o cheltuială a angajatorului, nu o reținere din salariul brut, deci nu trebuie confundată cu CASS la verificarea unei erori.

## Ce se greșește în practică

Cele mai frecvente greșeli semnalate pentru acest tip de calcul sunt: **brutul introdus sub salariul minim pe normă întreagă** (fără o excepție legală aplicabilă) și **facilitățile fiscale nemarcate** — adică angajatul se califică pentru scutirea de 200/300 lei, dar facilitatea nu e bifată, ceea ce duce la CASS calculat pe o bază mai mare decât ar trebui (sau invers, aplicată eronat cuiva care nu îndeplinește toate cele 4 condiții cumulative).

O altă greșeală tipică e ignorarea regulii "podelei": CASS nu poate fi calculată sub nivelul corespunzător salariului minim, indiferent dacă norma e întreagă sau parțială — cu excepția a 5 categorii: elevi/studenți sub 26 de ani, ucenici sub 18 ani, persoane cu dizabilități, pensionari la limită de vârstă și cazul cumulului de contracte cu bază cumulată cel puțin egală cu minimul.

## Ce face iConta.eu

Toate cotele și pragurile (CAS, CASS, salariul minim, facilitatea, plafoanele) nu sunt scrise fix în codul de calcul — vin dintr-un registru intern actualizat pe perioade, fiecare valoare având propriul temei legal atașat (act, articol, alineat, text citat). Astfel, motorul aplică automat valoarea corectă pentru luna la care se face calculul.

La generarea declarației D112, aplicația refuză ca date suspecte situațiile în care brutul introdus e sub salariul minim pe normă întreagă — un prim semnal că ceva nu a fost calculat sau introdus corect, inclusiv la CASS. Regula podelei pentru contribuții sub minim este implementată explicit în motorul de calcul, dar echipa a documentat-o ca o interpretare (proratarea pragului pe fereastra activă a lunii), nu ca text explicit al legii — merită tratată ca atare dacă recalculezi manual o situație contestată.

[iConta.eu](/)
