---
title: "Cum verific dacă toate declarațiile fiscale corespund cu contabilitatea?"
description: Motorul general de reconciliere a declarațiilor lucrează cu trei stări (verde/roșu/gri) și trei tipuri de remediu, dar acoperă declarație cu declarație — nu toate corespund automat cu contabilitatea, iar cont 441 rămâne o excepție declarată.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum verific dacă toate declarațiile fiscale corespund cu contabilitatea?

Nu există un singur buton „verifică tot" — există un motor general de reconciliere care rulează declarație cu declarație, plus câteva zone unde reconcilierea automată pur și simplu nu există încă.

## Temeiul legal

::: ghid-temei
„Pentru verificarea înregistrării corecte în contabilitate a operațiunilor efectuate, lunar se întocmește balanța de verificare." — Legea contabilității nr. 82/1991, art. 22.
:::

## Cum funcționează motorul general

Reconcilierea declarațiilor lucrează cu **trei stări**: verde (coincid), roșu (divergență confirmată) și gri (nu se poate stabili cu certitudine, de exemplu din cauza facturilor necontabilizate încă în fereastra verificată). Pentru fiecare stare de eșec, remediul propus e de unul din **trei tipuri**: executabil direct, sugerat contabilului, sau marcat pentru investigație manuală.

Acest motor acoperă, printre altele:

- **TVA**: cont 4427 (colectată) vs rândul din decont, 4426 (deductibilă) vs rândul din decont, rezultatul decontului (de plată/de recuperat) vs conturile 4423/4424 — cu toleranță de 1 leu.
- **D205 (dividende)** vs rulajul contului 457, prin doi mecanisme separate — unul cu recalcul independent al bazei/impozitului, celălalt integrat în motorul general de reconciliere.

## Ce NU acoperă

**Cont 441 (impozit pe profit) vs D100/D101.** Nu există un comparator automat între rulajul contului și ce arată declarația — spre deosebire de TVA sau de D112, unde comparația e explicită și rulează contra unui cont real. Verificarea aici rămâne manuală: recalculul obligației din declarație (profit impozabil × 16%) comparat cu rulajul propriu al contului.

Există și reconcilieri **interne** ale unor declarații — de exemplu D100 și D101 au un recalcul independent al bazei contabile (veniturile și cheltuielile pe clase de conturi) față de ce a folosit generatorul declarației. Această verificare confirmă că baza contabilă e agregată corect, dar **nu** compară declarația cu rulajul unui cont de impozit — sunt lucruri diferite, ușor de confundat.

## Ce se greșește în practică

- Se presupune că, pentru că unele declarații (TVA, D205) au reconciliere completă cu un cont real, toate au — cont 441 e o excepție declarată, nu ascunsă.
- Se confundă reconcilierea internă a bazei contabile a unei declarații (venituri/cheltuieli corect agregate) cu o reconciliere față de contul de impozit — prima nu înlocuiește pe a doua.
- Se citește o stare gri ca „eroare" sau ca „totul e în regulă", când de fapt gri înseamnă explicit „nu se poate stabili cu certitudine" — de obicei din cauza unor facturi necontabilizate încă.

## Ce face iConta.eu

Rulează motorul general de reconciliere pentru TVA (pe conturi și pe rezultatul decontului) și pentru D205 (pe rulajul contului 457, prin cele două mecanisme), cu cele trei stări și cele trei tipuri de remediu. Pentru cont 441 vs declarațiile de impozit pe profit, spunem clar: nu există încă un verificator automat, iar reconcilierea rămâne o procedură manuală de recalcul și comparare, nu un pas omis de aplicație.

[iConta.eu](/)
