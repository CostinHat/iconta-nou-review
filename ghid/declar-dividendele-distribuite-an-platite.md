---
title: Cum declar dividendele distribuite într-un an și plătite în anul următor?
description: Când plata se face în alt an decât distribuirea, D205 declară dividendul integral la momentul plății, iar impozitul se calculează cu cota valabilă la data distribuirii, fără recalculare la cota din anul plății.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum declar dividendele distribuite într-un an și plătite în anul următor?

E o situație frecventă: dividendul se aprobă și se înregistrează ca datorie a firmei într-un an, dar se plătește efectiv abia în anul următor. Întrebarea firească e în care declarație D205 apare și cu ce cotă de impozit.

## Temeiul legal

::: ghid-temei
**Cota impozitului pe dividende**, confirmată în sursele oficiale:
- **16%** de la 01.01.2026 — Legea 141/2025: „impozit pe dividende cota 16% asupra dividendului brut" (Art. II pct. 1, modifică art. 43 alin. 2 din Codul fiscal).
- **10%** în 2025 — OUG 156/2024: „Veniturile sub forma de dividende se impoziteaza cu o cota de 10% din suma acestora, impozitul fiind final."
:::

Regula de bază a D205: cota impozitului se stabilește la **data la care dividendul a fost distribuit** (creditat în contul 457), nu la data la care se face plata efectivă și nu se recalculează ulterior. Un dividend distribuit în 2025, cu cota de 10%, rămâne impozitat cu 10% chiar dacă plata efectivă are loc în 2026, la cota de 16%.

Din perspectiva declarației: dacă distribuirea a avut loc într-un an anterior ferestrei declarației curente, iar plata se face abia acum, D205 din anul plății declară automat suma ca fiind integral plătită (dividendul distribuit „nu mai apare" separat, pentru că fereastra anului curent nu conține momentul creditării contului 457) — practic tot dividendul plătit în acel an devine baza declarației, cu cota fixată la data distribuirii inițiale.

## Ce se greșește în practică

- Se aplică, din reflex, cota de impozit valabilă la data plății, nu cea de la data distribuirii — greșit dacă cele două cote diferă (ca în cazul trecerii de la 10% la 16% începând cu 2026).
- Se presupune că dividendul trebuia deja declarat integral în anul distribuirii, chiar dacă plata nu s-a făcut — declarația urmărește plata, nu doar aprobarea.

## Ce face iConta.eu

Motorul declarației D205 din iConta.eu calculează impozitul pe fiecare tranșă de plată pornind de la cota validă la data la care dividendul respectiv a fost distribuit (creditat în contul 457), nu de la cota curentă — fără recalculare ulterioară. Dacă distribuirea s-a făcut într-un an anterior anului declarației, iar plata are loc acum, aplicația recunoaște automat suma plătită ca dividend integral plătit pentru acel an, cu impozitul calculat la cota istorică a distribuirii.

[iConta.eu](/)
