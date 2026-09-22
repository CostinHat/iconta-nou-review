---
title: Cum corectez salariul brut calculat greșit?
description: Corectarea unui salariu dintr-o lună trecută se face aplicând regulile fiscale valabile la data acelui venit, nu regulile curente - inclusiv, dacă în lună au coexistat mai multe valori ale salariului minim, se ia în calcul cea mai mică dintre ele.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Cum corectez salariul brut calculat greșit?

Când descoperiți o eroare la un salariu dintr-o lună anterioară și trebuie să emiteți o rectificativă sau o adeverință recalculată, principiul de bază este simplu de formulat, dar ușor de greșit în practică: recalculul se face cu regulile fiscale valabile ATUNCI, la data realizării venitului, nu cu regulile de azi.

## Temeiul legal

::: ghid-temei
**Codul fiscal, Articolul 77, alin.(3):** *"Deducerea personală de bază se acordă pentru persoanele fizice care au un venit lunar brut de până la 2.000 de lei peste nivelul salariului de bază minim brut pe țară garantat în plată... În situația în care, în cursul aceleiași luni, se utilizează mai multe valori ale salariului minim brut pe țară, se ia în calcul valoarea cea mai mică a salariului minim brut pe țară."*
:::

## De ce contează data exactă a venitului

Cotele și pragurile fiscale (CAS, CASS, impozit, salariul minim, facilitatea pentru salariul minim, plafonul acesteia, plafonul tichetelor de masă) nu sunt fixe în timp — se modifică periodic prin acte normative noi, fiecare cu propria dată de intrare în vigoare. O corectare pe o lună din trecut trebuie să folosească exact valorile valabile în luna respectivă, nu valorile curente. De exemplu, dacă recalculați un salariu din decembrie 2025, salariul minim folosit trebuie să fie cel valabil atunci (4.050 lei, în vigoare de la 01.01.2025), nu cel valabil din iulie 2026 (4.325 lei).

O situație specifică, prevăzută explicit de lege: dacă în cursul aceleiași luni au fost în vigoare mai multe valori ale salariului minim (de exemplu, o modificare legislativă la mijlocul lunii, sau o rectificativă care schimbă parțial condițiile contractului), pentru calculul deducerii personale se ia în calcul valoarea CEA MAI MICĂ dintre acele valori ale salariului minim din lună — nu media, nu cea mai recentă.

::: ghid-exemplu
O rectificativă recalculează salariul unui angajat pentru o lună din 2025, unde salariul minim în vigoare era de 4.050 lei. Chiar dacă recalcularea se face în 2026, când salariul minim curent este de 4.325 lei, deducerea personală și celelalte praguri se calculează folosind valoarea de 4.050 lei, valabilă în luna respectivă.
:::

## Ce se greșește în practică

- Se recalculează salariul dintr-o lună trecută folosind cotele și pragurile CURENTE (de la data corectării), în loc de cele valabile în luna respectivă a venitului.
- Se ignoră situația în care, în aceeași lună, au coexistat mai multe valori ale salariului minim, și se folosește ultima valoare cunoscută, în loc de cea mai mică.
- Se recalculează manual, "din memorie", cotele unei perioade trecute, riscând erori față de actul normativ exact aplicabil la acea dată.
- Se aplică regulile curente ale facilității salariului minim (de exemplu plafonul valabil azi) unei luni din trecut, unde plafonul era altul.

## Ce face iConta.eu

Motorul de calcul nu ține cotele fiscale (CAS, CASS, impozit, CAM, salariul minim, facilitatea și plafonul ei, plafonul tichetelor de masă) fixe în cod, ci le citește dintr-un registru intern care păstrează fiecare valoare împreună cu data de la care a intrat în vigoare și temeiul legal aferent. Fiecare regulă fiscală (deducere, facilitate, suprataxare, procente concediu medical) este, la rândul ei, implementată în variante separate pe perioade, iar un mecanism de selecție alege automat varianta valabilă la data de realizare a venitului recalculat. O rectificativă sau o adeverință pentru o lună trecută recalculează astfel automat cu regula fiscală de atunci, nu cu regula curentă — inclusiv regula "cea mai mică valoare a salariului minim din lună", aplicată corect atunci când în lună coexistă mai multe valori.

[iConta.eu](/)
