---
title: "Cheltuieli nedeductibile 2026: ce nu se scade din impozitul pe profit"
description: Ce cheltuieli trebuie adăugate înapoi la calculul profitului impozabil în 2026 și cum le tratează D101 în iConta.eu — cu accent pe cheltuiala cu impozitul pe profit (cont 691) și pe sponsorizare.
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cheltuieli nedeductibile 2026: ce nu se scade din impozitul pe profit

O cheltuială nedeductibilă fiscal poate fi complet corectă contabil și, totuși, trebuie adăugată înapoi la profitul contabil brut pentru a obține profitul impozabil de pe D101. Cele mai frecvente două capcane confirmate în motorul de calcul al declarației sunt cheltuiala cu impozitul pe profit (cont 691) și depășirea plafonului de sponsorizare.

## Temeiul legal

::: ghid-temei
„dacă soldul debitor al contului 691 (cheltuiala cu impozitul pe profit) e >0 și rd.23 (P23, cheltuieli nedeductibile) e 0, se emite avertisment — cheltuiala e nedeductibilă (CF art.25 alin.(4) lit.a) și trebuie adăugată înapoi, altfel impozitul declarat iese subevaluat."
— sursă: `core/d101.py`, liniile 502–529, dosar de cercetare F027.

„Sponsorizare (P43) — dublă limită V5 (20% impozit, DUK) + V5-bis (0,75% cifră de afaceri, adăugat manual în cod fiindcă DUK verifică doar 20%), temei CF art.25 alin.(4) lit.i)"
— sursă: `core/d101.py`, liniile 179–188, dosar de cercetare F027.
:::

Practic, două reguli distincte se aplică simultan:

1. **Cheltuiala cu impozitul pe profit (cont 691)** este nedeductibilă potrivit art.25 alin.(4) lit.a) din Codul fiscal — se adaugă înapoi la baza impozabilă, indiferent cât de firesc pare că un impozit „reduce" rezultatul contabil.
2. **Sponsorizarea (art.25 alin.(4) lit.i))** are o dublă limită: 20% din impozitul pe profit datorat ȘI 0,75% din cifra de afaceri — se aplică plafonul mai mic dintre cele două, nu doar cel de 20%.

## Ce se greșește în practică

Cea mai comună greșeală este omiterea add-back-ului pentru cont 691: contabilul lasă cheltuiala cu impozitul „ca atare" în rulaj, fără s-o reintroducă la rândul de cheltuieli nedeductibile (P23/P34). Impactul nu e teoretic — pe un portofoliu monitorizat (tenant_005, 2025), omisiunea a redus impozitul declarat cu 2.432 lei, fără niciun semnal vizibil înainte de introducerea gardului automat.

A doua greșeală frecventă: verificarea sponsorizării doar prin plafonul de 20% din impozit, ignorând complet limita de 0,75% din cifra de afaceri — care poate fi, la firme mari, plafonul efectiv mai restrictiv.

## Ce face iConta.eu

Motorul D101 din iConta.eu verifică automat soldul contului 691: dacă e debitor și pozitiv, dar rândul P23 (cheltuieli nedeductibile) e completat cu 0, emite un avertisment explicit înainte de generarea declarației. Pentru sponsorizare, aplicația calculează ambele plafoane — cel de 20% din impozit (verificat și de validatorul oficial DUK) și cel de 0,75% din cifra de afaceri, adăugat manual în cod tocmai pentru că validatorul DUK verifică singur doar limita de 20%.

[iConta.eu](/)
