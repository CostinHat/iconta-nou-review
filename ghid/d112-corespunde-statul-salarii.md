---
title: "Ce faci dacă D112 nu corespunde cu statul de salarii?"
description: "Ce prevede legea pentru corectarea unei declarații 112 greșite și de ce, în practică, verificarea utilă nu e față de statul de salarii, ci față de contabilitate."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Ce faci dacă D112 nu corespunde cu statul de salarii?

Întrebarea presupune un scenariu — D112 diferă de statul de salarii — care, structural, nu ar trebui să apară dacă cele două documente sunt generate din aceeași sursă de date. Dacă totuși apare o diferență reală (de exemplu, o sumă plătită retroactiv sau o corecție descoperită după depunere), legea are un mecanism dedicat: declarația rectificativă.

## Temeiul legal

::: ghid-temei
„În cazul în care au fost acordate sume de natura celor prevăzute la art. 146 alin. (10) și (11), sume reprezentând salarii sau diferențe de salarii, stabilite în baza unor hotărâri judecătorești rămase definitive și irevocabile/hotărâri judecătorești definitive și executorii, inclusiv cele acordate potrivit hotărârilor primei instanțe, executorii de drept, precum și în cazul în care prin astfel de hotărâri s-a dispus reîncadrarea în muncă a unor persoane, în vederea stabilirii prestațiilor acordate de sistemul public de pensii, contribuțiile de asigurări sociale datorate potrivit legii se declară până la data de 25 a lunii următoare celei în care au fost plătite aceste sume, prin depunerea declarațiilor rectificative pentru lunile cărora le sunt aferente sumele respective."
— Legea 227/2015 (Codul fiscal), art. 147 alin. (3) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.html)
:::

- Mecanismul legal de corecție pentru o declarație deja depusă, dar greșită sau incompletă, e declarația rectificativă — depusă pentru luna la care se referă suma corectată, nu pentru luna curentă.
- Termenul de declarare a corecției e legat de data la care s-a plătit efectiv suma corectată (de exemplu, o diferență de salariu acordată printr-o hotărâre judecătorească), nu de data descoperirii erorii.
- Legea nu prevede o procedură separată „D112 vs. stat de salarii" — cele două sunt, prin definiție, expresii ale aceleiași realități economice (venitul plătit efectiv salariatului), deci nu ar trebui să difere dacă amândouă sunt corect calculate.

## Ce se greșește în practică

- Se caută o divergență între D112 și fluturașul de salariu ca prim pas de verificare, deși, dacă ambele sunt generate din aceleași date de intrare, o divergență reală ar indica de regulă o eroare de proces (o corecție aplicată într-un document și nu în celălalt), nu o discrepanță „normală" de acceptat.
- Se ignoră faptul că discrepanța relevantă din punct de vedere contabil-fiscal nu e față de statul de plată, ci față de **înregistrările contabile** ale obligațiilor salariale (conturi de datorii precum 421, 444, 436) — acolo pot apărea diferențe reale, de exemplu dacă o notă contabilă a fost înregistrată greșit sau omisă.
- Se depune o declarație rectificativă fără să se identifice întâi cauza reală a diferenței (eroare de calcul, sumă omisă, corecție retroactivă) — rectificativa corectează simptomul, nu cauza.

## Ce face iConta.eu

În iConta, declarația 112 și statul de plată **nu pot diverge structural**, pentru că sunt generate din exact același motor de calcul al salarizării, cu exact aceiași parametri (persoane în întreținere, normă, venit brut, facilități, deduceri) — o aliniere explicită, construită intern tocmai ca să elimine acest tip de discrepanță. Prin urmare, aplicația nu oferă un ecran separat de „verificare D112 vs. statul de salarii" — pentru că, în funcționare normală, nu există ce să compari acolo.

Ce oferă efectiv iConta este o verificare automată reală, dar pe o altă axă: **D112 față de contabilitatea salariilor** (conturile de datorii salariale din balanță), într-un ecran dedicat de control fiscal. Dacă titlul acestui ghid te-a adus aici căutând o discrepanță D112–fluturaș, subiectul potrivit pentru aplicație e verificarea față de contabilitate — vezi ghidul dedicat despre controlul încrucișat D112 față de contabilitatea salariilor.

[iConta.eu](/)
