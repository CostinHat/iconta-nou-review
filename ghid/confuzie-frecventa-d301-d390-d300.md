---
title: Confuzie frecventă între D301, D390 și D300
description: Trei declarații diferite, cu regimuri diferite — care aplicație le confruntă automat între ele și care rămân verificări separate, netratate aici.
published: 2026-09-23
modified: 2026-09-23
poarta: v1
---

# Confuzie frecventă între D301, D390 și D300

D300, D390 și D301 se confundă des pentru că toate trei ating, într-un fel sau altul, operațiuni intracomunitare. Diferența nu e de conținut, ci de regim: cine le depune și în ce condiții e complet diferit de la o declarație la alta.

## Temeiul legal

::: ghid-temei
**Art. 325 din Codul fiscal (Legea 227/2015) — Declarația recapitulativă (D390).** Orice persoană impozabilă înregistrată în scopuri de TVA conform art. 316 sau art. 317 depune o declarație recapitulativă lunară, cu livrările intracomunitare scutite (lit. a) și achizițiile intracomunitare taxabile (lit. d).

D300 este decontul de TVA, depus de persoanele înregistrate normal în scopuri de TVA (art. 316), pe regim lunar sau trimestrial.

D301 este decontul special de TVA, prevăzut pentru persoanele care aplică regimul special de scutire pentru întreprinderi mici (art. 317) — categorie de contribuabili care **nu depune D300**. Modelul D301 e reglementat prin OPANAF 592/2016.
:::

**D300** e decontul de TVA propriu-zis — îl depun persoanele înregistrate normal în scopuri de TVA (art. 316), lunar sau trimestrial, cu toate operațiunile taxabile, nu doar cele intracomunitare.

**D390** e declarația recapitulativă (VIES) — o depun aceleași persoane, dar și cele neînregistrate normal (art. 317), atunci când au operațiuni intracomunitare. Conținutul e restrâns la livrări/achiziții/prestări intracomunitare, pe cod de operațiune (L, A, S etc.), nu pe toate operațiunile taxabile.

**D301** e decontul special, pentru persoanele înregistrate conform art. 317 (regimul special de scutire pentru întreprinderi mici) — un regim în care D300 nici nu se depune. Pentru aceste persoane, corelarea relevantă e D390 față de D301, nu față de D300.

Practic: dacă firma e plătitoare normală de TVA, perechea de verificat e D390 ↔ D300. Dacă firma e neplătitoare (regim special art. 317), perechea e D390 ↔ D301 — un mecanism diferit, cu mapare proprie a tipurilor de operațiuni din D301 spre codurile D390.

## Ce se greșește în practică

- Se așteaptă ca D390 să fie confruntată automat cu D301 la o firmă neplătitoare de TVA prin același mecanism care confruntă D390 cu D300 — sunt mecanisme separate, cu surse de date diferite.
- Se presupune că D300 conține și operațiunile intracomunitare din D390 într-un rând unic, ușor de comparat vizual — de fapt corespondența e pe rânduri specifice (livrări la un rând, achiziții la altul), nu pe un total agregat.
- Se tratează cele trei declarații ca variante ale aceleiași informații, redepuse de trei ori — au regimuri de contribuabil diferite și, pentru D300 vs D301, sunt chiar mutual exclusive pentru aceeași firmă.

## Ce face iConta.eu

Pentru firmele plătitoare de TVA (regim normal, art. 316), aplicația confruntă automat D390 cu D300-ul efectiv depus prin aplicație, pe rândurile de operațiuni intracomunitare — livrări față de achiziții, fiecare pe rândul lui din decont.

Pentru firmele neplătitoare de TVA (regim special, art. 317), care depun D301 în locul D300, corelarea D390 ↔ D301 e un mecanism separat, cu logică proprie de mapare a tipurilor de operațiuni din D301 către codurile D390 — nu trece prin controlul încrucișat descris aici, pentru că D300 nici nu există în acest regim.

[iConta.eu](/)
