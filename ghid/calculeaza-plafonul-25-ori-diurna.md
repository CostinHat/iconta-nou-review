---
title: "Cum se calculează plafonul de 2,5 ori pentru diurnă?"
description: "Formula legală a primului prag din plafonul de diurnă neimpozabilă — 2,5 ori nivelul indemnizației bugetare — și cum interacționează cu al doilea prag."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se calculează plafonul de 2,5 ori pentru diurnă?

„2,5 ori diurna bugetară" e formula pe care majoritatea contabililor o știu pe de rost, dar care nu funcționează izolat — legea o combină cu un al doilea prag, iar plafonul final e cel mai mic dintre cele două. Aici ne oprim la mecanica exactă a primului prag: cele 2,5 ori.

## Temeiul legal

::: ghid-temei
„pentru partea care depășește plafonul neimpozabil stabilit astfel: (i) în țară, 2,5 ori nivelul legal stabilit pentru indemnizație, prin hotărâre a Guvernului, pentru personalul autorităților și instituțiilor publice, în limita a 3 salarii de bază corespunzătoare locului de muncă ocupat; [...] (ii) în străinătate, 2,5 ori nivelul legal stabilit pentru diurnă, prin hotărâre a Guvernului, pentru personalul român trimis în străinătate pentru îndeplinirea unor misiuni cu caracter temporar, în limita a 3 salarii de bază corespunzătoare locului de muncă ocupat."
— Codul fiscal, art. 76 alin. (2) lit. k) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Descompunerea formulei „2,5 ori":

- Baza de calcul este **nivelul legal al indemnizației/diurnei pentru personalul bugetar**, stabilit prin hotărâre de guvern — 23 lei/zi pentru intern (de la 1 aprilie 2023), respectiv valorile din nomenclatorul pe țări pentru extern (HG 518/1995).
- **Pragul 1 = 2,5 × nivelul bugetar** — pentru intern, 2,5 × 23 lei = 57,5 lei/zi.
- Acest prag **nu este plafonul final** — legea îl combină explicit „în limita a 3 salarii de bază", deci pragul 2,5× e valabil doar dacă nu depășește al doilea prag (3 salarii de bază raportate la zilele lucrătoare din lună). Plafonul neimpozabil efectiv e minimul dintre cele două.
- Formula e identică pentru intern și extern — diferă doar baza de calcul (indemnizația bugetară internă vs. diurna pe țară din nomenclatorul extern).

## Ce se greșește în practică

- Se aplică 2,5× ca plafon final, fără să se mai verifice al doilea prag (3 salarii de bază/zile lucrătoare) — pentru un salariu mic, acesta poate fi mai restrictiv și devine plafonul real.
- Se calculează 2,5× dintr-o valoare greșită a diurnei bugetare (de exemplu, se folosește 20 lei în loc de 23 lei pentru o deplasare din 2026, sau invers, pentru o deplasare din 2022).
- Se aplică factorul 2,5 și la alte beneficii neimpozabile (de exemplu clauza de mobilitate, plafonată la 33% din salariu, conform art. 76 alin. (4^1) CF) — sunt categorii diferite, cu formule diferite, nu se amestecă.

## Ce face iConta.eu

Formula 2,5× este implementată exact conform textului de mai sus, ca primă componentă a calculului din funcția `plafon_diurna` (`core/deconturi.py`): aplicația calculează `2,5 × diurna_bugetară` și îl compară automat cu al doilea prag (3×salariu/zile lucrătoare), reținând minimul. Calculul e „period-aware" — alege automat 20 sau 23 lei ca bază, în funcție de data la care se raportează plafonul.

Ca și în cazul celorlalte întrebări despre plafon, trebuie spus clar: acest calcul **nu are un ecran dedicat în iConta**. Formula de 2,5× nu e vizibilă nicăieri în interfața de „Decont deplasare / diurnă" — există doar ca funcție de calcul internă, apelabilă azi doar prin API, nu prin niciun buton din aplicație. Un contabil care vrea să vadă rezultatul acestei formule pentru un caz concret trebuie să-l calculeze manual.

[iConta.eu](/)
