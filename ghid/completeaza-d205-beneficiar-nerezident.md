---
title: "Cum se completează D205 pentru un beneficiar nerezident"
description: "De ce dividendele plătite unui beneficiar nerezident nu se raportează prin D205 și pe ce declarație trebuie trecute în schimb."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se completează D205 pentru un beneficiar nerezident

Răspunsul scurt: dividendele plătite unui beneficiar nerezident **nu se completează în D205**. Declarația D205, pentru veniturile din dividende, este rezervată beneficiarilor rezidenți.

## Temeiul legal

::: ghid-temei
Nomenclator D205: "08 1.a) venituri din dividende - 8%/2024, 10%/2025, 16%/2026"; câmpul `Rezid` este "obligatoriu «1»" pentru tip_venit1="08" (dividende).
— Structura XML oficială D205, `anaf_surse/d205_struct_anaf.txt`, linia 428 și câmpurile aferente tip_venit1="08"
:::

Regula de validare a formularului (validatorul oficial DUK, regula R32) admite valoarea "Rezid = 2" (nerezident) doar pentru alte tipuri de venit din formular, nu și pentru tipul "08" (dividende). Pentru un beneficiar nerezident, dividendele nu se raportează pe D205, ci pe declarația D207, care este destinată special veniturilor obținute din România de nerezidenți.

## Ce se greșește în practică

Se încearcă introducerea beneficiarului nerezident direct în D205, eventual completând un NIF sau un pașaport în locul CNP-ului, sperând ca declarația să fie totuși validă.

## Ce face iConta.eu

Aplicația derivă automat rezidența beneficiarului din CNP (cod numeric personal românesc, 13 cifre, prima cifră între 1 și 8 pentru rezident) — nu există un câmp separat "rezident/nerezident" introdus manual. Un beneficiar fără CNP românesc valid (de exemplu cu NIF străin sau pașaport) este **respins automat la generarea D205** (`core/d205.py`), confirmat inclusiv prin testul intern care simulează un CNP început cu cifra 9 și primește eroare explicită, fără emiterea vreunei declarații. Concret: pentru un beneficiar nerezident, nu folosiți fluxul D205 din iConta — dividendele respective trebuie raportate pe D207.

[iConta.eu](/)
