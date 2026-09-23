---
title: "Cum se inventariază numerarul din casierie la sfârșitul anului?"
description: "Regula legală privind inventarierea disponibilităților în lei și valută din casierie la finalul exercițiului financiar și ce acoperă efectiv ecranul de Inventariere anuală din iConta.eu."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se inventariază numerarul din casierie la sfârșitul anului?

Inventarierea generală anuală, obligatorie pentru toate entitățile, acoperă toate elementele de natura activelor — inclusiv numerarul din casierie, nu doar stocurile sau mijloacele fixe.

## Temeiul legal

::: ghid-temei
"Disponibilitățile în lei și în valută din casieria entității se inventariază în ultima zi lucrătoare a exercițiului financiar, după înregistrarea tuturor operațiunilor de încasări și plăți privind exercițiul respectiv, confruntându-se soldurile din registrul de casă cu monetarul și cu cele din contabilitate." — OMFP 2861/2009, Anexa 1, pct. 29 alin. (3)
:::

Momentul de referință este strict **ultima zi lucrătoare a exercițiului financiar**, și numai după ce toate încasările și plățile aferente anului au fost înregistrate. Rezultatul se stabilește prin confruntarea a trei surse: monetarul (numărătoarea faptică), registrul de casă și evidența contabilă.

## Ce se greșește în practică

- Numărătoarea se face înainte de închiderea tuturor operațiunilor de casă ale anului, ceea ce denaturează rezultatul.
- Se compară monetarul doar cu registrul de casă, fără confruntare și cu soldul din contabilitate.
- Se presupune că, la fel ca la stocuri, aplicația generează automat o notă contabilă de plus/minus de casă pornind din ecranul de inventariere.

## Ce face iConta.eu

Ecranul „Inventariere anuală" din aplicație (operațiile Plus stoc, Plus mijloc fix, Minus, Casare) este construit pentru stocuri — pe conturile 371, 301, 302, 303, 345, 381 — și pentru mijloace fixe. Motorul de calcul acceptă exclusiv aceste conturi; contul de casă (5311) nu se regăsește printre ele. Inventarierea numerarului rămâne, așadar, un proces procedural realizat de comisia de inventariere (numărare, confruntare cu registrul de casă și cu contabilitatea, consemnare în procesul-verbal), fără să treacă prin acest ecran — eventuala notă contabilă a diferențelor constatate la casierie se face separat, prin altă operațiune din aplicație, nu prin „Inventariere anuală".

[iConta.eu](/)
