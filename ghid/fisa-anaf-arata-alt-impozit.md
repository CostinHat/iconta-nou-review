---
title: "Ce fac dacă fișa ANAF arată alt impozit pe profit decât contabilitatea?"
description: "Pașii de urmat când suma din fișa pe plătitor ANAF nu corespunde cu impozitul pe profit calculat din contabilitate, pe baza mecanismului de corectare a declarațiilor fiscale."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Ce fac dacă fișa ANAF arată alt impozit pe profit decât contabilitatea?

Diferența dintre suma din fișa pe plătitor și impozitul pe profit calculat intern nu se rezolvă niciodată prin telefon sau printr-o simplă notă contabilă. Sursa e aproape întotdeauna o declarație D101 care nu reflectă ultima variantă corectă a calculului — iar remediul legal e unul singur: corectarea declarației.

## Temeiul legal

::: ghid-temei
„(1) Declarația de impunere poate fi corectată de către contribuabil/plătitor, pe perioada termenului de prescripție a dreptului de a stabili creanțe fiscale.
(2) Declarația informativă poate fi corectată de către contribuabil/plătitor indiferent de perioada la care se referă.
(3) Declarațiile prevăzute la alin. (1) și (2) pot fi corectate prin depunerea unei declarații rectificative."
— Legea nr. 207/2015 (Codul de procedură fiscală), art. 105 alin. (1), (2), (3) (sursă: anaf_surse/legea_207_2015_consolidat.txt)
:::

Concret, atunci când fișa pe plătitor arată alt impozit pe profit decât cel din contabilitate, ordinea de verificare e:

- Se compară suma din fișă cu **ultima declarație D101 efectiv depusă și validată** de ANAF — nu cu ultimul calcul intern al contabilului. Diferențele apar frecvent pentru că D101 nu a fost încă (re)depusă cu ultima variantă corectă a calculului.
- Dacă declarația depusă conține o eroare, ea se corectează prin **declarație rectificativă**, potrivit art. 105 alin. (1) — dreptul de corectare există pe toată perioada termenului de prescripție, deci nu e pierdut după câteva luni.
- Dacă suma din fișă provine dintr-o stabilire din oficiu (organul fiscal a estimat impozitul pentru că declarația nu a fost depusă la termen), soluția e depunerea declarației de impunere reale, care anulează decizia din oficiu — nu o contestație a sumei estimate.
- Doar după depunerea rectificativei (și după procesarea ei de ANAF, care nu e instantanee) fișa pe plătitor se actualizează; până atunci, diferența poate persista chiar dacă în contabilitate calculul e deja corect.

## Ce se greșește în practică

- Se contestă suma din fișă fără să se verifice mai întâi ce anume conține ultima declarație D101 depusă — de multe ori discrepanța vine dintr-o versiune veche a declarației, nu dintr-o eroare ANAF.
- Se așteaptă ca fișa să se corecteze automat, fără să se depună efectiv declarația rectificativă prevăzută la art. 105 alin. (3).
- Se confundă corectarea unei declarații de impunere (D101, supusă termenului de prescripție) cu corectarea unei declarații informative, care se poate corecta oricând, indiferent de perioada la care se referă.

## Ce face iConta.eu

La data acestui ghid, iConta.eu **calculează și generează declarația D101** pe baza datelor din contabilitate (`core/d101.py`, cu module de reconciliere în `core/d101_reconciliere.py`), inclusiv verificări interne care compară impozitul calculat cu rulajele contabile ale firmei. Aplicația **nu are acces la fișa pe plătitor din portalul ANAF** și nu compară automat suma din contabilitate cu ceea ce arată evidența ANAF — acea comparație și depunerea declarației rectificative, dacă e cazul, rămân o operațiune manuală, făcută de contabil pe baza consultării SPV sau a fișei eliberate de organul fiscal.

[iConta.eu](/)
