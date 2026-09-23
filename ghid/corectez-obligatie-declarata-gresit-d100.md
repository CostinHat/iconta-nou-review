---
title: "Cum corectez o obligație declarată greșit în D100?"
description: Orice obligație declarată greșit în D100 — impozit micro, impozit pe profit sau altă obligație de autoimpunere — se corectează prin formularul 710 „Declarație rectificativă", care înscrie suma eronată și suma corectă pentru codul de obligație respectiv, nu printr-o nouă D100.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum corectez o obligație declarată greșit în D100?

D100 „Declarație privind obligațiile de plată la bugetul de stat" acoperă mai multe coduri de obligație, nu doar impozitul micro — dar mecanismul de corecție e același pentru toate: D100 nu se rescrie, se rectifică printr-un formular separat.

## Temeiul legal

::: ghid-temei
„Declarația rectificativă se utilizează pentru corectarea impozitelor și taxelor administrate de Agenția Națională de Administrare Fiscală și stabilite de către plătitori prin autoimpunere sau cu regim de reținere la sursă, declarate în formularul 100 «Declarație privind obligațiile de plată la bugetul de stat»." — OPANAF 587/2016, Anexa 5, Capitolul I.
:::

## Cum funcționează corecția

Formularul **710 „Declarație rectificativă"** se completează cu codul de obligație afectat (de exemplu, 121 pentru impozitul micro, 103 pentru impozitul pe profit) și cu două sume: cea completată eronat în declarația inițială și cea corectă. Diferența rezultată e cea care se regularizează. Declarația rectificativă se depune la organul fiscal la care contribuabilul e înregistrat, prin mijloace electronice de transmitere la distanță — aceeași cale ca D100.

D100 însăși nu are un mecanism intern de auto-rectificare — nu există, pentru ea, un atribut de tipul „declarație rectificativă" care să înlocuiască pur și simplu declarația anterioară; corectarea trece obligatoriu prin formularul 710.

## Ce se greșește în practică

- Se încearcă redepunerea D100 pentru trimestrul greșit, sperând că sistemul o va trata ca înlocuire a celei anterioare — D100 nu funcționează așa.
- Se corectează evidența contabilă internă, fără depunerea efectivă a formularului 710 — fără depunerea lui, declarația oficială rămâne cea inițială, greșită.
- Se completează formularul 710 fără codul corect de obligație (121, 103 etc.), ceea ce face imposibilă potrivirea corecției cu declarația inițială la nivelul organului fiscal.

## Ce face iConta.eu

D100 nu are, în cod, niciun atribut de rectificare proprie — verificat direct: `core/d100.py` nu implementează un mecanism echivalent celui folosit la alte declarații (D300, D390), unde există un flag explicit de „declarație rectificativă". Corectarea se face prin ecranul dedicat formularului 710 (`core/d710.py`), cu selector de cod de obligație limitat la 121 (impozit micro) și 103 (impozit pe profit) — cele două coduri pe care aplicația le tratează prin acest flux de corecție.

[iConta.eu](/)
