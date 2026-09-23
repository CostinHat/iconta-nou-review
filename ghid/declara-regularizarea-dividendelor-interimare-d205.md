---
title: Cum se declară regularizarea dividendelor interimare în D205?
description: Regularizarea anuală mută dividendul aprobat în contul 457, compensat cu interimarele deja distribuite prin contul 463 — abia acest moment face suma vizibilă pentru D205, ca dividend distribuit al anului.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum se declară regularizarea dividendelor interimare în D205?

După ce firma a distribuit dividende interimare în cursul anului, situațiile financiare anuale aduc regularizarea: dividendul anual aprobat de adunarea asociaților se compensează cu ce a fost deja distribuit trimestrial.

## Temeiul legal

::: ghid-temei
**OMFP 1802/2014, pct. 423^2**: „Dividendele repartizate conform pct. 423^1 se regularizează pe seama dividendelor distribuite pe baza situațiilor financiare anuale aprobate [...] (articol contabil 457 «Dividende de plată» = 463)."

**Legea 31/1990, art. 67 alin. (2^1)**: distribuirea parțială în cursul anului atrage regularizarea corespunzătoare prin situațiile financiare anuale.
:::

Regularizarea presupune două înregistrări: dividendul anual aprobat, în sumă totală, creditează contul 457 (1171=457), iar suma deja distribuită interimar se compensează prin debitarea contului 457 în corespondență cu 463 (457=463) — practic o mută din „creanță interimară" în „dividend de plată" recunoscut oficial.

Pentru D205, momentul care contează e creditarea contului 457 cu dividendul anual aprobat — aceasta e mișcarea pe care declarația o citește ca dividend distribuit al anului respectiv, proporțional cu cota fiecărui asociat. Suma compensată cu interimarele (457=463) nu adaugă un al doilea dividend distribuit — e doar o mutare internă a aceleiași sume, nu o distribuire nouă.

## Ce se greșește în practică

- Se declară dividendul interimar și, separat, dividendul anual regularizat, ca și cum ar fi două distribuiri distincte — sunt aceeași sumă, regularizarea doar o mută contabil în contul 457.
- Se omite complet regularizarea din anul curent, lăsând dividendele interimare „suspendate" în contul 463, situație în care ele rămân invizibile pentru D205 până la o regularizare ulterioară.

## Ce face iConta.eu

Motorul de decontări asociați din iConta.eu generează, la regularizare, exact cele două note prevăzute de pct. 423^2 — dividendul anual aprobat (1171=457) și compensarea cu interimarele deja distribuite (457=463). D205, ca declarație separată, preia automat din contul 457 suma regularizată ca dividend distribuit al anului, calculând baza și impozitul proporțional cu cota fiecărui asociat, pe partea efectiv plătită.

[iConta.eu](/)
