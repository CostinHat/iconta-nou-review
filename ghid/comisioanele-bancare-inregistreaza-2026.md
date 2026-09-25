---
title: "Comisioanele bancare: cum se înregistrează în 2026"
description: "Cum se contează corect comisioanele bancare din extrasul de cont și ce document justificativ stă la baza înregistrării."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Comisioanele bancare: cum se înregistrează în 2026

Comisioanele de administrare cont, comisioanele de transfer sau taxele pentru servicii bancare apar aproape zilnic în extrasul de cont, în sume mici, dar recurente. Tratamentul lor contabil e simplu, dar trebuie aplicat consecvent, pentru ca extrasul de cont să se reconcilieze exact cu balanța.

## Temeiul legal

::: ghid-temei
„Orice operațiune economico-financiară efectuată se consemnează în momentul efectuării ei într-un document care stă la baza înregistrărilor în contabilitate, dobândind astfel calitatea de document justificativ."
— OMFP 1802/2014 (reglementări contabile), pct. 314 alin. (2), cu trimitere la art. 6 alin. (1) din Legea contabilității nr. 82/1991 (sursă: anaf_surse/omfp_1802_2014_reglementari_consolidat.txt)
:::

Pentru comisioanele bancare, documentul justificativ e chiar extrasul de cont emis de bancă, ștampilat/certificat de instituția de credit — nu e nevoie de o factură separată, pentru că extrasul îndeplinește el însuși rolul de document justificativ pentru operațiunile de trezorerie. Monografia contabilă standard:

- **Comisionul se înregistrează în contul 627** ("Cheltuieli cu serviciile bancare și asimilate"), în contrapartidă cu contul de disponibilități (5121, pentru lei, sau contul valutar corespunzător).
- **Nu se deduce TVA separat**, pentru că majoritatea serviciilor bancare sunt scutite de TVA fără drept de deducere.
- **Data înregistrării e data din extrasul de cont**, nu data facturii (băncile emit rar facturi individuale pentru comisioane curente de cont).

## Ce se greșește în practică

- Se înregistrează comisioanele bancare direct pe cheltuieli generale (contul 628 sau altul nespecific), în loc de contul 627, dedicat serviciilor bancare.
- Se așteaptă o factură de la bancă pentru fiecare comision, deși extrasul de cont e suficient ca document justificativ pentru aceste operațiuni.
- Se omit comisioanele mici, recurente, din reconcilierea lunară, ceea ce lasă diferențe reziduale între soldul contabil și soldul real din extrasul bancar.

## Ce face iConta.eu

La data acestui ghid, iConta.eu detectează automat, din descrierea liniilor de extras bancar, operațiunile marcate cu cuvinte-cheie precum "comision", "taxa adm" sau "speze" și le contează automat pe contul 627, în contrapartidă cu contul de disponibilități — funcționalitate reală, aflată în modulul de import și contabilizare a extraselor de cont.

[iConta.eu](/)
