---
title: 'Plafonul de sponsorizare 2026: cum se calculează'
description: Plafonul rămâne, în 2026, minimul dintre 0,75% din cifra de afaceri și 20% din impozitul pe profit datorat — regulă neschimbată din 3 februarie 2022; se calculează ambii termeni și se reține cel mai mic.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Plafonul de sponsorizare 2026: cum se calculează

Nu există o regulă nouă pentru 2026 — plafonul de sponsorizare deductibil din impozitul pe profit se calculează la fel ca în orice an fiscal începând cu 3 februarie 2022. Formula are un singur mecanism, dar doi termeni care trebuie calculați amândoi, nu doar unul.

## Temeiul legal

::: ghid-temei
„i) ... contribuabilii care efectuează sponsorizări și/sau acte de mecenat, potrivit prevederilor Legii nr. 32/1994 privind sponsorizarea..., scad sumele aferente din impozitul pe profit datorat la nivelul valorii minime dintre următoarele:
1. valoarea calculată prin aplicarea a 0,75% la cifra de afaceri; pentru situațiile în care reglementările contabile aplicabile nu definesc indicatorul cifra de afaceri, această limită se determină potrivit normelor;
2. valoarea reprezentând 20% din impozitul pe profit datorat. [...]”

— *Codul fiscal, art. 25 alin. (4) lit. i), forma actuală (de la 03.02.2022, aplicabilă și pentru anul fiscal 2026).*

„(la 03-02-2022, Litera i) din Alineatul (4)... a fost modificată de Punctul 1, Articolul II din ORDONANȚA nr. 11 din 31 ianuarie 2022...)”
:::

## Formula

`Plafon = min( 0,75% × cifra de afaceri ; 20% × impozitul pe profit datorat )`

Ambele componente se calculează întotdeauna, nu se alege una „reprezentativă” — pentru firme mici, cu profit relativ mare, de regulă limitează cifra de afaceri; pentru firme mari, cu profit relativ mic, de regulă limitează impozitul pe profit.

::: ghid-exemplu
**Firmă mică, profit mare.** Cifra de afaceri 800.000 lei, impozit pe profit 90.000 lei. Termen 1: 0,75% × 800.000 = 6.000 lei. Termen 2: 20% × 90.000 = 18.000 lei. Plafon = 6.000 lei (limitează cifra de afaceri).

**Firmă mare, profit mic.** Cifra de afaceri 15.000.000 lei, impozit pe profit 3.000 lei. Termen 1: 0,75% × 15.000.000 = 112.500 lei. Termen 2: 20% × 3.000 = 600 lei. Plafon = 600 lei (limitează impozitul pe profit, indiferent cât de mare e cifra de afaceri).
:::

## Ce se greșește în practică

- Se calculează doar termenul din cifra de afaceri, presupunând că e mereu cel relevant — de multe ori, tocmai impozitul pe profit mic e cel care limitează.
- Se folosește un impozit pe profit intermediar (înainte de alte credite/reduceri aplicate deja), nu impozitul pe profit efectiv datorat la momentul calculului.
- Se presupune că plafonul din 2026 diferă de cel din 2023-2025 — nu diferă, procentele au rămas neschimbate din 03.02.2022.
- Se uită condiția separată privind Registrul ANAF pentru beneficiarii nonprofit/cult — un plafon calculat corect nu ajută dacă beneficiarul nu e înscris la data contractului.

## Ce face iConta.eu

`plafon_credit(cifra_afaceri, impozit_profit, la_data=None)`, din `core/sponsorizari.py`, calculează exact formula de mai sus: `p1 = 0,75% × cifra_afaceri`, `p2 = 20% × impozit_profit`, rezultatul fiind `min(p1, p2)`. Singura variantă de calcul înregistrată în motor e activă din 01.01.2018, cu procentul de 0,75% — corect pentru orice `la_data` din 2026, dar de folosit cu atenție dacă recalculați o sponsorizare din perioada 2015–02.02.2022, unde procentul legal era 0,5%, nu 0,75% (motorul nu face această distincție istorică).

[iConta.eu](/)
