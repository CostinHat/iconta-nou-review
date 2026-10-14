---
title: Cum închid un SRL neplătitor de TVA?
description: Ce se schimbă, la lichidare, pentru o societate neplătitoare de TVA — și o limitare a ecranului de lichidare pe care trebuie să o cunoașteți dacă vindeți active.
published: 2026-09-24
modified: 2026-10-13
poarta: v1
---

# Cum închid un SRL neplătitor de TVA?

Pentru o societate neplătitoare de TVA, etapele juridice ale lichidării (dizolvare, valorificarea patrimoniului, stingerea pasivului, partaj, radiere) rămân aceleași ca pentru orice altă societate — diferența apare doar la nivelul operațiunilor care, la o firmă plătitoare, ar presupune colectarea TVA.

Dreptul de a vinde activele rămase în cursul lichidării nu depinde de statutul de plătitor sau neplătitor de TVA al societății — el aparține lichidatorilor indiferent de acest statut.

## Temeiul legal

::: ghid-temei
„În afară de puterile conferite de asociați, cu aceeași majoritate cerută pentru numirea lor, lichidatorii vor putea: [...] c) să vândă, prin licitație publică, imobilele și orice avere mobiliară a societății;”
— Legea nr. 31/1990 privind societățile, art. 255 alin. (1) lit. c) (sursă: [Legea nr. 31/1990 privind societățile](https://legislatie.just.ro/Public/DetaliiDocument/798))
:::

## Ce se greșește în practică

O confuzie posibilă la o firmă neplătitoare de TVA privește operația „Vânzare activ la lichidare" din ecranul „Lichidare / radiere firmă” al iConta.eu: operația cere obligatoriu o cotă de TVA la fiecare vânzare de activ — aplicația refuză explicit generarea notei contabile dacă această cotă lipsește, indiferent de statutul societății.

**Ce completezi la o societate neplătitoare de TVA:** câmpul obligatoriu „Cota TVA %” al operației (în care e sugerată valoarea 21) se completează cu 0. Aplicația acceptă cota 0 ca valoare validă și generează nota fără TVA colectată — doar 461 = 7583, fără linia 461 = 4427. Nota iese în ciornă; verifică-o înainte de a o valida.

## Ce face iConta.eu

Odată clarificată valoarea corectă a cotei de TVA pentru statutul de neplătitor (0%, dacă operațiunea nu e taxabilă), ecranul „Lichidare / radiere firmă", operația „Vânzare activ la lichidare", generează aceeași structură de notă contabilă ca pentru orice altă vânzare de activ imobilizat în cursul lichidării: venitul din vânzare pe 7583, descărcarea valorii rămase pe 6583 și a amortizării cumulate. Componenta de TVA colectată (4427) rămâne, pentru un neplătitor, fără efect practic asupra sumei datorate la buget — dar câmpul cotei trebuie totuși completat pentru ca aplicația să genereze nota.

[iConta.eu](/)
