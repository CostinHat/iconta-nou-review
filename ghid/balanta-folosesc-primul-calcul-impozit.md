---
title: "Ce balanță folosesc pentru primul calcul de impozit pe profit după ieșirea de la micro?"
description: "Balanța primului trimestru de profit trebuie să reflecte explicit elementele de curs valutar tratate ca venituri similare."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Ce balanță folosesc pentru primul calcul de impozit pe profit după ieșirea de la micro?

Balanța pentru primul calcul de impozit pe profit, după depășirea plafonului de microîntreprindere, folosește aceleași categorii de conturi ca orice calcul de profit — dar cu o ajustare specifică de tranziție.

## Temeiul legal

::: ghid-temei
"Art.53 alin.(2) lit.b): tratează elementele de curs valutar la trecere ca «elemente similare veniturilor în primul trimestru pentru care datorează impozit pe profit» — confirmă aceeași logică pe trimestru, nu retroactiv." — Legea 227/2015, citată în dosarul de cercetare F027.
:::

Balanța citită de aplicație (`pull()`, `core/d101.py` liniile 448–467) păstrează separarea clasică: conturile din clasele 76/66 ca financiar, restul din 7x/6x ca exploatare. Pentru firma aflată la primul calcul după ieșirea din regimul micro, elementele de curs valutar trebuie tratate explicit ca venituri similare în acel prim trimestru pentru care se datorează deja impozit pe profit — nu ignorate sau reportate ca și cum firma ar fi rămas la impozit micro.

## Ce se greșește în practică

Greșeala tipică e utilizarea unei balanțe „standard", fără ajustarea explicită a elementelor de curs valutar cerută de art.53 alin.(2) lit.b) pentru primul trimestru de profit.

## Ce face iConta.eu

`pull()` citește balanța cu aceeași separare financiar/exploatare indiferent de regimul anterior al firmei. Dosarul de cercetare nu documentează, dincolo de aceasta, un câmp specific în aplicație pentru marcarea automată a ajustării de curs valutar din primul trimestru de tranziție — recomandăm verificarea manuală a acestei ajustări în balanța pregătită.

[iConta.eu](/)
