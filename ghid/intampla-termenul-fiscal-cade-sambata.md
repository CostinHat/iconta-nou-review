---
title: Ce se întâmplă dacă termenul fiscal cade sâmbăta sau duminica?
description: Termenul se mută pe următoarea zi lucrătoare — valabil pentru orice tip de declarație, indiferent dacă ziua nominală e 25 (regula generală), 30 (D394) sau ultima zi a lunii (D406). Exemplu concret pentru 2026.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Ce se întâmplă dacă termenul fiscal cade sâmbăta sau duminica?

Indiferent de ziua nominală a termenului — 25 (majoritatea declarațiilor), 30 (D394) sau ultima zi a lunii (D406) — regula e aceeași: dacă acea zi e sâmbătă sau duminică, termenul se mută pe următoarea zi lucrătoare.

## Temeiul legal

::: ghid-temei
„Declaraţia se depune la organul fiscal competent până în data de 30 inclusiv a lunii următoare încheierii perioadei de raportare." — OPANAF 2194/2025, pentru D394 (exemplu de termen cu zi nominală diferită de 25, supus aceleiași reguli de mutare pentru weekend)
:::

**De semnalat onest**: ca și la celelalte ghiduri din această serie, dosarul verificat nu conține un citat verbatim din actul normativ care reglementează explicit regula de prorogare pentru weekend (de regulă, Codul de procedură fiscală) — mecanismul descris mai jos e confirmat din comportamentul codului sursă al aplicației, nu dintr-un text de lege reprodus aici.

## Exemplu concret, pentru 2026

Data de 30 august 2026 cade duminică. Pentru o declarație cu zi nominală 30 (ca D394), termenul real devine luni, 31 august 2026 — presupunând că 31 august nu e, la rândul ei, o zi de sărbătoare legală (nu e cazul: nu există o sărbătoare legală fixă cunoscută pe 31 august).

Regula e identică și pentru declarațiile cu zi nominală 25: dacă 25 a lunii cade sâmbătă sau duminică, termenul se mută pe următoarea zi lucrătoare, exact ca în exemplul de mai sus.

## Excepția D406 (SAF-T) — o nuanță suplimentară

Pentru D406, ziua nominală nu e fixă (nici 25, nici 30), ci **ultima zi calendaristică a lunii următoare perioadei de raportare**. Dacă acea ultimă zi de lună cade sâmbătă sau duminică, se aplică aceeași regulă de mutare pe următoarea zi lucrătoare. În plus, pentru contribuabilii nou-intrați în obligația SAF-T există o perioadă de grație separată (2-6 luni, după tipul de raportare) — care nu ține de mutarea pentru weekend, ci de un termen suplimentar prevăzut distinct în lege; nu o confundați cu regula de prorogare descrisă aici.

## Ce se greșește în practică

- Se aplică regula de mutare pentru weekend, dar se ignoră excepțiile de zi nominală (D394 — ziua 30; D406 — ultima zi a lunii), calculându-se greșit data de la care pornește verificarea.
- Se confundă perioada de grație pentru SAF-T (D406) cu simpla mutare a termenului pentru weekend — sunt două mecanisme diferite.

## Ce face iConta.eu

Pentru fiecare tip de declarație, aplicația calculează întâi data nominală specifică (25, 30, sau ultima zi a lunii, după caz), apoi verifică dacă acea dată cade în weekend sau într-o zi de sărbătoare legală și o mută, dacă e cazul, pe următoarea zi lucrătoare — același mecanism, aplicat consecvent pentru toate tipurile de declarații acoperite.

[iConta.eu](/)
