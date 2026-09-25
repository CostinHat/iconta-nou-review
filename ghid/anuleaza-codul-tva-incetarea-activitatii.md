---
title: "Când se anulează codul de TVA la încetarea activității?"
description: "Mecanismul legal prin care se anulează înregistrarea în scopuri de TVA atunci când o firmă își încetează existența, conform Codului de procedură fiscală."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Când se anulează codul de TVA la încetarea activității?

Codul de înregistrare în scopuri de TVA nu e un cod separat de codul de identificare fiscală (CIF/CUI) — e o calitate atașată acestuia. Când firma încetează să mai existe ca subiect de drept, se anulează întreaga înregistrare fiscală, nu doar componenta de TVA.

## Temeiul legal

::: ghid-temei
„ART. 90 Radierea înregistrării fiscale
(1) Radierea înregistrării fiscale reprezintă activitatea de retragere a codului de identificare fiscală și a certificatului de înregistrare fiscală.
(2) La încetarea calității de subiect de drept fiscal, persoanele sau entitățile înregistrate fiscal prin declarație de înregistrare fiscală potrivit art. 81 și 82 trebuie să solicite radierea înregistrării fiscale, prin depunerea unei declarații de radiere. Declarația se depune în termen de 30 de zile de la încetarea calității de subiect de drept fiscal și trebuie însoțită de certificatul de înregistrare fiscală în vederea anulării acestuia. Radierea înregistrării fiscale se poate efectua și din oficiu, de către organul fiscal, ori de câte ori acesta constată îndeplinirea condițiilor de radiere a înregistrării și nu s-a depus declarație de radiere.
(3) Radierea înregistrării fiscale se efectuează din oficiu, de către organul fiscal central, în cazul decesului persoanei fizice sau, după caz, încetării existenței persoanei juridice potrivit legii."
— Legea 207/2015 (Codul de procedură fiscală), art. 90 alin. (1)-(3) (sursă: anaf_surse/legea_207_2015_consolidat.txt)
:::

Ce înseamnă concret pentru firmă:

- **Termenul standard** pentru depunerea declarației de radiere e de **30 de zile de la încetarea calității de subiect de drept fiscal** — practic, de la data radierii firmei din registrul comerțului (art. 90 alin. 2).
- **Radierea automată, din oficiu**, are loc atunci când organul fiscal central constată încetarea existenței persoanei juridice, chiar dacă firma nu a depus declarația de radiere (art. 90 alin. 3) — deci nu e nevoie ca ANAF să aștepte inițiativa contribuabilului dacă firma s-a radiat deja la registrul comerțului.
- Odată radiată înregistrarea fiscală, **codul de TVA încetează să mai fie valabil** — el nu se „anulează separat" printr-o procedură distinctă de anularea codului de identificare fiscală, ci dispare o dată cu întregul certificat de înregistrare.
- Codul de identificare fiscală retras rămâne utilizabil ulterior **doar de succesorii legali**, pentru obligații fiscale din perioada în care firma a existat (art. 90 alin. 4) — de exemplu, pentru soluționarea unei rambursări de TVA solicitate înainte de radiere.

## Ce se greșește în practică

- Se depune declarația de radiere abia după ce firma e deja radiată din registrul comerțului de câteva luni, ignorând termenul de 30 de zile — deși radierea se poate face și din oficiu, întârzierea poate complica soluționarea unor decizii de rambursare de TVA aflate în lucru.
- Se crede că trebuie depusă o cerere separată de „scoatere din evidența plătitorilor de TVA" înainte de radierea firmei la registrul comerțului — art. 90 arată că radierea vizează întreaga înregistrare fiscală, o dată cu încetarea existenței persoanei juridice, nu componenta de TVA izolat.
- Se ignoră faptul că, până la radiere, firma rămâne obligată la toate declarațiile fiscale curente (inclusiv deconturi de TVA), chiar dacă e în lichidare — lichidarea nu suspendă obligațiile declarative.

## Ce face iConta.eu

Modulul de lichidare din iConta.eu (`core/lichidare.py`) calculează operațiunile specifice închiderii unei firme — cota de lichidare, nota de vânzare a activelor (cu TVA colectată explicit, fără cotă implicită), partajul capitalului și rezervelor — conform OMFP 897/2015 și Legii 31/1990, art. 227 și următoarele. La data acestui ghid, aplicația **nu depune automat declarația de radiere (formularul 010) la ANAF** — aceasta rămâne o depunere separată, pe care contabilul o pregătește în afara fluxului de lichidare din aplicație, respectând termenul de 30 de zile de la încetarea existenței firmei.

[iConta.eu](/)
