---
title: Sponsorizările pot reduce impozitul micro în 2026?
description: Nu. Facilitatea prin care microîntreprinderile scădeau sponsorizările din impozitul pe venit a fost abrogată de la 1 ianuarie 2024 (OUG 115/2023); în 2026 nu mai există nicio deducere de acest fel pentru micro, indiferent de beneficiar sau de sumă.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Sponsorizările pot reduce impozitul micro în 2026?

Răspunsul scurt: **nu**. Până la finalul lui 2023, microîntreprinderile puteau scădea sponsorizările direct din impozitul pe venit, în anumite limite. Facilitatea a fost însă abrogată de la 1 ianuarie 2024, iar în 2026 sponsorizarea unei microîntreprinderi rămâne pur și simplu cheltuială — fără niciun efect de reducere a impozitului micro.

## Temeiul legal

::: ghid-temei
„(1^1) Abrogat. (la 01-01-2024, Alineatul (1^1), Articolul 56, Titlul III a fost abrogat de Punctul 43., Articolul LIII, Capitolul II din ORDONANȚA DE URGENȚĂ nr. 115 din 14 decembrie 2023 ...)”

„(2^5) Ultimul an fiscal în care sumele reprezentând sponsorizări/burse și sumele reprezentând achiziția de aparate de marcat electronice fiscale, rămase de reportat, potrivit legii, se scad din impozitul pe veniturile microîntreprinderilor este anul fiscal 2023.”

— *Codul fiscal, art. 56, forma consolidată; OUG 115/2023, art. LIII pct. 43.*
:::

## Ce s-a schimbat și de când

- **Până la 31.12.2023**: microîntreprinderile puteau scădea din impozitul micro datorat pe trimestru sponsorizările către entități nonprofit/unități de cult înscrise în Registrul ANAF, în limita a 20% din impozitul micro al trimestrului respectiv (fostul art. 56 alin. (1^1) din Codul fiscal).
- **De la 01.01.2024, inclusiv în 2026**: alineatul care permitea deducerea a fost abrogat. Sumele rămase de reportat din anii anteriori s-au putut folosi cel mai târziu în anul fiscal 2023 — nu mai există niciun report valabil în 2026.
- Sponsorizarea rămâne, în continuare, o cheltuială legală și legitimă pentru o microîntreprindere, dar **nu mai reduce impozitul**, indiferent de valoarea sponsorizării sau de tipul beneficiarului.

## Ce se greșește în practică

- Se aplică, din reflex, regula veche de 20% din impozitul micro trimestrial pentru o sponsorizare acordată în 2024, 2025 sau 2026.
- Se confundă regula de la microîntreprinderi (abrogată din 2024) cu cea de la impozitul pe profit (art. 25 alin. (4) lit. i) din Codul fiscal), care rămâne activă și permite un credit fiscal de până la minimul dintre 0,75% din cifra de afaceri și 20% din impozitul pe profit — dar numai pentru firmele plătitoare de impozit pe profit.
- Se încearcă reportarea, în 2026, a unor sume de sponsorizare micro nescăzute din anii 2021-2023, deși ultimul an fiscal în care aceste sume s-au mai putut scădea a fost 2023.

## Ce face iConta.eu

În `core/sponsorizari.py`, funcția `credit_sponsorizare(..., tip_impozit="micro", ...)` este activă **doar pentru date cuprinse între 01.04.2019 și 31.12.2023** — în afara acestui interval, inclusiv pentru orice dată din 2024, 2025 sau 2026, motorul returnează credit 0, cu o notă explicită de inaplicabilitate. Asta reflectă corect abrogarea facilității: pentru o sponsorizare micro introdusă azi, aplicația nu propune nicio reducere de impozit — sponsorizarea se înregistrează contabil (`6582 = 401` sau `6582 = 5121`), dar rămâne cheltuială nedeductibilă din impozitul pe venitul microîntreprinderilor.

[iConta.eu](/)
