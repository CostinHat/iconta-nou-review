---
title: "Checklist pentru auto-verificarea contabilității"
description: Verificatoarele automate (echilibru, balanță, TVA pe cotă, trezorerie) acoperă doar o parte a coerenței — restul (cont 441, D205, decontul de TVA) cer fie alt ecran, fie o metodologie manuală. Un checklist onest, pe ce chiar rulează.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Checklist pentru auto-verificarea contabilității

Un checklist de auto-verificare e util doar dacă spune exact ce se verifică automat și ce rămâne, deliberat sau nu, în sarcina contabilului. Mai jos, verificatoarele care rulează efectiv, plus zonele unde nu există (încă) un verificator automat.

## Temeiul legal

::: ghid-temei
„Pentru verificarea înregistrării corecte în contabilitate a operațiunilor efectuate, lunar se întocmește balanța de verificare." — Legea contabilității nr. 82/1991, art. 22.
:::

## Ce se verifică automat

**1. Echilibrul fiecărei note contabile.** Fiecare notă trebuie să aibă total debit egal cu total credit pe liniile ei — o notă neechilibrată e blocantă.

**2. Echilibrul ledgerului pe perioadă.** Separat de echilibrul unei note izolate, se verifică și echilibrul brut al liniilor din perioadă (Σdebit = Σcredit pe toate liniile, nu doar în interiorul unei note), plus liniile „orfane" (fără notă-mamă) și soldurile inițiale care nu se închid. Verificarea acoperă doar luna curentă și doar notele **validate** — o ciornă cu un cont greșit nu se vede până la validare.

**3. Soldurile inițiale ale balanței.** Suma soldurilor inițiale debitoare trebuie să fie egală cu suma celor creditoare.

**4. TVA pe cota corectă.** Baza × cota TVA valabilă **la data tranzacției**, nu cota curentă — prinde o cotă greșită aplicată pe o perioadă cu regim vechi.

**5. Trezoreria negativă.** Conturile de casă și bancă (5121, 5124, 5311, 5314) nu pot avea sold creditor.

## Ce NU se verifică automat, deși pare că ar trebui

- **Contul 441 (impozit pe profit) vs D100/D101.** Nu există un verificator care să compare rulajul contului cu declarația — spre deosebire de TVA sau de D112, aici verificarea rămâne manuală.
- **Soldul TVA de plată/recuperat (4423/4424) vs decont.** Verificarea există, dar rulează în ecranul „Control fiscal", nu printre verificatoarele de coerență descrise mai sus.
- **D205 (dividende) vs cont 457.** Verificarea există, dar tot ca mecanism separat, în ecranul de reconcilieri al declarațiilor, nu ca verificator de balanță.

## Ce se greșește în practică

- Se tratează „am rulat verificatoarele și sunt toate verzi" ca dovadă completă de conformitate — verzi înseamnă doar că cele cinci verificări de mai sus au trecut, nu că toată contabilitatea corespunde cu toate declarațiile.
- Se ignoră diferența dintre „validat" și „ciornă": verificarea de echilibru pe perioadă vede doar notele validate, deci o ciornă cu o eroare structurală rămâne invizibilă până la validare.
- Se presupune că un verificator lipsă pentru contul 441 înseamnă un bug — e o limită de produs, declarată ca atare, nu o eroare de rulare.

## Ce face iConta.eu

Rulează automat cinci verificări de coerență contabilă: echilibrul fiecărei note, echilibrul ledgerului pe perioadă (cu detectarea liniilor orfane), echilibrul soldurilor inițiale, cota de TVA aplicată la data corectă și absența soldurilor creditoare la conturile de trezorerie. Pentru zonele neacoperite — contul 441 față de declarațiile de profit, soldul TVA de plată/recuperat față de decont, D205 față de contul 457 — direcționăm către ecranele corecte (Control fiscal, respectiv reconcilierea declarațiilor) sau, unde nu există încă automatizare, o spunem direct, ca limită curentă a produsului.

[iConta.eu](/)
