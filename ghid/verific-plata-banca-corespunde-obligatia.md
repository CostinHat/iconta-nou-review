---
title: "Cum verific dacă plata din bancă corespunde cu obligația din SPV?"
description: "Ce înseamnă concret verificarea unei plăți din extrasul de cont față de obligația afișată în Spațiul Privat Virtual și ce poate, respectiv nu poate, face automat o aplicație de contabilitate."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum verific dacă plata din bancă corespunde cu obligația din SPV?

Plata unei obligații fiscale se face către un cont unic de Trezorerie, iar contribuabilul vede în Spațiul Privat Virtual (SPV) fișa pe plătitor, cu obligațiile declarate și sumele achitate. Potrivirea dintre suma ieșită din extrasul de cont și suma reflectată ca „stinsă" în SPV nu e automată — trece prin mai mulți pași care pot introduce diferențe.

## Temeiul legal

::: ghid-temei
„(2) În cazul creanțelor fiscale administrate de organul fiscal central și organul fiscal local, debitorii efectuează plata acestora într-un cont unic, prin utilizarea unui ordin de plată pentru Trezoreria Statului pentru obligațiile fiscale datorate."
— Legea nr. 207/2015 (Codul de procedură fiscală), art. 163 alin. (2) (sursă: anaf_surse/legea_207_2015_consolidat.txt)
:::

- Toate obligațiile fiscale administrate central se plătesc într-un **cont unic** de Trezorerie, pe bază de ordin de plată — nu în conturi separate pe fiecare tip de impozit.
- Suma din extrasul bancar trebuie să corespundă cu suma din ordinul de plată emis către acest cont unic, cu codul de identificare fiscală și explicația corecte.
- Stingerea efectivă a obligației în evidența ANAF (vizibilă apoi în SPV) se face de organul fiscal, pe baza acestei plăți — de aceea poate exista un decalaj de timp între data plății din bancă și data la care apare „stinsă" obligația în SPV.
- Diferențele reale (nu doar de decalaj) apar de regulă din explicații greșite pe ordinul de plată, din plăți parțiale sau din confundarea codurilor de obligație.

## Ce se greșește în practică

- Se compară direct suma din extrasul bancar cu suma din decizia de impunere, ignorând faptul că plata poate acoperi și dobânzi sau penalități calculate ulterior, aplicate pe cont unic.
- Se presupune că orice plată către contul unic de Trezorerie se reflectă instant în SPV, deși prelucrarea la ANAF are un timp propriu.
- Se ignoră explicația plății (codul de identificare fiscală, tipul obligației) ca sursă de eroare — o explicație incorectă poate face ca suma să fie alocată greșit, deși banii au ajuns la Trezorerie.

## Ce face iConta.eu

La data acestui ghid, iConta.eu are, separat, un conector SPV (`core/spv_conector.py`, `core/spv_receive.py`, `core/spv_poll.py`) care autentifică firma la ANAF și descarcă mesajele/recipisele din SPV, și un modul de reconciliere bancară (`core/reconciliere.py`) care potrivește liniile din extrasul de cont cu facturile deschise ale partenerilor. Nu am găsit însă în cod o funcție care să lege direct cele două fluxuri — adică să confrunte automat o plată din extrasul bancar cu o obligație fiscală afișată în SPV și să confirme corespondența. Această verificare rămâne, la acest moment, manuală, între extrasul de cont și fișa pe plătitor din SPV.

[iConta.eu](/)
