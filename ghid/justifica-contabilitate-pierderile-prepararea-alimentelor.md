---
title: Cum se justifică în contabilitate pierderile din prepararea alimentelor?
description: Pierderile din prepararea alimentelor sunt, legal, pierderi tehnologice — justificate printr-o normă de consum proprie stabilită de firmă (rețetar, fișă tehnologică), nu prin coeficientul de perisabilitate al HG 831/2004.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum se justifică în contabilitate pierderile din prepararea alimentelor?

Pierderile care apar la prepararea alimentelor (curățare, tranșare, gătire) nu sunt perisabilități în sensul HG 831/2004 — acea hotărâre vizează mărfuri aflate în procesul de comercializare, nu materii prime transformate printr-un proces de producție sau prestare. Cadrul legal corect e cel al pierderilor tehnologice, justificate printr-o normă de consum proprie a firmei, nu printr-un procent stabilit de o hotărâre de guvern.

## Temeiul legal

::: ghid-temei
„Următoarele cheltuieli au deductibilitate limitată: [...] d) scăzămintele, perisabilitățile, pierderile rezultate din manipulare/depozitare, potrivit legii; e) pierderile tehnologice care sunt cuprinse în norma de consum proprie necesară pentru fabricarea unui produs sau prestarea unui serviciu;"

*(Codul fiscal — Legea nr. 227/2015, art. 25 alin. (3) lit. d) și e))*
:::

## Lit. d) și lit. e): două categorii distincte

Textul legal separă explicit cele două situații: perisabilitățile (lit. d) se justifică „potrivit legii" — adică prin HG 831/2004, cu coeficient pe grupă de marfă comercializată. Pierderile tehnologice (lit. e) se justifică prin „norma de consum proprie" a contribuabilului — un standard stabilit intern de firmă pentru fabricarea unui produs sau prestarea unui serviciu, nu un procent legal fix. O bucătărie care prepară mâncare desfășoară, conceptual, un proces de producție/prestare, deci pierderile ei intră mai degrabă la lit. e).

## Cum se documentează norma de consum proprie

Neexistând un procent legal impus, justificarea practică ține de documentația internă a firmei: un rețetar sau o fișă tehnologică pe fiecare preparat, care stabilește cantitatea de materie primă necesară pentru o porție, inclusiv pierderile normale de preparare (curățare, evaporare, tranșare). Norma astfel stabilită trebuie să fie rezonabilă și documentată — nu o justificare ad-hoc, la nevoie.

## Ce se greșește în practică

- Se aplică un coeficient de perisabilitate HG 831/2004 la materii prime consumate în bucătărie, deși hotărârea vizează mărfuri în procesul de comercializare, nu materii prime transformate.
- Se lasă pierderile de preparare nedocumentate, fără rețetar sau fișă tehnologică, ceea ce face imposibilă justificarea lor ca „normă de consum proprie" în caz de control.
- Se confundă modulul de rețete pentru vânzarea de porții (consum normal la vânzare) cu problema pierderilor/risipei din procesul de preparare — sunt lucruri diferite.

## Ce face iConta.eu

Aplicația nu are un modul dedicat calculului sau limitării unei norme de consum propriu pentru pierderi tehnologice — nu există în cod nicio funcție care să calculeze o astfel de normă. Modulul de rețete HoReCa (`core/retete.py`) tratează consumul normal de ingrediente la vânzarea unei porții (ieșire de stoc la cost mediu ponderat și calcul de food cost), nu pierderea sau risipa din procesul de preparare. Stabilirea și documentarea normei de consum proprie (rețetar, fișă tehnologică) rămân, integral, o decizie și o responsabilitate internă a firmei.

[iConta.eu](/)
