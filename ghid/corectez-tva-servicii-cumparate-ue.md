---
title: Cum corectez TVA pentru servicii cumpărate din UE?
description: OPANAF 779/2024 a adăugat pe D301 o căsuță de declarație rectificativă, dar mecanismul nu e implementat funcțional în iConta.eu — pentru o D301 deja depusă și greșită, corectarea trebuie verificată separat, direct cu ANAF.
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum corectez TVA pentru servicii cumpărate din UE?

O eroare descoperită după depunerea D301 — o operațiune omisă, o bază calculată greșit, o cotă aplicată incorect — ridică întrebarea firească: cum se corectează o declarație deja depusă. Răspunsul are o parte legală clară și o limită importantă în ce privește aplicația.

## Temeiul legal

::: ghid-temei
„Declarație rectificativă ca urmare a unei notificări de conformare" — căsuță adăugată pe formularul D301 (și pe alte formulare) prin OPANAF 779/2024
:::

Norma prevede explicit o căsuță separată de rectificare pe formularul D301, introdusă prin OPANAF 779/2024. Asta confirmă, la nivel de formă, că declarația rectificativă e mecanismul oficial pentru corectarea unei D301 deja depuse.

### Ce trebuie verificat înainte de a corecta

- Ce anume e greșit: o operațiune omisă complet, o bază calculată dintr-un curs greșit, sau o cotă aplicată eronat (standard în loc de redusă, sau invers).
- Perioada exactă căreia îi aparține operațiunea — corecția se face pe perioada în care a apărut exigibilitatea, nu pe luna în care se descoperă eroarea.
- Mecanismul concret prin care ANAF acceptă rectificarea (declarație rectificativă „ca urmare a unei notificări de conformare", conform textului citat mai sus) — un pas care nu e acoperit de acest ghid și trebuie confirmat direct la sursă, în funcție de situația firmei.

## Ce se greșește în practică

- Se presupune că eroarea se corectează pur și simplu prin includerea diferenței în declarația lunii curente — greșit; operațiunea aparține perioadei ei fiscale, nu perioadei în care a fost observată eroarea.
- Se așteaptă ca aplicația de contabilitate să genereze automat o declarație rectificativă bifată — nu e cazul, vezi mai jos.
- Se ignoră diferența dintre o eroare de bază (curs, valoare) și o eroare de încadrare (tip 4 în loc de tip 5, sau invers) — a doua schimbă și obligația de a depune D390, nu doar D301.

## Ce face iConta.eu

Generatorul de D301 din aplicație emite declarația mereu ca **originală**, nu ca rectificativă — căsuța de „declarație rectificativă ca urmare a unei notificări de conformare", introdusă prin OPANAF 779/2024, nu e implementată funcțional în generator. Aplicația **nu promite** și nu trebuie folosită pentru a depune o D301 rectificativă din interiorul ei.

Ce poate face aplicația: dacă eroarea e o operațiune omisă, o poți adăuga acum, pentru perioada corectă, iar cross-verificarea cu facturile de achiziție intracomunitară din evidența contabilă blochează generarea declarației dacă rămân facturi IC neintroduse. Pentru corectarea propriu-zisă la ANAF a unei declarații deja depuse, verifică separat mecanismul de rectificare aplicabil situației tale.

[iConta.eu](/)
