---
title: Cum afectează cursul valutar rezultatul fiscal la impozitul pe profit
description: Ce spune legea despre elementele de curs valutar la trecerea de la impozit micro la profit, și cum e folosit cursul de schimb la calculul pragului IMCA.
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum afectează cursul valutar rezultatul fiscal la impozitul pe profit

Cursul valutar intervine în două locuri distincte, confirmate în cercetarea funcționalității D101: la trecerea de la impozit micro la impozit pe profit în cursul anului, și la determinarea cifrei de afaceri relevante pentru pragul de la care se datorează impozitul minim pe cifra de afaceri (IMCA).

## Temeiul legal

::: ghid-temei
Art.53 alin.(2) lit.b) CF tratează elementele de curs valutar la trecerea de la micro la profit ca „elemente similare veniturilor în primul trimestru pentru care datorează impozit pe profit"
— sursă: dosar de cercetare F027, secțiunea „Ieșirea din regimul micro în cursul anului".

„cifra de afaceri anul precedent = VT−Vs, la cursul de închidere a exercițiului"
— sursă: `core/d101.py`, funcția `datoreaza_imca` (liniile 48–73), dosar de cercetare F027.
:::

Pentru firmele care trec de la impozit micro la impozit pe profit în cursul anului, diferențele de curs valutar generate până la momentul trecerii se recunosc fiscal ca elemente similare veniturilor, în primul trimestru pentru care se datorează deja impozit pe profit — nu se reportează și nu se ignoră, dar nici nu se tratează retroactiv pe perioada de micro.

Separat, pentru determinarea pragului de 50.000.000 EUR de la care o firmă mare intră sub incidența IMCA (impozitul minim pe cifra de afaceri), cifra de afaceri a anului precedent se calculează la cursul de închidere a exercițiului — deci conversia valutară contează direct în decizia dacă firma e sau nu eligibilă pentru acest regim special.

## Ce se greșește în practică

O greșeală frecventă este ignorarea completă a elementelor de curs valutar generate la trecerea de la micro la profit, tratându-le ca și cum ar fi „rămas" în perioada de micro (unde oricum nu mai există de declarat). O a doua greșeală, la firmele mari, este utilizarea unui alt curs de schimb (de exemplu cursul mediu anual) în loc de cursul de închidere a exercițiului pentru verificarea pragului IMCA, ceea ce poate schimba concluzia dacă firma depășește sau nu pragul de 50.000.000 EUR.

## Ce face iConta.eu

Pentru pragul IMCA, motorul D101 din iConta.eu calculează eligibilitatea firmei folosind cursul de închidere a exercițiului pentru cifra de afaceri a anului precedent, conform formulei implementate în cod. Pentru trecerea de la micro la profit, tratarea elementelor de curs valutar ca venituri ale primului trimestru de profit rămâne, la nivelul dosarului de cercetare consultat, un calcul pe care contabilul îl introduce în declarație — aplicația nu automatizează separat acest transfer specific de la un regim la altul.

[iConta.eu](/)
