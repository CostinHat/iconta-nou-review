---
title: "Cum pregătesc situațiile financiare pentru amortizare"
description: "Obligația legală a agenților economici de a evidenția distinct în contabilitate mijloacele fixe și amortizarea acestora, ca bază pentru situațiile financiare anuale."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum pregătesc situațiile financiare pentru amortizare

Pregătirea corectă a situațiilor financiare în privința mijloacelor fixe pornește de la o obligație simplă, dar frecvent tratată superficial: evidențierea distinctă, în conturi separate, a mijloacelor fixe și a amortizării lor cumulate — nu ca o singură cifră netă.

## Temeiul legal

::: ghid-temei
„Agenții economici, indiferent de forma de organizare și de tipul de proprietate, precum și persoanele juridice fără scop lucrativ au obligația să evidențieze în contabilitate, în conturi distincte, mijloacele fixe și amortizarea acestora."
— Legea nr. 15/1994 privind amortizarea capitalului imobilizat în active corporale și necorporale, art. 20 (sursă: anaf_surse/legea_15_1994_amortizarea_capitalului_imobilizat_active_corporale.txt)
:::

Consecințe practice pentru pregătirea situațiilor financiare:

- Valoarea de intrare a mijlocului fix (contul de imobilizări corporale) și amortizarea cumulată (contul de ajustare) trebuie să rămână **vizibile separat**, nu compensate într-o singură valoare netă în evidența contabilă curentă — compensarea apare doar la nivelul prezentării în bilanț.
- Amortizarea se calculează prin aplicarea cotelor de amortizare la valoarea de intrare, începând cu luna următoare punerii în funcțiune, până la recuperarea integrală a acesteia (art. 15 din aceeași lege).
- Situațiile financiare anuale reflectă, pentru fiecare categorie de mijloace fixe, soldul valorii de intrare și soldul amortizării cumulate din aceste conturi distincte, nu o reconstituire ulterioară din memorie sau din fișe externe.

## Ce se greșește în practică

- Se înregistrează achiziția mijlocului fix direct la valoarea netă (după o amortizare estimată), în loc de valoarea de intrare brută, ceea ce rupe legătura cu amortizarea cumulată reală.
- Se calculează amortizarea „la sfârșitul anului, retroactiv", deși legea leagă începutul amortizării de luna următoare punerii în funcțiune, nu de închiderea exercițiului.
- Se omite actualizarea fișei mijlocului fix când acesta este casat, vândut sau transferat, ceea ce lasă în situațiile financiare o valoare de intrare fără corespondent real în patrimoniu.

## Ce face iConta.eu

Verificat în cod: `core/bilant.py` generează situațiile financiare anuale (F10/F20, potrivit OMF 107/2025) din soldurile și rulajele conturilor din balanță; aplicația nu recalculează separat amortizarea mijloacelor fixe ca modul dedicat la acest moment — ea preia soldurile deja înregistrate pe conturile de imobilizări și de amortizare, așa cum sunt introduse/generate în contabilitatea curentă a firmei.

[iConta.eu](/)
