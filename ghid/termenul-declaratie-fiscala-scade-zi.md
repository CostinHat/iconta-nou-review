---
title: Care este termenul dacă o declarație fiscală scade într-o zi nelucrătoare?
description: Aceeași regulă se aplică indiferent de tipul declarației — data nominală se mută pe următoarea zi lucrătoare, ținând cont de weekend și de calendarul complet al sărbătorilor legale (fixe și mobile) până în 2099.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Care este termenul dacă o declarație fiscală scade într-o zi nelucrătoare?

„Zi nelucrătoare" înseamnă, pentru calculul unei scadențe fiscale, fie o zi de weekend (sâmbătă sau duminică), fie o zi de sărbătoare legală, fixă sau mobilă. În oricare din aceste cazuri, termenul nu rămâne pe data nominală — se mută pe următoarea zi lucrătoare.

## Temeiul legal

::: ghid-temei
Calendarul zilelor de sărbătoare legală folosit pentru mutarea termenelor are ca bază declarată art.139 din Codul muncii (Legea 53/2003), care enumeră atât zilele fixe, cât și cele cinci zile mobile calculate după Paștele ortodox (valabile pentru intervalul 2024–2099).
:::

**De semnalat onest**: regula de prorogare a termenului fiscal pentru „prima zi lucrătoare" e confirmată ca fiind implementată efectiv, ca mecanism, în aplicația verificată pentru acest dosar — dar dosarul nu conține un citat verbatim din actul normativ care reglementează explicit acest mecanism de prorogare (de regulă, Codul de procedură fiscală). Nu inventăm acest citat; mecanismul descris mai jos e confirmat din comportamentul codului sursă, nu dintr-un text de lege reprodus aici.

## Mecanismul, pas cu pas

1. Aplicația calculează data nominală a termenului, specifică fiecărui tip de declarație (de regulă ziua 25 a lunii următoare, cu excepții — de exemplu D394 are ziua 30, D406 are ultima zi a lunii).
2. Verifică dacă acea dată cade sâmbătă, duminică sau într-o zi de sărbătoare legală.
3. Dacă da, mută termenul pe următoarea zi calendaristică ce nu e nici weekend, nici sărbătoare legală.

Această verificare ține cont și de sărbătorile mobile, nu doar de cele fixe — an de an, datele mobile (legate de Paștele ortodox) diferă, iar o dată care nu era sărbătoare într-un an poate fi sărbătoare în altul.

## Ce se greșește în practică

- Se presupune că doar weekendul „mută" termenul, ignorându-se sărbătorile legale mobile care pot cădea în zile de lucru obișnuite.
- Se calculează manual termenul, fără acces la calendarul complet al sărbătorilor mobile pentru anul respectiv, și se ajunge la o dată greșită.

## Ce face iConta.eu

Ecranul „Termene" din aplicație (consumatorul funcționalității de calcul al scadențelor) afișează direct data reală a termenului, deja mutată dacă e cazul — nu doar data nominală. Calendarul de sărbători legale folosit intern acoperă integral 2026 (calculat pentru intervalul 2024–2099), deci mutările pentru sărbători mobile sunt reflectate automat, fără a fi nevoie de o verificare manuală separată.

[iConta.eu](/)
