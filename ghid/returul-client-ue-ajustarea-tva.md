---
title: Returul de la client din UE: ajustarea TVA și documente
description: Nomenclatorul D390 nu are un cod dedicat de "retur" — un retur de la un client din UE se reflectă prin stornarea (ajustarea) bazei impozabile raportate, păstrând aceeași clasificare fiscală ca livrarea inițială.
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Returul de la client din UE: ajustarea TVA și documente

Când un client dintr-un alt stat membru returnează bunuri dintr-o livrare intracomunitară (LIC), operațiunea nu se declară printr-un cod special de "retur" — nici în D300, nici în D390. Tratamentul corect e ajustarea (stornarea) bazei impozabile raportate inițial, cu aceleași elemente de clasificare fiscală ca operațiunea pe care o corectează.

## Temeiul legal

::: ghid-temei
"Ajustările se declară pentru luna calendaristică în care intervine exigibilitatea taxei, conform **art. 282 alin. (9) din Codul fiscal**, respectiv în luna calendaristică în care regularizarea a fost comunicată clientului." — OPANAF 705/2020, instrucțiuni D390

Nomenclatorul oficial D390 (OPANAF 705/2020) definește șase tipuri de operațiune: "L - pentru livrări intracomunitare de bunuri către alte state membre; T - pentru livrări în cadrul unei operațiuni triunghiulare; A - pentru achiziții intracomunitare de bunuri...; P - pentru prestările intracomunitare de servicii; S - pentru achiziții intracomunitare de servicii; R - livrări intracomunitare de bunuri efectuate în cadrul regimului special pentru agricultori." Niciunul dintre acestea nu înseamnă "retur" — codul R e pentru agricultori, nu pentru o marfă returnată.
:::

Important de clarificat: codul **R** din D390 e frecvent confundat cu "retur" din cauza literei, dar înseamnă exclusiv regimul special pentru agricultori (livrări IC de bunuri în acest regim). Nomenclatorul D390 nu prevede un cod separat pentru retur sau notă de credit — un retur se raportează prin ajustarea bazei impozabile a operațiunii inițiale (L pentru o livrare de bunuri, P pentru o prestare de servicii), nu printr-un tip de operațiune distinct.

Livrarea intracomunitară scutită se supune condițiilor de la art. 294 alin. (2) lit. a) Cod fiscal (cod TVA valid al cumpărătorului + dovada transportului în alt stat membru). Când marfa e returnată, aceleași condiții de fond ale scutirii rămân valabile pentru partea nereturnată — doar baza impozabilă se ajustează, în minus, cu valoarea bunurilor returnate.

Cât privește **momentul** declarării ajustării: regula din OPANAF 705/2020, citată mai sus, e clară — se declară în luna în care intervine exigibilitatea taxei sau în luna comunicării regularizării către client, conform art. 282 alin. (9) CF, nu retroactiv prin modificarea declarației deja depuse pentru perioada inițială.

Cât privește **convenția de semn**: instrucțiunile D390 nu conțin explicit cuvintele "semnul" sau "negativ" pentru retur/ajustare (spre deosebire de D394, care precizează expres "se înscrie cu semnul (-)"). Declararea bazei ajustate cu valoare negativă e o practică coerentă cu restul sistemului declarativ, nu un citat verbatim din instrucțiunile D390 înseși.

## Ce se greșește în practică

Cea mai frecventă greșeală e căutarea unui cod de tranzacție "de retur" în D390 — nu există. A doua greșeală: tratarea returului ca operațiune nouă, separată, în loc de ajustare (storno) a operațiunii inițiale — asta produce dublă raportare, nu corecție.

## Ce face iConta.eu

Motorul de stornare din contarea facturilor (`storno()`) generează aceleași note contabile ca factura originală, cu suma negată — nu o cotă recalculată sau un cont diferit. La nivelul documentului, crearea unei facturi de stornare păstrează cursul valutar al facturii inițiale și copiază identic clasificarea ei fiscală (țara terțului, taxarea inversă, axa intracomunitară bunuri/servicii, data faptului generator) — fără această copiere, stornul unei livrări intracomunitare ar deveni, în date, o livrare internă neclasificabilă, iar D300 și D390 nu ar mai corespunde. Practic, returul unei livrări IC aterizează pe același rând (L, cu bază negativă) ca factura originală.

Aplicația nu are o rutină D390 dedicată separat stornourilor intracomunitare — se bazează pe faptul că baza negativă circulă prin același flux de generare ca orice altă operațiune de tip L/A/P/S.

[iConta.eu](/)
