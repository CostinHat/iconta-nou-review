---
title: "Cum corectez impozitul micro calculat greșit?"
description: Impozitul micro declarat greșit prin D100 nu se corectează printr-o nouă D100 — D100 nu are mecanism propriu de rectificare. Corectarea se face prin formularul 710 „Declarație rectificativă", care înscrie suma greșită și suma corectă pentru obligația respectivă.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum corectez impozitul micro calculat greșit?

Dacă impozitul micro dintr-un trimestru a fost calculat greșit și declarat ca atare prin D100, reflexul de a depune „o D100 nouă, corectă" pentru același trimestru nu funcționează — D100 nu are un atribut sau un mecanism propriu de rectificare asupra ei însăși. Corectarea unei sume deja declarate prin D100 se face printr-un formular separat.

## Temeiul legal

::: ghid-temei
„Declarația rectificativă se utilizează pentru corectarea impozitelor și taxelor administrate de Agenția Națională de Administrare Fiscală și stabilite de către plătitori prin autoimpunere […], declarate în formularul 100 «Declarație privind obligațiile de plată la bugetul de stat»." — OPANAF 587/2016, Anexa 5, Capitolul I.
:::

## Cum se face corectarea

Corectarea se depune prin **formularul 710 „Declarație rectificativă"**, nu printr-o nouă D100. Pentru codul de obligație 121 (impozitul micro), formularul 710 cere: suma declarată inițial (eronat) și suma corectă, pentru trimestrul respectiv — diferența rezultată e cea care se regularizează (plată suplimentară sau, după caz, sumă de recuperat).

Declarația rectificativă se depune la organul fiscal în a cărui evidență contribuabilul e înregistrat, prin mijloace electronice de transmitere la distanță — aceeași cale folosită pentru D100.

Dacă din corecție rezultă o sumă suplimentară de plată, iar aceasta ajunge cu întârziere față de scadența inițială a trimestrului respectiv, se calculează dobânzi și penalități de întârziere, de la scadența inițială — nu de la data depunerii corecției.

## Ce se greșește în practică

- Se încearcă depunerea unei noi D100 pentru același trimestru, presupunând că „ultima depusă e cea valabilă" — D100 nu funcționează așa; e nevoie de formularul 710.
- Se calculează dobânzile/penalitățile de întârziere de la data depunerii corecției, nu de la scadența inițială a trimestrului corectat — regula corectă leagă penalizarea de scadența obligației inițiale.
- Se corectează suma direct în evidența contabilă internă, fără depunerea efectivă a formularului 710 la ANAF — corecția contabilă internă nu înlocuiește obligația de declarare oficială.

## Ce face iConta.eu

D100 nu are, în cod, niciun atribut de rectificare asupra ei însăși — verificat direct: `core/d100.py` nu conține un mecanism `d_rec` (spre deosebire de alte declarații, cum sunt D300 sau D390). Corectarea sumelor declarate greșit se face prin ecranul dedicat formularului 710 (`core/d710.py`), care calculează diferența dintre suma declarată eronat și suma corectă pentru obligația selectată (cod 121, pentru impozitul micro) și generează declarația rectificativă corespunzătoare.

[iConta.eu](/)
