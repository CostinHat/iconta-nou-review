---
title: Cum închid un SRL neplătitor de TVA?
description: Ce se schimbă, la lichidare, pentru o societate neplătitoare de TVA — și o limitare a ecranului de lichidare pe care trebuie să o cunoașteți dacă vindeți active.
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum închid un SRL neplătitor de TVA?

Pentru o societate neplătitoare de TVA, etapele juridice ale lichidării (dizolvare, valorificarea patrimoniului, stingerea pasivului, partaj, radiere) rămân aceleași ca pentru orice altă societate — diferența apare doar la nivelul operațiunilor care, la o firmă plătitoare, ar presupune colectarea TVA.

## Temeiul legal

::: ghid-temei
„lichidatorii pot [...] «să vândă, prin licitație publică, imobilele și orice avere mobiliară a societății»"
— L31/1990, art. 255 alin. (1) lit. c) (citat în dosarul de cercetare F057)
:::

Dreptul de a vinde activele rămase în cursul lichidării nu depinde de statutul de plătitor sau neplătitor de TVA al societății — el aparține lichidatorilor indiferent de acest statut.

## Ce se greșește în practică

O confuzie posibilă la o firmă neplătitoare de TVA privește ecranul de „Vânzare activ la lichidare" din iConta.eu: funcția de calcul care stă la baza acestei operațiuni (`core/lichidare.py`, `nota_vanzare_activ`) cere obligatoriu o cotă de TVA la fiecare vânzare de activ — codul refuză explicit generarea notei contabile dacă acest parametru lipsește, indiferent de statutul societății.

**Notă de transparență:** dosarul de cercetare pentru F057 nu a clarificat exact ce se completează în acest câmp pentru o societate neplătitoare de TVA (de exemplu, dacă se acceptă o cotă de 0% sau o valoare specială pentru „neplătitor"), pentru că ecranul de lichidare (`static/js/ecrane/operatiuni_ecran.js`) nu are un câmp explicit, vizibil, dedicat cotei de TVA la această operațiune — sursa exactă de unde preia aplicația această valoare nu a fost identificată în cercetarea de până acum. Recomandăm verificarea directă în aplicație, la momentul înregistrării vânzării, a valorii propuse implicit pentru cota de TVA, înainte de a valida nota contabilă.

## Ce face iConta.eu

Odată clarificată valoarea corectă a cotei de TVA pentru statutul de neplătitor (0%, dacă operațiunea nu e taxabilă), ecranul „Lichidare / radiere firmă", operația „Vânzare activ la lichidare", generează aceeași structură de notă contabilă ca pentru orice altă vânzare de activ imobilizat în cursul lichidării: venitul din vânzare pe 7583, descărcarea valorii rămase pe 6583 și a amortizării cumulate. Componenta de TVA colectată (4427) rămâne, pentru un neplătitor, fără efect practic asupra sumei datorate la buget — dar câmpul cotei trebuie totuși completat pentru ca aplicația să genereze nota.

[iConta.eu](/)
