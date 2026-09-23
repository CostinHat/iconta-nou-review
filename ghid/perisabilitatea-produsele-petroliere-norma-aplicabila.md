---
title: "Perisabilitatea la produsele petroliere: normă aplicabilă"
description: Mecanismul de calcul al perisabilității e același indiferent de grupa de marfă, dar coeficientul aplicabil produselor petroliere se stabilește din anexa HG 831/2004, nu dintr-un procent general de perisabilitate.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Perisabilitatea la produsele petroliere: normă aplicabilă

Ca la orice marfă în procesul de comercializare, perisabilitatea la produsele petroliere se calculează prin aplicarea unui coeficient la valoarea intrărilor — nu există o formulă separată pentru această categorie. Ce diferă e strict procentul de limită, specific grupei de produse petroliere, stabilit prin anexa HG 831/2004.

## Temeiul legal

::: ghid-temei
„Se aprobă Normele privind limitele admisibile de perisabilitate la mărfuri în procesul de comercializare, prevăzute în anexa care face parte integrantă din prezenta hotărâre."

*(HG nr. 831/2004, art. 1)*
:::

## Ce e important de reținut la produsele petroliere

Mecanismul de calcul e identic celui aplicat oricărei alte grupe de mărfuri:

`limita = valoare_intrări × procent_limită / 100`, iar `deductibil = min(pierdere_constatată, limita)`.

Diferența specifică produselor petroliere e doar procentul de limită aplicabil — acesta se regăsește în anexa HG 831/2004, pe grupa exactă de produse petroliere, și nu poate fi preluat prin analogie de la o altă grupă de marfă. Condițiile documentare rămân aceleași: verificare faptică, aprobarea administratorului, proces-verbal.

## Ce se greșește în practică

- Se aplică prin analogie procentul de perisabilitate al altei grupe de mărfuri (de exemplu alimente), presupunând că e apropiat de cel al produselor petroliere.
- Se calculează limita la valoarea vândută sau la stocul final, nu la valoarea intrărilor din perioadă.
- Se omite proba faptică (măsurătoare, inventariere) specifică manipulării produselor petroliere, ceea ce face dificil de susținut încadrarea în limita legală în caz de control.

## Ce face iConta.eu

Motorul F066 (`core/perisabilitati.py`) tratează toate grupele de mărfuri identic — calculul, separarea deductibil/nedeductibil și eventuala ajustare de TVA nu depind de tipul de produs, ci exclusiv de procentul de limită introdus de contabil în câmpul „Procent limită HG 831/2004 (%)". Aplicația nu conține coeficientul specific produselor petroliere din anexele HG 831/2004 — acesta trebuie verificat direct în hotărâre, în Monitorul Oficial, și introdus manual.

[iConta.eu](/)
