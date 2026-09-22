---
title: Cum verific dacă D300 este corect înainte de depunere?
description: iConta rulează gărzi de profil, calcul automat pe cote, un gard de oglindă pentru taxarea inversă și o reconciliere a doua cale înainte de a genera XML-ul — dar reconcilierea automată nu acoperă rândurile manuale, pro-rata sau TVA la încasare.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Cum verific dacă D300 este corect înainte de depunere?

Înainte de depunere, decontul trece deja prin mai multe verificări automate în aplicație — dar acestea au limite clare, mai ales pentru operațiunile care nu sunt derivate automat din facturi. O verificare finală, cel puțin sumară, rămâne responsabilitatea contabilului.

## Temeiul legal

::: ghid-temei
„19  TOTAL TAXĂ COLECTATĂ (sumă de la rd. 1 până la rd. 18, cu excepţia celor de la rd. 3.1,
5.1, 7.1, 12.1, 12.2)”

„30  TOTAL TAXĂ DEDUCTIBILĂ (sumă de la rd. 20 până la rd. 28, cu excepţia celor de la rd.
20.1, 22.1, 26.1, 26.2)
[...]
35  TOTAL TAXĂ DEDUSĂ (rd. 31 + rd. 32 + rd. 33 + rd. 34)”
— OPANAF 174/2026, ANEXA 2
:::

## Ce verifică aplicația automat înainte de generare

Fluxul de generare (`genereaza`) parcurge, în ordine: citirea facturilor pe fereastra fiscală a firmei, gărzi de profil (CUI cu cifră de control, denumire, bancă, cont/IBAN, cod CAEN, pro-rata), calculul propriu-zis pe cote și operațiuni speciale, gărzi blocante (inclusiv corelația tip de decont ↔ lună), un gard dedicat care verifică oglinda dintre rândul colectat și cel deductibil la taxarea inversă internă (dacă nu sunt egale, generarea se oprește cu eroare), o reconciliere independentă a totalurilor pe cote, apoi serializarea XML și un gard de sumă totală de plată, înainte de a semnala dacă decontul rezultat e nul.

## Ce se greșește în practică

- Se presupune că trecerea prin toate gărzile automate înseamnă că decontul e „100% corect” — gărzile nu acoperă rândurile manuale (intracomunitar, taxare inversă, ajustări), lanțul de regularizări rd.36–45, sau TVA la încasare.
- Nu se verifică statusul facturilor înainte de generare — facturi rămase în stare de ciornă sau nefinalizate pot lipsi din decont fără să genereze o alertă vizibilă.
- Se ignoră avertismentele de cotă (ex. resturi de 19% sau 5% vechi) care nu au rând valid — decontul se generează, dar sub-declarat pe acea sumă.
- Nu se compară soldurile manuale introduse (rd.38/rd.41) cu decontul efectiv depus în luna precedentă, ci se transcriu „din memorie”.

## Ce face iConta.eu

`genereaza(conn, schema, perioada, manual, reclasificari)` rulează, în ordine: gărzile de profil (`erori_generare`), calculul (`calcul_d300`), gărzile blocante pre-validare, gardul dedicat de oglindă pentru taxarea inversă (`_oglinda_r12_r25`, care ridică eroare dacă rândul colectat și cel deductibil nu sunt egale — regulă impusă de aplicație, nu de validatorul ANAF instalat), reconcilierea a doua cale (`d300_reconciliere.verifica_reconciliere`), serializarea XML și un gard de sumă totală de plată. Reconcilierea a doua cale recalculează independent doar totalurile automate pe cote — 21/11/9% pentru taxa colectată, dar doar 21/11% pentru cea deductibilă (cota 9% deductibilă nu se auto-emite) — nu acoperă rândurile manuale, lanțul de regularizări pro-rata (rd.36–45) și TVA la încasare, limite declarate explicit în cod. Pentru operațiunile speciale, verificarea manuală față de balanța contabilă rămâne necesară.

[iConta.eu](/)
