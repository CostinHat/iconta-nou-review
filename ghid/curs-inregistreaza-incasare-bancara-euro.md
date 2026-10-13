---
title: "La ce curs se înregistrează o încasare bancară în euro?"
description: "Explică regula legală a cursului BNR aplicabil unei operațiuni în valută și cum determină iConta.eu cursul corect pe data operațiunii."
published: 2026-09-26
modified: 2026-10-13
poarta: v1
---

# La ce curs se înregistrează o încasare bancară în euro?

O încasare în valută nu se înregistrează la un curs "la alegere" — legea leagă cursul de data operațiunii, iar cursul folosit trebuie să fie exact cel comunicat de BNR, publicat cu o zi înainte.

Practic, regula spune că se ia cursul BNR valabil în ziua operațiunii — nu cursul zilei precedente ca dată de referință proprie, ci cursul pe care BNR l-a publicat pentru ziua respectivă (comunicat, tehnic, cu o zi înainte). Dacă în ziua operațiunii nu există un curs comunicat (weekend, sărbătoare legală), regula practică e să se ia ultimul curs BNR anterior valabil, nu cursul din ziua următoare.

## Ce se greșește în practică

Greșeli tipice: se ia cursul din extrasul bancar al băncii comerciale (care poate diferi de cursul BNR) în loc de cursul BNR; se folosește cursul din ziua în care se face înregistrarea în contabilitate, nu cursul din ziua efectivă a operațiunii; sau se lasă cursul "implicit" dintr-o zi anterioară fără verificare, riscând să se folosească un curs prea vechi.

## Ce face iConta.eu

Motorul de curs valutar al iConta.eu preia cursurile publicate de BNR (`curs.bnr.ro`) și aplică exact regula de mai sus: pentru orice dată de operațiune, alege ultimul curs BNR comunicat cu data cursului mai mică sau egală cu data operațiunii. Dacă cel mai recent curs găsit e mai vechi de 5 zile calendaristice (prag intern de produs, ales să acopere un weekend prelungit cu sărbători legale — nu e o normă fiscală), aplicația semnalează explicit "curs prea vechi" în loc să aplice tăcut un curs învechit; dacă moneda nu e cotată de BNR sau serviciul BNR e indisponibil, situația e afișată clar, nu ascunsă. Rotunjirea se face cu regula fiscală („calcul zecimal exact”, ROUND_HALF_UP), niciodată cu rotunjire simplă.

Această regulă de curs e implementată în iConta.eu în principal pentru conversia sumelor pe facturi și în declarații (D300, D390, D394, D406). Pentru o încasare bancară propriu-zisă (extras de cont), curs-ul aplicabil e cel al operațiunii cu care încasarea se decontează — de regulă, o factură emisă în valută — vezi și ghidul dedicat facturilor în valută.

[iConta.eu](/)
