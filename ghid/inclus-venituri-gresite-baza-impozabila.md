---
title: "Ce fac dacă am inclus venituri greșite în baza impozabilă micro?"
description: Dacă baza impozabilă micro declarată prin D100 a inclus venituri care ar fi trebuit excluse (de exemplu, diferențe de curs valutar), corectarea se face prin formularul 710, cu suma corectă recalculată — nu prin editarea directă a declarației deja depuse.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Ce fac dacă am inclus venituri greșite în baza impozabilă micro?

Baza impozabilă a impozitului micro nu e „toate veniturile din balanță", ci veniturile din anumite conturi, din care legea scade explicit câteva categorii. Dacă o categorie exclusă a fost totuși inclusă din greșeală — de exemplu, venituri din diferențe de curs valutar — impozitul declarat a fost mai mare decât cel corect, iar corecția se face prin declarație rectificativă.

## Temeiul legal

::: ghid-temei
Baza impozabilă micro exclude, printre altele, „veniturile din diferențe de curs valutar" (art. 53 alin. (1) lit. h) și „veniturile financiare aferente creanțelor și datoriilor cu decontare în funcție de cursul unei valute, rezultate din evaluarea sau decontarea acestora" (lit. i) — Codul fiscal, art. 53 alin. (1). Corectarea unei sume greșit declarate în D100 se face prin formularul 710 „Declarație rectificativă" — OPANAF 587/2016, Anexa 5, Capitolul I.
:::

## Categorii tipic incluse din greșeală

Art. 53 alin. (1) enumeră, la lit. a)-o), categoriile de venituri excluse din baza impozabilă micro — greșeala frecventă e includerea, fără verificare, a unor venituri din clasele 75x/76x care ar trebui excluse, cum sunt cele de la lit. h) și i) (diferențe de curs valutar, venituri financiare legate de creanțe/datorii în valută). O sursă tehnică a acestei greșeli: preluarea automată a **întregii** clase de conturi 76x în baza impozabilă, fără o filtrare separată a conturilor 765 (diferențe de curs) sau 766, dacă evidența nu le separă corect.

## Cum se corectează

Se recalculează baza corectă pentru trimestrul afectat (venituri conform 70x+75x+76x, minus 709, minus categoriile excluse la art. 53 alin. (1) care au fost incluse din greșeală), se determină diferența față de suma declarată inițial și se depune formularul 710, cu suma corectă a impozitului — nu prin editarea directă a D100 deja depuse.

## Ce se greșește în practică

- Se include în bază toată clasa 76x, fără să se verifice care venituri din ea sunt excluse explicit de art. 53 alin. (1) lit. h)/i).
- Se corectează doar în evidența contabilă internă, fără depunerea efectivă a formularului 710 — declarația oficială rămâne, în continuare, cea greșită.
- Se presupune că orice corecție ulterioară implică automat o sancțiune — dacă rezultă o sumă de recuperat (impozit plătit în plus), corecția e în favoarea contribuabilului, nu generează penalități.

## Ce face iConta.eu

Verificat direct în cod: baza impozabilă micro calculată de aplicație (`core/repo_d100.py`) include întreaga clasă de conturi 76x (venituri financiare), fără o excludere explicită a conturilor 765/766 pentru diferențele de curs valutar cerute de art. 53 alin. (1) lit. h)/i). Dacă firma are astfel de venituri semnificative în 76x, verificați manual dacă au fost corect excluse din baza declarată — dacă nu, corecția se face prin ecranul formularului 710 (`core/d710.py`), cu suma recalculată corect.

[iConta.eu](/)
