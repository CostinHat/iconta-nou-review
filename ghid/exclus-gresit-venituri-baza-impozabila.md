---
title: "Ce fac dacă am exclus greșit venituri din baza impozabilă micro?"
description: Dacă venituri care ar fi trebuit incluse în baza impozabilă micro au fost excluse din greșeală, impozitul declarat a fost mai mic decât cel corect — se corectează prin formularul 710, iar dacă diferența ajunge cu întârziere, se calculează dobânzi și penalități de la scadența inițială.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Ce fac dacă am exclus greșit venituri din baza impozabilă micro?

Situația inversă celei în care s-au inclus greșit venituri excluse de lege: dacă din baza impozabilă a impozitului micro s-au scos venituri care, de fapt, trebuiau incluse, impozitul declarat și plătit a fost mai mic decât cel corect. Aici corectarea nu e doar o formalitate — implică, de regulă, o plată suplimentară, posibil cu dobânzi și penalități de întârziere.

## Temeiul legal

::: ghid-temei
Baza impozabilă micro e „veniturile din orice sursă", din care se scad **doar** categoriile enumerate explicit la art. 53 alin. (1) lit. a)-o) — Codul fiscal. Corectarea unei sume greșit declarate în D100 se face prin formularul 710 „Declarație rectificativă" — OPANAF 587/2016, Anexa 5, Capitolul I. Diferențele de întârziere la plată se calculează potrivit art. 174-183 din Codul de procedură fiscală (Legea 207/2015).
:::

## Când apare această greșeală

Legea exclude din baza impozabilă micro doar categoriile enumerate explicit la art. 53 alin. (1) — orice venit care nu se încadrează la vreuna dintre acele litere rămâne, implicit, în bază. Greșeala tipică: se exclude un venit „din prudență" sau din confuzie cu regulile de la impozitul pe profit (unde există mai multe categorii de venituri neimpozabile), deși legea specifică pentru micro nu prevede acea excludere.

## Cum se corectează

Se recalculează baza corectă pentru trimestrul afectat, incluzând veniturile excluse din greșeală, se determină diferența de impozit rezultată și se depune formularul 710, cu suma corectă. Dacă diferența implică o plată suplimentară, iar aceasta ajunge la buget după scadența inițială a trimestrului respectiv (25 a lunii următoare trimestrului), se datorează dobândă de 0,02%/zi și penalitate de întârziere de 0,01%/zi, calculate **de la scadența inițială**, nu de la data depunerii corecției.

## Ce se greșește în practică

- Se corectează doar suma de plată, fără să se recalculeze corect dobânzile/penalitățile de întârziere de la scadența inițială a trimestrului.
- Se presupune că orice excludere „logică" din perspectiva contabilă (de exemplu, un venit considerat neobișnuit sau nerecurent) e automat exclusă și fiscal — la impozitul micro contează strict lista limitativă de la art. 53 alin. (1), nu criterii contabile suplimentare.
- Se amână corectarea până la finalul anului, deși obligația de rectificare (și eventualele penalități) curg din momentul în care eroarea a apărut, nu din momentul descoperirii ei.

## Ce face iConta.eu

Corectarea unei sume declarate greșit în D100 se face prin ecranul formularului 710 (`core/d710.py`), care calculează diferența dintre suma declarată inițial și suma corectă pentru obligația de cod 121. Calculul dobânzilor și penalităților de întârziere pentru diferența plătită cu întârziere rămâne o verificare separată, pe baza scadenței inițiale a trimestrului corectat, nu una automatizată în fluxul de corecție D710 al aplicației.

[iConta.eu](/)
