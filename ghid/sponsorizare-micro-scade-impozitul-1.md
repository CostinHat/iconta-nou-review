---
title: 'Sponsorizare ca micro: se scade din impozitul de 1%'
description: Nu, nici din cota de 1%, nici din cea de 3% — facilitatea de deducere a sponsorizării din impozitul micro a fost abrogată de la 1 ianuarie 2024; indiferent de cota aplicată firmei în 2026, sponsorizarea nu mai reduce impozitul pe venitul microîntreprinderilor.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Sponsorizare ca micro: se scade din impozitul de 1%?

Nu. Indiferent de cota de impozitare aplicabilă microîntreprinderii — 1% sau 3%, în funcție de venituri și de codul CAEN — sponsorizarea nu mai reduce impozitul pe venitul microîntreprinderilor. Mecanismul de deducere a fost abrogat de la 1 ianuarie 2024, deci pentru orice sponsorizare acordată în 2026, cota micro efectivă (1% sau 3%) nu are nicio relevanță pentru acest calcul.

## Temeiul legal

::: ghid-temei
„(1^1) Abrogat. (la 01-01-2024, Alineatul (1^1), Articolul 56, Titlul III a fost abrogat de Punctul 43., Articolul LIII, Capitolul II din ORDONANȚA DE URGENȚĂ nr. 115 din 14 decembrie 2023...)”

„(2^5) Ultimul an fiscal în care sumele reprezentând sponsorizări/burse și sumele reprezentând achiziția de aparate de marcat electronice fiscale, rămase de reportat, potrivit legii, se scad din impozitul pe veniturile microîntreprinderilor este anul fiscal 2023.”

— *Codul fiscal, art. 56, formă consolidată.*
:::

## De ce cota (1% sau 3%) nu contează aici

Facilitatea abrogată era legată de **mecanismul de credit fiscal din art. 56 alin. (1^1)**, nu de o anumită cotă de impozitare. Cât timp a fost activă (01.04.2019–31.12.2023), deducerea se calcula ca 20% din impozitul micro datorat pe trimestru — indiferent dacă acel impozit rezulta din aplicarea cotei de 1% sau a altei cote în vigoare la momentul respectiv. De la abrogare, întregul mecanism a dispărut, deci discuția „se scade din impozitul de 1%” nu se mai pune: nu există nicio deducere de sponsorizare la nicio cotă micro, în 2026.

Sponsorizarea rămâne o cheltuială reală, înregistrată contabil, dar la calculul impozitului pe veniturile microîntreprinderilor (indiferent de cota aplicabilă firmei) ea nu reduce baza impozabilă și nici impozitul datorat — impozitul micro se calculează pe venituri, nu pe profit, iar cheltuielile (inclusiv sponsorizarea) nu se scad din bază decât în cazurile expres prevăzute de lege pentru acest impozit, printre care sponsorizarea nu mai figurează din 2024.

## Ce se greșește în practică

- Se caută o legătură între cota micro aplicabilă firmei (1% sau 3%) și o eventuală deducere de sponsorizare — cota nu are relevanță, pentru că mecanismul de deducere însuși nu mai există.
- Se presupune că doar firmele cu cota de 3% (fără salariați) ar fi excluse de la facilitate, iar cele cu 1% ar păstra-o — abrogarea din 2024 se aplică tuturor microîntreprinderilor, indiferent de cotă.
- Se caută facilitatea de sponsorizare micro în calculul impozitului pe venit, deși ea era, oricum, un credit din impozitul datorat, nu o deducere din baza impozabilă.

## Ce face iConta.eu

Funcția `credit_sponsorizare(..., tip_impozit="micro", ..., la_data=None)` din `core/sponsorizari.py` nu primește și nici nu folosește cota micro (1%/3%) ca parametru — calculul se baza, cât a fost activ, exclusiv pe impozitul micro deja calculat pentru trimestru, indiferent de cota din care rezultase acel impozit. Pentru orice `la_data` din afara intervalului 01.04.2019–31.12.2023 — deci pentru toate operațiunile din 2026 — funcția returnează credit 0, cu notă explicită de inaplicabilitate a facilității, indiferent de cota micro a firmei.

[iConta.eu](/)
