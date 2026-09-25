---
title: "Mai trebuie depus D112 dacă firma este suspendată?"
description: "Ce spune Codul de procedură fiscală despre obligația de depunere a D112 pentru firmele cu activitate suspendată sau declarate inactive temporar."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Mai trebuie depus D112 dacă firma este suspendată?

Suspendarea temporară a activității la Registrul Comerțului nu suspendă automat toate obligațiile declarative — dar legea prevede explicit o scutire pentru perioada respectivă, cu condiții și limite clare.

## Temeiul legal

::: ghid-temei
„(4^1) Entitățile înregistrate în registrul comerțului, pentru care există înscrise mențiuni privind inactivitatea temporară, nu au obligația depunerii declarațiilor fiscale pentru perioada în care se află în inactivitate temporară, începând cu data de 1 a lunii următoare înscrierii mențiunii privind inactivitatea temporară în registrul comerțului. [...] (4^3) Aplicarea prevederilor alin. (4^1) și (4^2) încetează la data reluării activității sau la împlinirea unui termen de 3 ani [...]. (4^4) Obligațiile de declarare, aferente activității desfășurate anterior înregistrării inactivității temporare/suspendării, se mențin."
— Legea 207/2015 (Codul de procedură fiscală), art. 101 alin. (4^1), (4^3), (4^4) (sursă: anaf_surse/legea_207_2015_consolidat.txt)
:::

Aplicat la D112 (declarația privind obligațiile de plată a contribuțiilor sociale, impozitului pe venit și evidența nominală a persoanelor asigurate):

- scutirea de depunere se aplică **doar din prima zi a lunii următoare** înregistrării mențiunii de inactivitate temporară în registrul comerțului — nu retroactiv, de la data hotărârii de suspendare;
- dacă firma are **salariați activi** în perioada de suspendare (de exemplu, contracte suspendate individual, dar nu toate, sau plăți restante de salarii), obligația declarativă pentru acele venituri rămâne, pentru că scutirea vizează activitatea firmei, nu elimină obligațiile deja generate;
- obligațiile de declarare pentru perioadele **anterioare** înscrierii mențiunii de inactivitate rămân integral în vigoare (alin. 4^4) — suspendarea nu șterge restanțele declarative;
- scutirea încetează automat fie la reluarea activității, fie la împlinirea a 3 ani de la înscrierea mențiunii de inactivitate temporară.

## Ce se greșește în practică

- Se oprește depunerea D112 din luna hotărârii de suspendare, nu din luna următoare înscrierii efective a mențiunii la registrul comerțului — data contează, nu intenția.
- Se presupune că suspendarea acoperă și D112 pentru salariile plătite chiar înainte de suspendare, dar declarate cu întârziere — obligația pentru perioada anterioară inactivității se menține integral.
- Se uită să se reia depunerea D112 la reluarea activității sau la împlinirea celor 3 ani, iar declarațiile restante se acumulează nedepuse.
- Se ignoră faptul că suspendarea la Registrul Comerțului nu suspendă automat contractele individuale de muncă — dacă salariații rămân activi contractual, D112 rămâne datorat indiferent de mențiunea de inactivitate.

## Ce face iConta.eu

La data acestui ghid, iConta.eu **nu detectează automat** mențiunea de inactivitate temporară a firmei și nu suspendă generarea sau scadențarea D112 pe baza acestui statut — nu există în cod nicio verificare de acest tip în modulul D112 (`core/d112.py`). Declarația se generează pe baza datelor din statul de plată introduse de utilizator, indiferent de statutul firmei la registrul comerțului; decizia de a opri sau nu depunerea rămâne, pentru moment, în responsabilitatea contabilului.

[iConta.eu](/)
