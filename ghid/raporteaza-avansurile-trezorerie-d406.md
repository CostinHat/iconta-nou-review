---
title: "Cum se raportează avansurile de trezorerie în D406?"
description: "Unde apar avansurile de trezorerie (contul 542) în structura fișierului SAF-T/D406 și de ce nu au o secțiune dedicată separată."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum se raportează avansurile de trezorerie în D406?

O întrebare firească pentru cei care pregătesc pentru prima dată fișierul SAF-T este dacă avansurile de trezorerie (contul 542) — acordate angajaților pentru deplasări sau achiziții — au o secțiune specială în D406. Nu au: structura oficială nu prevede o zonă dedicată pentru avansuri, pentru că principiul SAF-T e altul.

## Temeiul legal

::: ghid-temei
„GeneralLedgerEntries (Înregistrări contabile - Registrul-jurnal): Conține informații despre înregistrările contabile efectuate în perioada de raportare așa cum sunt înregistrate în sistemul contabil al contribuabilului/plătitor. Se vor raporta înregistrările contabile, la nivel de tranzacție, incluzând conturile contabile analitice stabilite conform planului de conturi românesc (AccountID)."
— OPANAF nr. 1.783/2021, Anexa 1 (sursă: anaf_surse/opanaf_1783_2021_saft_d406.txt)
:::

Ce rezultă de aici pentru avansurile de trezorerie:

- SAF-T nu raportează operațiuni pe „categorii" tematice (avansuri, salarii, stocuri etc.), ci **la nivel de tranzacție contabilă**, cu contul analitic exact folosit (AccountID) — deci avansurile de trezorerie apar automat, ca orice altă mișcare, în secțiunea **GeneralLedgerEntries**, identificate prin codul de cont 542, nu într-o zonă separată.
- Nu există, în structura oficială a D406, un modul dedicat „Avansuri" sau „Decontări cu personalul" — spre deosebire de secțiunile dedicate pentru stocuri (`MovementOfGoods`) sau active fixe (`FixedAssets`), care au propria lor structură specifică.
- Practic, dacă o firmă acordă un avans de trezorerie (542 = 5311/5121) și îl decontează ulterior (625 = 542), ambele înregistrări trebuie să apară corect, cu conturile lor, în registrul-jurnal raportat prin D406 — corectitudinea raportării ține de corectitudinea notelor contabile din sistemul intern, nu de o mapare specială pentru avansuri în SAF-T.
- Pentru contribuabilii cu volum mare de tranzacții, ANAF a prevăzut și o variantă de raportare la nivel de **balanță de conturi** analitică, nu doar tranzacție cu tranzacție — dar și în acest caz, avansurile rămân identificate prin contul lor, nu printr-o secțiune separată.

## Ce se greșește în practică

- Se caută în schema oficială SAF-T o secțiune specifică pentru „avansuri" — nu există, iar căutarea ei poate întârzia inutil pregătirea fișierului.
- Se omit avansurile de trezorerie nedecontate la sfârșitul perioadei de raportare, presupunând că „nu au ce căuta" în D406 — orice sold pe cont, inclusiv cel al avansurilor deschise, trebuie să fie reflectat corect în datele raportate.
- Se raportează avansul doar la momentul acordării, nu și la momentul decontării/regularizării, ceea ce lasă înregistrarea contabilă incompletă în fișier pentru perioada respectivă.

## Ce face iConta.eu

La data acestui ghid, motorul de generare D406 din iConta.eu (`core/d406.py`) construiește fișierul din notele contabile existente ale firmei, la nivel de tranzacție — avansurile de trezorerie (cont 542) sunt incluse automat, ca orice altă mișcare contabilă, fără o mapare specială separată de restul înregistrărilor.

[iConta.eu](/)
