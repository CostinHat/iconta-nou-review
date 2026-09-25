---
title: "Cum corectezi salariul brut declarat greșit în D112?"
description: "Ce spune Codul de procedură fiscală despre declarația rectificativă și ce trebuie făcut când salariul brut a fost raportat greșit în D112."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum corectezi salariul brut declarat greșit în D112?

O eroare de salariu brut în D112 (Declarația unică privind obligațiile de plată a contribuțiilor sociale, impozitului pe venit și evidența nominală a persoanelor asigurate) nu se corectează prin telefon sau printr-o „notă" trimisă la ANAF — singura cale legală este depunerea unei declarații rectificative pentru luna respectivă.

## Temeiul legal

::: ghid-temei
„Declarațiile [...] pot fi corectate prin depunerea unei declarații rectificative."
— Legea 207/2015 (Codul de procedură fiscală), art. 105 alin. (3) (sursă: anaf_surse/legea_207_2015_consolidat.txt)
:::

Ce presupune, concret, corectarea:

- Se depune o nouă declarație D112 pentru aceeași lună/perioadă, cu toate datele corecte (nu doar diferența) — declarația rectificativă înlocuiește, pentru acea perioadă, declarația inițială.
- Diferențele de obligații fiscale rezultate au termen de plată **data depunerii declarației rectificative** la organul fiscal, conform art. 156 alin. (4) din același act.
- Dacă rectificarea generează o diferență de plată în plus, aceasta poate atrage dobânzi/penalități de întârziere calculate de la scadența inițială, nu de la data rectificării.

## Ce se greșește în practică

- Se corectează salariul în statul de plată intern, dar se uită depunerea efectivă a D112 rectificative — pentru ANAF, declarația inițială (greșită) rămâne valabilă până când e înlocuită.
- Se presupune că orice corecție se face „la următoarea lună", incluzând diferența acolo — corect este să se refacă declarația pentru luna în care a fost salariul greșit.
- Se ignoră impactul asupra bazei de calcul pentru CAS/CASS ale salariatului, deși modificarea salariului brut schimbă și aceste contribuții, nu doar impozitul.

## Ce face iConta.eu

La data acestui ghid, generatorul D112 din iConta.eu (`core/d112.py`) construiește declarația din datele curente ale statelor de plată, dar marchează în XML explicit `d_rec="0"` — adică declarația inițială. Aplicația nu are momentan un flux dedicat de generare a unei declarații **rectificative** (cu `d_rec="1"`). Practic, dacă salariul brut se corectează în statul de plată, iConta.eu regenerează un D112 corect pentru acea lună, dar depunerea lui la ANAF ca declarație rectificativă (cu bifa aferentă) rămâne o operațiune pe care contabilul o face separat, în portalul ANAF.

[iConta.eu](/)
