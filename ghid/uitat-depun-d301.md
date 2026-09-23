---
title: Ce fac dacă am uitat să depun D301?
description: D301 se depune până pe 25 a lunii următoare celei în care apare exigibilitatea taxei, pentru fiecare perioadă cu operațiuni intracomunitare. Dacă termenul a trecut, declarația trebuie totuși depusă, pentru perioada corectă, nu pentru luna curentă.
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Ce fac dacă am uitat să depun D301?

O achiziție intracomunitară de bunuri sau servicii, pentru un neplătitor de TVA, generează obligația de a depune decontul special (D301) până pe 25 a lunii următoare. Dacă termenul a trecut fără ca declarația să fi fost depusă, obligația nu dispare — trebuie depusă cât mai curând, pentru perioada în care a apărut de fapt exigibilitatea.

## Temeiul legal

::: ghid-temei
„până la data de 25 inclusiv a lunii următoare celei în care ia naștere exigibilitatea operațiunilor prevăzute la secțiunile 1, 3, 4 și 4.1" — OPANAF 592/2016, art. privind termenul de depunere (Codul fiscal, art. 324 alin. (2))
:::

Termenul e legat de perioada în care ia naștere exigibilitatea taxei, nu de momentul în care contabilul își dă seama de omisiune. Practic, o D301 depusă cu întârziere se depune tot pentru luna în care a existat efectiv achiziția — nu se „mută" în luna curentă, ca și cum operațiunea ar fi avut loc acum.

### Ce se face concret

1. Se identifică exact luna (lunile) în care a existat achiziția intracomunitară neintrodusă în declarație.
2. Se completează D301 pentru fiecare perioadă afectată, cu operațiunile aferente acelei perioade — nu cumulat pe luna curentă.
3. Se depune declarația la ANAF, cât mai curând posibil după ce omisiunea e descoperită.

## Ce se greșește în practică

- Se introduce operațiunea uitată în declarația lunii curente, ca să „nu se piardă" — greșit, pentru că fiecare achiziție aparține perioadei în care a apărut exigibilitatea, nu perioadei în care a fost observată.
- Se amână depunerea până la o eventuală notificare de conformare de la ANAF, în loc să se depună din proprie inițiativă imediat ce omisiunea e găsită.
- Se presupune că, dacă factura a fost deja înregistrată contabil, obligația declarativă a fost automat îndeplinită — cele două lucruri sunt separate; D301 se generează explicit, nu implicit din notele contabile.

## Ce face iConta.eu

Aplicația nu generează D301 pentru o perioadă fără nicio operațiune introdusă — dacă lipsește o achiziție intracomunitară, declarația ar ieși, corect, pe zero, ceea ce nu rezolvă omisiunea. Un al doilea gard încrucișează operațiunile din D301 cu facturile de achiziție intracomunitară din evidența contabilă: dacă există facturi IC neintroduse în tabelul D301, aplicația blochează generarea declarației pentru acea perioadă, cu mesaj explicit, tocmai ca să prindă din timp exact situația de „am uitat o factură".

Atenție: generatorul emite mereu declarația ca originală (nerectificativă) — bifa de „declarație rectificativă" introdusă prin OPANAF 779/2024 nu e implementată în aplicație. Pentru o D301 deja depusă și incompletă, verifică separat mecanismul corect de corectare la ANAF.

[iConta.eu](/)
