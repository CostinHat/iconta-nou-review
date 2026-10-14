---
title: Care este termenul dacă o declarație fiscală scade într-o zi nelucrătoare?
description: Aceeași regulă se aplică indiferent de tipul declarației — data nominală se mută pe următoarea zi lucrătoare, ținând cont de weekend și de calendarul complet al sărbătorilor legale (fixe și mobile) până în 2099.
published: 2026-09-25
modified: 2026-10-13
poarta: v1
---

# Care este termenul dacă o declarație fiscală scade într-o zi nelucrătoare?

„Zi nelucrătoare" înseamnă, pentru calculul unei scadențe fiscale, fie o zi de weekend (sâmbătă sau duminică), fie o zi de sărbătoare legală, fixă sau mobilă. În oricare din aceste cazuri, termenul nu rămâne pe data nominală — se mută pe următoarea zi lucrătoare.

## Temeiul legal

::: ghid-temei
„Termenele de orice fel privind exercitarea drepturilor și îndeplinirea obligațiilor prevăzute de Codul fiscal, de prezentul cod, precum și de alte dispoziții legale aplicabile în materie, dacă legislația fiscală nu dispune altfel, se calculează potrivit dispozițiilor Codului de procedură civilă, republicat.”
— Legea nr. 207/2015 (Codul de procedură fiscală), art. 75 (sursă: [Legea nr. 207/2015 privind Codul de procedură fiscală](https://legislatie.just.ro/Public/DetaliiDocument/170007))

„Zilele de sărbătoare legală în care nu se lucrează sunt: – 1 și 2 ianuarie; [...] – 6 ianuarie - Botezul Domnului - Boboteaza; [...] – 7 ianuarie - Soborul Sfântului Proroc Ioan Botezătorul; [...] – 24 ianuarie – Ziua Unirii Principatelor Române; [...] – Vinerea Mare, ultima zi de vineri înaintea Paștelui; [...] – prima și a doua zi de Paști; [...] – 1 mai; [...] – 1 iunie; [...] – prima și a doua zi de Rusalii; [...] – Adormirea Maicii Domnului; [...] – 30 noiembrie - Sfântul Apostol Andrei, cel Întâi chemat, Ocrotitorul României; [...] – 1 decembrie; [...] – prima și a doua zi de Crăciun; [...]”
— Codul muncii (Legea 53/2003), art. 139 alin. (1) (sursă: [Legea nr. 53/2003 - Codul muncii](https://legislatie.just.ro/Public/DetaliiDocument/128647))
:::

Codul de procedură fiscală nu are o regulă proprie de prelungire a termenului: trimite, pentru calculul termenelor, la Codul de procedură civilă (art. 75, citat mai sus), al cărui text nu e reprodus în acest ghid. Calendarul zilelor nelucrătoare cuprinde, pe lângă sâmbete și duminici, sărbătorile legale de la art. 139 alin. (1) din Codul muncii — fixe și mobile (Vinerea Mare, Paștele și Rusaliile, după calendarul ortodox). Mecanismul descris mai jos este cel aplicat de aplicație.

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
