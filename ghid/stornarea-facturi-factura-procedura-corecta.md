---
title: "Stornarea unei facturi în e-Factura: procedura corectă"
description: Stornarea creează o factură nouă, cu cantități negative, care copiază numărul de serie, cursul valutar și clasificarea fiscală ale originalului — procedura corectă include și transmiterea separată a acestui document către ANAF.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Stornarea unei facturi în e-Factura: procedura corectă

Stornarea nu e o „ștergere" și nu e o simplă notă contabilă negativă în paralel cu factura — e emiterea unui document fiscal nou, care trebuie el însuși parcurs prin tot circuitul unei facturi obișnuite, inclusiv transmiterea către ANAF.

## Temeiul legal

::: ghid-temei
„69. — Înregistrarea stornării unei operațiuni contabile aferente exercițiului financiar curent se efectuează fie prin corectarea cu semnul minus a operațiunii inițiale (**stornare în roșu**), fie prin înregistrarea inversă a acesteia (**stornare în negru**), în funcție de politica contabilă și programele informatice […]"

— OMFP 1802/2014, reglementări contabile consolidate, pct. 69

**OPANAF 2194/2025 (instrucțiuni D394)**, pct. 2.2.1: „seria şi numărul facturilor **stornate**; factura stornată reprezintă factura emisă de persoana impozabilă, a cărei valoare totală este negativă."
:::

Procedura corectă are trei pași:

1. **Emiterea documentului de stornare** — o factură nouă, cu un număr propriu rezervat din aceeași serie ca originalul, care preia liniile facturii inițiale cu cantități negate, păstrează cursul valutar al originalului (nu al zilei de stornare) și copiază integral clasificarea fiscală a acestuia — cotă de TVA, regim (intern, intracomunitar, taxare inversă), țară terță, dacă e cazul.
2. **Transmiterea documentului de stornare către ANAF**, prin RO e-Factura — pentru că reprezintă o operațiune economică distinctă (negativă), nu o simplă corecție internă.
3. **Declararea corectă în celelalte declarații** care citesc facturile emise (D300, D394, D390, D406/SAF-T) — fiecare tratează valoarea negativă a stornării conform propriei reguli, cu factura originală și stornarea ei pe același tip de operațiune.

## Ce se greșește în practică

- Se emite factura de stornare, dar se oprește procedura acolo, fără transmiterea ei în SPV — corecția rămâne incompletă din punct de vedere fiscal dacă originalul fusese transmis.
- Se aplică la stornare o clasificare fiscală diferită de a originalului, introdusă manual — corect e copierea exactă a clasificării originalului, nu recalcularea ei.

## Ce face iConta.eu

Pasul 1 e complet automatizat: butonul „Stornează", disponibil pe orice factură emisă care nu e ea însăși un document de stornare, generează automat documentul de corecție cu toate elementele descrise mai sus.

Pentru pasul 2, la acest moment butonul de trimitere în SPV nu apare pe documentul de stornare — transmiterea efectivă a corecției către ANAF, pentru facturile deja transmise, nu are în interfață o cale automată; e o limitare curentă de produs, nu un pas normal de flux.

[iConta.eu](/)
