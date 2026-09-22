---
title: Am omis cheltuieli nedeductibile la D101. Cum corectez?
description: Cheltuielile nedeductibile omise se adaugă la rd. 34 din D101, care intră direct în rd. 35 (rd. 22 + rd. 34) — omiterea lor subevaluează profitul impozabil și impozitul de 16% calculat conform art. 17 Cod fiscal.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Am omis cheltuieli nedeductibile la completarea D101. Cum corectez?

Cheltuielile nedeductibile nu sunt un detaliu secundar în D101 — ele intră direct în formula care duce de la rezultatul contabil la profitul impozabil. Dacă la depunere ai omis o parte din ele, profitul impozabil declarat a ieșit mai mic decât cel real, iar impozitul de 16% calculat pe el a ieșit subevaluat. Corectarea nu e opțională: se face prin declarație rectificativă, cu recalcularea întregului lanț de la rd. 35 în jos.

## Temeiul legal

::: ghid-temei
**OPANAF 206/2025, rd. 35:** *„35 Total profit impozabil/pierdere fiscală pentru anul de raportare, înainte de ajustarea cu pierderile curente (rd. 22 + rd. 34)"*

**CF art. 17** — cota aplicată asupra profitului impozabil corectat: *„Cota de impozitare. Cota de impozit pe profit care se aplică asupra profitului impozabil este de 16%."*

**OPANAF 206/2025, rd. 41.1:** *„41.1 Impozit aferent profitului ce se impune cu cota de 16%"*
:::

## Ce se recalculează

Rd. 34 e **totalul** cheltuielilor nedeductibile — o cheltuială omisă la depunere înseamnă un rd. 34 mai mic decât cel real, deci un rd. 35 mai mic, care se propagă mai departe:

```
rd.35   = rd.22 + rd.34            (rd.34 subevaluat -> rd.35 subevaluat)
rd.38.1 = rd.35 + rd.36 + rd.37 - rd.38
rd.40   = rd.38.1 - rd.39.1
rd.41.1 = rd.40 × 16%              (impozit subevaluat)
```

Corecția presupune: identifici toate cheltuielile nedeductibile omise, le aduni corect la rd. 34, și reiei calculul din acel punct până la rd. 41.1. Nu e suficient să „ajustezi" doar impozitul final — trebuie parcurs din nou lanțul complet, pentru că o schimbare la rd. 34 poate modifica și rd. 39.1 (dacă profitul crescut face pierderea recuperabilă diferită) și, implicit, baza finală.

## De ce contează suma exactă, nu doar direcția

Impozitul de 16% se aplică pe rd. 40 în întregime, nu pe diferența de cheltuieli omise izolat — de aceea o omisiune la rd. 34 nu produce doar o eroare „mică" la final, ci recalculează întreaga bază de la acel punct în jos. O declarație rectificativă corectă reface tot lanțul, nu adaugă doar diferența de impozit pe cheltuiala omisă.

## Ce se greșește în practică

- **Se corectează direct impozitul de plată**, fără să se refacă lanțul rd. 34 → rd. 35 → rd. 38.1 → rd. 40. Suma finală poate ieși apropiată întâmplător, dar nu reflectă structura corectă a formularului.
- **Se presupune că orice cheltuială „ciudată" e automat nedeductibilă**, fără verificarea condițiilor legale de deductibilitate aplicabile fiecărei categorii — omisiunea inversă (marcarea ca nedeductibil a ceva deductibil) supraevaluează impozitul.
- **Se ignoră efectul asupra rd. 39.1**, dacă profitul corectat (rd. 38.1) devine suficient de mare încât să schimbe suma de pierdere recuperabilă din anii precedenți.

## Ce face iConta.eu

Rd. 35 e calculat ca sumă a rd. 22 (rezultat contabil) și rd. 34 (total cheltuieli nedeductibile), conform structurii din OPANAF 206/2025, cu impozitul final aplicat pe rd. 40 la cota de 16% de la art. 17.

Vezi și: [cheltuielile deductibile la impozitul pe profit](/ghid/cheltuieli-deductibile-impozit-profit) și [de la rezultatul contabil la rezultatul fiscal pe D101](/ghid/de-la-rezultatul-contabil-la-rezultatul-fiscal-d101).

[iConta.eu](/)
