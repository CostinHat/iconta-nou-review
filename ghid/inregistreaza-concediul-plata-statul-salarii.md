---
title: Cum se înregistrează concediul fără plată în statul de salarii?
description: Concediul fără plată nu generează o notă contabilă proprie — reduce brutul lunii proporțional cu zilele efectiv lucrate, iar statul de plată și notele contabile obișnuite (641/421, 421/4315, 421/4316, 421/444) se generează pe acest brut redus.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum se înregistrează concediul fără plată în statul de salarii?

Concediul fără plată nu are o înregistrare contabilă separată — nu există o notă contabilă „pentru zilele de concediu fără plată". Ce se schimbă e brutul lunii, redus proporțional cu zilele efectiv lucrate; statul de plată și monografia contabilă obișnuite se generează, ca de fiecare lună, pe acest brut recalculat.

## Temeiul legal

::: ghid-temei
„(2) Drepturile salariale se acordă proporțional cu timpul efectiv lucrat, raportat la drepturile stabilite pentru programul normal de lucru." — Legea 53/2003 (Codul muncii), art.103 alin.(2)
:::

**De semnalat onest**: la fel ca la GH-01668, articolul de mai sus e citat verbatim în dosarul verificat pentru principiul general al proporționalității salariale, nu specific pentru concediul fără plată. Regulile de evidență a prezenței (pontaj) pentru zilele de concediu fără plată nu au fost confirmate separat în acest dosar — vezi mai jos ce anume e confirmat din codul sursă al aplicației.

## Ce înseamnă în practică

1. Se recalculează brutul lunii, proporțional cu zilele efectiv lucrate (vezi GH-01668 pentru formulă și exemplu).
2. Pe brutul astfel redus, statul de plată al lunii se generează cu formula obișnuită de calcul (CAS, CASS, deducere personală, impozit).
3. Monografia contabilă e cea standard pentru orice stat de plată — nu apare o notă distinctă pentru zilele fără plată, pentru că acele zile pur și simplu nu generează drepturi salariale de înregistrat.

## Ce se greșește în practică

- Se caută o notă contabilă separată pentru „concediul fără plată" — nu există, pentru că zilele respective nu generează nicio cheltuială salarială de înregistrat.
- Se înregistrează salariul integral din contract și se face o corecție ulterioară, în loc să se calculeze de la început pe brutul proporțional corect.
- Se omite verificarea podelei de contribuții (CF art.146 alin.(5^6)) atunci când brutul redus ajunge sub salariul minim aplicabil lunii — vezi GH-01668.

## Ce face iConta.eu

Statul de plată se generează cu funcția `monografie_salariu()` din `core/salarizare.py`, care produce notele contabile standard (641/421 — salarii datorate, 421/4315 — CAS reținut, 421/4316 — CASS reținut, 421/444 — impozit reținut, 646/436 — CAM datorat de angajator) pornind de la brutul calculat pentru luna respectivă. Codul verificat pentru acest dosar nu conține o notă contabilă distinctă pentru concediul fără plată — brutul introdus în calcul e cel proporțional, iar restul fluxului (rețineri, notă contabilă) e identic cu al oricărei alte luni.

[iConta.eu](/)
