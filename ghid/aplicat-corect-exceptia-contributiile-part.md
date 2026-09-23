---
title: "Ce fac dacă nu am aplicat corect excepția de la contribuțiile pentru part-time?"
description: "Cele 5 categorii de angajați scutite de podeaua contribuțiilor la salariul minim, conform Codului fiscal."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Ce fac dacă nu am aplicat corect excepția de la contribuțiile pentru part-time?

Regula generală spune că CAS și CASS nu pot fi calculate sub nivelul corespunzător salariului minim, nici pentru normă întreagă, nici pentru normă parțială. Dar legea prevede și excepții exprese — iar aplicarea greșită a lor (fie omisă, fie acordată cuiva care nu se califică) duce direct la o eroare de calcul.

## Temeiul legal

::: ghid-temei
Codul fiscal, art.146 alin.(5^7): listează excepțiile de la regula podelei contribuțiilor — elevi/studenți sub 26 de ani, ucenici sub 18 ani, persoane cu dizabilități, pensionari la limită de vârstă, și cazul cumulului de contracte individuale de muncă cu bază de calcul cumulată cel puțin egală cu salariul minim.
:::

Aceste 5 categorii sunt singurele situații în care CAS/CASS pot fi calculate sub nivelul salariului minim pentru un angajat cu normă parțială (sau, teoretic, cu venit sub minim). În afara lor, se aplică podeaua descrisă la art.146 alin.(5^6): contribuțiile nu pot fi mai mici decât cele calculate pe salariul minim.

## Ce se greșește în practică

Două tipuri de erori simetrice: fie se aplică podeaua (deci se suprataxează) unui angajat care se încadrează de fapt la una din cele 5 excepții — de exemplu un student sub 26 de ani sau un pensionar la limită de vârstă —, fie se omite podeaua pentru un angajat care nu se califică la nicio excepție, rezultând contribuții sub minimul legal.

Cazul cumulului de contracte cere atenție suplimentară: excepția se aplică doar dacă baza de calcul **cumulată** din toate contractele e cel puțin egală cu salariul minim — o verificare care nu poate fi făcută corect dintr-un singur contract, izolat.

## Ce face iConta.eu

Motorul de calcul implementează regula podelei (pragul de referință fiind salariul minim, eventual redus cu facilitatea fiscală, dacă se aplică) ca interpretare documentată a echipei, nu ca literă explicită a legii, confirmată totuși de regula validatorului oficial (SP1B4_1). Verificarea corectă a celor 5 excepții — mai ales cea legată de cumulul de contracte — rămâne responsabilitatea celui care introduce datele salariatului, pe baza informațiilor din toate contractele acestuia.

[iConta.eu](/)
