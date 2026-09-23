---
title: Cum se completează D301 pentru bunuri cumpărate din UE?
description: Bunurile taxabile cumpărate din UE se declară la secțiunea 1 din D301 (sau la secțiunea 2/3 pentru mijloace de transport noi și produse accizabile), cu baza calculată din valoare valutară și curs.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum se completează D301 pentru bunuri cumpărate din UE?

Depinde de tipul bunului: bunurile taxabile "obișnuite" merg la secțiunea 1, mijloacele de transport noi la secțiunea 2, produsele accizabile la secțiunea 3.

## Temeiul legal

::: ghid-temei
Secțiunea 1 „Achiziții intracomunitare de bunuri taxabile - altele decât mijloacele de transport noi și produsele accizabile"; Secțiunea 2 „Achiziții intracomunitare de mijloace de transport noi"; Secțiunea 3 „Achiziții intracomunitare de produse accizabile" — OPANAF nr. 592/2016, Anexa 1
:::

::: ghid-temei
Pentru baza de impozitare: "se calculează coloana 2 x coloana 4" — OPANAF nr. 592/2016, Anexa 1 (coloana 2 = valoare în valută, coloana 4 = curs de schimb)
:::

Câmpurile de completat pe grila lunară sunt aceleași pentru toate cele trei secțiuni: tipul de operațiune (1, 2 sau 3), numărul și data documentului, valuta, valoarea în valută, cursul de schimb, cota aplicabilă și, opțional, țara/codul TVA/denumirea furnizorului. Baza se obține automat din valoarea în valută înmulțită cu cursul; contabilul nu o introduce direct.

Secțiunea 1 se depune doar de persoanele înregistrate special art. 317 (nu au și calitatea de plătitor art. 316); secțiunea 2 (mijloace de transport noi) se aplică oricărei persoane neînregistrate art. 316, indiferent dacă e sau nu înregistrată art. 317, și are un termen special legat de data înmatriculării, dar nu mai târziu de 25 ale lunii următoare.

## Ce se greșește în practică

- Se declară orice bun cumpărat din UE la secțiunea 1, inclusiv mijloacele de transport noi — acestea au propria secțiune (2), cu regim de termen diferit.
- Se calculează manual baza de impozitare, în loc să se lase valoarea în valută și cursul să facă acest calcul, cu riscul unei rotunjiri diferite.
- Se folosește un curs inventat sau vechi, în loc de cursul de schimb valabil la data exigibilității operațiunii.

## Ce face iConta.eu

Baza de impozitare nu se introduce manual: se recalculează la generarea declarației strict din valoarea în valută și curs, cu refuz explicit al unui curs absent sau ≤ 0, ca să nu se subevalueze tacit baza. Lista de valute acceptate e ținută aliniată la validatorul ANAF instalat, nu la un document vechi din 2013 — dacă o valută necesară lipsește, semnalați-o, nu o aproximați cu alta.

[iConta.eu](/)
