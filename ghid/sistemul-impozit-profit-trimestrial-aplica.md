---
title: "Sistemul de impozit pe profit trimestrial: cum se aplică în 2026"
description: "Care firme aplică plăți anticipate trimestriale calculate pe baza anului precedent și care aplică impozitul pe profit trimestrial pe profitul contabil efectiv, în 2026."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Sistemul de impozit pe profit trimestrial: cum se aplică în 2026

„Impozit pe profit trimestrial" acoperă, de fapt, două mecanisme diferite din Codul fiscal: plăți anticipate trimestriale calculate pe baza impozitului anului precedent (regula generală) și impozit calculat trimestrial pe profitul contabil efectiv (regula pentru firmele nou-înființate, cu pierdere fiscală anterioară, ieșite din inactivitate temporară sau foste micro). Confuzia dintre cele două produce cele mai multe greșeli de calcul.

## Temeiul legal

::: ghid-temei
„(6) Contribuabilii, alții decât cei prevăzuți la alin. (4) și (5), aplică sistemul de declarare și plată prevăzut la alin. (1) în anul pentru care se datorează impozit pe profit, dacă în anul precedent se încadrează în una dintre următoarele situații: a) au fost nou-înființați, cu excepția contribuabililor nou-înființați ca efect al unor operațiuni de reorganizare efectuate potrivit legii; b) au înregistrat pierdere fiscală sau nu au datorat impozit pe profit anual (...); c) s-au aflat în inactivitate temporară sau au declarat pe propria răspundere că nu desfășoară activități la sediul social/sediile secundare (...); d) au fost plătitori de impozit pe veniturile microîntreprinderilor."
— Legea 227/2015, art. 41 alin. (6) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Cele două regimuri, pentru 2026:

- **Regula generală** (alin. (8)): firmele „stabile" (fără niciuna dintre situațiile de mai jos) calculează plata anticipată trimestrială ca **1/4 din impozitul pe profit al anului precedent**, actualizat cu indicele prețurilor de consum, cu termen 25 a lunii următoare trimestrului (25 decembrie pentru trimestrul IV).
- **Regula pe profitul efectiv** (alin. (1), aplicabilă prin trimitere de la alin. (6)): firmele nou-înființate, cele cu pierdere fiscală sau fără impozit datorat în anul precedent, cele ieșite din inactivitate temporară și fostele plătitoare de impozit micro calculează și plătesc impozitul **trimestrial, pe profitul contabil efectiv** al fiecărui trimestru, nu pe baza anului precedent.
- O firmă ex-micro care trece la profit în 2026, de exemplu, intră direct în regula de la lit. d) — calculează impozitul pe profitul trimestrial real, nu pe o estimare bazată pe impozitul din anul în care era la micro (care oricum era alt tip de impozit, pe venituri, nu pe profit).

## Ce se greșește în practică

- Se aplică formula „1/4 din anul precedent" și la o firmă nou-înființată sau ex-micro, deși acestea intră explicit sub regula profitului trimestrial efectiv (alin. (6)), nu sub regula generală (alin. (8)).
- Se ignoră situația specifică a inactivității temporare — o firmă reluată din inactivitate aplică regula profitului efectiv, nu regula anului precedent, chiar dacă avea un istoric de impozit înainte de inactivitate.
- Se presupune că trecerea de la micro la profit „moștenește" automat regula generală de plăți anticipate — de fapt, art. 41 alin. (6) lit. d) o exclude explicit, tocmai pentru că anul precedent nu a avut impozit pe profit de la care să se calculeze 1/4.

## Ce face iConta.eu

La data acestui ghid, iConta.eu **nu decide automat** care dintre cele două regimuri (plăți anticipate pe anul precedent sau impozit pe profitul trimestrial efectiv) se aplică unei firme — încadrarea corectă, pe baza situației din anul precedent (nou-înființată, pierdere fiscală, inactivitate temporară, fostă micro), rămâne o verificare a contabilului. Aplicația generează declarația de impozit pe profit (D101) pe baza regimului configurat și a datelor contabile efective introduse.

[iConta.eu](/)
