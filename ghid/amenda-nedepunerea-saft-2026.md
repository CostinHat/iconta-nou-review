---
title: "Amenda pentru nedepunerea SAF-T: cât este în 2026"
description: "Cuantumul amenzii pentru nedepunerea sau depunerea incorectă a fișierului standard de control fiscal (SAF-T / D406), conform Codului de procedură fiscală."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Amenda pentru nedepunerea SAF-T: cât este în 2026

Fișierul standard de control fiscal (SAF-T), depus prin Declarația informativă D406, e o obligație distinctă de celelalte declarații fiscale, cu propriul regim de sancțiuni în Codul de procedură fiscală. Nedepunerea sau depunerea greșită se sancționează separat de restul contravențiilor fiscale, printr-un articol introdus special pentru fișierul standard.

## Temeiul legal

::: ghid-temei
„ART. 337^1 Contravenții aplicabile pentru încălcarea dispozițiilor referitoare la fișierul standard de control fiscal
(1) Constituie contravenții următoarele fapte:
a) nedepunerea la termenele prevăzute de lege a fișierului standard de control fiscal;
b) depunerea incorectă ori incompletă a fișierului standard de control fiscal.
(2) Contravențiile prevăzute la alin. (1) se sancționează astfel:
a) cu amendă de la 1.000 lei la 5.000 lei în cazul săvârșirii faptei prevăzute la lit. a);
b) cu amendă de la 500 lei la 1.500 lei în cazul săvârșirii faptei prevăzute la lit. b)."
— Legea 207/2015 (Codul de procedură fiscală), art. 337^1 (sursă: anaf_surse/legea_207_2015_consolidat.txt)
:::

Din text rezultă două praguri distincte, nu o singură amendă:

- **1.000–5.000 lei** — pentru **nedepunerea** fișierului D406 la termen.
- **500–1.500 lei** — pentru **depunerea incorectă sau incompletă**, adică un fișier transmis, dar cu erori de structură sau conținut.

Același articol, la alin. (3), prevede că **nu se sancționează contravențional** contribuabilul care corectează fișierul până la termenul legal de depunere a următorului fișier, sau care îl corectează ulterior din motive neimputabile lui.

## Ce se greșește în practică

- Se confundă amenda D406 cu amenzile generale pentru declarații fiscale de la art. 336 (care ajung la zeci de mii de lei pentru firme mari) — art. 337^1 e un regim separat, cu praguri mult mai mici.
- Se crede că orice eroare de conținut din D406 e automat sancționabilă, ignorând excepția de la alin. (3): o corecție depusă până la termenul următorului fișier scapă de amendă.
- Se aplică aceeași amendă indiferent dacă firma face parte din categoria contribuabililor mari/mijlocii sau nu — dar art. 337^1, spre deosebire de art. 336, nu diferențiază cuantumul pe categorie de contribuabil.

## Ce face iConta.eu

iConta.eu generează fișierul D406/SAF-T și îl validează contra validatorului oficial ANAF (structura XSD și regulile semantice din schema publicată), astfel încât fișierul transmis să respecte formatul cerut. La data acestui ghid, aplicația **nu urmărește automat termenul de depunere** al D406 pentru fiecare firmă (calendarul specific SAF-T, diferit de celelalte declarații) și **nu calculează sau afișează amenda** aplicabilă în caz de întârziere — verificarea termenului legal și evitarea penalizării rămân în sarcina contabilului.

[iConta.eu](/)
