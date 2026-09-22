---
title: Cine trebuie să depună decontul de TVA D300?
description: D300 se completează doar de persoanele înregistrate în scopuri de TVA, cu termen până pe 25 ale lunii următoare pentru declaranții lunari, iar frecvența (lunar/trimestrial/semestrial/anual) trebuie să corespundă corect lunii pentru care se depune.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Cine trebuie să depună decontul de TVA D300?

D300 nu e o declarație pentru orice firmă — obligația de depunere revine strict persoanelor impozabile înregistrate în scopuri de TVA, iar frecvența depunerii (lunar, trimestrial, semestrial sau anual) depinde de regimul fiscal al fiecărei firme.

## Temeiul legal

::: ghid-temei
„Formularul (300) «Decont de taxă pe valoarea adăugată» se completează de persoanele
impozabile înregistrate în scopuri de TVA conform art. 316 din Legea nr. 227/2015 [...]”

„a) lunar, până la data de 25 inclusiv a lunii următoare celei pentru care se depune
decontul [...]; b) trimestrial [...]; c) semestrial [...]; d) anual, până la data de 25
ianuarie inclusiv a anului următor [...]”
— OPANAF 174/2026
:::

## Cine are obligația și cu ce frecvență

Obligația de depunere revine exclusiv persoanelor impozabile înregistrate în scopuri de TVA conform art.316 Cod fiscal — o firmă neînregistrată în scopuri de TVA nu depune D300. Frecvența depunerii (lunar, trimestrial, semestrial sau anual) e stabilită pentru fiecare firmă în funcție de cifra de afaceri și regimul fiscal ales, iar termenul e până pe 25 ale lunii următoare perioadei de raportare (pentru declaranții anuali, 25 ianuarie).

Frecvența nu e liberă pentru orice lună — de exemplu, un decont trimestrial nu se poate genera pentru orice lună calendaristică: regula de validare aplicată la generare admite tipul trimestrial doar pentru lunile 02, 03, 05, 06, 08, 09, 11 și 12 — corelația greșită dintre tipul de decont și luna aleasă e una dintre cele mai frecvente cauze de blocare a generării.

## Ce se greșește în practică

- Se generează D300 pentru o firmă neînregistrată încă în scopuri de TVA, sau pentru care înregistrarea a fost anulată.
- Se alege tipul de decont greșit pentru lună (de exemplu trimestrial pentru o lună care nu se regăsește printre lunile valide pentru acest tip de decont).
- Se depune decontul după termenul de 25 ale lunii următoare, fără să se verifice calendarul fiscal specific firmei.
- Fereastra fiscală configurată în aplicație nu e sincronizată cu tipul de decont real declarat la ANAF (de exemplu firma trece de la lunar la trimestrial, dar setarea din aplicație rămâne pe lunar).

## Ce face iConta.eu

`pull` citește facturile pe fereastra fiscală a firmei (`c.fereastra_tva`), care ține cont de tipul de decont configurat — lunar, trimestrial, semestrial sau anual. Înainte de generare, gărzile blocante verifică explicit corelația dintre tipul de decont și luna pentru care se generează decontul (de exemplu, un decont trimestrial e valid doar pentru anumite luni din calendarul fiscal) — o combinație nevalidă oprește generarea, ca să nu se depună un decont pentru o perioadă greșit încadrată.

[iConta.eu](/)
